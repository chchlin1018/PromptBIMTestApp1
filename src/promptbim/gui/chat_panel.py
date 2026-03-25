"""Chat panel widget for AI-powered building generation.

Provides a text input + message history area.  Runs the
:class:`Orchestrator` pipeline in a background thread so the GUI stays
responsive.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QProgressBar,
)

if TYPE_CHECKING:
    from promptbim.schemas.land import LandParcel
    from promptbim.schemas.plan import BuildingPlan
    from promptbim.schemas.result import GenerationResult
    from promptbim.schemas.zoning import ZoningRules

from promptbim.debug import get_logger
logger = get_logger("gui.chat_panel")


class _PipelineWorker(QThread):
    """Runs the orchestrator in a background thread."""

    finished = Signal(object)  # GenerationResult
    status_update = Signal(str, float)  # message, progress 0-1
    plan_ready = Signal(object)  # BuildingPlan — emitted before build

    def __init__(
        self,
        prompt: str,
        land: "LandParcel",
        zoning: "ZoningRules",
        orchestrator: "Orchestrator",
    ) -> None:
        super().__init__()
        self._prompt = prompt
        self._land = land
        self._zoning = zoning
        self._orch = orchestrator

    def run(self) -> None:
        from promptbim.agents.orchestrator import PipelineStatus

        result = self._orch.generate(self._prompt, self._land, self._zoning)

        if self._orch.plan is not None:
            self.plan_ready.emit(self._orch.plan)

        self.finished.emit(result)


class _ModifyWorker(QThread):
    """Runs a modification in a background thread."""

    finished = Signal(object, object)  # (BuildingPlan, ModificationRecord)
    status_update = Signal(str, float)
    plan_ready = Signal(object)

    def __init__(
        self,
        command: str,
        orchestrator: "Orchestrator",
        zoning: "ZoningRules | None" = None,
    ) -> None:
        super().__init__()
        self._command = command
        self._orch = orchestrator
        self._zoning = zoning

    def run(self) -> None:
        new_plan, record = self._orch.modify(self._command, self._zoning)
        if new_plan is not None:
            self.plan_ready.emit(new_plan)
        self.finished.emit(new_plan, record)


class ChatPanel(QWidget):
    """Bottom chat panel with message history, input, and generate button."""

    generation_finished = Signal(object)  # GenerationResult
    plan_ready = Signal(object)  # BuildingPlan
    modification_done = Signal(object, object)  # (BuildingPlan, ModificationRecord)
    undo_done = Signal(object)  # BuildingPlan

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker: _PipelineWorker | None = None
        self._modify_worker: _ModifyWorker | None = None

        from promptbim.agents.orchestrator import Orchestrator, PipelineStatus

        self._orchestrator = Orchestrator(
            on_status=lambda s: self._on_status(s.message, s.progress)
        )

        # Voice input
        from promptbim.voice.stt import VoiceInput

        self._voice = VoiceInput()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Message history
        self._history = QTextEdit()
        self._history.setReadOnly(True)
        self._history.setMaximumHeight(150)
        self._history.setPlaceholderText("AI conversation will appear here...")
        layout.addWidget(self._history)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # Input row
        input_row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("Describe the building you want to create...")
        self._input.returnPressed.connect(self._on_send)
        input_row.addWidget(self._input, stretch=1)

        self._mic_btn = QPushButton("Mic")
        self._mic_btn.setFixedWidth(50)
        self._mic_btn.setCheckable(True)
        self._mic_btn.clicked.connect(self._on_mic_toggle)
        input_row.addWidget(self._mic_btn)

        self._gen_btn = QPushButton("Generate")
        self._gen_btn.clicked.connect(self._on_send)
        input_row.addWidget(self._gen_btn)

        self._export_btn = QPushButton("Export")
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._on_export)
        input_row.addWidget(self._export_btn)

        layout.addLayout(input_row)

        # State
        self._land: LandParcel | None = None
        self._zoning: ZoningRules | None = None
        self._has_plan = False
        self._current_plan: BuildingPlan | None = None
        self._current_result: GenerationResult | None = None

    def set_context(
        self, land: "LandParcel", zoning: "ZoningRules | None" = None
    ) -> None:
        """Set the land parcel and zoning rules for generation."""
        self._land = land
        self._zoning = zoning
        self._append_system(
            f"Land loaded: {land.name} ({land.area_sqm:.1f} m\u00b2). Ready to generate!"
        )

    def _on_send(self) -> None:
        prompt = self._input.text().strip()
        if not prompt:
            return
        logger.debug("User input: %s", prompt)

        if self._land is None:
            self._append_system("Please import a land parcel first.")
            return

        busy = (
            (self._worker is not None and self._worker.isRunning())
            or (self._modify_worker is not None and self._modify_worker.isRunning())
        )
        if busy:
            self._append_system("Already in progress...")
            return

        self._append_user(prompt)
        self._input.clear()

        # If we already have a plan, treat as modification
        if self._has_plan and self._orchestrator is not None:
            self._start_modify(prompt)
        else:
            self._start_generate(prompt)

    def _start_generate(self, prompt: str) -> None:
        logger.debug("Pipeline start: generate — prompt=%r", prompt)
        self._gen_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.setValue(0)

        from promptbim.schemas.zoning import ZoningRules

        zoning = self._zoning or ZoningRules()

        self._worker = _PipelineWorker(prompt, self._land, zoning, self._orchestrator)
        self._worker.status_update.connect(self._on_status)
        self._worker.plan_ready.connect(self._on_plan_ready)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _start_modify(self, command: str) -> None:
        logger.debug("Pipeline start: modify — command=%r", command)
        self._gen_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.setValue(0)
        self._append_system("Analyzing modification...")

        from promptbim.schemas.zoning import ZoningRules

        zoning = self._zoning or ZoningRules()

        self._modify_worker = _ModifyWorker(command, self._orchestrator, zoning)
        self._modify_worker.status_update.connect(self._on_status)
        self._modify_worker.plan_ready.connect(self._on_plan_ready)
        self._modify_worker.finished.connect(self._on_modify_finished)
        self._modify_worker.start()

    def _on_modify_finished(self, plan, record) -> None:
        logger.debug("Modify complete: plan=%s, success=%s", plan is not None, record.success if record else False)
        self._gen_btn.setEnabled(True)
        self._progress.setVisible(False)
        self._modify_worker = None

        if plan is not None and record is not None and record.success:
            changed = sum(1 for i in record.impacts if i.before_value != i.after_value)
            self._append_ai(
                f"Modified: {record.command}\n"
                f"  {changed} component(s) affected | "
                f"Stories: {len(plan.stories)} | "
                f"BCR: {plan.building_bcr:.0%} | FAR: {plan.building_far:.2f}"
            )
            self.modification_done.emit(plan, record)
        else:
            error = record.error if record else "No plan to modify"
            self._append_system(f"Modification failed: {error}")

    def request_undo(self) -> None:
        """Called externally (e.g., from modification panel) to undo."""
        if self._orchestrator is None:
            return
        restored, record = self._orchestrator.undo()
        if restored is not None:
            self._has_plan = True
            self._append_system(f"Undo: reverted '{record.command}'")
            self.plan_ready.emit(restored)
            self.undo_done.emit(restored)
        else:
            self._append_system("Nothing to undo.")

    def _on_status(self, message: str, progress: float) -> None:
        self._progress.setValue(int(progress * 100))
        self._append_system(message)

    def _on_mic_toggle(self) -> None:
        """Toggle voice recording on/off."""
        if self._mic_btn.isChecked():
            self._mic_btn.setText("Stop")
            self._mic_btn.setStyleSheet("background-color: #f44336; color: white;")
            self._voice.start_recording()
            self._append_system("Recording... click Stop when done.")
        else:
            self._mic_btn.setText("Mic")
            self._mic_btn.setStyleSheet("")
            self._append_system("Transcribing...")
            self._voice.stop_and_transcribe(callback=self._on_transcription)

    def _on_transcription(self, text: str) -> None:
        """Called from voice thread with transcribed text."""
        if text:
            self._input.setText(text)
            self._append_system(f"Voice: {text}")
        else:
            self._append_system("No speech detected or transcription failed.")

    def _on_export(self) -> None:
        """Open the export dialog."""
        if self._current_plan is None:
            self._append_system("No building to export yet.")
            return
        from promptbim.gui.dialogs.export_dialog import ExportDialog

        dlg = ExportDialog(self._current_plan, self._current_result, parent=self)
        dlg.exec()

    def _on_plan_ready(self, plan: "BuildingPlan") -> None:
        self._current_plan = plan
        self._export_btn.setEnabled(True)
        self.plan_ready.emit(plan)

    def _on_finished(self, result: "GenerationResult") -> None:
        logger.debug("Pipeline complete: success=%s", result.success)
        self._gen_btn.setEnabled(True)
        self._progress.setVisible(False)
        self._worker = None

        if result.success:
            self._has_plan = True
            self._current_result = result
            summary = result.summary
            self._append_ai(
                f"Building generated: {result.building_name}\n"
                f"  Stories: {summary.get('stories', '?')} | "
                f"BCR: {summary.get('bcr', 0):.0%} | "
                f"FAR: {summary.get('far', 0):.1f}"
            )
            if result.ifc_path:
                self._append_system(f"IFC: {result.ifc_path}")
            if result.usd_path:
                self._append_system(f"USD: {result.usd_path}")
        else:
            logger.error("Generation failed: %s", ", ".join(result.errors))
            self._append_system(f"Generation failed: {', '.join(result.errors)}")

        if result.warnings:
            for w in result.warnings:
                self._append_system(f"Warning: {w}")

        self.generation_finished.emit(result)

    def _append_user(self, text: str) -> None:
        self._history.append(f'<b style="color:#2196F3">You:</b> {text}')

    def _append_ai(self, text: str) -> None:
        self._history.append(f'<b style="color:#4CAF50">AI:</b> {text}')

    def _append_system(self, text: str) -> None:
        self._history.append(f'<span style="color:#999">{text}</span>')
