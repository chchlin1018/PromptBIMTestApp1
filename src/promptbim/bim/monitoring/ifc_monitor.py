"""IFC output for monitoring points — IfcSensor and IfcActuator entities.

Uses only ``ifcopenshell.api.run()`` high-level API.
"""

from __future__ import annotations

from pathlib import Path

import ifcopenshell
import ifcopenshell.api

from promptbim.bim.monitoring.auto_placement import MonitorPlacement, MonitorPlan

# Colour coding per category
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


class IFCMonitorGenerator:
    """Add IfcSensor / IfcActuator entities to an IFC file."""

    def __init__(self) -> None:
        self._file: ifcopenshell.file | None = None
        self._body_context = None
        self._style_cache: dict[str, object] = {}

    def add_monitors_to_file(
        self,
        ifc_path: str | Path,
        monitor_plan: MonitorPlan,
        output_path: str | Path | None = None,
    ) -> Path:
        """Load *ifc_path*, add monitoring entities, save to *output_path*."""
        ifc_path = Path(ifc_path)
        output_path = Path(output_path) if output_path else ifc_path

        self._file = ifcopenshell.open(str(ifc_path))
        self._body_context = self._find_body_context()
        self._style_cache.clear()

        storey_map = self._storey_map()

        for placement in monitor_plan.placements:
            storey = storey_map.get(placement.floor)
            self._add_monitor(placement, storey)

        self._file.write(str(output_path))
        return output_path

    def generate_standalone(
        self,
        monitor_plan: MonitorPlan,
        output_path: str | Path,
        project_name: str = "Monitoring",
    ) -> Path:
        """Create a standalone IFC file with only monitoring entities."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._file = ifcopenshell.api.run("project.create_file", version="IFC4")
        self._style_cache.clear()

        project = ifcopenshell.api.run(
            "root.create_entity", self._file, ifc_class="IfcProject", name=project_name
        )
        ifcopenshell.api.run(
            "unit.assign_unit",
            self._file,
            length={"is_metric": True, "raw": "METRES"},
        )
        ctx = ifcopenshell.api.run("context.add_context", self._file, context_type="Model")
        self._body_context = ifcopenshell.api.run(
            "context.add_context",
            self._file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=ctx,
        )

        site = ifcopenshell.api.run(
            "root.create_entity", self._file, ifc_class="IfcSite", name="Site"
        )
        building = ifcopenshell.api.run(
            "root.create_entity", self._file, ifc_class="IfcBuilding", name=project_name
        )
        ifcopenshell.api.run(
            "aggregate.assign_object", self._file, products=[site], relating_object=project
        )
        ifcopenshell.api.run(
            "aggregate.assign_object", self._file, products=[building], relating_object=site
        )

        # Create storeys
        floors = sorted(set(p.floor for p in monitor_plan.placements))
        storey_map: dict[str, object] = {}
        for fl in floors:
            storey = ifcopenshell.api.run(
                "root.create_entity", self._file, ifc_class="IfcBuildingStorey", name=fl
            )
            ifcopenshell.api.run(
                "aggregate.assign_object", self._file, products=[storey], relating_object=building
            )
            storey_map[fl] = storey

        for placement in monitor_plan.placements:
            storey = storey_map.get(placement.floor)
            self._add_monitor(placement, storey)

        self._file.write(str(output_path))
        return output_path

    # ---- internal ----

    def _find_body_context(self):
        for ctx in self._file.by_type("IfcGeometricRepresentationSubContext"):
            if ctx.ContextIdentifier == "Body":
                return ctx
        for ctx in self._file.by_type("IfcGeometricRepresentationContext"):
            return ctx
        return None

    def _storey_map(self) -> dict[str, object]:
        result: dict[str, object] = {}
        for storey in self._file.by_type("IfcBuildingStorey"):
            result[storey.Name] = storey
        return result

    def _add_monitor(self, placement: MonitorPlacement, storey=None) -> None:
        f = self._file
        ifc_class = placement.ifc_class

        element = ifcopenshell.api.run(
            "root.create_entity", f, ifc_class=ifc_class, name=placement.name
        )

        if storey is not None:
            ifcopenshell.api.run(
                "spatial.assign_container", f, products=[element], relating_structure=storey
            )

        # Placement at position
        x, y, z = placement.position
        matrix = [
            [1.0, 0.0, 0.0, x],
            [0.0, 1.0, 0.0, y],
            [0.0, 0.0, 1.0, z],
            [0.0, 0.0, 0.0, 1.0],
        ]
        ifcopenshell.api.run("geometry.edit_object_placement", f, product=element, matrix=matrix)

        # Small box representation (0.1m cube for sensor)
        size = 0.1
        rep = ifcopenshell.api.run(
            "geometry.add_wall_representation",
            f,
            context=self._body_context,
            length=size,
            height=size,
            thickness=size,
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", f, product=element, representation=rep
        )

        # Style by category
        self._apply_category_style(element, placement.category)

    def _apply_category_style(self, element, category: str) -> None:
        f = self._file
        color = _CATEGORY_COLORS.get(category, (0.0, 0.8, 0.8))

        if category not in self._style_cache:
            mat = ifcopenshell.api.run("material.add_material", f, name=f"Monitor_{category}")
            style = ifcopenshell.api.run("style.add_style", f, name=f"Monitor_{category}")
            ifcopenshell.api.run(
                "style.add_surface_style",
                f,
                style=style,
                ifc_class="IfcSurfaceStyleRendering",
                attributes={
                    "SurfaceColour": {
                        "Name": f"Monitor_{category}",
                        "Red": color[0],
                        "Green": color[1],
                        "Blue": color[2],
                    },
                    "Transparency": 0.0,
                },
            )
            self._style_cache[category] = mat

        ifcopenshell.api.run(
            "material.assign_material", f, products=[element], material=self._style_cache[category]
        )
