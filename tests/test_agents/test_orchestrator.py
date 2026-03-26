"""Tests for agents/orchestrator.py — Pipeline + _poly_area."""

from unittest.mock import patch

import pytest

from promptbim.agents.orchestrator import Orchestrator, _poly_area
from promptbim.schemas.land import LandParcel
from promptbim.schemas.zoning import ZoningRules


@pytest.fixture
def sample_land():
    return LandParcel(
        name="Test Parcel",
        boundary=[(0, 0), (30, 0), (30, 20), (0, 20)],
        area_sqm=600.0,
    )


@pytest.fixture
def sample_zoning():
    return ZoningRules(
        far_limit=2.0,
        bcr_limit=0.6,
        height_limit_m=15.0,
        setback_front_m=3.0,
        setback_back_m=3.0,
        setback_left_m=2.0,
        setback_right_m=2.0,
    )


class TestPolyArea:
    def test_rectangle(self):
        coords = [(0, 0), (10, 0), (10, 5), (0, 5)]
        assert abs(_poly_area(coords) - 50.0) < 0.01

    def test_triangle(self):
        coords = [(0, 0), (10, 0), (5, 8)]
        assert abs(_poly_area(coords) - 40.0) < 0.01

    def test_empty(self):
        assert _poly_area([]) == 0.0

    def test_two_points(self):
        assert _poly_area([(0, 0), (1, 1)]) == 0.0


class TestOrchestrator:
    @patch("promptbim.agents.enhancer.EnhancerAgent")
    @patch("promptbim.agents.planner.PlannerAgent")
    @patch("promptbim.agents.checker.CheckerAgent")
    def test_generate_with_fallbacks(
        self, MockChecker, MockPlanner, MockEnhancer, sample_land, sample_zoning, tmp_path
    ):
        """Test pipeline runs end-to-end using fallback (no API)."""
        from promptbim.agents.checker import CheckResult
        from promptbim.agents.planner import _fallback_box
        from promptbim.land.setback import compute_setback
        from promptbim.schemas.requirement import BuildingRequirement

        # Mock Enhancer to return a basic requirement
        req = BuildingRequirement(
            raw_prompt="office",
            building_type="commercial",
            num_stories=2,
            enhanced_description="2-story office",
        )
        mock_enhancer = MockEnhancer.return_value
        mock_enhancer.enhance.return_value = req

        # Mock Planner to return a fallback box
        buildable_area = compute_setback(sample_land, sample_zoning)
        plan = _fallback_box(sample_land, sample_zoning, buildable_area, req)
        mock_planner = MockPlanner.return_value
        mock_planner.plan.return_value = plan

        # Mock Checker to pass
        mock_checker = MockChecker.return_value
        mock_checker.check.return_value = CheckResult()

        orch = Orchestrator(output_dir=tmp_path)
        result = orch.generate("office building", sample_land, sample_zoning)

        assert result.success
        assert result.building_name
