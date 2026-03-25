"""Rule registry — registers all building code rules and runs batch checks."""

from __future__ import annotations

from promptbim.codes.base import BaseRule, CheckResult, Severity
from promptbim.codes.tw_building_code import (
    BCRRule,
    CeilingHeightRule,
    CorridorRule,
    ElevatorRule,
    FARRule,
    HeightLimitRule,
    ParkingRule,
    StairRule,
)
from promptbim.codes.tw_fire_code import (
    FireCompartmentRule,
    FireConstructionRule,
    FireEscapeRule,
    SafetyStairRule,
    TwoStairsRule,
)
from promptbim.codes.tw_seismic_code import SeismicDesignRule
from promptbim.codes.tw_accessibility_code import AccessibilityRule


# All rules in priority order
ALL_RULES: list[BaseRule] = [
    # Density / volume (highest priority)
    BCRRule(),
    FARRule(),
    HeightLimitRule(),
    # Evacuation safety
    StairRule(),
    CorridorRule(),
    FireConstructionRule(),
    FireCompartmentRule(),
    FireEscapeRule(),
    TwoStairsRule(),
    SafetyStairRule(),
    # Functional requirements
    CeilingHeightRule(),
    ElevatorRule(),
    ParkingRule(),
    # Structural safety
    SeismicDesignRule(),
    # Accessibility
    AccessibilityRule(),
]


def run_all_checks(plan, land, zoning) -> list[CheckResult]:
    """Run every registered rule against *plan*. Returns flat list of results."""
    results: list[CheckResult] = []
    for rule in ALL_RULES:
        try:
            rule_results = rule.check(plan, land, zoning)
            results.extend(rule_results)
        except Exception:
            results.append(CheckResult(
                rule_id=rule.rule_id,
                rule_name_zh=rule.rule_name_zh,
                law_reference=rule.law_reference,
                severity=Severity.WARNING,
                message_zh=f"規則 {rule.rule_id} 檢查時發生錯誤",
            ))
    return results


def get_compliance_summary(results: list[CheckResult]) -> dict:
    """Produce a compliance summary dict."""
    fails = [r for r in results if r.severity == Severity.FAIL]
    warnings = [r for r in results if r.severity == Severity.WARNING]
    passes = [r for r in results if r.severity == Severity.PASS]
    infos = [r for r in results if r.severity == Severity.INFO]
    total = len(results)

    return {
        "total_rules": total,
        "passed": len(passes),
        "warnings": len(warnings),
        "failed": len(fails),
        "info": len(infos),
        "compliance_rate": round(len(passes) / max(1, len(passes) + len(fails)) * 100, 1),
        "fail_details": [
            {"rule": f.rule_id, "law": f.law_reference, "issue": f.message_zh, "suggestion": f.suggestion}
            for f in fails
        ],
        "warning_details": [
            {"rule": w.rule_id, "law": w.law_reference, "issue": w.message_zh, "suggestion": w.suggestion}
            for w in warnings
        ],
    }
