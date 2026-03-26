"""Tests for schema version compatibility."""

from __future__ import annotations

from promptbim.schemas.version import CURRENT_SCHEMA_VERSION, check_schema_compatibility


class TestSchemaVersion:
    def test_current_version_compatible(self):
        ok, msg = check_schema_compatibility(CURRENT_SCHEMA_VERSION)
        assert ok

    def test_old_version_incompatible(self):
        ok, msg = check_schema_compatibility("1.0.0")
        assert not ok
        assert "too old" in msg

    def test_v2_compatible(self):
        ok, msg = check_schema_compatibility("2.0.0")
        assert ok

    def test_invalid_version_format(self):
        ok, msg = check_schema_compatibility("not.a.version")
        assert not ok
        assert "Invalid" in msg

    def test_plan_has_schema_version(self):
        from promptbim.schemas.plan import BuildingPlan

        plan = BuildingPlan(name="test")
        assert plan.schema_version == "2.4.0"

    def test_result_has_schema_version(self):
        from promptbim.schemas.result import GenerationResult

        result = GenerationResult()
        assert result.schema_version == "2.4.0"
