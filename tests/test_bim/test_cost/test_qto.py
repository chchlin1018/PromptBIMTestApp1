"""Tests for bim/cost/qto.py — Quantity Take-Off."""

import pytest

from promptbim.bim.cost.qto import QTOItem, QuantityTakeOff
from promptbim.schemas.plan import (
    BuildingPlan,
    OpeningDef,
    RoofPlan,
    StoryPlan,
    WallDef,
)


def _make_simple_plan() -> BuildingPlan:
    """A 10x10m single-story box building on a 20x20m lot."""
    return BuildingPlan(
        name="Test Box",
        land_boundary=[(0, 0), (20, 0), (20, 20), (0, 20)],
        buildable_area=[(2, 2), (18, 2), (18, 18), (2, 18)],
        building_footprint=[(5, 5), (15, 5), (15, 15), (5, 15)],
        building_bcr=0.25,
        building_far=0.25,
        stories=[
            StoryPlan(
                name="1F",
                elevation_m=0.0,
                height_m=3.0,
                walls=[
                    WallDef(start=(5, 5), end=(15, 5), wall_type="exterior"),
                    WallDef(start=(15, 5), end=(15, 15), wall_type="exterior"),
                    WallDef(start=(15, 15), end=(5, 15), wall_type="exterior"),
                    WallDef(start=(5, 15), end=(5, 5), wall_type="exterior"),
                    WallDef(start=(10, 5), end=(10, 15), wall_type="interior"),
                ],
                spaces=[],
                openings=[
                    OpeningDef(
                        wall_index=0,
                        offset_m=4.0,
                        width_m=1.0,
                        height_m=2.1,
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
                slab_boundary=[(5, 5), (15, 5), (15, 15), (5, 15)],
            ),
        ],
        roof=RoofPlan(roof_type="flat"),
    )


class TestQuantityTakeOff:
    def test_extract_returns_items(self):
        plan = _make_simple_plan()
        qto = QuantityTakeOff()
        items = qto.extract(plan)
        assert len(items) > 0
        assert all(isinstance(i, QTOItem) for i in items)

    def test_wall_quantities(self):
        plan = _make_simple_plan()
        qto = QuantityTakeOff()
        items = qto.extract(plan)
        walls = [i for i in items if i.ifc_class == "IfcWall"]
        assert len(walls) == 5
        # 4 exterior + 1 interior
        ext = [w for w in walls if w.category == "wall_exterior"]
        assert len(ext) == 4
        # Each exterior wall is 10m * 3m = 30 m2
        for w in ext:
            assert abs(w.quantity - 30.0) < 0.1

    def test_slab_quantity(self):
        plan = _make_simple_plan()
        qto = QuantityTakeOff()
        items = qto.extract(plan)
        slabs = [i for i in items if i.category == "slab"]
        assert len(slabs) == 1
        # 10x10 = 100 m2
        assert abs(slabs[0].quantity - 100.0) < 0.1

    def test_roof_quantity(self):
        plan = _make_simple_plan()
        qto = QuantityTakeOff()
        items = qto.extract(plan)
        roofs = [i for i in items if i.category == "roof"]
        assert len(roofs) == 1
        assert abs(roofs[0].quantity - 100.0) < 0.1

    def test_openings(self):
        plan = _make_simple_plan()
        qto = QuantityTakeOff()
        items = qto.extract(plan)
        doors = [i for i in items if i.category == "door"]
        windows = [i for i in items if i.category == "window"]
        assert len(doors) == 1
        assert doors[0].quantity == 1
        assert len(windows) == 1
        assert abs(windows[0].quantity - 1.8) < 0.01  # 1.5 * 1.2

    def test_mep_allowances(self):
        plan = _make_simple_plan()
        qto = QuantityTakeOff()
        items = qto.extract(plan)
        mep_cats = {"mep_hvac", "mep_plumbing", "mep_electrical", "mep_fire"}
        mep_items = [i for i in items if i.category in mep_cats]
        assert len(mep_items) == 4
        for m in mep_items:
            assert abs(m.quantity - 100.0) < 0.1  # floor area

    def test_site_work(self):
        plan = _make_simple_plan()
        qto = QuantityTakeOff()
        items = qto.extract(plan)
        site = [i for i in items if i.category == "site_work"]
        assert len(site) == 1
        # land=400, footprint=100, site=300
        assert abs(site[0].quantity - 300.0) < 0.1

    def test_polygon_area_triangle(self):
        area = QuantityTakeOff._polygon_area([(0, 0), (10, 0), (0, 10)])
        assert abs(area - 50.0) < 0.01

    def test_polygon_area_empty(self):
        assert QuantityTakeOff._polygon_area([]) == 0.0
        assert QuantityTakeOff._polygon_area([(0, 0)]) == 0.0

    def test_empty_plan(self):
        plan = BuildingPlan(name="Empty")
        qto = QuantityTakeOff()
        items = qto.extract(plan)
        assert items == []
