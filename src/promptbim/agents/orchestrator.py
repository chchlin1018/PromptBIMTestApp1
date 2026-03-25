"""Pipeline Orchestrator — chains Enhancer → Planner → Builder → Checker.

Supports iterative correction: if the Checker finds violations, the
Planner is re-invoked with the fix suggestions (up to ``max_iterations``).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from promptbim.agents.builder import BuilderAgent, BuildResult
from promptbim.agents.checker import CheckerAgent, CheckResult
from promptbim.agents.enhancer import EnhancerAgent
from promptbim.agents.planner import PlannerAgent
from promptbim.land.setback import compute_setback
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan
from promptbim.schemas.requirement import BuildingRequirement
from promptbim.schemas.result import GenerationResult
from promptbim.schemas.zoning import ZoningRules

logger = logging.getLogger(__name__)


@dataclass
class PipelineStatus:
    """Status callback data."""

    stage: str  # enhancer / planner / builder / checker
    message: str
    progress: float = 0.0  # 0.0 - 1.0


class Orchestrator:
    """Chains the four agents into a complete generation pipeline.

    Usage::

        orch = Orchestrator()
        result = orch.generate("3-story house with pool", land, zoning)
    """

    def __init__(
        self,
        output_dir: str | Path | None = None,
        max_iterations: int = 2,
        on_status: "callable | None" = None,
    ) -> None:
        self._enhancer = EnhancerAgent()
        self._planner = PlannerAgent()
        self._builder = BuilderAgent(output_dir=output_dir)
        self._checker = CheckerAgent()
        self._max_iterations = max_iterations
        self._on_status = on_status

        # Expose intermediate results
        self.requirement: BuildingRequirement | None = None
        self.plan: BuildingPlan | None = None
        self.build_result: BuildResult | None = None
        self.check_result: CheckResult | None = None

    def generate(
        self,
        prompt: str,
        land: LandParcel,
        zoning: ZoningRules | None = None,
    ) -> GenerationResult:
        """Run the full pipeline: Enhance → Plan → Build → Check.

        Returns a :class:`GenerationResult`.
        """
        if zoning is None:
            zoning = ZoningRules()

        buildable_area = compute_setback(land, zoning)

        # --- Stage 1: Enhance ---
        self._emit("enhancer", "Enhancing requirements...", 0.1)
        self.requirement = self._enhancer.enhance(prompt, land, zoning)
        logger.info(
            "Requirement: type=%s, stories=%d",
            self.requirement.building_type,
            self.requirement.num_stories,
        )

        # --- Stage 2+3+4: Plan → Build → Check (iterative) ---
        for iteration in range(self._max_iterations + 1):
            progress_base = 0.2 + iteration * 0.2

            # Plan
            self._emit("planner", f"Planning building (iteration {iteration + 1})...", progress_base)
            self.plan = self._planner.plan(
                self.requirement, land, zoning, buildable_area
            )
            logger.info(
                "Plan: %s, %d stories, BCR=%.2f, FAR=%.2f",
                self.plan.name,
                len(self.plan.stories),
                self.plan.building_bcr,
                self.plan.building_far,
            )

            # Check
            self._emit("checker", "Checking compliance...", progress_base + 0.1)
            self.check_result = self._checker.check(self.plan, land, zoning)

            if self.check_result.passed:
                logger.info("Plan passed all checks")
                break

            if iteration < self._max_iterations:
                # Feed suggestions back into the requirement for next iteration
                logger.warning(
                    "Plan has %d violations, retrying...",
                    len(self.check_result.violations),
                )
                fix_text = "; ".join(self.check_result.suggestions)
                self.requirement.constraints.append(f"Fix: {fix_text}")
            else:
                logger.warning("Max iterations reached, proceeding with current plan")

        # --- Build ---
        self._emit("builder", "Generating IFC + USD files...", 0.8)
        self.build_result = self._builder.build(self.plan)

        # --- Result ---
        self._emit("builder", "Done!", 1.0)
        warnings = [
            f"[{v.severity}] {v.rule}: {v.message}"
            for v in (self.check_result.violations if self.check_result else [])
        ]

        compliance_report = {}
        compliance_text = ""
        if self.check_result:
            compliance_report = self.check_result.compliance_summary
            compliance_text = self.check_result.report_text

        return GenerationResult(
            success=self.build_result.ok,
            building_name=self.plan.name,
            ifc_path=self.build_result.ifc_path,
            usd_path=self.build_result.usd_path,
            summary={
                "stories": len(self.plan.stories),
                "bcr": self.plan.building_bcr,
                "far": self.plan.building_far,
                "footprint_area": _poly_area(self.plan.building_footprint),
            },
            compliance_report=compliance_report,
            compliance_text=compliance_text,
            errors=self.build_result.errors,
            warnings=warnings,
        )

    def _emit(self, stage: str, message: str, progress: float) -> None:
        logger.info("[%s] %s (%.0f%%)", stage, message, progress * 100)
        if self._on_status:
            self._on_status(PipelineStatus(stage=stage, message=message, progress=progress))


def _poly_area(coords: list[tuple[float, float]]) -> float:
    """Shoelace formula for polygon area."""
    n = len(coords)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    return abs(area) / 2.0
