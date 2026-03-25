"""Tests for bim/monitoring/auto_placement.py — auto placement algorithm."""

import pytest

from promptbim.bim.monitoring.auto_placement import (
    AutoMonitorPlacer,
    MonitorPlan,
    MonitorPlacement,
)
from promptbim.schemas.plan import BuildingPlan, SpaceDef, StoryPlan


def _make_test_plan() -> BuildingPlan:
    """Create a simple 2-storey office building plan for testing."""
    return BuildingPlan(
        name="Test Office",
        building_footprint=[(0, 0), (20, 0), (20, 15), (0, 15)],
        stories=[
            StoryPlan(
                name="1F",
                elevation_m=0.0,
                height_m=3.5,
                slab_boundary=[(0, 0), (20, 0), (20, 15), (0, 15)],
                spaces=[
                    SpaceDef(
                        name="Lobby",
                        boundary=[(0, 0), (8, 0), (8, 10), (0, 10)],
                        space_type="lobby",
                        area_sqm=80,
                    ),
                    SpaceDef(
                        name="Office1",
                        boundary=[(8, 0), (20, 0), (20, 10), (8, 10)],
                        space_type="office",
                        area_sqm=120,
                    ),
                    SpaceDef(
                        name="Bathroom1",
                        boundary=[(0, 10), (8, 10), (8, 15), (0, 15)],
                        space_type="bathroom",
                        area_sqm=40,
                    ),
                    SpaceDef(
                        name="Corridor1",
                        boundary=[(8, 10), (20, 10), (20, 15), (8, 15)],
                        space_type="corridor",
                        area_sqm=60,
                    ),
                ],
            ),
            StoryPlan(
                name="2F",
                elevation_m=3.5,
                height_m=3.5,
                slab_boundary=[(0, 0), (20, 0), (20, 15), (0, 15)],
                spaces=[
                    SpaceDef(
                        name="Meeting",
                        boundary=[(0, 0), (10, 0), (10, 8), (0, 8)],
                        space_type="meeting",
                        area_sqm=80,
                    ),
                    SpaceDef(
                        name="Office2",
                        boundary=[(10, 0), (20, 0), (20, 8), (10, 8)],
                        space_type="office",
                        area_sqm=80,
                    ),
                    SpaceDef(
                        name="Corridor2",
                        boundary=[(0, 8), (20, 8), (20, 15), (0, 15)],
                        space_type="corridor",
                        area_sqm=140,
                    ),
                ],
            ),
        ],
    )


class TestAutoMonitorPlacer:
    def test_place_all_returns_monitor_plan(self):
        plan = _make_test_plan()
        placer = AutoMonitorPlacer()
        result = placer.place_all(plan)
        assert isinstance(result, MonitorPlan)
        assert result.total_count > 0

    def test_placements_have_positions(self):
        plan = _make_test_plan()
        placer = AutoMonitorPlacer()
        result = placer.place_all(plan)
        for p in result.placements:
            assert len(p.position) == 3
            assert all(isinstance(v, (int, float)) for v in p.position)

    def test_by_floor(self):
        plan = _make_test_plan()
        placer = AutoMonitorPlacer()
        result = placer.place_all(plan)
        floors = result.by_floor()
        assert "1F" in floors
        assert "2F" in floors
        assert len(floors["1F"]) > 0

    def test_by_category(self):
        plan = _make_test_plan()
        placer = AutoMonitorPlacer()
        result = placer.place_all(plan)
        cats = result.by_category()
        assert len(cats) > 1

    def test_by_type(self):
        plan = _make_test_plan()
        placer = AutoMonitorPlacer()
        result = placer.place_all(plan)
        types = result.by_type()
        assert len(types) > 5

    def test_total_cost_positive(self):
        plan = _make_test_plan()
        placer = AutoMonitorPlacer()
        result = placer.place_all(plan)
        assert result.total_cost_twd > 0

    def test_all_placements_have_valid_fields(self):
        plan = _make_test_plan()
        placer = AutoMonitorPlacer()
        result = placer.place_all(plan)
        for p in result.placements:
            assert p.monitor_type_id
            assert p.name
            assert p.floor
            assert p.ifc_class in ("IfcSensor", "IfcActuator")
            assert p.predefined_type

    def test_empty_plan(self):
        plan = BuildingPlan(name="Empty")
        placer = AutoMonitorPlacer()
        result = placer.place_all(plan)
        assert result.total_count == 0

    def test_per_building_sensors_present(self):
        plan = _make_test_plan()
        placer = AutoMonitorPlacer()
        result = placer.place_all(plan)
        type_ids = {p.monitor_type_id for p in result.placements}
        # seismic_sensor is per_building, should appear
        assert "seismic_sensor" in type_ids
