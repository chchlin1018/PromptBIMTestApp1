"""Compliance report generation — JSON + human-readable table."""

from __future__ import annotations

import json
from datetime import date

from promptbim.codes.base import CheckResult, Severity


def generate_report_json(
    results: list[CheckResult],
    project_name: str = "",
    location: str = "",
    zoning_name: str = "",
) -> dict:
    """Generate a full compliance report as a JSON-serialisable dict."""
    fails = [r for r in results if r.severity == Severity.FAIL]
    warnings = [r for r in results if r.severity == Severity.WARNING]
    passes = [r for r in results if r.severity == Severity.PASS]

    return {
        "project": project_name,
        "check_date": date.today().isoformat(),
        "location": location,
        "zoning": zoning_name,
        "total_rules_checked": len(results),
        "passed": len(passes),
        "warnings": len(warnings),
        "failed": len(fails),
        "compliance_rate": round(
            len(passes) / max(1, len(passes) + len(fails)) * 100, 1
        ),
        "results": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name_zh,
                "law_reference": r.law_reference,
                "severity": r.severity.value,
                "message": r.message_zh,
                "actual": r.actual_value,
                "limit": r.limit_value,
                "suggestion": r.suggestion,
            }
            for r in results
        ],
        "disclaimer": "本報告為 AI 概估用，不替代結構技師及建築師簽證。",
    }


def generate_report_table(results: list[CheckResult]) -> str:
    """Generate a human-readable text table of results."""
    severity_icon = {
        Severity.PASS: "✅",
        Severity.WARNING: "⚠️",
        Severity.FAIL: "❌",
        Severity.INFO: "ℹ️",
    }

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("台灣建築法規合規檢查報告")
    lines.append("=" * 80)
    lines.append("")

    for r in results:
        icon = severity_icon.get(r.severity, "?")
        lines.append(f"{icon} [{r.rule_id}] {r.rule_name_zh}")
        lines.append(f"   法源: {r.law_reference}")
        if r.message_zh:
            lines.append(f"   結果: {r.message_zh}")
        if r.suggestion:
            lines.append(f"   建議: {r.suggestion}")
        lines.append("")

    # Summary
    fails = sum(1 for r in results if r.severity == Severity.FAIL)
    warnings = sum(1 for r in results if r.severity == Severity.WARNING)
    passes = sum(1 for r in results if r.severity == Severity.PASS)
    infos = sum(1 for r in results if r.severity == Severity.INFO)
    lines.append("-" * 80)
    lines.append(
        f"合計: {len(results)} 項 | ✅ 通過 {passes} | ⚠️ 警告 {warnings} "
        f"| ❌ 不通過 {fails} | ℹ️ 資訊 {infos}"
    )
    rate = round(passes / max(1, passes + fails) * 100, 1)
    lines.append(f"合規率: {rate}%")
    lines.append("-" * 80)
    lines.append("※ 本報告為 AI 概估用，不替代結構技師及建築師簽證。")

    return "\n".join(lines)


def report_to_json_string(results: list[CheckResult], **kwargs) -> str:
    """Convenience: generate report dict and serialise to JSON string."""
    report = generate_report_json(results, **kwargs)
    return json.dumps(report, ensure_ascii=False, indent=2)
