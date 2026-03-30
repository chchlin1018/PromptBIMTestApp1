"""Cost Estimation engine — maps QTO items to unit prices and produces a cost summary."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from promptbim.bim.cost.qto import QTOItem, QuantityTakeOff
from promptbim.bim.cost.unit_prices_tw import (
    CATEGORY_LABELS,
    UNIT_PRICES_TWD,
)
from promptbim.debug import get_logger
from promptbim.schemas.plan import BuildingPlan

if TYPE_CHECKING:
    from promptbim.bim.monitoring.auto_placement import MonitorPlan

logger = get_logger("cost.estimator")


@dataclass
class CostLineItem:
    """A costed line item."""

    category: str
    name: str
    quantity: float
    unit: str
    unit_price_twd: float
    total_twd: float
    price_key: str = ""
    # D1-S1: vendor/supplier details
    vendor_name: str = ""
    vendor_brand: str = ""
    vendor_country: str = ""
    vendor_price_low: float = 0.0
    vendor_price_high: float = 0.0


@dataclass
class CostBreakdown:
    """Breakdown of cost by category."""

    category: str
    label: str
    cost_twd: float
    ratio: float = 0.0


@dataclass
class CostEstimate:
    """Complete cost estimation result.

    D1-S1: Adds chart_data() for visualization and vendor_summary for supplier breakdown.
    """

    project_name: str
    total_cost_twd: float
    total_floor_area_sqm: float
    cost_per_sqm_twd: float
    line_items: list[CostLineItem] = field(default_factory=list)
    breakdown: list[CostBreakdown] = field(default_factory=list)
    notes: str = "POC-grade estimate (+-30%), for early planning only"

    def to_dict(self) -> dict:
        return {
            "project": self.project_name,
            "total_cost_twd": round(self.total_cost_twd),
            "total_floor_area_sqm": round(self.total_floor_area_sqm, 1),
            "cost_per_sqm_twd": round(self.cost_per_sqm_twd),
            "breakdown": [
                {
                    "category": b.label,
                    "cost": round(b.cost_twd),
                    "ratio": round(b.ratio, 3),
                }
                for b in self.breakdown
            ],
            "notes": self.notes,
        }

    def chart_data(self) -> dict:
        """Return chart-ready data for cost visualization (D1-S1).

        Returns a dict with:
        - pie: [{label, value, color}] for category breakdown pie chart
        - bar: [{label, cost_low, cost_mid, cost_high}] for uncertainty bar chart
        - top_items: top 10 line items by cost for waterfall chart
        """
        # Category colors (consistent across charts)
        _COLORS = {
            "structure": "#4A90D9",
            "envelope": "#7B68EE",
            "interior": "#50C878",
            "door_window": "#FFD700",
            "mep": "#FF6B6B",
            "roof": "#FF8C00",
            "site": "#8B4513",
            "monitoring": "#20B2AA",
        }

        pie = [
            {
                "label": b.label,
                "value": round(b.cost_twd),
                "ratio": round(b.ratio, 3),
                "color": _COLORS.get(b.category, "#AAAAAA"),
            }
            for b in self.breakdown
        ]

        # Bar chart: cost range (±30% uncertainty)
        bar = [
            {
                "label": b.label,
                "cost_low": round(b.cost_twd * 0.7),
                "cost_mid": round(b.cost_twd),
                "cost_high": round(b.cost_twd * 1.3),
            }
            for b in self.breakdown
        ]

        # Top 10 items by cost
        top_items = sorted(self.line_items, key=lambda li: li.total_twd, reverse=True)[:10]

        return {
            "pie": pie,
            "bar": bar,
            "top_items": [
                {
                    "name": li.name,
                    "quantity": round(li.quantity, 1),
                    "unit": li.unit,
                    "unit_price": round(li.unit_price_twd),
                    "total": round(li.total_twd),
                    "vendor": li.vendor_name or "standard",
                }
                for li in top_items
            ],
            "summary": {
                "total": round(self.total_cost_twd),
                "per_sqm": round(self.cost_per_sqm_twd),
                "floor_area": round(self.total_floor_area_sqm, 1),
                "range_low": round(self.total_cost_twd * 0.7),
                "range_high": round(self.total_cost_twd * 1.3),
            },
        }

    def vendor_summary(self) -> list[dict]:
        """Return per-vendor cost summary for supplier analysis (D1-S1)."""
        vendors: dict[str, dict] = {}
        for li in self.line_items:
            if li.vendor_name:
                key = li.vendor_name
                if key not in vendors:
                    vendors[key] = {
                        "vendor": li.vendor_name,
                        "brand": li.vendor_brand,
                        "country": li.vendor_country,
                        "total_twd": 0.0,
                        "items": [],
                    }
                vendors[key]["total_twd"] += li.total_twd
                vendors[key]["items"].append(li.name)
        return sorted(vendors.values(), key=lambda v: v["total_twd"], reverse=True)


# ---- QTO category → price key mapping ----

_QTO_PRICE_MAP: dict[str, str] = {
    "wall_exterior": "brick_wall_sqm",
    "wall_interior": "partition_sqm",
    "slab": "slab_sqm",
    "door": "door_single",
    "window": "window_sliding_sqm",
    "roof": "roof_flat_sqm",
    "mep_hvac": "hvac_sqm",
    "mep_plumbing": "plumbing_sqm",
    "mep_electrical": "electrical_sqm",
    "mep_fire": "fire_protection_sqm",
    "site_work": "site_work_sqm",
}

# ---- Cost category mapping ----

_QTO_COST_CATEGORY: dict[str, str] = {
    "wall_exterior": "envelope",
    "wall_interior": "interior",
    "slab": "structure",
    "door": "door_window",
    "window": "door_window",
    "roof": "roof",
    "mep_hvac": "mep",
    "mep_plumbing": "mep",
    "mep_electrical": "mep",
    "mep_fire": "mep",
    "site_work": "site",
    "monitoring": "monitoring",
}


class CostEstimator:
    """Estimate construction costs from a BuildingPlan.

    D1-S1: Adds component substitution with real-time cost recalculation.
    - replace_component(): swap a component ID and get delta cost
    - estimate_with_substitutions(): estimate with a custom component mapping
    """

    def __init__(self) -> None:
        self._qto = QuantityTakeOff()
        # D1-S1: active component substitutions {qto_category → component_id}
        self._substitutions: dict[str, str] = {}

    def replace_component(
        self,
        plan: BuildingPlan,
        qto_category: str,
        new_component_id: str,
    ) -> "tuple[CostEstimate, float]":
        """Replace a component and recalculate costs immediately (D1-S1).

        Args:
            plan: Current BuildingPlan.
            qto_category: QTO category to override (e.g. "wall_exterior").
            new_component_id: ComponentDef ID to use instead.

        Returns:
            (new_estimate, delta_twd) — the new CostEstimate and cost change.
        """
        old_estimate = self.estimate(plan)

        # Register substitution and recalculate
        old_subs = dict(self._substitutions)
        self._substitutions[qto_category] = new_component_id
        new_estimate = self.estimate(plan)
        self._substitutions = old_subs  # restore after estimate

        delta = new_estimate.total_cost_twd - old_estimate.total_cost_twd
        logger.info(
            "Component substitution: %s → %s: delta = NT$%.0f",
            qto_category, new_component_id, delta,
        )
        return new_estimate, delta

    def estimate_with_substitutions(
        self,
        plan: BuildingPlan,
        substitutions: dict[str, str],
        monitor_plan=None,
    ) -> "CostEstimate":
        """Estimate costs with explicit component substitutions (D1-S1).

        Args:
            plan: BuildingPlan to estimate.
            substitutions: {qto_category: component_id} overrides.
        """
        self._substitutions = dict(substitutions)
        try:
            result = self.estimate(plan, monitor_plan)
        finally:
            self._substitutions = {}
        return result

    def estimate(
        self,
        plan: BuildingPlan,
        monitor_plan: MonitorPlan | None = None,
        quality_level: float = 1.0,
    ) -> CostEstimate:
        # ISS-L001: Clamp quality_level to valid range to prevent division/multiplication errors
        quality_level = max(0.0, min(1.0, float(quality_level)))
        qto_items = self._qto.extract(plan)
        line_items = self._price_items(qto_items)

        total = sum(li.total_twd for li in line_items)

        # Interior finishes allowance (ceiling + floor tile based on slab area)
        interior_extras = self._interior_finish_allowance(qto_items)
        line_items.extend(interior_extras)
        total += sum(li.total_twd for li in interior_extras)

        # Monitoring costs (if monitor plan provided)
        if monitor_plan is not None:
            monitor_items = self._monitoring_cost_items(monitor_plan)
            line_items.extend(monitor_items)
            total += sum(li.total_twd for li in monitor_items)

        # ISS-L001: Apply quality_level scaling (0.0=minimum, 1.0=standard)
        if quality_level < 1.0:
            total = total * (0.5 + 0.5 * quality_level)  # scale 50%-100%

        # Calculate total floor area
        total_floor_area = sum(qi.quantity for qi in qto_items if qi.category == "slab")

        # Breakdown by category
        cat_totals: dict[str, float] = {}
        for li in line_items:
            cat = _QTO_COST_CATEGORY.get(li.price_key, li.category)
            cat_totals[cat] = cat_totals.get(cat, 0.0) + li.total_twd

        breakdown = []
        for cat, cost in sorted(cat_totals.items(), key=lambda x: -x[1]):
            breakdown.append(
                CostBreakdown(
                    category=cat,
                    label=CATEGORY_LABELS.get(cat, cat),
                    cost_twd=cost,
                    ratio=cost / total if total > 0 else 0,
                )
            )

        cost_per_sqm = total / total_floor_area if total_floor_area > 0 else 0

        for li in line_items:
            logger.debug(
                "Cost: %s — %.0f %s x NT$%.0f = NT$%.0f",
                li.name,
                li.quantity,
                li.unit,
                li.unit_price_twd,
                li.total_twd,
            )
        for b in breakdown:
            logger.debug("Breakdown: %s — NT$%.0f (%.1f%%)", b.label, b.cost_twd, b.ratio * 100)
        logger.debug("Total cost: NT$%.0f (NT$%.0f/sqm)", total, cost_per_sqm)

        return CostEstimate(
            project_name=plan.name,
            total_cost_twd=total,
            total_floor_area_sqm=total_floor_area,
            cost_per_sqm_twd=cost_per_sqm,
            line_items=line_items,
            breakdown=breakdown,
        )

    def _price_items(self, qto_items: list[QTOItem]) -> list[CostLineItem]:
        result: list[CostLineItem] = []
        for qi in qto_items:
            # D1-S1: check if there's an active component substitution
            if qi.category in self._substitutions:
                sub_item = self._price_item_from_component(qi, self._substitutions[qi.category])
                if sub_item:
                    result.append(sub_item)
                    continue

            price_key = _QTO_PRICE_MAP.get(qi.category)
            if not price_key:
                logger.warning(
                    "COST-01: No price mapping for QTO category '%s' (qty=%.1f %s) — item skipped",
                    qi.category, qi.quantity, qi.unit,
                )
                continue
            entry = UNIT_PRICES_TWD.get(price_key)
            if not entry:
                logger.warning(
                    "COST-01: No unit price for key '%s' (category='%s') — item skipped",
                    price_key, qi.category,
                )
                continue
            unit_price = entry["price"]
            total = qi.quantity * unit_price

            # D1-S1: enrich with vendor info from component registry
            vendor_name, vendor_brand, vendor_country, price_low, price_high = (
                self._lookup_vendor(qi.category, unit_price)
            )

            result.append(
                CostLineItem(
                    category=_QTO_COST_CATEGORY.get(qi.category, qi.category),
                    name=qi.name,
                    quantity=qi.quantity,
                    unit=qi.unit,
                    unit_price_twd=unit_price,
                    total_twd=total,
                    price_key=qi.category,
                    vendor_name=vendor_name,
                    vendor_brand=vendor_brand,
                    vendor_country=vendor_country,
                    vendor_price_low=price_low,
                    vendor_price_high=price_high,
                )
            )
        return result

    def _price_item_from_component(
        self, qi: QTOItem, component_id: str
    ) -> CostLineItem | None:
        """Create a CostLineItem using a specific component's supplier price (D1-S1)."""
        try:
            from promptbim.bim.components.registry import ComponentRegistry
            comp = ComponentRegistry.get(component_id)
            if comp is None or not comp.suppliers:
                return None
            sup = comp.suppliers[0]
            if sup.price is None:
                return None
            unit_price = (sup.price.min_price + sup.price.max_price) / 2
            total = qi.quantity * unit_price
            return CostLineItem(
                category=_QTO_COST_CATEGORY.get(qi.category, qi.category),
                name=f"{qi.name} [{comp.name_zh}]",
                quantity=qi.quantity,
                unit=qi.unit,
                unit_price_twd=unit_price,
                total_twd=total,
                price_key=qi.category,
                vendor_name=sup.name,
                vendor_brand=sup.brand or "",
                vendor_country=sup.country or "",
                vendor_price_low=sup.price.min_price,
                vendor_price_high=sup.price.max_price,
            )
        except (ImportError, AttributeError, IndexError, TypeError) as exc:
            logger.debug("Component substitution failed for %s: %s", component_id, exc)
            return None

    def _lookup_vendor(
        self, qto_category: str, unit_price: float
    ) -> tuple[str, str, str, float, float]:
        """Look up vendor info from component registry for a QTO category (D1-S1)."""
        # Map QTO category → component search keywords
        _QTO_VENDOR_KEYWORDS: dict[str, list[str]] = {
            "wall_exterior": ["外牆", "brick", "curtain wall"],
            "wall_interior": ["輕隔間", "partition"],
            "mep_hvac": ["空調", "HVAC"],
            "mep_electrical": ["配電", "electrical"],
            "mep_plumbing": ["給水管", "plumbing"],
            "mep_fire": ["消防", "sprinkler"],
        }
        keywords = _QTO_VENDOR_KEYWORDS.get(qto_category, [])
        if not keywords:
            return ("", "", "", unit_price * 0.7, unit_price * 1.3)

        try:
            from promptbim.bim.components.registry import ComponentRegistry
            results = ComponentRegistry.search(keywords, max_results=1)
            if results and results[0].suppliers:
                sup = results[0].suppliers[0]
                price_low = sup.price.min_price if sup.price else unit_price * 0.7
                price_high = sup.price.max_price if sup.price else unit_price * 1.3
                return (sup.name, sup.brand or "", sup.country or "", price_low, price_high)
        except (ImportError, AttributeError, IndexError, TypeError) as exc:
            logger.debug("Vendor lookup failed for %s: %s", qto_category, exc)
        return ("", "", "", unit_price * 0.7, unit_price * 1.3)

    def _monitoring_cost_items(self, monitor_plan: MonitorPlan) -> list[CostLineItem]:
        """Add monitoring sensor/actuator costs from a MonitorPlan."""
        from promptbim.bim.monitoring.monitor_types import MONITOR_TYPES

        items: list[CostLineItem] = []
        # Aggregate by type
        type_counts: dict[str, int] = monitor_plan.by_type()
        for type_id, count in type_counts.items():
            mt = MONITOR_TYPES.get(type_id)
            if mt is None:
                continue
            items.append(
                CostLineItem(
                    category="monitoring",
                    name=mt.name,
                    quantity=count,
                    unit="unit",
                    unit_price_twd=mt.unit_cost_twd,
                    total_twd=count * mt.unit_cost_twd,
                    price_key="monitoring",
                )
            )
        return items

    def _interior_finish_allowance(self, qto_items: list[QTOItem]) -> list[CostLineItem]:
        """Add ceiling + floor tile costs based on slab areas."""
        items: list[CostLineItem] = []
        for qi in qto_items:
            if qi.category != "slab":
                continue
            area = qi.quantity
            # Ceiling
            ceiling_price = UNIT_PRICES_TWD["ceiling_sqm"]["price"]
            items.append(
                CostLineItem(
                    category="interior",
                    name=f"Ceiling-{qi.story}",
                    quantity=area,
                    unit="m2",
                    unit_price_twd=ceiling_price,
                    total_twd=area * ceiling_price,
                    price_key="ceiling",
                )
            )
            # Floor tile
            tile_price = UNIT_PRICES_TWD["floor_tile_sqm"]["price"]
            items.append(
                CostLineItem(
                    category="interior",
                    name=f"FloorTile-{qi.story}",
                    quantity=area,
                    unit="m2",
                    unit_price_twd=tile_price,
                    total_twd=area * tile_price,
                    price_key="floor_tile",
                )
            )
        return items
