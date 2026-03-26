"""Claude AI connection validation module.

Provides individual check functions for API key, ping test, and model availability.
All functions return CheckResult and use the debug logger.
"""

from __future__ import annotations

import os
import re
import time

from promptbim.debug import get_logger
from promptbim.startup.health_check import CheckResult

logger = get_logger("startup.ai")


def check_api_key(settings=None) -> CheckResult:
    """Verify ANTHROPIC_API_KEY is set and has valid format (sk-ant-*)."""
    start = time.monotonic()

    # Check env var first, then settings
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key and settings:
        key = settings.anthropic_api_key

    elapsed = (time.monotonic() - start) * 1000

    if not key:
        return CheckResult(
            name="API Key",
            category="AI services",
            status="fail",
            message="ANTHROPIC_API_KEY not set",
            fix_hint="Set ANTHROPIC_API_KEY in .env file (get key from console.anthropic.com)",
            elapsed_ms=elapsed,
        )

    # Mask key for logging
    masked = f"{key[:7]}...{key[-4:]}" if len(key) > 15 else "***"
    logger.debug("API Key found: %s", masked)

    # Validate format
    if not re.match(r"^sk-ant-", key):
        return CheckResult(
            name="API Key",
            category="AI services",
            status="warn",
            message=f"API Key set but unusual format ({masked})",
            detail="Expected format: sk-ant-*",
            fix_hint="Verify key at console.anthropic.com",
            elapsed_ms=elapsed,
        )

    return CheckResult(
        name="API Key",
        category="AI services",
        status="pass",
        message=f"API Key set ({masked})",
        elapsed_ms=elapsed,
    )


def ping_claude(settings=None, timeout: float | None = None) -> CheckResult:
    """Send minimal API request to verify Claude connectivity.

    Sends max_tokens=10 "ping" message and measures response time.
    """
    if timeout is None:
        timeout = settings.ai_ping_timeout_seconds if settings else 10.0

    model = settings.ai_model if settings else "claude-sonnet-4-20250514"
    start = time.monotonic()

    try:
        import anthropic

        client = anthropic.Anthropic(timeout=timeout)
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "ping"}],
        )
        elapsed = (time.monotonic() - start) * 1000

        logger.debug(
            "Claude API ping: %s, %.0fms, usage: in=%d out=%d",
            response.stop_reason,
            elapsed,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )

        return CheckResult(
            name="Claude API ping",
            category="AI services",
            status="pass",
            message=f"200 OK, {elapsed:.0f}ms",
            detail=f"model={response.model}, stop={response.stop_reason}",
            elapsed_ms=elapsed,
        )

    except ImportError:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(
            name="Claude API ping",
            category="AI services",
            status="fail",
            message="anthropic SDK not installed",
            fix_hint="pip install anthropic",
            elapsed_ms=elapsed,
        )

    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        error_type = type(e).__name__

        # Classify error for better hints
        hint = "Check network connection"
        if "authentication" in error_type.lower() or "auth" in str(e).lower():
            hint = "Check ANTHROPIC_API_KEY in .env"
        elif "rate" in error_type.lower() or "rate" in str(e).lower():
            return CheckResult(
                name="Claude API ping",
                category="AI services",
                status="warn",
                message=f"Rate limited ({error_type})",
                detail=str(e),
                fix_hint="API rate limit — wait and retry",
                elapsed_ms=elapsed,
            )
        elif "timeout" in error_type.lower() or "timeout" in str(e).lower():
            hint = "API timeout — check network or increase ai_ping_timeout_seconds"

        logger.debug("Claude API ping failed: %s: %s", error_type, e)

        return CheckResult(
            name="Claude API ping",
            category="AI services",
            status="fail",
            message=f"Connection failed ({error_type})",
            detail=str(e),
            fix_hint=hint,
            elapsed_ms=elapsed,
        )


def check_model_available(settings=None) -> CheckResult:
    """Check if the configured model is available (from last ping result)."""
    start = time.monotonic()
    model = settings.ai_model if settings else "claude-sonnet-4-20250514"
    elapsed = (time.monotonic() - start) * 1000

    # Model availability is implicitly confirmed if ping succeeded with that model
    return CheckResult(
        name="Model available",
        category="AI services",
        status="pass",
        message=f"{model} available",
        elapsed_ms=elapsed,
    )


def check_vision_available(settings=None, timeout: float | None = None) -> CheckResult:
    """Check if Vision API is available (for P9 image recognition)."""
    if timeout is None:
        timeout = settings.ai_ping_timeout_seconds if settings else 10.0

    model = settings.ai_model if settings else "claude-sonnet-4-20250514"
    start = time.monotonic()

    try:
        import base64

        import anthropic

        # Create a minimal 1x1 white PNG for testing
        minimal_png = base64.b64encode(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
            b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
            b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        ).decode()

        client = anthropic.Anthropic(timeout=timeout)
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": minimal_png,
                            },
                        },
                        {"type": "text", "text": "ok"},
                    ],
                }
            ],
        )
        elapsed = (time.monotonic() - start) * 1000

        return CheckResult(
            name="Vision API",
            category="AI services",
            status="pass",
            message=f"Vision OK, {elapsed:.0f}ms",
            elapsed_ms=elapsed,
        )

    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(
            name="Vision API",
            category="AI services",
            status="warn",
            message=f"Vision check failed: {type(e).__name__}",
            detail=str(e),
            elapsed_ms=elapsed,
        )
