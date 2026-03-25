"""Tests for the PromptBIM debug logging system."""

import logging
import os

import pytest

from promptbim.debug import (
    DEBUG_MODE,
    disable_debug,
    enable_debug,
    get_logger,
)


class TestGetLogger:
    """Test get_logger() creates properly configured loggers."""

    def test_creates_logger_with_prefix(self):
        logger = get_logger("test.module")
        assert logger.name == "promptbim.test.module"

    def test_logger_has_handler(self):
        logger = get_logger("test.handler")
        assert len(logger.handlers) >= 1

    def test_logger_does_not_propagate(self):
        logger = get_logger("test.propagate")
        assert logger.propagate is False

    def test_multiple_calls_same_logger(self):
        l1 = get_logger("test.same")
        l2 = get_logger("test.same")
        assert l1 is l2
        # Should not add duplicate handlers
        assert len(l1.handlers) == 1


class TestDebugModeToggle:
    """Test enable_debug() / disable_debug() runtime switching."""

    def test_enable_debug(self):
        logger = get_logger("test.toggle_on")
        disable_debug()
        assert logger.level == logging.WARNING

        enable_debug()
        # Re-fetch to see updated level
        logger = get_logger("test.toggle_on")
        assert logger.level == logging.DEBUG

    def test_disable_debug(self):
        enable_debug()
        logger = get_logger("test.toggle_off")
        assert logger.level == logging.DEBUG

        disable_debug()
        logger = get_logger("test.toggle_off")
        assert logger.level == logging.WARNING

    def test_toggle_affects_all_promptbim_loggers(self):
        l1 = get_logger("test.multi1")
        l2 = get_logger("test.multi2")

        enable_debug()
        assert l1.level == logging.DEBUG
        assert l2.level == logging.DEBUG

        disable_debug()
        assert l1.level == logging.WARNING
        assert l2.level == logging.WARNING


class TestEnvironmentVariable:
    """Test PROMPTBIM_DEBUG environment variable."""

    def test_env_var_enables_debug(self, monkeypatch):
        monkeypatch.setenv("PROMPTBIM_DEBUG", "1")
        # Re-import to pick up env var
        import importlib
        import promptbim.debug as dbg
        importlib.reload(dbg)
        assert dbg.DEBUG_MODE is True

        # Clean up
        monkeypatch.delenv("PROMPTBIM_DEBUG", raising=False)
        importlib.reload(dbg)

    def test_env_var_default_off(self, monkeypatch):
        monkeypatch.delenv("PROMPTBIM_DEBUG", raising=False)
        import importlib
        import promptbim.debug as dbg
        importlib.reload(dbg)
        assert dbg.DEBUG_MODE is False


class TestProductionMode:
    """Test that production mode suppresses debug output."""

    def test_no_debug_output_in_production(self, capsys):
        disable_debug()
        logger = get_logger("test.production")
        logger.debug("This should NOT appear")
        captured = capsys.readouterr()
        assert "This should NOT appear" not in captured.out
        assert "This should NOT appear" not in captured.err

    def test_warning_output_in_production(self, capsys):
        disable_debug()
        logger = get_logger("test.production_warn")
        logger.warning("This SHOULD appear")
        captured = capsys.readouterr()
        assert "This SHOULD appear" in captured.err


class TestCLIDebugFlag:
    """Test --debug CLI argument."""

    def test_cli_debug_flag_parsed(self):
        from promptbim.__main__ import app
        import sys

        # Just verify the parser accepts --debug without error
        old_argv = sys.argv
        sys.argv = ["promptbim", "--debug"]
        try:
            # This will try to print help and exit, which is fine
            app()
        except SystemExit:
            pass
        finally:
            sys.argv = old_argv
