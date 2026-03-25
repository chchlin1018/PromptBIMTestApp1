"""Tests for gui/simulation_tab.py — 4D Simulation GUI."""

import pytest
import pyvista as pv

from promptbim.bim.simulation.scheduler import generate_schedule


def _make_meshes():
    return {
        "ground_slab": pv.Box(bounds=(0, 10, 0, 10, -0.3, 0)),
        "1F_wall_0": pv.Box(bounds=(0, 10, 0, 0.2, 0, 3)),
        "1F_wall_1": pv.Box(bounds=(0, 0.2, 0, 10, 0, 3)),
        "1F_slab": pv.Box(bounds=(0, 10, 0, 10, 3, 3.2)),
        "roof": pv.Box(bounds=(0, 10, 0, 10, 6, 6.2)),
    }


class TestSimulationTabImport:
    def test_import(self):
        from promptbim.gui.simulation_tab import SimulationTab
        assert SimulationTab is not None

    def test_schedule_from_meshes(self):
        """Verify schedule generation works with mesh labels."""
        meshes = _make_meshes()
        sched = generate_schedule(list(meshes.keys()), total_days=360, num_stories=2)
        assert sched.total_days > 0
        assert len(sched.phases) >= 3

    def test_animator_from_meshes(self):
        """Verify animator can be created with mesh data."""
        from promptbim.bim.simulation.animator import ConstructionAnimator
        meshes = _make_meshes()
        sched = generate_schedule(list(meshes.keys()))
        animator = ConstructionAnimator(meshes, sched)
        frame = animator.get_frame_meshes(sched.total_days)
        assert len(frame) > 0
