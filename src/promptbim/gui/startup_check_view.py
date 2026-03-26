"""Startup health check GUI panel.

Displays check results with real-time status updates, categorized view,
error details, and action buttons.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from promptbim.debug import get_logger

logger = get_logger("gui.startup_check")


class _CheckWorker(QThread):
    """Background thread to run health checks."""

    check_done = Signal(int, object)  # (index, CheckResult)
    all_done = Signal(list)  # list[CheckResult]

    def __init__(self, checker):
        super().__init__()
        self._checker = checker

    def run(self):
        results = self._checker.run_all()
        for i, result in enumerate(results):
            self.check_done.emit(i, result)
        self.all_done.emit(results)


class _CheckItemWidget(QFrame):
    """Widget for a single check result row."""

    def __init__(self, index: int, name: str, category: str):
        super().__init__()
        self._index = index
        self.setFrameStyle(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self._icon = QLabel("\u23f3")  # hourglass
        self._icon.setFixedWidth(24)
        layout.addWidget(self._icon)

        self._name_label = QLabel(name)
        self._name_label.setMinimumWidth(200)
        font = self._name_label.font()
        font.setPointSize(13)
        self._name_label.setFont(font)
        layout.addWidget(self._name_label)

        self._status_label = QLabel("Checking...")
        self._status_label.setStyleSheet("color: gray;")
        layout.addWidget(self._status_label, stretch=1)

        self._detail_label = QLabel("")
        self._detail_label.setWordWrap(True)
        self._detail_label.setVisible(False)
        self._detail_label.setStyleSheet("color: #666; font-size: 11px; padding-left: 32px;")

        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.addLayout(layout)
        self._main_layout.addWidget(self._detail_label)
        self.setLayout(self._main_layout)

    def set_result(self, result):
        icons = {"pass": "\u2705", "fail": "\u274c", "warn": "\u26a0\ufe0f", "skip": "\u23ed\ufe0f"}
        self._icon.setText(icons.get(result.status, "?"))

        msg = result.message
        if result.elapsed_ms > 0:
            msg += f" ({result.elapsed_ms:.0f}ms)"
        self._status_label.setText(msg)

        colors = {"pass": "green", "fail": "red", "warn": "#b8860b", "skip": "gray"}
        self._status_label.setStyleSheet(f"color: {colors.get(result.status, 'black')};")

        # Show detail for failures
        if result.status in ("fail", "warn") and (result.detail or result.fix_hint):
            detail_parts = []
            if result.detail:
                detail_parts.append(f"Error: {result.detail}")
            if result.fix_hint:
                detail_parts.append(f"Fix: {result.fix_hint}")
            self._detail_label.setText("\n".join(detail_parts))
            self._detail_label.setVisible(True)


class StartupCheckView(QDialog):
    """Dialog showing startup health check results."""

    check_passed = Signal()  # Emitted when all checks pass
    skip_requested = Signal()  # Emitted when user clicks Skip

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PromptBIM \u2014 System Health Check")
        self.setMinimumSize(QSize(600, 500))
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("System Health Check")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Progress
        self._progress = QProgressBar()
        self._progress.setRange(0, 12)
        self._progress.setValue(0)
        layout.addWidget(self._progress)

        # Summary
        self._summary_label = QLabel("Running checks...")
        self._summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._summary_label)

        # Scroll area for check items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self._items_layout = QVBoxLayout(scroll_widget)
        self._items_layout.setSpacing(2)
        self._items_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, stretch=1)

        # Buttons
        btn_layout = QHBoxLayout()
        self._start_btn = QPushButton("Start")
        self._start_btn.setEnabled(False)
        self._start_btn.clicked.connect(self._on_start)
        btn_layout.addWidget(self._start_btn)

        self._recheck_btn = QPushButton("Re-check")
        self._recheck_btn.setEnabled(False)
        self._recheck_btn.clicked.connect(self._run_checks)
        btn_layout.addWidget(self._recheck_btn)

        self._log_btn = QPushButton("View Log")
        self._log_btn.clicked.connect(self._on_view_log)
        btn_layout.addWidget(self._log_btn)

        self._skip_btn = QPushButton("Skip")
        self._skip_btn.clicked.connect(self._on_skip)
        btn_layout.addWidget(self._skip_btn)

        layout.addLayout(btn_layout)

        self._check_items: list[_CheckItemWidget] = []
        self._results: list = []
        self._worker: _CheckWorker | None = None

    def start_checks(self, settings=None):
        """Initialize and run all health checks."""
        self._setup_items()
        self._run_checks(settings=settings)

    def _setup_items(self):
        # Clear existing
        for item in self._check_items:
            self._items_layout.removeWidget(item)
            item.deleteLater()
        self._check_items.clear()

        check_names = [
            ("Python version", "Python environment"),
            ("Conda env", "Python environment"),
            ("ifcopenshell", "Core dependencies"),
            ("pxr (OpenUSD)", "Core dependencies"),
            ("PySide6", "Core dependencies"),
            ("anthropic SDK", "Core dependencies"),
            ("shapely + pyproj", "Core dependencies"),
            ("pyvista + pyvistaqt", "Core dependencies"),
            ("API Key", "AI services"),
            ("Claude API ping", "AI services"),
            ("Model available", "AI services"),
            ("Filesystem", "Filesystem"),
        ]

        current_category = ""
        insert_pos = 0
        for i, (name, category) in enumerate(check_names):
            if category != current_category:
                current_category = category
                cat_label = QLabel(f"\n{category}")
                cat_font = QFont()
                cat_font.setBold(True)
                cat_font.setPointSize(14)
                cat_label.setFont(cat_font)
                self._items_layout.insertWidget(insert_pos, cat_label)
                insert_pos += 1

            item = _CheckItemWidget(i, name, category)
            self._items_layout.insertWidget(insert_pos, item)
            self._check_items.append(item)
            insert_pos += 1

        self._progress.setRange(0, len(check_names))
        self._progress.setValue(0)

    def _run_checks(self, settings=None):
        """Run health checks in background thread."""
        self._start_btn.setEnabled(False)
        self._recheck_btn.setEnabled(False)
        self._progress.setValue(0)
        self._summary_label.setText("Running checks...")

        # Reset item displays
        for item in self._check_items:
            item._icon.setText("\u23f3")
            item._status_label.setText("Checking...")
            item._status_label.setStyleSheet("color: gray;")
            item._detail_label.setVisible(False)

        from promptbim.startup.health_check import HealthChecker

        checker = HealthChecker(settings)
        self._worker = _CheckWorker(checker)
        self._worker.check_done.connect(self._on_check_done)
        self._worker.all_done.connect(self._on_all_done)
        self._worker.start()

    def _on_check_done(self, index: int, result):
        if index < len(self._check_items):
            self._check_items[index].set_result(result)
        self._progress.setValue(index + 1)

    def _on_all_done(self, results):
        self._results = results
        self._recheck_btn.setEnabled(True)

        passed = sum(1 for r in results if r.status == "pass")
        failed = sum(1 for r in results if r.status == "fail")
        warned = sum(1 for r in results if r.status == "warn")

        parts = [f"{passed}/{len(results)} passed"]
        if warned:
            parts.append(f"{warned} warnings")
        if failed:
            parts.append(f"{failed} failed")
        self._summary_label.setText(" \u2014 ".join(parts))

        if failed == 0:
            self._start_btn.setEnabled(True)
            self._start_btn.setFocus()
            self._summary_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self._start_btn.setEnabled(False)
            self._summary_label.setStyleSheet("color: red; font-weight: bold;")

    def _on_start(self):
        self.check_passed.emit()
        self.accept()

    def _on_skip(self):
        self.skip_requested.emit()
        self.accept()

    def _on_view_log(self):
        from promptbim.debug import setup_file_logging

        log_file = setup_file_logging()
        logger.debug("Log file created: %s", log_file)
        self._summary_label.setText(f"Log: {log_file}")
