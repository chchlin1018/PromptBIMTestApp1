"""Tests for agents/base.py — JSON extraction and AgentResponse."""

from promptbim.agents.base import AgentResponse, _try_extract_json


class TestTryExtractJson:
    def test_plain_json(self):
        data = _try_extract_json('{"key": "value"}')
        assert data == {"key": "value"}

    def test_markdown_code_block(self):
        text = '```json\n{"a": 1}\n```'
        data = _try_extract_json(text)
        assert data == {"a": 1}

    def test_json_embedded_in_text(self):
        text = 'Here is the result:\n{"building_type": "residential"}\nDone.'
        data = _try_extract_json(text)
        assert data == {"building_type": "residential"}

    def test_no_json(self):
        assert _try_extract_json("hello world") is None

    def test_nested_braces(self):
        text = '{"outer": {"inner": 42}}'
        data = _try_extract_json(text)
        assert data == {"outer": {"inner": 42}}

    def test_empty_string(self):
        assert _try_extract_json("") is None


class TestAgentResponse:
    def test_ok_when_no_error(self):
        r = AgentResponse(text="hello")
        assert r.ok is True

    def test_not_ok_when_error(self):
        r = AgentResponse(error="something failed")
        assert r.ok is False

    def test_json_data(self):
        r = AgentResponse(text="test", json_data={"key": "val"})
        assert r.json_data == {"key": "val"}
