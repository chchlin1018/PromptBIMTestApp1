"""Tests for viz/cost_charts.py — non-GUI chart data tests."""

import pytest

from promptbim.bim.cost.estimator import CostBreakdown, CostEstimate


class TestCostEstimateData:
    def test_cost_breakdown_ratios(self):
        breakdowns = [
            CostBreakdown(category="structure", label="Structure", cost_twd=5_000_000, ratio=0.5),
            CostBreakdown(category="mep", label="MEP", cost_twd=3_000_000, ratio=0.3),
            CostBreakdown(category="envelope", label="Envelope", cost_twd=2_000_000, ratio=0.2),
        ]
        est = CostEstimate(
            project_name="Test",
            total_cost_twd=10_000_000,
            total_floor_area_sqm=200,
            cost_per_sqm_twd=50_000,
            breakdown=breakdowns,
        )
        assert sum(b.ratio for b in est.breakdown) == pytest.approx(1.0)
        assert est.to_dict()["total_cost_twd"] == 10_000_000

    def test_empty_breakdown(self):
        est = CostEstimate(
            project_name="Empty",
            total_cost_twd=0,
            total_floor_area_sqm=0,
            cost_per_sqm_twd=0,
        )
        assert est.breakdown == []
        d = est.to_dict()
        assert d["breakdown"] == []
