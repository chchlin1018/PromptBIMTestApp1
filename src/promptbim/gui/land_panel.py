"""Land information panel — displays parcel metadata and zoning info."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from promptbim.schemas.land import LandParcel
from promptbim.schemas.zoning import ZoningRules


class LandPanel(QWidget):
    """Left-side panel showing land parcel information and zoning rules."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Land info group
        self._land_group = QGroupBox("Land Parcel")
        land_form = QFormLayout()
        self._lbl_name = QLabel("—")
        self._lbl_area = QLabel("—")
        self._lbl_perimeter = QLabel("—")
        self._lbl_vertices = QLabel("—")
        self._lbl_source = QLabel("—")
        self._lbl_crs = QLabel("—")
        land_form.addRow("Name:", self._lbl_name)
        land_form.addRow("Area:", self._lbl_area)
        land_form.addRow("Perimeter:", self._lbl_perimeter)
        land_form.addRow("Vertices:", self._lbl_vertices)
        land_form.addRow("Source:", self._lbl_source)
        land_form.addRow("CRS:", self._lbl_crs)
        self._land_group.setLayout(land_form)
        layout.addWidget(self._land_group)

        # Zoning group
        self._zoning_group = QGroupBox("Zoning Rules")
        zoning_form = QFormLayout()
        self._lbl_zone = QLabel("—")
        self._lbl_far = QLabel("—")
        self._lbl_bcr = QLabel("—")
        self._lbl_height = QLabel("—")
        self._lbl_setback = QLabel("—")
        zoning_form.addRow("Zone Type:", self._lbl_zone)
        zoning_form.addRow("FAR Limit:", self._lbl_far)
        zoning_form.addRow("BCR Limit:", self._lbl_bcr)
        zoning_form.addRow("Height Limit:", self._lbl_height)
        zoning_form.addRow("Setbacks:", self._lbl_setback)
        self._zoning_group.setLayout(zoning_form)
        layout.addWidget(self._zoning_group)

        # Import button
        self._btn_import = QPushButton("Import Land Data...")
        layout.addWidget(self._btn_import)

        layout.addStretch()

    @property
    def import_button(self) -> QPushButton:
        return self._btn_import

    def update_parcel(self, parcel: LandParcel):
        self._lbl_name.setText(parcel.name)
        self._lbl_area.setText(f"{parcel.area_sqm:.2f} m\u00b2")
        self._lbl_perimeter.setText(f"{parcel.perimeter_m:.2f} m")
        self._lbl_vertices.setText(str(len(parcel.boundary)))
        self._lbl_source.setText(parcel.source_type)
        self._lbl_crs.setText(parcel.crs)

    def update_zoning(self, zoning: ZoningRules):
        self._lbl_zone.setText(zoning.zone_type)
        self._lbl_far.setText(f"{zoning.far_limit:.1f}")
        self._lbl_bcr.setText(f"{zoning.bcr_limit * 100:.0f}%")
        self._lbl_height.setText(f"{zoning.height_limit_m:.1f} m")
        self._lbl_setback.setText(
            f"F:{zoning.setback_front_m} B:{zoning.setback_back_m} "
            f"L:{zoning.setback_left_m} R:{zoning.setback_right_m} m"
        )
