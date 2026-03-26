"""Tests for AI check module — mock API success/failure/timeout."""

import os
from unittest.mock import MagicMock, patch

from promptbim.startup.ai_check import check_api_key, check_model_available, ping_claude


class TestCheckApiKey:
    """Test API key validation."""

    def test_key_not_set(self):
        with patch.dict(os.environ, {}, clear=True):
            env = os.environ.copy()
            env.pop("ANTHROPIC_API_KEY", None)
            with patch.dict(os.environ, env, clear=True):
                settings = MagicMock()
                settings.anthropic_api_key = ""
                result = check_api_key(settings)
                assert result.status == "fail"

    def test_valid_key_format(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-api03-test1234567890abcdef"}):
            result = check_api_key()
            assert result.status == "pass"

    def test_unusual_key_format(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "unusual-key-format-12345678"}):
            result = check_api_key()
            assert result.status == "warn"

    def test_key_from_settings(self):
        with patch.dict(os.environ, {}, clear=True):
            env = os.environ.copy()
            env.pop("ANTHROPIC_API_KEY", None)
            with patch.dict(os.environ, env, clear=True):
                settings = MagicMock()
                settings.anthropic_api_key = "sk-ant-api03-test1234567890"
                result = check_api_key(settings)
                assert result.status == "pass"


class TestPingClaude:
    """Test Claude API ping with mocked responses."""

    def test_ping_success(self):
        mock_response = MagicMock()
        mock_response.stop_reason = "end_turn"
        mock_response.model = "claude-sonnet-4-20250514"
        mock_response.usage.input_tokens = 5
        mock_response.usage.output_tokens = 3

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        with patch("promptbim.startup.ai_check.anthropic", create=True) as mock_mod:
            mock_mod.Anthropic.return_value = mock_client
            # Need to patch the import inside the function
            original_import = (
                __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__
            )

            settings = MagicMock()
            settings.ai_ping_timeout_seconds = 10.0
            settings.ai_model = "claude-sonnet-4-20250514"

            with patch.dict("sys.modules", {"anthropic": mock_mod}):
                result = ping_claude(settings)
                assert result.status == "pass"
                assert "OK" in result.message

    def test_ping_auth_error(self):
        mock_mod = MagicMock()
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("AuthenticationError: Invalid API key")
        mock_mod.Anthropic.return_value = mock_client

        settings = MagicMock()
        settings.ai_ping_timeout_seconds = 5.0
        settings.ai_model = "claude-sonnet-4-20250514"

        with patch.dict("sys.modules", {"anthropic": mock_mod}):
            result = ping_claude(settings)
            assert result.status == "fail"

    def test_ping_timeout(self):
        mock_mod = MagicMock()
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("timeout: request timed out")
        mock_mod.Anthropic.return_value = mock_client

        settings = MagicMock()
        settings.ai_ping_timeout_seconds = 1.0
        settings.ai_model = "claude-sonnet-4-20250514"

        with patch.dict("sys.modules", {"anthropic": mock_mod}):
            result = ping_claude(settings)
            assert result.status == "fail"
            assert "timeout" in (result.fix_hint or "").lower()


class TestCheckModelAvailable:
    """Test model availability check."""

    def test_model_available(self):
        settings = MagicMock()
        settings.ai_model = "claude-sonnet-4-20250514"
        result = check_model_available(settings)
        assert result.status == "pass"
        assert "claude-sonnet-4-20250514" in result.message

    def test_default_model(self):
        result = check_model_available()
        assert result.status == "pass"
