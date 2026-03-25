"""Tests for agents/enhancer.py — EnhancerAgent (mocked API)."""

import pytest
from unittest.mock import patch, MagicMock

from promptbim.agents.enhancer import EnhancerAgent
from promptbim.agents.base import AgentResponse
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
    return ZoningRules(far_limit=2.0, bcr_limit=0.6, height_limit_m=15.0)


class TestEnhancerAgent:
    @patch.object(EnhancerAgent, "run")
    def test_enhance_success(self, mock_run, sample_land, sample_zoning):
        mock_run.return_value = AgentResponse(
            text="ok",
            json_data={
                "building_type": "commercial",
                "num_stories": 3,
                "total_area_sqm": 900.0,
                "features": ["lobby", "elevator"],
                "constraints": ["BCR <= 60%"],
                "enhanced_description": "A 3-story commercial building with lobby.",
            },
        )

        agent = EnhancerAgent()
        req = agent.enhance("office building", sample_land, sample_zoning)

        assert req.building_type == "commercial"
        assert req.num_stories == 3
        assert req.total_area_sqm == 900.0
        assert "lobby" in req.features
        assert req.raw_prompt == "office building"

    @patch.object(EnhancerAgent, "run")
    def test_enhance_respects_height_limit(self, mock_run, sample_land, sample_zoning):
        mock_run.return_value = AgentResponse(
            text="ok",
            json_data={
                "building_type": "residential",
                "num_stories": 20,  # exceeds height limit
                "total_area_sqm": 500.0,
                "features": [],
                "constraints": [],
                "enhanced_description": "Tall building",
            },
        )

        agent = EnhancerAgent()
        req = agent.enhance("tall building", sample_land, sample_zoning)

        # 15m limit / 3m per story = 5 max
        assert req.num_stories <= 5

    @patch.object(EnhancerAgent, "run")
    def test_enhance_respects_far_limit(self, mock_run, sample_land, sample_zoning):
        mock_run.return_value = AgentResponse(
            text="ok",
            json_data={
                "building_type": "residential",
                "num_stories": 2,
                "total_area_sqm": 99999.0,  # exceeds FAR
                "features": [],
                "constraints": [],
                "enhanced_description": "Big building",
            },
        )

        agent = EnhancerAgent()
        req = agent.enhance("big building", sample_land, sample_zoning)

        max_area = sample_land.area_sqm * sample_zoning.far_limit
        assert req.total_area_sqm <= max_area

    @patch.object(EnhancerAgent, "run")
    def test_enhance_fallback_on_error(self, mock_run, sample_land, sample_zoning):
        mock_run.return_value = AgentResponse(error="API error")

        agent = EnhancerAgent()
        req = agent.enhance("fallback test", sample_land, sample_zoning)

        assert req.raw_prompt == "fallback test"
        assert req.building_type == "residential"  # default
