"""Tests for viz/floorplan.py — per-floor SVG generation."""

import tempfile

from promptbim.schemas.plan import (
    BuildingPlan,
    OpeningDef,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)
from promptbim.viz.floorplan import (
    _bounds,
    _polygon_centroid,
    _story_svg,
    _to_svg_coords,
    generate_floorplan_svg_strings,
    generate_floorplans,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _sample_plan() -> BuildingPlan:
    footprint = [(0, 0), (10, 0), (10, 8), (0, 8)]
    return BuildingPlan(
        name="TestBuilding",
        building_footprint=footprint,
        building_bcr=0.50,
        building_far=1.0,
        stories=[
            StoryPlan(
                name="1F",
                elevation_m=0.0,
                height_m=3.0,
                slab_boundary=footprint,
                walls=[
                    WallDef(start=(0, 0), end=(10, 0), wall_type="exterior"),
                    WallDef(start=(10, 0), end=(10, 8), wall_type="exterior"),
                    WallDef(start=(10, 8), end=(0, 8), wall_type="exterior"),
                    WallDef(start=(0, 8), end=(0, 0), wall_type="exterior"),
                    WallDef(start=(5, 0), end=(5, 8), wall_type="interior"),
                ],
                spaces=[
                    SpaceDef(
                        name="Living",
                        boundary=[(0, 0), (5, 0), (5, 8), (0, 8)],
                        space_type="living",
                        area_sqm=40.0,
                    ),
                    SpaceDef(
                        name="Kitchen",
                        boundary=[(5, 0), (10, 0), (10, 8), (5, 8)],
                        space_type="living",
                        area_sqm=40.0,
                    ),
                ],
                openings=[
                    OpeningDef(
                        wall_index=0,
                        offset_m=2.0,
                        width_m=1.0,
                        height_m=2.1,
                        sill_height_m=0.0,
                        opening_type="door",
                    ),
                    OpeningDef(
                        wall_index=1,
                        offset_m=3.0,
                        width_m=1.5,
                        height_m=1.2,
                        sill_height_m=0.9,
                        opening_type="window",
                    ),
                ],
            ),
            StoryPlan(
                name="2F",
                elevation_m=3.0,
                height_m=3.0,
                slab_boundary=footprint,
                walls=[
                    WallDef(start=(0, 0), end=(10, 0), wall_type="exterior"),
                    WallDef(start=(10, 0), end=(10, 8), wall_type="exterior"),
                    WallDef(start=(10, 8), end=(0, 8), wall_type="exterior"),
                    WallDef(start=(0, 8), end=(0, 0), wall_type="exterior"),
                ],
                spaces=[
                    SpaceDef(
                        name="Bedroom",
                        boundary=[(0, 0), (10, 0), (10, 8), (0, 8)],
                        space_type="bedroom",
                        area_sqm=80.0,
                    ),
                ],
                openings=[],
            ),
        ],
        roof=RoofPlan(roof_type="flat"),
    )


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------


class TestBounds:
    def test_simple_rect(self):
        pts = [(0, 0), (10, 0), (10, 5), (0, 5)]
        assert _bounds(pts) == (0, 0, 10, 5)

    def test_negative_coords(self):
        pts = [(-5, -3), (5, -3), (5, 3), (-5, 3)]
        assert _bounds(pts) == (-5, -3, 5, 3)


class TestPolygonCentroid:
    def test_square(self):
        pts = [(0, 0), (4, 0), (4, 4), (0, 4)]
        cx, cy = _polygon_centroid(pts)
        assert abs(cx - 2.0) < 0.01
        assert abs(cy - 2.0) < 0.01

    def test_empty(self):
        assert _polygon_centroid([]) == (0.0, 0.0)


class TestToSvgCoords:
    def test_origin(self):
        sx, sy = _to_svg_coords(0.0, 0.0, 0.0, 0.0)
        assert sx == 40.0  # MARGIN
        assert sy == 40.0  # MARGIN


# ---------------------------------------------------------------------------
# SVG generation
# ---------------------------------------------------------------------------


class TestStorySvg:
    def test_nonempty_story_produces_svg(self):
        plan = _sample_plan()
        svg = _story_svg(plan.stories[0], plan.building_footprint)
        assert "<?xml" in svg
        assert "<svg" in svg
        assert "1F" in svg

    def test_empty_story_produces_placeholder(self):
        story = StoryPlan(name="B1", elevation_m=-3.0, height_m=3.0)
        svg = _story_svg(story, [])
        assert "no geometry" in svg


class TestGenerateFloorplans:
    def test_writes_svg_files(self):
        plan = _sample_plan()
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = generate_floorplans(plan, tmpdir)
            assert len(paths) == 2
            for p in paths:
                assert p.exists()
                assert p.suffix == ".svg"
                content = p.read_text()
                assert "<svg" in content

    def test_filenames_match_stories(self):
        plan = _sample_plan()
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = generate_floorplans(plan, tmpdir)
            names = [p.name for p in paths]
            assert "floorplan_1F.svg" in names
            assert "floorplan_2F.svg" in names


class TestGenerateFloorplanSvgStrings:
    def test_returns_dict_keyed_by_story(self):
        plan = _sample_plan()
        result = generate_floorplan_svg_strings(plan)
        assert "1F" in result
        assert "2F" in result
        assert "<svg" in result["1F"]

    def test_empty_plan(self):
        plan = BuildingPlan(name="Empty")
        result = generate_floorplan_svg_strings(plan)
        assert result == {}


class TestFloorplanWithOpenings:
    def test_openings_rendered(self):
        plan = _sample_plan()
        svg = _story_svg(plan.stories[0], plan.building_footprint)
        # Door and window should add coloured rectangles
        assert "rect" in svg

    def test_invalid_wall_index_skipped(self):
        plan = _sample_plan()
        story = plan.stories[0]
        story.openings.append(
            OpeningDef(
                wall_index=99,
                offset_m=0.0,
                width_m=1.0,
                height_m=2.0,
                opening_type="door",
            )
        )
        # Should not raise
        svg = _story_svg(story, plan.building_footprint)
        assert "<svg" in svg
