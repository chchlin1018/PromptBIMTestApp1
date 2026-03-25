"""Cost Estimation engine — maps QTO items to unit prices and produces a cost summary."""

from __future__ import annotations

from dataclasses import dataclass, field

from promptbim.debug import get_logger
from promptbim.bim.cost.qto import QTOItem, QuantityTakeOff
from promptbim.bim.cost.unit_prices_tw import (
    CATEGORY_LABELS,
    UNIT_PRICES_TWD,
)
from promptbim.schemas.plan import BuildingPlan

from typing import TYPE_CHECKING

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


@dataclass
class CostBreakdown:
    """Breakdown of cost by category."""

    category: str
    label: str
    cost_twd: float
    ratio: float = 0.0


@dataclass
class CostEstimate:
    """Complete cost estimation result."""

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
    """Estimate construction costs from a BuildingPlan."""

    def __init__(self) -> None:
        self._qto = QuantityTakeOff()

    def estimate(
        self,
        plan: BuildingPlan,
        monitor_plan: MonitorPlan | None = None,
    ) -> CostEstimate:
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

        # Calculate total floor area
        total_floor_area = sum(
            qi.quantity for qi in qto_items if qi.category == "slab"
        )

        # Breakdown by category
        cat_totals: dict[str, float] = {}
        for li in line_items:
            cat = _QTO_COST_CATEGORY.get(li.price_key, li.category)
            cat_totals[cat] = cat_totals.get(cat, 0.0) + li.total_twd

        breakdown = []
        for cat, cost in sorted(cat_totals.items(), key=lambda x: -x[1]):
            breakdown.append(CostBreakdown(
                category=cat,
                label=CATEGORY_LABELS.get(cat, cat),
                cost_twd=cost,
                ratio=cost / total if total > 0 else 0,
            ))

        cost_per_sqm = total / total_floor_area if total_floor_area > 0 else 0

        for li in line_items:
            logger.debug("Cost: %s — %.0f %s x NT$%.0f = NT$%.0f", li.name, li.quantity, li.unit, li.unit_price_twd, li.total_twd)
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
            price_key = _QTO_PRICE_MAP.get(qi.category)
            if not price_key:
                continue
            entry = UNIT_PRICES_TWD.get(price_key)
            if not entry:
                continue
            unit_price = entry["price"]
            total = qi.quantity * unit_price
            result.append(CostLineItem(
                category=_QTO_COST_CATEGORY.get(qi.category, qi.category),
                name=qi.name,
                quantity=qi.quantity,
                unit=qi.unit,
                unit_price_twd=unit_price,
                total_twd=total,
                price_key=qi.category,
            ))
        return result

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
            items.append(CostLineItem(
                category="monitoring",
                name=mt.name,
                quantity=count,
                unit="unit",
                unit_price_twd=mt.unit_cost_twd,
                total_twd=count * mt.unit_cost_twd,
                price_key="monitoring",
            ))
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
            items.append(CostLineItem(
                category="interior",
                name=f"Ceiling-{qi.story}",
                quantity=area,
                unit="m2",
                unit_price_twd=ceiling_price,
                total_twd=area * ceiling_price,
                price_key="ceiling",
            ))
            # Floor tile
            tile_price = UNIT_PRICES_TWD["floor_tile_sqm"]["price"]
            items.append(CostLineItem(
                category="interior",
                name=f"FloorTile-{qi.story}",
                quantity=area,
                unit="m2",
                unit_price_twd=tile_price,
                total_twd=area * tile_price,
                price_key="floor_tile",
            ))
        return items
