"""Token-bucket rate limiter for API calls."""

from __future__ import annotations

import threading
import time

from promptbim.debug import get_logger

logger = get_logger("agents.rate_limiter")


class TokenBucketRateLimiter:
    """Simple token-bucket rate limiter.

    Args:
        rpm: Maximum requests per minute.
    """

    def __init__(self, rpm: int = 50) -> None:
        self._rpm = rpm
        self._tokens = float(rpm)
        self._max_tokens = float(rpm)
        self._refill_rate = rpm / 60.0  # tokens per second
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    @property
    def rpm(self) -> int:
        return self._rpm

    def acquire(self, timeout: float = 60.0) -> bool:
        """Block until a token is available or timeout expires.

        Returns True if a token was acquired, False on timeout.
        """
        deadline = time.monotonic() + timeout
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return True
            if time.monotonic() >= deadline:
                logger.warning("Rate limiter timeout after %.1fs", timeout)
                return False
            time.sleep(0.05)

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._max_tokens, self._tokens + elapsed * self._refill_rate)
        self._last_refill = now

    def available_tokens(self) -> float:
        with self._lock:
            self._refill()
            return self._tokens


# Module-level singleton
_global_limiter: TokenBucketRateLimiter | None = None
_limiter_lock = threading.Lock()


def get_rate_limiter() -> TokenBucketRateLimiter:
    """Return the global rate limiter singleton."""
    global _global_limiter
    if _global_limiter is None:
        with _limiter_lock:
            if _global_limiter is None:
                from promptbim.config import get_settings

                settings = get_settings()
                rpm = getattr(settings, "api_rate_limit_rpm", 50)
                _global_limiter = TokenBucketRateLimiter(rpm=rpm)
    return _global_limiter


def reset_rate_limiter() -> None:
    """Reset the global rate limiter (for testing)."""
    global _global_limiter
    with _limiter_lock:
        _global_limiter = None
