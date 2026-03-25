"""Tests for coordinate projection utilities."""

import pytest

from promptbim.land.projection import to_local_meters, reproject_coords
from promptbim.schemas.land import LandParcel


class TestToLocalMeters:
    def test_local_crs_passthrough(self):
        parcel = LandParcel(
            name="Local",
            boundary=[(0, 0), (30, 0), (30, 20), (0, 20)],
            area_sqm=600.0,
            crs="LOCAL",
        )
        result = to_local_meters(parcel)
        assert result.boundary == parcel.boundary
        assert result.crs == "LOCAL"

    def test_already_target_crs(self):
        parcel = LandParcel(
            name="Already Projected",
            boundary=[(250000, 2750000), (250030, 2750000), (250030, 2750020), (250000, 2750020)],
            area_sqm=600.0,
            crs="EPSG:3826",
        )
        result = to_local_meters(parcel, target_crs="EPSG:3826")
        assert result.boundary == parcel.boundary

    def test_wgs84_to_tw97(self):
        # A small parcel near Taipei (WGS84 coords)
        parcel = LandParcel(
            name="Taipei Parcel",
            boundary=[
                (121.5, 25.0),
                (121.5003, 25.0),
                (121.5003, 25.0002),
                (121.5, 25.0002),
            ],
            area_sqm=0.0,  # will be recalculated
            crs="EPSG:4326",
        )
        result = to_local_meters(parcel, target_crs="EPSG:3826")
        assert result.crs == "EPSG:3826"
        # Coordinates should now be in meters, centered around 0
        for x, y in result.boundary:
            assert abs(x) < 100  # local coords should be small
            assert abs(y) < 100
        assert result.area_sqm > 0
        assert result.local_origin != (0.0, 0.0)


class TestReprojectCoords:
    def test_same_crs(self):
        coords = [(121.5, 25.0), (121.6, 25.1)]
        result = reproject_coords(coords, "EPSG:4326", "EPSG:4326")
        assert result == coords

    def test_wgs84_to_3826(self):
        coords = [(121.5, 25.0)]
        result = reproject_coords(coords, "EPSG:4326", "EPSG:3826")
        assert len(result) == 1
        x, y = result[0]
        # TWD97 coordinates for Taipei area should be ~250000, ~2750000
        assert 200000 < x < 350000
        assert 2700000 < y < 2800000
