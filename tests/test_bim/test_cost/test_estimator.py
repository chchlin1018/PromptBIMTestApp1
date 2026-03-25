"""Tests for bim/cost/estimator.py — Cost Estimation Engine."""

import pytest

from promptbim.bim.cost.estimator import CostEstimate, CostEstimator
from promptbim.schemas.plan import (
    BuildingPlan,
    OpeningDef,
    RoofPlan,
    StoryPlan,
    WallDef,
)


def _make_two_story_plan() -> BuildingPlan:
    """A 10x10m two-story box building."""
    fp = [(5, 5), (15, 5), (15, 15), (5, 15)]
    walls = [
        WallDef(start=(5, 5), end=(15, 5), wall_type="exterior"),
        WallDef(start=(15, 5), end=(15, 15), wall_type="exterior"),
        WallDef(start=(15, 15), end=(5, 15), wall_type="exterior"),
        WallDef(start=(5, 15), end=(5, 5), wall_type="exterior"),
    ]
    openings = [
        OpeningDef(wall_index=0, offset_m=4, width_m=1.0, height_m=2.1, opening_type="door"),
        OpeningDef(wall_index=1, offset_m=3, width_m=1.5, height_m=1.2,
                   sill_height_m=0.9, opening_type="window"),
    ]
    return BuildingPlan(
        name="Two Story Box",
        land_boundary=[(0, 0), (20, 0), (20, 20), (0, 20)],
        building_footprint=fp,
        building_bcr=0.25,
        building_far=0.50,
        stories=[
            StoryPlan(
                name="1F", elevation_m=0.0, height_m=3.0,
                walls=walls, openings=openings, slab_boundary=fp,
            ),
            StoryPlan(
                name="2F", elevation_m=3.0, height_m=3.0,
                walls=walls, openings=openings, slab_boundary=fp,
            ),
        ],
        roof=RoofPlan(roof_type="flat"),
    )


class TestCostEstimator:
    def test_estimate_returns_result(self):
        plan = _make_two_story_plan()
        est = CostEstimator().estimate(plan)
        assert isinstance(est, CostEstimate)
        assert est.project_name == "Two Story Box"

    def test_total_cost_positive(self):
        plan = _make_two_story_plan()
        est = CostEstimator().estimate(plan)
        assert est.total_cost_twd > 0

    def test_total_floor_area(self):
        plan = _make_two_story_plan()
        est = CostEstimator().estimate(plan)
        # 2 floors x 100 m2 = 200 m2
        assert abs(est.total_floor_area_sqm - 200.0) < 0.1

    def test_cost_per_sqm_reasonable(self):
        plan = _make_two_story_plan()
        est = CostEstimator().estimate(plan)
        # Typical Taiwan construction: ~30k-80k TWD/m2
        assert 10_000 < est.cost_per_sqm_twd < 200_000

    def test_breakdown_sums_to_total(self):
        plan = _make_two_story_plan()
        est = CostEstimator().estimate(plan)
        breakdown_total = sum(b.cost_twd for b in est.breakdown)
        assert abs(breakdown_total - est.total_cost_twd) < 1.0

    def test_breakdown_ratios_sum_to_one(self):
        plan = _make_two_story_plan()
        est = CostEstimator().estimate(plan)
        ratio_sum = sum(b.ratio for b in est.breakdown)
        assert abs(ratio_sum - 1.0) < 0.01

    def test_breakdown_has_multiple_categories(self):
        plan = _make_two_story_plan()
        est = CostEstimator().estimate(plan)
        assert len(est.breakdown) >= 4

    def test_to_dict(self):
        plan = _make_two_story_plan()
        est = CostEstimator().estimate(plan)
        d = est.to_dict()
        assert "project" in d
        assert "total_cost_twd" in d
        assert "breakdown" in d
        assert isinstance(d["breakdown"], list)
        assert d["total_cost_twd"] > 0

    def test_empty_plan(self):
        plan = BuildingPlan(name="Empty")
        est = CostEstimator().estimate(plan)
        assert est.total_cost_twd == 0
        assert est.total_floor_area_sqm == 0
        assert est.breakdown == []

    def test_line_items_populated(self):
        plan = _make_two_story_plan()
        est = CostEstimator().estimate(plan)
        assert len(est.line_items) > 0
        for li in est.line_items:
            assert li.total_twd > 0
            assert li.quantity > 0
            assert li.unit_price_twd > 0
