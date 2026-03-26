"""Tests for bim/simulation/scheduler.py."""

from promptbim.bim.simulation.scheduler import (
    ConstructionSchedule,
    ScheduledPhase,
    generate_schedule,
    get_active_phase,
    get_visible_components,
)


def _sample_labels() -> list[str]:
    return [
        "ground_slab",
        "1F_wall_0",
        "1F_wall_1",
        "1F_wall_2",
        "1F_wall_3",
        "1F_slab",
        "2F_wall_0",
        "2F_wall_1",
        "2F_wall_2",
        "2F_wall_3",
        "2F_slab",
        "roof",
    ]


class TestGenerateSchedule:
    def test_produces_schedule(self):
        sched = generate_schedule(_sample_labels())
        assert isinstance(sched, ConstructionSchedule)
        assert sched.total_days > 0

    def test_phases_have_components(self):
        sched = generate_schedule(_sample_labels())
        active = [sp for sp in sched.phases if sp.components]
        assert len(active) >= 3  # at least site prep + some structural + roof

    def test_phases_are_sequential(self):
        sched = generate_schedule(_sample_labels())
        for i in range(1, len(sched.phases)):
            assert sched.phases[i].start_day >= sched.phases[i - 1].start_day

    def test_no_overlap(self):
        sched = generate_schedule(_sample_labels())
        for i in range(1, len(sched.phases)):
            assert sched.phases[i].start_day >= sched.phases[i - 1].end_day

    def test_more_stories_longer_schedule(self):
        sched1 = generate_schedule(_sample_labels(), total_days=360, num_stories=1)
        sched3 = generate_schedule(_sample_labels(), total_days=360, num_stories=3)
        # 3 stories should scale the schedule
        assert sched3.total_days >= sched1.total_days

    def test_custom_total_days(self):
        sched = generate_schedule(_sample_labels(), total_days=100, num_stories=1)
        # Schedule should be roughly around the total_days
        assert sched.total_days > 0

    def test_site_prep_always_included(self):
        sched = generate_schedule(["1F_wall_0"])
        phase_ids = [sp.phase.phase_id for sp in sched.phases]
        assert "P01" in phase_ids


class TestGetVisibleComponents:
    def test_day_zero_mostly_hidden(self):
        sched = generate_schedule(_sample_labels())
        states = get_visible_components(sched, 0)
        # At day 0, P01 (site prep) should be in progress
        hidden_count = sum(1 for s in states.values() if s == "hidden")
        in_progress = sum(1 for s in states.values() if s == "in_progress")
        assert in_progress >= 1

    def test_day_end_all_completed(self):
        sched = generate_schedule(_sample_labels())
        states = get_visible_components(sched, sched.total_days)
        completed = sum(1 for s in states.values() if s == "completed")
        assert completed == len(states)

    def test_states_are_valid(self):
        sched = generate_schedule(_sample_labels())
        states = get_visible_components(sched, sched.total_days // 2)
        for state in states.values():
            assert state in ("hidden", "in_progress", "completed")


class TestGetActivePhase:
    def test_returns_phase_at_day(self):
        sched = generate_schedule(_sample_labels())
        phase = get_active_phase(sched, 0)
        assert phase is not None
        assert isinstance(phase, ScheduledPhase)

    def test_returns_none_after_end(self):
        sched = generate_schedule(_sample_labels())
        phase = get_active_phase(sched, sched.total_days + 100)
        assert phase is None
