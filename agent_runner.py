#!/usr/bin/env python3
"""Agent Runner — bridges C++ AgentBridge ↔ Python Orchestrator via JSON stdio.

Protocol:
  - Input:  one JSON object per line on stdin
  - Output: one JSON object per line on stdout (status/result/delta/error)
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

# Ensure promptbim is importable
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mesh_serializer import serialize_plan_to_mesh
from promptbim.agents.orchestrator import Orchestrator, PipelineStatus
from promptbim.schemas.land import LandParcel


def emit(obj: dict) -> None:
    """Write a JSON line to stdout and flush."""
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def make_status_callback():
    """Create a PipelineStatus callback that emits JSON status lines."""
    def on_status(status: PipelineStatus):
        emit({
            "type": "status",
            "stage": status.stage,
            "message": status.message,
            "progress": status.progress,
        })
    return on_status


def build_land_parcel(land_data: dict) -> LandParcel:
    """Build a LandParcel from the simplified JSON land data."""
    w = land_data.get("width", 100)
    d = land_data.get("depth", 80)
    boundary = [(0, 0), (w, 0), (w, d), (0, d)]
    return LandParcel(
        boundary=boundary,
        area_sqm=float(w * d),
    )


def handle_generate(orch: Orchestrator, data: dict) -> None:
    """Handle a 'generate' request."""
    prompt = data.get("prompt", "")
    land_data = data.get("land", {"width": 100, "depth": 80})
    land = build_land_parcel(land_data)

    emit({"type": "status", "message": "Starting generation...", "progress": 0.0})

    result = orch.generate(prompt, land, use_cache=False)

    # Serialize mesh from plan
    model_json = {}
    if orch.plan:
        model_json = serialize_plan_to_mesh(orch.plan)

    # Cost
    cost_json = {}
    try:
        cost_est = orch.compute_cost()
        if cost_est:
            cost_json = cost_est.to_dict()
    except Exception:
        pass

    # Schedule
    schedule_json = {}
    try:
        sched = orch.compute_schedule()
        if sched:
            schedule_json = {
                "total_days": sched.total_days,
                "phases": [
                    {
                        "phase": p.phase.value if hasattr(p.phase, "value") else str(p.phase),
                        "start_day": p.start_day,
                        "end_day": p.end_day,
                        "duration_days": p.duration_days,
                        "components": p.components,
                    }
                    for p in sched.phases
                ],
            }
    except Exception:
        pass

    emit({
        "type": "result",
        "model": model_json,
        "cost": cost_json,
        "schedule": schedule_json,
        "summary": result.summary if result else {},
        "success": result.success if result else False,
    })


def handle_modify(orch: Orchestrator, data: dict) -> None:
    """Handle a 'modify' request."""
    intent = data.get("intent", "")
    emit({"type": "status", "message": f"Modifying: {intent}", "progress": 0.0})

    plan, mod_record = orch.modify(intent)

    model_json = {}
    if plan:
        model_json = serialize_plan_to_mesh(plan)

    delta_json = {}
    if mod_record:
        delta_json = {
            "description": mod_record.description if hasattr(mod_record, "description") else str(mod_record),
        }

    # Recompute cost
    cost_json = {}
    try:
        cost_est = orch.compute_cost()
        if cost_est:
            cost_json = cost_est.to_dict()
    except Exception:
        pass

    schedule_json = {}
    try:
        sched = orch.compute_schedule()
        if sched:
            schedule_json = {
                "total_days": sched.total_days,
                "phases": [
                    {
                        "phase": p.phase.value if hasattr(p.phase, "value") else str(p.phase),
                        "start_day": p.start_day,
                        "end_day": p.end_day,
                        "duration_days": p.duration_days,
                        "components": p.components,
                    }
                    for p in sched.phases
                ],
            }
    except Exception:
        pass

    emit({
        "type": "delta",
        "model": model_json,
        "cost": cost_json,
        "schedule": schedule_json,
        "modification": delta_json,
    })


def handle_get_cost(orch: Orchestrator) -> None:
    """Handle a 'get_cost' request."""
    try:
        cost_est = orch.compute_cost()
        if cost_est:
            emit({"type": "result", "cost": cost_est.to_dict()})
        else:
            emit({"type": "error", "message": "No plan available for cost estimation"})
    except Exception as e:
        emit({"type": "error", "message": f"Cost computation failed: {e}"})


def handle_get_schedule(orch: Orchestrator) -> None:
    """Handle a 'get_schedule' request."""
    try:
        sched = orch.compute_schedule()
        if sched:
            emit({
                "type": "result",
                "schedule": {
                    "total_days": sched.total_days,
                    "phases": [
                        {
                            "phase": p.phase.value if hasattr(p.phase, "value") else str(p.phase),
                            "start_day": p.start_day,
                            "end_day": p.end_day,
                            "duration_days": p.duration_days,
                            "components": p.components,
                        }
                        for p in sched.phases
                    ],
                },
            })
        else:
            emit({"type": "error", "message": "No plan available for schedule"})
    except Exception as e:
        emit({"type": "error", "message": f"Schedule computation failed: {e}"})


def main() -> None:
    """Main loop: read JSON lines from stdin, dispatch to handlers."""
    orch = Orchestrator(
        output_dir="output",
        on_status=make_status_callback(),
    )

    emit({"type": "status", "message": "Agent runner ready", "progress": 0.0})

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            emit({"type": "error", "message": f"Invalid JSON: {e}"})
            continue

        req_type = data.get("type", "")

        try:
            if req_type == "generate":
                handle_generate(orch, data)
            elif req_type == "modify":
                handle_modify(orch, data)
            elif req_type == "get_cost":
                handle_get_cost(orch)
            elif req_type == "get_schedule":
                handle_get_schedule(orch)
            else:
                emit({"type": "error", "message": f"Unknown request type: {req_type}"})
        except Exception as e:
            emit({
                "type": "error",
                "message": f"Handler error ({req_type}): {e}",
                "traceback": traceback.format_exc(),
            })


if __name__ == "__main__":
    main()
