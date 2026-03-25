"""Base classes for the Taiwan Building Code rule engine."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    INFO = "info"


class CheckResult(BaseModel):
    """Result of a single rule check."""

    rule_id: str = Field(description="e.g. TW-BTC-25")
    rule_name_zh: str = Field(description="e.g. 建蔽率檢查")
    law_reference: str = Field(description="e.g. 建築技術規則建築設計施工編 第25條")
    severity: Severity = Severity.PASS
    message_zh: str = ""
    actual_value: float | str = ""
    limit_value: float | str = ""
    suggestion: str = ""


class BaseRule:
    """Abstract base for all building code rules.

    Subclasses must set ``rule_id``, ``rule_name_zh``, ``law_reference`` and
    implement :meth:`check`.
    """

    rule_id: str = ""
    rule_name_zh: str = ""
    law_reference: str = ""

    def check(self, plan, land, zoning) -> list[CheckResult]:
        """Check *plan* against this rule. Returns a list of CheckResults.

        Some rules may produce multiple results (e.g. per-story checks).
        """
        raise NotImplementedError

    def _pass(self, message: str = "", actual="", limit="") -> CheckResult:
        return CheckResult(
            rule_id=self.rule_id,
            rule_name_zh=self.rule_name_zh,
            law_reference=self.law_reference,
            severity=Severity.PASS,
            message_zh=message,
            actual_value=actual,
            limit_value=limit,
        )

    def _fail(self, message: str, actual="", limit="", suggestion: str = "") -> CheckResult:
        return CheckResult(
            rule_id=self.rule_id,
            rule_name_zh=self.rule_name_zh,
            law_reference=self.law_reference,
            severity=Severity.FAIL,
            message_zh=message,
            actual_value=actual,
            limit_value=limit,
            suggestion=suggestion,
        )

    def _warning(self, message: str, actual="", limit="", suggestion: str = "") -> CheckResult:
        return CheckResult(
            rule_id=self.rule_id,
            rule_name_zh=self.rule_name_zh,
            law_reference=self.law_reference,
            severity=Severity.WARNING,
            message_zh=message,
            actual_value=actual,
            limit_value=limit,
            suggestion=suggestion,
        )

    def _info(self, message: str, actual="", limit="") -> CheckResult:
        return CheckResult(
            rule_id=self.rule_id,
            rule_name_zh=self.rule_name_zh,
            law_reference=self.law_reference,
            severity=Severity.INFO,
            message_zh=message,
            actual_value=actual,
            limit_value=limit,
        )
