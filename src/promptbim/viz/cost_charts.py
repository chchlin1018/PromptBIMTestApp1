"""Cost visualization — pie chart and bar chart using matplotlib."""

from __future__ import annotations

from promptbim.debug import get_logger
logger = get_logger("viz.cost_charts")

from typing import TYPE_CHECKING

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

if TYPE_CHECKING:
    from promptbim.bim.cost.estimator import CostEstimate


# Colour palette for cost categories
_COLOURS = [
    "#4E79A7",  # blue
    "#F28E2B",  # orange
    "#E15759",  # red
    "#76B7B2",  # teal
    "#59A14F",  # green
    "#EDC948",  # yellow
    "#B07AA1",  # purple
    "#FF9DA7",  # pink
    "#9C755F",  # brown
    "#BAB0AC",  # grey
]


class CostPieChart(FigureCanvas):
    """Pie chart showing cost breakdown by category."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self._figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self._figure)
        self.setParent(parent)
        self._ax = self._figure.add_subplot(111)

    def update_data(self, estimate: CostEstimate) -> None:
        self._ax.clear()
        if not estimate.breakdown:
            self._ax.text(0.5, 0.5, "No data", ha="center", va="center")
            self.draw()
            return

        labels = [b.label for b in estimate.breakdown]
        sizes = [b.cost_twd for b in estimate.breakdown]
        colours = _COLOURS[: len(labels)]
        logger.debug("PieChart update: %d categories, total=NT$%.1fM", len(labels), estimate.total_cost_twd / 1_000_000)

        wedges, texts, autotexts = self._ax.pie(
            sizes,
            labels=labels,
            colors=colours,
            autopct="%1.1f%%",
            startangle=90,
            pctdistance=0.75,
        )
        for t in autotexts:
            t.set_fontsize(8)
        for t in texts:
            t.set_fontsize(8)

        total_m = estimate.total_cost_twd / 1_000_000
        self._ax.set_title(
            f"Cost Breakdown — Total: NT${total_m:,.1f}M",
            fontsize=10,
            fontweight="bold",
        )
        self._figure.tight_layout()
        self.draw()


class CostBarChart(FigureCanvas):
    """Horizontal bar chart showing cost by category."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self._figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self._figure)
        self.setParent(parent)
        self._ax = self._figure.add_subplot(111)

    def update_data(self, estimate: CostEstimate) -> None:
        self._ax.clear()
        if not estimate.breakdown:
            self._ax.text(0.5, 0.5, "No data", ha="center", va="center")
            self.draw()
            return

        labels = [b.label for b in reversed(estimate.breakdown)]
        values = [b.cost_twd / 1_000_000 for b in reversed(estimate.breakdown)]
        colours = list(reversed(_COLOURS[: len(labels)]))
        logger.debug("BarChart update: %d categories, total=NT$%.1fM", len(labels), estimate.total_cost_twd / 1_000_000)

        bars = self._ax.barh(labels, values, color=colours, height=0.6)
        self._ax.set_xlabel("Cost (NT$ Million)")
        self._ax.set_title("Cost by Category", fontsize=10, fontweight="bold")

        for bar, val in zip(bars, values):
            self._ax.text(
                bar.get_width() + 0.05,
                bar.get_y() + bar.get_height() / 2,
                f"${val:,.1f}M",
                va="center",
                fontsize=8,
            )

        self._figure.tight_layout()
        self.draw()
