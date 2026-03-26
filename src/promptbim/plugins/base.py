"""Plugin architecture base — registry and decorator for extensible components."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any

from promptbim.debug import get_logger

logger = get_logger("plugins.base")


class PluginType(str, Enum):
    AGENT = "agent"
    PARSER = "parser"
    CODE_RULE = "code_rule"


class PluginInfo:
    """Metadata for a registered plugin."""

    __slots__ = ("name", "plugin_type", "description", "func", "priority")

    def __init__(
        self,
        name: str,
        plugin_type: PluginType,
        func: Any,
        description: str = "",
        priority: int = 100,
    ) -> None:
        self.name = name
        self.plugin_type = plugin_type
        self.func = func
        self.description = description
        self.priority = priority

    def __repr__(self) -> str:
        return f"<Plugin {self.plugin_type.value}:{self.name}>"


class PluginRegistry:
    """Central plugin registry — discovers, stores, and retrieves plugins."""

    _plugins: dict[str, PluginInfo] = {}

    @classmethod
    def register(
        cls,
        name: str,
        plugin_type: PluginType,
        func: Any,
        description: str = "",
        priority: int = 100,
    ) -> None:
        info = PluginInfo(name, plugin_type, func, description, priority)
        cls._plugins[name] = info
        logger.debug("Registered plugin: %s (%s)", name, plugin_type.value)

    @classmethod
    def get(cls, name: str) -> PluginInfo | None:
        return cls._plugins.get(name)

    @classmethod
    def list_plugins(cls, plugin_type: PluginType | None = None) -> list[PluginInfo]:
        plugins = list(cls._plugins.values())
        if plugin_type is not None:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]
        return sorted(plugins, key=lambda p: p.priority)

    @classmethod
    def discover(cls, plugin_type: PluginType) -> list[PluginInfo]:
        """Return all plugins of the given type, sorted by priority."""
        return cls.list_plugins(plugin_type)

    @classmethod
    def execute(cls, name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a registered plugin by name."""
        info = cls._plugins.get(name)
        if info is None:
            raise KeyError(f"Plugin '{name}' not found")
        return info.func(*args, **kwargs)

    @classmethod
    def count(cls) -> int:
        return len(cls._plugins)

    @classmethod
    def clear(cls) -> None:
        cls._plugins.clear()

    @classmethod
    def reset(cls) -> None:
        cls._plugins = {}


def register_plugin(
    name: str,
    plugin_type: PluginType,
    description: str = "",
    priority: int = 100,
) -> Callable:
    """Decorator to register a function/class as a plugin.

    Usage::

        @register_plugin("geojson_parser", PluginType.PARSER, description="GeoJSON land parser")
        def parse_geojson(file_path):
            ...
    """

    def decorator(func: Any) -> Any:
        PluginRegistry.register(name, plugin_type, func, description, priority)
        return func

    return decorator
