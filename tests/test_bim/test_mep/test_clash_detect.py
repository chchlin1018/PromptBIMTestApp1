"""Tests for bim/mep/clash_detect.py — Basic collision detection."""

import pytest

from promptbim.bim.mep.clash_detect import (
    ClashSummary,
    detect_clashes,
    _bbox_overlap,
    _segment_bbox,
)
from promptbim.bim.mep.pathfinder import PathSegment, RoutePath
from promptbim.bim.mep.planner import MEPPlan, MEPRoute


def _make_route(system: str, start: tuple, end: tuple, diameter: float = 50) -> MEPRoute:
    rp = RoutePath.from_waypoints([start, end], grid_size=0.3)
    return MEPRoute(
        system=system,
        route_type="branch",
        diameter_mm=diameter,
        path=rp,
        floor="1F",
    )


class TestClashDetect:
    def test_no_clashes_when_far_apart(self):
        plan = MEPPlan(routes=[
            _make_route("plumbing", (0, 0, 0), (5, 0, 0)),
            _make_route("electrical", (0, 10, 0), (5, 10, 0)),
        ])
        result = detect_clashes(plan)
        assert result.total_clashes == 0

    def test_clashes_when_overlapping(self):
        plan = MEPPlan(routes=[
            _make_route("plumbing", (0, 0, 0), (5, 0, 0), diameter=100),
            _make_route("electrical", (2, 0, 0), (7, 0, 0), diameter=100),
        ])
        result = detect_clashes(plan, tolerance_m=0.1)
        assert result.total_clashes > 0
        assert "electrical_plumbing" in result.by_system_pair or "plumbing_electrical" in result.by_system_pair

    def test_same_system_not_counted(self):
        plan = MEPPlan(routes=[
            _make_route("plumbing", (0, 0, 0), (5, 0, 0), diameter=100),
            _make_route("plumbing", (2, 0, 0), (7, 0, 0), diameter=100),
        ])
        result = detect_clashes(plan)
        assert result.total_clashes == 0

    def test_empty_plan(self):
        plan = MEPPlan()
        result = detect_clashes(plan)
        assert result.total_clashes == 0


class TestBBoxHelpers:
    def test_segment_bbox(self):
        min_pt, max_pt = _segment_bbox((1, 2, 3), (4, 5, 6), radius=0.1)
        assert min_pt[0] < 1
        assert max_pt[0] > 4
        assert min_pt[2] < 3

    def test_bbox_overlap_yes(self):
        assert _bbox_overlap((0, 0, 0), (2, 2, 2), (1, 1, 1), (3, 3, 3))

    def test_bbox_overlap_no(self):
        assert not _bbox_overlap((0, 0, 0), (1, 1, 1), (2, 2, 2), (3, 3, 3))

    def test_bbox_overlap_touching(self):
        assert _bbox_overlap((0, 0, 0), (1, 1, 1), (1, 0, 0), (2, 1, 1))
