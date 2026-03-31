"""EntityListView — flat list of all BIMEntity from bim_core.

T03: Lists all entities with type, name, and position info.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from promptbim.debug import get_logger

if TYPE_CHECKING:
    from promptbim.gui.bim_core_bridge import BIMCoreBridge

logger = get_logger("gui.entity_list_view")


class EntityListView(QWidget):
    """Table listing all BIMEntity from the C++ SceneGraph."""

    entity_selected = Signal(str)  # entity id

    def __init__(self, bridge: BIMCoreBridge, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._bridge = bridge

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self._header = QLabel("Entities")
        self._header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self._header)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["ID", "Type", "Name", "Position"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self._table)

        self.refresh()

    def refresh(self) -> None:
        """Reload entity list from the SceneGraph."""
        self._table.setRowCount(0)
        if not self._bridge.available:
            self._header.setText("Entities (offline)")
            return

        entities = self._bridge.get_scene_entities()
        self._header.setText(f"Entities ({len(entities)})")
        self._table.setRowCount(len(entities))

        for row, e in enumerate(entities):
            self._table.setItem(row, 0, QTableWidgetItem(e.get("id", "")))
            self._table.setItem(row, 1, QTableWidgetItem(e.get("type", "")))
            self._table.setItem(row, 2, QTableWidgetItem(e.get("name", "")))

            pos = e.get("position", [0, 0, 0])
            pos_str = f"({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})"
            pos_item = QTableWidgetItem(pos_str)
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 3, pos_item)

    def _on_cell_clicked(self, row: int, _col: int) -> None:
        id_item = self._table.item(row, 0)
        if id_item:
            self.entity_selected.emit(id_item.text())
