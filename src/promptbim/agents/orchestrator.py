"""Pipeline Orchestrator — chains Enhancer → Planner → Builder → Checker.

Supports iterative correction: if the Checker finds violations, the
Planner is re-invoked with the fix suggestions (up to ``max_iterations``).
"""

from __future__ import annotations

import time
import typing
from dataclasses import dataclass
from pathlib import Path

from promptbim.debug import get_logger

if typing.TYPE_CHECKING:
    from promptbim.agents.builder import BuildResult
    from promptbim.agents.checker import CheckResult
    from promptbim.schemas.land import LandParcel
    from promptbim.schemas.modification import ModificationRecord
    from promptbim.schemas.plan import BuildingPlan
    from promptbim.schemas.requirement import BuildingRequirement
    from promptbim.schemas.result import GenerationResult
    from promptbim.schemas.zoning import ZoningRules

logger = get_logger("agents.orchestrator")


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
        on_status: "typing.Callable[[PipelineStatus], None] | None" = None,
        *,
        enhancer: "EnhancerAgent | None" = None,
        planner: "PlannerAgent | None" = None,
        builder: "BuilderAgent | None" = None,
        checker: "CheckerAgent | None" = None,
        modifier: "ModifierAgent | None" = None,
    ) -> None:
        from promptbim.agents.builder import BuilderAgent
        from promptbim.agents.checker import CheckerAgent
        from promptbim.agents.enhancer import EnhancerAgent
        from promptbim.agents.modifier import ModifierAgent
        from promptbim.agents.planner import PlannerAgent

        self._enhancer = enhancer or EnhancerAgent()
        self._planner = planner or PlannerAgent()
        self._builder = builder or BuilderAgent(output_dir=output_dir)
        self._checker = checker or CheckerAgent()
        self._modifier = modifier or ModifierAgent()
        self._max_iterations = max_iterations
        self._on_status = on_status
        self._output_dir = Path(output_dir) if output_dir else None

        # Intermediate results (private, exposed via @property)
        self._requirement: BuildingRequirement | None = None
        self._plan: BuildingPlan | None = None
        self._build_result: BuildResult | None = None
        self._check_result: CheckResult | None = None
        # D1-S1: Cost + Schedule + 4D integration
        self._cost_estimate: "CostEstimate | None" = None
        self._schedule: "ConstructionSchedule | None" = None

    @property
    def requirement(self) -> "BuildingRequirement | None":
        return self._requirement

    @property
    def plan(self) -> "BuildingPlan | None":
        return self._plan

    @property
    def build_result(self) -> "BuildResult | None":
        return self._build_result

    @property
    def check_result(self) -> "CheckResult | None":
        return self._check_result

    # --- DRY shared helpers (QA-06) ---

    def _prepare_pipeline(
        self, prompt: str, land: "LandParcel", zoning: "ZoningRules | None", use_cache: bool
    ) -> "tuple[ZoningRules, str | None, GenerationResult | None]":
        """Shared cache lookup + setback prep for generate/agenerate.

        Returns (zoning, cache_key, cached_result_or_None).
        """
        from promptbim.schemas.result import GenerationResult
        from promptbim.schemas.zoning import ZoningRules as ZR

        if zoning is None:
            zoning = ZR()

        cache_key = None
        if use_cache:
            try:
                from promptbim.cache.cache_key import compute_cache_key
                from promptbim.cache.store import CacheStore

                store = CacheStore()
                cache_key = compute_cache_key(prompt, land, zoning)
                cached = store.get(cache_key)
                if cached is not None:
                    self._emit("cache", "Cache hit — loading previous result", 1.0)
                    logger.info("Cache hit for key %s", cache_key[:12])
                    return zoning, cache_key, GenerationResult(**cached)
            except Exception:
                logger.debug("Cache lookup failed, proceeding with generation", exc_info=True)

        return zoning, cache_key, None

    def _build_result_obj(self, pipeline_start: float) -> "GenerationResult":
        """Build a GenerationResult from current intermediate state."""
        from promptbim.bim.geometry import poly_area
        from promptbim.schemas.result import GenerationResult

        elapsed = time.time() - pipeline_start
        logger.debug("Pipeline complete: %.2fs total", elapsed)
        self._emit("builder", "Done!", 1.0)

        warnings = [
            f"[{v.severity}] {v.rule}: {v.message}"
            for v in (self._check_result.violations if self._check_result else [])
        ]
        compliance_report = self._check_result.compliance_summary if self._check_result else {}
        compliance_text = self._check_result.report_text if self._check_result else ""

        return GenerationResult(
            success=self._build_result.ok,
            building_name=self._plan.name,
            ifc_path=self._build_result.ifc_path,
            usd_path=self._build_result.usd_path,
            summary={
                "stories": len(self._plan.stories),
                "bcr": self._plan.building_bcr,
                "far": self._plan.building_far,
                "footprint_area": poly_area(self._plan.building_footprint),
            },
            compliance_report=compliance_report,
            compliance_text=compliance_text,
            errors=self._build_result.errors,
            warnings=warnings,
        )

    def _store_cache(self, cache_key: str | None, result: "GenerationResult") -> None:
        """Store result in cache if applicable."""
        if cache_key and result.success:
            try:
                from promptbim.cache.store import CacheStore

                store = CacheStore()
                store.put(cache_key, result.model_dump(mode="json", exclude={"ifc_path", "usd_path"}))
                logger.info("Cached result for key %s", cache_key[:12])
            except Exception:
                logger.debug("Cache store failed", exc_info=True)

    # --- Main pipeline ---

    def generate(
        self,
        prompt: str,
        land: "LandParcel",
        zoning: "ZoningRules | None" = None,
        use_cache: bool = True,
    ) -> "GenerationResult":
        """Run the full pipeline: Enhance → Plan → Build → Check.

        Returns a :class:`GenerationResult`.
        """
        from promptbim.land.setback import compute_setback
        from promptbim.schemas.result import GenerationResult

        zoning, cache_key, cached = self._prepare_pipeline(prompt, land, zoning, use_cache)
        if cached is not None:
            return cached

        _pipeline_start = time.time()
        buildable_area = compute_setback(land, zoning)

        # --- Stage 1: Enhance ---
        self._emit("enhancer", "Enhancing requirements...", 0.1)
        self._requirement = self._enhancer.enhance(prompt, land, zoning)
        logger.info(
            "Requirement: type=%s, stories=%d",
            self._requirement.building_type,
            self._requirement.num_stories,
        )

        # --- Stage 2+3+4: Plan → Build → Check (iterative) ---
        for iteration in range(self._max_iterations + 1):
            progress_base = 0.2 + iteration * 0.2

            self._emit(
                "planner", f"Planning building (iteration {iteration + 1})...", progress_base
            )
            self._plan = self._planner.plan(self._requirement, land, zoning, buildable_area)
            logger.info(
                "Plan: %s, %d stories, BCR=%.2f, FAR=%.2f",
                self._plan.name,
                len(self._plan.stories),
                self._plan.building_bcr,
                self._plan.building_far,
            )

            self._emit("checker", "Checking compliance...", progress_base + 0.1)
            self._check_result = self._checker.check(self._plan, land, zoning)

            if self._check_result.passed:
                logger.info("Plan passed all checks")
                break

            if iteration < self._max_iterations:
                logger.warning(
                    "Plan has %d violations, retrying...",
                    len(self._check_result.violations),
                )
                fix_text = "; ".join(self._check_result.suggestions)
                constraint = f"Fix: {fix_text}"
                if constraint not in self._requirement.constraints:
                    self._requirement.constraints.append(constraint)
            else:
                logger.warning("Max iterations reached, proceeding with current plan")

        # --- Build ---
        self._emit("builder", "Generating IFC + USD files...", 0.8)
        try:
            self._build_result = self._builder.build(self._plan)
        except Exception as e:
            logger.error("Builder failed: %s", e)
            if self._output_dir:
                try:
                    plan_json = self._output_dir / "plan_partial.json"
                    plan_json.write_text(self._plan.model_dump_json(indent=2))
                    logger.info("Saved partial plan to %s", plan_json)
                except Exception:
                    pass
            return GenerationResult(
                success=False,
                building_name=self._plan.name if self._plan else "",
                errors=[str(e)],
            )

        result = self._build_result_obj(_pipeline_start)
        self._store_cache(cache_key, result)
        # D1-S1: auto-compute cost + schedule after generation
        self._emit("cost", "Computing cost estimate...", 0.92)
        self.compute_cost()
        self._emit("schedule", "Generating 4D schedule...", 0.96)
        self.compute_schedule()
        return result

    async def agenerate(
        self,
        prompt: str,
        land: "LandParcel",
        zoning: "ZoningRules | None" = None,
        use_cache: bool = True,
    ) -> "GenerationResult":
        """Async version of :meth:`generate`.

        Pipeline: await enhancer.aenhance() → await planner.aplan() →
        builder.build() (sync — pure Python) → await checker.acheck()
        """
        import asyncio

        from promptbim.land.setback import compute_setback
        from promptbim.schemas.result import GenerationResult

        zoning, cache_key, cached = self._prepare_pipeline(prompt, land, zoning, use_cache)
        if cached is not None:
            return cached

        _pipeline_start = time.time()
        buildable_area = compute_setback(land, zoning)

        # Stage 1: Enhance (async)
        self._emit("enhancer", "Enhancing requirements...", 0.1)
        self._requirement = await self._enhancer.aenhance(prompt, land, zoning)

        # Stage 2+3+4: Plan → Check (iterative, async)
        for iteration in range(self._max_iterations + 1):
            progress_base = 0.2 + iteration * 0.2

            self._emit("planner", f"Planning (iteration {iteration + 1})...", progress_base)
            self._plan = await self._planner.aplan(self._requirement, land, zoning, buildable_area)

            self._emit("checker", "Checking compliance...", progress_base + 0.1)
            self._check_result = await self._checker.acheck(self._plan, land, zoning)

            if self._check_result.passed:
                break
            if iteration < self._max_iterations:
                fix_text = "; ".join(self._check_result.suggestions)
                constraint = f"Fix: {fix_text}"
                if constraint not in self._requirement.constraints:
                    self._requirement.constraints.append(constraint)

        # Build (offloaded to thread to avoid blocking the event loop)
        self._emit("builder", "Generating IFC + USD files...", 0.8)
        try:
            self._build_result = await asyncio.to_thread(self._builder.build, self._plan)
        except Exception as e:
            logger.error("Builder failed: %s", e)
            return GenerationResult(
                success=False,
                building_name=self._plan.name if self._plan else "",
                errors=[str(e)],
            )

        result = self._build_result_obj(_pipeline_start)
        self._store_cache(cache_key, result)
        # D1-S1: auto-compute cost + schedule after async generation
        self.compute_cost()
        self.compute_schedule()
        return result

    def modify(
        self,
        command: str,
        zoning: "ZoningRules | None" = None,
    ) -> "tuple[BuildingPlan | None, ModificationRecord | None]":
        """Apply a modification to the current plan.

        Returns (new_plan, record) or (None, None) if no plan exists.
        """
        if self._plan is None:
            logger.warning("Cannot modify — no plan exists")
            return None, None

        self._emit("modifier", f"Analyzing: {command}", 0.1)
        try:
            new_plan, record = self._modifier.modify(command, self._plan, zoning)
        except Exception as e:
            logger.error("Modification failed unexpectedly: %s", e)
            return None, None

        if record.success:
            self._plan = new_plan
            self._emit("modifier", "Modification applied", 0.5)

            # Rebuild IFC/USD with the modified plan
            self._emit("builder", "Rebuilding IFC + USD...", 0.7)
            self._build_result = self._builder.build(new_plan)
            self._emit("builder", "Done!", 1.0)

            # Persist modification history (H-3)
            if self._output_dir:
                try:
                    history_path = self._output_dir / "modification_history.json"
                    self._modifier.history.save_history(history_path)
                    logger.debug("Saved modification history to %s", history_path)
                except Exception:
                    logger.warning("Failed to save modification history", exc_info=True)
        else:
            self._emit("modifier", f"Modification failed: {record.error}", 1.0)

        return new_plan, record

    def undo(self) -> "tuple[BuildingPlan | None, ModificationRecord | None]":
        """Undo the last modification.

        Returns (restored_plan, undone_record) or (None, None).
        """
        if self._plan is None:
            return None, None

        restored, record = self._modifier.undo(self._plan)
        if restored is not None:
            self._plan = restored
            self._emit("modifier", "Undo complete", 0.5)

            # Rebuild
            self._emit("builder", "Rebuilding IFC + USD...", 0.7)
            self._build_result = self._builder.build(restored)
            self._emit("builder", "Done!", 1.0)

        return restored, record

    @property
    def modification_history(self):
        return self._modifier.history

    @property
    def cost_estimate(self) -> "CostEstimate | None":
        """Latest cost estimate (populated after generate/modify)."""
        return self._cost_estimate

    @property
    def schedule(self) -> "ConstructionSchedule | None":
        """Latest construction schedule (populated after generate/modify)."""
        return self._schedule

    # ------------------------------------------------------------------ #
    # D1-S1: Cost + Schedule + 4D helpers
    # ------------------------------------------------------------------ #

    def compute_cost(self, monitor_plan=None) -> "CostEstimate | None":
        """Run cost estimation on the current plan and cache result.

        D1-S1: exposes cost as a first-class Orchestrator concern.
        """
        if self._plan is None:
            return None
        try:
            from promptbim.bim.cost.estimator import CostEstimator
            self._cost_estimate = CostEstimator().estimate(self._plan, monitor_plan)
            logger.info(
                "Cost estimate: %.0f TWD (%.0f TWD/m²)",
                self._cost_estimate.total_cost_twd,
                self._cost_estimate.cost_per_sqm_twd,
            )
        except Exception:
            logger.warning("Cost estimation failed", exc_info=True)
        return self._cost_estimate

    def compute_schedule(self, total_days: int = 360) -> "ConstructionSchedule | None":
        """Generate construction schedule for the current plan.

        D1-S1: exposes 4D schedule as a first-class Orchestrator concern.
        """
        if self._plan is None:
            return None
        try:
            from promptbim.bim.simulation.scheduler import generate_schedule
            component_labels = []
            for story in self._plan.stories:
                for i, wall in enumerate(story.walls):
                    component_labels.append(f"{story.name}_wall_{i}")
                for i, _ in enumerate(story.spaces):
                    component_labels.append(f"{story.name}_slab_{i}")
            self._schedule = generate_schedule(
                component_labels,
                total_days=total_days,
                num_stories=len(self._plan.stories),
            )
            logger.info("Schedule: %d phases, %d days", len(self._schedule.phases), self._schedule.total_days)
        except Exception:
            logger.warning("Schedule generation failed", exc_info=True)
        return self._schedule

    def export_4d_gif(self, output_path: "str | Path | None" = None, fps: int = 5) -> "Path | None":
        """Render 4D construction animation as GIF.

        D1-S1: bridges Orchestrator → 4D Animator.
        Requires QT_QPA_PLATFORM=offscreen or display.
        """
        if self._plan is None or self._schedule is None:
            logger.warning("export_4d_gif: plan or schedule not ready")
            return None
        try:
            import os
            from pathlib import Path as _Path
            from promptbim.bim.simulation.animator import ConstructionAnimator

            if output_path is None:
                base = self._output_dir or _Path(".")
                output_path = base / "construction_4d.gif"
            output_path = _Path(output_path)
            anim = ConstructionAnimator(self._plan, self._schedule)
            anim.export_gif(str(output_path), fps=fps)
            logger.info("4D GIF exported to %s", output_path)
            return output_path
        except Exception:
            logger.warning("4D GIF export failed", exc_info=True)
            return None

    def _emit(self, stage: str, message: str, progress: float) -> None:
        logger.info("[%s] %s (%.0f%%)", stage, message, progress * 100)
        if self._on_status:
            self._on_status(PipelineStatus(stage=stage, message=message, progress=progress))


def _poly_area(coords):
    """Backward compat alias — delegates to bim.geometry.poly_area."""
    from promptbim.bim.geometry import poly_area

    return poly_area(coords)
