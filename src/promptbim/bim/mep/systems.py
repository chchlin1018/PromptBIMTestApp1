"""MEP system definition templates.

Each building type has a template describing the four MEP systems:
HVAC, Plumbing, Electrical, Fire Protection.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HVACTemplate:
    type: str = "central_air"
    equipment: list[str] = field(default_factory=lambda: ["rooftop_ahu"])
    main_duct_mm: tuple[float, float] = (600, 400)
    branch_duct_mm: tuple[float, float] = (300, 200)
    terminals_per_100sqm: int = 4


@dataclass
class PlumbingTemplate:
    cold_water_main_mm: float = 65
    cold_water_branch_mm: float = 25
    drain_main_mm: float = 100
    drain_branch_mm: float = 50
    fixtures: list[str] = field(default_factory=lambda: ["toilet", "sink"])


@dataclass
class ElectricalTemplate:
    main_tray_mm: tuple[float, float] = (200, 100)
    branch_tray_mm: tuple[float, float] = (100, 50)
    panel_per_floor: int = 1
    outlets_per_100sqm: int = 20


@dataclass
class FireProtectionTemplate:
    sprinkler_main_mm: float = 65
    sprinkler_branch_mm: float = 25
    heads_per_sqm: float = 0.08
    extinguisher_per_floor: int = 2


@dataclass
class MEPSystemTemplate:
    hvac: HVACTemplate = field(default_factory=HVACTemplate)
    plumbing: PlumbingTemplate = field(default_factory=PlumbingTemplate)
    electrical: ElectricalTemplate = field(default_factory=ElectricalTemplate)
    fire_protection: FireProtectionTemplate = field(default_factory=FireProtectionTemplate)


# System colour definitions (R, G, B) for visualisation
SYSTEM_COLORS: dict[str, tuple[float, float, float]] = {
    "plumbing": (0.2, 0.4, 0.8),  # blue
    "electrical": (0.8, 0.2, 0.2),  # red
    "hvac": (0.2, 0.8, 0.2),  # green
    "fire_protection": (0.8, 0.8, 0.0),  # yellow
}

SYSTEM_LABELS: dict[str, str] = {
    "plumbing": "Plumbing (Water)",
    "electrical": "Electrical",
    "hvac": "HVAC",
    "fire_protection": "Fire Protection",
}

# Ceiling space allocation (from top, mm)
CEILING_LAYER_Z_OFFSET: dict[str, float] = {
    "hvac": -0.10,  # top layer, largest ducts
    "fire_protection": -0.30,  # middle
    "electrical": -0.40,  # middle
    "plumbing": -0.50,  # bottom layer
}


# ---- Building type templates ----

MEP_SYSTEM_TEMPLATES: dict[str, MEPSystemTemplate] = {
    "office": MEPSystemTemplate(
        hvac=HVACTemplate(
            type="central_air",
            equipment=["rooftop_ahu"],
            main_duct_mm=(600, 400),
            branch_duct_mm=(300, 200),
            terminals_per_100sqm=4,
        ),
        plumbing=PlumbingTemplate(
            cold_water_main_mm=65,
            cold_water_branch_mm=25,
            drain_main_mm=100,
            drain_branch_mm=50,
            fixtures=["toilet", "sink", "urinal"],
        ),
        electrical=ElectricalTemplate(
            main_tray_mm=(200, 100),
            branch_tray_mm=(100, 50),
            panel_per_floor=1,
            outlets_per_100sqm=20,
        ),
        fire_protection=FireProtectionTemplate(
            sprinkler_main_mm=65,
            sprinkler_branch_mm=25,
            heads_per_sqm=0.08,
            extinguisher_per_floor=2,
        ),
    ),
    "residential": MEPSystemTemplate(
        hvac=HVACTemplate(
            type="split_unit",
            equipment=["split_ac"],
            main_duct_mm=(400, 300),
            branch_duct_mm=(200, 150),
            terminals_per_100sqm=3,
        ),
        plumbing=PlumbingTemplate(
            cold_water_main_mm=50,
            cold_water_branch_mm=20,
            drain_main_mm=100,
            drain_branch_mm=50,
            fixtures=["toilet", "sink", "shower", "bathtub"],
        ),
        electrical=ElectricalTemplate(
            main_tray_mm=(150, 80),
            branch_tray_mm=(80, 40),
            panel_per_floor=1,
            outlets_per_100sqm=15,
        ),
        fire_protection=FireProtectionTemplate(
            sprinkler_main_mm=50,
            sprinkler_branch_mm=20,
            heads_per_sqm=0.06,
            extinguisher_per_floor=1,
        ),
    ),
}


def get_template(building_type: str) -> MEPSystemTemplate:
    """Return the MEP template for a building type, defaulting to office."""
    return MEP_SYSTEM_TEMPLATES.get(building_type, MEP_SYSTEM_TEMPLATES["office"])


# ---- MEP System Registry (MEP-02 fix) ----
# Central registry for pluggable MEP system types.
# To add a new system, call register_system() instead of editing multiple files.

_MEP_SYSTEM_REGISTRY: dict[str, dict] = {
    "hvac": {"label": "HVAC", "color": (0.2, 0.8, 0.2), "z_offset": -0.10},
    "plumbing": {"label": "Plumbing (Water)", "color": (0.2, 0.4, 0.8), "z_offset": -0.50},
    "electrical": {"label": "Electrical", "color": (0.8, 0.2, 0.2), "z_offset": -0.40},
    "fire_protection": {"label": "Fire Protection", "color": (0.8, 0.8, 0.0), "z_offset": -0.30},
}


def register_system(
    system_id: str,
    label: str,
    color: tuple[float, float, float],
    z_offset: float,
) -> None:
    """Register a new MEP system type (e.g., district_heating, pneumatic_waste)."""
    _MEP_SYSTEM_REGISTRY[system_id] = {
        "label": label,
        "color": color,
        "z_offset": z_offset,
    }
    SYSTEM_COLORS[system_id] = color
    SYSTEM_LABELS[system_id] = label
    CEILING_LAYER_Z_OFFSET[system_id] = z_offset


def get_registered_systems() -> dict[str, dict]:
    """Return all registered MEP system types."""
    return dict(_MEP_SYSTEM_REGISTRY)
