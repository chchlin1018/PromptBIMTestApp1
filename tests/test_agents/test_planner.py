"""Tests for agents/planner.py — PlannerAgent and fallback box."""

from unittest.mock import patch

import pytest

from promptbim.agents.base import AgentResponse
from promptbim.agents.planner import PlannerAgent, _fallback_box
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan
from promptbim.schemas.requirement import BuildingRequirement
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


@pytest.fixture
def sample_requirement():
    return BuildingRequirement(
        raw_prompt="3-story office",
        building_type="commercial",
        num_stories=3,
        enhanced_description="A 3-story commercial office building",
    )


@pytest.fixture
def buildable_area():
    return [(2, 3), (28, 3), (28, 17), (2, 17)]


class TestFallbackBox:
    def test_generates_valid_plan(
        self, sample_land, sample_zoning, buildable_area, sample_requirement
    ):
        plan = _fallback_box(sample_land, sample_zoning, buildable_area, sample_requirement)

        assert isinstance(plan, BuildingPlan)
        assert len(plan.stories) == 3
        assert plan.building_bcr <= sample_zoning.bcr_limit + 0.01
        assert plan.building_far <= sample_zoning.far_limit + 0.01
        assert len(plan.building_footprint) == 4

    def test_stories_respect_height_limit(self, sample_land, sample_zoning, buildable_area):
        req = BuildingRequirement(
            raw_prompt="tall",
            num_stories=10,
            enhanced_description="Tall building",
        )
        plan = _fallback_box(sample_land, sample_zoning, buildable_area, req)

        max_stories = int(sample_zoning.height_limit_m / 3.0)
        assert len(plan.stories) <= max_stories

    def test_first_floor_has_door(
        self, sample_land, sample_zoning, buildable_area, sample_requirement
    ):
        plan = _fallback_box(sample_land, sample_zoning, buildable_area, sample_requirement)

        first_floor = plan.stories[0]
        assert any(o.opening_type == "door" for o in first_floor.openings)

    def test_walls_form_rectangle(
        self, sample_land, sample_zoning, buildable_area, sample_requirement
    ):
        plan = _fallback_box(sample_land, sample_zoning, buildable_area, sample_requirement)

        for story in plan.stories:
            assert len(story.walls) == 4
            assert all(w.wall_type == "exterior" for w in story.walls)


class TestPlannerAgent:
    @patch.object(PlannerAgent, "run")
    def test_fallback_on_error(
        self, mock_run, sample_land, sample_zoning, buildable_area, sample_requirement
    ):
        mock_run.return_value = AgentResponse(error="API error")

        agent = PlannerAgent()
        plan = agent.plan(sample_requirement, sample_land, sample_zoning, buildable_area)

        assert isinstance(plan, BuildingPlan)
        assert len(plan.stories) > 0
