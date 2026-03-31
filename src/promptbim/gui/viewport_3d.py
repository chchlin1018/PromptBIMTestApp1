"""3D Viewport — renders bim_core SceneGraph entities via QOpenGLWidget.

T08: Lightweight 3D view that reads geometry from C++ SceneGraph.
Uses simple box rendering for each entity based on position + dimensions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from promptbim.debug import get_logger

if TYPE_CHECKING:
    from promptbim.gui.bim_core_bridge import BIMCoreBridge

logger = get_logger("gui.viewport_3d")

# Color map by entity type
_TYPE_COLORS = {
    "Wall": "#90A4AE",
    "Slab": "#B0BEC5",
    "Column": "#78909C",
    "Beam": "#607D8B",
    "Roof": "#8D6E63",
    "Door": "#A1887F",
    "Window": "#64B5F6",
    "Stair": "#FFB74D",
    "Elevator": "#FF8A65",
    "Chiller": "#4FC3F7",
    "CoolingTower": "#29B6F6",
    "AHU": "#26C6DA",
    "Pump": "#26A69A",
    "Fan": "#66BB6A",
    "Pipe": "#EF5350",
    "Duct": "#FFA726",
    "Cable": "#FFEE58",
    "Valve": "#EC407A",
    "Sensor": "#AB47BC",
    "ExhaustStack": "#8D6E63",
    "Generic": "#BDBDBD",
}


class Viewport3D(QWidget):
    """Pseudo-3D top-down viewport rendering bim_core SceneGraph entities.

    Uses a simple 2D projection (top-down XY) with color-coded entity types.
    For a full 3D OpenGL view, this can be extended with QOpenGLWidget.
    """

    entity_clicked = Signal(str)  # entity id

    def __init__(self, bridge: BIMCoreBridge, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._bridge = bridge
        self._entities: list[dict] = []
        self._highlighted_id: str | None = None
        self._scale = 12.0  # pixels per meter
        self._offset_x = 30.0
        self._offset_y = 30.0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._info_label = QLabel("C++ 3D Viewport — bim_core SceneGraph")
        self._info_label.setStyleSheet("font-weight: bold; padding: 4px;")
        layout.addWidget(self._info_label)

        self._canvas = _ViewportCanvas(self)
        layout.addWidget(self._canvas, stretch=1)

        self.refresh()

    def refresh(self) -> None:
        """Reload entities from the bridge and repaint."""
        if self._bridge.available:
            self._entities = self._bridge.get_scene_entities()
            count = len(self._entities)
            self._info_label.setText(
                f"C++ 3D Viewport — {count} entities from bim_core.SceneGraph"
            )
        else:
            self._entities = []
            self._info_label.setText("C++ 3D Viewport — bim_core offline")
        self._canvas.set_entities(self._entities, self._highlighted_id)

    def highlight_entity(self, entity_id: str) -> None:
        """Highlight a specific entity."""
        self._highlighted_id = entity_id
        self._canvas.set_entities(self._entities, self._highlighted_id)


class _ViewportCanvas(QWidget):
    """Canvas that paints entity boxes in a top-down XY projection."""

    def __init__(self, parent: Viewport3D) -> None:
        super().__init__(parent)
        self._viewport = parent
        self._entities: list[dict] = []
        self._highlighted_id: str | None = None
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #1a1a2e;")

    def set_entities(self, entities: list[dict], highlighted_id: str | None) -> None:
        self._entities = entities
        self._highlighted_id = highlighted_id
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        scale = self._viewport._scale
        ox = self._viewport._offset_x
        oy = self._viewport._offset_y

        # Draw grid
        painter.setPen(QPen(QColor("#333355"), 1))
        for i in range(0, self.width(), int(scale * 5)):
            painter.drawLine(i, 0, i, self.height())
        for j in range(0, self.height(), int(scale * 5)):
            painter.drawLine(0, j, self.width(), j)

        # Draw entities
        for e in self._entities:
            pos = e.get("position", [0, 0, 0])
            dims = e.get("dimensions", [1, 1, 1])
            etype = e.get("type", "Generic")
            eid = e.get("id", "")
            name = e.get("name", "")

            px = pos[0] * scale + ox
            py = pos[1] * scale + oy
            dx = max(dims[0], 0.2) * scale
            dy = max(dims[1], 0.2) * scale

            color = QColor(_TYPE_COLORS.get(etype, "#BDBDBD"))

            # Highlight selected entity
            if eid == self._highlighted_id:
                painter.setPen(QPen(QColor("#FFFF00"), 3))
                color.setAlpha(220)
            else:
                painter.setPen(QPen(color.darker(130), 1))
                color.setAlpha(160)

            painter.setBrush(color)
            painter.drawRect(int(px - dx / 2), int(py - dy / 2), int(dx), int(dy))

            # Label
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(int(px - dx / 2), int(py - dy / 2 - 2), name[:15])

        painter.end()
