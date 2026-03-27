"""Tests for io_usd — ILOS USD import/export.

Note: These tests use mock objects since pxr (USD) may not be installed.
They verify the logic structure, data flow, and JSON serialization.
"""
from __future__ import annotations

import numpy as np
import pytest

from src.promptbim.bim.io_usd.importer import (
    ConnectionPort,
    ILOSMetadata,
    USDElement,
    USDImporter,
)
from src.promptbim.bim.io_usd.exporter import USDExporter


# ── ILOSMetadata ──

class TestILOSMetadata:
    def test_defaults(self):
        meta = ILOSMetadata()
        assert meta.category == ""
        assert meta.part_number == ""
        assert meta.manufacturer == ""
        assert meta.description == ""

    def test_custom_values(self):
        meta = ILOSMetadata(
            category="HVAC",
            part_number="AHU-001",
            manufacturer="Daikin",
            description="Air Handling Unit",
        )
        assert meta.category == "HVAC"
        assert meta.part_number == "AHU-001"


# ── ConnectionPort ──

class TestConnectionPort:
    def test_defaults(self):
        port = ConnectionPort()
        assert port.name == ""
        assert port.port_type == ""
        assert port.port_size_mm == 0.0
        assert port.position == (0.0, 0.0, 0.0)

    def test_custom_values(self):
        port = ConnectionPort(
            name="inlet_1",
            port_type="flanged",
            port_medium="chilled_water",
            port_size_mm=150.0,
            port_direction="in",
            position=(1.0, 2.0, 3.0),
        )
        assert port.name == "inlet_1"
        assert port.port_size_mm == 150.0
        assert port.position == (1.0, 2.0, 3.0)


# ── USDElement ──

class TestUSDElement:
    def test_defaults(self):
        elem = USDElement()
        assert elem.path == ""
        assert elem.name == ""
        assert elem.vertices.shape == (0, 3)
        assert elem.faces.shape == (0, 3)
        assert elem.transform.shape == (4, 4)
        assert np.allclose(elem.transform, np.eye(4))
        assert isinstance(elem.ilos, ILOSMetadata)
        assert elem.connections == []
        assert elem.material == "default"

    def test_to_json(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]], dtype=np.float64)
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        elem = USDElement(
            path="/BIMModel/wall_1",
            name="wall_1",
            vertices=verts,
            faces=faces,
            ilos=ILOSMetadata(category="wall", manufacturer="TSMC"),
            connections=[
                ConnectionPort(name="port_1", port_type="flanged", port_medium="air"),
            ],
            material="concrete",
        )
        j = elem.to_json()
        assert j["id"] == "wall_1"
        assert j["path"] == "/BIMModel/wall_1"
        assert j["type"] == "wall"
        assert j["material"] == "concrete"
        assert len(j["vertices"]) == 3
        assert len(j["indices"]) == 1
        assert j["ilos"]["category"] == "wall"
        assert j["ilos"]["manufacturer"] == "TSMC"
        assert len(j["connections"]) == 1
        assert j["connections"][0]["name"] == "port_1"
        assert j["connections"][0]["port_medium"] == "air"

    def test_to_json_empty(self):
        elem = USDElement()
        j = elem.to_json()
        assert j["id"] == ""
        assert j["type"] == "mesh"  # default when category is empty
        assert j["vertices"] == []
        assert j["indices"] == []
        assert j["connections"] == []


# ── USDImporter (without pxr) ──

class TestUSDImporter:
    def test_construction(self):
        imp = USDImporter()
        assert imp.elements == []

    def test_to_json_empty(self):
        imp = USDImporter()
        result = imp.to_json()
        assert result["elements"] == []
        assert result["element_count"] == 0

    def test_to_json_with_elements(self):
        imp = USDImporter()
        imp._elements = [
            USDElement(
                name="beam_1",
                path="/BIMModel/beam_1",
                vertices=np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]], dtype=np.float64),
                faces=np.array([[0, 1, 2]], dtype=np.int32),
                ilos=ILOSMetadata(category="beam"),
                material="steel",
            ),
        ]
        result = imp.to_json()
        assert result["element_count"] == 1
        assert result["elements"][0]["id"] == "beam_1"
        assert result["elements"][0]["material"] == "steel"

    def test_load_file_not_found(self):
        imp = USDImporter()
        with pytest.raises(FileNotFoundError):
            imp.load("/nonexistent/path/model.usda")


# ── USDExporter (without pxr) ──

class TestUSDExporter:
    def test_construction(self):
        exp = USDExporter()
        assert exp is not None
