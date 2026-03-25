"""Agent 3: BIM Builder.

Converts a :class:`BuildingPlan` into IFC + USD files.
This agent is **pure Python** — no LLM calls.
"""

from __future__ import annotations

import logging
from pathlib import Path

from promptbim.bim.ifc_generator import IFCGenerator
from promptbim.bim.usd_generator import USDGenerator
from promptbim.config import get_settings
from promptbim.schemas.plan import BuildingPlan

logger = logging.getLogger(__name__)


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

        ifc_path = self._output_dir / f"{safe_name}.ifc"
        usd_path = self._output_dir / f"{safe_name}.usda"

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

        return BuildResult(
            ifc_path=ifc_path,
            usd_path=usd_path,
            errors=errors,
        )


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


def _safe_filename(name: str) -> str:
    """Convert a building name to a safe filename."""
    import re
    safe = re.sub(r"[^\w\s-]", "", name)
    safe = re.sub(r"\s+", "_", safe).strip("_")
    return safe[:80] or "building"
