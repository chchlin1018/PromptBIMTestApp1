"""Tests for plugin architecture."""

from __future__ import annotations

from promptbim.plugins.base import PluginInfo, PluginRegistry, PluginType, register_plugin


class TestPluginRegistry:
    """Test PluginRegistry CRUD operations."""

    def setup_method(self):
        PluginRegistry.reset()

    def test_register_and_get(self):
        PluginRegistry.register("test_plugin", PluginType.PARSER, lambda: None, "A test")
        info = PluginRegistry.get("test_plugin")
        assert info is not None
        assert info.name == "test_plugin"
        assert info.plugin_type == PluginType.PARSER

    def test_list_by_type(self):
        PluginRegistry.register("p1", PluginType.AGENT, lambda: None)
        PluginRegistry.register("p2", PluginType.PARSER, lambda: None)
        PluginRegistry.register("p3", PluginType.AGENT, lambda: None)

        agents = PluginRegistry.list_plugins(PluginType.AGENT)
        assert len(agents) == 2

        parsers = PluginRegistry.list_plugins(PluginType.PARSER)
        assert len(parsers) == 1

    def test_discover_returns_sorted_by_priority(self):
        PluginRegistry.register("low", PluginType.CODE_RULE, lambda: None, priority=200)
        PluginRegistry.register("high", PluginType.CODE_RULE, lambda: None, priority=50)

        results = PluginRegistry.discover(PluginType.CODE_RULE)
        assert results[0].name == "high"
        assert results[1].name == "low"

    def test_execute(self):
        PluginRegistry.register("adder", PluginType.PARSER, lambda a, b: a + b)
        result = PluginRegistry.execute("adder", 3, 4)
        assert result == 7

    def test_count(self):
        assert PluginRegistry.count() == 0
        PluginRegistry.register("p1", PluginType.AGENT, lambda: None)
        assert PluginRegistry.count() == 1

    def test_clear(self):
        PluginRegistry.register("p1", PluginType.AGENT, lambda: None)
        PluginRegistry.clear()
        assert PluginRegistry.count() == 0


class TestRegisterDecorator:
    """Test @register_plugin decorator."""

    def setup_method(self):
        PluginRegistry.reset()

    def test_decorator_registers(self):
        @register_plugin("my_parser", PluginType.PARSER, description="A parser")
        def my_func():
            return "parsed"

        info = PluginRegistry.get("my_parser")
        assert info is not None
        assert info.description == "A parser"
        assert info.func() == "parsed"

    def test_decorator_preserves_function(self):
        @register_plugin("test", PluginType.AGENT)
        def original():
            return 42

        assert original() == 42


class TestPluginTypes:
    """Test plugin type enum."""

    def test_plugin_types(self):
        assert PluginType.AGENT == "agent"
        assert PluginType.PARSER == "parser"
        assert PluginType.CODE_RULE == "code_rule"

    def test_plugin_info_repr(self):
        info = PluginInfo("test", PluginType.AGENT, lambda: None)
        assert "agent" in repr(info)
        assert "test" in repr(info)
