"""Tests for land parcel parsers."""

import json
from pathlib import Path

import pytest

from promptbim.land.parsers.geojson import parse_geojson
from promptbim.land.parsers.manual import parse_manual

FIXTURES = Path(__file__).parent.parent / "fixtures"


class TestGeoJSONParser:
    def test_parse_sample_parcel(self):
        parcels = parse_geojson(FIXTURES / "sample_parcel.geojson")
        assert len(parcels) == 1
        parcel = parcels[0]
        assert parcel.name == "Sample Taipei Parcel"
        assert parcel.source_type == "geojson"
        assert len(parcel.boundary) == 4
        assert parcel.area_sqm == pytest.approx(600.0, abs=0.1)
        assert parcel.perimeter_m == pytest.approx(100.0, abs=0.1)

    def test_parse_single_feature(self, tmp_path):
        data = {
            "type": "Feature",
            "properties": {"name": "Single"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
            },
        }
        f = tmp_path / "single.geojson"
        f.write_text(json.dumps(data))
        parcels = parse_geojson(f)
        assert len(parcels) == 1
        assert parcels[0].area_sqm == pytest.approx(100.0, abs=0.1)

    def test_parse_bare_polygon(self, tmp_path):
        data = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [5, 0], [5, 5], [0, 5], [0, 0]]],
        }
        f = tmp_path / "bare.geojson"
        f.write_text(json.dumps(data))
        parcels = parse_geojson(f)
        assert len(parcels) == 1
        assert parcels[0].area_sqm == pytest.approx(25.0, abs=0.1)

    def test_empty_feature_collection(self, tmp_path):
        data = {"type": "FeatureCollection", "features": []}
        f = tmp_path / "empty.geojson"
        f.write_text(json.dumps(data))
        parcels = parse_geojson(f)
        assert len(parcels) == 0


class TestManualParser:
    def test_basic_rectangle(self):
        parcel = parse_manual([(0, 0), (20, 0), (20, 15), (0, 15)], name="Test Lot")
        assert parcel.name == "Test Lot"
        assert parcel.area_sqm == pytest.approx(300.0, abs=0.1)
        assert parcel.source_type == "manual"
        assert len(parcel.boundary) == 4

    def test_closed_polygon_removes_duplicate(self):
        coords = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        parcel = parse_manual(coords)
        assert len(parcel.boundary) == 4

    def test_too_few_points_raises(self):
        with pytest.raises(ValueError, match="At least 3"):
            parse_manual([(0, 0), (1, 1)])

    def test_triangle(self):
        parcel = parse_manual([(0, 0), (10, 0), (5, 8)])
        assert parcel.area_sqm == pytest.approx(40.0, abs=0.1)

    def test_l_shaped_parcel(self):
        coords = [(0, 0), (20, 0), (20, 10), (10, 10), (10, 20), (0, 20)]
        parcel = parse_manual(coords, name="L-Shaped")
        assert parcel.name == "L-Shaped"
        assert parcel.area_sqm == pytest.approx(300.0, abs=0.1)
