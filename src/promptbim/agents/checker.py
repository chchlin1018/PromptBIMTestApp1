"""Agent 4: Rule Checker.

Validates a :class:`BuildingPlan` against zoning rules and building codes,
using the Taiwan building code engine for deterministic checks and Claude
to suggest fixes when violations are found.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from promptbim.agents.base import BaseAgent
from promptbim.codes.base import CheckResult as CodeCheckResult
from promptbim.codes.base import Severity
from promptbim.codes.registry import get_compliance_summary, run_all_checks
from promptbim.codes.report import generate_report_table
from promptbim.debug import get_logger
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan
from promptbim.schemas.zoning import ZoningRules

logger = get_logger("agents.checker")


@dataclass
class CheckViolation:
    """A single rule violation."""

    rule: str
    message: str
    severity: str = "error"  # error / warning


@dataclass
class CheckResult:
    """Result of checking a BuildingPlan."""

    violations: list[CheckViolation] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    code_results: list[CodeCheckResult] = field(default_factory=list)
    compliance_summary: dict = field(default_factory=dict)
    report_text: str = ""

    @property
    def passed(self) -> bool:
        return not any(v.severity == "error" for v in self.violations)


CHECKER_SYSTEM_PROMPT = """\
You are a Taiwan building code compliance checker. Given a list of violations
found in a building plan (based on Taiwan Building Technical Regulations),
suggest specific fixes for each violation.

## INPUT
You receive a list of violations, each with:
- rule_id: the Taiwan building code rule ID
- law_reference: the specific law article
- message: what went wrong
- severity: fail or warning

## OUTPUT
Return a JSON object:
{
  "suggestions": [
    "Specific fix suggestion 1 (in Chinese preferred)",
    "Specific fix suggestion 2",
    ...
  ]
}

Be concise and actionable. Return ONLY the JSON.
"""


class CheckerAgent(BaseAgent):
    """Agent 4 — validates building plans against Taiwan building codes."""

    SYSTEM_PROMPT = CHECKER_SYSTEM_PROMPT

    def check(
        self,
        plan: BuildingPlan,
        land: LandParcel,
        zoning: ZoningRules,
    ) -> CheckResult:
        """Check *plan* against Taiwan building codes.

        Runs the full code engine deterministically, then asks Claude for
        fix suggestions if violations are found.
        """
        # Run Taiwan building code engine
        code_results = run_all_checks(plan, land, zoning)
        compliance = get_compliance_summary(code_results)
        report_text = generate_report_table(code_results)

        # Convert code engine fails/warnings to legacy CheckViolation format
        violations = self._code_results_to_violations(code_results)
        result = CheckResult(
            violations=violations,
            code_results=code_results,
            compliance_summary=compliance,
            report_text=report_text,
        )

        # Also run legacy checks for footprint containment
        legacy_violations = self._check_legacy_rules(plan, land, zoning)
        result.violations.extend(legacy_violations)

        if result.violations:
            suggestions = self._get_suggestions(result.violations, code_results)
            result.suggestions = suggestions

        for v in result.violations:
            logger.debug("Violation [%s] %s: %s", v.severity, v.rule, v.message)
        logger.debug(
            "Compliance: %d passed, %d warnings, %d failed (rate: %.1f%%)",
            compliance.get("passed", 0),
            compliance.get("warnings", 0),
            compliance.get("failed", 0),
            compliance.get("compliance_rate", 0),
        )

        return result

    async def acheck(
        self,
        plan: BuildingPlan,
        land: LandParcel,
        zoning: ZoningRules,
    ) -> CheckResult:
        """Async version of :meth:`check`. Code checks are sync; suggestions are async."""
        code_results = run_all_checks(plan, land, zoning)
        compliance = get_compliance_summary(code_results)
        report_text = generate_report_table(code_results)

        violations = self._code_results_to_violations(code_results)
        result = CheckResult(
            violations=violations,
            code_results=code_results,
            compliance_summary=compliance,
            report_text=report_text,
        )

        legacy_violations = self._check_legacy_rules(plan, land, zoning)
        result.violations.extend(legacy_violations)

        if result.violations:
            suggestions = await self._aget_suggestions(result.violations, code_results)
            result.suggestions = suggestions

        return result

    async def _aget_suggestions(self, violations, code_results) -> list[str]:
        """Async version of _get_suggestions."""
        violation_text = "\n".join(f"- [{v.severity}] {v.rule}: {v.message}" for v in violations)
        user_msg = (
            f"The following building code violations were found:\n{violation_text}\n\n"
            f"Provide concise fix suggestions (one per violation). Return a JSON array of strings."
        )
        response = await self.arun(user_msg)
        if response.ok and response.json_data:
            data = response.json_data
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "suggestions" in data:
                return data["suggestions"]
        return [f"Fix violation: {v.rule}" for v in violations]

    def _code_results_to_violations(
        self, code_results: list[CodeCheckResult]
    ) -> list[CheckViolation]:
        """Convert code engine results to CheckViolation list."""
        violations: list[CheckViolation] = []
        for cr in code_results:
            if cr.severity == Severity.FAIL:
                violations.append(
                    CheckViolation(
                        rule=cr.rule_id,
                        message=cr.message_zh,
                        severity="error",
                    )
                )
            elif cr.severity == Severity.WARNING:
                violations.append(
                    CheckViolation(
                        rule=cr.rule_id,
                        message=cr.message_zh,
                        severity="warning",
                    )
                )
        return violations

    def _check_legacy_rules(
        self,
        plan: BuildingPlan,
        land: LandParcel,
        zoning: ZoningRules,
    ) -> list[CheckViolation]:
        """Footprint containment check (not covered by code engine)."""
        violations: list[CheckViolation] = []
        if plan.building_footprint and plan.buildable_area:
            try:
                from shapely.geometry import Polygon

                fp = Polygon(plan.building_footprint)
                ba = Polygon(plan.buildable_area)
                if not ba.contains(fp):
                    if not ba.buffer(0.1).contains(fp):
                        violations.append(
                            CheckViolation(
                                rule="Setback",
                                message="Building footprint extends beyond buildable area (setback violation)",
                            )
                        )
            except Exception:
                logger.warning("Could not verify footprint containment")
        return violations

    def _get_suggestions(
        self,
        violations: list[CheckViolation],
        code_results: list[CodeCheckResult] | None = None,
    ) -> list[str]:
        """Ask Claude for fix suggestions (best-effort)."""
        # Build context from code results for richer suggestions
        violations_text = "\n".join(f"- [{v.severity}] {v.rule}: {v.message}" for v in violations)

        # Include suggestions from code engine
        code_suggestions = []
        if code_results:
            for cr in code_results:
                if cr.suggestion and cr.severity in (Severity.FAIL, Severity.WARNING):
                    code_suggestions.append(f"[{cr.rule_id}] {cr.suggestion}")

        try:
            prompt = f"Violations found:\n{violations_text}"
            if code_suggestions:
                prompt += "\n\nCode engine suggestions:\n" + "\n".join(
                    f"- {s}" for s in code_suggestions
                )
            response = self.run(prompt)
            if response.ok and response.json_data:
                return response.json_data.get("suggestions", [])
        except Exception:
            logger.warning("Could not get AI suggestions for violations")

        # Fallback: use code engine suggestions directly
        if code_suggestions:
            return code_suggestions

        # Legacy fallback
        suggestions = []
        for v in violations:
            if "BCR" in v.rule:
                suggestions.append("縮小建築投影面積")
            elif "FAR" in v.rule:
                suggestions.append("減少樓層數或縮小各層面積")
            elif "Height" in v.rule or "24-1" in v.rule:
                suggestions.append("減少樓層數或降低層高")
            elif v.rule == "Setback":
                suggestions.append("將建築平面移入可建築範圍內")
        return suggestions
