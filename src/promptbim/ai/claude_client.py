"""Claude API client for NL→BIM intent parsing.

Uses the Anthropic SDK to parse ambiguous natural language
into structured BIM intents when regex fails.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from promptbim.debug import get_logger

if TYPE_CHECKING:
    from promptbim.ai.nl_parser import BIMIntent

logger = get_logger("ai.claude_client")

_INTENT_SYSTEM_PROMPT = """\
You are a BIM (Building Information Modeling) intent parser.
Given a natural language command about a building or its components,
extract the structured intent as JSON.

Entity types: Wall, Slab, Column, Beam, Roof, Door, Window, Stair,
Elevator, Ramp, Chiller, CoolingTower, AHU, Pump, Fan, Pipe, Duct,
Cable, Valve, Sensor, ExhaustStack, Generic.

Intent types: create, delete, move, rotate, resize, query, query_type,
query_name, get_position, get_nearby, get_scene_info, connect, cost, schedule.

Return ONLY valid JSON with these fields:
{
  "intent": "<intent_type>",
  "entity_type": "<EntityType or null>",
  "entity_id": "<id like chiller-1 or null>",
  "entity_name": "<name or null>",
  "target_id": "<target entity id or null>",
  "position": [x, y, z] or null,
  "dimensions": [w, h, d] or null,
  "rotation": [rx, ry, rz] or null,
  "radius": <number or null>,
  "confidence": <0.0-1.0>
}
"""

# Singleton
_client_instance: ClaudeClient | None = None


class ClaudeClient:
    """Lightweight Claude API wrapper for intent parsing."""

    def __init__(self, mock_mode: bool = False) -> None:
        self._mock_mode = mock_mode
        self._api_client = None

    @property
    def api_client(self):
        if self._api_client is None and not self._mock_mode:
            import anthropic
            from promptbim.config import get_settings
            settings = get_settings()
            api_key = settings.anthropic_api_key
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY not set")
            self._api_client = anthropic.Anthropic(api_key=api_key)
        return self._api_client

    def parse_intent(self, text: str) -> "BIMIntent | None":
        """Parse NL text into a BIMIntent using Claude."""
        from promptbim.ai.nl_parser import BIMIntent, IntentType

        if self._mock_mode:
            return self._mock_parse(text)

        try:
            message = self.api_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                system=_INTENT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": text}],
                timeout=15,
            )
            raw = message.content[0].text
            data = _extract_json(raw)
            if data:
                return _json_to_intent(data, text)
        except Exception as e:
            logger.warning("Claude intent parse error: %s", e)
        return None

    def chat(self, messages: list[dict], system: str | None = None) -> str:
        """General chat call with message history."""
        if self._mock_mode:
            return "[mock] I understood your request."

        try:
            msg = self.api_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system or "You are a helpful BIM assistant.",
                messages=messages,
                timeout=30,
            )
            return msg.content[0].text
        except Exception as e:
            logger.error("Claude chat error: %s", e)
            raise

    def _mock_parse(self, text: str) -> "BIMIntent | None":
        """Mock mode for testing without API calls."""
        from promptbim.ai.nl_parser import BIMIntent, IntentType
        lower = text.lower()
        if any(w in lower for w in ["建立", "create", "add"]):
            return BIMIntent(
                intent_type=IntentType.CREATE,
                entity_type="Wall",
                position=(5.0, 5.0, 0.0),
                raw_text=text,
                confidence=0.7,
            )
        return None


def _extract_json(text: str) -> dict | None:
    """Extract JSON from Claude's response."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    import re
    m = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except (json.JSONDecodeError, TypeError):
            pass
    return None


def _json_to_intent(data: dict, raw_text: str) -> "BIMIntent":
    """Convert parsed JSON dict to BIMIntent."""
    from promptbim.ai.nl_parser import BIMIntent, IntentType

    intent_str = data.get("intent", "unknown")
    try:
        intent_type = IntentType(intent_str)
    except ValueError:
        intent_type = IntentType.UNKNOWN

    pos = data.get("position")
    dims = data.get("dimensions")
    rot = data.get("rotation")

    return BIMIntent(
        intent_type=intent_type,
        entity_type=data.get("entity_type"),
        entity_id=data.get("entity_id"),
        entity_name=data.get("entity_name"),
        target_id=data.get("target_id"),
        position=tuple(pos) if pos and len(pos) == 3 else None,
        dimensions=tuple(dims) if dims and len(dims) == 3 else None,
        rotation=tuple(rot) if rot and len(rot) == 3 else None,
        radius=data.get("radius", 10.0) or 10.0,
        raw_text=raw_text,
        confidence=data.get("confidence", 0.6) or 0.6,
    )


def get_claude_client(mock_mode: bool = False) -> ClaudeClient:
    """Get or create the singleton ClaudeClient."""
    global _client_instance
    if _client_instance is None:
        _client_instance = ClaudeClient(mock_mode=mock_mode)
    return _client_instance
