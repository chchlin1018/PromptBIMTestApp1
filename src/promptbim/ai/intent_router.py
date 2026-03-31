"""IntentRouter — Maps BIMIntent to AgentBridge JSON actions.

Translates parsed intents into the JSON format expected by
C++ AgentBridge::executeJson().
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from promptbim.ai.nl_parser import BIMIntent, IntentType
from promptbim.debug import get_logger

logger = get_logger("ai.intent_router")

# All 13 AgentBridge actions — must match C++ executeJson action strings
ACTION_MAP: dict[IntentType, str] = {
    IntentType.QUERY_TYPE:      "query_by_type",
    IntentType.QUERY_NAME:      "query_by_name",
    IntentType.QUERY:           "query_by_name",
    IntentType.GET_POSITION:    "get_position",
    IntentType.GET_NEARBY:      "get_nearby",
    IntentType.GET_SCENE_INFO:  "get_scene_info",
    IntentType.MOVE:            "move",
    IntentType.ROTATE:          "rotate",
    IntentType.RESIZE:          "resize",
    IntentType.CREATE:          "add",
    IntentType.DELETE:           "delete",
    IntentType.CONNECT:         "connect",
    IntentType.COST:            "cost_delta",
    IntentType.SCHEDULE:        "schedule_impact",
}


class IntentRouter:
    """Routes BIMIntents to AgentBridge JSON actions."""

    def route(self, intent: BIMIntent) -> dict[str, Any] | None:
        """Convert a BIMIntent into an AgentBridge JSON action dict.

        Returns None if the intent cannot be routed.
        """
        if intent.intent_type == IntentType.UNKNOWN:
            return None

        action = ACTION_MAP.get(intent.intent_type)
        if not action:
            logger.warning("No action mapping for intent: %s", intent.intent_type)
            return None

        builder = getattr(self, f"_build_{action}", None)
        if builder:
            return builder(intent)

        # Generic fallback
        return {"action": action}

    def route_json(self, intent: BIMIntent) -> str | None:
        """Route and return as JSON string for AgentBridge.executeJson()."""
        action_dict = self.route(intent)
        if action_dict is None:
            return None
        return json.dumps(action_dict, ensure_ascii=False)

    # ---- Builder methods for each of the 13 actions ----

    def _build_query_by_type(self, intent: BIMIntent) -> dict:
        return {
            "action": "query_by_type",
            "type": intent.entity_type or "Generic",
        }

    def _build_query_by_name(self, intent: BIMIntent) -> dict:
        return {
            "action": "query_by_name",
            "name": intent.entity_name or intent.entity_id or "",
        }

    def _build_get_position(self, intent: BIMIntent) -> dict:
        return {
            "action": "get_position",
            "id": intent.entity_id or intent.entity_name or "",
        }

    def _build_get_nearby(self, intent: BIMIntent) -> dict:
        return {
            "action": "get_nearby",
            "id": intent.entity_id or intent.entity_name or "",
            "radius": intent.radius,
        }

    def _build_get_scene_info(self, intent: BIMIntent) -> dict:
        return {"action": "get_scene_info"}

    def _build_move(self, intent: BIMIntent) -> dict:
        pos = intent.position or (0.0, 0.0, 0.0)
        return {
            "action": "move",
            "id": intent.entity_id or intent.entity_name or "",
            "position": list(pos),
        }

    def _build_rotate(self, intent: BIMIntent) -> dict:
        rot = intent.rotation or (0.0, 0.0, 90.0)
        return {
            "action": "rotate",
            "id": intent.entity_id or intent.entity_name or "",
            "rotation": list(rot),
        }

    def _build_resize(self, intent: BIMIntent) -> dict:
        dims = intent.dimensions or (1.0, 1.0, 1.0)
        return {
            "action": "resize",
            "id": intent.entity_id or intent.entity_name or "",
            "dimensions": list(dims),
        }

    def _build_add(self, intent: BIMIntent) -> dict:
        etype = intent.entity_type or "Generic"
        pos = intent.position or (0.0, 0.0, 0.0)
        eid = intent.entity_id or f"{etype.lower()}-{uuid.uuid4().hex[:6]}"
        name = intent.entity_name or f"New-{etype}"

        return {
            "action": "add",
            "id": eid,
            "type": etype,
            "name": name,
            "position": list(pos),
        }

    def _build_delete(self, intent: BIMIntent) -> dict:
        return {
            "action": "delete",
            "id": intent.entity_id or intent.entity_name or "",
        }

    def _build_connect(self, intent: BIMIntent) -> dict:
        return {
            "action": "connect",
            "from": intent.entity_id or "",
            "to": intent.target_id or "",
        }

    def _build_cost_delta(self, intent: BIMIntent) -> dict:
        return {"action": "cost_delta"}

    def _build_schedule_impact(self, intent: BIMIntent) -> dict:
        return {"action": "schedule_impact"}
