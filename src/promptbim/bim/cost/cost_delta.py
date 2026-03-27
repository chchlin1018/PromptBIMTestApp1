"""Cost change delta analysis — D1-S1 Task 10.

Computes the cost difference between two BuildingPlan versions
(e.g. before and after a design modification) and produces a
structured delta report suitable for display and downstream use.

Usage::

    from promptbim.bim.cost.cost_delta import CostDeltaAnalyzer
    analyzer = CostDeltaAnalyzer()
    report = analyzer.compare(original_plan, modified_plan)
    print(report.summary_text())
    chart = report.chart_data()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from promptbim.bim.cost.estimator import CostEstimate
    from promptbim.schemas.plan import BuildingPlan


@dataclass
class CostDeltaItem:
    """Delta for a single cost category."""

    category: str
    label: str
    cost_before: float
    cost_after: float
    delta: float
    delta_pct: float  # percentage change
    is_increase: bool


@dataclass
class CostDeltaReport:
    """Full cost change analysis report.

    D1-S1: Bridges design modification → cost impact.
    Produced by CostDeltaAnalyzer.compare().
    """

    project_name: str
    modification_desc: str = ""

    total_before: float = 0.0
    total_after: float = 0.0
    total_delta: float = 0.0
    total_delta_pct: float = 0.0

    per_sqm_before: float = 0.0
    per_sqm_after: float = 0.0

    floor_area_before: float = 0.0
    floor_area_after: float = 0.0
    floor_area_delta: float = 0.0

    category_deltas: list[CostDeltaItem] = field(default_factory=list)
    top_increases: list[CostDeltaItem] = field(default_factory=list)
    top_decreases: list[CostDeltaItem] = field(default_factory=list)

    # Raw estimates for downstream use
    estimate_before: "CostEstimate | None" = None
    estimate_after: "CostEstimate | None" = None

    def summary_text(self) -> str:
        """Human-readable summary string."""
        sign = "+" if self.total_delta >= 0 else ""
        lines = [
            f"Cost Delta Report — {self.project_name}",
            f"Modification: {self.modification_desc or 'N/A'}",
            "",
            f"  Before: NT${self.total_before:,.0f} ({self.floor_area_before:.0f} m²)",
            f"  After:  NT${self.total_after:,.0f} ({self.floor_area_after:.0f} m²)",
            f"  Delta:  {sign}NT${self.total_delta:,.0f} ({sign}{self.total_delta_pct:.1f}%)",
            "",
            "Category Breakdown:",
        ]
        for item in sorted(self.category_deltas, key=lambda x: abs(x.delta), reverse=True):
            sign_i = "+" if item.delta >= 0 else ""
            lines.append(
                f"  {item.label:20s}: {sign_i}NT${item.delta:,.0f} ({sign_i}{item.delta_pct:.1f}%)"
            )
        return "\n".join(lines)

    def chart_data(self) -> dict:
        """Return chart-ready data for visualization.

        Returns a dict with:
        - waterfall: [{category, before, after, delta}] for waterfall chart
        - bar_comparison: [{label, before, after}] for grouped bar
        - summary: {total_before, total_after, delta, delta_pct}
        """
        waterfall = []
        running = self.total_before
        for item in sorted(self.category_deltas, key=lambda x: abs(x.delta), reverse=True):
            waterfall.append({
                "category": item.label,
                "before": round(item.cost_before),
                "after": round(item.cost_after),
                "delta": round(item.delta),
                "delta_pct": round(item.delta_pct, 1),
                "running_start": round(running),
                "running_end": round(running + item.delta),
                "color": "#FF4444" if item.is_increase else "#44AA44",
            })
            running += item.delta

        bar_comparison = [
            {
                "label": item.label,
                "before": round(item.cost_before),
                "after": round(item.cost_after),
            }
            for item in self.category_deltas
        ]

        return {
            "waterfall": waterfall,
            "bar_comparison": bar_comparison,
            "summary": {
                "total_before": round(self.total_before),
                "total_after": round(self.total_after),
                "delta": round(self.total_delta),
                "delta_pct": round(self.total_delta_pct, 1),
                "per_sqm_before": round(self.per_sqm_before),
                "per_sqm_after": round(self.per_sqm_after),
                "floor_area_before": round(self.floor_area_before, 1),
                "floor_area_after": round(self.floor_area_after, 1),
                "floor_area_delta": round(self.floor_area_delta, 1),
            },
        }


class CostDeltaAnalyzer:
    """Analyze cost changes between two BuildingPlan versions (D1-S1).

    Computes category-level deltas by comparing two CostEstimate objects
    produced from before/after BuildingPlans.
    """

    def compare(
        self,
        plan_before: "BuildingPlan",
        plan_after: "BuildingPlan",
        modification_desc: str = "",
        substitutions_before: dict | None = None,
        substitutions_after: dict | None = None,
    ) -> CostDeltaReport:
        """Compare two plans and return a CostDeltaReport.

        Args:
            plan_before: Original BuildingPlan.
            plan_after: Modified BuildingPlan.
            modification_desc: Human-readable description of the change.
            substitutions_before / substitutions_after: Optional component
                substitution maps for each plan version.
        """
        from promptbim.bim.cost.estimator import CostEstimator

        est = CostEstimator()

        if substitutions_before:
            estimate_before = est.estimate_with_substitutions(plan_before, substitutions_before)
        else:
            estimate_before = est.estimate(plan_before)

        if substitutions_after:
            estimate_after = est.estimate_with_substitutions(plan_after, substitutions_after)
        else:
            estimate_after = est.estimate(plan_after)

        return self.compare_estimates(
            estimate_before,
            estimate_after,
            modification_desc=modification_desc,
        )

    def compare_estimates(
        self,
        before: "CostEstimate",
        after: "CostEstimate",
        modification_desc: str = "",
    ) -> CostDeltaReport:
        """Compare two CostEstimate objects directly (D1-S1).

        Useful when you already have estimates computed separately.
        """
        # Build category cost maps
        before_cats: dict[str, tuple[str, float]] = {
            b.category: (b.label, b.cost_twd) for b in before.breakdown
        }
        after_cats: dict[str, tuple[str, float]] = {
            b.category: (b.label, b.cost_twd) for b in after.breakdown
        }
        all_cats = set(before_cats.keys()) | set(after_cats.keys())

        category_deltas: list[CostDeltaItem] = []
        for cat in sorted(all_cats):
            label_b, cost_b = before_cats.get(cat, (cat, 0.0))
            label_a, cost_a = after_cats.get(cat, (cat, 0.0))
            label = label_a or label_b
            delta = cost_a - cost_b
            delta_pct = (delta / cost_b * 100) if cost_b > 0 else (100.0 if delta > 0 else 0.0)
            category_deltas.append(CostDeltaItem(
                category=cat,
                label=label,
                cost_before=cost_b,
                cost_after=cost_a,
                delta=delta,
                delta_pct=delta_pct,
                is_increase=(delta > 0),
            ))

        total_delta = after.total_cost_twd - before.total_cost_twd
        total_delta_pct = (
            (total_delta / before.total_cost_twd * 100)
            if before.total_cost_twd > 0 else 0.0
        )
        floor_area_delta = after.total_floor_area_sqm - before.total_floor_area_sqm

        increases = sorted([d for d in category_deltas if d.delta > 0], key=lambda x: -x.delta)
        decreases = sorted([d for d in category_deltas if d.delta < 0], key=lambda x: x.delta)

        return CostDeltaReport(
            project_name=after.project_name or before.project_name,
            modification_desc=modification_desc,
            total_before=before.total_cost_twd,
            total_after=after.total_cost_twd,
            total_delta=total_delta,
            total_delta_pct=total_delta_pct,
            per_sqm_before=before.cost_per_sqm_twd,
            per_sqm_after=after.cost_per_sqm_twd,
            floor_area_before=before.total_floor_area_sqm,
            floor_area_after=after.total_floor_area_sqm,
            floor_area_delta=floor_area_delta,
            category_deltas=category_deltas,
            top_increases=increases[:3],
            top_decreases=decreases[:3],
            estimate_before=before,
            estimate_after=after,
        )
