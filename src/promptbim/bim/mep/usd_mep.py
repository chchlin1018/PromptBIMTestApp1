"""MEP USD generator — adds pipe/duct geometry to a USD stage.

Uses only ``pxr.Usd``, ``pxr.UsdGeom``, ``pxr.UsdShade``.
"""

from __future__ import annotations

import math
from pathlib import Path

from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade

from promptbim.bim.mep.planner import MEPPlan
from promptbim.bim.mep.systems import SYSTEM_COLORS


class USDMEPGenerator:
    """Add MEP geometry to a USD stage."""

    def __init__(self) -> None:
        self._stage: Usd.Stage | None = None
        self._material_cache: dict[str, UsdShade.Material] = {}

    def add_mep_to_stage(
        self,
        usd_path: str | Path,
        mep_plan: MEPPlan,
        output_path: str | Path | None = None,
    ) -> Path:
        """Load a .usda file, add MEP, and save."""
        usd_path = Path(usd_path)
        output_path = Path(output_path) if output_path else usd_path

        self._stage = Usd.Stage.Open(str(usd_path))
        self._material_cache.clear()
        self._add_routes(mep_plan)
        self._stage.GetRootLayer().Export(str(output_path))
        return output_path

    def generate_standalone(
        self,
        mep_plan: MEPPlan,
        output_path: str | Path,
    ) -> Path:
        """Create a standalone .usda with only MEP geometry."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._stage = Usd.Stage.CreateNew(str(output_path))
        self._material_cache.clear()
        UsdGeom.SetStageUpAxis(self._stage, UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(self._stage, 1.0)

        UsdGeom.Xform.Define(self._stage, "/MEP")
        self._add_routes(mep_plan)
        self._stage.GetRootLayer().Save()
        return output_path

    # ---- internal ----

    def _add_routes(self, mep_plan: MEPPlan) -> None:
        seg_counter = 0
        for route in mep_plan.routes:
            if not route.path.waypoints or len(route.path.waypoints) < 2:
                continue
            for seg in route.path.segments:
                prim_path = f"/MEP/{route.system}/{route.floor}/seg_{seg_counter:04d}"
                self._add_cylinder_segment(
                    prim_path=prim_path,
                    start=seg.start,
                    end=seg.end,
                    radius_m=route.diameter_mm / 2000.0,
                    system=route.system,
                )
                seg_counter += 1

    def _add_cylinder_segment(
        self,
        prim_path: str,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        radius_m: float,
        system: str,
    ) -> None:
        """Create a box approximation of a pipe/duct segment."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dz = end[2] - start[2]
        length = math.sqrt(dx**2 + dy**2 + dz**2)
        if length < 1e-6:
            return

        # Ensure parent Xforms exist
        parts = prim_path.strip("/").split("/")
        for i in range(1, len(parts)):
            parent = "/" + "/".join(parts[:i])
            if not self._stage.GetPrimAtPath(parent).IsValid():
                UsdGeom.Xform.Define(self._stage, parent)

        # Create a cube prim scaled to represent the segment
        cube = UsdGeom.Cube.Define(self._stage, prim_path)

        # Position at midpoint
        mid = (
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2,
            (start[2] + end[2]) / 2,
        )

        xform = UsdGeom.Xformable(cube.GetPrim())
        xform.ClearXformOpOrder()

        translate_op = xform.AddTranslateOp()
        translate_op.Set(Gf.Vec3d(*mid))

        # Rotation: align cube along segment direction
        angle_z = math.atan2(dy, dx)
        if abs(angle_z) > 1e-6:
            rotate_op = xform.AddRotateZOp()
            rotate_op.Set(math.degrees(angle_z))

        # Scale: length along X, radius on Y/Z
        scale_op = xform.AddScaleOp()
        scale_op.Set(Gf.Vec3f(float(length / 2), float(radius_m), float(radius_m)))

        # Material
        mat = self._get_or_create_material(system)
        UsdShade.MaterialBindingAPI(cube.GetPrim()).Bind(mat)

    def _get_or_create_material(self, system: str) -> UsdShade.Material:
        if system in self._material_cache:
            return self._material_cache[system]

        color = SYSTEM_COLORS.get(system, (0.5, 0.5, 0.5))
        safe_name = f"MEP_{system}"
        mat_path = f"/MEP/Materials/{safe_name}"
        usd_mat = UsdShade.Material.Define(self._stage, mat_path)

        shader_path = f"{mat_path}/PBRShader"
        shader = UsdShade.Shader.Define(self._stage, shader_path)
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.6)
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.3)

        usd_mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        self._material_cache[system] = usd_mat
        return usd_mat
