"""Basic MEP clash (collision) detection using axis-aligned bounding boxes.

Checks for overlapping segments between different MEP systems.
"""

from __future__ import annotations

from dataclasses import dataclass

from promptbim.bim.mep.planner import MEPPlan, MEPRoute


@dataclass
class ClashReport:
    """A single clash between two MEP segments."""

    system_a: str
    system_b: str
    segment_a_start: tuple[float, float, float]
    segment_a_end: tuple[float, float, float]
    segment_b_start: tuple[float, float, float]
    segment_b_end: tuple[float, float, float]
    overlap_point: tuple[float, float, float]
    severity: str = "warning"  # "warning" or "error"


@dataclass
class ClashSummary:
    """Summary of all detected clashes."""

    total_clashes: int
    clashes: list[ClashReport]
    by_system_pair: dict[str, int]


def detect_clashes(
    mep_plan: MEPPlan,
    tolerance_m: float = 0.05,
) -> ClashSummary:
    """Detect bounding-box clashes between segments of different systems.

    Parameters
    ----------
    mep_plan:
        The complete MEP plan with routed segments.
    tolerance_m:
        Minimum separation distance; segments closer than this clash.

    Returns
    -------
    ClashSummary with all detected clashes.
    """
    # Collect all segments with their bounding boxes
    seg_list: list[tuple[str, tuple[float, float, float], tuple[float, float, float], float]] = []
    for route in mep_plan.routes:
        if not route.path.segments:
            continue
        radius = route.diameter_mm / 2000.0
        for seg in route.path.segments:
            seg_list.append((route.system, seg.start, seg.end, radius))

    clashes: list[ClashReport] = []
    pair_counts: dict[str, int] = {}

    for i in range(len(seg_list)):
        sys_a, sa_start, sa_end, ra = seg_list[i]
        min_a, max_a = _segment_bbox(sa_start, sa_end, ra + tolerance_m)

        for j in range(i + 1, len(seg_list)):
            sys_b, sb_start, sb_end, rb = seg_list[j]
            if sys_a == sys_b:
                continue  # only check cross-system clashes

            min_b, max_b = _segment_bbox(sb_start, sb_end, rb + tolerance_m)

            if _bbox_overlap(min_a, max_a, min_b, max_b):
                overlap = _overlap_center(min_a, max_a, min_b, max_b)
                pair_key = "_".join(sorted([sys_a, sys_b]))

                clashes.append(ClashReport(
                    system_a=sys_a,
                    system_b=sys_b,
                    segment_a_start=sa_start,
                    segment_a_end=sa_end,
                    segment_b_start=sb_start,
                    segment_b_end=sb_end,
                    overlap_point=overlap,
                ))
                pair_counts[pair_key] = pair_counts.get(pair_key, 0) + 1

    return ClashSummary(
        total_clashes=len(clashes),
        clashes=clashes,
        by_system_pair=pair_counts,
    )


# ---- geometry helpers ----

def _segment_bbox(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Axis-aligned bounding box for a segment with radius."""
    min_pt = (
        min(start[0], end[0]) - radius,
        min(start[1], end[1]) - radius,
        min(start[2], end[2]) - radius,
    )
    max_pt = (
        max(start[0], end[0]) + radius,
        max(start[1], end[1]) + radius,
        max(start[2], end[2]) + radius,
    )
    return min_pt, max_pt


def _bbox_overlap(
    min_a: tuple[float, float, float],
    max_a: tuple[float, float, float],
    min_b: tuple[float, float, float],
    max_b: tuple[float, float, float],
) -> bool:
    """Check if two AABBs overlap."""
    return (
        min_a[0] <= max_b[0] and max_a[0] >= min_b[0]
        and min_a[1] <= max_b[1] and max_a[1] >= min_b[1]
        and min_a[2] <= max_b[2] and max_a[2] >= min_b[2]
    )


def _overlap_center(
    min_a: tuple[float, float, float],
    max_a: tuple[float, float, float],
    min_b: tuple[float, float, float],
    max_b: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Center of the overlap region."""
    ox = (max(min_a[0], min_b[0]) + min(max_a[0], max_b[0])) / 2
    oy = (max(min_a[1], min_b[1]) + min(max_a[1], max_b[1])) / 2
    oz = (max(min_a[2], min_b[2]) + min(max_a[2], max_b[2])) / 2
    return (ox, oy, oz)
