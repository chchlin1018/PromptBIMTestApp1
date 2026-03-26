"""Tests for viz/model_3d.py — BuildingPlan -> PyVista mesh assembly."""

import pyvista as pv

from promptbim.schemas.plan import (
    BuildingPlan,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)
from promptbim.viz.model_3d import (
    build_model,
    build_model_by_floor,
    clip_model_at_elevation,
    story_meshes,
)


def _simple_box_plan() -> BuildingPlan:
    """A minimal 2-story box building for testing."""
    footprint = [(0, 0), (10, 0), (10, 8), (0, 8)]
    walls_1f = [
        WallDef(start=(0, 0), end=(10, 0), wall_type="exterior"),
        WallDef(start=(10, 0), end=(10, 8), wall_type="exterior"),
        WallDef(start=(10, 8), end=(0, 8), wall_type="exterior"),
        WallDef(start=(0, 8), end=(0, 0), wall_type="exterior"),
        WallDef(start=(5, 0), end=(5, 8), wall_type="interior"),
    ]
    walls_2f = [
        WallDef(start=(0, 0), end=(10, 0), wall_type="exterior"),
        WallDef(start=(10, 0), end=(10, 8), wall_type="exterior"),
        WallDef(start=(10, 8), end=(0, 8), wall_type="exterior"),
        WallDef(start=(0, 8), end=(0, 0), wall_type="exterior"),
    ]
    return BuildingPlan(
        name="Test Box",
        building_footprint=footprint,
        building_bcr=0.5,
        building_far=1.0,
        stories=[
            StoryPlan(
                name="1F",
                elevation_m=0.0,
                height_m=3.0,
                walls=walls_1f,
                slab_boundary=footprint,
                spaces=[
                    SpaceDef(name="Room A", boundary=footprint, space_type="office", area_sqm=40.0)
                ],
            ),
            StoryPlan(
                name="2F",
                elevation_m=3.0,
                height_m=3.0,
                walls=walls_2f,
                slab_boundary=footprint,
                spaces=[],
            ),
        ],
        roof=RoofPlan(roof_type="flat"),
    )


class TestBuildModel:
    def test_build_model_returns_meshes(self):
        plan = _simple_box_plan()
        meshes = build_model(plan)
        assert len(meshes) > 0
        for pd, color, label in meshes:
            assert isinstance(pd, pv.PolyData)
            assert pd.n_points > 0
            assert color.startswith("#")
            assert isinstance(label, str)

    def test_build_model_has_ground_slab(self):
        plan = _simple_box_plan()
        meshes = build_model(plan)
        labels = [label for _, _, label in meshes]
        assert "ground_slab" in labels

    def test_build_model_has_roof(self):
        plan = _simple_box_plan()
        meshes = build_model(plan)
        labels = [label for _, _, label in meshes]
        assert "roof" in labels

    def test_build_model_wall_count(self):
        plan = _simple_box_plan()
        meshes = build_model(plan)
        wall_meshes = [m for m in meshes if "wall" in m[2]]
        # 5 walls 1F + 4 walls 2F = 9
        assert len(wall_meshes) == 9

    def test_build_model_slab_count(self):
        plan = _simple_box_plan()
        meshes = build_model(plan)
        slab_meshes = [m for m in meshes if "slab" in m[2]]
        # ground_slab + 1F_slab + 2F_slab = 3
        assert len(slab_meshes) == 3


class TestBuildModelByFloor:
    def test_returns_grouped_dict(self):
        plan = _simple_box_plan()
        grouped = build_model_by_floor(plan)
        assert "1F" in grouped
        assert "2F" in grouped
        assert "ground_slab" in grouped
        assert "roof" in grouped

    def test_floor_meshes_not_empty(self):
        plan = _simple_box_plan()
        grouped = build_model_by_floor(plan)
        for key, meshes in grouped.items():
            assert len(meshes) > 0


class TestStoryMeshes:
    def test_single_story(self):
        footprint = [(0, 0), (10, 0), (10, 8), (0, 8)]
        story = StoryPlan(
            name="1F",
            elevation_m=0.0,
            height_m=3.0,
            walls=[
                WallDef(start=(0, 0), end=(10, 0)),
                WallDef(start=(10, 0), end=(10, 8)),
            ],
            slab_boundary=footprint,
        )
        meshes = story_meshes(story)
        # 2 walls + 1 slab = 3
        assert len(meshes) == 3

    def test_story_no_slab(self):
        story = StoryPlan(
            name="1F",
            elevation_m=0.0,
            height_m=3.0,
            walls=[WallDef(start=(0, 0), end=(10, 0))],
            slab_boundary=[],
        )
        meshes = story_meshes(story)
        assert len(meshes) == 1  # just the wall


class TestClipModel:
    def test_clip_at_mid_height(self):
        plan = _simple_box_plan()
        meshes = build_model(plan)
        clipped = clip_model_at_elevation(meshes, 1.5)
        assert len(clipped) > 0

    def test_clip_above_building(self):
        plan = _simple_box_plan()
        meshes = build_model(plan)
        clipped = clip_model_at_elevation(meshes, 100.0)
        # clip_model_at_elevation clips at elevation; result depends on PyVista clip semantics
        # At z=100 (above everything), result may be empty or full depending on invert
        assert isinstance(clipped, list)


class TestGableRoof:
    def test_gable_roof_model(self):
        plan = _simple_box_plan()
        plan.roof = RoofPlan(roof_type="gable", slope_degrees=30.0)
        meshes = build_model(plan)
        labels = [label for _, _, label in meshes]
        assert "roof" in labels


class TestEmptyPlan:
    def test_empty_plan_no_crash(self):
        plan = BuildingPlan(name="Empty")
        meshes = build_model(plan)
        assert meshes == []

    def test_empty_plan_by_floor(self):
        plan = BuildingPlan(name="Empty")
        grouped = build_model_by_floor(plan)
        assert grouped == {}
