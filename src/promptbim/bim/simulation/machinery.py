"""Construction machinery 3D models and site entry logic — D1-S1 Task 12.

Provides:
- MachineryDef: definition of a construction machine (type, geometry, entry days)
- MachinerySchedule: schedule of when each machine is on-site
- MachineryPlanner: determines required machinery from a BuildingPlan + schedule
- USD export: adds machinery geometry to an existing USD stage

Usage::

    from promptbim.bim.simulation.machinery import MachineryPlanner
    planner = MachineryPlanner()
    sched = planner.plan(plan, construction_schedule)
    for m in sched.entries:
        print(f"{m.machine_type}: days {m.start_day}–{m.end_day}")
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from promptbim.bim.simulation.scheduler import ConstructionSchedule
    from promptbim.schemas.plan import BuildingPlan


# ============================================================
# Machine definitions
# ============================================================

MACHINE_TYPES = {
    "tower_crane": {
        "name_zh": "塔吊",
        "name_en": "Tower Crane",
        "height_m": 30.0,
        "radius_m": 25.0,
        "phases": ["P01", "P02", "P03", "P04", "P05", "P06", "P07", "S01", "S02", "S03", "S04"],
        "min_stories": 4,  # required when building > 4 stories
        "geometry": "tower_crane",
    },
    "mobile_crane": {
        "name_zh": "移動式吊車",
        "name_en": "Mobile Crane",
        "height_m": 15.0,
        "radius_m": 12.0,
        "phases": ["P01", "P02", "E03", "E05"],
        "min_stories": 1,
        "geometry": "mobile_crane",
    },
    "excavator": {
        "name_zh": "挖土機",
        "name_en": "Excavator",
        "height_m": 3.5,
        "length_m": 8.0,
        "width_m": 3.2,
        "phases": ["E01", "E02", "E03", "E04", "P01"],
        "geometry": "excavator",
    },
    "concrete_pump": {
        "name_zh": "混凝土泵車",
        "name_en": "Concrete Pump Truck",
        "height_m": 4.5,
        "boom_length_m": 42.0,
        "phases": ["E05", "P02", "P03", "P04", "P05", "P06"],
        "geometry": "pump_truck",
    },
    "formwork_system": {
        "name_zh": "模板系統",
        "name_en": "Jump Form / Table Form",
        "height_m": 6.0,
        "phases": ["P03", "P04", "P05", "P06", "P07"],
        "geometry": "formwork",
    },
    "construction_elevator": {
        "name_zh": "施工電梯",
        "name_en": "Construction Hoist",
        "height_m": 40.0,
        "phases": ["P05", "P06", "P07", "P08", "P09", "P10", "P11", "P12", "P13", "P14", "P15", "P16"],
        "min_stories": 3,
        "geometry": "hoist",
    },
    "scissor_lift": {
        "name_zh": "剪刀式升降台",
        "name_en": "Scissor Lift",
        "height_m": 12.0,
        "phases": ["P09", "P10", "P11", "P14"],
        "geometry": "scissor_lift",
    },
}


@dataclass
class MachineryEntry:
    """A construction machine scheduled on-site."""

    machine_type: str
    name_zh: str
    name_en: str
    start_day: int
    end_day: int
    position: tuple[float, float] = (0.0, 0.0)  # site position (x, y)
    notes: str = ""


@dataclass
class MachinerySchedule:
    """Full machinery schedule for a construction project."""

    entries: list[MachineryEntry] = field(default_factory=list)
    total_days: int = 360

    def active_machines(self, day: int) -> list[MachineryEntry]:
        """Return machines on-site at a given day."""
        return [e for e in self.entries if e.start_day <= day <= e.end_day]

    def gantt_data(self) -> list[dict]:
        """Return Gantt-ready data for machinery visualization."""
        return [
            {
                "machine": e.name_zh,
                "type": e.machine_type,
                "start_day": e.start_day,
                "end_day": e.end_day,
                "duration": e.end_day - e.start_day,
                "position": list(e.position),
            }
            for e in sorted(self.entries, key=lambda x: x.start_day)
        ]


class MachineryPlanner:
    """Determine construction machinery requirements and entry/exit schedule.

    D1-S1: Maps construction phases to equipment needs and generates
    a MachinerySchedule with position and timing.
    """

    def plan(
        self,
        plan: "BuildingPlan",
        schedule: "ConstructionSchedule",
    ) -> MachinerySchedule:
        """Generate machinery schedule from a BuildingPlan and ConstructionSchedule.

        Logic:
        1. Determine building height and footprint for crane sizing
        2. For each machine type, find the phase window where it's needed
        3. Add position based on site layout (perimeter of building footprint)
        """
        num_stories = len(plan.stories)
        building_height = sum(s.height_m for s in plan.stories)
        total_days = schedule.total_days

        # Build phase_id → (start_day, end_day) map
        phase_windows: dict[str, tuple[int, int]] = {}
        for sp in schedule.phases:
            phase_windows[sp.phase.phase_id] = (sp.start_day, sp.end_day)

        entries: list[MachineryEntry] = []

        # Site position: outside building footprint NE corner
        cx, cy = 0.0, 0.0
        if plan.building_footprint:
            xs = [p[0] for p in plan.building_footprint]
            ys = [p[1] for p in plan.building_footprint]
            cx = max(xs) + 5.0
            cy = max(ys) + 5.0

        for machine_id, machine_def in MACHINE_TYPES.items():
            # Check minimum story requirement
            min_stories = machine_def.get("min_stories", 0)
            if num_stories < min_stories:
                continue

            # Find day window from phases
            applicable_phases = [
                p for p in machine_def.get("phases", [])
                if p in phase_windows
            ]
            if not applicable_phases:
                continue

            day_starts = [phase_windows[p][0] for p in applicable_phases]
            day_ends = [phase_windows[p][1] for p in applicable_phases]
            start_day = min(day_starts)
            end_day = max(day_ends)

            # Machine-specific position offsets
            pos_x = cx
            pos_y = cy
            if machine_id == "tower_crane":
                pos_x = cx + 3.0
                pos_y = cy + 3.0
            elif machine_id == "excavator":
                pos_x = cx - 8.0
                pos_y = cy - 5.0
            elif machine_id == "construction_elevator":
                pos_x = cx - 3.0
                pos_y = cy
            elif machine_id == "concrete_pump":
                pos_x = cx + 10.0
                pos_y = cy + 2.0

            entries.append(MachineryEntry(
                machine_type=machine_id,
                name_zh=machine_def["name_zh"],
                name_en=machine_def["name_en"],
                start_day=max(0, start_day - 5),  # arrive 5 days before phase
                end_day=min(total_days, end_day + 3),  # leave 3 days after
                position=(round(pos_x, 1), round(pos_y, 1)),
                notes=f"Required for phases: {', '.join(applicable_phases)}",
            ))

        return MachinerySchedule(entries=entries, total_days=total_days)

    def add_to_usd_stage(
        self,
        schedule: MachinerySchedule,
        stage,  # Usd.Stage
        day: int,
    ) -> None:
        """Add active machinery geometry to a USD stage for a given day (D1-S1).

        Generates simplified box meshes for each active machine.
        Requires pxr (OpenUSD).
        """
        try:
            from pxr import Gf, Sdf, UsdGeom, Vt
        except ImportError:
            return

        machinery_root = "/Building/Machinery"
        if not stage.GetPrimAtPath(machinery_root):
            UsdGeom.Xform.Define(stage, machinery_root)

        active = schedule.active_machines(day)
        for entry in active:
            mdef = MACHINE_TYPES.get(entry.machine_type, {})
            h = mdef.get("height_m", 5.0)
            w = mdef.get("width_m", 3.0)
            length = mdef.get("length_m", 5.0)
            x, y = entry.position

            prim_path = f"{machinery_root}/{entry.machine_type}_{entry.start_day}"
            if stage.GetPrimAtPath(prim_path):
                continue

            # Create simple box mesh
            mesh = UsdGeom.Mesh.Define(stage, prim_path)
            pts = [
                Gf.Vec3f(x, y, 0), Gf.Vec3f(x + length, y, 0),
                Gf.Vec3f(x + length, y + w, 0), Gf.Vec3f(x, y + w, 0),
                Gf.Vec3f(x, y, h), Gf.Vec3f(x + length, y, h),
                Gf.Vec3f(x + length, y + w, h), Gf.Vec3f(x, y + w, h),
            ]
            mesh.GetPointsAttr().Set(Vt.Vec3fArray(pts))
            mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray([4, 4, 4, 4, 4, 4]))
            mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray([
                0,1,2,3, 4,7,6,5, 0,4,5,1, 1,5,6,2, 2,6,7,3, 3,7,4,0
            ]))
            p = stage.GetPrimAtPath(prim_path)
            if p:
                p.CreateAttribute("custom:machine_type", Sdf.ValueTypeNames.String).Set(entry.machine_type)
                p.CreateAttribute("custom:machine_name", Sdf.ValueTypeNames.String).Set(entry.name_zh)
