"""Boundary confirmation logic for AI-recognized land parcels.

Handles candidate ranking, coordinate adjustment, and validation
before the recognized boundary enters the BIM generation pipeline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from promptbim.debug import get_logger
from promptbim.schemas.land import LandParcel

logger = get_logger("land.boundary_confirm")


@dataclass
class BoundaryCandidate:
    """A candidate boundary from AI recognition."""

    parcel: LandParcel
    confidence: float = 0.0
    notes: str = ""


@dataclass
class BoundaryConfirmation:
    """Result of the boundary confirmation flow."""

    candidates: list[BoundaryCandidate] = field(default_factory=list)
    selected_index: int = 0

    @property
    def selected(self) -> BoundaryCandidate | None:
        if 0 <= self.selected_index < len(self.candidates):
            return self.candidates[self.selected_index]
        return None

    @property
    def selected_parcel(self) -> LandParcel | None:
        c = self.selected
        return c.parcel if c else None

    def select(self, index: int) -> None:
        if 0 <= index < len(self.candidates):
            self.selected_index = index

    def add_candidate(self, parcel: LandParcel, confidence: float = 0.0, notes: str = "") -> None:
        self.candidates.append(BoundaryCandidate(parcel=parcel, confidence=confidence, notes=notes))

    def sort_by_confidence(self) -> None:
        self.candidates.sort(key=lambda c: c.confidence, reverse=True)
        self.selected_index = 0
        logger.debug(
            "Sorted %d candidates by confidence: %s",
            len(self.candidates),
            [f"{c.confidence:.2f}" for c in self.candidates],
        )


def adjust_vertex(
    parcel: LandParcel,
    vertex_index: int,
    new_x: float,
    new_y: float,
) -> LandParcel:
    """Adjust a single vertex of the parcel boundary.

    Returns a new LandParcel with updated boundary, area, and perimeter.
    """
    boundary = list(parcel.boundary)
    if not (0 <= vertex_index < len(boundary)):
        return parcel

    old = boundary[vertex_index]
    boundary[vertex_index] = (new_x, new_y)
    logger.debug("Adjusted vertex %d: (%.4f,%.4f) -> (%.4f,%.4f)", vertex_index, old[0], old[1], new_x, new_y)

    area = _shoelace_area(boundary)
    perimeter = _polygon_perimeter(boundary)

    return parcel.model_copy(
        update={
            "boundary": boundary,
            "area_sqm": area,
            "perimeter_m": perimeter,
        }
    )


def validate_boundary(boundary: list[tuple[float, float]]) -> list[str]:
    """Validate a boundary polygon and return a list of issues (empty = valid)."""
    issues: list[str] = []

    if len(boundary) < 3:
        issues.append("Boundary must have at least 3 vertices")
        return issues

    area = _shoelace_area(boundary)
    if area < 0.01:
        issues.append(f"Area too small: {area:.4f} m²")

    if _has_self_intersection(boundary):
        issues.append("Boundary has self-intersections")

    return issues


def _shoelace_area(coords: list[tuple[float, float]]) -> float:
    n = len(coords)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    return abs(area) / 2.0


def _polygon_perimeter(coords: list[tuple[float, float]]) -> float:
    n = len(coords)
    perimeter = 0.0
    for i in range(n):
        j = (i + 1) % n
        dx = coords[j][0] - coords[i][0]
        dy = coords[j][1] - coords[i][1]
        perimeter += math.sqrt(dx * dx + dy * dy)
    return perimeter


def _has_self_intersection(coords: list[tuple[float, float]]) -> bool:
    """Simple O(n^2) self-intersection check for small polygons."""
    n = len(coords)
    if n < 4:
        return False

    def _segments_intersect(p1, p2, p3, p4):
        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        d1 = cross(p3, p4, p1)
        d2 = cross(p3, p4, p2)
        d3 = cross(p1, p2, p3)
        d4 = cross(p1, p2, p4)

        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
           ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True
        return False

    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            p1 = coords[i]
            p2 = coords[(i + 1) % n]
            p3 = coords[j]
            p4 = coords[(j + 1) % n]
            if _segments_intersect(p1, p2, p3, p4):
                return True
    return False
