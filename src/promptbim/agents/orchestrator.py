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
        on_status: "callable | None" = None,
    ) -> None:
        from promptbim.agents.builder import BuilderAgent
        from promptbim.agents.checker import CheckerAgent
        from promptbim.agents.enhancer import EnhancerAgent
        from promptbim.agents.modifier import ModifierAgent
        from promptbim.agents.planner import PlannerAgent

        self._enhancer = EnhancerAgent()
        self._planner = PlannerAgent()
        self._builder = BuilderAgent(output_dir=output_dir)
        self._checker = CheckerAgent()
        self._modifier = ModifierAgent()
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
        land: "LandParcel",
        zoning: "ZoningRules | None" = None,
        use_cache: bool = True,
    ) -> "GenerationResult":
        """Run the full pipeline: Enhance → Plan → Build → Check.

        Returns a :class:`GenerationResult`.
        """
        from promptbim.land.setback import compute_setback
        from promptbim.schemas.result import GenerationResult
        from promptbim.schemas.zoning import ZoningRules

        if zoning is None:
            zoning = ZoningRules()

        # Cache lookup
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
                    return GenerationResult(**cached)
            except Exception:
                logger.debug("Cache lookup failed, proceeding with generation", exc_info=True)

        _pipeline_start = time.time()
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
            self._emit(
                "planner", f"Planning building (iteration {iteration + 1})...", progress_base
            )
            self.plan = self._planner.plan(self.requirement, land, zoning, buildable_area)
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
        output_dir = self._builder._output_dir if hasattr(self._builder, "_output_dir") else None
        try:
            self.build_result = self._builder.build(self.plan)
        except Exception as e:
            from promptbim.schemas.result import GenerationResult

            logger.error("Builder failed: %s", e)
            # Save partial result (plan JSON) for debugging
            if output_dir:
                try:
                    plan_json = Path(output_dir) / "plan_partial.json"
                    plan_json.write_text(self.plan.model_dump_json(indent=2))
                    logger.info("Saved partial plan to %s", plan_json)
                except Exception:
                    pass
            return GenerationResult(
                success=False,
                building_name=self.plan.name if self.plan else "",
                errors=[str(e)],
            )

        # --- Result ---
        from promptbim.bim.geometry import poly_area
        from promptbim.schemas.result import GenerationResult

        _pipeline_elapsed = time.time() - _pipeline_start
        logger.debug("Pipeline complete: %.2fs total", _pipeline_elapsed)
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

        result = GenerationResult(
            success=self.build_result.ok,
            building_name=self.plan.name,
            ifc_path=self.build_result.ifc_path,
            usd_path=self.build_result.usd_path,
            summary={
                "stories": len(self.plan.stories),
                "bcr": self.plan.building_bcr,
                "far": self.plan.building_far,
                "footprint_area": poly_area(self.plan.building_footprint),
            },
            compliance_report=compliance_report,
            compliance_text=compliance_text,
            errors=self.build_result.errors,
            warnings=warnings,
        )

        # Store in cache
        if cache_key and result.success:
            try:
                from promptbim.cache.store import CacheStore

                store = CacheStore()
                store.put(cache_key, result.model_dump(mode="json", exclude={"ifc_path", "usd_path"}))
                logger.info("Cached result for key %s", cache_key[:12])
            except Exception:
                logger.debug("Cache store failed", exc_info=True)

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
        from promptbim.land.setback import compute_setback
        from promptbim.schemas.result import GenerationResult
        from promptbim.schemas.zoning import ZoningRules

        if zoning is None:
            zoning = ZoningRules()

        # Cache lookup
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
                    return GenerationResult(**cached)
            except Exception:
                logger.debug("Async cache lookup failed", exc_info=True)

        _pipeline_start = time.time()
        buildable_area = compute_setback(land, zoning)

        # Stage 1: Enhance (async)
        self._emit("enhancer", "Enhancing requirements...", 0.1)
        self.requirement = await self._enhancer.aenhance(prompt, land, zoning)

        # Stage 2+3+4: Plan → Check (iterative, async)
        for iteration in range(self._max_iterations + 1):
            progress_base = 0.2 + iteration * 0.2

            self._emit("planner", f"Planning (iteration {iteration + 1})...", progress_base)
            self.plan = await self._planner.aplan(self.requirement, land, zoning, buildable_area)

            self._emit("checker", "Checking compliance...", progress_base + 0.1)
            self.check_result = await self._checker.acheck(self.plan, land, zoning)

            if self.check_result.passed:
                break
            if iteration < self._max_iterations:
                fix_text = "; ".join(self.check_result.suggestions)
                self.requirement.constraints.append(f"Fix: {fix_text}")

        # Build (sync — pure Python, no API)
        self._emit("builder", "Generating IFC + USD files...", 0.8)
        try:
            self.build_result = self._builder.build(self.plan)
        except Exception as e:
            logger.error("Builder failed: %s", e)
            return GenerationResult(success=False, building_name=self.plan.name if self.plan else "", errors=[str(e)])

        # Result
        from promptbim.bim.geometry import poly_area

        _pipeline_elapsed = time.time() - _pipeline_start
        logger.debug("Async pipeline complete: %.2fs total", _pipeline_elapsed)
        self._emit("builder", "Done!", 1.0)

        warnings = [
            f"[{v.severity}] {v.rule}: {v.message}"
            for v in (self.check_result.violations if self.check_result else [])
        ]
        compliance_report = self.check_result.compliance_summary if self.check_result else {}
        compliance_text = self.check_result.report_text if self.check_result else ""

        result = GenerationResult(
            success=self.build_result.ok,
            building_name=self.plan.name,
            ifc_path=self.build_result.ifc_path,
            usd_path=self.build_result.usd_path,
            summary={
                "stories": len(self.plan.stories),
                "bcr": self.plan.building_bcr,
                "far": self.plan.building_far,
                "footprint_area": poly_area(self.plan.building_footprint),
            },
            compliance_report=compliance_report,
            compliance_text=compliance_text,
            errors=self.build_result.errors,
            warnings=warnings,
        )

        if cache_key and result.success:
            try:
                from promptbim.cache.store import CacheStore

                store = CacheStore()
                store.put(cache_key, result.model_dump(mode="json", exclude={"ifc_path", "usd_path"}))
            except Exception:
                logger.debug("Async cache store failed", exc_info=True)

        return result

    def modify(
        self,
        command: str,
        zoning: "ZoningRules | None" = None,
    ) -> tuple[BuildingPlan | None, ModificationRecord | None]:
        """Apply a modification to the current plan.

        Returns (new_plan, record) or (None, None) if no plan exists.
        """
        if self.plan is None:
            logger.warning("Cannot modify — no plan exists")
            return None, None

        self._emit("modifier", f"Analyzing: {command}", 0.1)
        try:
            new_plan, record = self._modifier.modify(command, self.plan, zoning)
        except Exception as e:
            logger.error("Modification failed unexpectedly: %s", e)
            return None, None

        if record.success:
            self.plan = new_plan
            self._emit("modifier", "Modification applied", 0.5)

            # Rebuild IFC/USD with the modified plan
            self._emit("builder", "Rebuilding IFC + USD...", 0.7)
            self.build_result = self._builder.build(new_plan)
            self._emit("builder", "Done!", 1.0)

            # Persist modification history (H-3)
            try:
                history_path = self._output_dir / "modification_history.json"
                self._modifier.history.save_history(history_path)
                logger.debug("Saved modification history to %s", history_path)
            except Exception:
                logger.warning("Failed to save modification history", exc_info=True)
        else:
            self._emit("modifier", f"Modification failed: {record.error}", 1.0)

        return new_plan, record

    def undo(self) -> tuple[BuildingPlan | None, ModificationRecord | None]:
        """Undo the last modification.

        Returns (restored_plan, undone_record) or (None, None).
        """
        if self.plan is None:
            return None, None

        restored, record = self._modifier.undo(self.plan)
        if restored is not None:
            self.plan = restored
            self._emit("modifier", "Undo complete", 0.5)

            # Rebuild
            self._emit("builder", "Rebuilding IFC + USD...", 0.7)
            self.build_result = self._builder.build(restored)
            self._emit("builder", "Done!", 1.0)

        return restored, record

    @property
    def modification_history(self):
        return self._modifier.history

    def _emit(self, stage: str, message: str, progress: float) -> None:
        logger.info("[%s] %s (%.0f%%)", stage, message, progress * 100)
        if self._on_status:
            self._on_status(PipelineStatus(stage=stage, message=message, progress=progress))


def _poly_area(coords):
    """Backward compat alias — delegates to bim.geometry.poly_area."""
    from promptbim.bim.geometry import poly_area

    return poly_area(coords)
