"""PyVista 4D construction animation engine.

Renders construction progress frames showing components as:
- Hidden (not started)
- In-progress (semi-transparent orange)
- Completed (normal colour)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pyvista as pv

from promptbim.bim.simulation.scheduler import (
    ConstructionSchedule,
    get_visible_components,
)

if TYPE_CHECKING:
    pass


# Colours for rendering states
_COLOR_IN_PROGRESS = "orange"
_OPACITY_IN_PROGRESS = 0.5
_COLOR_COMPLETED = "lightgray"
_OPACITY_COMPLETED = 1.0


class ConstructionAnimator:
    """4D construction animation engine using PyVista."""

    def __init__(
        self,
        building_meshes: dict[str, pv.PolyData],
        schedule: ConstructionSchedule,
        mesh_colors: dict[str, str] | None = None,
    ) -> None:
        self.meshes = building_meshes
        self.schedule = schedule
        self.mesh_colors = mesh_colors or {}

    def render_frame(self, day: int, plotter: pv.Plotter) -> None:
        """Render the construction state at a given day onto the plotter."""
        states = get_visible_components(self.schedule, day)

        for label, mesh in self.meshes.items():
            state = states.get(label, "hidden")
            if state == "hidden":
                continue
            elif state == "in_progress":
                plotter.add_mesh(
                    mesh,
                    color=_COLOR_IN_PROGRESS,
                    opacity=_OPACITY_IN_PROGRESS,
                    name=label,
                )
            else:  # completed
                color = self.mesh_colors.get(label, _COLOR_COMPLETED)
                plotter.add_mesh(
                    mesh,
                    color=color,
                    opacity=_OPACITY_COMPLETED,
                    name=label,
                )

    def export_gif(
        self,
        output_path: str | Path,
        fps: int = 10,
        window_size: tuple[int, int] = (800, 600),
    ) -> Path:
        """Export construction animation as a GIF.

        Args:
            output_path: Path for the output GIF file.
            fps: Frames per second.
            window_size: Render window size (width, height).

        Returns:
            Path to the exported GIF.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        total_days = self.schedule.total_days
        # Generate ~fps*10 frames total (about 10 seconds)
        num_frames = min(fps * 10, total_days)
        step = max(1, total_days // num_frames)

        plotter = pv.Plotter(off_screen=True, window_size=window_size)
        plotter.open_gif(str(output_path), fps=fps)

        for day in range(0, total_days + 1, step):
            plotter.clear()
            self.render_frame(day, plotter)
            # Set camera
            plotter.reset_camera()
            plotter.camera.azimuth = 30
            plotter.camera.elevation = 25
            plotter.write_frame()

        # Final frame (show completed state)
        plotter.clear()
        self.render_frame(total_days, plotter)
        plotter.reset_camera()
        plotter.camera.azimuth = 30
        plotter.camera.elevation = 25
        plotter.write_frame()

        plotter.close()
        return output_path

    def get_frame_meshes(self, day: int) -> list[tuple[pv.PolyData, str, float]]:
        """Get meshes for a frame without a plotter.

        Returns list of (mesh, color, opacity) tuples suitable for
        external rendering (e.g., in a Qt widget).
        """
        states = get_visible_components(self.schedule, day)
        result: list[tuple[pv.PolyData, str, float]] = []

        for label, mesh in self.meshes.items():
            state = states.get(label, "hidden")
            if state == "hidden":
                continue
            elif state == "in_progress":
                result.append((mesh, _COLOR_IN_PROGRESS, _OPACITY_IN_PROGRESS))
            else:
                color = self.mesh_colors.get(label, _COLOR_COMPLETED)
                result.append((mesh, color, _OPACITY_COMPLETED))

        return result
