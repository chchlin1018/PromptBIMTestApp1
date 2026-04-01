"""Tests for IntentRouter — BIMIntent to AgentBridge JSON action mapping."""
import json
import pytest
from promptbim.ai.nl_parser import BIMIntent, IntentType
from promptbim.ai.intent_router import IntentRouter, ACTION_MAP


@pytest.fixture
def router():
    return IntentRouter()


class TestRouteActions:
    def test_query_by_type(self, router):
        intent = BIMIntent(intent_type=IntentType.QUERY_TYPE, entity_type="Wall")
        result = router.route(intent)
        assert result == {"action": "query_by_type", "type": "Wall"}

    def test_query_by_name(self, router):
        intent = BIMIntent(intent_type=IntentType.QUERY_NAME, entity_name="main-chiller")
        result = router.route(intent)
        assert result == {"action": "query_by_name", "name": "main-chiller"}

    def test_move(self, router):
        intent = BIMIntent(
            intent_type=IntentType.MOVE,
            entity_id="chiller-1",
            position=(10.0, 20.0, 0.0),
        )
        result = router.route(intent)
        assert result["action"] == "move"
        assert result["id"] == "chiller-1"
        assert result["position"] == [10.0, 20.0, 0.0]

    def test_rotate(self, router):
        intent = BIMIntent(
            intent_type=IntentType.ROTATE,
            entity_id="pump-1",
            rotation=(0.0, 0.0, 45.0),
        )
        result = router.route(intent)
        assert result["action"] == "rotate"
        assert result["rotation"] == [0.0, 0.0, 45.0]

    def test_create_add(self, router):
        intent = BIMIntent(
            intent_type=IntentType.CREATE,
            entity_type="Column",
            position=(5.0, 5.0, 0.0),
        )
        result = router.route(intent)
        assert result["action"] == "add"
        assert result["type"] == "Column"
        assert result["position"] == [5.0, 5.0, 0.0]
        assert "id" in result

    def test_delete(self, router):
        intent = BIMIntent(intent_type=IntentType.DELETE, entity_id="wall-3")
        result = router.route(intent)
        assert result == {"action": "delete", "id": "wall-3"}

    def test_connect(self, router):
        intent = BIMIntent(
            intent_type=IntentType.CONNECT,
            entity_id="pipe-1",
            target_id="chiller-1",
        )
        result = router.route(intent)
        assert result == {"action": "connect", "from": "pipe-1", "to": "chiller-1"}

    def test_get_scene_info(self, router):
        intent = BIMIntent(intent_type=IntentType.GET_SCENE_INFO)
        result = router.route(intent)
        assert result == {"action": "get_scene_info"}

    def test_cost_delta(self, router):
        intent = BIMIntent(intent_type=IntentType.COST)
        result = router.route(intent)
        assert result == {"action": "cost_delta"}

    def test_get_nearby(self, router):
        intent = BIMIntent(
            intent_type=IntentType.GET_NEARBY,
            entity_id="chiller-1",
            radius=15.0,
        )
        result = router.route(intent)
        assert result["action"] == "get_nearby"
        assert result["radius"] == 15.0


class TestRouteEdgeCases:
    def test_unknown_returns_none(self, router):
        intent = BIMIntent(intent_type=IntentType.UNKNOWN)
        assert router.route(intent) is None

    def test_route_json_output(self, router):
        intent = BIMIntent(intent_type=IntentType.GET_SCENE_INFO)
        result = router.route_json(intent)
        assert result is not None
        parsed = json.loads(result)
        assert parsed["action"] == "get_scene_info"

    def test_route_json_unknown_returns_none(self, router):
        intent = BIMIntent(intent_type=IntentType.UNKNOWN)
        assert router.route_json(intent) is None

    def test_move_no_position_defaults(self, router):
        intent = BIMIntent(intent_type=IntentType.MOVE, entity_id="x-1")
        result = router.route(intent)
        assert result["position"] == [0.0, 0.0, 0.0]

    def test_resize(self, router):
        intent = BIMIntent(
            intent_type=IntentType.RESIZE,
            entity_id="wall-1",
            dimensions=(2.0, 3.0, 4.0),
        )
        result = router.route(intent)
        assert result["action"] == "resize"
        assert result["dimensions"] == [2.0, 3.0, 4.0]


class TestActionMap:
    def test_all_13_actions_mapped(self):
        """All 13 AgentBridge actions must be in ACTION_MAP."""
        expected_actions = {
            "query_by_type", "query_by_name", "get_position", "get_nearby",
            "get_scene_info", "move", "rotate", "resize", "add", "delete",
            "connect", "cost_delta", "schedule_impact",
        }
        actual = set(ACTION_MAP.values())
        assert expected_actions == actual
