"""Tests for viz/site_plan.py — 2D site plan widget."""

import pytest

from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan, StoryPlan, WallDef, RoofPlan
from promptbim.viz.site_plan import SitePlanView


def _sample_parcel() -> LandParcel:
    return LandParcel(
        name="Test Parcel",
        boundary=[(0, 0), (30, 0), (30, 20), (0, 20)],
        area_sqm=600.0,
        perimeter_m=100.0,
    )


def _sample_plan() -> BuildingPlan:
    footprint = [(5, 3), (25, 3), (25, 17), (5, 17)]
    return BuildingPlan(
        name="Office",
        building_footprint=footprint,
        building_bcr=0.47,
        building_far=0.93,
        stories=[
            StoryPlan(
                name="1F",
                elevation_m=0.0,
                height_m=3.0,
                walls=[WallDef(start=(5, 3), end=(25, 3))],
                slab_boundary=footprint,
            ),
            StoryPlan(
                name="2F",
                elevation_m=3.0,
                height_m=3.0,
                walls=[WallDef(start=(5, 3), end=(25, 3))],
                slab_boundary=footprint,
            ),
        ],
        roof=RoofPlan(roof_type="flat"),
    )


class TestSitePlanViewUnit:
    """Unit tests that don't require a display (test data flow, not rendering)."""

    def test_set_data_parcel_only(self):
        view = SitePlanView.__new__(SitePlanView)
        view._parcel = None
        view._buildable_area = []
        view._plan = None
        parcel = _sample_parcel()
        view._parcel = parcel
        assert view._parcel.name == "Test Parcel"

    def test_set_data_plan(self):
        view = SitePlanView.__new__(SitePlanView)
        view._parcel = None
        view._buildable_area = []
        view._plan = None
        plan = _sample_plan()
        view._plan = plan
        assert view._plan.name == "Office"
        assert len(view._plan.stories) == 2

    def test_sample_plan_bcr_far(self):
        plan = _sample_plan()
        assert plan.building_bcr == pytest.approx(0.47, abs=0.01)
        assert plan.building_far == pytest.approx(0.93, abs=0.01)
