"""Import land dialog — file picker + drag-and-drop support."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from promptbim.schemas.land import LandParcel

SUPPORTED_EXTENSIONS = {".geojson", ".json", ".shp", ".dxf"}


class ImportLandDialog(QDialog):
    """Dialog for importing land parcel data via file selection or drag-drop."""

    parcel_imported = Signal(object)  # emits LandParcel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Land Data")
        self.setMinimumSize(400, 200)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)

        # Instructions
        self._label = QLabel(
            "Drag & drop a file here, or click Browse.\n\n"
            "Supported formats: GeoJSON, Shapefile, DXF"
        )
        self._label.setWordWrap(True)
        layout.addWidget(self._label)

        # Buttons
        btn_layout = QHBoxLayout()
        self._btn_browse = QPushButton("Browse...")
        self._btn_browse.clicked.connect(self._on_browse)
        btn_layout.addWidget(self._btn_browse)
        self._btn_cancel = QPushButton("Cancel")
        self._btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self._btn_cancel)
        layout.addLayout(btn_layout)

    def _on_browse(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Land Data File",
            "",
            "Land files (*.geojson *.json *.shp *.dxf);;All files (*)",
        )
        if file_path:
            self._import_file(file_path)

    def _import_file(self, file_path: str):
        path = Path(file_path)
        suffix = path.suffix.lower()

        try:
            parcels = _parse_file(path, suffix)
            if parcels:
                self.parcel_imported.emit(parcels[0])
                self._label.setText(f"Imported: {parcels[0].name} ({parcels[0].area_sqm:.1f} m\u00b2)")
                self.accept()
            else:
                self._label.setText(f"No valid parcels found in {path.name}")
        except Exception as e:
            self._label.setText(f"Error: {e}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if Path(file_path).suffix.lower() in SUPPORTED_EXTENSIONS:
                self._import_file(file_path)
                return


def _parse_file(path: Path, suffix: str) -> list[LandParcel]:
    """Route to appropriate parser based on file extension."""
    if suffix in (".geojson", ".json"):
        from promptbim.land.parsers.geojson import parse_geojson
        return parse_geojson(path)
    elif suffix == ".shp":
        from promptbim.land.parsers.shapefile import parse_shapefile
        return parse_shapefile(path)
    elif suffix == ".dxf":
        from promptbim.land.parsers.dxf import parse_dxf
        return parse_dxf(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
