"""Setback line calculation using shapely buffer."""

from __future__ import annotations

from shapely.geometry import Polygon
from shapely.ops import orient

from promptbim.debug import get_logger
from promptbim.schemas.land import LandParcel
from promptbim.schemas.zoning import ZoningRules

logger = get_logger("land.setback")


def compute_setback(
    parcel: LandParcel,
    zoning: ZoningRules,
) -> list[tuple[float, float]]:
    """Compute the buildable area after applying uniform setback rules.

    Uses the average of all four sides as a simplified inward buffer.

    Returns:
        List of (x, y) coordinates for the buildable polygon boundary.
        Returns empty list if the setback eliminates the buildable area.
    """
    return uniform_setback(parcel.boundary, _avg_setback(zoning))


def uniform_setback(
    boundary: list[tuple[float, float]],
    distance: float,
) -> list[tuple[float, float]]:
    """Apply a uniform inward setback to a polygon boundary.

    Returns empty list if the setback eliminates the buildable area.
    """
    poly = Polygon(boundary)
    poly = orient(poly, sign=1.0)

    logger.debug("Uniform setback=%.1fm, original area=%.1f sqm", distance, poly.area)

    buffered = poly.buffer(-distance, join_style="mitre")

    if buffered.is_empty or not isinstance(buffered, Polygon):
        logger.debug("Setback eliminated all buildable area")
        return []

    result = list(buffered.exterior.coords[:-1])
    logger.debug("Result area=%.1f sqm, vertices=%d", Polygon(result).area, len(result))
    return result


def per_side_setback(
    polygon: list[tuple[float, float]],
    setbacks: dict,
) -> list[tuple[float, float]]:
    """Compute buildable area with per-side setback distances.

    Args:
        polygon: Boundary coordinates [(x,y), ...].
        setbacks: Dict with keys 'front', 'right', 'back', 'left' (float metres).
            For polygons with > 4 edges, falls back to uniform setback using the
            average of all provided values.

    Returns:
        List of (x, y) coordinates for the buildable polygon, or empty list.
    """
    import numpy as np

    front = setbacks.get("front", 0.0)
    right = setbacks.get("right", 0.0)
    back = setbacks.get("back", 0.0)
    left = setbacks.get("left", 0.0)

    # Fallback for non-quad polygons
    if len(polygon) > 4:
        avg = (front + right + back + left) / 4.0
        logger.debug("Polygon has %d sides (> 4), falling back to uniform %.1fm", len(polygon), avg)
        return uniform_setback(polygon, avg)

    poly = Polygon(polygon)
    poly = orient(poly, sign=1.0)
    ordered = list(poly.exterior.coords[:-1])

    side_distances = [front, right, back, left]

    # Inward offset each edge
    inward_lines = []
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
        offset = normal * side_distances[i % len(side_distances)]
        inward_lines.append((p1 + offset, p2 + offset))

    if len(inward_lines) < 3:
        avg = (front + right + back + left) / 4.0
        return uniform_setback(polygon, avg)

    # Find intersections of consecutive offset edges
    buildable_coords = []
    n = len(inward_lines)
    for i in range(n):
        line1 = inward_lines[i]
        line2 = inward_lines[(i + 1) % n]
        pt = _line_intersection(line1[0], line1[1], line2[0], line2[1])
        if pt is not None:
            buildable_coords.append(tuple(pt))

    if len(buildable_coords) < 3:
        avg = (front + right + back + left) / 4.0
        return uniform_setback(polygon, avg)

    result_poly = Polygon(buildable_coords)
    if result_poly.is_empty or not result_poly.is_valid:
        avg = (front + right + back + left) / 4.0
        return uniform_setback(polygon, avg)

    return buildable_coords


def compute_setback_per_side(
    parcel: LandParcel,
    zoning: ZoningRules,
) -> list[tuple[float, float]]:
    """Compute buildable area with per-side setback distances (legacy API).

    Assumes the boundary edges are ordered: front, right, back, left.
    For non-rectangular parcels, falls back to uniform setback.
    """
    return per_side_setback(
        parcel.boundary,
        {
            "front": zoning.setback_front_m,
            "right": zoning.setback_right_m,
            "back": zoning.setback_back_m,
            "left": zoning.setback_left_m,
        },
    )


def _avg_setback(zoning: ZoningRules) -> float:
    """Return the average setback distance from a ZoningRules instance."""
    return (
        zoning.setback_front_m
        + zoning.setback_back_m
        + zoning.setback_left_m
        + zoning.setback_right_m
    ) / 4.0


def _line_intersection(
    p1: "np.ndarray",
    p2: "np.ndarray",
    p3: "np.ndarray",
    p4: "np.ndarray",
) -> "np.ndarray | None":
    """Find intersection point of two lines (p1-p2) and (p3-p4)."""

    d1 = p2 - p1
    d2 = p4 - p3
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) < 1e-10:
        return None
    t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / cross
    return p1 + t * d1
