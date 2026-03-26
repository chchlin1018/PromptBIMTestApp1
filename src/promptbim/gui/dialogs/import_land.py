"""Import land dialog — file picker + drag-and-drop support.

Supports GIS formats (GeoJSON, Shapefile, DXF) and AI image recognition
(JPG, PNG, TIFF, BMP, WebP, HEIC, PDF).
"""

from __future__ import annotations

from promptbim.debug import get_logger

logger = get_logger("gui.import_land")

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from promptbim.schemas.land import LandParcel

SUPPORTED_EXTENSIONS = {".geojson", ".json", ".shp", ".dxf", ".kml", ".kmz"}
PDF_EXTENSIONS = {".pdf"}
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".tiff",
    ".tif",
    ".bmp",
    ".webp",
    ".heic",
    ".heif",
}
ALL_EXTENSIONS = SUPPORTED_EXTENSIONS | IMAGE_EXTENSIONS | PDF_EXTENSIONS


class ImportLandDialog(QDialog):
    """Dialog for importing land parcel data via file selection or drag-drop."""

    parcel_imported = Signal(object)  # emits LandParcel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Land Data")
        self.setMinimumSize(480, 280)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)

        # Tab widget: GIS File / Image AI
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        # Tab 1: GIS File Import
        gis_tab = QWidget()
        gis_layout = QVBoxLayout(gis_tab)
        self._gis_label = QLabel(
            "Drag & drop a file here, or click Browse.\n\n"
            "Supported formats: GeoJSON, Shapefile, DXF"
        )
        self._gis_label.setWordWrap(True)
        gis_layout.addWidget(self._gis_label)
        btn_gis = QHBoxLayout()
        self._btn_browse_gis = QPushButton("Browse GIS File...")
        self._btn_browse_gis.clicked.connect(self._on_browse_gis)
        btn_gis.addWidget(self._btn_browse_gis)
        gis_layout.addLayout(btn_gis)
        self._tabs.addTab(gis_tab, "GIS File")

        # Tab 2: Image AI Import
        img_tab = QWidget()
        img_layout = QVBoxLayout(img_tab)
        self._img_label = QLabel(
            "Drag & drop an image here, or click Browse.\n\n"
            "Supported: JPG, PNG, TIFF, BMP, WebP, HEIC, PDF\n"
            "AI will automatically detect land boundaries."
        )
        self._img_label.setWordWrap(True)
        img_layout.addWidget(self._img_label)
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        img_layout.addWidget(self._progress)
        btn_img = QHBoxLayout()
        self._btn_browse_img = QPushButton("Browse Image...")
        self._btn_browse_img.clicked.connect(self._on_browse_image)
        btn_img.addWidget(self._btn_browse_img)
        img_layout.addLayout(btn_img)
        self._tabs.addTab(img_tab, "Image (AI)")

        # Tab 3: PDF Cadastral Import
        pdf_tab = QWidget()
        pdf_layout = QVBoxLayout(pdf_tab)
        self._pdf_label = QLabel(
            "Drag & drop a PDF here, or click Browse.\n\n"
            "Supports cadastral PDF documents.\n"
            "Auto-detects lot numbers, area, and coordinates."
        )
        self._pdf_label.setWordWrap(True)
        pdf_layout.addWidget(self._pdf_label)
        self._pdf_progress = QProgressBar()
        self._pdf_progress.setVisible(False)
        pdf_layout.addWidget(self._pdf_progress)
        btn_pdf = QHBoxLayout()
        self._btn_browse_pdf = QPushButton("Browse PDF...")
        self._btn_browse_pdf.clicked.connect(self._on_browse_pdf)
        btn_pdf.addWidget(self._btn_browse_pdf)
        pdf_layout.addLayout(btn_pdf)
        self._tabs.addTab(pdf_tab, "PDF (OCR)")

        # Cancel button
        cancel_layout = QHBoxLayout()
        cancel_layout.addStretch()
        self._btn_cancel = QPushButton("Cancel")
        self._btn_cancel.clicked.connect(self.reject)
        cancel_layout.addWidget(self._btn_cancel)
        layout.addLayout(cancel_layout)

    def _on_browse_gis(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Land Data File",
            "",
            "Land files (*.geojson *.json *.shp *.dxf);;All files (*)",
        )
        if file_path:
            self._import_gis_file(file_path)

    def _on_browse_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF Document",
            "",
            "PDF files (*.pdf);;All files (*)",
        )
        if file_path:
            self._import_pdf_file(file_path)

    def _import_pdf_file(self, file_path: str):
        logger.debug("Importing PDF for OCR: %s", file_path)
        self._pdf_progress.setVisible(True)
        self._pdf_progress.setRange(0, 0)
        self._pdf_label.setText("Parsing PDF document...")
        self._btn_browse_pdf.setEnabled(False)

        try:
            from promptbim.land.parsers.pdf_ocr import PDFLandParser

            parser = PDFLandParser(use_ai=True)
            parcels = parser.parse(file_path)
            self._pdf_progress.setVisible(False)
            self._btn_browse_pdf.setEnabled(True)

            if parcels:
                parcel = parcels[0]
                self._pdf_label.setText(
                    f"Extracted: {parcel.name} ({parcel.area_sqm:.1f} m\u00b2)\n"
                    f"Boundary: {len(parcel.boundary)} points"
                )
                self.parcel_imported.emit(parcel)
                self.accept()
            else:
                self._pdf_label.setText(
                    "No cadastral data found in PDF.\n"
                    "Try the Image (AI) tab for image-based recognition."
                )
        except Exception as e:
            self._pdf_progress.setVisible(False)
            self._btn_browse_pdf.setEnabled(True)
            self._pdf_label.setText(f"Error: {e}")

    def _on_browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Land Image",
            "",
            "Images (*.jpg *.jpeg *.png *.tiff *.tif *.bmp *.webp *.heic *.pdf);;All files (*)",
        )
        if file_path:
            self._import_image_file(file_path)

    def _import_gis_file(self, file_path: str):
        path = Path(file_path)
        suffix = path.suffix.lower()
        logger.debug("Importing GIS file: %s (format=%s)", path.name, suffix)
        try:
            parcels = _parse_file(path, suffix)
            if parcels:
                self.parcel_imported.emit(parcels[0])
                self._gis_label.setText(
                    f"Imported: {parcels[0].name} ({parcels[0].area_sqm:.1f} m\u00b2)"
                )
                self.accept()
            else:
                self._gis_label.setText(f"No valid parcels found in {path.name}")
        except Exception as e:
            self._gis_label.setText(f"Error: {e}")

    def _import_image_file(self, file_path: str):
        logger.debug("Importing image file for AI recognition: %s", file_path)
        self._progress.setVisible(True)
        self._progress.setRange(0, 0)  # indeterminate
        self._img_label.setText("AI is analysing the image...")
        self._btn_browse_img.setEnabled(False)

        try:
            from promptbim.land.parsers.image_ai import parse_image_ai

            result = parse_image_ai(file_path)
            self._progress.setVisible(False)
            self._btn_browse_img.setEnabled(True)

            if result.ok:
                parcel = result.parcels[0]
                self._show_confirmation(parcel, result, file_path)
            else:
                self._img_label.setText(f"AI recognition failed: {result.error}")
        except Exception as e:
            self._progress.setVisible(False)
            self._btn_browse_img.setEnabled(True)
            self._img_label.setText(f"Error: {e}")

    def _show_confirmation(self, parcel: LandParcel, result, file_path: str):
        """Show the boundary confirmation dialog."""
        try:
            from promptbim.gui.dialogs.confirm_boundary import ConfirmBoundaryDialog
            from promptbim.land.boundary_confirm import BoundaryConfirmation

            confirmation = BoundaryConfirmation()
            confirmation.add_candidate(
                parcel,
                confidence=result.confidence,
                notes=result.notes,
            )

            dialog = ConfirmBoundaryDialog(confirmation, image_path=file_path, parent=self)
            dialog.boundary_confirmed.connect(self._on_boundary_confirmed)
            dialog.exec()
        except Exception:
            self.parcel_imported.emit(parcel)
            self.accept()

    def _on_boundary_confirmed(self, parcel: LandParcel):
        self.parcel_imported.emit(parcel)
        self.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            suffix = Path(file_path).suffix.lower()
            logger.debug("File dropped: %s (detected format=%s)", file_path, suffix)
            if suffix in SUPPORTED_EXTENSIONS:
                self._import_gis_file(file_path)
                return
            elif suffix in PDF_EXTENSIONS:
                self._tabs.setCurrentIndex(2)
                self._import_pdf_file(file_path)
                return
            elif suffix in IMAGE_EXTENSIONS:
                self._tabs.setCurrentIndex(1)
                self._import_image_file(file_path)
                return


def _parse_file(path: Path, suffix: str) -> list[LandParcel]:
    """Route to appropriate parser based on file extension."""
    logger.debug("_parse_file: %s (suffix=%s)", path, suffix)
    if suffix in (".geojson", ".json"):
        from promptbim.land.parsers.geojson import parse_geojson

        return parse_geojson(path)
    elif suffix == ".shp":
        from promptbim.land.parsers.shapefile import parse_shapefile

        return parse_shapefile(path)
    elif suffix == ".dxf":
        from promptbim.land.parsers.dxf import parse_dxf

        return parse_dxf(path)
    elif suffix in (".kml", ".kmz"):
        from promptbim.land.parsers.kml import parse_kml

        return parse_kml(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
