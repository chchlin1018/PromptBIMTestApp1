"""Construction schedule generator for 4D BIM simulation.

Assigns building components to construction phases and computes
start/end days for each phase based on total project duration.
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
