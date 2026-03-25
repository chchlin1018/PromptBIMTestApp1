"""Setback line calculation using shapely buffer."""

from __future__ import annotations

from shapely.geometry import Polygon
from shapely.ops import orient

from promptbim.schemas.land import LandParcel
from promptbim.schemas.zoning import ZoningRules


def compute_setback(
    parcel: LandParcel,
    zoning: ZoningRules,
) -> list[tuple[float, float]]:
    """Compute the buildable area after applying setback rules.

    Uses a uniform setback (average of all four sides) as a simplified
    inward buffer. For precise per-side setbacks, a more advanced approach
    with oriented edges would be needed.

    Returns:
        List of (x, y) coordinates for the buildable polygon boundary.
        Returns empty list if the setback eliminates the buildable area.
    """
    poly = Polygon(parcel.boundary)
    poly = orient(poly, sign=1.0)  # ensure counter-clockwise

    avg_setback = (
        zoning.setback_front_m
        + zoning.setback_back_m
        + zoning.setback_left_m
        + zoning.setback_right_m
    ) / 4.0

    buffered = poly.buffer(-avg_setback, join_style="mitre")

    if buffered.is_empty or not isinstance(buffered, Polygon):
        return []

    return list(buffered.exterior.coords[:-1])


def compute_setback_per_side(
    parcel: LandParcel,
    zoning: ZoningRules,
) -> list[tuple[float, float]]:
    """Compute buildable area with per-side setback distances.

    Assumes the boundary edges are ordered: front, right, back, left
    (starting from the south-facing edge for a typical rectangular parcel).
    For non-rectangular parcels, falls back to uniform setback.
    """
    coords = parcel.boundary
    if len(coords) != 4:
        return compute_setback(parcel, zoning)

    poly = Polygon(coords)
    poly = orient(poly, sign=1.0)
    ordered = list(poly.exterior.coords[:-1])

    setbacks = [
        zoning.setback_front_m,
        zoning.setback_right_m,
        zoning.setback_back_m,
        zoning.setback_left_m,
    ]

    import numpy as np

    # Inward offset each edge
    inward_points = []
    n = len(ordered)
    for i in range(n):
        p1 = np.array(ordered[i])
        p2 = np.array(ordered[(i + 1) % n])
        edge = p2 - p1
        normal = np.array([-edge[1], edge[0]])
        norm = np.linalg.norm(normal)
        if norm == 0:
            continue
        normal = normal / norm
        offset = normal * setbacks[i % len(setbacks)]
        inward_points.append((p1 + offset, p2 + offset))

    if len(inward_points) < 3:
        return compute_setback(parcel, zoning)

    # Find intersections of consecutive offset edges
    buildable_coords = []
    n = len(inward_points)
    for i in range(n):
        line1 = inward_points[i]
        line2 = inward_points[(i + 1) % n]
        pt = _line_intersection(line1[0], line1[1], line2[0], line2[1])
        if pt is not None:
            buildable_coords.append(tuple(pt))

    if len(buildable_coords) < 3:
        return compute_setback(parcel, zoning)

    result_poly = Polygon(buildable_coords)
    if result_poly.is_empty or not result_poly.is_valid:
        return compute_setback(parcel, zoning)

    return buildable_coords


def _line_intersection(
    p1: "np.ndarray", p2: "np.ndarray",
    p3: "np.ndarray", p4: "np.ndarray",
) -> "np.ndarray | None":
    """Find intersection point of two lines (p1-p2) and (p3-p4)."""
    import numpy as np

    d1 = p2 - p1
    d2 = p4 - p3
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) < 1e-10:
        return None
    t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / cross
    return p1 + t * d1
