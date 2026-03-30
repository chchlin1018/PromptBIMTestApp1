"""BuildingPlan -> PyVista mesh assembly for 3D interactive preview."""

from __future__ import annotations

from promptbim.debug import get_logger

logger = get_logger("viz.model_3d")

import numpy as np
import pyvista as pv

from promptbim.bim.geometry import Mesh, flat_roof_mesh, gable_roof_mesh, slab_mesh, wall_mesh
from promptbim.bim.materials import roof_material, slab_material, wall_material
from promptbim.schemas.plan import BuildingPlan, StoryPlan


def _mesh_to_polydata(mesh: Mesh) -> pv.PolyData | None:
    """Convert our Mesh dataclass to a PyVista PolyData."""
    if mesh.vertices.shape[0] == 0:
        return None
    n_faces = mesh.faces.shape[0]
    # PyVista face format: [n_verts, v0, v1, v2, ...]
    face_arr = np.column_stack(
        [
            np.full(n_faces, 3, dtype=np.int32),
            mesh.faces,
        ]
    ).ravel()
    return pv.PolyData(mesh.vertices, face_arr)


def _color_from_material(mat) -> str:
    """Convert MaterialDef color tuple to hex string."""
    r, g, b = mat.color
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def story_meshes(story: StoryPlan) -> list[tuple[pv.PolyData, str, str]]:
    """Build PyVista meshes for a single story.

    Returns list of (polydata, color_hex, label) tuples.
    """
    results: list[tuple[pv.PolyData, str, str]] = []

    # Walls
    for i, w in enumerate(story.walls):
        m = wall_mesh(
            start=w.start,
            end=w.end,
            height=story.height_m,
            thickness=w.thickness_m,
            base_z=story.elevation_m,
        )
        pd = _mesh_to_polydata(m)
        if pd is not None:
            mat = wall_material(w.wall_type)
            results.append((pd, _color_from_material(mat), f"{story.name}_wall_{i}"))

    # Slab
    if story.slab_boundary:
        m = slab_mesh(
            boundary=story.slab_boundary,
            thickness=story.slab_thickness_m,
            base_z=story.elevation_m - story.slab_thickness_m,
        )
        pd = _mesh_to_polydata(m)
        if pd is not None:
            mat = slab_material()
            results.append((pd, _color_from_material(mat), f"{story.name}_slab"))

    return results


def build_model(plan: BuildingPlan) -> list[tuple[pv.PolyData, str, str]]:
    """Assemble full building model from a BuildingPlan.

    Returns list of (polydata, color_hex, label) tuples for all elements.
    """
    import time as _time

    t0 = _time.perf_counter()
    all_meshes: list[tuple[pv.PolyData, str, str]] = []

    # Ground slab (under first floor)
    if plan.building_footprint:
        m = slab_mesh(
            boundary=plan.building_footprint,
            thickness=0.3,
            base_z=-0.3,
        )
        pd = _mesh_to_polydata(m)
        if pd is not None:
            mat = slab_material()
            all_meshes.append((pd, _color_from_material(mat), "ground_slab"))

    # Stories
    for story in plan.stories:
        all_meshes.extend(story_meshes(story))

    # Roof
    if plan.stories and plan.building_footprint:
        top_story = plan.stories[-1]
        roof_z = top_story.elevation_m + top_story.height_m
        roof_boundary = top_story.slab_boundary or plan.building_footprint

        if plan.roof.roof_type == "gable":
            ridge_h = max(1.5, plan.roof.slope_degrees * 0.05)
            m = gable_roof_mesh(
                boundary=roof_boundary,
                ridge_height=ridge_h,
                base_z=roof_z,
            )
        else:
            m = flat_roof_mesh(
                boundary=roof_boundary,
                thickness=0.2,
                base_z=roof_z,
            )
        pd = _mesh_to_polydata(m)
        if pd is not None:
            mat = roof_material(plan.roof.roof_type)
            all_meshes.append((pd, _color_from_material(mat), "roof"))

    total_verts = sum(pd.n_points for pd, _, _ in all_meshes)
    total_faces = sum(pd.n_cells for pd, _, _ in all_meshes)
    logger.debug(
        "build_model complete: %d meshes, %d vertices, %d faces in %.3fs",
        len(all_meshes),
        total_verts,
        total_faces,
        _time.perf_counter() - t0,
    )
    return all_meshes


def build_model_by_floor(plan: BuildingPlan) -> dict[str, list[tuple[pv.PolyData, str, str]]]:
    """Assemble building model grouped by floor name.

    Returns dict mapping floor name -> list of (polydata, color, label).
    Special keys: "ground_slab", "roof".
    """
    grouped: dict[str, list[tuple[pv.PolyData, str, str]]] = {}

    # Ground slab
    if plan.building_footprint:
        m = slab_mesh(boundary=plan.building_footprint, thickness=0.3, base_z=-0.3)
        pd = _mesh_to_polydata(m)
        if pd is not None:
            mat = slab_material()
            grouped["ground_slab"] = [(pd, _color_from_material(mat), "ground_slab")]

    # Stories
    for story in plan.stories:
        grouped[story.name] = story_meshes(story)

    # Roof
    if plan.stories and plan.building_footprint:
        top_story = plan.stories[-1]
        roof_z = top_story.elevation_m + top_story.height_m
        roof_boundary = top_story.slab_boundary or plan.building_footprint
        if plan.roof.roof_type == "gable":
            ridge_h = max(1.5, plan.roof.slope_degrees * 0.05)
            m = gable_roof_mesh(boundary=roof_boundary, ridge_height=ridge_h, base_z=roof_z)
        else:
            m = flat_roof_mesh(boundary=roof_boundary, thickness=0.2, base_z=roof_z)
        pd = _mesh_to_polydata(m)
        if pd is not None:
            mat = roof_material(plan.roof.roof_type)
            grouped["roof"] = [(pd, _color_from_material(mat), "roof")]

    return grouped


def clip_model_at_elevation(
    meshes: list[tuple[pv.PolyData, str, str]],
    elevation: float,
) -> list[tuple[pv.PolyData, str, str]]:
    """Clip all meshes at a given elevation (section cut).

    Returns meshes clipped below the elevation plane.
    """
    clipped: list[tuple[pv.PolyData, str, str]] = []
    for pd, color, label in meshes:
        try:
            result = pd.clip(normal="z", origin=(0, 0, elevation), invert=False)
            if result.n_points > 0:
                clipped.append((result, color, label))
        except (ValueError, RuntimeError) as exc:
            logger.debug("Clip failed for '%s', keeping original: %s", label, exc)
            clipped.append((pd, color, label))
    return clipped
