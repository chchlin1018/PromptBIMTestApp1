"""SceneGraph tree widget — displays bim_core.BIMSceneGraph as a tree.

T02: Reads entity hierarchy from C++ SceneGraph, grouped by EntityType.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from promptbim.debug import get_logger

if TYPE_CHECKING:
    from promptbim.gui.bim_core_bridge import BIMCoreBridge

logger = get_logger("gui.scene_graph_widget")


class SceneGraphWidget(QWidget):
    """Tree view of all entities in the C++ SceneGraph, grouped by type."""

    entity_selected = Signal(str)  # entity id

    def __init__(self, bridge: BIMCoreBridge, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._bridge = bridge

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self._header = QLabel("Scene Graph")
        self._header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self._header)

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Name", "ID"])
        self._tree.setColumnWidth(0, 160)
        self._tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._tree)

        self.refresh()

    def refresh(self) -> None:
        """Rebuild the tree from the current SceneGraph state."""
        self._tree.clear()
        if not self._bridge.available:
            self._header.setText("Scene Graph (offline)")
            return

        entities = self._bridge.get_scene_entities()
        self._header.setText(f"Scene Graph ({len(entities)} entities)")

        # Group by type
        groups: dict[str, list[dict]] = {}
        for e in entities:
            etype = e.get("type", "Generic")
            groups.setdefault(etype, []).append(e)

        for type_name, ents in sorted(groups.items()):
            parent_item = QTreeWidgetItem(self._tree, [f"{type_name} ({len(ents)})", ""])
            parent_item.setExpanded(True)
            for ent in ents:
                child = QTreeWidgetItem(parent_item, [
                    ent.get("name", "?"),
                    ent.get("id", "?"),
                ])
                child.setData(0, 256, ent.get("id"))  # UserRole

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        entity_id = item.data(0, 256)
        if entity_id:
            self.entity_selected.emit(entity_id)
            logger.debug("SceneGraph entity selected: %s", entity_id)
