"""Taiwan construction reference unit prices (2025-2026, POC-grade estimates).

Prices are in TWD and are rough estimates for early-stage cost planning.
NOT suitable for formal bidding or contracts.
"""

from __future__ import annotations

from dataclasses import dataclass

from promptbim.debug import get_logger

logger = get_logger("cost.unit_prices")


@dataclass(frozen=True)
class UnitPrice:
    """A single unit price entry."""

    key: str
    price_twd: float
    unit: str
    description: str
    category: str


# ---- Master price table ----

UNIT_PRICES_TWD: dict[str, dict] = {
    # Structure
    "rc_concrete_m3": {
        "price": 3200,
        "unit": "m3",
        "desc": "RC concrete fc'280",
        "category": "structure",
    },
    "rebar_ton": {"price": 25000, "unit": "ton", "desc": "SD420 rebar", "category": "structure"},
    "steel_structure_ton": {
        "price": 45000,
        "unit": "ton",
        "desc": "Steel structure (fabricated + installed)",
        "category": "structure",
    },
    "formwork_sqm": {"price": 650, "unit": "m2", "desc": "Formwork", "category": "structure"},
    # Envelope / Exterior walls
    "brick_wall_sqm": {
        "price": 1800,
        "unit": "m2",
        "desc": "1B brick wall (plastered)",
        "category": "envelope",
    },
    "curtain_wall_sqm": {
        "price": 12000,
        "unit": "m2",
        "desc": "Aluminium curtain wall",
        "category": "envelope",
    },
    "ext_paint_sqm": {"price": 450, "unit": "m2", "desc": "Exterior paint", "category": "envelope"},
    # Interior
    "partition_sqm": {
        "price": 1200,
        "unit": "m2",
        "desc": "Light partition wall",
        "category": "interior",
    },
    "ceiling_sqm": {
        "price": 800,
        "unit": "m2",
        "desc": "Light-gauge steel ceiling",
        "category": "interior",
    },
    "floor_tile_sqm": {
        "price": 1500,
        "unit": "m2",
        "desc": "Floor tile (material + labour)",
        "category": "interior",
    },
    # Doors & Windows
    "door_single": {
        "price": 8000,
        "unit": "unit",
        "desc": "Aluminium door 90x210cm",
        "category": "door_window",
    },
    "door_fire": {
        "price": 18000,
        "unit": "unit",
        "desc": "Fire door 60min rated",
        "category": "door_window",
    },
    "window_sliding_sqm": {
        "price": 6500,
        "unit": "m2",
        "desc": "Aluminium sliding window",
        "category": "door_window",
    },
    # MEP
    "hvac_sqm": {
        "price": 3500,
        "unit": "m2",
        "desc": "HVAC system (equipment + piping)",
        "category": "mep",
    },
    "plumbing_sqm": {
        "price": 1200,
        "unit": "m2",
        "desc": "Plumbing (water + drainage)",
        "category": "mep",
    },
    "electrical_sqm": {"price": 2000, "unit": "m2", "desc": "Electrical system", "category": "mep"},
    "fire_protection_sqm": {
        "price": 800,
        "unit": "m2",
        "desc": "Fire protection (sprinklers)",
        "category": "mep",
    },
    # Equipment
    "elevator_unit": {
        "price": 2500000,
        "unit": "unit",
        "desc": "Passenger elevator (standard)",
        "category": "equipment",
    },
    "escalator_unit": {
        "price": 4500000,
        "unit": "unit",
        "desc": "Escalator",
        "category": "equipment",
    },
    # Roof
    "roof_flat_sqm": {
        "price": 2200,
        "unit": "m2",
        "desc": "Flat roof waterproofing + insulation",
        "category": "roof",
    },
    "roof_sloped_sqm": {
        "price": 3000,
        "unit": "m2",
        "desc": "Sloped roof (tiles + frame)",
        "category": "roof",
    },
    # Slab
    "slab_sqm": {
        "price": 2800,
        "unit": "m2",
        "desc": "RC slab (concrete + rebar + formwork)",
        "category": "structure",
    },
    # Site
    "site_work_sqm": {
        "price": 1500,
        "unit": "m2",
        "desc": "Site work (grading, paving)",
        "category": "site",
    },
    "landscaping_sqm": {"price": 2500, "unit": "m2", "desc": "Landscaping", "category": "site"},
    # Monitoring
    "monitoring_sensor": {
        "price": 5000,
        "unit": "unit",
        "desc": "Smart sensor (average)",
        "category": "monitoring",
    },
    "monitoring_actuator": {
        "price": 8000,
        "unit": "unit",
        "desc": "Smart actuator (average)",
        "category": "monitoring",
    },
}


# ---- Cost category display labels ----

CATEGORY_LABELS: dict[str, str] = {
    "structure": "Structure",
    "envelope": "Envelope",
    "interior": "Interior Finishes",
    "door_window": "Doors & Windows",
    "mep": "MEP Systems",
    "equipment": "Equipment",
    "roof": "Roof",
    "site": "Site Work",
    "monitoring": "Smart Monitoring",
}


def get_price(key: str) -> float:
    """Return the TWD unit price for *key*, or 0 if not found."""
    entry = UNIT_PRICES_TWD.get(key)
    if entry:
        logger.debug("Price lookup: '%s' -> NT$%.0f/%s", key, entry["price"], entry["unit"])
        return entry["price"]
    logger.debug("Price lookup: '%s' -> miss", key)
    return 0


def get_category(key: str) -> str:
    """Return the cost category for *key*."""
    entry = UNIT_PRICES_TWD.get(key)
    return entry["category"] if entry else "other"
