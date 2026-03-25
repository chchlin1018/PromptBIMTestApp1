"""3D Model view — pyvistaqt interactor embedded in Qt with floor section switching."""

from __future__ import annotations

import pyvista as pv
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from promptbim.schemas.plan import BuildingPlan
from promptbim.viz.model_3d import build_model, build_model_by_floor, clip_model_at_elevation

# Use off-screen rendering when no display is available (CI, testing)
pv.OFF_SCREEN = False


def _try_create_plotter(parent: QWidget):
    """Try to create pyvistaqt BackgroundPlotter; return None on failure."""
    try:
        from pyvistaqt import QtInteractor
        plotter = QtInteractor(parent)
        return plotter
    except Exception:
        return None


class ModelView(QWidget):
    """3D building model viewer with floor section switching."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar: floor selector
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Section:"))
        self._floor_combo = QComboBox()
        self._floor_combo.addItem("All Floors")
        self._floor_combo.currentIndexChanged.connect(self._on_floor_changed)
        toolbar.addWidget(self._floor_combo)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # PyVista interactor
        self._plotter = _try_create_plotter(self)
        if self._plotter is not None:
            layout.addWidget(self._plotter.interactor)
        else:
            layout.addWidget(QLabel("3D viewer unavailable (no display or VTK error)"))

        self._plan: BuildingPlan | None = None
        self._all_meshes: list[tuple[pv.PolyData, str, str]] = []
        self._floor_meshes: dict[str, list[tuple[pv.PolyData, str, str]]] = {}
        self._floor_names: list[str] = []

    def set_plan(self, plan: BuildingPlan):
        """Load a BuildingPlan and display the 3D model."""
        self._plan = plan
        self._all_meshes = build_model(plan)
        self._floor_meshes = build_model_by_floor(plan)
        self._floor_names = list(self._floor_meshes.keys())

        # Update combo
        self._floor_combo.blockSignals(True)
        self._floor_combo.clear()
        self._floor_combo.addItem("All Floors")
        for name in self._floor_names:
            self._floor_combo.addItem(name)
        self._floor_combo.blockSignals(False)

        self._render_all()

    def _render_all(self):
        """Render all meshes."""
        self._render_meshes(self._all_meshes)

    def _render_meshes(self, meshes: list[tuple[pv.PolyData, str, str]]):
        if self._plotter is None:
            return
        self._plotter.clear()
        for pd, color, label in meshes:
            self._plotter.add_mesh(pd, color=color, label=label, show_edges=True, edge_color="gray", opacity=0.95)
        self._plotter.reset_camera()
        self._plotter.render()

    def _on_floor_changed(self, index: int):
        if index <= 0:
            # "All Floors"
            self._render_all()
            return

        floor_name = self._floor_combo.currentText()
        if floor_name in self._floor_meshes:
            self._render_meshes(self._floor_meshes[floor_name])
        else:
            # Section cut mode: clip at the floor elevation
            if self._plan and index - 1 < len(self._plan.stories):
                story = self._plan.stories[index - 1]
                cut_z = story.elevation_m + story.height_m
                clipped = clip_model_at_elevation(self._all_meshes, cut_z)
                self._render_meshes(clipped)

    def close(self):
        if self._plotter is not None:
            try:
                self._plotter.close()
            except Exception:
                pass
        super().close()
