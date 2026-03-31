"""PySide6 main window for PromptBIM desktop application."""

from promptbim.debug import get_logger

logger = get_logger("gui.main_window")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from promptbim import __version__
from promptbim.gui.bim_core_bridge import BIMCoreBridge
from promptbim.gui.chat_panel import ChatPanel
from promptbim.gui.cost_panel import CostPanel
from promptbim.gui.dialogs.import_land import ImportLandDialog
from promptbim.gui.entity_list_view import EntityListView
from promptbim.gui.land_panel import LandPanel
from promptbim.gui.map_view import MapView
from promptbim.gui.model_view import ModelView
from promptbim.gui.modification_panel import ModificationPanel
from promptbim.gui.property_panel import PropertyPanel
from promptbim.gui.scene_graph_widget import SceneGraphWidget
from promptbim.gui.simulation_tab import SimulationTab
from promptbim.gui.delta_panel import DeltaPanel
from promptbim.gui.viewport_3d import Viewport3D
from promptbim.gui.workflow_controller import WorkflowController, WorkflowProgressBar
from promptbim.land.setback import compute_setback
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan
from promptbim.schemas.zoning import ZoningRules
from promptbim.viz.site_plan import SitePlanView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.debug("MainWindow.__init__ starting")
        self.setWindowTitle(f"PromptBIM v{__version__} - AI-Powered BIM Generator")
        self.setMinimumSize(1200, 800)
        self.setAcceptDrops(True)

        self._parcel: LandParcel | None = None
        self._zoning = ZoningRules()

        # C++ bim_core bridge — shared by all widgets
        self._bridge = BIMCoreBridge(self)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main splitter: left panel | center view | right panel
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, stretch=1)

        # Left panel — land info + scene graph tree + entity list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self._land_panel = LandPanel()
        self._land_panel.setMaximumWidth(350)
        self._land_panel.import_button.clicked.connect(self._show_import_dialog)
        left_layout.addWidget(self._land_panel)

        # Scene graph tree (reads from bim_core.SceneGraph)
        self._scene_graph_widget = SceneGraphWidget(self._bridge)
        self._scene_graph_widget.entity_selected.connect(self._on_entity_selected)
        left_layout.addWidget(self._scene_graph_widget)

        # Entity list view
        self._entity_list = EntityListView(self._bridge)
        self._entity_list.entity_selected.connect(self._on_entity_selected)
        left_layout.addWidget(self._entity_list)

        left_widget.setMaximumWidth(350)
        splitter.addWidget(left_widget)

        # Center tab view
        self._tabs = QTabWidget()
        self._map_view = MapView()
        self._tabs.addTab(self._map_view, "2D Map")
        self._model_view = ModelView()
        self._tabs.addTab(self._model_view, "3D Model")

        # 3D Viewport (bim_core SceneGraph geometry)
        self._viewport_3d = Viewport3D(self._bridge)
        self._tabs.addTab(self._viewport_3d, "C++ 3D View")

        self._site_plan = SitePlanView()
        self._tabs.addTab(self._site_plan, "Site Plan")
        self._cost_panel = CostPanel()
        self._tabs.addTab(self._cost_panel, "Cost (5D)")
        self._sim_tab = SimulationTab()
        self._sim_tab.day_changed.connect(self._on_sim_day_changed)
        self._tabs.addTab(self._sim_tab, "4D Simulation")

        # Tab: Delta (change comparison)
        self._delta_panel = DeltaPanel()
        self._delta_panel.undo_requested.connect(self._on_delta_undo)
        self._tabs.addTab(self._delta_panel, "Delta")
        splitter.addWidget(self._tabs)

        # Right panel — property panel from bim_core.PropertyManager
        self._property_panel = PropertyPanel(self._bridge)
        self._property_panel.setMaximumWidth(300)
        self._bridge.entity_selected.connect(self._property_panel.show_entity)
        splitter.addWidget(self._property_panel)

        # Modification impact panel
        self._mod_panel = ModificationPanel()
        layout.addWidget(self._mod_panel)

        # Bottom chat panel
        self._chat_panel = ChatPanel()
        self._chat_panel.plan_ready.connect(self.set_building_plan)
        self._chat_panel.generation_finished.connect(self._on_generation_finished)
        self._chat_panel.modification_done.connect(self._on_modification_done)
        self._chat_panel.undo_done.connect(self._on_undo_done)
        self._mod_panel.undo_requested.connect(self._chat_panel.request_undo)
        layout.addWidget(self._chat_panel)

        # Workflow progress bar (Prompt→3D→Cost→4D→Done)
        self._progress_bar = WorkflowProgressBar()
        layout.addWidget(self._progress_bar)

        # Workflow controller
        self._workflow = WorkflowController(self)
        self._workflow.step_changed.connect(self._on_workflow_step)
        self._workflow.workflow_complete.connect(self._on_workflow_complete)

        # Status bar
        self.statusBar().showMessage(f"PromptBIM v{__version__} ready")
        logger.debug("MainWindow.__init__ complete — %d tabs", self._tabs.count())

        # Connect bridge signals to refresh widgets
        self._bridge.scene_changed.connect(self._scene_graph_widget.refresh)
        self._bridge.scene_changed.connect(self._entity_list.refresh)
        self._bridge.scene_changed.connect(self._viewport_3d.refresh)
        self._bridge.cost_updated.connect(self._on_core_cost_updated)

        # Load demo data if no existing project
        self._demo_loaded = False
        self._try_load_demo()

        # Load bim_core demo scene
        if self._bridge.available:
            self._bridge.load_demo_scene()

    def _try_load_demo(self):
        """Load demo data on startup — including 3D model generation."""
        if self._parcel is not None:
            return
        try:
            from promptbim.demo.demo_data import (
                generate_all_demo_resources,
                get_demo_land,
                get_demo_plan,
                get_demo_zoning,
            )

            land = get_demo_land()
            zoning = get_demo_zoning()
            plan = get_demo_plan()

            self._parcel = land
            self._zoning = zoning
            self._demo_loaded = True

            self._land_panel.update_parcel(land)
            self._land_panel.update_zoning(zoning)

            buildable = compute_setback(land, zoning)
            self._map_view.set_parcel(land, buildable)
            self._site_plan.set_data(parcel=land, buildable_area=buildable)
            self._chat_panel.set_context(land, zoning)
            self.set_building_plan(plan)

            # Generate demo 3D resources (IFC + USDA + SVG) in background
            try:
                demo_paths = generate_all_demo_resources()
                generated = [k for k, v in demo_paths.items() if v is not None]
                logger.info("Demo resources generated: %s", ", ".join(generated))
            except Exception:
                logger.debug("Demo resource generation skipped", exc_info=True)

            self._chat_panel.append_system_message(
                "歡迎使用 PromptBIM！這是一個範例專案 — 台北市信義區 3 層住宅。"
                "已自動生成 3D 模型 (IFC + USDA + SVG)。"
                "您可以在聊天面板輸入指令修改建築，或從 File > 清除展示資料 重新開始。"
            )
            self.statusBar().showMessage(
                f"Demo Project Loaded: {land.name} ({land.area_sqm:.1f} m²) — 3D model ready"
            )
            logger.info("Demo data loaded on startup with 3D resources")
        except Exception:
            logger.debug("Demo data load skipped", exc_info=True)

    def clear_demo(self):
        """Clear demo data and return to blank state."""
        self._parcel = None
        self._zoning = ZoningRules()
        self._demo_loaded = False
        self._model_view.clear()
        self._map_view.clear()
        self._site_plan.clear()
        self.statusBar().showMessage(f"PromptBIM v{__version__} ready — demo cleared")
        logger.info("Demo data cleared")

    def _show_import_dialog(self):
        dialog = ImportLandDialog(self)
        dialog.parcel_imported.connect(self._on_parcel_imported)
        dialog.exec()

    def _on_parcel_imported(self, parcel: LandParcel):
        logger.debug("Parcel imported: %s (%.1f m²)", parcel.name, parcel.area_sqm)
        self._parcel = parcel
        self._land_panel.update_parcel(parcel)
        self._land_panel.update_zoning(self._zoning)

        buildable = compute_setback(parcel, self._zoning)
        self._map_view.set_parcel(parcel, buildable)
        self._site_plan.set_data(parcel=parcel, buildable_area=buildable)
        self._chat_panel.set_context(parcel, self._zoning)
        self._tabs.setCurrentIndex(0)  # switch to 2D Map tab
        self.statusBar().showMessage(f"Loaded: {parcel.name} ({parcel.area_sqm:.1f} m\u00b2)")

    def _on_generation_finished(self, result):
        if result.success:
            self.statusBar().showMessage(
                f"Generated: {result.building_name} | "
                f"IFC: {'OK' if result.ifc_path else 'N/A'} | "
                f"USD: {'OK' if result.usd_path else 'N/A'}"
            )
        else:
            self.statusBar().showMessage(f"Generation failed: {', '.join(result.errors)}")

    def set_building_plan(self, plan: BuildingPlan, run_workflow: bool = True):
        """Display a generated building plan in 3D, site plan, cost, and 4D views."""
        logger.debug("set_building_plan: %s, %d stories", plan.name, len(plan.stories))
        self._model_view.set_plan(plan)
        self._site_plan.set_data(plan=plan)
        estimate = self._cost_panel.estimate_from_plan(plan)
        total_m = estimate.total_cost_twd / 1_000_000

        # Feed 4D simulation
        self._setup_simulation(plan)

        # Update delta panel if present
        if hasattr(self, "_delta_panel"):
            self._delta_panel.set_plan(plan)

        self._tabs.setCurrentIndex(1)  # switch to 3D Model tab
        self._progress_bar.set_step(1)
        logger.debug("Tab switched to 3D Model (index 1)")
        self.statusBar().showMessage(
            f"Building: {plan.name} | {len(plan.stories)} floors | "
            f"BCR: {plan.building_bcr:.0%} | FAR: {plan.building_far:.1f} | "
            f"Cost: NT${total_m:,.1f}M"
        )

        # Trigger sequential Prompt→3D→Cost→4D workflow
        if run_workflow:
            self._workflow.run(plan)

    def _on_workflow_step(self, tab_idx: int, label: str) -> None:
        """Update progress bar when workflow advances."""
        # Map tab idx to progress bar step
        _tab_to_step = {1: 1, 2: 2, 3: 2, 4: 3, 5: 4}
        step = _tab_to_step.get(tab_idx, 0)
        self._progress_bar.set_step(step)

    def _on_workflow_complete(self) -> None:
        self._progress_bar.set_step(4)
        self.statusBar().showMessage("✅ Demo-1 Workflow Complete — Prompt→3D→Cost→4D ready")

    def _setup_simulation(self, plan: BuildingPlan):
        """Initialize 4D simulation from a BuildingPlan."""
        from promptbim.viz.model_3d import build_model

        meshes_data = build_model(plan)
        mesh_dict = {}
        color_dict = {}
        for pd, color, label in meshes_data:
            mesh_dict[label] = pd
            color_dict[label] = color

        self._sim_tab.set_building_data(
            meshes=mesh_dict,
            mesh_colors=color_dict,
            num_stories=len(plan.stories),
        )

    def _on_sim_day_changed(self, day: int):
        """Update 3D view when simulation day changes."""
        animator = self._sim_tab.animator
        if not animator:
            return
        frame_meshes = animator.get_frame_meshes(day)
        self._model_view.set_simulation_frame(frame_meshes)

    def _on_modification_done(self, plan, record):
        """Handle a completed modification."""
        logger.debug("Modification done: %s (success=%s)", record.command, record.success)
        self.set_building_plan(plan)
        history_count = len(self._chat_panel._orchestrator.modification_history.records)
        self._mod_panel.show_record(record, history_count)

    def _on_delta_undo(self) -> None:
        """Undo triggered from delta panel."""
        self._chat_panel.request_undo()

    def _on_undo_done(self, plan):
        """Handle an undo operation."""
        logger.debug("Undo done: plan=%s", plan.name)
        self.set_building_plan(plan, run_workflow=False)
        self._delta_panel.clear()
        history_count = len(self._chat_panel._orchestrator.modification_history.records)
        self._mod_panel.update_history_count(history_count)
        if history_count == 0:
            self._mod_panel.clear_panel()

    def _on_entity_selected(self, entity_id: str) -> None:
        """Handle entity selection from scene graph or entity list."""
        self._bridge.entity_selected.emit(entity_id)
        self._viewport_3d.highlight_entity(entity_id)
        self.statusBar().showMessage(f"Selected: {entity_id}")

    def _on_core_cost_updated(self) -> None:
        """Update status bar with C++ core cost info."""
        summary = self._bridge.get_cost_summary()
        total = summary.get("total_cost", 0)
        if total:
            self.statusBar().showMessage(
                f"C++ Core Cost: NT${total:,.0f} | Entities: {self._bridge.scene.entity_count()}"
            )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        from pathlib import Path

        from promptbim.gui.dialogs.import_land import SUPPORTED_EXTENSIONS, _parse_file

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            logger.debug("File dropped on main window: %s", file_path)
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

    # Startup health check
    from promptbim.config import get_settings

    settings = get_settings()

    if settings.startup_check_enabled:
        from promptbim.gui.startup_check_view import StartupCheckView

        check_dialog = StartupCheckView()
        check_dialog.start_checks(settings)
        check_dialog.exec()

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
