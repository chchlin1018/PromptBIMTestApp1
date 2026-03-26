"""Auto-fix suggestions and execution for failed health checks."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass

from promptbim.debug import get_logger
from promptbim.startup.health_check import CheckResult

logger = get_logger("startup.autofix")

# Fix command lookup by check name
FIX_COMMANDS: dict[str, list[str]] = {
    "Python version": ["conda", "install", "python=3.11", "-y"],
    "ifcopenshell": ["conda", "install", "-c", "conda-forge", "ifcopenshell", "-y"],
    "pxr (OpenUSD)": [sys.executable, "-m", "pip", "install", "usd-core"],
    "PySide6": [sys.executable, "-m", "pip", "install", "PySide6"],
    "anthropic SDK": [sys.executable, "-m", "pip", "install", "anthropic"],
    "shapely + pyproj": [sys.executable, "-m", "pip", "install", "shapely", "pyproj"],
    "pyvista + pyvistaqt": [sys.executable, "-m", "pip", "install", "pyvista", "pyvistaqt"],
}

# Human-readable fix hints for non-automatable issues
MANUAL_FIXES: dict[str, str] = {
    "API Key": "Set ANTHROPIC_API_KEY in .env (get key from console.anthropic.com)",
    "Claude API ping": "Check network connection or proxy settings",
    "Conda env": "Run: conda activate promptbim",
    "Filesystem": "Run: mkdir -p output && chmod 755 output",
}


@dataclass
class FixResult:
    """Result of an auto-fix attempt."""

    check_name: str
    success: bool
    command: str
    output: str


def get_fix_suggestion(result: CheckResult) -> str | None:
    """Get a fix suggestion string for a failed check."""
    if result.fix_hint:
        return result.fix_hint

    if result.name in FIX_COMMANDS:
        return f"Run: {' '.join(FIX_COMMANDS[result.name])}"

    return MANUAL_FIXES.get(result.name)


def can_auto_fix(result: CheckResult) -> bool:
    """Check if a failed result can be auto-fixed."""
    return result.name in FIX_COMMANDS and result.status == "fail"


def auto_fix(result: CheckResult) -> FixResult:
    """Attempt to auto-fix a failed check by running the fix command."""
    if not can_auto_fix(result):
        return FixResult(
            check_name=result.name,
            success=False,
            command="N/A",
            output=f"No auto-fix available for {result.name}",
        )

    cmd = FIX_COMMANDS[result.name]
    cmd_str = " ".join(cmd)
    logger.debug("Auto-fix: running %s", cmd_str)

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        success = proc.returncode == 0
        output = proc.stdout if success else proc.stderr
        logger.debug("Auto-fix %s: rc=%d", result.name, proc.returncode)
        return FixResult(
            check_name=result.name,
            success=success,
            command=cmd_str,
            output=output[:500],
        )
    except subprocess.TimeoutExpired:
        return FixResult(
            check_name=result.name,
            success=False,
            command=cmd_str,
            output="Command timed out (120s)",
        )
    except Exception as e:
        return FixResult(
            check_name=result.name,
            success=False,
            command=cmd_str,
            output=str(e),
        )


def auto_fix_all(results: list[CheckResult]) -> list[FixResult]:
    """Attempt to auto-fix all failed checks that support it."""
    fix_results = []
    for r in results:
        if can_auto_fix(r):
            fix_results.append(auto_fix(r))
    return fix_results


def generate_fix_report(results: list[CheckResult]) -> str:
    """Generate a human-readable fix report for all failed/warned checks."""
    lines = []
    for r in results:
        if r.status in ("fail", "warn"):
            suggestion = get_fix_suggestion(r)
            auto = " [auto-fixable]" if can_auto_fix(r) else ""
            lines.append(f"  {r.name}: {r.message}")
            if suggestion:
                lines.append(f"    -> {suggestion}{auto}")
    if not lines:
        return "All checks passed. No fixes needed."
    return "Fix suggestions:\n" + "\n".join(lines)
