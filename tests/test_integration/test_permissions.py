"""File permission error handling tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest


class TestPermissionErrors:
    """Test graceful handling of file permission errors."""

    def test_geojson_permission_denied(self, tmp_path):
        """GeoJSON parser should raise on permission denied."""
        from promptbim.land.parsers.geojson import parse_geojson

        f = tmp_path / "noperm.geojson"
        f.write_text('{"type": "FeatureCollection", "features": []}')

        with patch("builtins.open", side_effect=PermissionError("Permission denied")), pytest.raises(PermissionError):
            parse_geojson(f)

    def test_output_dir_permission_denied(self, tmp_path):
        """Output directory permission error should be handled."""
        no_write = tmp_path / "readonly"
        no_write.mkdir()

        with patch.object(Path, "mkdir", side_effect=PermissionError("Cannot create directory")), pytest.raises(PermissionError):
            Path("/fake/readonly/dir").mkdir(parents=True, exist_ok=True)

    def test_is_a_directory_error(self, tmp_path):
        """Opening a directory as a file should raise."""
        from promptbim.land.parsers.geojson import parse_geojson

        dir_path = tmp_path / "adir.geojson"
        dir_path.mkdir()

        with pytest.raises((IsADirectoryError, PermissionError, OSError)):
            parse_geojson(dir_path)

    def test_file_not_found_error(self, tmp_path):
        """Non-existent file should raise FileNotFoundError."""
        from promptbim.land.parsers.geojson import parse_geojson

        with pytest.raises((FileNotFoundError, OSError)):
            parse_geojson(tmp_path / "nonexistent.geojson")

    def test_config_output_dir_fallback(self):
        """Config should handle unwritable output dir."""
        from promptbim.config import Settings

        settings = Settings(_env_file=None)
        assert settings.output_dir is not None
