"""MEP IFC generator — adds pipe/duct/cable segments to an IFC file.

Uses only ``ifcopenshell.api.run()`` high-level API.
"""

from __future__ import annotations

import math
from pathlib import Path

import ifcopenshell
import ifcopenshell.api

from promptbim.bim.mep.planner import MEPPlan
from promptbim.bim.mep.systems import SYSTEM_COLORS

# IFC class per system
_SYSTEM_IFC_CLASS: dict[str, str] = {
    "plumbing": "IfcPipeSegment",
    "electrical": "IfcCableCarrierSegment",
    "hvac": "IfcDuctSegment",
    "fire_protection": "IfcPipeSegment",
}


class IFCMEPGenerator:
    """Append MEP elements to an existing IFC file or create a new one."""

    def __init__(self) -> None:
        self._file: ifcopenshell.file | None = None
        self._body_context = None
        self._style_cache: dict[str, object] = {}

    def add_mep_to_file(
        self,
        ifc_path: str | Path,
        mep_plan: MEPPlan,
        output_path: str | Path | None = None,
    ) -> Path:
        """Load *ifc_path*, add MEP geometry, save to *output_path*."""
        ifc_path = Path(ifc_path)
        output_path = Path(output_path) if output_path else ifc_path

        self._file = ifcopenshell.open(str(ifc_path))
        self._body_context = self._find_body_context()
        self._style_cache.clear()

        # Find or create building storey map
        storey_map = self._storey_map()

        seg_counter = 0
        for route in mep_plan.routes:
            if not route.path.waypoints or len(route.path.waypoints) < 2:
                continue
            for seg in route.path.segments:
                ifc_class = _SYSTEM_IFC_CLASS.get(route.system, "IfcPipeSegment")
                name = f"MEP_{route.system}_{seg_counter:04d}"
                storey = storey_map.get(route.floor)

                self._add_segment(
                    ifc_class=ifc_class,
                    name=name,
                    start=seg.start,
                    end=seg.end,
                    diameter_mm=route.diameter_mm,
                    system=route.system,
                    storey=storey,
                )
                seg_counter += 1

        self._file.write(str(output_path))
        return output_path

    def generate_standalone(
        self,
        mep_plan: MEPPlan,
        output_path: str | Path,
        project_name: str = "MEP",
    ) -> Path:
        """Create a standalone IFC file with just MEP elements."""
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
        floors = sorted(set(r.floor for r in mep_plan.routes))
        storey_map: dict[str, object] = {}
        for fl in floors:
            storey = ifcopenshell.api.run(
                "root.create_entity", self._file, ifc_class="IfcBuildingStorey", name=fl
            )
            ifcopenshell.api.run(
                "aggregate.assign_object", self._file, products=[storey], relating_object=building
            )
            storey_map[fl] = storey

        seg_counter = 0
        for route in mep_plan.routes:
            if not route.path.waypoints or len(route.path.waypoints) < 2:
                continue
            for seg in route.path.segments:
                ifc_class = _SYSTEM_IFC_CLASS.get(route.system, "IfcPipeSegment")
                name = f"MEP_{route.system}_{seg_counter:04d}"
                storey = storey_map.get(route.floor)
                self._add_segment(
                    ifc_class=ifc_class,
                    name=name,
                    start=seg.start,
                    end=seg.end,
                    diameter_mm=route.diameter_mm,
                    system=route.system,
                    storey=storey,
                )
                seg_counter += 1

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

    def _add_segment(
        self,
        ifc_class: str,
        name: str,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        diameter_mm: float,
        system: str,
        storey=None,
    ) -> None:
        f = self._file

        element = ifcopenshell.api.run("root.create_entity", f, ifc_class=ifc_class, name=name)

        if storey is not None:
            ifcopenshell.api.run(
                "spatial.assign_container", f, products=[element], relating_structure=storey
            )

        # Placement at segment start
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dz = end[2] - start[2]
        length = math.sqrt(dx**2 + dy**2 + dz**2)
        if length < 1e-6:
            return

        angle = math.atan2(dy, dx)
        matrix = [
            [math.cos(angle), -math.sin(angle), 0.0, start[0]],
            [math.sin(angle), math.cos(angle), 0.0, start[1]],
            [0.0, 0.0, 1.0, start[2]],
            [0.0, 0.0, 0.0, 1.0],
        ]
        ifcopenshell.api.run("geometry.edit_object_placement", f, product=element, matrix=matrix)

        # Representation: use wall representation as a simple extruded box
        radius_m = diameter_mm / 2000.0
        rep = ifcopenshell.api.run(
            "geometry.add_wall_representation",
            f,
            context=self._body_context,
            length=length,
            height=radius_m * 2,
            thickness=radius_m * 2,
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", f, product=element, representation=rep
        )

        # Style / color
        self._apply_system_style(element, system)

    def _apply_system_style(self, element, system: str) -> None:
        f = self._file
        color = SYSTEM_COLORS.get(system, (0.5, 0.5, 0.5))

        if system not in self._style_cache:
            mat = ifcopenshell.api.run("material.add_material", f, name=f"MEP_{system}")
            style = ifcopenshell.api.run("style.add_style", f, name=f"MEP_{system}")
            ifcopenshell.api.run(
                "style.add_surface_style",
                f,
                style=style,
                ifc_class="IfcSurfaceStyleRendering",
                attributes={
                    "SurfaceColour": {
                        "Name": f"MEP_{system}",
                        "Red": color[0],
                        "Green": color[1],
                        "Blue": color[2],
                    },
                    "Transparency": 0.0,
                },
            )
            self._style_cache[system] = mat

        ifcopenshell.api.run(
            "material.assign_material", f, products=[element], material=self._style_cache[system]
        )
