"""Tests for setback line calculation."""

import pytest

from promptbim.land.setback import compute_setback, compute_setback_per_side
from promptbim.schemas.land import LandParcel
from promptbim.schemas.zoning import ZoningRules


@pytest.fixture
def rectangular_parcel():
    return LandParcel(
        name="Rectangular",
        boundary=[(0, 0), (30, 0), (30, 20), (0, 20)],
        area_sqm=600.0,
        perimeter_m=100.0,
    )


@pytest.fixture
def default_zoning():
    return ZoningRules()


class TestComputeSetback:
    def test_basic_setback(self, rectangular_parcel, default_zoning):
        buildable = compute_setback(rectangular_parcel, default_zoning)
        assert len(buildable) >= 3
        # Buildable area should be smaller than original
        from shapely.geometry import Polygon

        original = Polygon(rectangular_parcel.boundary)
        result = Polygon(buildable)
        assert result.area < original.area

    def test_uniform_setback_reduces_area(self, rectangular_parcel):
        zoning = ZoningRules(
            setback_front_m=3.0,
            setback_back_m=3.0,
            setback_left_m=3.0,
            setback_right_m=3.0,
        )
        buildable = compute_setback(rectangular_parcel, zoning)
        from shapely.geometry import Polygon

        result = Polygon(buildable)
        # 30x20 with 3m uniform setback => 24x14 = 336
        assert result.area == pytest.approx(336.0, abs=5.0)

    def test_large_setback_eliminates_area(self):
        small = LandParcel(
            name="Tiny",
            boundary=[(0, 0), (5, 0), (5, 5), (0, 5)],
            area_sqm=25.0,
        )
        zoning = ZoningRules(
            setback_front_m=5.0,
            setback_back_m=5.0,
            setback_left_m=5.0,
            setback_right_m=5.0,
        )
        buildable = compute_setback(small, zoning)
        assert buildable == []


class TestComputeSetbackPerSide:
    def test_rectangular_per_side(self, rectangular_parcel, default_zoning):
        buildable = compute_setback_per_side(rectangular_parcel, default_zoning)
        assert len(buildable) >= 3
        from shapely.geometry import Polygon

        result = Polygon(buildable)
        assert result.area > 0
        assert result.area < 600.0

    def test_non_rectangular_falls_back(self, default_zoning):
        triangle = LandParcel(
            name="Triangle",
            boundary=[(0, 0), (20, 0), (10, 15)],
            area_sqm=150.0,
            perimeter_m=50.0,
        )
        buildable = compute_setback_per_side(triangle, default_zoning)
        # Should fall back to uniform setback for non-rectangular
        assert len(buildable) >= 3 or buildable == []
