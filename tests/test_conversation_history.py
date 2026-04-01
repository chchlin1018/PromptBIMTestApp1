"""Tests for ConversationHistory — rolling context management."""
import pytest
from promptbim.ai.conversation_history import ConversationHistory, Message


class TestMessage:
    def test_to_api_dict(self):
        msg = Message(role="user", content="hello")
        d = msg.to_api_dict()
        assert d == {"role": "user", "content": "hello"}

    def test_metadata(self):
        msg = Message(role="assistant", content="hi", metadata={"ts": 123})
        assert msg.metadata["ts"] == 123


class TestAddMessages:
    def test_add_user(self):
        h = ConversationHistory()
        h.add_user("hello")
        assert h.message_count == 1
        msgs = h.get_messages()
        assert msgs[0]["role"] == "user"
        assert msgs[0]["content"] == "hello"

    def test_add_assistant(self):
        h = ConversationHistory()
        h.add_assistant("I can help")
        assert h.message_count == 1
        msgs = h.get_messages()
        assert msgs[0]["role"] == "assistant"

    def test_add_system_context(self):
        h = ConversationHistory()
        h.add_system_context("Scene has 5 entities")
        msgs = h.get_messages()
        assert "[System Context]" in msgs[0]["content"]

    def test_multiple_messages(self):
        h = ConversationHistory()
        h.add_user("query all walls")
        h.add_assistant("Found 3 walls")
        h.add_user("delete wall-1")
        assert h.message_count == 3


class TestTrimming:
    def test_trim_by_message_count(self):
        h = ConversationHistory(max_messages=3)
        for i in range(10):
            h.add_user(f"msg {i}")
        assert h.message_count == 3
        msgs = h.get_messages()
        assert "msg 7" in msgs[0]["content"]

    def test_trim_by_tokens(self):
        h = ConversationHistory(max_messages=100, max_tokens=10)
        for i in range(20):
            h.add_user("a" * 30)  # each ~10 tokens
        assert h.message_count <= 5
        assert h.estimated_tokens <= 25  # 2 msgs minimum kept, each ~10 tokens


class TestClearAndGet:
    def test_clear(self):
        h = ConversationHistory()
        h.add_user("hello")
        h.add_assistant("hi")
        h.clear()
        assert h.message_count == 0
        assert h.get_messages() == []

    def test_get_last_n(self):
        h = ConversationHistory()
        h.add_user("a")
        h.add_user("b")
        h.add_user("c")
        last2 = h.get_last_n(2)
        assert len(last2) == 2
        assert last2[0]["content"] == "b"
        assert last2[1]["content"] == "c"

    def test_get_last_n_more_than_available(self):
        h = ConversationHistory()
        h.add_user("only one")
        last5 = h.get_last_n(5)
        assert len(last5) == 1


class TestTokenEstimation:
    def test_estimated_tokens(self):
        h = ConversationHistory()
        h.add_user("hello world")  # 11 chars / 3 = ~3 tokens
        assert h.estimated_tokens >= 2

    def test_system_message_included(self):
        h = ConversationHistory(system_message="You are a BIM assistant" * 10)
        tokens_with_sys = h.estimated_tokens
        h2 = ConversationHistory()
        tokens_without = h2.estimated_tokens
        assert tokens_with_sys > tokens_without


class TestSystemMessage:
    def test_set_system_message(self):
        h = ConversationHistory(system_message="initial")
        assert h.system_message == "initial"
        h.system_message = "updated"
        assert h.system_message == "updated"

    def test_summary(self):
        h = ConversationHistory()
        h.add_user("test")
        summary = h.get_summary()
        assert "1 messages" in summary
        assert "tokens" in summary
