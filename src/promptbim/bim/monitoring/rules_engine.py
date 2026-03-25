"""Placement density rules for monitoring points.

Each rule specifies how many sensors/actuators of a given type should be placed
per unit area or per space, depending on space type.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PlacementRule:
    """A placement density rule for a monitor type."""

    monitor_type_id: str
    mode: str  # "per_sqm" | "per_space" | "per_floor" | "per_building"
    density: float  # e.g. 0.05 means 1 per 20 sqm; 1.0 means 1 per space
    min_per_space: int = 0
    max_per_space: int = 100
    min_area_sqm: float = 0.0  # only place if space area >= this


# ---- Default placement rules ----

PLACEMENT_RULES: dict[str, PlacementRule] = {}


def _rule(r: PlacementRule) -> None:
    PLACEMENT_RULES[r.monitor_type_id] = r


# Environmental
_rule(PlacementRule("temp_sensor", "per_sqm", 0.02, min_per_space=1, max_per_space=4))
_rule(PlacementRule("humidity_sensor", "per_sqm", 0.01, min_per_space=1, max_per_space=2))
_rule(PlacementRule("co2_sensor", "per_sqm", 0.01, min_per_space=1, max_per_space=2))
_rule(PlacementRule("pm25_sensor", "per_space", 1.0, min_per_space=1, max_per_space=1, min_area_sqm=30))
_rule(PlacementRule("light_sensor", "per_sqm", 0.015, min_per_space=1, max_per_space=4))
_rule(PlacementRule("noise_sensor", "per_space", 1.0, min_per_space=1, max_per_space=1, min_area_sqm=40))
_rule(PlacementRule("voc_sensor", "per_space", 1.0, min_per_space=0, max_per_space=1, min_area_sqm=50))
_rule(PlacementRule("outdoor_weather", "per_building", 1.0))

# Safety
_rule(PlacementRule("smoke_detector", "per_sqm", 0.04, min_per_space=1, max_per_space=10))
_rule(PlacementRule("heat_detector", "per_space", 1.0, min_per_space=1, max_per_space=2))
_rule(PlacementRule("gas_detector", "per_space", 1.0, min_per_space=1, max_per_space=2))
_rule(PlacementRule("co_detector", "per_space", 1.0, min_per_space=1, max_per_space=2))
_rule(PlacementRule("water_leak_sensor", "per_space", 1.0, min_per_space=1, max_per_space=3))
_rule(PlacementRule("seismic_sensor", "per_building", 1.0))
_rule(PlacementRule("fire_alarm_pull", "per_floor", 2.0))
_rule(PlacementRule("sprinkler_flow", "per_floor", 1.0))

# Security
_rule(PlacementRule("access_reader", "per_space", 1.0, min_per_space=1, max_per_space=2))
_rule(PlacementRule("cctv_camera", "per_space", 1.0, min_per_space=1, max_per_space=4))
_rule(PlacementRule("motion_sensor", "per_sqm", 0.02, min_per_space=1, max_per_space=4))
_rule(PlacementRule("door_contact", "per_space", 1.0, min_per_space=1, max_per_space=2))
_rule(PlacementRule("glass_break", "per_space", 1.0, min_per_space=1, max_per_space=2))
_rule(PlacementRule("intercom", "per_space", 1.0, min_per_space=1, max_per_space=1))

# Energy
_rule(PlacementRule("power_meter", "per_floor", 1.0))
_rule(PlacementRule("water_meter", "per_floor", 1.0))
_rule(PlacementRule("gas_meter", "per_building", 1.0))
_rule(PlacementRule("solar_irradiance", "per_building", 1.0))
_rule(PlacementRule("btu_meter", "per_building", 1.0))
_rule(PlacementRule("ct_sensor", "per_floor", 3.0))

# Structural
_rule(PlacementRule("strain_gauge", "per_floor", 4.0))
_rule(PlacementRule("tilt_sensor", "per_building", 2.0))
_rule(PlacementRule("crack_sensor", "per_floor", 2.0))
_rule(PlacementRule("vibration_sensor", "per_building", 2.0))

# MEP
_rule(PlacementRule("pressure_sensor", "per_floor", 1.0))
_rule(PlacementRule("duct_temp_sensor", "per_floor", 2.0))
_rule(PlacementRule("vav_controller", "per_sqm", 0.01, min_per_space=1, max_per_space=4, min_area_sqm=20))
_rule(PlacementRule("damper_actuator", "per_floor", 2.0))
_rule(PlacementRule("valve_actuator", "per_floor", 2.0))
_rule(PlacementRule("pump_vfd", "per_building", 2.0))

# Smart
_rule(PlacementRule("occupancy_sensor", "per_space", 1.0, min_per_space=1, max_per_space=2))
_rule(PlacementRule("people_counter", "per_space", 1.0, min_per_space=1, max_per_space=1))
_rule(PlacementRule("smart_thermostat", "per_space", 1.0, min_per_space=1, max_per_space=1))
_rule(PlacementRule("lighting_controller", "per_sqm", 0.01, min_per_space=1, max_per_space=4))
_rule(PlacementRule("blind_actuator", "per_space", 1.0, min_per_space=0, max_per_space=2))
_rule(PlacementRule("air_purifier_ctrl", "per_space", 1.0, min_per_space=0, max_per_space=1, min_area_sqm=30))

# Accessibility
_rule(PlacementRule("emergency_button", "per_space", 1.0, min_per_space=1, max_per_space=2))
_rule(PlacementRule("wayfinding_beacon", "per_sqm", 0.02, min_per_space=1, max_per_space=4))
_rule(PlacementRule("elevator_sensor", "per_space", 1.0, min_per_space=1, max_per_space=1))
_rule(PlacementRule("parking_sensor", "per_sqm", 0.04, min_per_space=1, max_per_space=50))


class RulesEngine:
    """Compute the number of monitors to place given space information."""

    def __init__(self, rules: dict[str, PlacementRule] | None = None) -> None:
        self._rules = rules or PLACEMENT_RULES

    def compute_count(
        self,
        monitor_type_id: str,
        area_sqm: float = 0.0,
        *,
        mode_override: str | None = None,
    ) -> int:
        """Return the number of monitors to place for a given space."""
        rule = self._rules.get(monitor_type_id)
        if rule is None:
            return 1

        if area_sqm < rule.min_area_sqm:
            return 0

        mode = mode_override or rule.mode

        if mode == "per_sqm":
            count = max(rule.min_per_space, int(area_sqm * rule.density + 0.5))
        elif mode == "per_space":
            count = max(rule.min_per_space, int(rule.density + 0.5))
        elif mode == "per_floor":
            count = max(1, int(rule.density + 0.5))
        elif mode == "per_building":
            count = max(1, int(rule.density + 0.5))
        else:
            count = 1

        return min(count, rule.max_per_space)
