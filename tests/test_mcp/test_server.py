"""Tests for MCP Server tools and resources."""

import json
from unittest.mock import MagicMock, patch

import pytest

from promptbim.mcp.server import (
    _shoelace_area,
    _state,
    import_land,
    set_zoning,
)


@pytest.fixture(autouse=True)
def reset_state():
    """Reset server state before each test."""
    _state["land"] = None
    _state["zoning"] = None
    _state["plan"] = None
    _state["result"] = None
    _state["output_dir"] = None
    yield
    _state["land"] = None
    _state["zoning"] = None
    _state["plan"] = None
    _state["result"] = None
    _state["output_dir"] = None


class TestImportLand:
    def test_import_rectangular_land(self):
        result = json.loads(import_land(
            boundary=[[0, 0], [20, 0], [20, 15], [0, 15]],
            name="Test Plot",
        ))
        assert result["status"] == "ok"
        assert result["name"] == "Test Plot"
        assert result["area_sqm"] == 300.0
        assert result["vertices"] == 4
        assert _state["land"] is not None

    def test_import_with_area_override(self):
        result = json.loads(import_land(
            boundary=[[0, 0], [10, 0], [10, 10], [0, 10]],
            area_sqm=500.0,
        ))
        assert result["area_sqm"] == 500.0

    def test_import_triangle(self):
        result = json.loads(import_land(
            boundary=[[0, 0], [10, 0], [5, 8]],
        ))
        assert result["status"] == "ok"
        assert result["vertices"] == 3


class TestSetZoning:
    def test_default_zoning(self):
        result = json.loads(set_zoning())
        assert result["status"] == "ok"
        assert result["zoning"]["zone_type"] == "residential"
        assert _state["zoning"] is not None

    def test_custom_zoning(self):
        result = json.loads(set_zoning(
            zone_type="commercial",
            far_limit=4.0,
            bcr_limit=0.8,
            height_limit_m=50.0,
        ))
        zoning = result["zoning"]
        assert zoning["zone_type"] == "commercial"
        assert zoning["far_limit"] == 4.0
        assert zoning["bcr_limit"] == 0.8
        assert zoning["height_limit_m"] == 50.0


class TestGenerateBuilding:
    def test_no_land_error(self):
        from promptbim.mcp.server import generate_building
        result = json.loads(generate_building("3 story house"))
        assert "error" in result

    @patch("promptbim.mcp.server._get_orchestrator")
    def test_generate_with_mock(self, mock_orch_fn):
        from promptbim.mcp.server import generate_building
        from promptbim.schemas.result import GenerationResult

        # First import land
        import_land(boundary=[[0, 0], [20, 0], [20, 15], [0, 15]])

        mock_result = GenerationResult(
            success=True,
            building_name="Test House",
            summary={"stories": 3, "bcr": 0.55, "far": 1.65},
        )
        mock_plan = MagicMock()
        mock_plan.model_dump.return_value = {"name": "Test House", "stories": [], "building_bcr": 0.55, "building_far": 1.65}

        mock_orch = MagicMock()
        mock_orch.generate.return_value = mock_result
        mock_orch.plan = mock_plan
        mock_orch_fn.return_value = mock_orch

        result = json.loads(generate_building("3 story house"))
        assert result["status"] == "ok"
        assert result["building_name"] == "Test House"


class TestCheckCompliance:
    def test_no_plan_error(self):
        from promptbim.mcp.server import check_compliance
        result = json.loads(check_compliance())
        assert "error" in result


class TestEstimateCost:
    def test_no_plan_error(self):
        from promptbim.mcp.server import estimate_cost
        result = json.loads(estimate_cost())
        assert "error" in result


class TestResources:
    def test_no_building_resource(self):
        from promptbim.mcp.server import get_current_building
        result = json.loads(get_current_building())
        assert result["status"] == "no_building"

    def test_no_land_resource(self):
        from promptbim.mcp.server import get_current_land
        result = json.loads(get_current_land())
        assert result["status"] == "no_land"

    def test_land_resource_after_import(self):
        from promptbim.mcp.server import get_current_land
        import_land(boundary=[[0, 0], [10, 0], [10, 10], [0, 10]])
        result = json.loads(get_current_land())
        assert result["status"] == "ok"
        assert result["land"]["area_sqm"] == 100.0


class TestShoelaceArea:
    def test_unit_square(self):
        assert abs(_shoelace_area([(0, 0), (1, 0), (1, 1), (0, 1)]) - 1.0) < 0.001

    def test_rectangle(self):
        assert abs(_shoelace_area([(0, 0), (20, 0), (20, 15), (0, 15)]) - 300.0) < 0.001

    def test_too_few_points(self):
        assert _shoelace_area([(0, 0), (1, 0)]) == 0.0


class TestMCPServerRegistration:
    def test_mcp_instance_exists(self):
        from promptbim.mcp.server import mcp
        assert mcp is not None
        assert mcp.name == "PromptBIM"
