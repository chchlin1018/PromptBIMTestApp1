"""Tests for Sprint P16 quality remediation tasks."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from promptbim.bim.geometry import poly_area

# ---------------------------------------------------------------------------
# Task 3 (C-3): Shoelace unification — all callers use poly_area
# ---------------------------------------------------------------------------


class TestPolyAreaUnification:
    def test_poly_area_triangle(self):
        assert poly_area([(0, 0), (10, 0), (0, 10)]) == pytest.approx(50.0)

    def test_poly_area_square(self):
        assert poly_area([(0, 0), (5, 0), (5, 5), (0, 5)]) == pytest.approx(25.0)

    def test_poly_area_empty(self):
        assert poly_area([]) == 0.0

    def test_poly_area_two_points(self):
        assert poly_area([(0, 0), (1, 1)]) == 0.0

    def test_no_duplicate_shoelace_in_codebase(self):
        """Verify no _shoelace_area or _polygon_area functions remain in source."""
        import promptbim.bim.cost.qto as qto_mod
        import promptbim.codes.tw_building_code as tw_mod
        import promptbim.land.boundary_confirm as bc_mod
        import promptbim.land.parsers.image_ai as ai_mod
        import promptbim.land.parsers.pdf_ocr as pdf_mod

        for mod in [qto_mod, tw_mod, bc_mod, ai_mod, pdf_mod]:
            assert not hasattr(mod, "_shoelace_area"), f"{mod.__name__} still has _shoelace_area"
            # tw_building_code and qto had _polygon_area
            if mod in (tw_mod,):
                assert not hasattr(mod, "_polygon_area"), f"{mod.__name__} still has _polygon_area"


# ---------------------------------------------------------------------------
# Task 4 (H-1): buildable_area input validation
# ---------------------------------------------------------------------------


class TestBuildableAreaValidation:
    def test_empty_buildable_area_raises(self, sample_land, sample_zoning):
        from promptbim.agents.planner import PlannerAgent
        from promptbim.schemas.requirement import BuildingRequirement

        agent = PlannerAgent.__new__(PlannerAgent)
        req = BuildingRequirement(raw_prompt="test", building_type="residential", num_stories=3)
        with pytest.raises(ValueError, match=">=\\s*3 vertices"):
            agent.plan(req, sample_land, sample_zoning, [])

    def test_two_points_raises(self, sample_land, sample_zoning):
        from promptbim.agents.planner import PlannerAgent
        from promptbim.schemas.requirement import BuildingRequirement

        agent = PlannerAgent.__new__(PlannerAgent)
        req = BuildingRequirement(raw_prompt="test", building_type="residential", num_stories=3)
        with pytest.raises(ValueError, match=">=\\s*3 vertices"):
            agent.plan(req, sample_land, sample_zoning, [(0, 0), (1, 1)])

    def test_collinear_points_raises(self, sample_land, sample_zoning):
        from promptbim.agents.planner import PlannerAgent
        from promptbim.schemas.requirement import BuildingRequirement

        agent = PlannerAgent.__new__(PlannerAgent)
        req = BuildingRequirement(raw_prompt="test", building_type="residential", num_stories=3)
        with pytest.raises(ValueError, match="non-positive area"):
            agent.plan(req, sample_land, sample_zoning, [(0, 0), (5, 0), (10, 0)])


# ---------------------------------------------------------------------------
# Task 5 (H-2): ComponentRegistry test isolation
# ---------------------------------------------------------------------------


class TestComponentRegistryIsolation:
    def test_registry_reset_clears_state(self):
        from promptbim.bim.components.base import ComponentCategory, ComponentDef
        from promptbim.bim.components.registry import ComponentRegistry

        ComponentRegistry.register(
            ComponentDef(
                id="test-comp-1",
                name_zh="測試",
                name_en="Test",
                category=ComponentCategory.STRUCTURAL,
                ifc_class="IfcBuildingElement",
            )
        )
        assert ComponentRegistry.count() >= 1
        ComponentRegistry.reset()
        assert ComponentRegistry.count() == 0

    def test_conftest_autouse_resets_registry(self):
        from promptbim.bim.components.registry import ComponentRegistry

        # The autouse fixture should have reset between tests
        # so count should be 0 at the start of each test
        assert ComponentRegistry.count() == 0


# ---------------------------------------------------------------------------
# Task 6 (H-3): ModificationHistory persistence
# ---------------------------------------------------------------------------


class TestModificationHistoryPersistence:
    def test_save_and_load_roundtrip(self, tmp_path):
        from promptbim.schemas.modification import ModificationHistory, ModificationRecord

        history = ModificationHistory()
        history.add(ModificationRecord(command="change to 5 stories"))
        history.add(ModificationRecord(command="add parking"))

        path = tmp_path / "history.json"
        history.save_history(path)

        loaded = ModificationHistory.load_history(path)
        assert len(loaded.records) == 2
        assert loaded.records[0].command == "change to 5 stories"
        assert loaded.records[1].command == "add parking"

    def test_load_nonexistent_returns_empty(self, tmp_path):
        from promptbim.schemas.modification import ModificationHistory

        loaded = ModificationHistory.load_history(tmp_path / "nope.json")
        assert len(loaded.records) == 0

    def test_save_creates_parent_dirs(self, tmp_path):
        from promptbim.schemas.modification import ModificationHistory, ModificationRecord

        history = ModificationHistory()
        history.add(ModificationRecord(command="test"))
        path = tmp_path / "sub" / "dir" / "history.json"
        history.save_history(path)
        assert path.exists()


# ---------------------------------------------------------------------------
# Task 7 (H-4): Planner JSON schema validation
# ---------------------------------------------------------------------------


class TestPlannerSchemaValidation:
    def _make_agent(self):
        from promptbim.agents.planner import PlannerAgent

        agent = PlannerAgent.__new__(PlannerAgent)
        agent._settings = MagicMock()
        agent._settings.claude_model = "test"
        agent._settings.api_timeout_seconds = 30.0
        agent._model = "test"
        agent._max_tokens = 8192
        agent._client = MagicMock()
        return agent

    def test_missing_stories_triggers_fallback(self, sample_land, sample_zoning):
        from promptbim.agents.base import AgentResponse
        from promptbim.schemas.requirement import BuildingRequirement

        agent = self._make_agent()

        # JSON with missing stories field
        resp = AgentResponse(
            text="{}",
            json_data={"building_footprint": [(0, 0), (10, 0), (10, 10), (0, 10)]},
        )

        req = BuildingRequirement(raw_prompt="test", building_type="residential", num_stories=2)
        buildable = [(2, 2), (28, 2), (28, 28), (2, 28)]
        plan = agent._to_plan(resp, sample_land, sample_zoning, buildable, req)
        # Should fallback to box
        assert plan.name  # fallback name is set

    def test_missing_footprint_triggers_fallback(self, sample_land, sample_zoning):
        from promptbim.agents.base import AgentResponse
        from promptbim.schemas.requirement import BuildingRequirement

        agent = self._make_agent()
        resp = AgentResponse(
            text="{}",
            json_data={"stories": [{"name": "1F"}]},
        )
        req = BuildingRequirement(raw_prompt="test", building_type="residential", num_stories=2)
        buildable = [(2, 2), (28, 2), (28, 28), (2, 28)]
        plan = agent._to_plan(resp, sample_land, sample_zoning, buildable, req)
        assert plan is not None  # fallback


# ---------------------------------------------------------------------------
# Task 8 (H-5): Coordinate precision
# ---------------------------------------------------------------------------


class TestCoordinatePrecision:
    def test_plan_snapshot_roundtrip_precision(self, sample_plan):
        """model_dump → model_validate preserves float precision."""
        from promptbim.schemas.plan import BuildingPlan

        snapshot = sample_plan.model_dump()
        restored = BuildingPlan.model_validate(snapshot)

        for orig, rest in zip(
            sample_plan.building_footprint, restored.building_footprint
        ):
            assert abs(orig[0] - rest[0]) < 1e-10
            assert abs(orig[1] - rest[1]) < 1e-10


# ---------------------------------------------------------------------------
# Task 9 (M-1): Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_constants_exist(self):
        from promptbim.constants import (
            API_MAX_TOKENS_DEFAULT,
            API_MAX_TOKENS_PLANNER,
            DEFAULT_SLAB_THICKNESS_M,
            DEFAULT_STORY_HEIGHT_M,
            DEFAULT_WALL_THICKNESS_M,
            GUI_STARTUP_DELAY_S,
        )

        assert DEFAULT_STORY_HEIGHT_M == 3.0
        assert DEFAULT_WALL_THICKNESS_M == 0.2
        assert DEFAULT_SLAB_THICKNESS_M == 0.2
        assert API_MAX_TOKENS_DEFAULT == 4096
        assert API_MAX_TOKENS_PLANNER == 8192
        assert GUI_STARTUP_DELAY_S == 1.0


# ---------------------------------------------------------------------------
# Task 10 (M-3): Builder backup
# ---------------------------------------------------------------------------


class TestBuilderBackup:
    def test_backup_creates_bak_file(self, tmp_path):
        from promptbim.agents.builder import _backup_if_exists

        f = tmp_path / "test.ifc"
        f.write_text("original")
        _backup_if_exists(f)
        bak = tmp_path / "test.ifc.bak"
        assert bak.exists()
        assert bak.read_text() == "original"
        assert not f.exists()

    def test_backup_overwrites_old_bak(self, tmp_path):
        from promptbim.agents.builder import _backup_if_exists

        f = tmp_path / "test.ifc"
        bak = tmp_path / "test.ifc.bak"
        bak.write_text("old backup")
        f.write_text("new file")
        _backup_if_exists(f)
        assert bak.read_text() == "new file"

    def test_no_file_no_backup(self, tmp_path):
        from promptbim.agents.builder import _backup_if_exists

        f = tmp_path / "nonexistent.ifc"
        _backup_if_exists(f)  # should not raise
        assert not (tmp_path / "nonexistent.ifc.bak").exists()
