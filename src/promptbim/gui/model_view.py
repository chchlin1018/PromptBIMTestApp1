"""3D Model view — pyvistaqt interactor embedded in Qt with floor section switching."""

from __future__ import annotations

from promptbim.debug import get_logger

logger = get_logger("gui.model_view")

import pyvista as pv
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from promptbim.gui.mep_toggle import MEPTogglePanel
from promptbim.schemas.plan import BuildingPlan
from promptbim.viz.model_3d import build_model, build_model_by_floor, clip_model_at_elevation

# Use off-screen rendering when no display is available (CI, testing)
pv.OFF_SCREEN = False

# MEP system keyword → system name mapping
_MEP_KEYWORDS: dict[str, str] = {
    "hvac": "hvac",
    "duct": "hvac",
    "plumb": "plumbing",
    "pipe": "plumbing",
    "water": "plumbing",
    "elec": "electrical",
    "conduit": "electrical",
    "cable": "electrical",
    "fire": "fire_protection",
    "sprinkler": "fire_protection",
}


def _label_to_mep_system(label: str) -> str | None:
    """Map a mesh label to a MEP system name, or None if not MEP."""
    lbl = label.lower()
    for kw, sys in _MEP_KEYWORDS.items():
        if kw in lbl:
            return sys
    return None


def _try_create_plotter(parent: QWidget):
    """Try to create pyvistaqt BackgroundPlotter; return None on failure."""
    try:
        from pyvistaqt import QtInteractor

        plotter = QtInteractor(parent)
        return plotter
    except Exception:
        return None


class ModelView(QWidget):
    """3D building model viewer with floor section switching, component pick, and MEP layers."""

    component_selected = Signal(str)  # emits label of picked mesh

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Toolbar: floor selector
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Section:"))
        self._floor_combo = QComboBox()
        self._floor_combo.addItem("All Floors")
        self._floor_combo.currentIndexChanged.connect(self._on_floor_changed)
        toolbar.addWidget(self._floor_combo)
        toolbar.addStretch()
        outer.addLayout(toolbar)

        # Main horizontal splitter: [3D view | MEP panel + info]
        h_split = QSplitter(Qt.Orientation.Horizontal)
        outer.addWidget(h_split, stretch=1)

        # PyVista interactor
        self._plotter = _try_create_plotter(self)
        if self._plotter is not None:
            h_split.addWidget(self._plotter.interactor)
            # Enable cell picking for component click
            try:
                self._plotter.enable_cell_picking(
                    callback=self._on_cell_picked,
                    show_message=False,
                    font_size=10,
                )
            except Exception:
                pass
        else:
            h_split.addWidget(QLabel("3D viewer unavailable (no display or VTK error)"))

        # Right sidebar: MEP toggle + component info
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(4, 4, 4, 4)

        self._mep_toggle = MEPTogglePanel()
        self._mep_toggle.visibility_changed.connect(self._on_mep_visibility_changed)
        right_layout.addWidget(self._mep_toggle)

        right_layout.addWidget(QLabel("Component Info:"))
        self._info_box = QTextEdit()
        self._info_box.setReadOnly(True)
        self._info_box.setMaximumHeight(120)
        self._info_box.setPlaceholderText("Click a component to see details…")
        right_layout.addWidget(self._info_box)
        right_layout.addStretch()
        right_widget.setMaximumWidth(220)
        h_split.addWidget(right_widget)

        self._plan: BuildingPlan | None = None
        self._all_meshes: list[tuple[pv.PolyData, str, str]] = []
        self._floor_meshes: dict[str, list[tuple[pv.PolyData, str, str]]] = {}
        self._floor_names: list[str] = []
        self._hidden_mep: set[str] = set()

    def _on_cell_picked(self, mesh) -> None:
        """Handle component click from PyVista picker."""
        if mesh is None:
            return
        # Try to find which label this mesh corresponds to
        label = getattr(mesh, "_label", None)
        if label is None:
            label = "Unknown Component"
        self._info_box.setPlainText(
            f"Component: {label}\n"
            f"Points: {mesh.n_points}\n"
            f"Cells: {mesh.n_cells}\n"
            f"Bounds: {', '.join(f'{b:.2f}' for b in mesh.bounds)}"
        )
        self.component_selected.emit(str(label))
        logger.debug("Component picked: %s", label)

    def _on_mep_visibility_changed(self, system: str, visible: bool) -> None:
        """Toggle MEP system layer visibility."""
        if visible:
            self._hidden_mep.discard(system)
        else:
            self._hidden_mep.add(system)
        # Re-render current view with MEP filter applied
        current_idx = self._floor_combo.currentIndex()
        self._on_floor_changed(current_idx)

    def clear(self):
        """Clear the 3D model view."""
        self._plan = None
        self._all_meshes = []
        self._floor_meshes = {}
        self._floor_names = []
        if hasattr(self, '_plotter') and self._plotter:
            self._plotter.clear()

    def set_plan(self, plan: BuildingPlan):
        """Load a BuildingPlan and display the 3D model."""
        import time as _time

        t0 = _time.perf_counter()
        self._plan = plan
        self._all_meshes = build_model(plan)
        self._floor_meshes = build_model_by_floor(plan)
        self._floor_names = list(self._floor_meshes.keys())
        logger.debug(
            "Mesh loaded: %d meshes, %d floors in %.3fs",
            len(self._all_meshes),
            len(self._floor_names),
            _time.perf_counter() - t0,
        )

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
        import time as _time

        t0 = _time.perf_counter()
        self._plotter.clear()
        for pd, color, label in meshes:
            # Filter hidden MEP systems
            if self._hidden_mep:
                mep_system = _label_to_mep_system(label)
                if mep_system and mep_system in self._hidden_mep:
                    continue
            # Attach label for pick callback
            pd._label = label  # type: ignore[attr-defined]
            self._plotter.add_mesh(
                pd, color=color, label=label, show_edges=True, edge_color="gray", opacity=0.95
            )
        self._plotter.reset_camera()
        self._plotter.render()
        logger.debug("Render complete: %d meshes in %.3fs", len(meshes), _time.perf_counter() - t0)

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

    def set_simulation_frame(
        self,
        frame_meshes: list[tuple["pv.PolyData", str, float]],
    ) -> None:
        """Render a 4D simulation frame.

        Args:
            frame_meshes: List of (polydata, color, opacity) tuples.
        """
        if self._plotter is None:
            return
        self._plotter.clear()
        for pd, color, opacity in frame_meshes:
            self._plotter.add_mesh(
                pd, color=color, opacity=opacity, show_edges=True, edge_color="gray"
            )
        self._plotter.reset_camera()
        self._plotter.render()

    def close(self):
        if self._plotter is not None:
            try:
                self._plotter.close()
            except Exception:
                pass
        super().close()
