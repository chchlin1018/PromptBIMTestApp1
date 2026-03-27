"""Demo-1 export utilities: JSON schedule, CSV cost, SVG site plan summary.

Provides a single `export_demo_package` function that writes all
Demo-1 deliverables to a target directory.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING

from promptbim.debug import get_logger

if TYPE_CHECKING:
    from promptbim.bim.simulation.scheduler import ConstructionSchedule
    from promptbim.bim.cost.estimator import CostEstimate
    from promptbim.schemas.plan import BuildingPlan

logger = get_logger("bim.export")


# ---------------------------------------------------------------------------
# JSON Schedule Export
# ---------------------------------------------------------------------------

def export_schedule_json(schedule: "ConstructionSchedule", path: Path) -> Path:
    """Export construction schedule as JSON."""
    data = {
        "total_days": schedule.total_days,
        "phases": [
            {
                "phase_id": sp.phase.phase_id,
                "name": sp.phase.name,
                "start_day": sp.start_day,
                "end_day": sp.end_day,
                "duration_days": sp.duration_days,
                "color": sp.phase.color,
            }
            for sp in schedule.phases
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    logger.info("Schedule JSON exported: %s", path)
    return path


# ---------------------------------------------------------------------------
# CSV Cost Export
# ---------------------------------------------------------------------------

def export_cost_csv(estimate: "CostEstimate", path: Path) -> Path:
    """Export cost estimate as CSV."""
    rows = [
        ["Category", "Item", "Unit", "Quantity", "Unit Cost (NT$)", "Total (NT$)"],
    ]
    # Breakdown by category if available
    if hasattr(estimate, "items") and estimate.items:
        for item in estimate.items:
            rows.append([
                getattr(item, "category", "—"),
                getattr(item, "name", "—"),
                getattr(item, "unit", "—"),
                f"{getattr(item, 'quantity', 0):.2f}",
                f"{getattr(item, 'unit_cost', 0):.0f}",
                f"{getattr(item, 'total', 0):.0f}",
            ])
    else:
        rows.append(["Total", "Building Construction", "式", "1",
                     f"{estimate.total_cost_twd:.0f}", f"{estimate.total_cost_twd:.0f}"])

    rows.append(["", "", "", "", "TOTAL", f"{estimate.total_cost_twd:.0f}"])
    path.write_text(
        "\n".join(",".join(str(c) for c in row) for row in rows),
        encoding="utf-8-sig",
    )
    logger.info("Cost CSV exported: %s", path)
    return path


# ---------------------------------------------------------------------------
# Plan JSON Export (BIM metadata)
# ---------------------------------------------------------------------------

def export_plan_json(plan: "BuildingPlan", path: Path) -> Path:
    """Export BuildingPlan metadata as JSON."""
    data = {
        "name": plan.name,
        "schema_version": plan.schema_version,
        "building_bcr": plan.building_bcr,
        "building_far": plan.building_far,
        "stories": [
            {
                "name": s.name,
                "elevation_m": s.elevation_m,
                "height_m": s.height_m,
                "gfa_sqm": s.gfa_sqm,
                "spaces": [
                    {
                        "name": sp.name,
                        "space_type": sp.space_type,
                        "area_sqm": sp.area_sqm,
                    }
                    for sp in s.spaces
                ],
            }
            for s in plan.stories
        ],
        "roof": {
            "roof_type": plan.roof.roof_type,
            "slope_degrees": plan.roof.slope_degrees,
            "overhang_m": plan.roof.overhang_m,
        },
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    logger.info("Plan JSON exported: %s", path)
    return path


# ---------------------------------------------------------------------------
# Demo Package Export
# ---------------------------------------------------------------------------

def export_demo_package(
    plan: "BuildingPlan",
    scene_id: str,
    output_dir: Path | str,
    schedule: "ConstructionSchedule | None" = None,
    estimate: "CostEstimate | None" = None,
) -> dict[str, Path]:
    """Export a complete Demo-1 deliverable package.

    Creates:
      {output_dir}/
        {scene_id}_plan.json
        {scene_id}_schedule.json   (if schedule provided)
        {scene_id}_cost.csv        (if estimate provided)

    Returns dict mapping filename stem → Path.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    result: dict[str, Path] = {}

    # Plan JSON
    plan_path = out / f"{scene_id}_plan.json"
    result["plan"] = export_plan_json(plan, plan_path)

    # Schedule JSON
    if schedule is not None:
        sched_path = out / f"{scene_id}_schedule.json"
        result["schedule"] = export_schedule_json(schedule, sched_path)

    # Cost CSV
    if estimate is not None:
        cost_path = out / f"{scene_id}_cost.csv"
        result["cost"] = export_cost_csv(estimate, cost_path)

    logger.info("Demo package exported to %s: %s", out, list(result.keys()))
    return result
