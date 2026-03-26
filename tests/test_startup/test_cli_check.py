"""Tests for CLI check subcommand."""

import json
from unittest.mock import MagicMock, patch

import pytest

from promptbim.startup.health_check import CheckResult


class TestCliCheck:
    """Test the CLI check subcommand."""

    def _make_mock_checker(self):
        """Create a mock HealthChecker with preset results."""
        mock = MagicMock()
        mock.run_all.return_value = [
            CheckResult(
                name="Python version",
                category="Python environment",
                status="pass",
                message="3.11.15",
                elapsed_ms=1.0,
            ),
            CheckResult(
                name="Conda env",
                category="Python environment",
                status="pass",
                message="promptbim",
                elapsed_ms=1.0,
            ),
        ]
        mock.run_ai_only.return_value = [
            CheckResult(
                name="API Key", category="AI services", status="pass", message="set", elapsed_ms=1.0
            ),
        ]
        mock.to_dict.return_value = [{"name": "test", "status": "pass"}]
        mock.summary.return_value = {
            "total": 2,
            "passed": 2,
            "failed": 0,
            "warned": 0,
            "skipped": 0,
            "all_passed": True,
        }
        return mock

    @patch("promptbim.startup.health_check.HealthChecker")
    def test_check_command_runs(self, MockChecker, capsys):
        MockChecker.return_value = self._make_mock_checker()

        from promptbim.__main__ import _run_check

        args = MagicMock()
        args.json = False
        args.ai = False
        args.fix = False

        with pytest.raises(SystemExit) as exc:
            _run_check(args)
        assert exc.value.code == 0

    @patch("promptbim.startup.health_check.HealthChecker")
    def test_check_json_output(self, MockChecker, capsys):
        MockChecker.return_value = self._make_mock_checker()

        from promptbim.__main__ import _run_check

        args = MagicMock()
        args.json = True
        args.ai = False
        args.fix = False

        with pytest.raises(SystemExit):
            _run_check(args)

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "results" in data
        assert "summary" in data

    @patch("promptbim.startup.health_check.HealthChecker")
    def test_check_ai_only(self, MockChecker):
        mock = self._make_mock_checker()
        MockChecker.return_value = mock

        from promptbim.__main__ import _run_check

        args = MagicMock()
        args.json = False
        args.ai = True
        args.fix = False

        with pytest.raises(SystemExit):
            _run_check(args)

        mock.run_ai_only.assert_called_once()

    @patch("promptbim.startup.health_check.HealthChecker")
    def test_check_exit_code_on_failure(self, MockChecker):
        mock = self._make_mock_checker()
        mock.summary.return_value = {
            "total": 2,
            "passed": 1,
            "failed": 1,
            "warned": 0,
            "skipped": 0,
            "all_passed": False,
        }
        MockChecker.return_value = mock

        from promptbim.__main__ import _run_check

        args = MagicMock()
        args.json = False
        args.ai = False
        args.fix = False

        with pytest.raises(SystemExit) as exc:
            _run_check(args)
        assert exc.value.code == 1


class TestStartupCheckDisabled:
    """Test that startup_check_enabled=False skips the check."""

    def test_config_defaults(self):
        from promptbim.config import Settings

        s = Settings()
        assert s.startup_check_enabled is True
        assert s.startup_check_skip_ai is False
        assert s.ai_ping_timeout_seconds == 10.0
        assert s.ai_model == "claude-sonnet-4-20250514"
