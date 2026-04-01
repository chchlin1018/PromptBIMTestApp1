"""Tests for ErrorHandler — graceful AI error recovery."""
import pytest
from promptbim.ai.nl_parser import BIMIntent, IntentType
from promptbim.ai.error_handler import ErrorHandler


@pytest.fixture
def handler():
    return ErrorHandler()


class TestParseFailure:
    def test_returns_suggestions(self, handler):
        msg = handler.handle_parse_failure("asdfghjkl")
        assert "無法理解" in msg
        assert "•" in msg

    def test_relevant_examples_for_create(self, handler):
        msg = handler.handle_parse_failure("create something")
        assert "•" in msg

    def test_relevant_examples_for_move(self, handler):
        msg = handler.handle_parse_failure("move things")
        assert "•" in msg

    def test_empty_input(self, handler):
        msg = handler.handle_parse_failure("")
        assert len(msg) > 0


class TestExecutionError:
    def test_not_found_error(self, handler):
        intent = BIMIntent(intent_type=IntentType.DELETE, entity_id="wall-99")
        msg = handler.handle_execution_error(intent, "Entity not found")
        assert "找不到" in msg

    def test_already_exists_error(self, handler):
        intent = BIMIntent(intent_type=IntentType.CREATE, entity_type="Wall")
        msg = handler.handle_execution_error(intent, "Entity already exists")
        assert "已存在" in msg

    def test_generic_error(self, handler):
        intent = BIMIntent(intent_type=IntentType.MOVE)
        msg = handler.handle_execution_error(intent, "Something broke")
        assert "錯誤" in msg
        assert "Something broke" in msg


class TestLowConfidence:
    def test_low_confidence_message(self, handler):
        intent = BIMIntent(intent_type=IntentType.CREATE, confidence=0.3)
        msg = handler.handle_low_confidence(intent)
        assert "不太確定" in msg
        assert "create" in msg


class TestMissingInfo:
    def test_missing_position_for_move(self, handler):
        intent = BIMIntent(intent_type=IntentType.MOVE, entity_id="x-1")
        msg = handler.handle_missing_info(intent)
        assert "位置座標" in msg

    def test_missing_type_for_create(self, handler):
        intent = BIMIntent(intent_type=IntentType.CREATE)
        msg = handler.handle_missing_info(intent)
        assert "元件類型" in msg

    def test_missing_id_for_delete(self, handler):
        intent = BIMIntent(intent_type=IntentType.DELETE)
        msg = handler.handle_missing_info(intent)
        assert "元件 ID" in msg

    def test_no_missing_when_complete(self, handler):
        intent = BIMIntent(
            intent_type=IntentType.CREATE,
            entity_type="Wall",
            position=(1, 2, 3),
        )
        msg = handler.handle_missing_info(intent)
        assert msg == ""
