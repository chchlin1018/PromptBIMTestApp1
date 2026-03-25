"""Gantt chart visualization for construction schedule using matplotlib."""

from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

if TYPE_CHECKING:
    from promptbim.bim.simulation.scheduler import ConstructionSchedule


class GanttChart(FigureCanvas):
    """Interactive Gantt chart showing construction phases."""

    def __init__(
        self,
        width: float = 8,
        height: float = 4,
        dpi: int = 100,
        parent=None,
    ) -> None:
        self._fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self._fig)
        self.setParent(parent)
        self._ax = self._fig.add_subplot(111)
        self._schedule = None
        self._current_day = 0
        self._day_line = None
        self._draw_empty()

    def _draw_empty(self) -> None:
        self._ax.clear()
        self._ax.text(
            0.5, 0.5, "No schedule loaded",
            ha="center", va="center",
            transform=self._ax.transAxes,
            fontsize=12, color="#999",
        )
        self._ax.set_axis_off()
        self._fig.tight_layout()
        self.draw()

    def set_schedule(self, schedule: ConstructionSchedule) -> None:
        """Load a construction schedule and draw the Gantt chart."""
        self._schedule = schedule
        self._redraw()

    def set_current_day(self, day: int) -> None:
        """Update the current day indicator."""
        self._current_day = day
        if self._day_line and self._schedule:
            self._day_line.set_xdata([day, day])
            self.draw_idle()
        elif self._schedule:
            self._redraw()

    def _redraw(self) -> None:
        self._ax.clear()
        schedule = self._schedule
        if not schedule or not schedule.phases:
            self._draw_empty()
            return

        phases = schedule.phases
        n = len(phases)
        y_positions = list(range(n))

        for i, sp in enumerate(phases):
            color = sp.phase.color
            is_active = sp.start_day <= self._current_day < sp.end_day
            edge_color = "red" if is_active else "black"
            line_width = 2.0 if is_active else 0.5

            self._ax.barh(
                i,
                sp.duration_days,
                left=sp.start_day,
                height=0.6,
                color=color,
                edgecolor=edge_color,
                linewidth=line_width,
                alpha=1.0 if self._current_day >= sp.start_day else 0.4,
            )

            # Phase label inside bar
            mid_x = sp.start_day + sp.duration_days / 2
            self._ax.text(
                mid_x, i, f"{sp.phase.phase_id}",
                ha="center", va="center",
                fontsize=7, fontweight="bold",
                color="white" if is_active else "black",
            )

        # Phase names on y-axis
        self._ax.set_yticks(y_positions)
        self._ax.set_yticklabels(
            [sp.phase.name for sp in phases],
            fontsize=8,
        )
        self._ax.invert_yaxis()

        # Day marker line
        self._day_line = self._ax.axvline(
            self._current_day, color="red", linewidth=1.5, linestyle="--",
        )

        self._ax.set_xlabel("Day", fontsize=9)
        self._ax.set_title("Construction Schedule", fontsize=11, fontweight="bold")
        self._ax.set_xlim(0, schedule.total_days)

        self._fig.tight_layout()
        self.draw()

    def export_svg(self, path: str) -> None:
        """Export the Gantt chart as SVG."""
        if self._schedule:
            self._fig.savefig(path, format="svg", bbox_inches="tight")
