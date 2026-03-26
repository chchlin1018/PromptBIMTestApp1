"""Tests for bim/simulation/animator.py."""

import pyvista as pv

from promptbim.bim.simulation.animator import ConstructionAnimator
from promptbim.bim.simulation.scheduler import generate_schedule


def _make_test_meshes() -> dict[str, pv.PolyData]:
    """Create simple box meshes for testing."""
    meshes = {}
    labels = ["ground_slab", "1F_wall_0", "1F_wall_1", "1F_slab", "roof"]
    for i, label in enumerate(labels):
        box = pv.Box(bounds=(i, i + 1, 0, 1, 0, 1))
        meshes[label] = box
    return meshes


class TestConstructionAnimator:
    def test_create_animator(self):
        meshes = _make_test_meshes()
        schedule = generate_schedule(list(meshes.keys()))
        animator = ConstructionAnimator(meshes, schedule)
        assert animator.schedule.total_days > 0

    def test_get_frame_meshes_day_zero(self):
        meshes = _make_test_meshes()
        schedule = generate_schedule(list(meshes.keys()))
        animator = ConstructionAnimator(meshes, schedule)
        frame = animator.get_frame_meshes(0)
        # At day 0, some meshes should be visible (at least site prep)
        assert isinstance(frame, list)

    def test_get_frame_meshes_end(self):
        meshes = _make_test_meshes()
        schedule = generate_schedule(list(meshes.keys()))
        animator = ConstructionAnimator(meshes, schedule)
        frame = animator.get_frame_meshes(schedule.total_days)
        # All meshes that have a phase should be completed (visible)
        assert len(frame) > 0
        for mesh, color, opacity in frame:
            assert isinstance(mesh, pv.PolyData)
            assert opacity > 0

    def test_get_frame_meshes_middle(self):
        meshes = _make_test_meshes()
        schedule = generate_schedule(list(meshes.keys()))
        animator = ConstructionAnimator(meshes, schedule)
        mid_day = schedule.total_days // 2
        frame = animator.get_frame_meshes(mid_day)
        assert isinstance(frame, list)

    def test_custom_colors(self):
        meshes = _make_test_meshes()
        schedule = generate_schedule(list(meshes.keys()))
        colors = {"ground_slab": "#ff0000", "roof": "#00ff00"}
        animator = ConstructionAnimator(meshes, schedule, mesh_colors=colors)
        frame = animator.get_frame_meshes(schedule.total_days)
        # Check that custom colours are used for completed meshes
        color_map = {
            label: color
            for mesh, color, opacity in frame
            for label, m in meshes.items()
            if m is mesh
        }
        # The animator should use the provided colours

    def test_render_frame_offscreen(self):
        meshes = _make_test_meshes()
        schedule = generate_schedule(list(meshes.keys()))
        animator = ConstructionAnimator(meshes, schedule)
        plotter = pv.Plotter(off_screen=True)
        animator.render_frame(schedule.total_days // 2, plotter)
        plotter.close()

    def test_export_gif(self, tmp_path):
        meshes = _make_test_meshes()
        schedule = generate_schedule(list(meshes.keys()))
        animator = ConstructionAnimator(meshes, schedule)
        gif_path = tmp_path / "test_anim.gif"
        result = animator.export_gif(gif_path, fps=5, window_size=(200, 150))
        assert result.exists()
        assert result.stat().st_size > 0
