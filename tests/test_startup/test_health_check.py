"""Tests for the HealthChecker engine."""

import os
import sys
from unittest.mock import patch, MagicMock

import pytest

from promptbim.startup.health_check import HealthChecker, CheckResult


class TestCheckResult:
    """Test CheckResult dataclass."""

    def test_basic_creation(self):
        r = CheckResult(
            name="test", category="test_cat",
            status="pass", message="OK",
        )
        assert r.name == "test"
        assert r.status == "pass"
        assert r.detail is None
        assert r.fix_hint is None
        assert r.elapsed_ms == 0.0

    def test_with_all_fields(self):
        r = CheckResult(
            name="test", category="cat",
            status="fail", message="Failed",
            detail="some error", fix_hint="do this",
            elapsed_ms=42.5,
        )
        assert r.detail == "some error"
        assert r.fix_hint == "do this"
        assert r.elapsed_ms == 42.5


class TestHealthChecker:
    """Test HealthChecker."""

    def test_categories_defined(self):
        assert len(HealthChecker.CATEGORIES) == 4

    def test_python_version_check_passes(self):
        checker = HealthChecker()
        result = checker._check_python_version()
        if sys.version_info >= (3, 11):
            assert result.status == "pass"
        else:
            assert result.status == "fail"

    def test_conda_env_check(self):
        checker = HealthChecker()
        with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "promptbim"}):
            result = checker._check_conda_env()
            assert result.status == "pass"

    def test_conda_env_wrong_name(self):
        checker = HealthChecker()
        with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "other_env"}):
            result = checker._check_conda_env()
            assert result.status == "warn"

    def test_conda_env_not_set(self):
        checker = HealthChecker()
        with patch.dict(os.environ, {}, clear=True):
            # Clear CONDA_DEFAULT_ENV
            env = os.environ.copy()
            env.pop("CONDA_DEFAULT_ENV", None)
            with patch.dict(os.environ, env, clear=True):
                result = checker._check_conda_env()
                assert result.status == "warn"

    def test_import_check_success(self):
        checker = HealthChecker()
        result = checker._check_import(
            lambda: "ok 1.0", "test_pkg",
        )
        assert result.status == "pass"
        assert result.message == "ok 1.0"

    def test_import_check_failure(self):
        checker = HealthChecker()

        def _fail():
            raise ImportError("no module")

        result = checker._check_import(
            _fail, "missing_pkg", fix_hint="pip install missing_pkg",
        )
        assert result.status == "fail"
        assert result.fix_hint == "pip install missing_pkg"

    def test_filesystem_check_with_env(self, tmp_path):
        """Test filesystem check when .env exists and output is writable."""
        checker = HealthChecker()
        # Create .env in cwd
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            (tmp_path / ".env").write_text("test=1")
            checker._settings.output_dir = tmp_path / "output"
            result = checker._check_filesystem()
            assert result.status == "pass"
        finally:
            os.chdir(original_cwd)

    def test_run_all_returns_12_results(self):
        """Test run_all returns results (mocking AI checks)."""
        checker = HealthChecker()

        # Mock AI checks to avoid real API calls
        with patch("promptbim.startup.ai_check.check_api_key") as mock_key, \
             patch("promptbim.startup.ai_check.ping_claude") as mock_ping, \
             patch("promptbim.startup.ai_check.check_model_available") as mock_model:

            mock_key.return_value = CheckResult(
                name="API Key", category="AI services",
                status="pass", message="mocked",
            )
            mock_ping.return_value = CheckResult(
                name="Claude API ping", category="AI services",
                status="pass", message="mocked",
            )
            mock_model.return_value = CheckResult(
                name="Model available", category="AI services",
                status="pass", message="mocked",
            )

            results = checker.run_all()
            assert len(results) == 12

    def test_run_ai_only(self):
        """Test run_ai_only returns 3 results."""
        checker = HealthChecker()

        with patch("promptbim.startup.ai_check.check_api_key") as mock_key, \
             patch("promptbim.startup.ai_check.ping_claude") as mock_ping, \
             patch("promptbim.startup.ai_check.check_model_available") as mock_model:

            mock_key.return_value = CheckResult(
                name="API Key", category="AI services",
                status="pass", message="mocked",
            )
            mock_ping.return_value = CheckResult(
                name="Claude API ping", category="AI services",
                status="pass", message="mocked",
            )
            mock_model.return_value = CheckResult(
                name="Model available", category="AI services",
                status="pass", message="mocked",
            )

            results = checker.run_ai_only()
            assert len(results) == 3

    def test_summary(self):
        checker = HealthChecker()
        checker._results = [
            CheckResult(name="a", category="c", status="pass", message="ok"),
            CheckResult(name="b", category="c", status="fail", message="bad"),
            CheckResult(name="c", category="c", status="warn", message="meh"),
        ]
        s = checker.summary()
        assert s["total"] == 3
        assert s["passed"] == 1
        assert s["failed"] == 1
        assert s["warned"] == 1
        assert s["all_passed"] is False

    def test_to_dict(self):
        checker = HealthChecker()
        checker._results = [
            CheckResult(name="test", category="cat", status="pass", message="ok", elapsed_ms=5.123),
        ]
        d = checker.to_dict()
        assert len(d) == 1
        assert d[0]["name"] == "test"
        assert d[0]["elapsed_ms"] == 5.1

    def test_skip_ping_when_key_fails(self):
        """Claude API ping should be skipped if API key check failed."""
        checker = HealthChecker()
        checker._results = [
            CheckResult(name="API Key", category="AI services", status="fail", message="not set"),
        ]
        result = checker._check_claude_ping()
        assert result.status == "skip"

    def test_skip_model_when_ping_fails(self):
        """Model check should be skipped if ping failed."""
        checker = HealthChecker()
        checker._results = [
            CheckResult(name="Claude API ping", category="AI services", status="fail", message="failed"),
        ]
        result = checker._check_model_available()
        assert result.status == "skip"
