"""Boundary confirmation GUI — overlay AI-recognized boundary on original image.

Shows the original image with the detected polygon overlay.
Users can drag vertices to fine-tune, switch between candidates,
or confirm/reject the result.
"""

from __future__ import annotations

from promptbim.debug import get_logger

logger = get_logger("gui.confirm_boundary")

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from promptbim.land.boundary_confirm import (
    BoundaryConfirmation,
    adjust_vertex,
    validate_boundary,
)

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure

    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class ConfirmBoundaryDialog(QDialog):
    """Dialog for reviewing and adjusting AI-recognized land boundaries."""

    boundary_confirmed = Signal(object)  # emits LandParcel

    def __init__(
        self,
        confirmation: BoundaryConfirmation,
        image_path: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        logger.debug("ConfirmBoundaryDialog init — %d candidates", len(confirmation.candidates))
        self.setWindowTitle("Confirm Land Boundary")
        self.setMinimumSize(700, 550)

        self._confirmation = confirmation
        self._image_path = image_path
        self._dragging_vertex: int | None = None

        self._build_ui()
        self._update_display()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Info bar
        info_layout = QHBoxLayout()
        self._confidence_label = QLabel()
        info_layout.addWidget(self._confidence_label)
        self._area_label = QLabel()
        info_layout.addWidget(self._area_label)
        self._perimeter_label = QLabel()
        info_layout.addWidget(self._perimeter_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Candidate selector (if multiple candidates)
        if len(self._confirmation.candidates) > 1:
            cand_layout = QHBoxLayout()
            cand_layout.addWidget(QLabel("Candidate:"))
            self._candidate_combo = QComboBox()
            for i, c in enumerate(self._confirmation.candidates):
                self._candidate_combo.addItem(f"#{i + 1} (conf: {c.confidence:.0%})")
            self._candidate_combo.setCurrentIndex(self._confirmation.selected_index)
            self._candidate_combo.currentIndexChanged.connect(self._on_candidate_changed)
            cand_layout.addWidget(self._candidate_combo)
            cand_layout.addStretch()
            layout.addLayout(cand_layout)

        # Matplotlib canvas for image + boundary overlay
        if HAS_MPL:
            self._figure = Figure(figsize=(6, 4))
            self._canvas = FigureCanvasQTAgg(self._figure)
            self._canvas.mpl_connect("button_press_event", self._on_mouse_press)
            self._canvas.mpl_connect("motion_notify_event", self._on_mouse_move)
            self._canvas.mpl_connect("button_release_event", self._on_mouse_release)
            layout.addWidget(self._canvas)
        else:
            layout.addWidget(QLabel("(matplotlib not available for preview)"))

        # Notes
        self._notes_label = QLabel()
        self._notes_label.setWordWrap(True)
        layout.addWidget(self._notes_label)

        # Validation warnings
        self._warn_label = QLabel()
        self._warn_label.setStyleSheet("color: #cc6600;")
        self._warn_label.setWordWrap(True)
        layout.addWidget(self._warn_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self._btn_confirm = QPushButton("Confirm")
        self._btn_confirm.clicked.connect(self._on_confirm)
        btn_layout.addWidget(self._btn_confirm)

        self._btn_cancel = QPushButton("Cancel")
        self._btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self._btn_cancel)
        layout.addLayout(btn_layout)

    def _update_display(self) -> None:
        candidate = self._confirmation.selected
        if not candidate:
            return

        parcel = candidate.parcel
        conf = candidate.confidence
        conf_color = "#00aa00" if conf >= 0.7 else "#cc6600" if conf >= 0.4 else "#cc0000"

        self._confidence_label.setText(
            f'<b>Confidence:</b> <span style="color:{conf_color}">{conf:.0%}</span>'
        )
        self._area_label.setText(f"<b>Area:</b> {parcel.area_sqm:,.1f} m\u00b2")
        self._perimeter_label.setText(f"<b>Perimeter:</b> {parcel.perimeter_m:,.1f} m")
        self._notes_label.setText(f"<i>{candidate.notes}</i>" if candidate.notes else "")

        # Validation
        issues = validate_boundary(parcel.boundary)
        if issues:
            self._warn_label.setText("Warnings: " + "; ".join(issues))
        else:
            self._warn_label.setText("")

        if HAS_MPL:
            self._draw_overlay()

    def _draw_overlay(self) -> None:
        self._figure.clear()
        ax = self._figure.add_subplot(111)

        # Load and show original image if available
        if self._image_path and Path(self._image_path).exists():
            try:
                from PIL import Image

                img = Image.open(self._image_path)
                ax.imshow(img, alpha=0.5)
            except Exception:
                pass

        candidate = self._confirmation.selected
        if candidate:
            boundary = candidate.parcel.boundary
            if boundary:
                xs = [p[0] for p in boundary] + [boundary[0][0]]
                ys = [p[1] for p in boundary] + [boundary[0][1]]
                ax.plot(xs, ys, "r-", linewidth=2, label="Boundary")
                ax.plot(
                    [p[0] for p in boundary],
                    [p[1] for p in boundary],
                    "ro",
                    markersize=8,
                    picker=5,
                )
                # Label vertices
                for i, (x, y) in enumerate(boundary):
                    ax.annotate(str(i), (x, y), fontsize=8, ha="center", va="bottom")

        ax.set_aspect("equal")
        ax.set_title("AI-Recognized Land Boundary")
        ax.grid(True, alpha=0.3)
        self._canvas.draw()

    def _on_candidate_changed(self, index: int) -> None:
        logger.debug("User switched to candidate #%d", index + 1)
        self._confirmation.select(index)
        self._update_display()

    def _on_mouse_press(self, event) -> None:
        if event.inaxes is None or event.button != 1:
            return
        candidate = self._confirmation.selected
        if not candidate:
            return
        # Find nearest vertex
        boundary = candidate.parcel.boundary
        min_dist = float("inf")
        closest = -1
        for i, (bx, by) in enumerate(boundary):
            d = (event.xdata - bx) ** 2 + (event.ydata - by) ** 2
            if d < min_dist:
                min_dist = d
                closest = i
        # Threshold based on plot scale
        if min_dist < _pick_threshold(boundary):
            self._dragging_vertex = closest

    def _on_mouse_move(self, event) -> None:
        if self._dragging_vertex is None or event.inaxes is None:
            return
        candidate = self._confirmation.selected
        if candidate:
            logger.debug(
                "User adjusting vertex %d to (%.2f, %.2f)",
                self._dragging_vertex,
                event.xdata,
                event.ydata,
            )
            new_parcel = adjust_vertex(
                candidate.parcel, self._dragging_vertex, event.xdata, event.ydata
            )
            candidate.parcel = new_parcel
            self._update_display()

    def _on_mouse_release(self, event) -> None:
        self._dragging_vertex = None

    def _on_confirm(self) -> None:
        logger.debug("User confirmed boundary")
        candidate = self._confirmation.selected
        if candidate:
            self.boundary_confirmed.emit(candidate.parcel)
            self.accept()


def _pick_threshold(boundary: list[tuple[float, float]]) -> float:
    """Compute a reasonable pick distance threshold based on polygon extent."""
    if len(boundary) < 2:
        return 100.0
    xs = [p[0] for p in boundary]
    ys = [p[1] for p in boundary]
    extent = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
    return (extent * 0.03) ** 2
