"""Chat panel widget for AI-powered building generation.

Provides a text input + message history area.  Runs the
:class:`Orchestrator` pipeline in a background thread so the GUI stays
responsive.
"""

from __future__ import annotations

import logging
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

logger = logging.getLogger(__name__)


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
        output_dir: str | None = None,
    ) -> None:
        super().__init__()
        self._prompt = prompt
        self._land = land
        self._zoning = zoning
        self._output_dir = output_dir

    def run(self) -> None:
        from promptbim.agents.orchestrator import Orchestrator, PipelineStatus

        def on_status(status: PipelineStatus) -> None:
            self.status_update.emit(status.message, status.progress)

        orch = Orchestrator(output_dir=self._output_dir, on_status=on_status)
        result = orch.generate(self._prompt, self._land, self._zoning)

        # Emit plan so the GUI can display it before build finishes
        if orch.plan is not None:
            self.plan_ready.emit(orch.plan)

        self.finished.emit(result)


class ChatPanel(QWidget):
    """Bottom chat panel with message history, input, and generate button."""

    generation_finished = Signal(object)  # GenerationResult
    plan_ready = Signal(object)  # BuildingPlan

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker: _PipelineWorker | None = None

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
        self._input.returnPressed.connect(self._on_generate)
        input_row.addWidget(self._input, stretch=1)

        self._mic_btn = QPushButton("Mic")
        self._mic_btn.setFixedWidth(50)
        input_row.addWidget(self._mic_btn)

        self._gen_btn = QPushButton("Generate")
        self._gen_btn.clicked.connect(self._on_generate)
        input_row.addWidget(self._gen_btn)

        layout.addLayout(input_row)

        # State
        self._land: LandParcel | None = None
        self._zoning: ZoningRules | None = None

    def set_context(
        self, land: "LandParcel", zoning: "ZoningRules | None" = None
    ) -> None:
        """Set the land parcel and zoning rules for generation."""
        self._land = land
        self._zoning = zoning
        self._append_system(
            f"Land loaded: {land.name} ({land.area_sqm:.1f} m\u00b2). Ready to generate!"
        )

    def _on_generate(self) -> None:
        prompt = self._input.text().strip()
        if not prompt:
            return

        if self._land is None:
            self._append_system("Please import a land parcel first.")
            return

        if self._worker is not None and self._worker.isRunning():
            self._append_system("Generation already in progress...")
            return

        self._append_user(prompt)
        self._input.clear()
        self._gen_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.setValue(0)

        from promptbim.schemas.zoning import ZoningRules

        zoning = self._zoning or ZoningRules()

        self._worker = _PipelineWorker(prompt, self._land, zoning)
        self._worker.status_update.connect(self._on_status)
        self._worker.plan_ready.connect(self._on_plan_ready)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_status(self, message: str, progress: float) -> None:
        self._progress.setValue(int(progress * 100))
        self._append_system(message)

    def _on_plan_ready(self, plan: "BuildingPlan") -> None:
        self.plan_ready.emit(plan)

    def _on_finished(self, result: "GenerationResult") -> None:
        self._gen_btn.setEnabled(True)
        self._progress.setVisible(False)
        self._worker = None

        if result.success:
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
