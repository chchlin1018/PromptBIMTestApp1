"""Schedule change delta analysis and Gantt comparison — D1-S1 Task 15.

Computes the difference in construction schedules before and after a
design modification and produces Gantt-chart-ready comparison data.

Usage::

    from promptbim.bim.simulation.schedule_delta import ScheduleDeltaAnalyzer
    analyzer = ScheduleDeltaAnalyzer()
    report = analyzer.compare(schedule_before, schedule_after, "Added 2 stories")
    print(report.summary_text())
    gantt = report.gantt_comparison()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from promptbim.bim.simulation.scheduler import ConstructionSchedule, ScheduledPhase


@dataclass
class PhaseDeltaItem:
    """Duration/date change for a single construction phase."""

    phase_id: str
    phase_name: str
    start_before: int
    end_before: int
    start_after: int
    end_after: int
    duration_before: int
    duration_after: int
    duration_delta: int
    start_delta: int
    is_new: bool = False      # phase only in after
    is_removed: bool = False  # phase only in before
    color: tuple[float, float, float] = (0.5, 0.5, 0.5)


@dataclass
class ScheduleDeltaReport:
    """Full schedule change analysis report.

    D1-S1: Bridges design modification → schedule impact.
    Produced by ScheduleDeltaAnalyzer.compare().
    """

    modification_desc: str = ""

    total_days_before: int = 0
    total_days_after: int = 0
    total_days_delta: int = 0

    phases_before: int = 0
    phases_after: int = 0
    phases_added: int = 0
    phases_removed: int = 0

    phase_deltas: list[PhaseDeltaItem] = field(default_factory=list)

    def summary_text(self) -> str:
        """Human-readable summary string."""
        sign = "+" if self.total_days_delta >= 0 else ""
        lines = [
            f"Schedule Delta Report",
            f"Modification: {self.modification_desc or 'N/A'}",
            "",
            f"  Before: {self.total_days_before} days ({self.phases_before} phases)",
            f"  After:  {self.total_days_after} days ({self.phases_after} phases)",
            f"  Delta:  {sign}{self.total_days_delta} days",
            "",
            "Phase Breakdown:",
        ]
        for item in sorted(self.phase_deltas, key=lambda x: abs(x.duration_delta), reverse=True):
            if item.is_new:
                lines.append(f"  [NEW]    {item.phase_id} {item.phase_name}: {item.duration_after}d")
            elif item.is_removed:
                lines.append(f"  [REMOVED]{item.phase_id} {item.phase_name}: was {item.duration_before}d")
            elif item.duration_delta != 0:
                sign_i = "+" if item.duration_delta >= 0 else ""
                lines.append(
                    f"  {item.phase_id} {item.phase_name:25s}: "
                    f"{sign_i}{item.duration_delta}d "
                    f"({item.duration_before}→{item.duration_after}d)"
                )
        return "\n".join(lines)

    def gantt_comparison(self) -> dict:
        """Return Gantt-chart-ready comparison data.

        Returns a dict with:
        - before: [{phase_id, name, start, end, duration, color}]
        - after:  [{phase_id, name, start, end, duration, color}]
        - delta:  [{phase_id, name, duration_before, duration_after, duration_delta, start_delta}]
        - summary: {total_days_before, total_days_after, delta, phases_added, phases_removed}
        """
        before_rows = []
        after_rows = []
        delta_rows = []

        for item in self.phase_deltas:
            color_hex = _rgb_to_hex(item.color)
            if not item.is_new:
                before_rows.append({
                    "phase_id": item.phase_id,
                    "name": item.phase_name,
                    "start": item.start_before,
                    "end": item.end_before,
                    "duration": item.duration_before,
                    "color": color_hex,
                })
            if not item.is_removed:
                after_rows.append({
                    "phase_id": item.phase_id,
                    "name": item.phase_name,
                    "start": item.start_after,
                    "end": item.end_after,
                    "duration": item.duration_after,
                    "color": color_hex,
                    "is_new": item.is_new,
                })
            delta_rows.append({
                "phase_id": item.phase_id,
                "name": item.phase_name,
                "duration_before": item.duration_before,
                "duration_after": item.duration_after,
                "duration_delta": item.duration_delta,
                "start_delta": item.start_delta,
                "is_new": item.is_new,
                "is_removed": item.is_removed,
                "bar_color": "#FF4444" if item.duration_delta > 0 else "#44AA44" if item.duration_delta < 0 else "#888888",
            })

        return {
            "before": sorted(before_rows, key=lambda x: x["start"]),
            "after": sorted(after_rows, key=lambda x: x["start"]),
            "delta": sorted(delta_rows, key=lambda x: abs(x["duration_delta"]), reverse=True),
            "summary": {
                "total_days_before": self.total_days_before,
                "total_days_after": self.total_days_after,
                "total_days_delta": self.total_days_delta,
                "phases_before": self.phases_before,
                "phases_after": self.phases_after,
                "phases_added": self.phases_added,
                "phases_removed": self.phases_removed,
            },
        }

    def critical_path_changes(self) -> list[dict]:
        """Return phases whose start date shifted (critical path impact)."""
        return [
            {
                "phase_id": item.phase_id,
                "name": item.phase_name,
                "start_delta": item.start_delta,
                "duration_delta": item.duration_delta,
            }
            for item in self.phase_deltas
            if item.start_delta != 0 and not item.is_new and not item.is_removed
        ]


def _rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    r, g, b = rgb
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))


class ScheduleDeltaAnalyzer:
    """Analyze schedule changes between two ConstructionSchedule versions (D1-S1).

    Computes phase-level duration and start-date deltas, identifies added/
    removed phases, and generates Gantt comparison data.
    """

    def compare(
        self,
        schedule_before: "ConstructionSchedule",
        schedule_after: "ConstructionSchedule",
        modification_desc: str = "",
    ) -> ScheduleDeltaReport:
        """Compare two ConstructionSchedule objects and return a ScheduleDeltaReport.

        Args:
            schedule_before: Original schedule.
            schedule_after: Modified schedule.
            modification_desc: Human-readable description of the design change.
        """
        before_map: dict[str, "ScheduledPhase"] = {
            sp.phase.phase_id: sp for sp in schedule_before.phases
        }
        after_map: dict[str, "ScheduledPhase"] = {
            sp.phase.phase_id: sp for sp in schedule_after.phases
        }

        all_phase_ids = sorted(set(before_map.keys()) | set(after_map.keys()))
        phase_deltas: list[PhaseDeltaItem] = []
        phases_added = 0
        phases_removed = 0

        for pid in all_phase_ids:
            sp_before = before_map.get(pid)
            sp_after = after_map.get(pid)

            is_new = sp_before is None
            is_removed = sp_after is None

            if is_new:
                phases_added += 1
                phase_deltas.append(PhaseDeltaItem(
                    phase_id=pid,
                    phase_name=sp_after.phase.name,  # type: ignore[union-attr]
                    start_before=0,
                    end_before=0,
                    start_after=sp_after.start_day,  # type: ignore[union-attr]
                    end_after=sp_after.end_day,  # type: ignore[union-attr]
                    duration_before=0,
                    duration_after=sp_after.duration_days,  # type: ignore[union-attr]
                    duration_delta=sp_after.duration_days,  # type: ignore[union-attr]
                    start_delta=sp_after.start_day,  # type: ignore[union-attr]
                    is_new=True,
                    color=sp_after.phase.color,  # type: ignore[union-attr]
                ))
            elif is_removed:
                phases_removed += 1
                phase_deltas.append(PhaseDeltaItem(
                    phase_id=pid,
                    phase_name=sp_before.phase.name,  # type: ignore[union-attr]
                    start_before=sp_before.start_day,  # type: ignore[union-attr]
                    end_before=sp_before.end_day,  # type: ignore[union-attr]
                    start_after=0,
                    end_after=0,
                    duration_before=sp_before.duration_days,  # type: ignore[union-attr]
                    duration_after=0,
                    duration_delta=-sp_before.duration_days,  # type: ignore[union-attr]
                    start_delta=0,
                    is_removed=True,
                    color=sp_before.phase.color,  # type: ignore[union-attr]
                ))
            else:
                phase_deltas.append(PhaseDeltaItem(
                    phase_id=pid,
                    phase_name=sp_after.phase.name,
                    start_before=sp_before.start_day,
                    end_before=sp_before.end_day,
                    start_after=sp_after.start_day,
                    end_after=sp_after.end_day,
                    duration_before=sp_before.duration_days,
                    duration_after=sp_after.duration_days,
                    duration_delta=sp_after.duration_days - sp_before.duration_days,
                    start_delta=sp_after.start_day - sp_before.start_day,
                    color=sp_after.phase.color,
                ))

        total_days_delta = schedule_after.total_days - schedule_before.total_days

        return ScheduleDeltaReport(
            modification_desc=modification_desc,
            total_days_before=schedule_before.total_days,
            total_days_after=schedule_after.total_days,
            total_days_delta=total_days_delta,
            phases_before=len(schedule_before.phases),
            phases_after=len(schedule_after.phases),
            phases_added=phases_added,
            phases_removed=phases_removed,
            phase_deltas=phase_deltas,
        )

    def compare_from_plans(
        self,
        plan_before: "BuildingPlan",
        plan_after: "BuildingPlan",
        modification_desc: str = "",
        total_days: int | None = None,
    ) -> ScheduleDeltaReport:
        """Build schedules from two plans and compare them (convenience method).

        D1-S1: Called from UI when user modifies building and wants to see
        the schedule impact immediately.
        """
        from promptbim.bim.simulation.scheduler import regenerate_from_plan

        sched_before = regenerate_from_plan(plan_before, total_days=total_days)
        sched_after = regenerate_from_plan(plan_after, total_days=total_days)
        return self.compare(sched_before, sched_after, modification_desc)


# TYPE_CHECKING import guard
from typing import TYPE_CHECKING  # noqa: E402, F811
if TYPE_CHECKING:
    from promptbim.schemas.plan import BuildingPlan  # noqa: F401
