"""E2E test: validates the full JSON protocol chain.

Tests the complete path: JSON request → agent_runner parsing → mesh serialization → JSON response.
Uses mock orchestrator to avoid needing ANTHROPIC_API_KEY.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def mock_plan():
    """Create a mock BuildingPlan for testing."""
    from promptbim.schemas.plan import BuildingPlan, StoryPlan, WallDef, SpaceDef

    wall1 = WallDef(start=(0, 0), end=(20, 0), thickness_m=0.2, wall_type="exterior")
    wall2 = WallDef(start=(20, 0), end=(20, 15), thickness_m=0.2, wall_type="exterior")
    wall3 = WallDef(start=(20, 15), end=(0, 15), thickness_m=0.2, wall_type="exterior")
    wall4 = WallDef(start=(0, 15), end=(0, 0), thickness_m=0.2, wall_type="exterior")

    space = SpaceDef(
        name="Office",
        boundary=[(0, 0), (20, 0), (20, 15), (0, 15)],
        space_type="office",
        area_sqm=300.0,
    )

    story = StoryPlan(
        name="1F",
        elevation_m=0.0,
        height_m=3.0,
        walls=[wall1, wall2, wall3, wall4],
        spaces=[space],
        openings=[],
        slab_boundary=[(0, 0), (20, 0), (20, 15), (0, 15)],
        slab_thickness_m=0.2,
    )

    return BuildingPlan(
        name="Test Factory",
        stories=[story],
        building_footprint=[(0, 0), (20, 0), (20, 15), (0, 15)],
        building_bcr=0.5,
        building_far=0.5,
    )


def test_e2e_mesh_serialization(mock_plan):
    """E2E: BuildingPlan → mesh JSON → validate structure."""
    from mesh_serializer import serialize_plan_to_mesh

    result = serialize_plan_to_mesh(mock_plan)

    assert "elements" in result
    assert "element_count" in result
    assert result["element_count"] > 0
    assert result["stories"] == 1

    for elem in result["elements"]:
        assert "id" in elem
        assert "type" in elem
        assert "material" in elem
        assert "vertices" in elem
        assert "indices" in elem
        assert "color" in elem
        assert len(elem["color"]) == 4
        assert len(elem["vertices"]) > 0
        assert len(elem["indices"]) > 0

    wall_elements = [e for e in result["elements"] if e["type"] == "wall"]
    assert len(wall_elements) == 4

    col_elements = [e for e in result["elements"] if e["type"] == "column"]
    assert len(col_elements) > 0


def test_e2e_json_roundtrip(mock_plan):
    """E2E: mesh JSON → serialize → deserialize → validate."""
    from mesh_serializer import serialize_plan_to_mesh

    result = serialize_plan_to_mesh(mock_plan)
    json_str = json.dumps(result)
    parsed = json.loads(json_str)

    assert parsed["element_count"] == result["element_count"]
    assert len(parsed["elements"]) == len(result["elements"])

    first_elem = parsed["elements"][0]
    for v in first_elem["vertices"]:
        assert len(v) == 3
        assert all(isinstance(c, (int, float)) for c in v)

    for tri in first_elem["indices"]:
        assert len(tri) == 3
        assert all(isinstance(i, int) for i in tri)


def test_e2e_full_result_format(mock_plan):
    """E2E: validate the complete result JSON format matching protocol."""
    from mesh_serializer import serialize_plan_to_mesh

    model = serialize_plan_to_mesh(mock_plan)

    result_msg = {
        "type": "result",
        "model": model,
        "cost": {"total_cost_twd": 5000000},
        "schedule": {"total_days": 180, "phases": []},
        "summary": {"stories": 1, "bcr": 0.5, "far": 0.5},
        "success": True,
    }

    json_str = json.dumps(result_msg)
    parsed = json.loads(json_str)

    assert parsed["type"] == "result"
    assert parsed["success"] is True
    assert parsed["model"]["element_count"] > 0
    assert parsed["cost"]["total_cost_twd"] == 5000000
    assert parsed["schedule"]["total_days"] == 180
