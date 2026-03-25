"""MEP Auto-Routing: Plumbing, Electrical, HVAC, Fire Protection"""

from promptbim.bim.mep.clash_detect import ClashReport, ClashSummary, detect_clashes
from promptbim.bim.mep.pathfinder import MEPPathfinder, RoutePath
from promptbim.bim.mep.planner import MEPPlan, MEPPlanner
from promptbim.bim.mep.systems import (
    SYSTEM_COLORS,
    SYSTEM_LABELS,
    MEPSystemTemplate,
    get_template,
)

__all__ = [
    "ClashReport",
    "ClashSummary",
    "MEPPathfinder",
    "MEPPlan",
    "MEPPlanner",
    "MEPSystemTemplate",
    "RoutePath",
    "SYSTEM_COLORS",
    "SYSTEM_LABELS",
    "detect_clashes",
    "get_template",
]
