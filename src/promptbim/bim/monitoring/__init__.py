"""Smart Monitoring Auto-Placement: sensors and actuators for buildings."""

from promptbim.bim.monitoring.auto_placement import (
    AutoMonitorPlacer,
    MonitorPlacement,
    MonitorPlan,
)
from promptbim.bim.monitoring.monitor_types import (
    MONITOR_CATEGORIES,
    MONITOR_TYPES,
    MonitorCategory,
    MonitorType,
    get_types_for_space,
)
from promptbim.bim.monitoring.rules_engine import (
    PLACEMENT_RULES,
    PlacementRule,
    RulesEngine,
)

__all__ = [
    "AutoMonitorPlacer",
    "MONITOR_CATEGORIES",
    "MONITOR_TYPES",
    "MonitorCategory",
    "MonitorPlan",
    "MonitorPlacement",
    "MonitorType",
    "PLACEMENT_RULES",
    "PlacementRule",
    "RulesEngine",
    "get_types_for_space",
]
