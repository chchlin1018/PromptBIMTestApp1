"""Dashboard JSON export for monitoring points.

Generates a structured JSON summary suitable for dashboard UIs or API responses.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from promptbim.bim.monitoring.auto_placement import MonitorPlan, MonitorPlacement
from promptbim.bim.monitoring.monitor_types import MONITOR_CATEGORIES, MONITOR_TYPES


def generate_dashboard_json(
    monitor_plan: MonitorPlan,
    project_name: str = "PromptBIM Project",
) -> dict:
    """Generate a dashboard-ready JSON dict from a MonitorPlan."""
    by_floor = monitor_plan.by_floor()
    by_category = monitor_plan.by_category()
    by_type = monitor_plan.by_type()

    # Floor summary
    floor_summary = []
    for floor, placements in sorted(by_floor.items()):
        floor_cost = sum(p.unit_cost_twd for p in placements)
        floor_summary.append({
            "floor": floor,
            "count": len(placements),
            "cost_twd": round(floor_cost),
        })

    # Category summary
    category_summary = []
    for cat, placements in sorted(by_category.items()):
        cat_cost = sum(p.unit_cost_twd for p in placements)
        category_summary.append({
            "category": cat,
            "count": len(placements),
            "cost_twd": round(cat_cost),
            "ratio": round(cat_cost / monitor_plan.total_cost_twd, 3) if monitor_plan.total_cost_twd > 0 else 0,
        })

    # Type detail
    type_detail = []
    for type_id, count in sorted(by_type.items(), key=lambda x: -x[1]):
        mt = MONITOR_TYPES.get(type_id)
        if mt:
            type_detail.append({
                "type_id": type_id,
                "name": mt.name,
                "category": mt.category.value,
                "ifc_class": mt.ifc_class,
                "count": count,
                "unit_cost_twd": mt.unit_cost_twd,
                "total_cost_twd": round(mt.unit_cost_twd * count),
            })

    # Sensor list (individual placements)
    sensor_list = []
    for p in monitor_plan.placements:
        sensor_list.append({
            "name": p.name,
            "type_id": p.monitor_type_id,
            "floor": p.floor,
            "space": p.space_name,
            "position": list(p.position),
            "ifc_class": p.ifc_class,
            "category": p.category,
            "unit_cost_twd": p.unit_cost_twd,
        })

    return {
        "project": project_name,
        "total_monitors": monitor_plan.total_count,
        "total_cost_twd": round(monitor_plan.total_cost_twd),
        "floor_summary": floor_summary,
        "category_summary": category_summary,
        "type_detail": type_detail,
        "sensors": sensor_list,
    }


def export_dashboard_json(
    monitor_plan: MonitorPlan,
    output_path: str | Path,
    project_name: str = "PromptBIM Project",
) -> Path:
    """Export dashboard JSON to a file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = generate_dashboard_json(monitor_plan, project_name)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return output_path
