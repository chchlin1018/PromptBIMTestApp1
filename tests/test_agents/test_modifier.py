"""Tests for agents/modifier.py — Modifier Agent + impact propagation."""

from unittest.mock import MagicMock, patch

import pytest

from promptbim.agents.modifier import (
    IMPACT_MATRIX,
    ModifierAgent,
    _poly_area,
    _recalculate_metrics,
    _scale_polygon,
    compute_impacts,
)
from promptbim.schemas.modification import (
    ModificationHistory,
    ModificationRecord,
    ModificationType,
)
from promptbim.schemas.plan import (
    BuildingPlan,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)
from promptbim.schemas.zoning import ZoningRules


@pytest.fixture
def sample_plan():
    """A 3-story box building on a 30x20 land."""
    footprint = [(3, 3), (27, 3), (27, 17), (3, 17)]
    land = [(0, 0), (30, 0), (30, 20), (0, 20)]
    stories = []
    for i in range(3):
        stories.append(
            StoryPlan(
                name=f"{i + 1}F",
                elevation_m=i * 3.0,
                height_m=3.0,
                walls=[
                    WallDef(start=(3, 3), end=(27, 3), wall_type="exterior"),
                    WallDef(start=(27, 3), end=(27, 17), wall_type="exterior"),
                    WallDef(start=(27, 17), end=(3, 17), wall_type="exterior"),
                    WallDef(start=(3, 17), end=(3, 3), wall_type="exterior"),
                ],
                spaces=[
                    SpaceDef(
                        name=f"Room {i + 1}F",
                        boundary=footprint,
                        space_type="office",
                        area_sqm=336.0,
                    )
                ],
                slab_boundary=footprint,
            )
        )

    return BuildingPlan(
        name="Test Building",
        land_boundary=land,
        buildable_area=[(2, 2), (28, 2), (28, 18), (2, 18)],
        building_footprint=footprint,
        building_bcr=0.56,
        building_far=1.68,
        stories=stories,
        roof=RoofPlan(roof_type="flat"),
    )


@pytest.fixture
def sample_zoning():
    return ZoningRules(
        far_limit=3.0,
        bcr_limit=0.6,
        height_limit_m=36.0,
    )


# ---------------------------------------------------------------------------
# Impact propagation
# ---------------------------------------------------------------------------


class TestImpactMatrix:
    def test_stories_impacts_exist(self):
        impacts = IMPACT_MATRIX[ModificationType.STORIES]
        component_names = [c for c, _ in impacts]
        assert "structure" in component_names
        assert "FAR" in component_names

    def test_all_types_have_entries(self):
        for mod_type in ModificationType:
            assert mod_type in IMPACT_MATRIX


class TestComputeImpacts:
    def test_stories_change_detects_diff(self, sample_plan):
        old = sample_plan
        new = sample_plan.model_copy(deep=True)
        # Add 3 more stories
        for i in range(3, 6):
            new.stories.append(
                StoryPlan(
                    name=f"{i + 1}F",
                    elevation_m=i * 3.0,
                    height_m=3.0,
                    slab_boundary=new.building_footprint,
                )
            )
        new.building_far = 3.36

        impacts = compute_impacts(ModificationType.STORIES, old, new)
        assert len(impacts) > 0
        # Should detect structure change (stories 3 → 6)
        structure_impacts = [i for i in impacts if i.component == "structure"]
        assert len(structure_impacts) == 1
        assert structure_impacts[0].before_value == "3"
        assert structure_impacts[0].after_value == "6"

    def test_no_change_still_returns_items(self, sample_plan):
        # Same plan → only items where before != after are included
        impacts = compute_impacts(ModificationType.STORIES, sample_plan, sample_plan)
        # All items should have same before/after so none should be included
        assert len(impacts) == 0


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


class TestPolyArea:
    def test_rectangle(self):
        assert abs(_poly_area([(0, 0), (10, 0), (10, 5), (0, 5)]) - 50.0) < 0.01

    def test_empty(self):
        assert _poly_area([]) == 0.0


class TestScalePolygon:
    def test_scale_up(self):
        rect = [(0, 0), (10, 0), (10, 10), (0, 10)]
        scaled = _scale_polygon(rect, 2.0)
        # Centroid is (5, 5). Each point should be 2x distance from centroid.
        assert abs(scaled[0][0] - (-5.0)) < 0.01
        assert abs(scaled[0][1] - (-5.0)) < 0.01
        assert abs(scaled[2][0] - 15.0) < 0.01

    def test_scale_1_unchanged(self):
        rect = [(0, 0), (10, 0), (10, 10), (0, 10)]
        scaled = _scale_polygon(rect, 1.0)
        for orig, sc in zip(rect, scaled):
            assert abs(orig[0] - sc[0]) < 0.01
            assert abs(orig[1] - sc[1]) < 0.01

    def test_empty(self):
        assert _scale_polygon([], 2.0) == []


class TestRecalculateMetrics:
    def test_recalculates_bcr_far(self, sample_plan):
        plan = sample_plan.model_copy(deep=True)
        plan.building_bcr = 0.0
        plan.building_far = 0.0
        result = _recalculate_metrics(plan)
        assert result.building_bcr > 0
        assert result.building_far > 0


# ---------------------------------------------------------------------------
# ModificationHistory
# ---------------------------------------------------------------------------


class TestModificationHistory:
    def test_add_and_undo(self):
        history = ModificationHistory()
        assert not history.can_undo

        record = ModificationRecord(command="test", plan_snapshot_json={})
        history.add(record)
        assert history.can_undo
        assert history.latest == record

        popped = history.pop_last()
        assert popped == record
        assert not history.can_undo

    def test_pop_empty(self):
        history = ModificationHistory()
        assert history.pop_last() is None


# ---------------------------------------------------------------------------
# ModifierAgent (with mocked Claude)
# ---------------------------------------------------------------------------


class TestModifierAgent:
    @patch("promptbim.agents.modifier.BaseAgent.run")
    def test_modify_stories(self, mock_run, sample_plan, sample_zoning):
        """Test changing to 5 stories via mocked Claude intent parse."""
        mock_run.return_value = MagicMock(
            ok=True,
            json_data={
                "modification_type": "stories",
                "parameters": {"target_stories": 5},
                "confidence": 0.9,
            },
        )

        agent = ModifierAgent()
        new_plan, record = agent.modify("change to 5 stories", sample_plan, sample_zoning)

        assert record.success
        assert len(new_plan.stories) == 5
        assert record.intent.modification_type == ModificationType.STORIES
        assert len(record.impacts) > 0

    @patch("promptbim.agents.modifier.BaseAgent.run")
    def test_modify_stories_reduces(self, mock_run, sample_plan, sample_zoning):
        """Test reducing stories from 3 to 1."""
        mock_run.return_value = MagicMock(
            ok=True,
            json_data={
                "modification_type": "stories",
                "parameters": {"target_stories": 1},
                "confidence": 0.9,
            },
        )

        agent = ModifierAgent()
        new_plan, record = agent.modify("reduce to 1 story", sample_plan, sample_zoning)

        assert record.success
        assert len(new_plan.stories) == 1

    @patch("promptbim.agents.modifier.BaseAgent.run")
    def test_modify_roof(self, mock_run, sample_plan, sample_zoning):
        """Test changing roof type."""
        mock_run.return_value = MagicMock(
            ok=True,
            json_data={
                "modification_type": "roof",
                "parameters": {"roof_type": "gable", "slope_degrees": 30},
                "confidence": 0.8,
            },
        )

        agent = ModifierAgent()
        new_plan, record = agent.modify("change to gable roof", sample_plan, sample_zoning)

        assert record.success
        assert new_plan.roof.roof_type == "gable"
        assert new_plan.roof.slope_degrees == 30.0

    @patch("promptbim.agents.modifier.BaseAgent.run")
    def test_modify_height(self, mock_run, sample_plan, sample_zoning):
        """Test changing story height."""
        mock_run.return_value = MagicMock(
            ok=True,
            json_data={
                "modification_type": "height",
                "parameters": {"story_height_m": 3.5},
                "confidence": 0.85,
            },
        )

        agent = ModifierAgent()
        new_plan, record = agent.modify("set floor height to 3.5m", sample_plan, sample_zoning)

        assert record.success
        for s in new_plan.stories:
            assert s.height_m == 3.5
        assert new_plan.stories[1].elevation_m == 3.5

    @patch("promptbim.agents.modifier.BaseAgent.run")
    def test_undo(self, mock_run, sample_plan, sample_zoning):
        """Test undo restores previous plan."""
        mock_run.return_value = MagicMock(
            ok=True,
            json_data={
                "modification_type": "stories",
                "parameters": {"target_stories": 9},
                "confidence": 0.9,
            },
        )

        agent = ModifierAgent()
        new_plan, record = agent.modify("change to 9 stories", sample_plan, sample_zoning)
        assert len(new_plan.stories) == 9

        restored, undone_record = agent.undo(new_plan)
        assert restored is not None
        assert len(restored.stories) == 3  # original
        assert undone_record.command == "change to 9 stories"

    @patch("promptbim.agents.modifier.BaseAgent.run")
    def test_undo_empty(self, mock_run, sample_plan):
        """Test undo with no history returns None."""
        agent = ModifierAgent()
        restored, record = agent.undo(sample_plan)
        assert restored is None
        assert record is None

    def test_fallback_parse_stories(self):
        """Test keyword-based fallback parser for stories."""
        agent = ModifierAgent()
        intent = agent._fallback_parse("change to 9 stories")
        assert intent.modification_type == ModificationType.STORIES
        assert intent.parameters.get("target_stories") == 9

    def test_fallback_parse_stories_chinese(self):
        """Test keyword-based fallback parser for Chinese."""
        agent = ModifierAgent()
        intent = agent._fallback_parse("改為9層")
        assert intent.modification_type == ModificationType.STORIES
        assert intent.parameters.get("target_stories") == 9

    def test_fallback_parse_roof(self):
        agent = ModifierAgent()
        intent = agent._fallback_parse("change to gable roof")
        assert intent.modification_type == ModificationType.ROOF
        assert intent.parameters.get("roof_type") == "gable"

    @patch("promptbim.agents.modifier.BaseAgent.run")
    def test_metrics_recalculated_after_modify(self, mock_run, sample_plan, sample_zoning):
        """BCR/FAR should be updated after modification."""
        mock_run.return_value = MagicMock(
            ok=True,
            json_data={
                "modification_type": "stories",
                "parameters": {"target_stories": 6},
                "confidence": 0.9,
            },
        )
        agent = ModifierAgent()
        new_plan, record = agent.modify("6 stories", sample_plan, sample_zoning)

        assert new_plan.building_far > sample_plan.building_far

    @patch("promptbim.agents.modifier.BaseAgent.run")
    def test_stories_capped_by_height_limit(self, mock_run, sample_plan):
        """Stories should not exceed height limit / 3."""
        zoning = ZoningRules(height_limit_m=15.0)  # max 5 stories
        mock_run.return_value = MagicMock(
            ok=True,
            json_data={
                "modification_type": "stories",
                "parameters": {"target_stories": 20},
                "confidence": 0.9,
            },
        )
        agent = ModifierAgent()
        new_plan, record = agent.modify("20 stories", sample_plan, zoning)
        assert len(new_plan.stories) == 5

    @patch("promptbim.agents.modifier.BaseAgent.run")
    def test_modification_history_grows(self, mock_run, sample_plan, sample_zoning):
        """History should track all modifications."""
        mock_run.return_value = MagicMock(
            ok=True,
            json_data={
                "modification_type": "stories",
                "parameters": {"target_stories": 4},
                "confidence": 0.9,
            },
        )
        agent = ModifierAgent()
        plan = sample_plan
        for _ in range(3):
            plan, _ = agent.modify("add story", plan, sample_zoning)

        assert len(agent.history.records) == 3
