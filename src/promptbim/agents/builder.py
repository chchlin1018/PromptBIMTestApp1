"""Agent 3: BIM Builder.

Converts a :class:`BuildingPlan` into IFC + USD files.
This agent is **pure Python** — no LLM calls.
"""

from __future__ import annotations

from pathlib import Path

from promptbim.bim.ifc_generator import IFCGenerator
from promptbim.bim.usd_generator import USDGenerator
from promptbim.config import get_settings
from promptbim.debug import get_logger
from promptbim.schemas.plan import BuildingPlan

logger = get_logger("agents.builder")


class BuilderAgent:
    """Agent 3 — deterministic BIM generator (no LLM).

    Takes a :class:`BuildingPlan` and produces ``.ifc`` + ``.usda`` files.
    """

    def __init__(self, output_dir: str | Path | None = None) -> None:
        self._output_dir = Path(output_dir) if output_dir else get_settings().output_dir

    def build(self, plan: BuildingPlan) -> BuildResult:
        """Generate IFC + USD files from *plan*.

        Returns a :class:`BuildResult` with paths and status.
        """
        self._output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = _safe_filename(plan.name)
        logger.debug("Building IFC+USD: name=%s, output=%s", safe_name, self._output_dir)

        ifc_path = self._output_dir / f"{safe_name}.ifc"
        usd_path = self._output_dir / f"{safe_name}.usda"

        # Backup existing files before overwriting (M-3)
        _backup_if_exists(ifc_path)
        _backup_if_exists(usd_path)

        errors: list[str] = []

        # Generate IFC
        try:
            ifc_gen = IFCGenerator()
            ifc_gen.generate(plan, ifc_path)
            logger.info("IFC generated: %s", ifc_path)
        except Exception as exc:
            logger.exception("IFC generation failed")
            errors.append(f"IFC: {exc}")
            ifc_path = None

        # Generate USD
        try:
            usd_gen = USDGenerator()
            usd_gen.generate(plan, usd_path)
            logger.info("USD generated: %s", usd_path)
        except Exception as exc:
            logger.exception("USD generation failed")
            errors.append(f"USD: {exc}")
            usd_path = None

        result = BuildResult(ifc_path=ifc_path, usd_path=usd_path, errors=errors)
        if result.ok:
            sizes = []
            if ifc_path:
                sizes.append(f"IFC={ifc_path.stat().st_size / 1024:.0f}KB")
            if usd_path:
                sizes.append(f"USD={usd_path.stat().st_size / 1024:.0f}KB")
            logger.debug("Build complete: %s", ", ".join(sizes))
        else:
            logger.debug("Build failed: %s", errors)
        return result


class BuildResult:
    """Result of a Builder agent run."""

    def __init__(
        self,
        ifc_path: Path | None = None,
        usd_path: Path | None = None,
        errors: list[str] | None = None,
    ) -> None:
        self.ifc_path = ifc_path
        self.usd_path = usd_path
        self.errors = errors or []

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0 and (self.ifc_path is not None or self.usd_path is not None)


def _backup_if_exists(path: Path) -> None:
    """Rename an existing file to .bak (keeping only 1 backup)."""
    if path.exists():
        bak = path.with_suffix(path.suffix + ".bak")
        try:
            if bak.exists():
                bak.unlink()
            path.rename(bak)
            logger.debug("Backed up %s → %s", path.name, bak.name)
        except OSError:
            logger.warning("Failed to backup %s", path, exc_info=True)


def _safe_filename(name: str) -> str:
    """Convert a building name to a safe filename."""
    import re

    safe = re.sub(r"[^\w\s-]", "", name)
    safe = re.sub(r"\s+", "_", safe).strip("_")
    return safe[:80] or "building"
