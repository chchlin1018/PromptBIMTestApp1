"""PySide6 main window for PromptBIM desktop application."""

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QTabWidget,
    QLineEdit,
    QPushButton,
)
from PySide6.QtCore import Qt

from promptbim import __version__
from promptbim.gui.land_panel import LandPanel
from promptbim.gui.map_view import MapView
from promptbim.gui.model_view import ModelView
from promptbim.gui.dialogs.import_land import ImportLandDialog
from promptbim.land.setback import compute_setback
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan
from promptbim.schemas.zoning import ZoningRules
from promptbim.viz.site_plan import SitePlanView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PromptBIM v{__version__} - AI-Powered BIM Generator")
        self.setMinimumSize(1200, 800)
        self.setAcceptDrops(True)

        self._parcel: LandParcel | None = None
        self._zoning = ZoningRules()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main splitter: left panel | center view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, stretch=1)

        # Left panel — land info
        self._land_panel = LandPanel()
        self._land_panel.setMaximumWidth(350)
        self._land_panel.import_button.clicked.connect(self._show_import_dialog)
        splitter.addWidget(self._land_panel)

        # Center tab view
        self._tabs = QTabWidget()
        self._map_view = MapView()
        self._tabs.addTab(self._map_view, "2D Map")
        self._model_view = ModelView()
        self._tabs.addTab(self._model_view, "3D Model")
        self._site_plan = SitePlanView()
        self._tabs.addTab(self._site_plan, "Site Plan")
        splitter.addWidget(self._tabs)

        # Bottom chat panel
        chat_widget = QWidget()
        chat_layout = QHBoxLayout(chat_widget)
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText(
            "Describe the building you want to create..."
        )
        chat_layout.addWidget(self.chat_input, stretch=1)
        mic_btn = QPushButton("Mic")
        chat_layout.addWidget(mic_btn)
        gen_btn = QPushButton("Generate")
        chat_layout.addWidget(gen_btn)
        layout.addWidget(chat_widget)

        # Status bar
        self.statusBar().showMessage(f"PromptBIM v{__version__} ready")

    def _show_import_dialog(self):
        dialog = ImportLandDialog(self)
        dialog.parcel_imported.connect(self._on_parcel_imported)
        dialog.exec()

    def _on_parcel_imported(self, parcel: LandParcel):
        self._parcel = parcel
        self._land_panel.update_parcel(parcel)
        self._land_panel.update_zoning(self._zoning)

        buildable = compute_setback(parcel, self._zoning)
        self._map_view.set_parcel(parcel, buildable)
        self._site_plan.set_data(parcel=parcel, buildable_area=buildable)
        self._tabs.setCurrentIndex(0)  # switch to 2D Map tab
        self.statusBar().showMessage(
            f"Loaded: {parcel.name} ({parcel.area_sqm:.1f} m\u00b2)"
        )

    def set_building_plan(self, plan: BuildingPlan):
        """Display a generated building plan in 3D and site plan views."""
        self._model_view.set_plan(plan)
        self._site_plan.set_data(plan=plan)
        self._tabs.setCurrentIndex(1)  # switch to 3D Model tab
        self.statusBar().showMessage(
            f"Building: {plan.name} | {len(plan.stories)} floors | "
            f"BCR: {plan.building_bcr:.0%} | FAR: {plan.building_far:.1f}"
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        from pathlib import Path
        from promptbim.gui.dialogs.import_land import SUPPORTED_EXTENSIONS, _parse_file

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            path = Path(file_path)
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                try:
                    parcels = _parse_file(path, path.suffix.lower())
                    if parcels:
                        self._on_parcel_imported(parcels[0])
                except Exception as e:
                    self.statusBar().showMessage(f"Import error: {e}")
                return


def launch_main_window():
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
