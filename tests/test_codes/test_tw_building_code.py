"""Tests for Taiwan Building Code rules."""

import pytest

from promptbim.codes.base import Severity
from promptbim.codes.tw_building_code import (
    BCRRule,
    CeilingHeightRule,
    CorridorRule,
    ElevatorRule,
    FARRule,
    HeightLimitRule,
    ParkingRule,
    StairRule,
)
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan, RoofPlan, SpaceDef, StoryPlan, WallDef
from promptbim.schemas.zoning import ZoningRules


# -- Fixtures ----------------------------------------------------------------

def _land(area: float = 500.0) -> LandParcel:
    """Square land parcel of given area."""
    side = area ** 0.5
    return LandParcel(
        boundary=[(0, 0), (side, 0), (side, side), (0, side)],
        area_sqm=area,
    )


def _zoning(**kwargs) -> ZoningRules:
    defaults = dict(bcr_limit=0.6, far_limit=2.0, height_limit_m=15.0)
    defaults.update(kwargs)
    return ZoningRules(**defaults)


def _plan(
    footprint_side: float = 15.0,
    num_stories: int = 3,
    story_height: float = 3.0,
    space_type: str = "office",
) -> BuildingPlan:
    fp = [(0, 0), (footprint_side, 0), (footprint_side, footprint_side), (0, footprint_side)]
    stories = []
    for i in range(num_stories):
        stories.append(StoryPlan(
            name=f"{i+1}F",
            elevation_m=i * story_height,
            height_m=story_height,
            walls=[
                WallDef(start=(0, 0), end=(footprint_side, 0)),
                WallDef(start=(footprint_side, 0), end=(footprint_side, footprint_side)),
                WallDef(start=(footprint_side, footprint_side), end=(0, footprint_side)),
                WallDef(start=(0, footprint_side), end=(0, 0)),
            ],
            spaces=[SpaceDef(
                name=f"Room {i+1}F",
                boundary=fp,
                space_type=space_type,
                area_sqm=footprint_side ** 2,
            )],
            slab_boundary=fp,
        ))
    return BuildingPlan(
        name="Test Building",
        building_footprint=fp,
        building_bcr=footprint_side ** 2 / 500,
        building_far=footprint_side ** 2 * num_stories / 500,
        stories=stories,
        roof=RoofPlan(),
    )


# -- BCR Tests ---------------------------------------------------------------

class TestBCRRule:
    def test_pass(self):
        plan = _plan(footprint_side=15.0)  # 225/500 = 0.45
        results = BCRRule().check(plan, _land(), _zoning(bcr_limit=0.6))
        assert results[0].severity == Severity.PASS

    def test_fail(self):
        plan = _plan(footprint_side=20.0)  # 400/500 = 0.80
        results = BCRRule().check(plan, _land(), _zoning(bcr_limit=0.6))
        assert results[0].severity == Severity.FAIL

    def test_warning_near_limit(self):
        plan = _plan(footprint_side=17.0)  # 289/500 = 0.578 (97% of 0.6)
        results = BCRRule().check(plan, _land(), _zoning(bcr_limit=0.6))
        assert results[0].severity == Severity.WARNING


# -- FAR Tests ---------------------------------------------------------------

class TestFARRule:
    def test_pass(self):
        plan = _plan(footprint_side=15.0, num_stories=3)  # 675/500 = 1.35
        results = FARRule().check(plan, _land(), _zoning(far_limit=2.0))
        assert results[0].severity == Severity.PASS

    def test_fail(self):
        plan = _plan(footprint_side=15.0, num_stories=5)  # 1125/500 = 2.25
        results = FARRule().check(plan, _land(), _zoning(far_limit=2.0))
        assert results[0].severity == Severity.FAIL


# -- Height Tests ------------------------------------------------------------

class TestHeightLimitRule:
    def test_pass(self):
        plan = _plan(num_stories=3, story_height=3.0)  # 9m
        results = HeightLimitRule().check(plan, _land(), _zoning(height_limit_m=15.0))
        assert results[0].severity == Severity.PASS

    def test_fail(self):
        plan = _plan(num_stories=6, story_height=3.0)  # 18m
        results = HeightLimitRule().check(plan, _land(), _zoning(height_limit_m=15.0))
        assert results[0].severity == Severity.FAIL


# -- Stair Tests -------------------------------------------------------------

class TestStairRule:
    def test_single_story(self):
        plan = _plan(num_stories=1)
        results = StairRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.PASS

    def test_multi_story(self):
        plan = _plan(num_stories=3)
        results = StairRule().check(plan, _land(), _zoning())
        assert len(results) >= 1
        assert results[0].severity == Severity.INFO


# -- Corridor Tests ----------------------------------------------------------

class TestCorridorRule:
    def test_no_corridors(self):
        plan = _plan()
        results = CorridorRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.PASS


# -- Ceiling Height Tests ---------------------------------------------------

class TestCeilingHeightRule:
    def test_pass(self):
        plan = _plan(story_height=3.0)  # net = 3.0 - 0.2 = 2.8
        results = CeilingHeightRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.PASS

    def test_fail(self):
        plan = _plan(story_height=2.2)  # net = 2.2 - 0.2 = 2.0
        results = CeilingHeightRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.FAIL


# -- Elevator Tests ----------------------------------------------------------

class TestElevatorRule:
    def test_low_rise(self):
        plan = _plan(num_stories=3)
        results = ElevatorRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.PASS

    def test_six_stories(self):
        plan = _plan(num_stories=6)
        results = ElevatorRule().check(plan, _land(), _zoning(height_limit_m=30.0))
        assert any(r.severity == Severity.INFO for r in results)


# -- Parking Tests -----------------------------------------------------------

class TestParkingRule:
    def test_small_building(self):
        plan = _plan(footprint_side=5.0, num_stories=1)  # 25 sqm
        results = ParkingRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.PASS

    def test_large_building(self):
        plan = _plan(footprint_side=15.0, num_stories=3)  # 675 sqm
        results = ParkingRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.INFO
