"""Component registry — central lookup for all building components."""

from __future__ import annotations

from promptbim.bim.components.base import ComponentCategory, ComponentDef
from promptbim.debug import get_logger

logger = get_logger("bim.components.registry")


class ComponentRegistry:
    """Building component registry — SSOT for all component definitions.

    Uses an inverted index ``_by_category`` for O(1) category lookups and
    faster keyword search when a category filter is supplied.
    """

    _components: dict[str, ComponentDef] = {}
    _by_category: dict[ComponentCategory, list[str]] = {}

    @classmethod
    def _index_component(cls, comp: ComponentDef) -> None:
        cat_list = cls._by_category.setdefault(comp.category, [])
        if comp.id not in cat_list:
            cat_list.append(comp.id)

    @classmethod
    def register(cls, component: ComponentDef) -> None:
        cls._components[component.id] = component
        cls._index_component(component)

    @classmethod
    def register_many(cls, components: list[ComponentDef]) -> None:
        for comp in components:
            cls._components[comp.id] = comp
            cls._index_component(comp)

    @classmethod
    def get(cls, component_id: str) -> ComponentDef | None:
        return cls._components.get(component_id)

    @classmethod
    def search(
        cls, keywords: list[str], category: ComponentCategory | None = None
    ) -> list[ComponentDef]:
        """Search components by keywords (matches ai_keywords + names).

        When *category* is given, uses the inverted index for faster lookup.
        """
        if category is not None:
            candidates = [
                cls._components[cid]
                for cid in cls._by_category.get(category, [])
                if cid in cls._components
            ]
        else:
            candidates = list(cls._components.values())

        results = []
        for comp in candidates:
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
        """Return components in *category* via the inverted index."""
        return [
            cls._components[cid]
            for cid in cls._by_category.get(category, [])
            if cid in cls._components
        ]

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
        cls._by_category.clear()

    @classmethod
    def reset(cls) -> None:
        """Reset registry to a clean class-level dict (test isolation)."""
        cls._components = {}
        cls._by_category = {}
