"""IFC file generator using IfcOpenShell high-level API.

Only ``ifcopenshell.api.run()`` is used — no low-level entity manipulation.
"""

from __future__ import annotations

import math
import os
import tempfile
from pathlib import Path

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.owner
import ifcopenshell.util.placement

from promptbim.debug import get_logger
from promptbim.bim.materials import (
    MaterialDef,
    roof_material,
    slab_material,
    wall_material,
)
from promptbim.schemas.plan import BuildingPlan, StoryPlan, WallDef

_logger = get_logger("bim.ifc")


class IFCGenerator:
    """Build an IFC model from a :class:`BuildingPlan`."""

    def __init__(self) -> None:
        self._file: ifcopenshell.file | None = None
        self._project = None
        self._site = None
        self._building = None
        self._body_context = None
        self._owner_history = None
        self._material_cache: dict[str, object] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, plan: BuildingPlan, output_path: str | Path) -> Path:
        """Generate an IFC file from *plan* and write it to *output_path*."""
        import time as _time
        _t0 = _time.time()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        total_walls = sum(len(s.walls) for s in plan.stories)
        _logger.debug(
            "Generating IFC4: %d stories, %d walls, %d slabs, roof=%s",
            len(plan.stories), total_walls, len(plan.stories), plan.roof.roof_type,
        )

        self._init_file()
        self._create_project(plan.name)

        for story in plan.stories:
            self._add_story(story, plan)

        # Roof
        if plan.stories:
            top = plan.stories[-1]
            roof_z = top.elevation_m + top.height_m
            boundary = plan.building_footprint or (
                top.slab_boundary if top.slab_boundary else []
            )
            if boundary:
                self._add_roof(plan.roof.roof_type, boundary, roof_z)

        self._file.write(str(output_path))
        _elapsed = _time.time() - _t0
        file_size = output_path.stat().st_size / 1024
        _logger.debug("IFC written: %s (%.0f KB, %.2fs)", output_path, file_size, _elapsed)
        return output_path

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_file(self) -> None:
        self._file = ifcopenshell.api.run("project.create_file", version="IFC4")
        self._material_cache.clear()

    def _create_project(self, name: str) -> None:
        f = self._file
        self._project = ifcopenshell.api.run(
            "root.create_entity", f, ifc_class="IfcProject", name=name
        )

        # Length / area / volume units — metric
        ifcopenshell.api.run(
            "unit.assign_unit",
            f,
            length={"is_metric": True, "raw": "METRES"},
            area={"is_metric": True, "raw": "SQUARE_METRE"},
            volume={"is_metric": True, "raw": "CUBIC_METRE"},
        )

        # Geometric context
        self._body_context = ifcopenshell.api.run(
            "context.add_context", f, context_type="Model"
        )
        self._body_context = ifcopenshell.api.run(
            "context.add_context",
            f,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=self._body_context,
        )

        # Site + Building
        self._site = ifcopenshell.api.run(
            "root.create_entity", f, ifc_class="IfcSite", name="Site"
        )
        self._building = ifcopenshell.api.run(
            "root.create_entity", f, ifc_class="IfcBuilding", name=name
        )
        ifcopenshell.api.run(
            "aggregate.assign_object", f, products=[self._site], relating_object=self._project
        )
        ifcopenshell.api.run(
            "aggregate.assign_object",
            f,
            products=[self._building],
            relating_object=self._site,
        )

    # ------------------------------------------------------------------
    # Story
    # ------------------------------------------------------------------

    def _add_story(self, story: StoryPlan, plan: BuildingPlan) -> None:
        f = self._file
        ifc_storey = ifcopenshell.api.run(
            "root.create_entity",
            f,
            ifc_class="IfcBuildingStorey",
            name=story.name,
        )
        ifc_storey.Elevation = story.elevation_m
        ifcopenshell.api.run(
            "aggregate.assign_object",
            f,
            products=[ifc_storey],
            relating_object=self._building,
        )

        # Walls
        for wall_def in story.walls:
            self._add_wall(wall_def, story, ifc_storey)

        # Slab
        slab_boundary = story.slab_boundary or plan.building_footprint
        if slab_boundary:
            self._add_slab(slab_boundary, story, ifc_storey)

    # ------------------------------------------------------------------
    # Wall
    # ------------------------------------------------------------------

    def _add_wall(
        self, wall_def: WallDef, story: StoryPlan, ifc_storey
    ) -> None:
        f = self._file
        wall = ifcopenshell.api.run(
            "root.create_entity", f, ifc_class="IfcWall", name="Wall"
        )
        ifcopenshell.api.run(
            "spatial.assign_container",
            f,
            products=[wall],
            relating_structure=ifc_storey,
        )

        sx, sy = wall_def.start
        ex, ey = wall_def.end
        length = math.hypot(ex - sx, ey - sy)
        angle = math.atan2(ey - sy, ex - sx)

        # Placement at wall start, rotated
        matrix = _placement_matrix(sx, sy, story.elevation_m, angle)
        ifcopenshell.api.run(
            "geometry.edit_object_placement", f, product=wall, matrix=matrix
        )

        # Extruded rectangle representation
        rep = ifcopenshell.api.run(
            "geometry.add_wall_representation",
            f,
            context=self._body_context,
            length=length,
            height=story.height_m,
            thickness=wall_def.thickness_m,
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", f, product=wall, representation=rep
        )

        # Material
        mat_def = wall_material(wall_def.wall_type)
        ifc_mat = self._get_or_create_material(mat_def)
        ifcopenshell.api.run(
            "material.assign_material", f, products=[wall], material=ifc_mat
        )

    # ------------------------------------------------------------------
    # Slab
    # ------------------------------------------------------------------

    def _add_slab(
        self,
        boundary: list[tuple[float, float]],
        story: StoryPlan,
        ifc_storey,
    ) -> None:
        f = self._file
        slab = ifcopenshell.api.run(
            "root.create_entity", f, ifc_class="IfcSlab", name=f"Slab-{story.name}"
        )
        ifcopenshell.api.run(
            "spatial.assign_container",
            f,
            products=[slab],
            relating_structure=ifc_storey,
        )

        matrix = _placement_matrix(0, 0, story.elevation_m, 0)
        ifcopenshell.api.run(
            "geometry.edit_object_placement", f, product=slab, matrix=matrix
        )

        thickness = story.slab_thickness_m
        rep = ifcopenshell.api.run(
            "geometry.add_slab_representation",
            f,
            context=self._body_context,
            depth=thickness,
            polyline=list(boundary),
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", f, product=slab, representation=rep
        )

        mat_def = slab_material()
        ifc_mat = self._get_or_create_material(mat_def)
        ifcopenshell.api.run(
            "material.assign_material", f, products=[slab], material=ifc_mat
        )

    # ------------------------------------------------------------------
    # Roof
    # ------------------------------------------------------------------

    def _add_roof(
        self,
        roof_type: str,
        boundary: list[tuple[float, float]],
        base_z: float,
    ) -> None:
        f = self._file
        roof = ifcopenshell.api.run(
            "root.create_entity", f, ifc_class="IfcRoof", name="Roof"
        )
        # Assign to building directly (roof spans the whole building)
        ifcopenshell.api.run(
            "spatial.assign_container",
            f,
            products=[roof],
            relating_structure=self._building,
        )

        matrix = _placement_matrix(0, 0, base_z, 0)
        ifcopenshell.api.run(
            "geometry.edit_object_placement", f, product=roof, matrix=matrix
        )

        thickness = 0.15
        rep = ifcopenshell.api.run(
            "geometry.add_slab_representation",
            f,
            context=self._body_context,
            depth=thickness,
            polyline=list(boundary),
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", f, product=roof, representation=rep
        )

        mat_def = roof_material(roof_type)
        ifc_mat = self._get_or_create_material(mat_def)
        ifcopenshell.api.run(
            "material.assign_material", f, products=[roof], material=ifc_mat
        )

    # ------------------------------------------------------------------
    # Material
    # ------------------------------------------------------------------

    def _get_or_create_material(self, mat_def: MaterialDef):
        if mat_def.name in self._material_cache:
            return self._material_cache[mat_def.name]

        f = self._file
        ifc_mat = ifcopenshell.api.run(
            "material.add_material", f, name=mat_def.name
        )

        # Add surface style (colour)
        style = ifcopenshell.api.run("style.add_style", f, name=mat_def.name)
        ifcopenshell.api.run(
            "style.add_surface_style",
            f,
            style=style,
            ifc_class="IfcSurfaceStyleRendering",
            attributes={
                "SurfaceColour": {
                    "Name": mat_def.name,
                    "Red": mat_def.color[0],
                    "Green": mat_def.color[1],
                    "Blue": mat_def.color[2],
                },
                "Transparency": mat_def.transparency,
            },
        )

        self._material_cache[mat_def.name] = ifc_mat
        return ifc_mat


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _placement_matrix(
    x: float, y: float, z: float, angle_rad: float
) -> list[list[float]]:
    """4×4 placement matrix: translate + rotate around Z."""
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return [
        [c, -s, 0.0, x],
        [s, c, 0.0, y],
        [0.0, 0.0, 1.0, z],
        [0.0, 0.0, 0.0, 1.0],
    ]
