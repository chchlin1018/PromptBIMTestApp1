"""Tests for agent_runner.py — JSON stdio bridge between C++ and Python."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_import_agent_runner():
    """Test that agent_runner can be imported without crash."""
    import agent_runner
    assert hasattr(agent_runner, "main")
    assert hasattr(agent_runner, "emit")
    assert hasattr(agent_runner, "build_land_parcel")
    assert hasattr(agent_runner, "handle_generate")


def test_import_mesh_serializer():
    """Test that mesh_serializer can be imported."""
    import mesh_serializer
    assert hasattr(mesh_serializer, "serialize_plan_to_mesh")
    assert hasattr(mesh_serializer, "_box_mesh")
    assert hasattr(mesh_serializer, "_mesh_to_json")


def test_build_land_parcel():
    """Test land parcel construction from JSON data."""
    from agent_runner import build_land_parcel

    lp = build_land_parcel({"width": 120, "depth": 80})
    assert lp.area_sqm == 9600.0
    assert len(lp.boundary) == 4

    lp2 = build_land_parcel({"width": 50, "depth": 50})
    assert lp2.area_sqm == 2500.0


def test_build_land_parcel_defaults():
    """Test land parcel with default values."""
    from agent_runner import build_land_parcel

    lp = build_land_parcel({})
    assert lp.area_sqm == 8000.0  # 100 * 80 default


def test_mesh_serializer_box_mesh():
    """Test box mesh generation."""
    from mesh_serializer import _box_mesh

    mesh = _box_mesh(0, 0, 0, 10, 3, 8)
    assert mesh.vertices.shape == (8, 3)
    assert mesh.faces.shape == (12, 3)
    # Check bounds
    assert mesh.vertices[:, 0].min() == 0
    assert mesh.vertices[:, 0].max() == 10
    assert mesh.vertices[:, 2].max() == 3  # height


def test_mesh_to_json():
    """Test mesh to JSON conversion."""
    from mesh_serializer import _box_mesh, _mesh_to_json

    mesh = _box_mesh(0, 0, 0, 5, 3, 4)
    data = _mesh_to_json(mesh)
    assert "vertices" in data
    assert "indices" in data
    assert len(data["vertices"]) == 8
    assert len(data["indices"]) == 12
    # Check vertex format: [x, y, z]
    assert len(data["vertices"][0]) == 3


def test_emit_writes_json_line(capsys):
    """Test emit writes proper JSON line to stdout."""
    from agent_runner import emit

    emit({"type": "status", "message": "test"})
    captured = capsys.readouterr()
    line = captured.out.strip()
    parsed = json.loads(line)
    assert parsed["type"] == "status"
    assert parsed["message"] == "test"


def test_error_handling_invalid_json(capsys):
    """Test error response for invalid JSON input."""
    from agent_runner import emit

    # Simulate what would happen with invalid JSON
    try:
        json.loads("not valid json")
    except json.JSONDecodeError as e:
        emit({"type": "error", "message": f"Invalid JSON: {e}"})

    captured = capsys.readouterr()
    line = captured.out.strip()
    parsed = json.loads(line)
    assert parsed["type"] == "error"
    assert "Invalid JSON" in parsed["message"]


def test_material_map():
    """Test material mappings are complete."""
    from mesh_serializer import MATERIAL_MAP, COLOR_MAP

    for elem_type in ["wall", "slab", "column", "window", "door", "roof"]:
        assert elem_type in MATERIAL_MAP
        mat = MATERIAL_MAP[elem_type]
        assert mat in COLOR_MAP
        color = COLOR_MAP[mat]
        assert len(color) == 4  # RGBA
