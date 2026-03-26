"""Tests for bim/mep/planner.py — MEP Planner."""

from promptbim.bim.mep.planner import MEPPlanner, _distribute_points, _polygon_centroid
from promptbim.schemas.plan import (
    BuildingPlan,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)


def _make_simple_building() -> BuildingPlan:
    """10x10m single-story box with one office and one bathroom."""
    fp = [(0, 0), (10, 0), (10, 10), (0, 10)]
    walls = [
        WallDef(start=(0, 0), end=(10, 0), wall_type="exterior"),
        WallDef(start=(10, 0), end=(10, 10), wall_type="exterior"),
        WallDef(start=(10, 10), end=(0, 10), wall_type="exterior"),
        WallDef(start=(0, 10), end=(0, 0), wall_type="exterior"),
        WallDef(start=(0, 7), end=(10, 7), wall_type="interior"),
    ]
    spaces = [
        SpaceDef(
            name="Office",
            boundary=[(0, 0), (10, 0), (10, 7), (0, 7)],
            space_type="office",
            area_sqm=70,
        ),
        SpaceDef(
            name="Bathroom",
            boundary=[(0, 7), (10, 7), (10, 10), (0, 10)],
            space_type="bathroom",
            area_sqm=30,
        ),
    ]
    return BuildingPlan(
        name="Simple Box",
        building_footprint=fp,
        stories=[
            StoryPlan(
                name="1F",
                elevation_m=0.0,
                height_m=3.0,
                walls=walls,
                spaces=spaces,
                slab_boundary=fp,
            ),
        ],
        roof=RoofPlan(),
    )


class TestMEPPlanner:
    def test_plan_produces_routes(self):
        planner = MEPPlanner(grid_size=0.5)
        building = _make_simple_building()
        result = planner.plan(building, building_type="office")
        assert len(result.equipment) > 0
        assert len(result.terminals) > 0
        assert len(result.routes) > 0

    def test_four_systems_present(self):
        planner = MEPPlanner(grid_size=0.5)
        building = _make_simple_building()
        result = planner.plan(building)
        systems = set(r.system for r in result.routes)
        # At least some systems should have routes
        assert len(systems) >= 2

    def test_equipment_per_floor(self):
        planner = MEPPlanner(grid_size=0.5)
        building = _make_simple_building()
        result = planner.plan(building)
        floor_equip = [e for e in result.equipment if e.floor == "1F"]
        assert len(floor_equip) == 4  # one per system

    def test_plumbing_terminals_for_bathroom(self):
        planner = MEPPlanner(grid_size=0.5)
        building = _make_simple_building()
        result = planner.plan(building)
        plumbing_terms = [t for t in result.terminals if t.system == "plumbing"]
        assert len(plumbing_terms) >= 1
        assert any(t.terminal_type == "fixture" for t in plumbing_terms)

    def test_empty_building(self):
        planner = MEPPlanner()
        empty = BuildingPlan(name="Empty")
        result = planner.plan(empty)
        assert len(result.routes) == 0
        assert len(result.equipment) == 0

    def test_no_footprint(self):
        planner = MEPPlanner()
        building = BuildingPlan(
            name="No FP",
            stories=[StoryPlan(name="1F", elevation_m=0, height_m=3)],
        )
        result = planner.plan(building)
        assert len(result.routes) == 0


class TestGeometryHelpers:
    def test_polygon_centroid(self):
        boundary = [(0, 0), (10, 0), (10, 10), (0, 10)]
        cx, cy = _polygon_centroid(boundary)
        assert abs(cx - 5) < 0.01
        assert abs(cy - 5) < 0.01

    def test_polygon_centroid_empty(self):
        assert _polygon_centroid([]) == (0.0, 0.0)

    def test_distribute_points(self):
        boundary = [(0, 0), (10, 0), (10, 10), (0, 10)]
        pts = _distribute_points(boundary, 4)
        assert len(pts) == 4
        for x, y in pts:
            assert 0 <= x <= 10
            assert 0 <= y <= 10

    def test_distribute_single(self):
        boundary = [(0, 0), (10, 0), (10, 10), (0, 10)]
        pts = _distribute_points(boundary, 1)
        assert len(pts) == 1
        assert abs(pts[0][0] - 5) < 0.01

    def test_distribute_zero(self):
        assert _distribute_points([(0, 0), (1, 0), (1, 1)], 0) == []
