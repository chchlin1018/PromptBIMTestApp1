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
        cls,
        keywords: list[str],
        category: ComponentCategory | None = None,
        max_results: int = 20,
        scored: bool = False,
    ) -> list[ComponentDef]:
        """Search components by keywords (matches ai_keywords + names).

        D1-S1 enhancement: relevance scoring and max_results limit.

        When *category* is given, uses the inverted index for faster lookup.
        When *scored* is True, results are sorted by relevance score (descending).
        """
        if category is not None:
            candidates = [
                cls._components[cid]
                for cid in cls._by_category.get(category, [])
                if cid in cls._components
            ]
        else:
            candidates = list(cls._components.values())

        scored_results: list[tuple[int, ComponentDef]] = []
        for comp in candidates:
            searchable = " ".join(comp.ai_keywords + [comp.name_zh, comp.name_en, comp.id]).lower()
            score = sum(
                (3 if kw.lower() in comp.ai_keywords else 0)
                + (2 if kw.lower() in comp.name_zh.lower() or kw.lower() in comp.name_en.lower() else 0)
                + (1 if kw.lower() in searchable else 0)
                for kw in keywords
            )
            if score > 0:
                scored_results.append((score, comp))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        results = [comp for _, comp in scored_results[:max_results]]

        logger.debug(
            "search(%s, category=%s) -> %d results: %s",
            keywords,
            category,
            len(results),
            [r.id for r in results],
        )
        return results

    @classmethod
    def find_alternatives(
        cls,
        component_id: str,
        max_results: int = 5,
    ) -> list[ComponentDef]:
        """Find alternative components for a given component (D1-S1).

        Returns components in the same category with overlapping ai_keywords,
        excluding the original component, sorted by keyword overlap score.
        """
        original = cls._components.get(component_id)
        if original is None:
            return []

        orig_keywords = set(kw.lower() for kw in original.ai_keywords)
        candidates = [
            cls._components[cid]
            for cid in cls._by_category.get(original.category, [])
            if cid in cls._components and cid != component_id
        ]

        scored: list[tuple[int, ComponentDef]] = []
        for comp in candidates:
            comp_keywords = set(kw.lower() for kw in comp.ai_keywords)
            overlap = len(orig_keywords & comp_keywords)
            if overlap > 0:
                scored.append((overlap, comp))

        scored.sort(key=lambda x: x[0], reverse=True)
        alts = [comp for _, comp in scored[:max_results]]

        logger.debug(
            "find_alternatives(%s) -> %d alternatives: %s",
            component_id,
            len(alts),
            [a.id for a in alts],
        )
        return alts

    @classmethod
    def compare_components(
        cls,
        component_ids: list[str],
    ) -> dict:
        """Compare multiple components side by side (D1-S1 competitive analysis).

        Returns a dict with:
        - components: list of ComponentDef
        - comparison: list of dicts [{field, values}]
        - price_summary: cheapest / most expensive / avg
        """
        components = [cls._components[cid] for cid in component_ids if cid in cls._components]
        if not components:
            return {"components": [], "comparison": [], "price_summary": {}}

        comparison = []

        # Name comparison
        comparison.append({
            "field": "name_zh",
            "label": "名稱",
            "values": {c.id: c.name_zh for c in components},
        })
        comparison.append({
            "field": "category",
            "label": "分類",
            "values": {c.id: c.category.value for c in components},
        })
        comparison.append({
            "field": "ifc_class",
            "label": "IFC Class",
            "values": {c.id: c.ifc_class for c in components},
        })

        # Price comparison
        price_min_by_comp = {}
        price_max_by_comp = {}
        all_min_prices = []
        all_max_prices = []

        for comp in components:
            if comp.suppliers:
                prices = [s.price for s in comp.suppliers if s.price]
                if prices:
                    mins = [p.min_price for p in prices if p]
                    maxs = [p.max_price for p in prices if p]
                    if mins and maxs:
                        price_min_by_comp[comp.id] = min(mins)
                        price_max_by_comp[comp.id] = max(maxs)
                        all_min_prices.extend(mins)
                        all_max_prices.extend(maxs)
            else:
                price_min_by_comp[comp.id] = "N/A"
                price_max_by_comp[comp.id] = "N/A"

        comparison.append({
            "field": "price_min",
            "label": "最低價 (TWD)",
            "values": price_min_by_comp,
        })
        comparison.append({
            "field": "price_max",
            "label": "最高價 (TWD)",
            "values": price_max_by_comp,
        })

        # Supplier count
        comparison.append({
            "field": "supplier_count",
            "label": "供應商數",
            "values": {c.id: len(c.suppliers) for c in components},
        })

        # Key parameters
        all_param_keys = set()
        for comp in components:
            all_param_keys.update(comp.parameters.keys())
        for param_key in sorted(all_param_keys):
            comparison.append({
                "field": f"param_{param_key}",
                "label": f"參數: {param_key}",
                "values": {
                    c.id: str(c.parameters.get(param_key, {}).get("default", "N/A"))
                    for c in components
                },
            })

        price_summary = {}
        if all_min_prices:
            numeric_mins = [p for p in all_min_prices if isinstance(p, (int, float))]
            numeric_maxs = [p for p in all_max_prices if isinstance(p, (int, float))]
            if numeric_mins:
                price_summary = {
                    "cheapest_id": min(price_min_by_comp, key=lambda k: price_min_by_comp[k] if isinstance(price_min_by_comp[k], (int, float)) else float("inf")),
                    "most_expensive_id": max(price_max_by_comp, key=lambda k: price_max_by_comp[k] if isinstance(price_max_by_comp[k], (int, float)) else 0),
                    "avg_min_price": round(sum(numeric_mins) / len(numeric_mins), 0),
                    "avg_max_price": round(sum(numeric_maxs) / len(numeric_maxs), 0),
                }

        return {
            "components": components,
            "comparison": comparison,
            "price_summary": price_summary,
        }

    @classmethod
    def search_by_price_range(
        cls,
        min_price: float,
        max_price: float,
        category: ComponentCategory | None = None,
    ) -> list[ComponentDef]:
        """Filter components by price range (D1-S1).

        Returns components whose price range overlaps with [min_price, max_price].
        """
        candidates = (
            cls.list_by_category(category) if category else cls.all_components()
        )
        results = []
        for comp in candidates:
            for supplier in comp.suppliers:
                if supplier.price:
                    # Check overlap: comp [smin, smax] ∩ query [min, max]
                    smin = supplier.price.min_price or 0
                    smax = supplier.price.max_price or float("inf")
                    if smin <= max_price and smax >= min_price:
                        results.append(comp)
                        break
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
