"""Taiwan Industrial / Fab building code checks for Demo-1.

Covers semiconductor fab and data center specific requirements:
  - Cleanroom area ratio (無塵室面積比)
  - Sub-fab utility clearance
  - Emergency power backup (緊急電源)
  - Data center cooling redundancy (N+1)
"""

from __future__ import annotations

from promptbim.codes.base import BaseRule, CheckResult, Severity
from promptbim.debug import get_logger
from promptbim.schemas.plan import BuildingPlan

logger = get_logger("codes.tw_industrial")


def _story_area(s) -> float:
    return sum(sp.area_sqm for sp in s.spaces)


class CleanroomRatioRule(BaseRule):
    """Cleanroom GFA should be 25~65% of total fab GFA (TSMC guideline)."""

    rule_id = "TW-IND-001"
    name = "Cleanroom Area Ratio"

    def check(self, plan: BuildingPlan) -> CheckResult:
        fab_stories = [s for s in plan.stories if "fab" in s.name.lower() or "clean" in s.name.lower()]
        if not fab_stories:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name_zh="無塵室面積比",
                law_reference="TSMC Fab Design Guideline §3.1",
                severity=Severity.PASS,
                message_zh="無廠房/無塵室樓層 — 略過",
            )
        total_gfa = sum(_story_area(s) for s in plan.stories if s.elevation_m >= 0)
        clean_gfa = sum(_story_area(s) for s in fab_stories)
        if total_gfa == 0:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name_zh="無塵室面積比",
                law_reference="TSMC Fab Design Guideline §3.1",
                severity=Severity.PASS,
                message_zh="GFA=0，略過",
            )
        ratio = clean_gfa / total_gfa
        passed = 0.25 <= ratio <= 0.65
        return CheckResult(
            rule_id=self.rule_id,
            rule_name_zh="無塵室面積比",
            law_reference="TSMC Fab Design Guideline §3.1",
            severity=Severity.PASS if passed else Severity.WARNING,
            message_zh=f"無塵室面積比 {ratio:.1%}（目標 25~65%）",
            actual_value=ratio,
            limit_value=0.65,
        )


class SubFabClearanceRule(BaseRule):
    """Sub-fab level must have height ≥ 4m for utility routing."""

    rule_id = "TW-IND-002"
    name = "Sub-fab Clearance"

    def check(self, plan: BuildingPlan) -> CheckResult:
        subfab = next(
            (s for s in plan.stories if "sub" in s.name.lower() or "utility" in s.name.lower()),
            None,
        )
        if subfab is None:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name_zh="Sub-fab 淨高",
                law_reference="工廠設廠標準 §8",
                severity=Severity.PASS,
                message_zh="無 Sub-fab 樓層 — 略過",
            )
        passed = subfab.height_m >= 4.0
        return CheckResult(
            rule_id=self.rule_id,
            rule_name_zh="Sub-fab 淨高",
            law_reference="工廠設廠標準 §8",
            severity=Severity.PASS if passed else Severity.FAIL,
            message_zh=f"Sub-fab 淨高 {subfab.height_m:.1f}m（須 ≥ 4.0m）",
            actual_value=subfab.height_m,
            limit_value=4.0,
        )


class EmergencyPowerRule(BaseRule):
    """Industrial buildings > 5,000 m² require emergency power space."""

    rule_id = "TW-IND-003"
    name = "Emergency Power Requirement"

    def check(self, plan: BuildingPlan) -> CheckResult:
        total_gfa = sum(_story_area(s) for s in plan.stories if s.elevation_m >= 0)
        if total_gfa < 5000:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name_zh="緊急電源設備",
                law_reference="建築技術規則建築設備編 §98",
                severity=Severity.PASS,
                message_zh=f"GFA {total_gfa:.0f}m² < 5000m²，不需緊急電源",
            )
        has_power_space = any(
            "power" in s.name.lower() or "ups" in s.name.lower() or "mech" in s.name.lower()
            for s in plan.stories
        )
        return CheckResult(
            rule_id=self.rule_id,
            rule_name_zh="緊急電源設備",
            law_reference="建築技術規則建築設備編 §98",
            severity=Severity.PASS if has_power_space else Severity.FAIL,
            message_zh=(
                "已設緊急電源空間 ✅" if has_power_space
                else f"GFA {total_gfa:.0f}m²，未設緊急電源空間"
            ),
            actual_value=float(has_power_space),
            limit_value=1.0,
        )


class DataCenterCoolingRule(BaseRule):
    """Data center requires cooling floor (N+1 redundancy)."""

    rule_id = "TW-IND-004"
    name = "Data Center Cooling Redundancy"

    def check(self, plan: BuildingPlan) -> CheckResult:
        is_dc = any("data" in s.name.lower() or "server" in s.name.lower() for s in plan.stories)
        if not is_dc:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name_zh="資料中心冷卻備援",
                law_reference="TIA-942 §6.4",
                severity=Severity.PASS,
                message_zh="非資料中心建築 — 略過",
            )
        has_cooling = any(
            "cool" in s.name.lower() or "mech" in s.name.lower() for s in plan.stories
        )
        return CheckResult(
            rule_id=self.rule_id,
            rule_name_zh="資料中心冷卻備援",
            law_reference="TIA-942 §6.4",
            severity=Severity.PASS if has_cooling else Severity.WARNING,
            message_zh="已設冷卻樓層 ✅" if has_cooling else "資料中心未設專用冷卻樓層",
            actual_value=float(has_cooling),
            limit_value=1.0,
        )


INDUSTRIAL_RULES: list[BaseRule] = [
    CleanroomRatioRule(),
    SubFabClearanceRule(),
    EmergencyPowerRule(),
    DataCenterCoolingRule(),
]


def run_industrial_checks(plan: BuildingPlan) -> list[CheckResult]:
    """Run all industrial code checks on a BuildingPlan."""
    results = []
    for rule in INDUSTRIAL_RULES:
        try:
            results.append(rule.check(plan))
        except Exception as e:
            logger.warning("Rule %s failed: %s", rule.rule_id, e)
            results.append(CheckResult(
                rule_id=rule.rule_id,
                rule_name_zh=rule.name,
                law_reference="—",
                severity=Severity.FAIL,
                message_zh=f"規則執行錯誤: {e}",
            ))
    return results
