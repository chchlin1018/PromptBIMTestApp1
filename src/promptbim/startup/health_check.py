"""Health check engine for PromptBIM startup validation.

Runs 12 checks across 4 categories:
- Python environment (2): version, conda env
- Core dependencies (6): ifcopenshell, pxr, PySide6, anthropic, shapely+pyproj, pyvista+pyvistaqt
- AI services (3): API key, Claude ping, model availability
- Filesystem (1): .env + output/ writable
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from typing import Literal

from promptbim.debug import get_logger

logger = get_logger("startup")


@dataclass
class CheckResult:
    """Result of a single health check."""

    name: str
    category: str
    status: Literal["pass", "fail", "warn", "skip"]
    message: str
    detail: str | None = None
    fix_hint: str | None = None
    elapsed_ms: float = 0.0


class HealthChecker:
    """Runs all startup health checks."""

    CATEGORIES = ["Python environment", "Core dependencies", "AI services", "Filesystem"]

    def __init__(self, settings=None):
        if settings is None:
            from promptbim.config import get_settings
            settings = get_settings()
        self._settings = settings
        self._results: list[CheckResult] = []

    @property
    def results(self) -> list[CheckResult]:
        return list(self._results)

    def run_all(self) -> list[CheckResult]:
        """Run all 12 checks and return results."""
        self._results = []
        logger.debug("=== System Health Check Starting ===")
        total_start = time.monotonic()

        checks = [
            # Python environment
            self._check_python_version,
            self._check_conda_env,
            # Core dependencies
            self._check_ifcopenshell,
            self._check_pxr,
            self._check_pyside6,
            self._check_anthropic,
            self._check_shapely_pyproj,
            self._check_pyvista,
            # AI services
            self._check_api_key,
            self._check_claude_ping,
            self._check_model_available,
            # Filesystem
            self._check_filesystem,
        ]

        for i, check_fn in enumerate(checks, 1):
            result = check_fn()
            self._results.append(result)
            status_icon = {"pass": "\u2705", "fail": "\u274c", "warn": "\u26a0\ufe0f", "skip": "\u23ed\ufe0f"}
            logger.debug(
                "[%d/%d] %s: %s %s (%.0fms)",
                i, len(checks), result.name, result.message,
                status_icon.get(result.status, "?"), result.elapsed_ms,
            )

        total_ms = (time.monotonic() - total_start) * 1000
        passed = sum(1 for r in self._results if r.status == "pass")
        logger.debug(
            "=== Health Check Complete: %d/%d PASS (%.1fs) ===",
            passed, len(self._results), total_ms / 1000,
        )
        return self._results

    def run_category(self, category: str) -> list[CheckResult]:
        """Run checks for a specific category only."""
        all_results = self.run_all()
        return [r for r in all_results if r.category == category]

    def run_ai_only(self) -> list[CheckResult]:
        """Run only AI-related checks."""
        self._results = []
        for check_fn in [self._check_api_key, self._check_claude_ping, self._check_model_available]:
            self._results.append(check_fn())
        return self._results

    def summary(self) -> dict:
        """Return summary dict of check results."""
        passed = sum(1 for r in self._results if r.status == "pass")
        failed = sum(1 for r in self._results if r.status == "fail")
        warned = sum(1 for r in self._results if r.status == "warn")
        skipped = sum(1 for r in self._results if r.status == "skip")
        return {
            "total": len(self._results),
            "passed": passed,
            "failed": failed,
            "warned": warned,
            "skipped": skipped,
            "all_passed": failed == 0,
        }

    def to_dict(self) -> list[dict]:
        """Serialize results to list of dicts (for JSON output)."""
        return [
            {
                "name": r.name,
                "category": r.category,
                "status": r.status,
                "message": r.message,
                "detail": r.detail,
                "fix_hint": r.fix_hint,
                "elapsed_ms": round(r.elapsed_ms, 1),
            }
            for r in self._results
        ]

    # ── Python environment checks ──

    def _check_python_version(self) -> CheckResult:
        start = time.monotonic()
        vi = sys.version_info
        version_str = f"{vi.major}.{vi.minor}.{vi.micro}"
        elapsed = (time.monotonic() - start) * 1000
        if vi >= (3, 11):
            return CheckResult(
                name="Python version", category="Python environment",
                status="pass", message=f"Python {version_str}",
                elapsed_ms=elapsed,
            )
        return CheckResult(
            name="Python version", category="Python environment",
            status="fail", message=f"Python {version_str} (need >= 3.11)",
            fix_hint="conda install python=3.11", elapsed_ms=elapsed,
        )

    def _check_conda_env(self) -> CheckResult:
        start = time.monotonic()
        conda_env = os.environ.get("CONDA_DEFAULT_ENV", "")
        elapsed = (time.monotonic() - start) * 1000
        if conda_env == "promptbim":
            return CheckResult(
                name="Conda env", category="Python environment",
                status="pass", message="conda env: promptbim",
                elapsed_ms=elapsed,
            )
        if conda_env:
            return CheckResult(
                name="Conda env", category="Python environment",
                status="warn", message=f"conda env: {conda_env} (expected: promptbim)",
                fix_hint="conda activate promptbim", elapsed_ms=elapsed,
            )
        return CheckResult(
            name="Conda env", category="Python environment",
            status="warn", message="No conda env active",
            fix_hint="conda activate promptbim", elapsed_ms=elapsed,
        )

    # ── Core dependency checks ──

    def _check_import(self, import_fn, name: str, category: str = "Core dependencies",
                      fix_hint: str | None = None) -> CheckResult:
        """Helper to check an import and return a CheckResult."""
        start = time.monotonic()
        try:
            version_info = import_fn()
            elapsed = (time.monotonic() - start) * 1000
            return CheckResult(
                name=name, category=category,
                status="pass", message=version_info,
                elapsed_ms=elapsed,
            )
        except ImportError as e:
            elapsed = (time.monotonic() - start) * 1000
            return CheckResult(
                name=name, category=category,
                status="fail", message=f"Not installed",
                detail=str(e), fix_hint=fix_hint,
                elapsed_ms=elapsed,
            )
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return CheckResult(
                name=name, category=category,
                status="fail", message=f"Error: {e}",
                detail=str(e), elapsed_ms=elapsed,
            )

    def _check_ifcopenshell(self) -> CheckResult:
        def _import():
            import ifcopenshell
            return f"ifcopenshell {ifcopenshell.version}"
        return self._check_import(
            _import, "ifcopenshell",
            fix_hint="conda install -c conda-forge ifcopenshell",
        )

    def _check_pxr(self) -> CheckResult:
        def _import():
            from pxr import Usd
            stage = Usd.Stage.CreateInMemory()
            stage = None  # noqa: F841
            return "pxr (OpenUSD): OK"
        return self._check_import(
            _import, "pxr (OpenUSD)",
            fix_hint="pip install usd-core",
        )

    def _check_pyside6(self) -> CheckResult:
        def _import():
            from PySide6.QtWidgets import QApplication
            from PySide6 import __version__
            return f"PySide6 {__version__}"
        return self._check_import(
            _import, "PySide6",
            fix_hint="pip install PySide6",
        )

    def _check_anthropic(self) -> CheckResult:
        def _import():
            import anthropic
            return f"anthropic {anthropic.__version__}"
        return self._check_import(
            _import, "anthropic SDK",
            fix_hint="pip install anthropic",
        )

    def _check_shapely_pyproj(self) -> CheckResult:
        def _import():
            import shapely
            import pyproj
            return f"shapely {shapely.__version__} + pyproj {pyproj.__version__}"
        return self._check_import(
            _import, "shapely + pyproj",
            fix_hint="pip install shapely pyproj",
        )

    def _check_pyvista(self) -> CheckResult:
        def _import():
            import pyvista
            import pyvistaqt  # noqa: F401
            return f"pyvista {pyvista.__version__} + pyvistaqt"
        return self._check_import(
            _import, "pyvista + pyvistaqt",
            fix_hint="pip install pyvista pyvistaqt",
        )

    # ── AI service checks ──

    def _check_api_key(self) -> CheckResult:
        from promptbim.startup.ai_check import check_api_key
        return check_api_key(self._settings)

    def _check_claude_ping(self) -> CheckResult:
        # Skip if API key check failed
        key_results = [r for r in self._results if r.name == "API Key"]
        if key_results and key_results[0].status == "fail":
            return CheckResult(
                name="Claude API ping", category="AI services",
                status="skip", message="Skipped (API key not available)",
                elapsed_ms=0.0,
            )
        if self._settings.startup_check_skip_ai:
            return CheckResult(
                name="Claude API ping", category="AI services",
                status="skip", message="Skipped (offline mode)",
                elapsed_ms=0.0,
            )
        from promptbim.startup.ai_check import ping_claude
        return ping_claude(self._settings)

    def _check_model_available(self) -> CheckResult:
        # Skip if ping failed/skipped
        ping_results = [r for r in self._results if r.name == "Claude API ping"]
        if ping_results and ping_results[0].status != "pass":
            return CheckResult(
                name="Model available", category="AI services",
                status="skip", message="Skipped (API not available)",
                elapsed_ms=0.0,
            )
        from promptbim.startup.ai_check import check_model_available
        return check_model_available(self._settings)

    # ── Filesystem checks ──

    def _check_filesystem(self) -> CheckResult:
        start = time.monotonic()
        issues = []
        env_ok = os.path.isfile(".env")
        if not env_ok:
            issues.append(".env missing")

        output_dir = self._settings.output_dir
        try:
            os.makedirs(output_dir, exist_ok=True)
            test_file = output_dir / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            output_ok = True
        except (OSError, PermissionError) as e:
            output_ok = False
            issues.append(f"output/ not writable: {e}")

        elapsed = (time.monotonic() - start) * 1000

        if not issues:
            return CheckResult(
                name="Filesystem", category="Filesystem",
                status="pass", message=".env exists, output/ writable",
                elapsed_ms=elapsed,
            )

        fix_hints = []
        if not env_ok:
            fix_hints.append("cp .env.example .env && edit .env")
        if not output_ok:
            fix_hints.append("mkdir -p output && chmod 755 output")

        return CheckResult(
            name="Filesystem", category="Filesystem",
            status="fail" if not output_ok else "warn",
            message="; ".join(issues),
            fix_hint=" | ".join(fix_hints),
            elapsed_ms=elapsed,
        )
