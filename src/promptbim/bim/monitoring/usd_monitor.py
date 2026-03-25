"""USD output for monitoring points — uses monitor: namespace for IDTF integration.

Uses only ``pxr.Usd``, ``pxr.UsdGeom``, ``pxr.UsdShade``.
Each sensor/actuator is a small sphere prim under /Monitoring/{floor}/{category}/.
Custom attributes use the ``monitor:`` namespace per IDTF requirements.
"""

from __future__ import annotations

from pathlib import Path

from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade

from promptbim.bim.monitoring.auto_placement import MonitorPlan, MonitorPlacement
from promptbim.bim.monitoring.monitor_types import MONITOR_TYPES


_CATEGORY_COLORS: dict[str, tuple[float, float, float]] = {
    "environmental": (0.2, 0.6, 1.0),
    "safety": (1.0, 0.3, 0.3),
    "security": (0.6, 0.2, 0.8),
    "energy": (0.9, 0.7, 0.1),
    "structural": (0.7, 0.2, 0.2),
    "mep": (0.3, 0.7, 0.8),
    "smart": (0.3, 0.9, 0.5),
    "accessibility": (0.4, 0.4, 1.0),
}


class USDMonitorGenerator:
    """Add monitoring points to a USD stage with monitor: namespace attributes."""

    def __init__(self) -> None:
        self._stage: Usd.Stage | None = None
        self._material_cache: dict[str, UsdShade.Material] = {}

    def add_monitors_to_stage(
        self,
        usd_path: str | Path,
        monitor_plan: MonitorPlan,
        output_path: str | Path | None = None,
    ) -> Path:
        """Load a .usda file, add monitoring prims, and save."""
        usd_path = Path(usd_path)
        output_path = Path(output_path) if output_path else usd_path

        self._stage = Usd.Stage.Open(str(usd_path))
        self._material_cache.clear()
        self._add_placements(monitor_plan)
        self._stage.GetRootLayer().Export(str(output_path))
        return output_path

    def generate_standalone(
        self,
        monitor_plan: MonitorPlan,
        output_path: str | Path,
    ) -> Path:
        """Create a standalone .usda with only monitoring geometry."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._stage = Usd.Stage.CreateNew(str(output_path))
        self._material_cache.clear()
        UsdGeom.SetStageUpAxis(self._stage, UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(self._stage, 1.0)

        UsdGeom.Xform.Define(self._stage, "/Monitoring")
        self._add_placements(monitor_plan)
        self._stage.GetRootLayer().Save()
        return output_path

    # ---- internal ----

    def _add_placements(self, monitor_plan: MonitorPlan) -> None:
        counter = 0
        for placement in monitor_plan.placements:
            safe_name = self._sanitize(placement.name)
            safe_floor = self._sanitize(placement.floor)
            safe_cat = self._sanitize(placement.category)
            prim_path = f"/Monitoring/{safe_floor}/{safe_cat}/{safe_name}_{counter}"
            self._add_monitor_prim(prim_path, placement)
            counter += 1

    @staticmethod
    def _sanitize(name: str) -> str:
        """Make a string safe for use as a USD prim name."""
        import re
        s = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        if s and s[0].isdigit():
            s = "F" + s
        return s or "_"

    def _add_monitor_prim(self, prim_path: str, placement: MonitorPlacement) -> None:
        # Ensure parent Xforms exist
        parts = prim_path.strip("/").split("/")
        for i in range(1, len(parts)):
            parent = "/" + "/".join(parts[:i])
            if not self._stage.GetPrimAtPath(parent).IsValid():
                UsdGeom.Xform.Define(self._stage, parent)

        # Create a small sphere for the sensor
        sphere = UsdGeom.Sphere.Define(self._stage, prim_path)
        sphere.GetRadiusAttr().Set(0.08)

        # Position
        x, y, z = placement.position
        xform = UsdGeom.Xformable(sphere.GetPrim())
        xform.ClearXformOpOrder()
        translate_op = xform.AddTranslateOp()
        translate_op.Set(Gf.Vec3d(x, y, z))

        # monitor: namespace custom attributes (IDTF requirement)
        prim = sphere.GetPrim()
        prim.CreateAttribute("monitor:type_id", Sdf.ValueTypeNames.String).Set(
            placement.monitor_type_id
        )
        prim.CreateAttribute("monitor:category", Sdf.ValueTypeNames.String).Set(
            placement.category
        )
        prim.CreateAttribute("monitor:floor", Sdf.ValueTypeNames.String).Set(
            placement.floor
        )
        prim.CreateAttribute("monitor:space", Sdf.ValueTypeNames.String).Set(
            placement.space_name
        )
        prim.CreateAttribute("monitor:ifc_class", Sdf.ValueTypeNames.String).Set(
            placement.ifc_class
        )
        prim.CreateAttribute("monitor:predefined_type", Sdf.ValueTypeNames.String).Set(
            placement.predefined_type
        )
        prim.CreateAttribute("monitor:unit_cost_twd", Sdf.ValueTypeNames.Float).Set(
            float(placement.unit_cost_twd)
        )

        # Lookup description from type definitions
        mt = MONITOR_TYPES.get(placement.monitor_type_id)
        if mt:
            prim.CreateAttribute("monitor:description", Sdf.ValueTypeNames.String).Set(
                mt.description
            )
            prim.CreateAttribute("monitor:measurement_unit", Sdf.ValueTypeNames.String).Set(
                mt.measurement_unit
            )

        # Material by category
        mat = self._get_or_create_material(placement.category)
        UsdShade.MaterialBindingAPI(prim).Bind(mat)

    def _get_or_create_material(self, category: str) -> UsdShade.Material:
        if category in self._material_cache:
            return self._material_cache[category]

        color = _CATEGORY_COLORS.get(category, (0.0, 0.8, 0.8))
        mat_path = f"/Monitoring/Materials/Monitor_{category}"
        usd_mat = UsdShade.Material.Define(self._stage, mat_path)

        shader_path = f"{mat_path}/PBRShader"
        shader = UsdShade.Shader.Define(self._stage, shader_path)
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
            Gf.Vec3f(*color)
        )
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.1)
        shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(0.85)

        usd_mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        self._material_cache[category] = usd_mat
        return usd_mat
