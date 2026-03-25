"""Geometry helpers — wall, slab, and roof mesh generation.

All coordinates are in metres, local coordinate system.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import mapbox_earcut
import numpy as np

from promptbim.debug import get_logger

logger = get_logger("bim.geometry")


@dataclass
class Mesh:
    """Simple triangle-mesh container."""

    vertices: np.ndarray  # (N, 3) float64
    faces: np.ndarray  # (M, 3) int32 — triangle indices


# ---------------------------------------------------------------------------
# Wall
# ---------------------------------------------------------------------------

def wall_mesh(
    start: tuple[float, float],
    end: tuple[float, float],
    height: float,
    thickness: float = 0.2,
    base_z: float = 0.0,
) -> Mesh:
    """Generate an extruded wall mesh (box) from *start* to *end*.

    The wall centre-line runs from *start* to *end*; it is extruded by
    *thickness* (half on each side of the centre-line) and *height* upward.
    """
    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return Mesh(vertices=np.zeros((0, 3)), faces=np.zeros((0, 3), dtype=np.int32))

    # Normal perpendicular to wall direction (unit)
    nx, ny = -dy / length, dx / length
    half_t = thickness / 2.0

    # Four corners at base, four at top
    z0 = base_z
    z1 = base_z + height
    verts = np.array(
        [
            [sx - nx * half_t, sy - ny * half_t, z0],
            [sx + nx * half_t, sy + ny * half_t, z0],
            [ex + nx * half_t, ey + ny * half_t, z0],
            [ex - nx * half_t, ey - ny * half_t, z0],
            [sx - nx * half_t, sy - ny * half_t, z1],
            [sx + nx * half_t, sy + ny * half_t, z1],
            [ex + nx * half_t, ey + ny * half_t, z1],
            [ex - nx * half_t, ey - ny * half_t, z1],
        ],
        dtype=np.float64,
    )
    faces = _box_faces()
    logger.debug("wall_mesh: length=%.2f, height=%.2f, thickness=%.2f, verts=%d, faces=%d", length, height, thickness, len(verts), len(faces))
    return Mesh(vertices=verts, faces=faces)


# ---------------------------------------------------------------------------
# Slab
# ---------------------------------------------------------------------------

def slab_mesh(
    boundary: list[tuple[float, float]],
    thickness: float = 0.2,
    base_z: float = 0.0,
) -> Mesh:
    """Generate an extruded slab from a 2-D polygon boundary.

    The slab sits between *base_z* and *base_z + thickness*.
    Uses earcut triangulation (handles convex and concave polygons).
    """
    if len(boundary) < 3:
        return Mesh(vertices=np.zeros((0, 3)), faces=np.zeros((0, 3), dtype=np.int32))

    n = len(boundary)
    z0 = base_z
    z1 = base_z + thickness

    # Bottom + top vertices
    verts_bottom = [(x, y, z0) for x, y in boundary]
    verts_top = [(x, y, z1) for x, y in boundary]
    verts = np.array(verts_bottom + verts_top, dtype=np.float64)

    faces: list[list[int]] = []

    # Bottom face — reversed winding for outward normal
    tri_indices = _earcut_triangulate(boundary)
    for a, b, c in tri_indices:
        faces.append([a, c, b])  # flip for downward normal

    # Top face
    for a, b, c in tri_indices:
        faces.append([a + n, b + n, c + n])

    # Side faces
    for i in range(n):
        j = (i + 1) % n
        bi, bj = i, j
        ti, tj = i + n, j + n
        faces.append([bi, bj, tj])
        faces.append([bi, tj, ti])

    result = Mesh(vertices=verts, faces=np.array(faces, dtype=np.int32))
    logger.debug("slab_mesh: boundary_pts=%d, verts=%d, faces=%d", len(boundary), len(result.vertices), len(result.faces))
    return result


# ---------------------------------------------------------------------------
# Roof
# ---------------------------------------------------------------------------

def flat_roof_mesh(
    boundary: list[tuple[float, float]],
    thickness: float = 0.15,
    base_z: float = 0.0,
) -> Mesh:
    """Flat roof — essentially a slab at the roof level."""
    return slab_mesh(boundary, thickness=thickness, base_z=base_z)


def gable_roof_mesh(
    boundary: list[tuple[float, float]],
    ridge_height: float = 2.0,
    base_z: float = 0.0,
) -> Mesh:
    """Simple gable roof along the longest dimension of the bounding box.

    Creates a triangular prism along the major axis.
    """
    pts = np.array(boundary, dtype=np.float64)
    min_xy = pts.min(axis=0)
    max_xy = pts.max(axis=0)
    dx = max_xy[0] - min_xy[0]
    dy = max_xy[1] - min_xy[1]

    x0, y0 = min_xy
    x1, y1 = max_xy
    z0 = base_z
    zr = base_z + ridge_height

    if dx >= dy:
        # Ridge along X
        mid_y = (y0 + y1) / 2.0
        verts = np.array(
            [
                [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],  # base
                [x0, mid_y, zr], [x1, mid_y, zr],  # ridge
            ],
            dtype=np.float64,
        )
        faces = np.array(
            [
                [0, 1, 5], [0, 5, 4],  # front slope
                [2, 3, 4], [2, 4, 5],  # back slope
                [0, 4, 3],  # left gable
                [1, 2, 5],  # right gable
            ],
            dtype=np.int32,
        )
    else:
        # Ridge along Y
        mid_x = (x0 + x1) / 2.0
        verts = np.array(
            [
                [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                [mid_x, y0, zr], [mid_x, y1, zr],
            ],
            dtype=np.float64,
        )
        faces = np.array(
            [
                [0, 1, 4],  # front gable
                [2, 3, 5],  # back gable
                [1, 2, 5], [1, 5, 4],  # right slope
                [0, 4, 5], [0, 5, 3],  # left slope
            ],
            dtype=np.int32,
        )

    return Mesh(vertices=verts, faces=faces)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _box_faces() -> np.ndarray:
    """12 triangles forming a box with vertices 0-3 (bottom) and 4-7 (top)."""
    return np.array(
        [
            # bottom
            [0, 2, 1], [0, 3, 2],
            # top
            [4, 5, 6], [4, 6, 7],
            # front
            [0, 1, 5], [0, 5, 4],
            # back
            [2, 3, 7], [2, 7, 6],
            # left
            [0, 4, 7], [0, 7, 3],
            # right
            [1, 2, 6], [1, 6, 5],
        ],
        dtype=np.int32,
    )


def _earcut_triangulate(boundary: list[tuple[float, float]]) -> list[tuple[int, int, int]]:
    """Robust triangulation using earcut — works for convex and concave polygons."""
    pts = np.array(boundary, dtype=np.float64)
    ring_ends = np.array([len(boundary)], dtype=np.uint32)
    indices = mapbox_earcut.triangulate_float64(pts, ring_ends)
    return [(indices[i], indices[i + 1], indices[i + 2]) for i in range(0, len(indices), 3)]
