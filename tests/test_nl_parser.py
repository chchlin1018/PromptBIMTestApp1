"""Tests for NLParser — natural language to BIM intent parsing."""
import pytest
from promptbim.ai.nl_parser import NLParser, BIMIntent, IntentType, ENTITY_NAME_MAP


@pytest.fixture
def parser():
    """Parser with LLM disabled (regex-only)."""
    return NLParser(use_llm=False)


class TestParseCreate:
    def test_create_wall_chinese(self, parser):
        intent = parser.parse("建立一面牆")
        assert intent.intent_type == IntentType.CREATE
        assert intent.entity_type == "Wall"
        assert intent.is_valid

    def test_create_column_english(self, parser):
        intent = parser.parse("create a column")
        assert intent.intent_type == IntentType.CREATE
        assert intent.entity_type == "Column"

    def test_create_with_position(self, parser):
        intent = parser.parse("add a chiller at (10, 20, 0)")
        assert intent.intent_type == IntentType.CREATE
        assert intent.entity_type == "Chiller"
        assert intent.position == (10.0, 20.0, 0.0)

    def test_create_unknown_type(self, parser):
        intent = parser.parse("create something weird")
        assert intent.intent_type == IntentType.CREATE
        assert intent.entity_type == "Generic"


class TestParseDelete:
    def test_delete_by_id(self, parser):
        intent = parser.parse("刪除 chiller-1")
        assert intent.intent_type == IntentType.DELETE
        assert intent.entity_id == "chiller-1"

    def test_delete_english(self, parser):
        intent = parser.parse("remove wall-2")
        assert intent.intent_type == IntentType.DELETE
        assert intent.entity_id == "wall-2"


class TestParseMove:
    def test_move_with_coords(self, parser):
        intent = parser.parse("移動 pump-1 到 (5, 10, 0)")
        assert intent.intent_type == IntentType.MOVE
        assert intent.entity_id == "pump-1"
        assert intent.position == (5.0, 10.0, 0.0)

    def test_move_english(self, parser):
        intent = parser.parse("move chiller-1 to (1, 2, 3)")
        assert intent.intent_type == IntentType.MOVE
        assert intent.entity_id == "chiller-1"
        assert intent.position == (1.0, 2.0, 3.0)


class TestParseQuery:
    def test_query_type_chinese(self, parser):
        intent = parser.parse("查詢所有的牆")
        assert intent.intent_type == IntentType.QUERY_TYPE
        assert intent.entity_type == "Wall"

    def test_query_by_name(self, parser):
        intent = parser.parse("find main-entrance")
        assert intent.intent_type in (IntentType.QUERY_NAME, IntentType.QUERY_TYPE)

    def test_scene_info(self, parser):
        intent = parser.parse("show scene info")
        assert intent.intent_type == IntentType.GET_SCENE_INFO


class TestParseEdgeCases:
    def test_empty_string(self, parser):
        intent = parser.parse("")
        assert intent.intent_type == IntentType.UNKNOWN
        assert not intent.is_valid

    def test_whitespace_only(self, parser):
        intent = parser.parse("   ")
        assert intent.intent_type == IntentType.UNKNOWN

    def test_special_characters(self, parser):
        intent = parser.parse("!@#$%^&*()")
        assert intent.intent_type == IntentType.UNKNOWN

    def test_rotate_with_angle(self, parser):
        intent = parser.parse("旋轉 pump-1 45度")
        assert intent.intent_type == IntentType.ROTATE
        assert intent.rotation == (0.0, 0.0, 45.0)

    def test_cost_query(self, parser):
        intent = parser.parse("成本是多少？")
        assert intent.intent_type == IntentType.COST

    def test_nearby_query(self, parser):
        intent = parser.parse("附近 chiller-1 5m")
        assert intent.intent_type == IntentType.GET_NEARBY
        assert intent.radius == 5.0

    def test_connect(self, parser):
        intent = parser.parse("連接 pipe-1 和 chiller-1")
        assert intent.intent_type == IntentType.CONNECT


class TestEntityNameMap:
    def test_all_22_types_covered(self):
        expected = {
            "Wall", "Slab", "Column", "Beam", "Roof", "Door", "Window",
            "Stair", "Elevator", "Ramp", "Chiller", "CoolingTower", "AHU",
            "Pump", "Fan", "Pipe", "Duct", "Cable", "Valve", "Sensor",
            "ExhaustStack",
        }
        actual = set(ENTITY_NAME_MAP.values())
        for e in expected:
            assert e in actual, f"Missing entity type: {e}"

    def test_chinese_mapping(self):
        assert ENTITY_NAME_MAP["冰水主機"] == "Chiller"
        assert ENTITY_NAME_MAP["柱子"] == "Column"
        assert ENTITY_NAME_MAP["風管"] == "Duct"


class TestBIMIntent:
    def test_is_valid_threshold(self):
        valid = BIMIntent(intent_type=IntentType.CREATE, confidence=0.5)
        assert valid.is_valid

        invalid = BIMIntent(intent_type=IntentType.CREATE, confidence=0.2)
        assert not invalid.is_valid

        unknown = BIMIntent(intent_type=IntentType.UNKNOWN, confidence=0.9)
        assert not unknown.is_valid
