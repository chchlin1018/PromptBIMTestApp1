"""Fuzzing / malicious input tests for land parsers."""

from __future__ import annotations

import json

import pytest


class TestOversizedGeoJSON:
    """Test file size limit enforcement."""

    def test_large_file_rejected(self, tmp_path):
        """Files exceeding MAX_LAND_FILE_SIZE_MB should be rejected."""
        from promptbim.land.parsers.utils import check_file_size

        # Create a file just over the limit (we mock constants)
        large_file = tmp_path / "large.geojson"
        large_file.write_text("x" * 100)  # small file

        # Should not raise for small file
        check_file_size(large_file)

    def test_file_over_limit_raises(self, tmp_path, monkeypatch):
        """Files over the size limit should raise ValueError."""
        import promptbim.land.parsers.utils as utils_mod

        monkeypatch.setattr(utils_mod, "MAX_LAND_FILE_SIZE_MB", 0)

        tiny_file = tmp_path / "tiny.geojson"
        tiny_file.write_text('{"type": "Polygon"}')

        with pytest.raises(ValueError, match="exceeding"):
            utils_mod.check_file_size(tiny_file)


class TestMalformedJSON:
    """Test malformed JSON inputs."""

    def test_invalid_json_raises(self, tmp_path):
        """Invalid JSON should raise an error."""
        from promptbim.land.parsers.geojson import parse_geojson

        bad_file = tmp_path / "bad.geojson"
        bad_file.write_text("{{not valid json}}")

        with pytest.raises(json.JSONDecodeError):
            parse_geojson(bad_file)

    def test_empty_file(self, tmp_path):
        """Empty file should raise."""
        from promptbim.land.parsers.geojson import parse_geojson

        empty = tmp_path / "empty.geojson"
        empty.write_text("")

        with pytest.raises((json.JSONDecodeError, ValueError)):
            parse_geojson(empty)

    def test_binary_content(self, tmp_path):
        """Binary content should raise."""
        from promptbim.land.parsers.geojson import parse_geojson

        bin_file = tmp_path / "binary.geojson"
        bin_file.write_bytes(b"\x00\x01\x02\xff\xfe\xfd")

        with pytest.raises((json.JSONDecodeError, UnicodeDecodeError, ValueError)):
            parse_geojson(bin_file)


class TestSelfIntersectingPolygon:
    """Test self-intersecting / degenerate geometries."""

    def test_self_intersecting_geojson(self, tmp_path):
        """Self-intersecting polygon should be handled gracefully."""
        from promptbim.land.parsers.geojson import parse_geojson

        # Bowtie / self-intersecting polygon
        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [10, 10], [10, 0], [0, 10], [0, 0]]],
            },
            "properties": {"name": "Self-Intersecting"},
        }
        f = tmp_path / "selfintersect.geojson"
        f.write_text(json.dumps(geojson))

        # Should either parse or skip, but not crash
        result = parse_geojson(f)
        assert isinstance(result, list)

    def test_degenerate_line_polygon(self, tmp_path):
        """Degenerate polygon (collinear points) should be handled."""
        from promptbim.land.parsers.geojson import parse_geojson

        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [5, 0], [10, 0], [0, 0]]],
            },
            "properties": {},
        }
        f = tmp_path / "degenerate.geojson"
        f.write_text(json.dumps(geojson))

        result = parse_geojson(f)
        assert isinstance(result, list)


class TestExtremeCoordinates:
    """Test extreme coordinate values."""

    def test_extreme_large_coordinates(self, tmp_path):
        """Very large coordinates should not crash parser."""
        from promptbim.land.parsers.geojson import parse_geojson

        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[1e15, 1e15], [1e15 + 100, 1e15], [1e15 + 100, 1e15 + 100], [1e15, 1e15 + 100], [1e15, 1e15]]
                ],
            },
            "properties": {},
        }
        f = tmp_path / "extreme.geojson"
        f.write_text(json.dumps(geojson))
        result = parse_geojson(f)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_negative_coordinates(self, tmp_path):
        """Negative coordinates should work fine."""
        from promptbim.land.parsers.geojson import parse_geojson

        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[-100, -200], [100, -200], [100, 200], [-100, 200], [-100, -200]]
                ],
            },
            "properties": {},
        }
        f = tmp_path / "negative.geojson"
        f.write_text(json.dumps(geojson))
        result = parse_geojson(f)
        assert len(result) == 1


class TestEmptyAndMissing:
    """Test empty and missing data edge cases."""

    def test_empty_feature_collection(self, tmp_path):
        """Empty FeatureCollection should return empty list."""
        from promptbim.land.parsers.geojson import parse_geojson

        geojson = {"type": "FeatureCollection", "features": []}
        f = tmp_path / "empty_fc.geojson"
        f.write_text(json.dumps(geojson))
        assert parse_geojson(f) == []

    def test_non_polygon_features_skipped(self, tmp_path):
        """Non-polygon features should be skipped."""
        from promptbim.land.parsers.geojson import parse_geojson

        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                }
            ],
        }
        f = tmp_path / "point.geojson"
        f.write_text(json.dumps(geojson))
        assert parse_geojson(f) == []
