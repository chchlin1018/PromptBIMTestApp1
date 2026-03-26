"""P23 Sprint test additions — 20+ new tests covering rate limiting, cache,
schema validation, config, debug, geometry edge cases, web validation, and imports.
"""

from __future__ import annotations

import logging
import math
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).parent.parent


# ===========================================================================
# 1. Rate limiter tests (mock-based)
# ===========================================================================


class TestRateLimiter:
    """Test API rate limiting behaviour via config settings."""

    def test_rate_limit_config_default(self):
        from promptbim.config import Settings

        s = Settings(_env_file=None)
        assert s.api_rate_limit_rpm == 50

    def test_rate_limit_config_custom(self):
        from promptbim.config import Settings

        s = Settings(_env_file=None, api_rate_limit_rpm=100)
        assert s.api_rate_limit_rpm == 100

    def test_rate_limit_zero_allowed(self):
        """A zero rate limit means unlimited — should not raise."""
        from promptbim.config import Settings

        s = Settings(_env_file=None, api_rate_limit_rpm=0)
        assert s.api_rate_limit_rpm == 0

    def test_api_timeout_default(self):
        from promptbim.config import Settings

        s = Settings(_env_file=None)
        assert s.api_timeout_seconds == 30.0

    def test_api_timeout_custom(self):
        from promptbim.config import Settings

        s = Settings(_env_file=None, api_timeout_seconds=60.0)
        assert s.api_timeout_seconds == 60.0


# ===========================================================================
# 2. Cache concurrency tests
# ===========================================================================


class TestCacheConcurrency:
    """Verify cache settings and concurrent access safety."""

    def test_cache_enabled_default(self):
        from promptbim.config import Settings

        s = Settings(_env_file=None)
        assert s.cache_enabled is True

    def test_cache_ttl_default(self):
        from promptbim.config import Settings

        s = Settings(_env_file=None)
        assert s.cache_ttl_days == 7

    def test_cache_disabled(self):
        from promptbim.config import Settings

        s = Settings(_env_file=None, cache_enabled=False)
        assert s.cache_enabled is False

    def test_concurrent_settings_access(self):
        """Multiple threads reading settings should not crash."""
        from promptbim.config import Settings

        errors: list[Exception] = []
        s = Settings(_env_file=None)

        def reader():
            try:
                for _ in range(100):
                    _ = s.cache_enabled
                    _ = s.api_rate_limit_rpm
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=reader) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0


# ===========================================================================
# 3. Schema validation tests
# ===========================================================================


class TestSchemaValidation:
    """Validate Pydantic schemas enforce constraints."""

    def test_land_parcel_requires_boundary(self):
        from promptbim.schemas.land import LandParcel

        with pytest.raises(Exception):
            LandParcel(area_sqm=100.0)  # missing boundary

    def test_land_parcel_valid(self):
        from promptbim.schemas.land import LandParcel

        lp = LandParcel(
            boundary=[(0, 0), (10, 0), (10, 10), (0, 10)],
            area_sqm=100.0,
        )
        assert lp.area_sqm == 100.0
        assert len(lp.boundary) == 4

    def test_building_plan_defaults(self):
        from promptbim.schemas.plan import BuildingPlan

        bp = BuildingPlan(name="Test")
        assert bp.schema_version == "2.4.0"
        assert bp.stories == []
        assert bp.building_bcr == 0.0

    def test_wall_def_defaults(self):
        from promptbim.schemas.plan import WallDef

        w = WallDef(start=(0, 0), end=(5, 0))
        assert w.thickness_m == 0.2
        assert w.wall_type == "exterior"

    def test_zoning_rules_defaults(self):
        from promptbim.schemas.zoning import ZoningRules

        z = ZoningRules()
        assert z.far_limit == 2.0
        assert z.bcr_limit == 0.6
        assert z.height_limit_m == 15.0


# ===========================================================================
# 4. Config loading tests
# ===========================================================================


class TestConfigLoading:
    """Test configuration loading edge cases."""

    def test_get_settings_no_env_file(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("PROMPTBIM_ENV_FILE", raising=False)
        from promptbim.config import get_settings

        s = get_settings()
        assert s.log_level == "INFO"

    def test_validate_api_key_valid(self):
        from promptbim.config import validate_api_key

        assert validate_api_key("sk-ant-api03-" + "x" * 20) is True

    def test_validate_api_key_empty(self):
        from promptbim.config import validate_api_key

        assert validate_api_key("") is False

    def test_validate_api_key_wrong_prefix(self):
        from promptbim.config import validate_api_key

        assert validate_api_key("bad-key-format") is False

    def test_validate_api_key_too_short(self):
        from promptbim.config import validate_api_key

        assert validate_api_key("sk-ant-x") is False


# ===========================================================================
# 5. Debug logger tests
# ===========================================================================


class TestDebugLoggerExtended:
    """Extended debug logger tests for P23."""

    def test_get_logger_prefix(self):
        from promptbim.debug import get_logger

        logger = get_logger("p23.test")
        assert logger.name == "promptbim.p23.test"

    def test_setup_file_logging(self, tmp_path):
        from promptbim.debug import setup_file_logging

        log_file = setup_file_logging(log_dir=tmp_path / "test_logs")
        assert Path(log_file).exists()
        assert (tmp_path / "test_logs").is_dir()

    def test_color_formatter_module_detection(self):
        from promptbim.debug import _ColorFormatter

        fmt = _ColorFormatter(use_color=False)
        record = logging.LogRecord(
            name="promptbim.bim.test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        output = fmt.format(record)
        assert "test message" in output


# ===========================================================================
# 6. Geometry poly_area edge cases
# ===========================================================================


class TestPolyAreaEdgeCases:
    """Edge cases for the Shoelace polygon area function."""

    def test_poly_area_single_point(self):
        from promptbim.bim.geometry import poly_area

        assert poly_area([(5, 5)]) == 0.0

    def test_poly_area_collinear_points(self):
        from promptbim.bim.geometry import poly_area

        assert poly_area([(0, 0), (5, 0), (10, 0)]) == pytest.approx(0.0)

    def test_poly_area_large_polygon(self):
        from promptbim.bim.geometry import poly_area

        # 1km x 1km square
        area = poly_area([(0, 0), (1000, 0), (1000, 1000), (0, 1000)])
        assert area == pytest.approx(1_000_000.0)

    def test_poly_area_negative_coords(self):
        from promptbim.bim.geometry import poly_area

        area = poly_area([(-5, -5), (5, -5), (5, 5), (-5, 5)])
        assert area == pytest.approx(100.0)

    def test_poly_area_clockwise_vs_counterclockwise(self):
        from promptbim.bim.geometry import poly_area

        ccw = poly_area([(0, 0), (10, 0), (10, 10), (0, 10)])
        cw = poly_area([(0, 0), (0, 10), (10, 10), (10, 0)])
        assert ccw == pytest.approx(cw)  # abs() makes winding irrelevant


# ===========================================================================
# 7. Web app validation patterns
# ===========================================================================


class TestWebAppValidation:
    """Verify web module exists and is importable."""

    def test_web_module_importable(self):
        import promptbim.web

        assert hasattr(promptbim.web, "__name__")

    def test_web_module_docstring(self):
        import promptbim.web

        assert promptbim.web.__doc__ is not None


# ===========================================================================
# 8. Import / version checks
# ===========================================================================


class TestImportAndVersion:
    """Verify package imports and version string."""

    def test_version_string_format(self):
        import promptbim

        parts = promptbim.__version__.split(".")
        assert len(parts) == 3
        for p in parts:
            assert p.isdigit()

    def test_version_is_2_10_0(self):
        import promptbim

        assert promptbim.__version__ == "2.10.0"

    def test_author_set(self):
        import promptbim

        assert "Michael Lin" in promptbim.__author__

    def test_lazy_submodules_defined(self):
        import promptbim

        assert "schemas" in promptbim._LAZY_SUBMODULES
        assert "bim" in promptbim._LAZY_SUBMODULES
        assert "web" in promptbim._LAZY_SUBMODULES

    def test_lazy_import_schemas(self):
        import promptbim

        schemas = promptbim.schemas
        assert hasattr(schemas, "__name__")

    def test_invalid_submodule_raises(self):
        import promptbim

        with pytest.raises(AttributeError):
            _ = promptbim.nonexistent_module_xyz
