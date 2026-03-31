"""PropertyPanel — displays entity properties from bim_core.PropertyManager.

T04: Reads properties for a selected entity from the C++ core.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
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

logger = get_logger("gui.property_panel")


class PropertyPanel(QWidget):
    """Right-side panel showing properties for the selected BIMEntity."""

    def __init__(self, bridge: BIMCoreBridge, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._bridge = bridge
        self._current_id: str | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._header = QLabel("Properties")
        self._header.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(self._header)

        self._entity_label = QLabel("Select an entity")
        self._entity_label.setStyleSheet("color: #666;")
        layout.addWidget(self._entity_label)

        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Property", "Value"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table)

        # Material info section
        self._mat_label = QLabel("")
        self._mat_label.setWordWrap(True)
        self._mat_label.setStyleSheet("color: #555; font-size: 11px;")
        layout.addWidget(self._mat_label)

        layout.addStretch()

    def show_entity(self, entity_id: str) -> None:
        """Display properties for the given entity from bim_core."""
        self._current_id = entity_id
        if not self._bridge.available:
            self._entity_label.setText(f"{entity_id} (bim_core offline)")
            return

        entities = self._bridge.get_scene_entities()
        entity = None
        for e in entities:
            if e.get("id") == entity_id:
                entity = e
                break

        if not entity:
            self._entity_label.setText(f"{entity_id} — not found")
            self._table.setRowCount(0)
            return

        self._header.setText(f"Properties — {entity.get('name', entity_id)}")
        self._entity_label.setText(
            f"Type: {entity.get('type', '?')} | ID: {entity_id}"
        )

        # Build property rows
        rows = []
        rows.append(("Name", entity.get("name", "")))
        rows.append(("Type", entity.get("type", "")))

        pos = entity.get("position", [0, 0, 0])
        rows.append(("Position", f"({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})"))

        rot = entity.get("rotation", [0, 0, 0])
        rows.append(("Rotation", f"({rot[0]:.1f}, {rot[1]:.1f}, {rot[2]:.1f})"))

        dims = entity.get("dimensions", [0, 0, 0])
        rows.append(("Dimensions", f"({dims[0]:.2f}, {dims[1]:.2f}, {dims[2]:.2f})"))

        # Volume and surface area
        dx = dims[0]
        dy = dims[1]
        dz = dims[2]
        vol = dx * dy * dz
        rows.append(("Volume", f"{vol:.2f} m\u00b3"))

        # Custom properties
        props = entity.get("properties", {})
        for k, v in sorted(props.items()):
            rows.append((k, str(v)))

        # Connections
        conns = entity.get("connections", [])
        if conns:
            rows.append(("Connections", ", ".join(conns)))

        self._table.setRowCount(len(rows))
        for i, (key, val) in enumerate(rows):
            key_item = QTableWidgetItem(key)
            key_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(i, 0, key_item)
            val_item = QTableWidgetItem(str(val))
            val_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(i, 1, val_item)

        # Material info from PropertyManager
        pm = self._bridge.property_manager
        if pm:
            try:
                pm_json = json.loads(pm.to_json())
                mat_count = pm_json.get("material_count", 0)
                self._mat_label.setText(f"PropertyManager: {mat_count} materials registered")
            except Exception:
                self._mat_label.setText("")

        logger.debug("PropertyPanel showing entity %s (%d rows)", entity_id, len(rows))
