"""Modification impact summary panel with confirm/undo capability.

Displays the impact analysis of a modification and provides
buttons to confirm, undo, or dismiss changes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from promptbim.schemas.modification import ImpactItem, ModificationRecord

# Colour map for impact levels
_LEVEL_COLOURS = {
    "high": "#F44336",
    "medium": "#FF9800",
    "low": "#4CAF50",
    "none": "#9E9E9E",
}


class ModificationPanel(QWidget):
    """Shows modification impact summary and version history controls."""

    undo_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMaximumHeight(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        header = QHBoxLayout()
        self._title = QLabel("Modification Impact")
        self._title.setStyleSheet("font-weight: bold; font-size: 13px;")
        header.addWidget(self._title)
        header.addStretch()

        self._undo_btn = QPushButton("Undo")
        self._undo_btn.setFixedWidth(70)
        self._undo_btn.setEnabled(False)
        self._undo_btn.clicked.connect(self.undo_requested.emit)
        header.addWidget(self._undo_btn)

        self._history_label = QLabel("History: 0")
        self._history_label.setStyleSheet("color: #666;")
        header.addWidget(self._history_label)

        layout.addLayout(header)

        # Impact table
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Component", "Impact", "Before", "After"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._table.setMaximumHeight(150)
        layout.addWidget(self._table)

        # Status line
        self._status = QLabel("")
        self._status.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self._status)

        self.setVisible(False)

    def show_record(self, record: "ModificationRecord", history_count: int) -> None:
        """Display the impacts from a modification record."""
        self.setVisible(True)
        self._history_label.setText(f"History: {history_count}")
        self._undo_btn.setEnabled(history_count > 0)

        if record.success:
            self._title.setText(f"Modification: {record.command}")
            self._title.setStyleSheet("font-weight: bold; font-size: 13px; color: #2196F3;")
        else:
            self._title.setText(f"Failed: {record.command}")
            self._title.setStyleSheet("font-weight: bold; font-size: 13px; color: #F44336;")

        self._populate_impacts(record.impacts)

        if record.success:
            changed = sum(1 for i in record.impacts if i.before_value != i.after_value)
            self._status.setText(f"{changed} component(s) affected")
        else:
            self._status.setText(f"Error: {record.error or 'Unknown'}")

    def _populate_impacts(self, impacts: list["ImpactItem"]) -> None:
        self._table.setRowCount(len(impacts))
        for row, item in enumerate(impacts):
            self._table.setItem(row, 0, QTableWidgetItem(item.component))

            level_item = QTableWidgetItem(item.level.value)
            colour = _LEVEL_COLOURS.get(item.level.value, "#999")
            level_item.setForeground(Qt.GlobalColor.white)
            level_item.setBackground(
                __import__("PySide6.QtGui", fromlist=["QColor"]).QColor(colour)
            )
            self._table.setItem(row, 1, level_item)

            self._table.setItem(row, 2, QTableWidgetItem(item.before_value))
            self._table.setItem(row, 3, QTableWidgetItem(item.after_value))

    def update_history_count(self, count: int) -> None:
        self._history_label.setText(f"History: {count}")
        self._undo_btn.setEnabled(count > 0)

    def clear_panel(self) -> None:
        self._table.setRowCount(0)
        self._status.setText("")
        self.setVisible(False)
