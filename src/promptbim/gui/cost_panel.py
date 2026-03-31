"""Cost estimation panel — shows cost summary table + pie/bar charts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from promptbim.bim.cost.estimator import CostEstimate, CostEstimator
from promptbim.viz.cost_charts import CostBarChart, CostPieChart

if TYPE_CHECKING:
    from promptbim.gui.bim_core_bridge import BIMCoreBridge
    from promptbim.schemas.plan import BuildingPlan


class CostPanel(QWidget):
    """Displays cost estimation results with charts and table.

    Also integrates with bim_core.CostCalculator when available.
    """

    def __init__(self, parent: QWidget | None = None, bridge: "BIMCoreBridge | None" = None) -> None:
        super().__init__(parent)
        self._estimator = CostEstimator()
        self._estimate: CostEstimate | None = None
        self._bridge = bridge

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        self._header = QLabel("Cost Estimation")
        self._header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self._header)

        # Summary line
        self._summary = QLabel("No estimate available")
        self._summary.setStyleSheet("color: #666;")
        layout.addWidget(self._summary)

        # Tabs: charts and table
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs, stretch=1)

        # Pie chart tab
        self._pie = CostPieChart(width=5, height=3.5, dpi=100)
        self._tabs.addTab(self._pie, "Pie Chart")

        # Bar chart tab
        self._bar = CostBarChart(width=5, height=3.5, dpi=100)
        self._tabs.addTab(self._bar, "Bar Chart")

        # Table tab
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Category", "Cost (NT$)", "Ratio", "Per m\u00b2"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._tabs.addTab(self._table, "Details")

    def estimate_from_plan(self, plan: BuildingPlan) -> CostEstimate:
        """Run cost estimation and update the display."""
        self._estimate = self._estimator.estimate(plan)
        self._update_display()
        return self._estimate

    def _update_display(self) -> None:
        est = self._estimate
        if not est:
            return

        total_m = est.total_cost_twd / 1_000_000
        self._header.setText(f"Cost Estimation \u2014 {est.project_name}")
        self._summary.setText(
            f"Total: NT${total_m:,.1f}M | "
            f"Floor area: {est.total_floor_area_sqm:,.0f} m\u00b2 | "
            f"NT${est.cost_per_sqm_twd:,.0f}/m\u00b2 | "
            f"{est.notes}"
        )

        # Update charts
        self._pie.update_data(est)
        self._bar.update_data(est)

        # Update table
        self._table.setRowCount(len(est.breakdown))
        for row, b in enumerate(est.breakdown):
            self._table.setItem(row, 0, QTableWidgetItem(b.label))

            cost_item = QTableWidgetItem(f"NT${b.cost_twd:,.0f}")
            cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 1, cost_item)

            ratio_item = QTableWidgetItem(f"{b.ratio:.1%}")
            ratio_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 2, ratio_item)

            if est.total_floor_area_sqm > 0:
                per_sqm = b.cost_twd / est.total_floor_area_sqm
                per_sqm_item = QTableWidgetItem(f"NT${per_sqm:,.0f}")
            else:
                per_sqm_item = QTableWidgetItem("N/A")
            per_sqm_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self._table.setItem(row, 3, per_sqm_item)

    def update_from_core(self) -> None:
        """Update cost display from bim_core.CostCalculator if available."""
        if not self._bridge or not self._bridge.available:
            return
        summary = self._bridge.get_cost_summary()
        total = summary.get("total_cost", 0)
        if total:
            self._summary.setText(
                f"C++ Core Total: NT${total:,.0f} | "
                f"Entities: {self._bridge.scene.entity_count()}"
            )
