"""Construction Simulation (4D) Tab — timeline slider + play/pause + Gantt panel.

Provides a complete 4D BIM simulation experience:
- Timeline slider to scrub through construction days
- Play/pause button for auto-advance
- Gantt chart synchronized with the 3D view
- GIF export button
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from promptbim.bim.simulation.animator import ConstructionAnimator
from promptbim.bim.simulation.scheduler import (
    ConstructionSchedule,
    generate_schedule,
    get_active_phase,
)
from promptbim.viz.gantt_chart import GanttChart

if TYPE_CHECKING:
    import pyvista as pv


class SimulationTab(QWidget):
    """4D construction simulation panel with timeline and Gantt chart."""

    day_changed = Signal(int)  # emitted when slider moves

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._schedule: ConstructionSchedule | None = None
        self._animator: ConstructionAnimator | None = None
        self._playing = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        self._header = QLabel("Construction Simulation (4D)")
        self._header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self._header)

        # Info label
        self._info = QLabel("No building loaded. Generate a building first.")
        self._info.setStyleSheet("color: #666;")
        layout.addWidget(self._info)

        # Splitter: gantt chart (top) + controls (bottom)
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter, stretch=1)

        # Gantt chart — click on bar jumps 4D view to that day
        self._gantt = GanttChart(width=8, height=3, dpi=100)
        self._gantt.day_clicked.connect(self._on_gantt_day_clicked)
        splitter.addWidget(self._gantt)

        # Placeholder for external 3D rendering info
        self._phase_label = QLabel("")
        self._phase_label.setStyleSheet("font-size: 12px; padding: 4px;")
        splitter.addWidget(self._phase_label)

        # Controls row
        controls = QWidget()
        ctrl_layout = QHBoxLayout(controls)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)

        # Play/Pause button
        self._play_btn = QPushButton("Play")
        self._play_btn.setFixedWidth(80)
        self._play_btn.clicked.connect(self._toggle_play)
        self._play_btn.setEnabled(False)
        ctrl_layout.addWidget(self._play_btn)

        # Day label
        self._day_label = QLabel("Day: 0")
        self._day_label.setFixedWidth(80)
        ctrl_layout.addWidget(self._day_label)

        # Timeline slider
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(0)
        self._slider.setValue(0)
        self._slider.setEnabled(False)
        self._slider.valueChanged.connect(self._on_slider_changed)
        ctrl_layout.addWidget(self._slider, stretch=1)

        # Total days label
        self._total_label = QLabel("/ 0 days")
        self._total_label.setFixedWidth(80)
        ctrl_layout.addWidget(self._total_label)

        # Speed selector
        ctrl_layout.addWidget(QLabel("Speed:"))
        self._speed_combo = QComboBox()
        self._speed_combo.addItems(["1×", "2×", "5×", "10×"])
        self._speed_combo.currentIndexChanged.connect(self._on_speed_changed)
        self._speed_combo.setFixedWidth(60)
        ctrl_layout.addWidget(self._speed_combo)

        # Export GIF button
        self._export_btn = QPushButton("Export GIF")
        self._export_btn.setFixedWidth(100)
        self._export_btn.clicked.connect(self._export_gif)
        self._export_btn.setEnabled(False)
        ctrl_layout.addWidget(self._export_btn)

        layout.addWidget(controls)

        # Auto-play timer (200ms = 5fps at 1× speed)
        self._play_speed = 1
        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._advance_day)

    def set_building_data(
        self,
        meshes: dict[str, "pv.PolyData"],
        mesh_colors: dict[str, str] | None = None,
        num_stories: int = 1,
        total_days: int = 360,
    ) -> None:
        """Initialize simulation from building mesh data.

        Args:
            meshes: Dict mapping label -> PyVista PolyData.
            mesh_colors: Optional colour map for completed components.
            num_stories: Number of building stories (scales schedule).
            total_days: Base total construction days.
        """
        labels = list(meshes.keys())
        self._schedule = generate_schedule(labels, total_days, num_stories)
        self._animator = ConstructionAnimator(meshes, self._schedule, mesh_colors)

        self._slider.setMaximum(self._schedule.total_days)
        self._slider.setValue(0)
        self._slider.setEnabled(True)
        self._play_btn.setEnabled(True)
        self._export_btn.setEnabled(True)
        self._total_label.setText(f"/ {self._schedule.total_days} days")
        self._info.setText(
            f"Schedule: {len(self._schedule.phases)} phases, {self._schedule.total_days} days total"
        )
        self._gantt.set_schedule(self._schedule)
        self._on_slider_changed(0)

    def _on_slider_changed(self, day: int) -> None:
        self._day_label.setText(f"Day: {day}")
        self._gantt.set_current_day(day)

        if self._schedule:
            active = get_active_phase(self._schedule, day)
            if active:
                progress = (day - active.start_day) / max(1, active.duration_days)
                self._phase_label.setText(
                    f"Phase: {active.phase.name} "
                    f"(Day {active.start_day}-{active.end_day}, "
                    f"{progress:.0%} complete)"
                )
            elif day >= self._schedule.total_days:
                self._phase_label.setText("Construction Complete!")
            else:
                self._phase_label.setText("")

        self.day_changed.emit(day)

    def _toggle_play(self) -> None:
        if self._playing:
            self._timer.stop()
            self._playing = False
            self._play_btn.setText("Play")
        else:
            if self._slider.value() >= self._slider.maximum():
                self._slider.setValue(0)
            self._timer.start()
            self._playing = True
            self._play_btn.setText("Pause")

    def _advance_day(self) -> None:
        current = self._slider.value()
        base_step = max(1, self._slider.maximum() // 200)
        step = base_step * self._play_speed
        new_val = current + step
        if new_val >= self._slider.maximum():
            self._slider.setValue(self._slider.maximum())
            self._timer.stop()
            self._playing = False
            self._play_btn.setText("Play")
        else:
            self._slider.setValue(new_val)

    def _on_gantt_day_clicked(self, day: int) -> None:
        """Jump 4D view to day when user clicks Gantt bar."""
        self._slider.setValue(day)

    def _on_speed_changed(self, index: int) -> None:
        speeds = [1, 2, 5, 10]
        self._play_speed = speeds[index] if index < len(speeds) else 1
        # Adjust step size for advance (interval stays 200ms, step multiplied)

    def _export_gif(self) -> None:
        if not self._animator:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export GIF", "construction_animation.gif", "GIF (*.gif)"
        )
        if path:
            self._animator.export_gif(path)
            self._info.setText(f"GIF exported: {path}")

    @property
    def animator(self) -> ConstructionAnimator | None:
        return self._animator

    @property
    def schedule(self) -> ConstructionSchedule | None:
        return self._schedule

    @property
    def current_day(self) -> int:
        return self._slider.value()
