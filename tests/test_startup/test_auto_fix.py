"""Tests for auto-fix suggestion module."""

from unittest.mock import patch

from promptbim.startup.auto_fix import (
    auto_fix,
    auto_fix_all,
    can_auto_fix,
    generate_fix_report,
    get_fix_suggestion,
)
from promptbim.startup.health_check import CheckResult


class TestGetFixSuggestion:
    """Test fix suggestion generation."""

    def test_returns_fix_hint_if_present(self):
        r = CheckResult(
            name="test",
            category="c",
            status="fail",
            message="bad",
            fix_hint="custom fix",
        )
        assert get_fix_suggestion(r) == "custom fix"

    def test_returns_command_for_known_check(self):
        r = CheckResult(
            name="PySide6",
            category="Core dependencies",
            status="fail",
            message="Not installed",
        )
        suggestion = get_fix_suggestion(r)
        assert suggestion is not None
        assert "PySide6" in suggestion

    def test_returns_manual_fix_for_api_key(self):
        r = CheckResult(
            name="API Key",
            category="AI services",
            status="fail",
            message="not set",
        )
        suggestion = get_fix_suggestion(r)
        assert suggestion is not None
        assert "console.anthropic.com" in suggestion


class TestCanAutoFix:
    """Test auto-fix eligibility."""

    def test_known_fail_is_fixable(self):
        r = CheckResult(
            name="ifcopenshell",
            category="Core dependencies",
            status="fail",
            message="Not installed",
        )
        assert can_auto_fix(r) is True

    def test_pass_is_not_fixable(self):
        r = CheckResult(
            name="ifcopenshell",
            category="Core dependencies",
            status="pass",
            message="OK",
        )
        assert can_auto_fix(r) is False

    def test_unknown_check_not_fixable(self):
        r = CheckResult(
            name="Unknown Check",
            category="Other",
            status="fail",
            message="bad",
        )
        assert can_auto_fix(r) is False


class TestAutoFix:
    """Test auto-fix execution."""

    def test_auto_fix_not_available(self):
        r = CheckResult(
            name="API Key",
            category="AI services",
            status="fail",
            message="not set",
        )
        result = auto_fix(r)
        assert result.success is False

    @patch("subprocess.run")
    def test_auto_fix_success(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Successfully installed"
        mock_run.return_value.stderr = ""

        r = CheckResult(
            name="PySide6",
            category="Core dependencies",
            status="fail",
            message="Not installed",
        )
        result = auto_fix(r)
        assert result.success is True
        assert mock_run.called

    @patch("subprocess.run")
    def test_auto_fix_failure(self, mock_run):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "Error: no matching package"

        r = CheckResult(
            name="PySide6",
            category="Core dependencies",
            status="fail",
            message="Not installed",
        )
        result = auto_fix(r)
        assert result.success is False


class TestGenerateFixReport:
    """Test fix report generation."""

    def test_all_passed(self):
        results = [
            CheckResult(name="a", category="c", status="pass", message="ok"),
        ]
        report = generate_fix_report(results)
        assert "No fixes needed" in report

    def test_with_failures(self):
        results = [
            CheckResult(
                name="PySide6",
                category="c",
                status="fail",
                message="missing",
                fix_hint="pip install PySide6",
            ),
            CheckResult(name="ok", category="c", status="pass", message="ok"),
        ]
        report = generate_fix_report(results)
        assert "PySide6" in report
        assert "pip install" in report

    def test_auto_fix_all_filters_fixable(self):
        results = [
            CheckResult(name="PySide6", category="c", status="fail", message="missing"),
            CheckResult(name="API Key", category="c", status="fail", message="not set"),
        ]
        with patch("promptbim.startup.auto_fix.auto_fix") as mock_fix:
            mock_fix.return_value.success = True
            fix_results = auto_fix_all(results)
            # Only PySide6 is auto-fixable
            assert mock_fix.call_count == 1
