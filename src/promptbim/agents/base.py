"""Base agent wrapping the Anthropic Claude API."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from promptbim.config import get_settings
from promptbim.debug import get_logger

logger = get_logger("agents.base")


@dataclass
class AgentResponse:
    """Structured response from a Claude API call."""

    text: str = ""
    json_data: dict | None = None
    usage: dict = field(default_factory=dict)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


class BaseAgent:
    """Thin wrapper around the Anthropic Python SDK.

    Subclasses set ``SYSTEM_PROMPT`` and optionally override
    :meth:`_parse_response` to extract structured data.
    """

    SYSTEM_PROMPT: str = "You are a helpful assistant."

    def __init__(self, model: str | None = None, max_tokens: int = 4096) -> None:
        self._settings = get_settings()
        self._model = model or self._settings.claude_model
        self._max_tokens = max_tokens
        self._client = None  # lazy init

    @property
    def client(self):
        if self._client is None:
            import anthropic

            api_key = self._settings.anthropic_api_key
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY not set. Add it to .env or environment.")
            self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

    def run(self, user_message: str) -> AgentResponse:
        """Send *user_message* to Claude and return an :class:`AgentResponse`."""
        try:
            logger.debug("API request: model=%s, max_tokens=%d", self._model, self._max_tokens)
            t0 = time.time()
            message = self.client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            elapsed = time.time() - t0
            text = message.content[0].text
            usage = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }
            logger.debug(
                "API response: %.2fs, input_tokens=%d, output_tokens=%d",
                elapsed,
                usage["input_tokens"],
                usage["output_tokens"],
            )
            resp = self._parse_response(text, usage)
            logger.debug("JSON parse: %s", "OK" if resp.json_data else "no JSON")
            return resp
        except Exception as exc:
            logger.exception("Agent API call failed")
            return AgentResponse(error=str(exc))

    def _parse_response(self, text: str, usage: dict) -> AgentResponse:
        """Parse raw text into an :class:`AgentResponse`.

        Override in subclasses to extract JSON etc.
        """
        json_data = _try_extract_json(text)
        return AgentResponse(text=text, json_data=json_data, usage=usage)


def _try_extract_json(text: str) -> dict | None:
    """Try to extract a JSON object from text (possibly wrapped in markdown)."""
    # Try direct parse first
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Try extracting from ```json ... ``` blocks
    import re

    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except (json.JSONDecodeError, TypeError):
            pass

    # Try finding first { ... } block
    brace_start = text.find("{")
    if brace_start >= 0:
        depth = 0
        for i in range(brace_start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[brace_start : i + 1])
                    except (json.JSONDecodeError, TypeError):
                        pass
                    break

    return None
