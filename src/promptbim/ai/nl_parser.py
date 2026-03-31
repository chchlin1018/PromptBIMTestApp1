"""NLParser — Natural language to BIM intent parser.

Two-stage parsing:
1. Regex-based fast path for common patterns (no API call)
2. Claude LLM fallback for complex/ambiguous inputs
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from promptbim.debug import get_logger

logger = get_logger("ai.nl_parser")


class IntentType(Enum):
    """BIM operation intents matching AgentBridge actions."""
    CREATE = "create"
    DELETE = "delete"
    MOVE = "move"
    ROTATE = "rotate"
    RESIZE = "resize"
    QUERY = "query"
    QUERY_TYPE = "query_type"
    QUERY_NAME = "query_name"
    GET_POSITION = "get_position"
    GET_NEARBY = "get_nearby"
    GET_SCENE_INFO = "get_scene_info"
    CONNECT = "connect"
    COST = "cost"
    SCHEDULE = "schedule"
    UNKNOWN = "unknown"


# Mapping from Chinese/English entity names to C++ EntityType strings
ENTITY_NAME_MAP: dict[str, str] = {
    # Chinese
    "牆": "Wall", "牆壁": "Wall", "墙": "Wall", "墙壁": "Wall",
    "板": "Slab", "樓板": "Slab", "楼板": "Slab", "地板": "Slab",
    "柱": "Column", "柱子": "Column",
    "梁": "Beam", "橫梁": "Beam", "横梁": "Beam",
    "屋頂": "Roof", "屋顶": "Roof", "天花板": "Roof",
    "門": "Door", "门": "Door",
    "窗": "Window", "窗戶": "Window", "窗户": "Window",
    "樓梯": "Stair", "楼梯": "Stair",
    "電梯": "Elevator", "电梯": "Elevator",
    "坡道": "Ramp", "斜坡": "Ramp",
    "冰水主機": "Chiller", "冰水机": "Chiller", "冷水機": "Chiller",
    "冷卻塔": "CoolingTower", "冷却塔": "CoolingTower", "冷卻水塔": "CoolingTower",
    "空調箱": "AHU", "空调箱": "AHU", "空調": "AHU",
    "泵": "Pump", "水泵": "Pump", "幫浦": "Pump",
    "風機": "Fan", "风机": "Fan", "風扇": "Fan",
    "管": "Pipe", "管道": "Pipe", "水管": "Pipe",
    "風管": "Duct", "风管": "Duct",
    "電纜": "Cable", "电缆": "Cable", "線纜": "Cable",
    "閥": "Valve", "阀": "Valve", "閥門": "Valve",
    "感測器": "Sensor", "传感器": "Sensor", "感應器": "Sensor",
    "排氣管": "ExhaustStack", "排气管": "ExhaustStack",
    # English
    "wall": "Wall", "slab": "Slab", "column": "Column", "beam": "Beam",
    "roof": "Roof", "door": "Door", "window": "Window", "stair": "Stair",
    "elevator": "Elevator", "ramp": "Ramp", "chiller": "Chiller",
    "cooling tower": "CoolingTower", "coolingtower": "CoolingTower",
    "ahu": "AHU", "pump": "Pump", "fan": "Fan",
    "pipe": "Pipe", "duct": "Duct", "cable": "Cable",
    "valve": "Valve", "sensor": "Sensor",
    "exhaust stack": "ExhaustStack", "exhauststack": "ExhaustStack",
}


@dataclass
class BIMIntent:
    """Parsed intent from natural language."""
    intent_type: IntentType
    entity_type: str | None = None  # C++ EntityType string
    entity_id: str | None = None
    entity_name: str | None = None
    target_id: str | None = None
    position: tuple[float, float, float] | None = None
    dimensions: tuple[float, float, float] | None = None
    rotation: tuple[float, float, float] | None = None
    radius: float = 10.0
    raw_text: str = ""
    confidence: float = 0.0
    params: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return self.intent_type != IntentType.UNKNOWN and self.confidence > 0.3


class NLParser:
    """Two-stage NL parser: regex fast path + Claude LLM fallback."""

    # Regex patterns for intent detection
    _CREATE_PATTERNS = [
        re.compile(r"(?:建立|新增|加|創建|create|add|build|make)\s*(?:一[個面道根台扇]?\s*)?(.+)", re.I),
    ]
    _DELETE_PATTERNS = [
        re.compile(r"(?:刪除|移除|拆除|delete|remove|destroy)\s*(.+)", re.I),
    ]
    _MOVE_PATTERNS = [
        re.compile(r"(?:移動|搬|移|move)\s*(.+?)(?:到|至|to)\s*(.+)", re.I),
    ]
    _ROTATE_PATTERNS = [
        re.compile(r"(?:旋轉|轉|rotate|turn)\s*(.+?)(?:\s+(\d+)\s*(?:度|deg|°)?)?$", re.I),
    ]
    _RESIZE_PATTERNS = [
        re.compile(r"(?:調整|resize|scale|改變大小)\s*(.+?)(?:到|to)\s*(.+)", re.I),
    ]
    _QUERY_PATTERNS = [
        re.compile(r"(?:查詢|搜尋|找|查|列出|query|find|search|list|show)\s*(?:所有的?\s*)?(.+)", re.I),
    ]
    _POSITION_PATTERNS = [
        re.compile(r"(?:位置|在哪|哪裡|where|position)\s*(?:of\s+|是\s*)?(.+)", re.I),
    ]
    _NEARBY_PATTERNS = [
        re.compile(r"(?:附近|周圍|nearby|near|around)\s*(.+?)(?:\s+(\d+\.?\d*)\s*(?:m|公尺|米)?)?$", re.I),
    ]
    _COST_PATTERNS = [
        re.compile(r"(?:成本|費用|花費|多少錢|cost|price|how much|budget)", re.I),
    ]
    _SCENE_PATTERNS = [
        re.compile(r"(?:場景|概覽|overview|scene|status|info)", re.I),
    ]
    _CONNECT_PATTERNS = [
        re.compile(r"(?:連接|接|connect|link)\s*(.+?)(?:和|與|to|and|with)\s*(.+)", re.I),
    ]

    # Coordinate extraction
    _COORD_PATTERN = re.compile(
        r"[(\[\s]*(-?\d+\.?\d*)\s*[,，\s]\s*(-?\d+\.?\d*)\s*[,，\s]\s*(-?\d+\.?\d*)\s*[)\]\s]*"
    )
    _COORD_2D_PATTERN = re.compile(
        r"[(\[\s]*(-?\d+\.?\d*)\s*[,，\s]\s*(-?\d+\.?\d*)\s*[)\]\s]*"
    )

    def __init__(self, use_llm: bool = True) -> None:
        self._use_llm = use_llm
        self._llm_client = None

    def parse(self, text: str) -> BIMIntent:
        """Parse natural language text into a BIMIntent.

        Tries regex first; falls back to LLM if confidence is low.
        """
        text = text.strip()
        if not text:
            return BIMIntent(intent_type=IntentType.UNKNOWN, raw_text=text)

        # Stage 1: Regex fast path
        intent = self._regex_parse(text)
        if intent.is_valid:
            logger.debug("Regex parse: %s (conf=%.2f)", intent.intent_type.value, intent.confidence)
            return intent

        # Stage 2: LLM fallback
        if self._use_llm:
            llm_intent = self._llm_parse(text)
            if llm_intent.is_valid:
                logger.debug("LLM parse: %s (conf=%.2f)", llm_intent.intent_type.value, llm_intent.confidence)
                return llm_intent

        logger.debug("Parse failed for: %s", text[:50])
        return BIMIntent(intent_type=IntentType.UNKNOWN, raw_text=text, confidence=0.1)

    def _regex_parse(self, text: str) -> BIMIntent:
        """Try to parse using regex patterns."""
        lower = text.lower().strip()

        # Scene info (check first — no entity needed)
        for pat in self._SCENE_PATTERNS:
            if pat.search(lower):
                return BIMIntent(intent_type=IntentType.GET_SCENE_INFO, raw_text=text, confidence=0.8)

        # Cost
        for pat in self._COST_PATTERNS:
            if pat.search(lower):
                return BIMIntent(intent_type=IntentType.COST, raw_text=text, confidence=0.8)

        # Create
        for pat in self._CREATE_PATTERNS:
            m = pat.search(text)
            if m:
                rest = m.group(1).strip()
                etype = self._extract_entity_type(rest)
                coords = self._extract_coords(text)
                dims = self._extract_dimensions(text)
                return BIMIntent(
                    intent_type=IntentType.CREATE,
                    entity_type=etype or "Generic",
                    position=coords,
                    dimensions=dims,
                    raw_text=text,
                    confidence=0.85 if etype else 0.5,
                )

        # Delete
        for pat in self._DELETE_PATTERNS:
            m = pat.search(text)
            if m:
                rest = m.group(1).strip()
                etype = self._extract_entity_type(rest)
                eid = self._extract_entity_id(rest)
                return BIMIntent(
                    intent_type=IntentType.DELETE,
                    entity_type=etype,
                    entity_id=eid,
                    entity_name=rest if not eid else None,
                    raw_text=text,
                    confidence=0.8,
                )

        # Move
        for pat in self._MOVE_PATTERNS:
            m = pat.search(text)
            if m:
                subject = m.group(1).strip()
                dest = m.group(2).strip()
                etype = self._extract_entity_type(subject)
                eid = self._extract_entity_id(subject)
                coords = self._extract_coords(dest)
                return BIMIntent(
                    intent_type=IntentType.MOVE,
                    entity_type=etype,
                    entity_id=eid,
                    entity_name=subject if not eid else None,
                    position=coords,
                    raw_text=text,
                    confidence=0.8 if coords else 0.5,
                )

        # Rotate
        for pat in self._ROTATE_PATTERNS:
            m = pat.search(text)
            if m:
                subject = m.group(1).strip()
                angle_str = m.group(2) if m.lastindex >= 2 else None
                eid = self._extract_entity_id(subject)
                angle = float(angle_str) if angle_str else 90.0
                return BIMIntent(
                    intent_type=IntentType.ROTATE,
                    entity_id=eid,
                    entity_name=subject if not eid else None,
                    rotation=(0.0, 0.0, angle),
                    raw_text=text,
                    confidence=0.75,
                )

        # Resize
        for pat in self._RESIZE_PATTERNS:
            m = pat.search(text)
            if m:
                subject = m.group(1).strip()
                target = m.group(2).strip()
                eid = self._extract_entity_id(subject)
                dims = self._extract_coords(target)
                return BIMIntent(
                    intent_type=IntentType.RESIZE,
                    entity_id=eid,
                    entity_name=subject if not eid else None,
                    dimensions=dims,
                    raw_text=text,
                    confidence=0.7 if dims else 0.4,
                )

        # Connect
        for pat in self._CONNECT_PATTERNS:
            m = pat.search(text)
            if m:
                e1 = m.group(1).strip()
                e2 = m.group(2).strip()
                return BIMIntent(
                    intent_type=IntentType.CONNECT,
                    entity_id=self._extract_entity_id(e1) or e1,
                    target_id=self._extract_entity_id(e2) or e2,
                    raw_text=text,
                    confidence=0.8,
                )

        # Nearby
        for pat in self._NEARBY_PATTERNS:
            m = pat.search(text)
            if m:
                subject = m.group(1).strip()
                radius = float(m.group(2)) if m.lastindex >= 2 and m.group(2) else 10.0
                eid = self._extract_entity_id(subject)
                return BIMIntent(
                    intent_type=IntentType.GET_NEARBY,
                    entity_id=eid,
                    entity_name=subject if not eid else None,
                    radius=radius,
                    raw_text=text,
                    confidence=0.75,
                )

        # Position
        for pat in self._POSITION_PATTERNS:
            m = pat.search(text)
            if m:
                subject = m.group(1).strip()
                eid = self._extract_entity_id(subject)
                return BIMIntent(
                    intent_type=IntentType.GET_POSITION,
                    entity_id=eid,
                    entity_name=subject if not eid else None,
                    raw_text=text,
                    confidence=0.75,
                )

        # Query (general — check last to avoid false positives)
        for pat in self._QUERY_PATTERNS:
            m = pat.search(text)
            if m:
                rest = m.group(1).strip()
                etype = self._extract_entity_type(rest)
                if etype:
                    return BIMIntent(
                        intent_type=IntentType.QUERY_TYPE,
                        entity_type=etype,
                        raw_text=text,
                        confidence=0.8,
                    )
                return BIMIntent(
                    intent_type=IntentType.QUERY_NAME,
                    entity_name=rest,
                    raw_text=text,
                    confidence=0.6,
                )

        return BIMIntent(intent_type=IntentType.UNKNOWN, raw_text=text, confidence=0.1)

    def _llm_parse(self, text: str) -> BIMIntent:
        """Use Claude to parse ambiguous natural language."""
        try:
            from promptbim.ai.claude_client import get_claude_client
            client = get_claude_client()
            result = client.parse_intent(text)
            if result:
                return result
        except Exception as e:
            logger.warning("LLM parse failed: %s", e)
        return BIMIntent(intent_type=IntentType.UNKNOWN, raw_text=text, confidence=0.1)

    def _extract_entity_type(self, text: str) -> str | None:
        """Extract entity type from text using the name map."""
        lower = text.lower().strip()
        # Try exact match first
        if lower in ENTITY_NAME_MAP:
            return ENTITY_NAME_MAP[lower]
        # Try substring match
        for name, etype in sorted(ENTITY_NAME_MAP.items(), key=lambda x: -len(x[0])):
            if name in lower:
                return etype
        return None

    def _extract_entity_id(self, text: str) -> str | None:
        """Extract an entity ID like 'chiller-1' or 'wall-2'."""
        m = re.search(r"([a-zA-Z][\w-]*-\d+)", text)
        return m.group(1) if m else None

    def _extract_coords(self, text: str) -> tuple[float, float, float] | None:
        """Extract 3D coordinates from text."""
        m = self._COORD_PATTERN.search(text)
        if m:
            return (float(m.group(1)), float(m.group(2)), float(m.group(3)))
        m = self._COORD_2D_PATTERN.search(text)
        if m:
            return (float(m.group(1)), float(m.group(2)), 0.0)
        return None

    def _extract_dimensions(self, text: str) -> tuple[float, float, float] | None:
        """Extract dimensions specified with '大小' or 'size'."""
        m = re.search(
            r"(?:大小|尺寸|size|dims?)\s*[=:：]?\s*"
            r"[(\[\s]*(-?\d+\.?\d*)\s*[x×,，\s]\s*(-?\d+\.?\d*)\s*[x×,，\s]\s*(-?\d+\.?\d*)",
            text, re.I
        )
        if m:
            return (float(m.group(1)), float(m.group(2)), float(m.group(3)))
        return None
