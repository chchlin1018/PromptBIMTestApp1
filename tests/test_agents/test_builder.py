"""Tests for agents/builder.py — BuilderAgent (no LLM)."""

import pytest
from pathlib import Path

from promptbim.agents.builder import BuilderAgent, BuildResult, _safe_filename
from promptbim.schemas.plan import (
    BuildingPlan,
    RoofPlan,
    StoryPlan,
    WallDef,
    SpaceDef,
)


@pytest.fixture
def simple_plan():
    footprint = [(0, 0), (10, 0), (10, 8), (0, 8)]
    return BuildingPlan(
        name="Test Building",
        building_footprint=footprint,
        building_bcr=0.5,
        building_far=1.0,
        stories=[
            StoryPlan(
                name="1F",
                elevation_m=0.0,
                height_m=3.0,
                walls=[
                    WallDef(start=(0, 0), end=(10, 0), wall_type="exterior"),
                    WallDef(start=(10, 0), end=(10, 8), wall_type="exterior"),
                    WallDef(start=(10, 8), end=(0, 8), wall_type="exterior"),
                    WallDef(start=(0, 8), end=(0, 0), wall_type="exterior"),
                ],
                spaces=[
                    SpaceDef(name="Room", boundary=footprint, space_type="office", area_sqm=80.0),
                ],
                slab_boundary=footprint,
            ),
            StoryPlan(
                name="2F",
                elevation_m=3.0,
                height_m=3.0,
                walls=[
                    WallDef(start=(0, 0), end=(10, 0), wall_type="exterior"),
                    WallDef(start=(10, 0), end=(10, 8), wall_type="exterior"),
                    WallDef(start=(10, 8), end=(0, 8), wall_type="exterior"),
                    WallDef(start=(0, 8), end=(0, 0), wall_type="exterior"),
                ],
                spaces=[
                    SpaceDef(name="Room", boundary=footprint, space_type="office", area_sqm=80.0),
                ],
                slab_boundary=footprint,
            ),
        ],
        roof=RoofPlan(roof_type="flat"),
    )


class TestBuilderAgent:
    def test_build_generates_files(self, simple_plan, tmp_path):
        builder = BuilderAgent(output_dir=tmp_path)
        result = builder.build(simple_plan)

        assert isinstance(result, BuildResult)
        assert result.ok
        assert result.ifc_path is not None
        assert result.usd_path is not None
        assert result.ifc_path.exists()
        assert result.usd_path.exists()

    def test_ifc_file_can_be_read(self, simple_plan, tmp_path):
        import ifcopenshell

        builder = BuilderAgent(output_dir=tmp_path)
        result = builder.build(simple_plan)

        ifc_file = ifcopenshell.open(str(result.ifc_path))
        walls = ifc_file.by_type("IfcWall")
        assert len(walls) >= 4  # at least 4 walls per story

    def test_usd_file_can_be_opened(self, simple_plan, tmp_path):
        from pxr import Usd

        builder = BuilderAgent(output_dir=tmp_path)
        result = builder.build(simple_plan)

        stage = Usd.Stage.Open(str(result.usd_path))
        assert stage is not None


class TestSafeFilename:
    def test_normal_name(self):
        assert _safe_filename("My Building") == "My_Building"

    def test_special_chars(self):
        assert _safe_filename("test!@#$%") == "test"

    def test_empty(self):
        assert _safe_filename("") == "building"

    def test_long_name(self):
        result = _safe_filename("a" * 200)
        assert len(result) <= 80
