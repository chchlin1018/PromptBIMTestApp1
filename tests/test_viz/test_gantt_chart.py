"""Tests for viz/gantt_chart.py — Gantt chart visualization."""

import pytest

from promptbim.bim.simulation.scheduler import generate_schedule


def _sample_schedule():
    labels = [
        "ground_slab", "1F_wall_0", "1F_wall_1",
        "1F_slab", "2F_wall_0", "2F_slab", "roof",
    ]
    return generate_schedule(labels, total_days=360, num_stories=2)


class TestGanttChartImport:
    def test_import(self):
        from promptbim.viz.gantt_chart import GanttChart
        assert GanttChart is not None

    def test_schedule_for_chart(self):
        """Verify schedule has the data needed for the Gantt chart."""
        sched = _sample_schedule()
        assert sched.total_days > 0
        assert len(sched.phases) >= 3
        for sp in sched.phases:
            assert sp.phase.name
            assert sp.start_day >= 0
            assert sp.end_day > sp.start_day
            assert len(sp.phase.color) == 3
