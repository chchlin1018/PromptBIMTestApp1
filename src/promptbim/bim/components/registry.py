"""Component registry — central lookup for all building components."""

from __future__ import annotations

from promptbim.bim.components.base import ComponentCategory, ComponentDef
from promptbim.debug import get_logger

logger = get_logger("bim.components.registry")


class ComponentRegistry:
    """Building component registry — SSOT for all component definitions."""

    _components: dict[str, ComponentDef] = {}

    @classmethod
    def register(cls, component: ComponentDef) -> None:
        cls._components[component.id] = component

    @classmethod
    def register_many(cls, components: list[ComponentDef]) -> None:
        for comp in components:
            cls._components[comp.id] = comp

    @classmethod
    def get(cls, component_id: str) -> ComponentDef | None:
        return cls._components.get(component_id)

    @classmethod
    def search(
        cls, keywords: list[str], category: ComponentCategory | None = None
    ) -> list[ComponentDef]:
        """Search components by keywords (matches ai_keywords + names)."""
        results = []
        for comp in cls._components.values():
            if category and comp.category != category:
                continue
            searchable = " ".join(comp.ai_keywords + [comp.name_zh, comp.name_en, comp.id]).lower()
            if any(kw.lower() in searchable for kw in keywords):
                results.append(comp)
        logger.debug(
            "search(%s, category=%s) -> %d results: %s",
            keywords,
            category,
            len(results),
            [r.id for r in results],
        )
        return results

    @classmethod
    def list_by_category(cls, category: ComponentCategory) -> list[ComponentDef]:
        return [c for c in cls._components.values() if c.category == category]

    @classmethod
    def all_components(cls) -> list[ComponentDef]:
        return list(cls._components.values())

    @classmethod
    def count(cls) -> int:
        return len(cls._components)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered components (for testing)."""
        cls._components.clear()
