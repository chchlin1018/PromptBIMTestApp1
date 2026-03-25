"""Tests for seismic, fire, and accessibility rules."""

import pytest

from promptbim.codes.base import Severity
from promptbim.codes.tw_seismic_code import (
    SeismicDesignRule,
    get_min_column_cm,
    get_seismic_params,
)
from promptbim.codes.tw_fire_code import (
    FireCompartmentRule,
    FireConstructionRule,
    FireEscapeRule,
    SafetyStairRule,
    TwoStairsRule,
)
from promptbim.codes.tw_accessibility_code import AccessibilityRule
from promptbim.codes.tw_zoning_data import lookup_zoning
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan, RoofPlan, SpaceDef, StoryPlan, WallDef
from promptbim.schemas.zoning import ZoningRules


def _land(area: float = 500.0) -> LandParcel:
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
        stories=stories,
        roof=RoofPlan(),
    )


# -- Seismic Tests -----------------------------------------------------------

class TestSeismicDesignRule:
    def test_returns_info(self):
        results = SeismicDesignRule().check(_plan(), _land(), _zoning())
        assert len(results) >= 2
        assert all(r.severity in (Severity.INFO, Severity.WARNING) for r in results)

    def test_shear_wall_warning_high_rise(self):
        plan = _plan(num_stories=12)
        results = SeismicDesignRule().check(plan, _land(), _zoning(height_limit_m=50.0))
        warnings = [r for r in results if r.severity == Severity.WARNING]
        assert len(warnings) >= 1


class TestSeismicHelpers:
    def test_get_min_column_cm(self):
        assert get_min_column_cm(3) == 40
        assert get_min_column_cm(8) == 50
        assert get_min_column_cm(15) == 60

    def test_get_seismic_params_known(self):
        p = get_seismic_params("台北市")
        assert p["Ss"] == 0.60
        assert p["S1"] == 0.30

    def test_get_seismic_params_unknown(self):
        p = get_seismic_params("未知城市")
        assert "Ss" in p
        assert "S1" in p


# -- Fire Tests --------------------------------------------------------------

class TestFireConstructionRule:
    def test_small_building(self):
        plan = _plan(num_stories=2, footprint_side=10.0)  # 2F, 200sqm total
        results = FireConstructionRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.PASS

    def test_large_building(self):
        plan = _plan(num_stories=5, footprint_side=20.0)
        results = FireConstructionRule().check(plan, _land(), _zoning(height_limit_m=30.0))
        assert results[0].severity == Severity.INFO


class TestFireCompartmentRule:
    def test_small_floors(self):
        plan = _plan(footprint_side=15.0)  # 225 sqm/floor
        results = FireCompartmentRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.PASS

    def test_large_floor(self):
        plan = _plan(footprint_side=40.0, num_stories=1)  # 1600 sqm
        results = FireCompartmentRule().check(plan, _land(area=5000), _zoning())
        assert results[0].severity == Severity.WARNING


class TestFireEscapeRule:
    def test_normal_building(self):
        plan = _plan(footprint_side=15.0)  # diagonal ~21m, half ~10.5m
        results = FireEscapeRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.PASS


class TestTwoStairsRule:
    def test_low_rise(self):
        plan = _plan(num_stories=3)
        results = TwoStairsRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.PASS

    def test_high_rise(self):
        plan = _plan(num_stories=8, footprint_side=15.0)
        results = TwoStairsRule().check(plan, _land(), _zoning(height_limit_m=30.0))
        assert any(r.severity == Severity.INFO for r in results)


class TestSafetyStairRule:
    def test_low_rise(self):
        plan = _plan(num_stories=5)
        results = SafetyStairRule().check(plan, _land(), _zoning())
        assert results[0].severity == Severity.PASS

    def test_high_rise(self):
        plan = _plan(num_stories=16)
        results = SafetyStairRule().check(plan, _land(), _zoning(height_limit_m=60.0))
        assert results[0].severity == Severity.INFO


# -- Accessibility Tests -----------------------------------------------------

class TestAccessibilityRule:
    def test_commercial(self):
        results = AccessibilityRule().check(
            _plan(space_type="office"), _land(), _zoning(zone_type="commercial")
        )
        assert len(results) >= 3  # ramp, elevator, toilet, parking, path

    def test_residential(self):
        results = AccessibilityRule().check(
            _plan(), _land(), _zoning(zone_type="residential")
        )
        assert results[0].severity == Severity.INFO


# -- Zoning Data Tests -------------------------------------------------------

class TestZoningData:
    def test_lookup_taipei(self):
        data = lookup_zoning(city="台北市", zone_name="商三")
        assert data["bcr"] == 0.65
        assert data["far"] == 5.60

    def test_lookup_non_urban(self):
        data = lookup_zoning(zone_name="甲種建築用地")
        assert data["bcr"] == 0.60
        assert data["far"] == 2.40

    def test_lookup_generic_fallback(self):
        data = lookup_zoning(zone_type="commercial")
        assert "bcr" in data
        assert "far" in data

    def test_lookup_unknown(self):
        data = lookup_zoning(city="未知", zone_name="未知", zone_type="residential")
        assert data["bcr"] == 0.50
