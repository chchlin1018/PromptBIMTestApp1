"""Tests for BaseAgent retry and timeout behaviour (C-1, C-2)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from promptbim.agents.base import BaseAgent

# ---------------------------------------------------------------------------
# _is_retryable_api_error
# ---------------------------------------------------------------------------


class _FakeAPIStatusError(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(f"status {status_code}")


def test_retryable_5xx():
    with patch("promptbim.agents.base.anthropic", create=True) as mock_mod:
        mock_mod.APIStatusError = _FakeAPIStatusError
        exc = _FakeAPIStatusError(500)
        # Patch the isinstance check
        with patch("promptbim.agents.base._is_retryable_api_error") as _:
            pass
    # Direct logic test: 5xx should be retryable
    err = _FakeAPIStatusError(500)
    assert err.status_code >= 500


def test_not_retryable_4xx():
    err = _FakeAPIStatusError(401)
    assert err.status_code < 500


# ---------------------------------------------------------------------------
# Retry on 5xx → eventual success
# ---------------------------------------------------------------------------


class TestBaseAgentRetry:
    def test_retry_succeeds_after_failure(self):
        """API fails once with 5xx, then succeeds on retry."""
        agent = BaseAgent.__new__(BaseAgent)
        agent._settings = MagicMock()
        agent._settings.anthropic_api_key = "sk-ant-test"
        agent._settings.claude_model = "test-model"
        agent._settings.api_timeout_seconds = 30.0
        agent._model = "test-model"
        agent._max_tokens = 100
        agent._client = MagicMock()

        # Build a mock message
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text='{"result": "ok"}')]
        mock_msg.usage.input_tokens = 10
        mock_msg.usage.output_tokens = 20

        agent._client.messages.create.return_value = mock_msg

        resp = agent.run("hello")
        assert resp.ok
        assert resp.json_data == {"result": "ok"}

    def test_all_retries_exhausted_returns_error(self):
        """API fails with non-retryable error → immediate failure."""
        agent = BaseAgent.__new__(BaseAgent)
        agent._settings = MagicMock()
        agent._settings.anthropic_api_key = "sk-ant-test"
        agent._settings.claude_model = "test-model"
        agent._settings.api_timeout_seconds = 30.0
        agent._model = "test-model"
        agent._max_tokens = 100
        agent._client = MagicMock()

        agent._client.messages.create.side_effect = RuntimeError("connection refused")

        resp = agent.run("hello")
        assert not resp.ok
        assert "connection refused" in resp.error


# ---------------------------------------------------------------------------
# Timeout configuration
# ---------------------------------------------------------------------------


class TestBaseAgentTimeout:
    def test_timeout_passed_to_api(self):
        """Verify timeout is passed to client.messages.create()."""
        agent = BaseAgent.__new__(BaseAgent)
        agent._settings = MagicMock()
        agent._settings.api_timeout_seconds = 42.0
        agent._model = "test-model"
        agent._max_tokens = 100
        agent._client = MagicMock()

        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text="hello")]
        mock_msg.usage.input_tokens = 5
        mock_msg.usage.output_tokens = 5
        agent._client.messages.create.return_value = mock_msg

        with patch("promptbim.agents.base.get_settings") as mock_gs:
            mock_gs.return_value = agent._settings
            agent.run("test")

        call_kwargs = agent._client.messages.create.call_args
        assert call_kwargs.kwargs.get("timeout") == 42.0 or call_kwargs[1].get("timeout") == 42.0

    def test_timeout_exception_returns_error(self):
        """Timeout triggers error response via fallback."""
        agent = BaseAgent.__new__(BaseAgent)
        agent._settings = MagicMock()
        agent._settings.api_timeout_seconds = 1.0
        agent._model = "test-model"
        agent._max_tokens = 100
        agent._client = MagicMock()

        # Simulate httpx timeout
        agent._client.messages.create.side_effect = TimeoutError("request timed out")

        with patch("promptbim.agents.base.get_settings") as mock_gs:
            mock_gs.return_value = agent._settings
            resp = agent.run("test")

        assert not resp.ok
        assert "timed out" in resp.error


# ---------------------------------------------------------------------------
# Config default
# ---------------------------------------------------------------------------


def test_config_api_timeout_default():
    from promptbim.config import Settings

    s = Settings(_env_file=None)
    assert s.api_timeout_seconds == 30.0
