"""Change comparison panel (Delta Panel) for PromptBIM Demo-1.

Shows a side-by-side diff of 3D geometry, cost, schedule, and 4D deltas
when a design modification is applied.

Layout:
    ┌──────────────────────────────────────────────────────┐
    │  Delta Panel — 變更對照  [Before] ← → [After]       │
    ├──────────────────┬───────────────────────────────────┤
    │  3D Changes      │  Cost Changes       │ 4D Changes  │
    │  (mesh diff)     │  (NT$ breakdown)    │ (days±)     │
    └──────────────────┴───────────────────────────────────┘
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from promptbim.debug import get_logger

if TYPE_CHECKING:
    from promptbim.schemas.plan import BuildingPlan

logger = get_logger("gui.delta_panel")


@dataclass
class DeltaRecord:
    """A single field-level change record."""

    field: str
    before: str
    after: str
    delta: str = ""
    category: str = "general"  # 3d | cost | schedule | 4d


@dataclass
class PlanDelta:
    """Complete delta between two BuildingPlan versions."""

    command: str = ""
    records: list[DeltaRecord] = field(default_factory=list)
    cost_before_twd: float = 0.0
    cost_after_twd: float = 0.0
    schedule_before_days: int = 0
    schedule_after_days: int = 0
    stories_before: int = 0
    stories_after: int = 0

    @property
    def cost_delta_twd(self) -> float:
        return self.cost_after_twd - self.cost_before_twd

    @property
    def schedule_delta_days(self) -> int:
        return self.schedule_after_days - self.schedule_before_days

    @property
    def stories_delta(self) -> int:
        return self.stories_after - self.stories_before


def compute_plan_delta(
    before: "BuildingPlan",
    after: "BuildingPlan",
    command: str = "",
) -> PlanDelta:
    """Compute delta between two BuildingPlan instances."""
    records: list[DeltaRecord] = []

    # Stories
    if len(before.stories) != len(after.stories):
        records.append(
            DeltaRecord(
                field="Stories",
                before=str(len(before.stories)),
                after=str(len(after.stories)),
                delta=f"{len(after.stories) - len(before.stories):+d}",
                category="3d",
            )
        )

    # BCR / FAR
    if abs(before.building_bcr - after.building_bcr) > 0.001:
        records.append(
            DeltaRecord(
                field="BCR",
                before=f"{before.building_bcr:.1%}",
                after=f"{after.building_bcr:.1%}",
                delta=f"{(after.building_bcr - before.building_bcr):+.1%}",
                category="3d",
            )
        )
    if abs(before.building_far - after.building_far) > 0.01:
        records.append(
            DeltaRecord(
                field="FAR",
                before=f"{before.building_far:.2f}",
                after=f"{after.building_far:.2f}",
                delta=f"{(after.building_far - before.building_far):+.2f}",
                category="3d",
            )
        )

    # GFA
    gfa_before = sum(sum(sp.area_sqm for sp in s.spaces) for s in before.stories)
    gfa_after = sum(sum(sp.area_sqm for sp in s.spaces) for s in after.stories)
    if abs(gfa_before - gfa_after) > 0.5:
        records.append(
            DeltaRecord(
                field="GFA (m²)",
                before=f"{gfa_before:.1f}",
                after=f"{gfa_after:.1f}",
                delta=f"{gfa_after - gfa_before:+.1f}",
                category="3d",
            )
        )

    delta = PlanDelta(
        command=command,
        records=records,
        stories_before=len(before.stories),
        stories_after=len(after.stories),
    )
    return delta


class _DeltaTable(QTableWidget):
    """Compact table showing before/after/delta rows."""

    _COL_FIELD = 0
    _COL_BEFORE = 1
    _COL_AFTER = 2
    _COL_DELTA = 3

    def __init__(self, parent=None) -> None:
        super().__init__(0, 4, parent)
        self.setHorizontalHeaderLabels(["Field", "Before", "After", "Δ"])
        self.horizontalHeader().setStretchLastSection(False)
        self.setColumnWidth(0, 100)
        self.setColumnWidth(1, 80)
        self.setColumnWidth(2, 80)
        self.setColumnWidth(3, 60)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)

    def load_records(self, records: list[DeltaRecord]) -> None:
        self.setRowCount(0)
        for rec in records:
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, self._COL_FIELD, QTableWidgetItem(rec.field))
            self.setItem(row, self._COL_BEFORE, QTableWidgetItem(rec.before))
            self.setItem(row, self._COL_AFTER, QTableWidgetItem(rec.after))

            delta_item = QTableWidgetItem(rec.delta)
            # Colour code: green=increase, red=decrease
            if rec.delta.startswith("+"):
                delta_item.setForeground(QColor("#4CAF50"))
            elif rec.delta.startswith("-"):
                delta_item.setForeground(QColor("#F44336"))
            self.setItem(row, self._COL_DELTA, delta_item)

        self.resizeRowsToContents()


class DeltaPanel(QWidget):
    """Side-by-side change comparison panel for 3D + Cost + Schedule + 4D."""

    undo_requested = Signal()
    accept_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_plan: "BuildingPlan | None" = None
        self._previous_plan: "BuildingPlan | None" = None
        self._delta: PlanDelta | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(4)

        # Header row
        header_row = QHBoxLayout()
        title = QLabel("🔄 變更對照面板 — Delta Review")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        header_row.addWidget(title)
        header_row.addStretch()

        self._cmd_label = QLabel("")
        self._cmd_label.setStyleSheet("color: #2196F3; font-style: italic;")
        header_row.addWidget(self._cmd_label)

        btn_undo = QPushButton("↩ Undo")
        btn_undo.setFixedWidth(80)
        btn_undo.clicked.connect(self.undo_requested)
        header_row.addWidget(btn_undo)

        btn_accept = QPushButton("✅ Accept")
        btn_accept.setFixedWidth(80)
        btn_accept.clicked.connect(self.accept_requested)
        header_row.addWidget(btn_accept)

        outer.addLayout(header_row)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #444;")
        outer.addWidget(line)

        # Main splitter: 3D | Cost | Schedule+4D
        splitter = QSplitter(Qt.Orientation.Horizontal)
        outer.addWidget(splitter, stretch=1)

        # --- 3D panel ---
        g3d = QGroupBox("3D Geometry Changes")
        g3d_layout = QVBoxLayout(g3d)
        self._table_3d = _DeltaTable()
        g3d_layout.addWidget(self._table_3d)
        splitter.addWidget(g3d)

        # --- Cost panel ---
        gcost = QGroupBox("Cost Changes (NT$)")
        gcost_layout = QVBoxLayout(gcost)
        self._cost_before_label = QLabel("Before: —")
        self._cost_after_label = QLabel("After:  —")
        self._cost_delta_label = QLabel("Δ:      —")
        self._cost_delta_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        gcost_layout.addWidget(self._cost_before_label)
        gcost_layout.addWidget(self._cost_after_label)
        gcost_layout.addWidget(self._cost_delta_label)
        gcost_layout.addStretch()
        splitter.addWidget(gcost)

        # --- Schedule / 4D panel ---
        gsched = QGroupBox("Schedule & 4D Changes")
        gsched_layout = QVBoxLayout(gsched)
        self._sched_before_label = QLabel("Before: — days")
        self._sched_after_label = QLabel("After:  — days")
        self._sched_delta_label = QLabel("Δ:      —")
        self._sched_delta_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        gsched_layout.addWidget(self._sched_before_label)
        gsched_layout.addWidget(self._sched_after_label)
        gsched_layout.addWidget(self._sched_delta_label)
        gsched_layout.addStretch()
        splitter.addWidget(gsched)

        splitter.setSizes([300, 200, 200])
        self.setVisible(False)  # hidden until a delta is set

    def set_plan(self, plan: "BuildingPlan") -> None:
        """Update the current plan (used for baseline)."""
        self._previous_plan = self._current_plan
        self._current_plan = plan

    def show_delta(
        self,
        before: "BuildingPlan",
        after: "BuildingPlan",
        command: str = "",
        cost_before: float = 0.0,
        cost_after: float = 0.0,
        schedule_before: int = 0,
        schedule_after: int = 0,
    ) -> None:
        """Populate and show the delta panel."""
        delta = compute_plan_delta(before, after, command)
        delta.cost_before_twd = cost_before
        delta.cost_after_twd = cost_after
        delta.schedule_before_days = schedule_before
        delta.schedule_after_days = schedule_after
        self._delta = delta

        self._cmd_label.setText(f'Command: "{command}"')

        # 3D table
        records_3d = [r for r in delta.records if r.category == "3d"]
        self._table_3d.load_records(records_3d)

        # Cost labels
        b_m = cost_before / 1_000_000
        a_m = cost_after / 1_000_000
        d_m = (cost_after - cost_before) / 1_000_000
        self._cost_before_label.setText(f"Before: NT${b_m:,.1f}M")
        self._cost_after_label.setText(f"After:  NT${a_m:,.1f}M")
        sign = "+" if d_m >= 0 else ""
        self._cost_delta_label.setText(f"Δ: {sign}NT${d_m:,.1f}M")
        color = "#4CAF50" if d_m <= 0 else "#F44336"
        self._cost_delta_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color};")

        # Schedule labels
        self._sched_before_label.setText(f"Before: {schedule_before} days")
        self._sched_after_label.setText(f"After:  {schedule_after} days")
        d_days = schedule_after - schedule_before
        sign2 = "+" if d_days >= 0 else ""
        self._sched_delta_label.setText(f"Δ: {sign2}{d_days} days")
        sched_color = "#4CAF50" if d_days <= 0 else "#F44336"
        self._sched_delta_label.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {sched_color};"
        )

        self.setVisible(True)
        logger.info("DeltaPanel: showing delta for '%s' (%d records)", command, len(delta.records))

    def clear(self) -> None:
        self._delta = None
        self._table_3d.setRowCount(0)
        self._cost_before_label.setText("Before: —")
        self._cost_after_label.setText("After:  —")
        self._cost_delta_label.setText("Δ: —")
        self._sched_before_label.setText("Before: — days")
        self._sched_after_label.setText("After:  — days")
        self._sched_delta_label.setText("Δ: —")
        self.setVisible(False)
