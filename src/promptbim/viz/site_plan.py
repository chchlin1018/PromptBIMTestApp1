"""2D site plan — land parcel + building footprint overlay using matplotlib."""

from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan


class SitePlanView(QWidget):
    """Matplotlib-based 2D site plan showing land + building footprint overlay."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._figure = Figure(figsize=(8, 6), dpi=100)
        self._canvas = FigureCanvas(self._figure)
        self._ax = self._figure.add_subplot(111)
        self._ax.set_aspect("equal")
        self._ax.set_title("Site Plan")
        self._ax.grid(True, alpha=0.3)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)

        self._parcel: LandParcel | None = None
        self._buildable_area: list[tuple[float, float]] = []
        self._plan: BuildingPlan | None = None

    def set_data(
        self,
        parcel: LandParcel | None = None,
        buildable_area: list[tuple[float, float]] | None = None,
        plan: BuildingPlan | None = None,
    ):
        if parcel is not None:
            self._parcel = parcel
        if buildable_area is not None:
            self._buildable_area = buildable_area
        if plan is not None:
            self._plan = plan
        self._redraw()

    def _redraw(self):
        self._ax.clear()
        self._ax.set_aspect("equal")
        self._ax.grid(True, alpha=0.3)

        has_data = False

        # Land boundary
        if self._parcel and self._parcel.boundary:
            coords = self._parcel.boundary
            xs = [c[0] for c in coords] + [coords[0][0]]
            ys = [c[1] for c in coords] + [coords[0][1]]
            self._ax.fill(xs, ys, alpha=0.1, color="green")
            self._ax.plot(xs, ys, "g-", linewidth=2, label="Land boundary")
            has_data = True

        # Buildable area
        if self._buildable_area:
            bx = [c[0] for c in self._buildable_area] + [self._buildable_area[0][0]]
            by = [c[1] for c in self._buildable_area] + [self._buildable_area[0][1]]
            self._ax.plot(bx, by, "b--", linewidth=1.5, label="Buildable area")

        # Building footprint
        if self._plan and self._plan.building_footprint:
            fp = self._plan.building_footprint
            fx = [c[0] for c in fp] + [fp[0][0]]
            fy = [c[1] for c in fp] + [fp[0][1]]
            self._ax.fill(fx, fy, alpha=0.3, color="coral", label="Building footprint")
            self._ax.plot(fx, fy, "r-", linewidth=2)

            # Annotate BCR / FAR
            cx = sum(c[0] for c in fp) / len(fp)
            cy = sum(c[1] for c in fp) / len(fp)
            info = f"BCR: {self._plan.building_bcr:.0%}\nFAR: {self._plan.building_far:.1f}"
            self._ax.annotate(
                info, (cx, cy), ha="center", va="center",
                fontsize=10, fontweight="bold", color="darkred",
            )

            # Per-story outlines (lighter)
            for story in self._plan.stories:
                if story.slab_boundary:
                    sx = [c[0] for c in story.slab_boundary] + [story.slab_boundary[0][0]]
                    sy = [c[1] for c in story.slab_boundary] + [story.slab_boundary[0][1]]
                    self._ax.plot(sx, sy, "-", linewidth=0.8, alpha=0.4, color="gray")
            has_data = True

        if has_data:
            title_parts = []
            if self._parcel:
                title_parts.append(f"{self._parcel.name} ({self._parcel.area_sqm:.1f} m\u00b2)")
            if self._plan:
                title_parts.append(f"Building: {self._plan.name}")
            self._ax.set_title(" | ".join(title_parts) if title_parts else "Site Plan")
        else:
            self._ax.set_title("No data loaded")

        self._ax.set_xlabel("X (m)")
        self._ax.set_ylabel("Y (m)")
        self._ax.legend(loc="upper right", fontsize=8)
        self._figure.tight_layout()
        self._canvas.draw()
