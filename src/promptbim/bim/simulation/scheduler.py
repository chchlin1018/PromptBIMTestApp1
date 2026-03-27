"""Construction schedule generator for 4D BIM simulation.

Assigns building components to construction phases and computes
start/end days for each phase based on total project duration.

D1-S1 additions:
- regenerate_from_plan(): rebuild schedule when BuildingPlan changes
- ScheduleChangeLink: connects design modifications to schedule updates
"""

from __future__ import annotations

from dataclasses import dataclass, field

from promptbim.bim.simulation.construction_phases import (
    STANDARD_PHASES,
    ConstructionPhase,
    classify_component,
)
from promptbim.debug import get_logger

logger = get_logger("simulation.scheduler")


@dataclass
class ScheduledPhase:
    """A phase with assigned components and time span."""

    phase: ConstructionPhase
    components: list[str] = field(default_factory=list)
    start_day: int = 0
    end_day: int = 0

    @property
    def duration_days(self) -> int:
        return self.end_day - self.start_day


@dataclass
class ConstructionSchedule:
    """Complete construction schedule with all phases."""

    total_days: int = 0
    phases: list[ScheduledPhase] = field(default_factory=list)

    @property
    def active_phase_ids(self) -> list[str]:
        """Phase IDs that have at least one component."""
        return [sp.phase.phase_id for sp in self.phases if sp.components]


def generate_schedule(
    component_labels: list[str],
    total_days: int = 360,
    num_stories: int = 1,
) -> ConstructionSchedule:
    """Generate a construction schedule from component labels.

    Args:
        component_labels: List of mesh label strings (e.g. '1F_wall_0', 'roof').
        total_days: Total construction duration in days.
        num_stories: Number of stories (scales structural phases).

    Returns:
        A ConstructionSchedule with phases and day assignments.
    """
    # Group components by phase
    phase_components: dict[str, list[str]] = {}
    for label in component_labels:
        phase_id = classify_component(label)
        if phase_id:
            phase_components.setdefault(phase_id, []).append(label)

    # Scale total days by building size
    scale = max(1.0, num_stories / 3.0)
    adjusted_days = int(total_days * scale)

    # Build scheduled phases (only include phases with components, plus
    # always include P01 site prep as a virtual phase)
    if "P01" not in phase_components:
        phase_components["P01"] = ["site_preparation"]

    scheduled: list[ScheduledPhase] = []
    current_day = 0

    for phase_def in STANDARD_PHASES:
        comps = phase_components.get(phase_def.phase_id, [])
        if not comps:
            continue
        duration = max(1, int(adjusted_days * phase_def.duration_ratio))
        sp = ScheduledPhase(
            phase=phase_def,
            components=comps,
            start_day=current_day,
            end_day=current_day + duration,
        )
        scheduled.append(sp)
        current_day += duration

    for sp in scheduled:
        logger.debug(
            "Phase %s: day %d-%d (%d days), %d components",
            sp.phase.phase_id,
            sp.start_day,
            sp.end_day,
            sp.duration_days,
            len(sp.components),
        )
    logger.debug("Schedule: %d phases, total %d days", len(scheduled), current_day)

    return ConstructionSchedule(
        total_days=current_day,
        phases=scheduled,
    )


def get_visible_components(schedule: ConstructionSchedule, day: int) -> dict[str, str]:
    """Get component visibility state at a given day.

    Returns dict mapping component label -> state.
    States: 'hidden', 'in_progress', 'completed'.
    """
    result: dict[str, str] = {}
    for sp in schedule.phases:
        for comp in sp.components:
            if day < sp.start_day:
                result[comp] = "hidden"
            elif day < sp.end_day:
                result[comp] = "in_progress"
            else:
                result[comp] = "completed"
    return result


def get_active_phase(schedule: ConstructionSchedule, day: int) -> ScheduledPhase | None:
    """Get the phase that is active at a given day."""
    for sp in schedule.phases:
        if sp.start_day <= day < sp.end_day:
            return sp
    return None


# ============================================================
# D1-S1: Design Change → 4D Auto-update
# ============================================================

def regenerate_from_plan(
    plan: "BuildingPlan",
    total_days: int | None = None,
    include_excavation: bool = False,
    include_steel: bool = False,
) -> ConstructionSchedule:
    """Rebuild the construction schedule from a (modified) BuildingPlan (D1-S1).

    Called automatically after design modifications to keep the 4D simulation
    in sync with the current building geometry.

    Args:
        plan: Current BuildingPlan (after modification).
        total_days: Override total duration; defaults to num_stories × 120 days.
        include_excavation: Add excavation phases.
        include_steel: Add steel erection phases.
    """
    from promptbim.bim.simulation.construction_phases import (
        get_extended_phases,
        classify_component_extended,
    )

    num_stories = len(plan.stories)
    if total_days is None:
        total_days = max(180, num_stories * 120)

    # Build component labels from plan
    component_labels: list[str] = []
    for story in plan.stories:
        for i, _ in enumerate(story.walls):
            component_labels.append(f"{story.name}_wall_{i}")
        for i, _ in enumerate(story.spaces):
            component_labels.append(f"{story.name}_slab_{i}")
    if plan.stories:
        component_labels.append("roof")

    # Get phase set
    phases = get_extended_phases(include_excavation=include_excavation, include_steel=include_steel)
    phase_map = {p.phase_id: p for p in phases}

    # Group components by phase
    phase_components: dict[str, list[str]] = {}
    for label in component_labels:
        phase_id = classify_component_extended(label)
        if phase_id:
            phase_components.setdefault(phase_id, []).append(label)

    if "P01" not in phase_components:
        phase_components["P01"] = ["site_preparation"]

    scale = max(1.0, num_stories / 3.0)
    adjusted_days = int(total_days * scale)
    scheduled: list[ScheduledPhase] = []
    current_day = 0

    for phase_def in phases:
        comps = phase_components.get(phase_def.phase_id, [])
        if not comps:
            continue
        duration = max(1, int(adjusted_days * phase_def.duration_ratio))
        sp = ScheduledPhase(
            phase=phase_def,
            components=comps,
            start_day=current_day,
            end_day=current_day + duration,
        )
        scheduled.append(sp)
        current_day += duration

    logger.debug(
        "regenerate_from_plan: %d stories, %d phases, %d days",
        num_stories, len(scheduled), current_day,
    )
    return ConstructionSchedule(total_days=current_day, phases=scheduled)


class ScheduleChangeLink:
    """Links design modifications to automatic 4D schedule regeneration (D1-S1).

    Usage::

        link = ScheduleChangeLink(plan, schedule)
        new_schedule = link.apply_modification(modified_plan, "Added 2 stories")
        print(link.change_log)
    """

    def __init__(
        self,
        original_plan: "BuildingPlan",
        original_schedule: ConstructionSchedule,
    ) -> None:
        self._original_plan = original_plan
        self._original_schedule = original_schedule
        self._current_schedule = original_schedule
        self.change_log: list[dict] = []

    @property
    def current_schedule(self) -> ConstructionSchedule:
        return self._current_schedule

    def apply_modification(
        self,
        modified_plan: "BuildingPlan",
        modification_desc: str = "",
        total_days: int | None = None,
    ) -> ConstructionSchedule:
        """Regenerate schedule from a modified plan and record the change.

        D1-S1: Called automatically by Orchestrator.modify() to keep 4D in sync.
        """
        prev_schedule = self._current_schedule
        new_schedule = regenerate_from_plan(modified_plan, total_days=total_days)
        self._current_schedule = new_schedule

        # Record change
        old_days = prev_schedule.total_days
        new_days = new_schedule.total_days
        day_delta = new_days - old_days

        self.change_log.append({
            "modification": modification_desc,
            "old_total_days": old_days,
            "new_total_days": new_days,
            "day_delta": day_delta,
            "old_phases": len(prev_schedule.phases),
            "new_phases": len(new_schedule.phases),
        })

        logger.info(
            "ScheduleChangeLink: '%s' → %d days (delta=%+d)",
            modification_desc, new_days, day_delta,
        )
        return new_schedule

    def revert_to_original(self) -> ConstructionSchedule:
        """Revert schedule to the original baseline."""
        self._current_schedule = self._original_schedule
        self.change_log.append({"modification": "revert_to_original", "day_delta": 0})
        return self._original_schedule
