"""Non-mock smoke tests for critical paths.

These tests exercise real code paths without mocking, skipping
if external dependencies (e.g., API keys) are unavailable.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest


class TestSmoke:
    """Smoke tests that exercise real code paths."""

    def test_cli_version_output(self):
        """Verify CLI --version runs and returns expected format."""
        result = subprocess.run(
            [sys.executable, "-m", "promptbim", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0
        assert "promptbim" in result.stdout.lower()

    def test_cli_check_without_ai(self):
        """Verify `python -m promptbim check` runs (non-AI checks)."""
        result = subprocess.run(
            [sys.executable, "-m", "promptbim", "check"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # May fail if API key missing, but should not crash
        assert result.returncode in (0, 1)
        assert "Health Check" in result.stdout

    @pytest.mark.api
    def test_cli_check_ai(self):
        """Verify `python -m promptbim check --ai` with real API key."""
        if not os.getenv("ANTHROPIC_API_KEY", "").startswith("sk-"):
            # Try loading from .env
            try:
                from promptbim.config import get_settings

                settings = get_settings()
                if not settings.anthropic_api_key.startswith("sk-"):
                    pytest.skip("No API key available")
            except Exception:
                pytest.skip("No API key available")

        result = subprocess.run(
            [sys.executable, "-m", "promptbim", "check", "--ai"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1)
        assert "Health Check" in result.stdout

    def test_import_all_core_modules(self):
        """Verify all core modules can be imported without error."""
        modules = [
            "promptbim",
            "promptbim.config",
            "promptbim.schemas.land",
            "promptbim.schemas.plan",
            "promptbim.bim.ifc_generator",
            "promptbim.bim.usd_generator",
            "promptbim.bim.templates",
            "promptbim.codes.registry",
            "promptbim.bim.cost.estimator",
        ]
        for mod_name in modules:
            __import__(mod_name)
