"""Workflow controller: seamless Prompt → 3D → Cost → 4D progression.

Provides auto-tab-advance and status notifications for the full
Demo-1 TSMC workflow pipeline.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtWidgets import QProgressBar, QStatusBar

from promptbim.debug import get_logger

if TYPE_CHECKING:
    from promptbim.gui.main_window import MainWindow
    from promptbim.schemas.plan import BuildingPlan

logger = get_logger("gui.workflow_controller")

# Tab indices that match MainWindow._tabs order
TAB_2D_MAP = 0
TAB_3D_MODEL = 1
TAB_SITE_PLAN = 2
TAB_COST = 3
TAB_4D_SIM = 4
TAB_DELTA = 5  # added by delta_panel


class WorkflowStep:
    """Single step in the workflow pipeline."""

    def __init__(self, tab_idx: int, label: str, duration_ms: int = 1500) -> None:
        self.tab_idx = tab_idx
        self.label = label
        self.duration_ms = duration_ms


# Default step sequence for full Demo-1 workflow
DEMO1_STEPS = [
    WorkflowStep(TAB_3D_MODEL, "3D 模型生成完成", 2000),
    WorkflowStep(TAB_COST, "5D 成本估算完成", 1800),
    WorkflowStep(TAB_4D_SIM, "4D 施工模擬就緒", 2000),
    WorkflowStep(TAB_DELTA, "變更對照面板", 1500),
]


class WorkflowController(QObject):
    """Orchestrates the Prompt→3D→Cost→4D tab progression.

    Signals
    -------
    step_changed(int, str) : (tab_index, step_label)
    workflow_complete : all steps finished
    """

    step_changed = Signal(int, str)
    workflow_complete = Signal()

    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self._mw = main_window
        self._steps: list[WorkflowStep] = []
        self._step_idx = 0
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._advance)
        self._running = False
        self._plan: BuildingPlan | None = None

    def run(
        self,
        plan: "BuildingPlan",
        steps: list[WorkflowStep] | None = None,
    ) -> None:
        """Start workflow for a given plan."""
        if self._running:
            self._timer.stop()

        self._plan = plan
        self._steps = steps or DEMO1_STEPS
        self._step_idx = 0
        self._running = True
        logger.info("WorkflowController: starting %d-step workflow", len(self._steps))
        self._advance()

    @Slot()
    def _advance(self) -> None:
        if self._step_idx >= len(self._steps):
            self._running = False
            self.workflow_complete.emit()
            logger.info("WorkflowController: workflow complete")
            return

        step = self._steps[self._step_idx]

        # Switch tab safely (ignore if tab doesn't exist)
        tabs = self._mw._tabs
        if 0 <= step.tab_idx < tabs.count():
            tabs.setCurrentIndex(step.tab_idx)

        # Status bar update
        sb: QStatusBar = self._mw.statusBar()
        sb.showMessage(f"✅ {step.label}")

        self.step_changed.emit(step.tab_idx, step.label)
        logger.debug("WorkflowController step %d: tab=%d %s", self._step_idx, step.tab_idx, step.label)

        self._step_idx += 1
        self._timer.start(step.duration_ms)

    def stop(self) -> None:
        self._timer.stop()
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running


class WorkflowProgressBar(QProgressBar):
    """Slim progress bar that shows workflow pipeline steps."""

    _LABELS = ["Prompt", "3D", "Cost", "4D", "Done"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMaximum(len(self._LABELS) - 1)
        self.setValue(0)
        self.setTextVisible(True)
        self.setFormat("● Prompt")
        self.setFixedHeight(16)
        self.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #555;
                border-radius: 4px;
                background: #1a1a2e;
                color: white;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #2196F3);
                border-radius: 3px;
            }
        """
        )

    def set_step(self, step: int) -> None:
        self.setValue(step)
        if 0 <= step < len(self._LABELS):
            self.setFormat(f"● {self._LABELS[step]}")
