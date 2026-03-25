"""Monitoring point show/hide toggle panel.

Provides checkboxes to toggle visibility of each monitoring category
(Environmental, Safety, Security, Energy, Structural, MEP, Smart, Accessibility)
in the 3D view.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from promptbim.bim.monitoring.monitor_types import MonitorCategory

if TYPE_CHECKING:
    pass


CATEGORY_COLORS: dict[str, tuple[float, float, float]] = {
    "environmental": (0.2, 0.6, 1.0),
    "safety": (1.0, 0.3, 0.3),
    "security": (0.6, 0.2, 0.8),
    "energy": (0.9, 0.7, 0.1),
    "structural": (0.7, 0.2, 0.2),
    "mep": (0.3, 0.7, 0.8),
    "smart": (0.3, 0.9, 0.5),
    "accessibility": (0.4, 0.4, 1.0),
}

CATEGORY_LABELS: dict[str, str] = {
    "environmental": "Environmental",
    "safety": "Safety",
    "security": "Security",
    "energy": "Energy",
    "structural": "Structural",
    "mep": "MEP Monitoring",
    "smart": "Smart Controls",
    "accessibility": "Accessibility",
}


class MonitorTogglePanel(QWidget):
    """Panel with checkboxes to toggle monitoring category visibility."""

    visibility_changed = Signal(str, bool)  # (category_name, visible)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._checkboxes: dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        header = QLabel("Monitoring Points")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        # Category toggles
        group = QGroupBox("Show/Hide Categories")
        group_layout = QVBoxLayout(group)

        for cat_name, label in CATEGORY_LABELS.items():
            color = CATEGORY_COLORS.get(cat_name, (0.5, 0.5, 0.5))
            hex_color = f"#{int(color[0]*255):02x}{int(color[1]*255):02x}{int(color[2]*255):02x}"

            cb = QCheckBox(label)
            cb.setChecked(True)
            cb.setStyleSheet(f"QCheckBox {{ color: {hex_color}; font-weight: bold; }}")
            cb.toggled.connect(lambda checked, c=cat_name: self._on_toggled(c, checked))
            group_layout.addWidget(cb)
            self._checkboxes[cat_name] = cb

        layout.addWidget(group)

        # Quick buttons
        btn_layout = QHBoxLayout()
        btn_all = QPushButton("Show All")
        btn_all.clicked.connect(self._show_all)
        btn_layout.addWidget(btn_all)

        btn_none = QPushButton("Hide All")
        btn_none.clicked.connect(self._hide_all)
        btn_layout.addWidget(btn_none)

        layout.addLayout(btn_layout)

        # Summary label
        self._summary = QLabel("No monitoring data")
        self._summary.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self._summary)

        layout.addStretch()

    def set_summary(self, total_count: int, total_cost_twd: float) -> None:
        cost_m = total_cost_twd / 1_000_000
        self._summary.setText(f"{total_count} sensors | TWD {cost_m:.1f}M")

    def is_category_visible(self, category: str) -> bool:
        cb = self._checkboxes.get(category)
        return cb.isChecked() if cb else True

    def visible_categories(self) -> list[str]:
        return [c for c, cb in self._checkboxes.items() if cb.isChecked()]

    def _on_toggled(self, category: str, checked: bool) -> None:
        self.visibility_changed.emit(category, checked)

    def _show_all(self) -> None:
        for cb in self._checkboxes.values():
            cb.setChecked(True)

    def _hide_all(self) -> None:
        for cb in self._checkboxes.values():
            cb.setChecked(False)
