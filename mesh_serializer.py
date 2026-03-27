"""Mesh Serializer — converts BuildingPlan to JSON mesh data for C++ rendering.

Each BIM element becomes:
  {
    "id": "1F_wall_0",
    "type": "wall",
    "material": "concrete",
    "vertices": [[x,y,z], ...],
    "indices": [[i0,i1,i2], ...],
    "dimensions": {"width": W, "height": H, "depth": D},
    "cost": N,
    "color": [r,g,b,a],
    "story": 0
  }
"""
from __future__ import annotations

from typing import Any

import numpy as np

from promptbim.bim.geometry import Mesh, wall_mesh, slab_mesh, flat_roof_mesh
from promptbim.schemas.plan import BuildingPlan


# Material mapping by element type
MATERIAL_MAP = {
    "wall": "concrete",
    "slab": "concrete",
    "column": "steel",
    "window": "glass",
    "door": "wood",
    "roof": "concrete",
    "pool": "glass",
    "parking": "concrete",
    "stair": "concrete",
}

# Color mapping [r, g, b, a]
COLOR_MAP = {
    "concrete": [0.6, 0.6, 0.6, 1.0],
    "glass": [0.7, 0.85, 1.0, 0.3],
    "steel": [0.8, 0.8, 0.82, 1.0],
    "wood": [0.55, 0.35, 0.15, 1.0],
}


def _mesh_to_json(mesh: Mesh) -> dict[str, list]:
    """Convert a Mesh (vertices, faces) to JSON-serializable format."""
    return {
        "vertices": mesh.vertices.tolist(),
        "indices": mesh.faces.tolist(),
    }


def _box_mesh(x: float, y: float, z: float, w: float, h: float, d: float) -> Mesh:
    """Generate a simple box mesh at position (x,y,z) with size (w,h,d)."""
    verts = np.array([
        [x,     y,     z],
        [x + w, y,     z],
        [x + w, y + d, z],
        [x,     y + d, z],
        [x,     y,     z + h],
        [x + w, y,     z + h],
        [x + w, y + d, z + h],
        [x,     y + d, z + h],
    ], dtype=np.float64)

    faces = np.array([
        [0, 2, 1], [0, 3, 2],
        [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4],
        [2, 3, 7], [2, 7, 6],
        [0, 4, 7], [0, 7, 3],
        [1, 2, 6], [1, 6, 5],
    ], dtype=np.int32)

    return Mesh(vertices=verts, faces=faces)


def serialize_plan_to_mesh(plan: BuildingPlan) -> dict[str, Any]:
    """Convert a BuildingPlan to JSON mesh data for the C++ renderer."""
    elements = []

    for story_idx, story in enumerate(plan.stories):
        # Use actual schema fields: elevation_m, height_m
        base_z = story.elevation_m
        floor_height = story.height_m
        story_label = f"{story_idx + 1}F"

        # Walls
        for w_idx, wall in enumerate(story.walls):
            try:
                mesh = wall_mesh(wall.start, wall.end, floor_height, wall.thickness_m, base_z)
                mesh_data = _mesh_to_json(mesh)
                dx = wall.end[0] - wall.start[0]
                dy = wall.end[1] - wall.start[1]
                length = (dx**2 + dy**2) ** 0.5

                elements.append({
                    "id": f"{story_label}_wall_{w_idx}",
                    "type": "wall",
                    "material": "concrete",
                    "color": COLOR_MAP["concrete"],
                    "story": story_idx,
                    "dimensions": {
                        "width": round(length, 2),
                        "height": round(floor_height, 2),
                        "depth": round(wall.thickness_m, 2),
                    },
                    **mesh_data,
                })
            except Exception:
                pass

        # Slab (uses slab_boundary + slab_thickness_m)
        if story.slab_boundary:
            try:
                mesh = slab_mesh(story.slab_boundary, story.slab_thickness_m, base_z)
                mesh_data = _mesh_to_json(mesh)
                elements.append({
                    "id": f"{story_label}_slab",
                    "type": "slab",
                    "material": "concrete",
                    "color": COLOR_MAP["concrete"],
                    "story": story_idx,
                    "dimensions": {
                        "width": 0, "height": round(story.slab_thickness_m, 2), "depth": 0,
                    },
                    **mesh_data,
                })
            except Exception:
                pass

        # Spaces → columns at corners
        for s_idx, space in enumerate(story.spaces):
            if hasattr(space, "boundary") and space.boundary:
                for c_idx, corner in enumerate(space.boundary[:4]):
                    col_size = 0.4
                    mesh = _box_mesh(
                        corner[0] - col_size / 2,
                        corner[1] - col_size / 2,
                        base_z,
                        col_size, floor_height, col_size,
                    )
                    mesh_data = _mesh_to_json(mesh)
                    elements.append({
                        "id": f"{story_label}_col_{s_idx}_{c_idx}",
                        "type": "column",
                        "material": "steel",
                        "color": COLOR_MAP["steel"],
                        "story": story_idx,
                        "dimensions": {
                            "width": col_size,
                            "height": round(floor_height, 2),
                            "depth": col_size,
                        },
                        **mesh_data,
                    })

        # Openings (windows/doors)
        for o_idx, opening in enumerate(story.openings):
            o_type = "window" if opening.sill_height_m > 0 else "door"
            mat = "glass" if o_type == "window" else "wood"
            if opening.wall_index < len(story.walls):
                w = story.walls[opening.wall_index]
                dx = w.end[0] - w.start[0]
                dy = w.end[1] - w.start[1]
                length = (dx**2 + dy**2) ** 0.5
                if length > 0:
                    t = opening.offset_m / length
                    ox = w.start[0] + dx * t
                    oy = w.start[1] + dy * t
                    sill = opening.sill_height_m
                    mesh = _box_mesh(
                        ox - opening.width_m / 2, oy - 0.05,
                        base_z + sill,
                        opening.width_m, opening.height_m, 0.1,
                    )
                    mesh_data = _mesh_to_json(mesh)
                    elements.append({
                        "id": f"{story_label}_{o_type}_{o_idx}",
                        "type": o_type,
                        "material": mat,
                        "color": COLOR_MAP[mat],
                        "story": story_idx,
                        "dimensions": {
                            "width": round(opening.width_m, 2),
                            "height": round(opening.height_m, 2),
                            "depth": 0.1,
                        },
                        **mesh_data,
                    })

    # Roof (on BuildingPlan, not on story)
    if plan.roof and hasattr(plan.roof, "boundary") and plan.roof.boundary:
        top_z = sum(s.height_m for s in plan.stories)
        try:
            mesh = flat_roof_mesh(plan.roof.boundary, 0.15, top_z)
            mesh_data = _mesh_to_json(mesh)
            elements.append({
                "id": "roof",
                "type": "roof",
                "material": "concrete",
                "color": [0.45, 0.45, 0.5, 1.0],
                "story": len(plan.stories),
                "dimensions": {"width": 0, "height": 0.15, "depth": 0},
                **mesh_data,
            })
        except Exception:
            pass

    return {
        "elements": elements,
        "element_count": len(elements),
        "stories": len(plan.stories),
    }
