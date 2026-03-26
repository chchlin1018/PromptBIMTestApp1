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


def _make_mock_pipeline(sample_land, sample_zoning, tmp_path):
    """Helper to create a fully mocked orchestrator pipeline."""
    from unittest.mock import MagicMock

    from promptbim.agents.checker import CheckResult
    from promptbim.agents.planner import _fallback_box
    from promptbim.land.setback import compute_setback
    from promptbim.schemas.requirement import BuildingRequirement

    req = BuildingRequirement(
        raw_prompt="office",
        building_type="commercial",
        num_stories=2,
        enhanced_description="2-story office",
    )

    buildable_area = compute_setback(sample_land, sample_zoning)
    plan = _fallback_box(sample_land, sample_zoning, buildable_area, req)

    mock_enhancer = MagicMock()
    mock_enhancer.enhance.return_value = req

    mock_planner = MagicMock()
    mock_planner.plan.return_value = plan

    mock_checker = MagicMock()
    mock_checker.check.return_value = CheckResult()

    orch = Orchestrator(
        output_dir=tmp_path,
        enhancer=mock_enhancer,
        planner=mock_planner,
        checker=mock_checker,
    )
    return orch, req, plan


class TestOrchestratorDI:
    """Task 9: Verify dependency injection works correctly."""

    def test_custom_enhancer_injected(self, sample_land, sample_zoning, tmp_path):
        from unittest.mock import MagicMock

        custom_enhancer = MagicMock()
        custom_enhancer.enhance.return_value = MagicMock(
            building_type="custom",
            num_stories=1,
            constraints=[],
        )
        orch = Orchestrator(output_dir=tmp_path, enhancer=custom_enhancer)
        assert orch._enhancer is custom_enhancer

    def test_custom_checker_injected(self, tmp_path):
        from unittest.mock import MagicMock

        custom_checker = MagicMock()
        orch = Orchestrator(output_dir=tmp_path, checker=custom_checker)
        assert orch._checker is custom_checker

    def test_custom_modifier_injected(self, tmp_path):
        from unittest.mock import MagicMock

        custom_modifier = MagicMock()
        orch = Orchestrator(output_dir=tmp_path, modifier=custom_modifier)
        assert orch._modifier is custom_modifier

    def test_output_dir_stored(self, tmp_path):
        from pathlib import Path

        orch = Orchestrator(output_dir=tmp_path)
        assert orch._output_dir == Path(tmp_path)

    def test_output_dir_none(self):
        orch = Orchestrator()
        assert orch._output_dir is None


class TestOrchestratorModify:
    """Task 10: Test modify() execution path — no more AttributeError."""

    def test_modify_no_plan_returns_none(self, tmp_path):
        orch = Orchestrator(output_dir=tmp_path)
        result = orch.modify("add pool")
        assert result == (None, None)

    def test_modify_with_plan(self, sample_land, sample_zoning, tmp_path):
        from unittest.mock import MagicMock

        from promptbim.schemas.modification import ModificationRecord

        orch, req, plan = _make_mock_pipeline(sample_land, sample_zoning, tmp_path)
        orch._plan = plan

        mock_record = MagicMock(spec=ModificationRecord)
        mock_record.success = True
        orch._modifier = MagicMock()
        orch._modifier.modify.return_value = (plan, mock_record)

        new_plan, record = orch.modify("add pool", sample_zoning)
        assert record.success
        assert new_plan is not None

    def test_modify_failure_does_not_crash(self, sample_land, sample_zoning, tmp_path):
        from unittest.mock import MagicMock

        from promptbim.schemas.modification import ModificationRecord

        orch, req, plan = _make_mock_pipeline(sample_land, sample_zoning, tmp_path)
        orch._plan = plan

        mock_record = MagicMock(spec=ModificationRecord)
        mock_record.success = False
        mock_record.error = "test error"
        orch._modifier = MagicMock()
        orch._modifier.modify.return_value = (None, mock_record)

        new_plan, record = orch.modify("invalid op", sample_zoning)
        assert not record.success


class TestOrchestratorConstraintDedup:
    """Task 11: Test constraint deduplication across iterations."""

    def test_duplicate_constraints_not_added(self, sample_land, sample_zoning, tmp_path):
        from unittest.mock import MagicMock, call

        from promptbim.agents.checker import CheckResult
        from promptbim.schemas.requirement import BuildingRequirement

        req = BuildingRequirement(
            raw_prompt="house",
            building_type="residential",
            num_stories=2,
            enhanced_description="2-story house",
            constraints=[],
        )

        mock_enhancer = MagicMock()
        mock_enhancer.enhance.return_value = req

        mock_plan = MagicMock()
        mock_plan.name = "Test"
        mock_plan.stories = [MagicMock()]
        mock_plan.building_bcr = 0.4
        mock_plan.building_far = 0.8
        mock_plan.building_footprint = [(0, 0), (10, 0), (10, 10), (0, 10)]
        mock_plan.model_dump_json.return_value = "{}"

        mock_planner = MagicMock()
        mock_planner.plan.return_value = mock_plan

        # Checker fails first, passes second
        fail_result = MagicMock()
        fail_result.passed = False
        fail_result.violations = [MagicMock(severity="error", rule="BCR", message="too high")]
        fail_result.suggestions = ["reduce footprint"]
        pass_result = CheckResult()

        mock_checker = MagicMock()
        mock_checker.check.side_effect = [fail_result, pass_result]

        orch = Orchestrator(
            output_dir=tmp_path,
            max_iterations=2,
            enhancer=mock_enhancer,
            planner=mock_planner,
            checker=mock_checker,
        )
        orch.generate("house", sample_land, sample_zoning, use_cache=False)

        # The constraint should appear only once
        fix_constraints = [c for c in req.constraints if c.startswith("Fix:")]
        assert len(fix_constraints) == 1

    def test_different_constraints_both_added(self, sample_land, sample_zoning, tmp_path):
        from unittest.mock import MagicMock

        from promptbim.agents.checker import CheckResult
        from promptbim.schemas.requirement import BuildingRequirement

        req = BuildingRequirement(
            raw_prompt="house",
            building_type="residential",
            num_stories=2,
            enhanced_description="2-story house",
            constraints=[],
        )

        mock_enhancer = MagicMock()
        mock_enhancer.enhance.return_value = req

        mock_plan = MagicMock()
        mock_plan.name = "Test"
        mock_plan.stories = [MagicMock()]
        mock_plan.building_bcr = 0.4
        mock_plan.building_far = 0.8
        mock_plan.building_footprint = [(0, 0), (10, 0), (10, 10), (0, 10)]
        mock_plan.model_dump_json.return_value = "{}"

        mock_planner = MagicMock()
        mock_planner.plan.return_value = mock_plan

        fail1 = MagicMock()
        fail1.passed = False
        fail1.violations = [MagicMock()]
        fail1.suggestions = ["reduce footprint"]

        fail2 = MagicMock()
        fail2.passed = False
        fail2.violations = [MagicMock()]
        fail2.suggestions = ["lower height"]

        pass_result = CheckResult()

        mock_checker = MagicMock()
        mock_checker.check.side_effect = [fail1, fail2, pass_result]

        orch = Orchestrator(
            output_dir=tmp_path,
            max_iterations=3,
            enhancer=mock_enhancer,
            planner=mock_planner,
            checker=mock_checker,
        )
        orch.generate("house", sample_land, sample_zoning, use_cache=False)

        fix_constraints = [c for c in req.constraints if c.startswith("Fix:")]
        assert len(fix_constraints) == 2


class TestOrchestrator:
    def test_generate_with_fallbacks(
        self, sample_land, sample_zoning, tmp_path
    ):
        """Test pipeline runs end-to-end using fallback (no API)."""
        orch, req, plan = _make_mock_pipeline(sample_land, sample_zoning, tmp_path)
        result = orch.generate("office building", sample_land, sample_zoning)

        assert result.success
        assert result.building_name

    def test_properties_are_readonly(self, sample_land, sample_zoning, tmp_path):
        """Task 3: Verify properties are read-only after encapsulation."""
        orch, _, _ = _make_mock_pipeline(sample_land, sample_zoning, tmp_path)
        with pytest.raises(AttributeError):
            orch.requirement = "should fail"
        with pytest.raises(AttributeError):
            orch.plan = "should fail"
        with pytest.raises(AttributeError):
            orch.build_result = "should fail"
        with pytest.raises(AttributeError):
            orch.check_result = "should fail"
