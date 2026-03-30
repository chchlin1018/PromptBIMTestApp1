"""Device type registry — T14 Device Extensibility.

Provides an extensible device type system using enum + factory pattern.
New device types can be registered without modifying existing code.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from promptbim.debug import get_logger

logger = get_logger("bim.devices")


class DeviceCategory(str, Enum):
    """Standard BIM device categories."""
    HVAC = "hvac"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    FIRE_PROTECTION = "fire_protection"
    MONITORING = "monitoring"
    LIGHTING = "lighting"
    SECURITY = "security"
    ELEVATOR = "elevator"
    CUSTOM = "custom"


class DeviceSpec:
    """Specification for a BIM device type."""

    __slots__ = ("type_id", "category", "name", "name_zh", "parameters", "ifc_class")

    def __init__(
        self,
        type_id: str,
        category: DeviceCategory,
        name: str,
        name_zh: str = "",
        parameters: dict | None = None,
        ifc_class: str = "IfcDistributionElement",
    ) -> None:
        self.type_id = type_id
        self.category = category
        self.name = name
        self.name_zh = name_zh
        self.parameters = parameters or {}
        self.ifc_class = ifc_class


class DeviceRegistry:
    """Extensible device type registry with factory pattern.

    Register new device types with `register()`. Create instances with `create()`.
    """

    _specs: dict[str, DeviceSpec] = {}

    @classmethod
    def register(cls, spec: DeviceSpec) -> None:
        """Register a new device type specification."""
        cls._specs[spec.type_id] = spec
        logger.debug("Registered device type: %s (%s)", spec.type_id, spec.category.value)

    @classmethod
    def get(cls, type_id: str) -> DeviceSpec | None:
        """Get device spec by type ID."""
        return cls._specs.get(type_id)

    @classmethod
    def list_by_category(cls, category: DeviceCategory) -> list[DeviceSpec]:
        """List all device types in a category."""
        return [s for s in cls._specs.values() if s.category == category]

    @classmethod
    def list_all(cls) -> list[DeviceSpec]:
        """List all registered device types."""
        return list(cls._specs.values())

    @classmethod
    def create(cls, type_id: str, **overrides: Any) -> dict:
        """Factory: create a device instance dict from a spec.

        Returns a dict with all spec parameters, overridden by any kwargs.
        """
        spec = cls._specs.get(type_id)
        if spec is None:
            raise KeyError(f"Unknown device type: {type_id}")
        instance = {
            "type_id": spec.type_id,
            "category": spec.category.value,
            "name": spec.name,
            "name_zh": spec.name_zh,
            "ifc_class": spec.ifc_class,
            **spec.parameters,
            **overrides,
        }
        return instance


# Register built-in device types
def _register_builtins() -> None:
    DeviceRegistry.register(DeviceSpec("chiller", DeviceCategory.HVAC, "Chiller", "冰水主機"))
    DeviceRegistry.register(DeviceSpec("ahu", DeviceCategory.HVAC, "Air Handling Unit", "空調箱"))
    DeviceRegistry.register(DeviceSpec("cooling_tower", DeviceCategory.HVAC, "Cooling Tower", "冷卻水塔"))
    DeviceRegistry.register(DeviceSpec("pump", DeviceCategory.PLUMBING, "Pump", "泵浦"))
    DeviceRegistry.register(DeviceSpec("sprinkler", DeviceCategory.FIRE_PROTECTION, "Sprinkler", "灑水頭"))
    DeviceRegistry.register(DeviceSpec("panel_board", DeviceCategory.ELECTRICAL, "Panel Board", "配電盤"))
    DeviceRegistry.register(DeviceSpec("transformer", DeviceCategory.ELECTRICAL, "Transformer", "變壓器"))
    DeviceRegistry.register(DeviceSpec("elevator", DeviceCategory.ELEVATOR, "Elevator", "電梯"))
    DeviceRegistry.register(DeviceSpec("temp_sensor", DeviceCategory.MONITORING, "Temperature Sensor", "溫度感測器"))
    DeviceRegistry.register(DeviceSpec("humidity_sensor", DeviceCategory.MONITORING, "Humidity Sensor", "濕度感測器"))


_register_builtins()
