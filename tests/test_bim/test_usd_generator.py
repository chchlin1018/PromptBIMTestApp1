"""Tests for bim/usd_generator.py — USD file generation."""

import pytest
from pxr import Usd, UsdGeom

from promptbim.bim.usd_generator import USDGenerator
from promptbim.schemas.plan import (
    BuildingPlan,
    RoofPlan,
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


def test_generate_usda_file(simple_plan, tmp_path):
    gen = USDGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.usda")
    assert output.exists()
    assert output.suffix == ".usda"


def test_usd_can_be_reopened(simple_plan, tmp_path):
    gen = USDGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.usda")
    stage = Usd.Stage.Open(str(output))
    assert stage is not None


def test_usd_up_axis_is_z(simple_plan, tmp_path):
    gen = USDGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.usda")
    stage = Usd.Stage.Open(str(output))
    assert UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z


def test_usd_has_building_root(simple_plan, tmp_path):
    gen = USDGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.usda")
    stage = Usd.Stage.Open(str(output))
    building = stage.GetPrimAtPath("/Building")
    assert building.IsValid()


def test_usd_has_wall_meshes(simple_plan, tmp_path):
    gen = USDGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.usda")
    stage = Usd.Stage.Open(str(output))
    wall_prims = [
        p for p in stage.Traverse()
        if "Wall" in p.GetPath().pathString and p.GetTypeName() == "Mesh"
    ]
    assert len(wall_prims) == 4


def test_usd_has_slab(simple_plan, tmp_path):
    gen = USDGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.usda")
    stage = Usd.Stage.Open(str(output))
    slab_prims = [
        p for p in stage.Traverse()
        if "Slab" in p.GetPath().pathString
    ]
    assert len(slab_prims) >= 1


def test_usd_has_roof(simple_plan, tmp_path):
    gen = USDGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.usda")
    stage = Usd.Stage.Open(str(output))
    roof = stage.GetPrimAtPath("/Building/Roof")
    assert roof.IsValid()


def test_usd_has_materials(simple_plan, tmp_path):
    gen = USDGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.usda")
    stage = Usd.Stage.Open(str(output))
    mat_prims = [
        p for p in stage.Traverse()
        if "Materials" in p.GetPath().pathString
    ]
    assert len(mat_prims) >= 1


def test_usd_round_trip_prim_count(simple_plan, tmp_path):
    """USD round-trip: open file and verify expected prim count."""
    gen = USDGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.usda")
    stage = Usd.Stage.Open(str(output))
    prims = list(stage.Traverse())
    # Building root + 1F Xform + 4 walls + 1 slab + Roof + Materials + shaders
    assert len(prims) >= 8


def test_usd_mesh_has_normals(simple_plan, tmp_path):
    """USD mesh prims should have normals set."""
    gen = USDGenerator()
    output = gen.generate(simple_plan, tmp_path / "test.usda")
    stage = Usd.Stage.Open(str(output))
    wall_prims = [
        p for p in stage.Traverse()
        if "Wall" in p.GetPath().pathString and p.GetTypeName() == "Mesh"
    ]
    assert len(wall_prims) > 0
    mesh = UsdGeom.Mesh(wall_prims[0])
    normals = mesh.GetNormalsAttr().Get()
    assert normals is not None
    assert len(normals) > 0


def test_usd_empty_plan(tmp_path):
    """Generate with empty plan (no stories)."""
    plan = BuildingPlan(name="Empty")
    gen = USDGenerator()
    output = gen.generate(plan, tmp_path / "empty.usda")
    stage = Usd.Stage.Open(str(output))
    assert stage is not None


def test_usd_multi_storey(tmp_path):
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
    gen = USDGenerator()
    output = gen.generate(plan, tmp_path / "multi.usda")
    stage = Usd.Stage.Open(str(output))
    wall_prims = [
        p for p in stage.Traverse()
        if "Wall" in p.GetPath().pathString and p.GetTypeName() == "Mesh"
    ]
    assert len(wall_prims) == 8
