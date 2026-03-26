"""MEP system show/hide toggle panel.

Provides checkboxes to toggle visibility of each MEP system
(HVAC, Plumbing, Electrical, Fire Protection) in the 3D view.
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

from promptbim.bim.mep.systems import SYSTEM_COLORS, SYSTEM_LABELS

if TYPE_CHECKING:
    pass


class MEPTogglePanel(QWidget):
    """Panel with checkboxes to toggle MEP system visibility."""

    visibility_changed = Signal(str, bool)  # (system_name, visible)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._checkboxes: dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        header = QLabel("MEP Systems")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        # System toggles
        group = QGroupBox("Show/Hide Systems")
        group_layout = QVBoxLayout(group)

        for system_name, label in SYSTEM_LABELS.items():
            color = SYSTEM_COLORS.get(system_name, (0.5, 0.5, 0.5))
            hex_color = (
                f"#{int(color[0] * 255):02x}{int(color[1] * 255):02x}{int(color[2] * 255):02x}"
            )

            cb = QCheckBox(label)
            cb.setChecked(True)
            cb.setStyleSheet(f"QCheckBox {{ color: {hex_color}; font-weight: bold; }}")
            cb.toggled.connect(lambda checked, s=system_name: self._on_toggled(s, checked))
            group_layout.addWidget(cb)
            self._checkboxes[system_name] = cb

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

        # Status label
        self._status = QLabel("No MEP data loaded")
        self._status.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self._status)

        layout.addStretch()

    def set_status(self, text: str) -> None:
        self._status.setText(text)

    def is_system_visible(self, system: str) -> bool:
        cb = self._checkboxes.get(system)
        return cb.isChecked() if cb else True

    def visible_systems(self) -> list[str]:
        return [s for s, cb in self._checkboxes.items() if cb.isChecked()]

    def _on_toggled(self, system: str, checked: bool) -> None:
        self.visibility_changed.emit(system, checked)

    def _show_all(self) -> None:
        for cb in self._checkboxes.values():
            cb.setChecked(True)

    def _hide_all(self) -> None:
        for cb in self._checkboxes.values():
            cb.setChecked(False)
