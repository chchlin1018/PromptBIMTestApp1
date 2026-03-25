"""Agent 4: Rule Checker.

Validates a :class:`BuildingPlan` against zoning rules and building codes,
using Claude to suggest fixes when violations are found.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from promptbim.agents.base import BaseAgent
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan
from promptbim.schemas.zoning import ZoningRules

logger = logging.getLogger(__name__)


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

    @property
    def passed(self) -> bool:
        return not any(v.severity == "error" for v in self.violations)


CHECKER_SYSTEM_PROMPT = """\
You are a building code compliance checker. Given a list of violations
found in a building plan, suggest specific fixes for each violation.

## INPUT
You receive a list of violations, each with:
- rule: the rule name
- message: what went wrong
- severity: error or warning

## OUTPUT
Return a JSON object:
{
  "suggestions": [
    "Specific fix suggestion 1",
    "Specific fix suggestion 2",
    ...
  ]
}

Be concise and actionable. Return ONLY the JSON.
"""


class CheckerAgent(BaseAgent):
    """Agent 4 — validates building plans and suggests fixes."""

    SYSTEM_PROMPT = CHECKER_SYSTEM_PROMPT

    def check(
        self,
        plan: BuildingPlan,
        land: LandParcel,
        zoning: ZoningRules,
    ) -> CheckResult:
        """Check *plan* against zoning rules. Returns a :class:`CheckResult`.

        Deterministic checks run locally; Claude is only called when
        violations are found, to generate fix suggestions.
        """
        violations = self._check_rules(plan, land, zoning)
        result = CheckResult(violations=violations)

        if violations:
            suggestions = self._get_suggestions(violations)
            result.suggestions = suggestions

        return result

    def _check_rules(
        self,
        plan: BuildingPlan,
        land: LandParcel,
        zoning: ZoningRules,
    ) -> list[CheckViolation]:
        """Run deterministic rule checks."""
        violations: list[CheckViolation] = []

        # 1. BCR check
        if plan.building_bcr > zoning.bcr_limit:
            violations.append(
                CheckViolation(
                    rule="BCR",
                    message=(
                        f"Building coverage ratio {plan.building_bcr:.2%} "
                        f"exceeds limit {zoning.bcr_limit:.2%}"
                    ),
                )
            )

        # 2. FAR check
        if plan.building_far > zoning.far_limit:
            violations.append(
                CheckViolation(
                    rule="FAR",
                    message=(
                        f"Floor area ratio {plan.building_far:.2f} "
                        f"exceeds limit {zoning.far_limit:.2f}"
                    ),
                )
            )

        # 3. Height check
        if plan.stories:
            top = plan.stories[-1]
            total_height = top.elevation_m + top.height_m
            if total_height > zoning.height_limit_m:
                violations.append(
                    CheckViolation(
                        rule="Height",
                        message=(
                            f"Building height {total_height:.1f}m "
                            f"exceeds limit {zoning.height_limit_m:.1f}m"
                        ),
                    )
                )

        # 4. Footprint containment check
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

        # 5. Minimum story height
        for story in plan.stories:
            if story.height_m < 2.4:
                violations.append(
                    CheckViolation(
                        rule="MinHeight",
                        message=f"Story {story.name} height {story.height_m}m < 2.4m minimum",
                        severity="warning",
                    )
                )

        return violations

    def _get_suggestions(self, violations: list[CheckViolation]) -> list[str]:
        """Ask Claude for fix suggestions (best-effort)."""
        violations_text = "\n".join(
            f"- [{v.severity}] {v.rule}: {v.message}" for v in violations
        )

        try:
            response = self.run(f"Violations found:\n{violations_text}")
            if response.ok and response.json_data:
                return response.json_data.get("suggestions", [])
        except Exception:
            logger.warning("Could not get AI suggestions for violations")

        # Fallback: generate basic suggestions locally
        suggestions = []
        for v in violations:
            if v.rule == "BCR":
                suggestions.append("Reduce building footprint area")
            elif v.rule == "FAR":
                suggestions.append("Reduce number of stories or footprint area")
            elif v.rule == "Height":
                suggestions.append("Reduce number of stories or story height")
            elif v.rule == "Setback":
                suggestions.append("Move building footprint within buildable area")
        return suggestions
