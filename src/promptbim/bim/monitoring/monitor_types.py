"""48 sensor/actuator type definitions for smart building monitoring.

Each type has an IFC class (IfcSensor or IfcActuator), a category, applicable
space types, and a reference unit cost (TWD) for 5D integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MonitorCategory(str, Enum):
    """Top-level sensor/actuator categories."""

    ENVIRONMENTAL = "environmental"
    SAFETY = "safety"
    SECURITY = "security"
    ENERGY = "energy"
    STRUCTURAL = "structural"
    MEP = "mep"
    SMART = "smart"
    ACCESSIBILITY = "accessibility"


@dataclass(frozen=True)
class MonitorType:
    """Definition of a single sensor or actuator type."""

    id: str
    name: str
    category: MonitorCategory
    ifc_class: str  # IfcSensor or IfcActuator
    predefined_type: str  # e.g. TEMPERATURESENSOR, THERMOSTAT
    applicable_spaces: list[str] = field(default_factory=list)
    unit_cost_twd: float = 0
    description: str = ""
    measurement_unit: str = ""
    color_rgb: tuple[float, float, float] = (0.0, 0.8, 0.8)


# ---- 48 monitor type definitions ----

MONITOR_TYPES: dict[str, MonitorType] = {}


def _reg(mt: MonitorType) -> None:
    MONITOR_TYPES[mt.id] = mt


# === ENVIRONMENTAL (8) ===
_reg(MonitorType("temp_sensor", "Temperature Sensor", MonitorCategory.ENVIRONMENTAL,
    "IfcSensor", "TEMPERATURESENSOR",
    ["office", "meeting", "living", "bedroom", "corridor"],
    3500, "Indoor air temperature", "C", (0.2, 0.6, 1.0)))
_reg(MonitorType("humidity_sensor", "Humidity Sensor", MonitorCategory.ENVIRONMENTAL,
    "IfcSensor", "HUMIDITYSENSOR",
    ["office", "meeting", "living", "bedroom"],
    3000, "Relative humidity", "%RH", (0.2, 0.7, 0.9)))
_reg(MonitorType("co2_sensor", "CO2 Sensor", MonitorCategory.ENVIRONMENTAL,
    "IfcSensor", "COSENSOR",
    ["office", "meeting", "living", "corridor"],
    5500, "CO2 concentration", "ppm", (0.4, 0.8, 0.4)))
_reg(MonitorType("pm25_sensor", "PM2.5 Sensor", MonitorCategory.ENVIRONMENTAL,
    "IfcSensor", "PARTICLESENSOR",
    ["office", "living", "corridor"],
    6000, "PM2.5 particle concentration", "ug/m3", (0.6, 0.6, 0.3)))
_reg(MonitorType("light_sensor", "Light Level Sensor", MonitorCategory.ENVIRONMENTAL,
    "IfcSensor", "LIGHTSENSOR",
    ["office", "meeting", "living"],
    2500, "Illuminance", "lux", (1.0, 0.9, 0.3)))
_reg(MonitorType("noise_sensor", "Noise Level Sensor", MonitorCategory.ENVIRONMENTAL,
    "IfcSensor", "SOUNDSENSOR",
    ["office", "meeting", "living", "bedroom"],
    4000, "Sound pressure level", "dB", (0.8, 0.5, 0.8)))
_reg(MonitorType("voc_sensor", "VOC Sensor", MonitorCategory.ENVIRONMENTAL,
    "IfcSensor", "GASSENSOR",
    ["office", "meeting", "living"],
    7000, "Volatile organic compounds", "ppb", (0.5, 0.8, 0.5)))
_reg(MonitorType("outdoor_weather", "Outdoor Weather Station", MonitorCategory.ENVIRONMENTAL,
    "IfcSensor", "WEATHERSTATION",
    ["roof"],
    25000, "Temperature/humidity/wind/rain", "multi", (0.3, 0.3, 0.9)))

# === SAFETY (8) ===
_reg(MonitorType("smoke_detector", "Smoke Detector", MonitorCategory.SAFETY,
    "IfcSensor", "SMOKEDETECTOR",
    ["office", "meeting", "living", "bedroom", "corridor", "storage"],
    1500, "Optical smoke detection", "bool", (1.0, 0.3, 0.3)))
_reg(MonitorType("heat_detector", "Heat Detector", MonitorCategory.SAFETY,
    "IfcSensor", "HEATDETECTOR",
    ["kitchen", "server_room", "storage"],
    1800, "Rate-of-rise heat detection", "C", (1.0, 0.4, 0.2)))
_reg(MonitorType("gas_detector", "Gas Leak Detector", MonitorCategory.SAFETY,
    "IfcSensor", "GASSENSOR",
    ["kitchen", "mechanical", "parking"],
    4500, "Combustible gas detection", "ppm", (1.0, 0.5, 0.0)))
_reg(MonitorType("co_detector", "CO Detector", MonitorCategory.SAFETY,
    "IfcSensor", "COSENSOR",
    ["parking", "mechanical"],
    3500, "Carbon monoxide detection", "ppm", (0.9, 0.3, 0.3)))
_reg(MonitorType("water_leak_sensor", "Water Leak Sensor", MonitorCategory.SAFETY,
    "IfcSensor", "MOISTURESENSOR",
    ["bathroom", "kitchen", "mechanical", "server_room"],
    2000, "Water leak detection", "bool", (0.3, 0.3, 1.0)))
_reg(MonitorType("seismic_sensor", "Seismic Sensor", MonitorCategory.SAFETY,
    "IfcSensor", "EARTHQUAKESENSOR",
    ["basement"],
    35000, "Acceleration measurement", "gal", (0.8, 0.2, 0.2)))
_reg(MonitorType("fire_alarm_pull", "Manual Fire Alarm Pull Station", MonitorCategory.SAFETY,
    "IfcActuator", "FIRESUPPRESSION",
    ["corridor", "lobby"],
    2500, "Manual fire alarm", "bool", (1.0, 0.0, 0.0)))
_reg(MonitorType("sprinkler_flow", "Sprinkler Flow Switch", MonitorCategory.SAFETY,
    "IfcSensor", "FLOWSENSOR",
    ["mechanical"],
    3000, "Fire sprinkler flow monitoring", "L/min", (1.0, 0.4, 0.4)))

# === SECURITY (6) ===
_reg(MonitorType("access_reader", "Access Control Reader", MonitorCategory.SECURITY,
    "IfcSensor", "IDENTIFIERSENSOR",
    ["entrance", "lobby", "corridor", "server_room"],
    8000, "RFID/card reader", "bool", (0.6, 0.2, 0.8)))
_reg(MonitorType("cctv_camera", "CCTV Camera", MonitorCategory.SECURITY,
    "IfcSensor", "VIDEOCAMERA",
    ["entrance", "lobby", "corridor", "parking", "roof"],
    12000, "Video surveillance", "video", (0.5, 0.5, 0.5)))
_reg(MonitorType("motion_sensor", "Motion Sensor", MonitorCategory.SECURITY,
    "IfcSensor", "MOVEMENTSENSOR",
    ["corridor", "lobby", "entrance", "parking"],
    2000, "PIR motion detection", "bool", (0.7, 0.3, 0.7)))
_reg(MonitorType("door_contact", "Door Contact Sensor", MonitorCategory.SECURITY,
    "IfcSensor", "CONTACTSENSOR",
    ["entrance", "server_room", "storage"],
    1200, "Magnetic door contact", "bool", (0.5, 0.5, 0.7)))
_reg(MonitorType("glass_break", "Glass Break Sensor", MonitorCategory.SECURITY,
    "IfcSensor", "SOUNDSENSOR",
    ["entrance", "office"],
    1800, "Glass break acoustic detection", "bool", (0.6, 0.4, 0.6)))
_reg(MonitorType("intercom", "Video Intercom", MonitorCategory.SECURITY,
    "IfcActuator", "COMMUNICATIONSENSOR",
    ["entrance", "lobby"],
    15000, "Video door intercom", "audio/video", (0.4, 0.4, 0.6)))

# === ENERGY (6) ===
_reg(MonitorType("power_meter", "Power Meter", MonitorCategory.ENERGY,
    "IfcSensor", "ELECTRICITYSENSOR",
    ["mechanical", "server_room"],
    8000, "Electricity consumption", "kWh", (0.9, 0.7, 0.1)))
_reg(MonitorType("water_meter", "Water Flow Meter", MonitorCategory.ENERGY,
    "IfcSensor", "FLOWSENSOR",
    ["mechanical", "bathroom"],
    6000, "Water consumption", "m3", (0.2, 0.5, 1.0)))
_reg(MonitorType("gas_meter", "Gas Meter", MonitorCategory.ENERGY,
    "IfcSensor", "FLOWSENSOR",
    ["mechanical", "kitchen"],
    7000, "Gas consumption", "m3", (0.9, 0.6, 0.2)))
_reg(MonitorType("solar_irradiance", "Solar Irradiance Sensor", MonitorCategory.ENERGY,
    "IfcSensor", "SOLARSENSOR",
    ["roof"],
    12000, "Solar radiation measurement", "W/m2", (1.0, 0.8, 0.0)))
_reg(MonitorType("btu_meter", "BTU Meter", MonitorCategory.ENERGY,
    "IfcSensor", "HEATSENSOR",
    ["mechanical"],
    15000, "Thermal energy measurement", "kWh", (0.9, 0.4, 0.1)))
_reg(MonitorType("ct_sensor", "Current Transformer Sensor", MonitorCategory.ENERGY,
    "IfcSensor", "ELECTRICITYSENSOR",
    ["mechanical"],
    3000, "Branch circuit current", "A", (0.8, 0.6, 0.1)))

# === STRUCTURAL (4) ===
_reg(MonitorType("strain_gauge", "Strain Gauge", MonitorCategory.STRUCTURAL,
    "IfcSensor", "STRAINSENSOR",
    ["basement", "structural"],
    8000, "Structural strain", "microstrain", (0.7, 0.2, 0.2)))
_reg(MonitorType("tilt_sensor", "Tilt Sensor", MonitorCategory.STRUCTURAL,
    "IfcSensor", "INCLINATIONSENSOR",
    ["structural", "roof"],
    12000, "Structural inclination", "deg", (0.8, 0.3, 0.3)))
_reg(MonitorType("crack_sensor", "Crack Width Sensor", MonitorCategory.STRUCTURAL,
    "IfcSensor", "DISPLACEMENTSENSOR",
    ["basement", "structural"],
    10000, "Crack width monitoring", "mm", (0.6, 0.2, 0.2)))
_reg(MonitorType("vibration_sensor", "Vibration Sensor", MonitorCategory.STRUCTURAL,
    "IfcSensor", "ACCELERATIONSENSOR",
    ["basement", "mechanical"],
    9000, "Structural vibration", "mm/s", (0.7, 0.3, 0.1)))

# === MEP (6) ===
_reg(MonitorType("pressure_sensor", "Pipe Pressure Sensor", MonitorCategory.MEP,
    "IfcSensor", "PRESSURESENSOR",
    ["mechanical"],
    4000, "Water/air pressure", "kPa", (0.3, 0.6, 0.9)))
_reg(MonitorType("duct_temp_sensor", "Duct Temperature Sensor", MonitorCategory.MEP,
    "IfcSensor", "TEMPERATURESENSOR",
    ["mechanical"],
    3000, "Supply/return air temperature", "C", (0.3, 0.7, 0.8)))
_reg(MonitorType("vav_controller", "VAV Box Controller", MonitorCategory.MEP,
    "IfcActuator", "THERMOSTAT",
    ["office", "meeting"],
    18000, "Variable air volume control", "L/s", (0.3, 0.8, 0.6)))
_reg(MonitorType("damper_actuator", "Damper Actuator", MonitorCategory.MEP,
    "IfcActuator", "DAMPERACTUATOR",
    ["mechanical", "corridor"],
    5000, "Fire/smoke damper control", "bool", (0.4, 0.7, 0.5)))
_reg(MonitorType("valve_actuator", "Valve Actuator", MonitorCategory.MEP,
    "IfcActuator", "VALVEACTUATOR",
    ["mechanical"],
    6000, "Water/gas valve control", "bool", (0.3, 0.5, 0.8)))
_reg(MonitorType("pump_vfd", "Pump VFD Controller", MonitorCategory.MEP,
    "IfcActuator", "MOTORCONTROLLER",
    ["mechanical"],
    22000, "Variable frequency drive", "Hz", (0.4, 0.5, 0.7)))

# === SMART (6) ===
_reg(MonitorType("occupancy_sensor", "Occupancy Sensor", MonitorCategory.SMART,
    "IfcSensor", "OCCUPANCYSENSOR",
    ["office", "meeting", "corridor", "bathroom"],
    3500, "Room occupancy detection", "bool", (0.5, 0.8, 0.9)))
_reg(MonitorType("people_counter", "People Counter", MonitorCategory.SMART,
    "IfcSensor", "PEOPLESENSOR",
    ["entrance", "lobby", "corridor"],
    18000, "Bidirectional people counting", "count", (0.4, 0.7, 0.9)))
_reg(MonitorType("smart_thermostat", "Smart Thermostat", MonitorCategory.SMART,
    "IfcActuator", "THERMOSTAT",
    ["office", "meeting", "living", "bedroom"],
    8000, "AI-controlled temperature", "C", (0.3, 0.9, 0.5)))
_reg(MonitorType("lighting_controller", "Smart Lighting Controller", MonitorCategory.SMART,
    "IfcActuator", "LIGHTINGCONTROLLER",
    ["office", "meeting", "corridor", "lobby"],
    5000, "DALI/KNX lighting control", "lux", (1.0, 0.9, 0.5)))
_reg(MonitorType("blind_actuator", "Smart Blind Actuator", MonitorCategory.SMART,
    "IfcActuator", "BLINDACTUATOR",
    ["office", "meeting", "living"],
    6000, "Motorised blind/shade control", "%", (0.7, 0.7, 0.3)))
_reg(MonitorType("air_purifier_ctrl", "Air Purifier Controller", MonitorCategory.SMART,
    "IfcActuator", "MOTORCONTROLLER",
    ["office", "meeting", "living"],
    4500, "Air purifier speed control", "level", (0.5, 0.9, 0.6)))

# === ACCESSIBILITY (4) ===
_reg(MonitorType("emergency_button", "Emergency Call Button", MonitorCategory.ACCESSIBILITY,
    "IfcActuator", "ALARMPANEL",
    ["bathroom", "corridor", "lobby"],
    3000, "Emergency assistance call", "bool", (1.0, 0.0, 0.0)))
_reg(MonitorType("wayfinding_beacon", "Wayfinding Beacon", MonitorCategory.ACCESSIBILITY,
    "IfcActuator", "BEACON",
    ["corridor", "lobby", "entrance"],
    2500, "BLE beacon for indoor navigation", "RSSI", (0.4, 0.4, 1.0)))
_reg(MonitorType("elevator_sensor", "Elevator Load Sensor", MonitorCategory.ACCESSIBILITY,
    "IfcSensor", "LOADSENSOR",
    ["lobby"],
    12000, "Elevator load measurement", "kg", (0.5, 0.5, 0.5)))
_reg(MonitorType("parking_sensor", "Parking Space Sensor", MonitorCategory.ACCESSIBILITY,
    "IfcSensor", "OCCUPANCYSENSOR",
    ["parking"],
    2000, "Parking space occupancy", "bool", (0.3, 0.6, 0.3)))


# ---- category registry ----

MONITOR_CATEGORIES: dict[str, list[str]] = {}
for _mt in MONITOR_TYPES.values():
    MONITOR_CATEGORIES.setdefault(_mt.category.value, []).append(_mt.id)


def get_types_for_space(space_type: str) -> list[MonitorType]:
    """Return all monitor types applicable to a given space type."""
    return [mt for mt in MONITOR_TYPES.values() if space_type in mt.applicable_spaces]
