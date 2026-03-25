"""Export dialog — one-click package of IFC + USD + SVG + JSON.

Exports all generated files into a chosen directory as a complete
delivery package.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

if TYPE_CHECKING:
    from promptbim.schemas.plan import BuildingPlan
    from promptbim.schemas.result import GenerationResult

from promptbim.debug import get_logger
logger = get_logger("gui.export_dialog")


class _ExportWorker(QThread):
    """Run export in a background thread."""

    progress = Signal(str, int)  # message, percent
    finished = Signal(bool, str)  # success, message

    def __init__(
        self,
        plan: "BuildingPlan",
        result: "GenerationResult | None",
        output_dir: Path,
        export_ifc: bool,
        export_usd: bool,
        export_svg: bool,
        export_json: bool,
        export_report: bool,
        export_usdz: bool = False,
    ) -> None:
        super().__init__()
        self._plan = plan
        self._result = result
        self._output_dir = output_dir
        self._export_ifc = export_ifc
        self._export_usd = export_usd
        self._export_svg = export_svg
        self._export_json = export_json
        self._export_report = export_report
        self._export_usdz = export_usdz

    def run(self) -> None:
        try:
            self._output_dir.mkdir(parents=True, exist_ok=True)
            exported: list[str] = []
            total_steps = sum([
                self._export_ifc,
                self._export_usd,
                self._export_usdz,
                self._export_svg,
                self._export_json,
                self._export_report,
            ])
            step = 0

            # 1. IFC
            if self._export_ifc:
                step += 1
                self.progress.emit("Exporting IFC...", int(step / total_steps * 100))
                ifc_path = self._export_ifc_file()
                if ifc_path:
                    exported.append(f"IFC: {ifc_path.name}")

            # 2. USD
            if self._export_usd:
                step += 1
                self.progress.emit("Exporting USD...", int(step / total_steps * 100))
                usd_path = self._export_usd_file()
                if usd_path:
                    exported.append(f"USD: {usd_path.name}")

            # 2b. USDZ
            if self._export_usdz:
                step += 1
                self.progress.emit("Packing USDZ...", int(step / total_steps * 100))
                usdz_path = self._export_usdz_file()
                if usdz_path:
                    exported.append(f"USDZ: {usdz_path.name}")

            # 3. SVG floor plans
            if self._export_svg:
                step += 1
                self.progress.emit("Generating SVG floor plans...", int(step / total_steps * 100))
                svg_paths = self._export_svg_files()
                if svg_paths:
                    exported.append(f"SVG: {len(svg_paths)} floor plans")

            # 4. JSON (BuildingPlan)
            if self._export_json:
                step += 1
                self.progress.emit("Exporting JSON...", int(step / total_steps * 100))
                json_path = self._export_json_file()
                if json_path:
                    exported.append(f"JSON: {json_path.name}")

            # 5. Compliance report
            if self._export_report:
                step += 1
                self.progress.emit("Exporting compliance report...", int(step / total_steps * 100))
                rpt_path = self._export_report_file()
                if rpt_path:
                    exported.append(f"Report: {rpt_path.name}")

            msg = f"Exported {len(exported)} items:\n" + "\n".join(exported)
            self.finished.emit(True, msg)

        except Exception as exc:
            logger.exception("Export failed")
            self.finished.emit(False, f"Export failed: {exc}")

    def _export_ifc_file(self) -> Path | None:
        # If we have an existing IFC, copy it; otherwise regenerate
        if self._result and self._result.ifc_path and Path(self._result.ifc_path).exists():
            dest = self._output_dir / Path(self._result.ifc_path).name
            shutil.copy2(self._result.ifc_path, dest)
            return dest
        # Regenerate
        try:
            from promptbim.bim.ifc_generator import IFCGenerator

            gen = IFCGenerator()
            dest = self._output_dir / f"{self._plan.name}.ifc"
            gen.generate(self._plan, dest)
            return dest
        except Exception as exc:
            logger.warning("IFC export failed: %s", exc)
            return None

    def _export_usd_file(self) -> Path | None:
        if self._result and self._result.usd_path and Path(self._result.usd_path).exists():
            dest = self._output_dir / Path(self._result.usd_path).name
            shutil.copy2(self._result.usd_path, dest)
            return dest
        try:
            from promptbim.bim.usd_generator import USDGenerator

            gen = USDGenerator()
            dest = self._output_dir / f"{self._plan.name}.usda"
            gen.generate(self._plan, dest)
            return dest
        except Exception as exc:
            logger.warning("USD export failed: %s", exc)
            return None

    def _export_usdz_file(self) -> Path | None:
        """Pack USD into USDZ for Apple Quick Look / Vision Pro."""
        # We need a .usda first
        usd_source = None
        if self._result and self._result.usd_path and Path(self._result.usd_path).exists():
            usd_source = Path(self._result.usd_path)
        else:
            # Try to generate one
            try:
                from promptbim.bim.usd_generator import USDGenerator

                gen = USDGenerator()
                usd_source = self._output_dir / f"{self._plan.name}.usda"
                gen.generate(self._plan, usd_source)
            except Exception:
                pass

        if usd_source and usd_source.exists():
            try:
                from promptbim.bim.usdz_packer import pack_usdz

                dest = self._output_dir / f"{self._plan.name}.usdz"
                return pack_usdz(usd_source, dest)
            except Exception as exc:
                logger.warning("USDZ export failed: %s", exc)
        return None

    def _export_svg_files(self) -> list[Path]:
        try:
            from promptbim.viz.floorplan import generate_floorplans

            svg_dir = self._output_dir / "floorplans"
            return generate_floorplans(self._plan, svg_dir)
        except Exception as exc:
            logger.warning("SVG export failed: %s", exc)
            return []

    def _export_json_file(self) -> Path | None:
        try:
            dest = self._output_dir / f"{self._plan.name}_plan.json"
            dest.write_text(
                self._plan.model_dump_json(indent=2),
                encoding="utf-8",
            )
            return dest
        except Exception as exc:
            logger.warning("JSON export failed: %s", exc)
            return None

    def _export_report_file(self) -> Path | None:
        if not self._result or not self._result.compliance_report:
            return None
        try:
            dest = self._output_dir / f"{self._plan.name}_compliance.json"
            dest.write_text(
                json.dumps(self._result.compliance_report, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return dest
        except Exception as exc:
            logger.warning("Report export failed: %s", exc)
            return None


class ExportDialog(QDialog):
    """Modal dialog for one-click export of the 5-piece delivery package."""

    def __init__(
        self,
        plan: "BuildingPlan",
        result: "GenerationResult | None" = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._plan = plan
        self._result = result
        self._worker: _ExportWorker | None = None

        self.setWindowTitle("Export Building Package")
        self.setMinimumWidth(450)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Info
        info = QLabel(f"Building: <b>{self._plan.name}</b> | "
                      f"Stories: {len(self._plan.stories)}")
        layout.addWidget(info)

        # Format checkboxes
        fmt_group = QGroupBox("Export Formats")
        fmt_layout = QVBoxLayout(fmt_group)
        self._chk_ifc = QCheckBox("IFC (Industry Foundation Classes)")
        self._chk_ifc.setChecked(True)
        self._chk_usd = QCheckBox("USD (Universal Scene Description)")
        self._chk_usd.setChecked(True)
        self._chk_usdz = QCheckBox("USDZ (Apple Quick Look / Vision Pro)")
        self._chk_usdz.setChecked(False)
        self._chk_svg = QCheckBox("SVG Floor Plans (one per story)")
        self._chk_svg.setChecked(True)
        self._chk_json = QCheckBox("JSON (Building Plan data)")
        self._chk_json.setChecked(True)
        self._chk_report = QCheckBox("Compliance Report (JSON)")
        self._chk_report.setChecked(bool(self._result and self._result.compliance_report))
        self._chk_report.setEnabled(bool(self._result and self._result.compliance_report))

        for chk in [self._chk_ifc, self._chk_usd, self._chk_usdz, self._chk_svg, self._chk_json, self._chk_report]:
            fmt_layout.addWidget(chk)
        layout.addWidget(fmt_group)

        # Output directory
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("Output:"))
        self._dir_input = QLineEdit()
        self._dir_input.setPlaceholderText("Select output directory...")
        default_dir = Path.home() / "Desktop" / f"PromptBIM_{self._plan.name}"
        self._dir_input.setText(str(default_dir))
        dir_row.addWidget(self._dir_input, stretch=1)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(browse_btn)
        layout.addLayout(dir_row)

        # Progress
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._export_btn = QPushButton("Export")
        self._export_btn.clicked.connect(self._on_export)
        self._export_btn.setDefault(True)
        btn_row.addWidget(self._export_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _browse_dir(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if d:
            self._dir_input.setText(d)

    def _on_export(self) -> None:
        out_dir = self._dir_input.text().strip()
        if not out_dir:
            QMessageBox.warning(self, "Error", "Please select an output directory.")
            return

        self._export_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.setValue(0)

        self._worker = _ExportWorker(
            plan=self._plan,
            result=self._result,
            output_dir=Path(out_dir),
            export_ifc=self._chk_ifc.isChecked(),
            export_usd=self._chk_usd.isChecked(),
            export_svg=self._chk_svg.isChecked(),
            export_json=self._chk_json.isChecked(),
            export_report=self._chk_report.isChecked(),
            export_usdz=self._chk_usdz.isChecked(),
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, msg: str, percent: int) -> None:
        self._status_label.setText(msg)
        self._progress.setValue(percent)

    def _on_finished(self, success: bool, message: str) -> None:
        self._export_btn.setEnabled(True)
        self._progress.setVisible(False)
        self._worker = None

        if success:
            QMessageBox.information(self, "Export Complete", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Export Failed", message)
