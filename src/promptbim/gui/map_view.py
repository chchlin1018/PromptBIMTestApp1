"""2D Map view — matplotlib canvas embedded in Qt for land parcel display."""

from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from promptbim.schemas.land import LandParcel


class MapView(QWidget):
    """Matplotlib-based 2D map view for displaying land parcels and setback lines."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._figure = Figure(figsize=(8, 6), dpi=100)
        self._canvas = FigureCanvas(self._figure)
        self._ax = self._figure.add_subplot(111)
        self._ax.set_aspect("equal")
        self._ax.set_title("Land Parcel View")
        self._ax.grid(True, alpha=0.3)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)

        self._parcel: LandParcel | None = None
        self._buildable_area: list[tuple[float, float]] = []
        self._basemap_style: str = "none"

    def set_parcel(self, parcel: LandParcel, buildable_area: list[tuple[float, float]] | None = None):
        """Display a land parcel with optional buildable area overlay."""
        self._parcel = parcel
        self._buildable_area = buildable_area or []
        self._redraw()

    def set_basemap_style(self, style: str) -> None:
        """Set basemap style ('osm', 'satellite', 'none') and redraw."""
        self._basemap_style = style
        self._redraw()

    def _redraw(self):
        self._ax.clear()
        self._ax.set_aspect("equal")
        self._ax.grid(True, alpha=0.3)

        if self._parcel is None:
            self._ax.set_title("No land parcel loaded")
            self._canvas.draw()
            return

        # Draw land boundary
        coords = self._parcel.boundary
        if coords:
            xs = [c[0] for c in coords] + [coords[0][0]]
            ys = [c[1] for c in coords] + [coords[0][1]]
            self._ax.fill(xs, ys, alpha=0.15, color="green", label="Land parcel")
            self._ax.plot(xs, ys, "g-", linewidth=2)

        # Draw buildable area (setback)
        if self._buildable_area:
            bx = [c[0] for c in self._buildable_area] + [self._buildable_area[0][0]]
            by = [c[1] for c in self._buildable_area] + [self._buildable_area[0][1]]
            self._ax.fill(bx, by, alpha=0.2, color="blue", label="Buildable area")
            self._ax.plot(bx, by, "b--", linewidth=1.5)

        # Basemap overlay
        if self._basemap_style != "none" and coords:
            try:
                from promptbim.viz.basemap import add_basemap, calculate_bounds

                bounds = calculate_bounds(coords)
                add_basemap(
                    self._ax,
                    bounds,
                    crs=self._parcel.crs,
                    style=self._basemap_style,
                )
            except Exception:
                pass  # basemap is best-effort

        # Area annotation
        if coords:
            cx = sum(c[0] for c in coords) / len(coords)
            cy = sum(c[1] for c in coords) / len(coords)
            self._ax.annotate(
                f"{self._parcel.area_sqm:.1f} m\u00b2",
                (cx, cy),
                ha="center",
                va="center",
                fontsize=12,
                fontweight="bold",
                color="darkgreen",
            )

        self._ax.set_title(f"{self._parcel.name} ({self._parcel.area_sqm:.1f} m\u00b2)")
        self._ax.set_xlabel("X (m)")
        self._ax.set_ylabel("Y (m)")
        self._ax.legend(loc="upper right", fontsize=8)
        self._figure.tight_layout()
        self._canvas.draw()
