"""MEP system definition templates.

Each building type has a template describing the four MEP systems:
HVAC, Plumbing, Electrical, Fire Protection.

D1-S1 additions:
- Additional building type templates (factory, hospital, school, mixed_use)
- ElectricalTemplate.power_load_kw: total estimated power load
- HVACTemplate.cooling_capacity_kw: estimated cooling capacity
- MEPPenetrationSpec: wall/slab penetration requirement data
- calculate_mep_loads(): compute all MEP loads from a BuildingPlan
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
    cooling_capacity_kw: float = 0.0  # kW per 100 sqm; 0 = auto-calculated


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
    power_load_kw: float = 0.0  # kW per 100 sqm; 0 = auto-calculated


@dataclass
class FireProtectionTemplate:
    sprinkler_main_mm: float = 65
    sprinkler_branch_mm: float = 25
    heads_per_sqm: float = 0.08
    extinguisher_per_floor: int = 2


@dataclass
class MEPPenetrationSpec:
    """Wall/slab penetration requirement for a MEP system (D1-S1).

    Records how many penetrations per unit area are needed,
    sleeve diameter, and fire rating requirement.
    """

    system: str  # e.g. "hvac", "plumbing"
    element_type: str  # "wall" or "slab"
    count_per_100sqm: float = 1.0
    sleeve_diameter_mm: float = 150.0
    fire_rated: bool = False
    notes: str = ""


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
    "factory": MEPSystemTemplate(
        hvac=HVACTemplate(
            type="industrial_ventilation",
            equipment=["industrial_ahu", "exhaust_fan"],
            main_duct_mm=(900, 600),
            branch_duct_mm=(450, 300),
            terminals_per_100sqm=2,
            cooling_capacity_kw=8.0,
        ),
        plumbing=PlumbingTemplate(
            cold_water_main_mm=100,
            cold_water_branch_mm=40,
            drain_main_mm=150,
            drain_branch_mm=75,
            fixtures=["toilet", "sink", "floor_drain", "eyewash_station"],
        ),
        electrical=ElectricalTemplate(
            main_tray_mm=(400, 200),
            branch_tray_mm=(200, 100),
            panel_per_floor=2,
            outlets_per_100sqm=10,
            power_load_kw=40.0,
        ),
        fire_protection=FireProtectionTemplate(
            sprinkler_main_mm=100,
            sprinkler_branch_mm=40,
            heads_per_sqm=0.12,
            extinguisher_per_floor=4,
        ),
    ),
    "hospital": MEPSystemTemplate(
        hvac=HVACTemplate(
            type="central_air_medical",
            equipment=["rooftop_ahu", "hepa_filter", "humidifier"],
            main_duct_mm=(700, 500),
            branch_duct_mm=(350, 250),
            terminals_per_100sqm=6,
            cooling_capacity_kw=15.0,
        ),
        plumbing=PlumbingTemplate(
            cold_water_main_mm=100,
            cold_water_branch_mm=32,
            drain_main_mm=125,
            drain_branch_mm=65,
            fixtures=["toilet", "sink", "shower", "medical_gas_panel", "nurse_station_sink"],
        ),
        electrical=ElectricalTemplate(
            main_tray_mm=(300, 150),
            branch_tray_mm=(150, 75),
            panel_per_floor=2,
            outlets_per_100sqm=35,
            power_load_kw=25.0,
        ),
        fire_protection=FireProtectionTemplate(
            sprinkler_main_mm=80,
            sprinkler_branch_mm=32,
            heads_per_sqm=0.10,
            extinguisher_per_floor=3,
        ),
    ),
    "school": MEPSystemTemplate(
        hvac=HVACTemplate(
            type="split_unit",
            equipment=["split_ac", "fresh_air_unit"],
            main_duct_mm=(500, 350),
            branch_duct_mm=(250, 180),
            terminals_per_100sqm=3,
            cooling_capacity_kw=7.0,
        ),
        plumbing=PlumbingTemplate(
            cold_water_main_mm=65,
            cold_water_branch_mm=25,
            drain_main_mm=100,
            drain_branch_mm=50,
            fixtures=["toilet", "sink", "urinal", "drinking_fountain"],
        ),
        electrical=ElectricalTemplate(
            main_tray_mm=(200, 100),
            branch_tray_mm=(100, 50),
            panel_per_floor=1,
            outlets_per_100sqm=18,
            power_load_kw=12.0,
        ),
        fire_protection=FireProtectionTemplate(
            sprinkler_main_mm=65,
            sprinkler_branch_mm=25,
            heads_per_sqm=0.08,
            extinguisher_per_floor=2,
        ),
    ),
    "mixed_use": MEPSystemTemplate(
        hvac=HVACTemplate(
            type="central_air",
            equipment=["rooftop_ahu", "split_ac"],
            main_duct_mm=(700, 450),
            branch_duct_mm=(350, 220),
            terminals_per_100sqm=5,
            cooling_capacity_kw=12.0,
        ),
        plumbing=PlumbingTemplate(
            cold_water_main_mm=80,
            cold_water_branch_mm=32,
            drain_main_mm=125,
            drain_branch_mm=65,
            fixtures=["toilet", "sink", "urinal", "shower", "restaurant_grease_trap"],
        ),
        electrical=ElectricalTemplate(
            main_tray_mm=(300, 150),
            branch_tray_mm=(150, 75),
            panel_per_floor=2,
            outlets_per_100sqm=25,
            power_load_kw=20.0,
        ),
        fire_protection=FireProtectionTemplate(
            sprinkler_main_mm=80,
            sprinkler_branch_mm=32,
            heads_per_sqm=0.10,
            extinguisher_per_floor=3,
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


# ---- MEP Load Calculation (D1-S1) ----

# Power load defaults by building type (kW / 100 sqm)
_POWER_LOAD_KW_PER_100SQM: dict[str, float] = {
    "office": 8.0,
    "residential": 5.0,
    "factory": 40.0,
    "hospital": 25.0,
    "school": 12.0,
    "mixed_use": 20.0,
}

# Cooling capacity defaults by building type (kW / 100 sqm)
_COOLING_KW_PER_100SQM: dict[str, float] = {
    "office": 10.0,
    "residential": 6.5,
    "factory": 8.0,
    "hospital": 15.0,
    "school": 7.0,
    "mixed_use": 12.0,
}


def calculate_mep_loads(plan: "BuildingPlan", building_type: str = "office") -> dict:
    """Compute all MEP loads from a BuildingPlan (D1-S1).

    Returns a dict with:
    - total_floor_area_sqm
    - power_load_kw (total electrical demand)
    - cooling_capacity_kw (total cooling demand)
    - plumbing_fixture_count (estimated)
    - sprinkler_head_count (estimated)
    - penetration_specs (list of MEPPenetrationSpec dicts)
    """
    from promptbim.schemas.plan import BuildingPlan as _BP  # noqa: F401

    total_area = sum(
        sum(sp.area_sqm for sp in story.spaces)
        for story in plan.stories
    )
    num_stories = len(plan.stories)

    pw_per_100 = _POWER_LOAD_KW_PER_100SQM.get(building_type, 8.0)
    cool_per_100 = _COOLING_KW_PER_100SQM.get(building_type, 10.0)

    template = get_template(building_type)

    power_load_kw = round(total_area / 100.0 * (
        template.electrical.power_load_kw if template.electrical.power_load_kw > 0
        else pw_per_100
    ), 1)
    cooling_capacity_kw = round(total_area / 100.0 * (
        template.hvac.cooling_capacity_kw if template.hvac.cooling_capacity_kw > 0
        else cool_per_100
    ), 1)

    fixture_count = max(1, int(total_area / 100.0 * len(template.plumbing.fixtures) * 2))
    sprinkler_count = max(1, int(total_area * template.fire_protection.heads_per_sqm))

    # Build penetration specs
    penetration_specs = [
        MEPPenetrationSpec(
            system="hvac",
            element_type="wall",
            count_per_100sqm=1.5,
            sleeve_diameter_mm=400.0,
            fire_rated=True,
            notes="Main duct penetration through fire-rated wall",
        ).__dict__,
        MEPPenetrationSpec(
            system="plumbing",
            element_type="slab",
            count_per_100sqm=2.0,
            sleeve_diameter_mm=150.0,
            fire_rated=True,
            notes="Drain/supply riser through slab",
        ).__dict__,
        MEPPenetrationSpec(
            system="electrical",
            element_type="wall",
            count_per_100sqm=3.0,
            sleeve_diameter_mm=100.0,
            fire_rated=False,
            notes="Conduit through partition wall",
        ).__dict__,
        MEPPenetrationSpec(
            system="fire_protection",
            element_type="wall",
            count_per_100sqm=0.5,
            sleeve_diameter_mm=80.0,
            fire_rated=True,
            notes="Sprinkler branch through fire wall",
        ).__dict__,
    ]

    return {
        "total_floor_area_sqm": round(total_area, 1),
        "num_stories": num_stories,
        "building_type": building_type,
        "power_load_kw": power_load_kw,
        "cooling_capacity_kw": cooling_capacity_kw,
        "plumbing_fixture_count": fixture_count,
        "sprinkler_head_count": sprinkler_count,
        "penetration_specs": penetration_specs,
    }


# TYPE_CHECKING import guard
from typing import TYPE_CHECKING  # noqa: E402
if TYPE_CHECKING:
    from promptbim.schemas.plan import BuildingPlan  # noqa: F401
