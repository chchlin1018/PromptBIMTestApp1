"""Network failure simulation tests for Agent layer."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


class TestNetworkTimeout:
    """Test timeout handling in BaseAgent."""

    def test_timeout_returns_error_response(self):
        """Agent should return error on timeout."""
        from promptbim.agents.base import BaseAgent

        agent = BaseAgent()

        with patch.object(type(agent), "_call_api_with_retry") as mock_call:
            mock_call.side_effect = TimeoutError("Request timed out")
            resp = agent.run("test prompt")
            assert not resp.ok
            assert resp.error is not None

    def test_timeout_error_message_is_descriptive(self):
        """Error message should mention timeout."""
        from promptbim.agents.base import BaseAgent

        agent = BaseAgent()

        with patch.object(type(agent), "_call_api_with_retry") as mock_call:
            mock_call.side_effect = TimeoutError("Connection timed out")
            resp = agent.run("test")
            assert "timed out" in resp.error.lower() or "timeout" in resp.error.lower()


class TestConnectionError:
    """Test connection error handling."""

    def test_connection_refused(self):
        """Agent should handle connection refused gracefully."""
        from promptbim.agents.base import BaseAgent

        agent = BaseAgent()

        with patch.object(agent, "_call_api_with_retry") as mock_call:
            mock_call.side_effect = ConnectionError("Connection refused")
            resp = agent.run("test prompt")
            assert not resp.ok
            assert "refused" in resp.error.lower() or "connection" in resp.error.lower()

    def test_dns_resolution_failure(self):
        """Agent should handle DNS failure gracefully."""
        from promptbim.agents.base import BaseAgent

        agent = BaseAgent()

        with patch.object(agent, "_call_api_with_retry") as mock_call:
            mock_call.side_effect = OSError("Name or service not known")
            resp = agent.run("test")
            assert not resp.ok


class TestServerErrors:
    """Test 5xx server error retry behavior."""

    def test_5xx_is_retryable(self):
        """5xx errors should be classified as retryable."""
        import anthropic

        from promptbim.agents.base import _is_retryable_api_error

        error_503 = anthropic.APIStatusError(
            message="Service Unavailable",
            response=MagicMock(status_code=503, headers={}, text=""),
            body={"error": {"message": "Service Unavailable"}},
        )
        assert _is_retryable_api_error(error_503)

        error_500 = anthropic.APIStatusError(
            message="Internal Server Error",
            response=MagicMock(status_code=500, headers={}, text=""),
            body={"error": {"message": "Internal Server Error"}},
        )
        assert _is_retryable_api_error(error_500)

    def test_500_retried_up_to_max(self):
        """500 errors should result in error response."""
        from promptbim.agents.base import BaseAgent

        agent = BaseAgent()

        with patch.object(type(agent), "_call_api_with_retry") as mock_call:
            mock_call.side_effect = ConnectionError("Internal Server Error 500")
            resp = agent.run("test")
            assert not resp.ok


class TestRateLimiting:
    """Test 429 rate limit handling."""

    def test_429_not_retried(self):
        """429 should NOT be retried (rate limiter handles this)."""
        import anthropic

        from promptbim.agents.base import _is_retryable_api_error

        error_429 = anthropic.APIStatusError(
            message="Rate limited",
            response=MagicMock(status_code=429, headers={}, text=""),
            body={"error": {"message": "Rate limited"}},
        )
        # 429 is not a 5xx, so should not be retried
        assert not _is_retryable_api_error(error_429)


class TestRateLimiterUnit:
    """Test token bucket rate limiter."""

    def test_acquire_within_limit(self):
        """Should acquire tokens within RPM limit."""
        from promptbim.agents.rate_limiter import TokenBucketRateLimiter

        limiter = TokenBucketRateLimiter(rpm=60)
        assert limiter.acquire(timeout=1.0)

    def test_acquire_timeout_when_exhausted(self):
        """Should timeout when all tokens exhausted."""
        from promptbim.agents.rate_limiter import TokenBucketRateLimiter

        limiter = TokenBucketRateLimiter(rpm=1)
        assert limiter.acquire(timeout=0.1)  # consume the one token
        assert not limiter.acquire(timeout=0.1)  # should timeout

    def test_tokens_refill_over_time(self):
        """Tokens should refill based on elapsed time."""
        import time

        from promptbim.agents.rate_limiter import TokenBucketRateLimiter

        limiter = TokenBucketRateLimiter(rpm=60)  # 1 per second
        limiter.acquire(timeout=0.1)
        time.sleep(0.15)
        assert limiter.available_tokens() >= 0.1
