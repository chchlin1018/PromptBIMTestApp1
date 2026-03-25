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
    QTextEdit,
    QLineEdit,
    QPushButton,
    QStatusBar,
)
from PySide6.QtCore import Qt

from promptbim import __version__


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PromptBIM v{__version__} - AI-Powered BIM Generator")
        self.setMinimumSize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main splitter: left panel | center view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, stretch=1)

        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Project Tree"))
        left_layout.addWidget(QLabel("No land data loaded"))
        left_layout.addStretch()
        left_panel.setMaximumWidth(350)
        splitter.addWidget(left_panel)

        # Center tab view
        tabs = QTabWidget()
        tabs.addTab(QLabel("2D Map - Land parcel view"), "2D Map")
        tabs.addTab(QLabel("3D Model - Building preview"), "3D Model")
        splitter.addWidget(tabs)

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


def launch_main_window():
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
