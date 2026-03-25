"""Tests for bim/ifc_generator.py — IFC file generation."""

import tempfile
from pathlib import Path

import ifcopenshell
import pytest

from promptbim.bim.ifc_generator import IFCGenerator
from promptbim.schemas.plan import (
    BuildingPlan,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)


@pytest.fixture
def simple_plan() -> BuildingPlan:
    footprint = [(0, 0), (10, 0), (10, 8), (0, 8)]
    walls = [
        WallDef(start=(0, 0), end=(10, 0)),
        WallDef(start=(10, 0), end=(10, 8)),
        WallDef(start=(10, 8), end=(0, 8)),
        WallDef(start=(0, 8), end=(0, 0)),
    ]
    story = StoryPlan(
        name="1F",
        elevation_m=0.0,
        height_m=3.0,
        walls=walls,
        slab_boundary=footprint,
    )
    return BuildingPlan(
        name="Test Box",
        building_footprint=footprint,
        stories=[story],
        roof=RoofPlan(roof_type="flat"),
    )


def test_generate_ifc_file(simple_plan, tmp_path):
    gen = IFCGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.ifc")
    assert output.exists()
    assert output.suffix == ".ifc"


def test_ifc_can_be_reopened(simple_plan, tmp_path):
    gen = IFCGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.ifc")
    model = ifcopenshell.open(str(output))
    assert model is not None


def test_ifc_has_project(simple_plan, tmp_path):
    gen = IFCGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.ifc")
    model = ifcopenshell.open(str(output))
    projects = model.by_type("IfcProject")
    assert len(projects) == 1
    assert projects[0].Name == "Test Box"


def test_ifc_has_walls(simple_plan, tmp_path):
    gen = IFCGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.ifc")
    model = ifcopenshell.open(str(output))
    walls = model.by_type("IfcWall")
    assert len(walls) == 4


def test_ifc_has_slab(simple_plan, tmp_path):
    gen = IFCGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.ifc")
    model = ifcopenshell.open(str(output))
    slabs = model.by_type("IfcSlab")
    assert len(slabs) == 1


def test_ifc_has_storey(simple_plan, tmp_path):
    gen = IFCGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.ifc")
    model = ifcopenshell.open(str(output))
    storeys = model.by_type("IfcBuildingStorey")
    assert len(storeys) == 1
    assert storeys[0].Name == "1F"


def test_ifc_has_roof(simple_plan, tmp_path):
    gen = IFCGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.ifc")
    model = ifcopenshell.open(str(output))
    roofs = model.by_type("IfcRoof")
    assert len(roofs) == 1


def test_ifc_empty_plan(tmp_path):
    """Generate with empty plan (no stories) should still produce valid IFC."""
    plan = BuildingPlan(name="Empty")
    gen = IFCGenerator()
    output = gen.generate(plan, tmp_path / "empty.ifc")
    model = ifcopenshell.open(str(output))
    assert len(model.by_type("IfcProject")) == 1
    assert len(model.by_type("IfcWall")) == 0


def test_ifc_zero_length_wall(tmp_path):
    """Zero-length walls should be handled gracefully."""
    walls = [
        WallDef(start=(0, 0), end=(0, 0)),  # zero-length
        WallDef(start=(0, 0), end=(5, 0)),  # valid
    ]
    story = StoryPlan(name="1F", elevation_m=0.0, height_m=3.0, walls=walls)
    plan = BuildingPlan(name="ZeroWall", stories=[story])
    gen = IFCGenerator()
    output = gen.generate(plan, tmp_path / "zero.ifc")
    model = ifcopenshell.open(str(output))
    # Both walls created in IFC (zero-length still gets entity, just empty geo)
    assert len(model.by_type("IfcWall")) == 2


def test_ifc_concave_slab(tmp_path):
    """L-shaped concave boundary should produce valid IFC slab."""
    footprint = [(0, 0), (16, 0), (16, 6), (10, 6), (10, 10), (0, 10)]
    story = StoryPlan(
        name="1F", elevation_m=0.0, height_m=3.0,
        slab_boundary=footprint,
    )
    plan = BuildingPlan(name="L-Shape", building_footprint=footprint, stories=[story])
    gen = IFCGenerator()
    output = gen.generate(plan, tmp_path / "l_shape.ifc")
    model = ifcopenshell.open(str(output))
    assert len(model.by_type("IfcSlab")) == 1


def test_ifc_multi_storey(tmp_path):
    footprint = [(0, 0), (8, 0), (8, 6), (0, 6)]
    walls = [
        WallDef(start=(0, 0), end=(8, 0)),
        WallDef(start=(8, 0), end=(8, 6)),
        WallDef(start=(8, 6), end=(0, 6)),
        WallDef(start=(0, 6), end=(0, 0)),
    ]
    stories = [
        StoryPlan(name="1F", elevation_m=0.0, height_m=3.0, walls=walls, slab_boundary=footprint),
        StoryPlan(name="2F", elevation_m=3.0, height_m=3.0, walls=walls, slab_boundary=footprint),
    ]
    plan = BuildingPlan(
        name="2-Storey",
        building_footprint=footprint,
        stories=stories,
        roof=RoofPlan(roof_type="flat"),
    )
    gen = IFCGenerator()
    output = gen.generate(plan, tmp_path / "multi.ifc")
    model = ifcopenshell.open(str(output))
    assert len(model.by_type("IfcBuildingStorey")) == 2
    assert len(model.by_type("IfcWall")) == 8
