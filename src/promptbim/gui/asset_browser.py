"""Asset Browser GUI — Parts Library (零件庫) for PromptBIM Demo-1.

Three-category browser:
  1. Structural   — columns, beams, slabs, walls, foundations
  2. MEP          — HVAC, plumbing, electrical, fire protection
  3. Finishes     — flooring, ceilings, facades, glazing

Features:
  - Category tab switching
  - Keyword search with live filter
  - Asset card grid with thumbnail placeholder + specs
  - "Replace Component" button → emits replace_requested signal
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from promptbim.debug import get_logger

logger = get_logger("gui.asset_browser")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class AssetSpec:
    """Specification for a single BIM component asset."""

    asset_id: str
    name: str
    category: str       # structural | mep | finish
    subcategory: str    # e.g. column, hvac, flooring
    description: str
    material: str = ""
    unit_cost_twd: float = 0.0
    weight_kg_m2: float = 0.0
    tags: list[str] = field(default_factory=list)
    icon_emoji: str = "🧱"


# ---------------------------------------------------------------------------
# Built-in asset library
# ---------------------------------------------------------------------------

ASSET_LIBRARY: list[AssetSpec] = [
    # ── Structural ──────────────────────────────────────────────────────────
    AssetSpec("STR-COL-RC-400",  "RC Column 400×400",       "structural", "column",  "Reinforced concrete column 400×400mm, C30",           "RC C30",    8500.0,  960.0, ["rc","column","400"],  "🏛️"),
    AssetSpec("STR-COL-SRC-400", "SRC Column 400×400",      "structural", "column",  "Steel-reinforced concrete, high-rise",                "SRC",      12000.0, 1200.0, ["src","column","high-rise"], "🏛️"),
    AssetSpec("STR-BEAM-RC-600", "RC Beam 600×300",         "structural", "beam",    "RC beam 600×300mm, typical floor",                    "RC C30",    5200.0,  540.0, ["rc","beam"],           "🏗️"),
    AssetSpec("STR-BEAM-WIDE",   "Wide Flange Beam W400",   "structural", "beam",    "Steel wide flange W400 series",                       "A36 Steel", 9800.0,  390.0, ["steel","wide-flange"], "🏗️"),
    AssetSpec("STR-SLAB-120",    "RC Slab t=120mm",         "structural", "slab",    "Reinforced concrete slab 120mm thick",                "RC C30",    2800.0,  300.0, ["slab","rc"],           "▭"),
    AssetSpec("STR-SLAB-200",    "PT Slab t=200mm",         "structural", "slab",    "Post-tensioned slab for long span",                   "PT C35",    4500.0,  500.0, ["slab","pt","longspan"],"▭"),
    AssetSpec("STR-WALL-200",    "Shear Wall 200mm",        "structural", "wall",    "RC shear wall 200mm, seismic zone",                   "RC C30",    3500.0,  480.0, ["wall","shear","seismic"],"🧱"),
    AssetSpec("STR-FND-PILE",    "Bored Pile φ800",         "structural", "foundation","Cast-in-place bored pile φ800mm",                  "RC C35",   25000.0, 1500.0, ["pile","foundation"],   "⬇️"),
    AssetSpec("STR-FND-MAT",     "Mat Foundation t=800",    "structural", "foundation","Mat/raft foundation for high-rise",                 "RC C35",   18000.0, 2000.0, ["mat","raft"],          "⬇️"),
    # ── MEP ─────────────────────────────────────────────────────────────────
    AssetSpec("MEP-HVAC-AHU",    "AHU 10,000 CMH",          "mep", "hvac",       "Air handling unit, 10,000 m³/h, Class-100 capable",   "Steel",    95000.0,  280.0, ["hvac","ahu","cleanroom"],"❄️"),
    AssetSpec("MEP-HVAC-FCU",    "FCU Ceiling Cassette 4P", "mep", "hvac",       "4-pipe fan coil unit, ceiling cassette type",         "Steel",    15000.0,   18.0, ["hvac","fcu","ceiling"], "❄️"),
    AssetSpec("MEP-HVAC-CHILLER","Chiller 300RT",           "mep", "hvac",       "Centrifugal chiller, 300 refrigeration tons",         "Steel",   850000.0,4500.0, ["hvac","chiller"],       "❄️"),
    AssetSpec("MEP-PLUMB-PP",    "PP-R Pipe DN100",         "mep", "plumbing",   "PP-R pressure pipe DN100 for domestic water",         "PP-R",      1200.0,    8.5, ["plumbing","pipe"],      "🚰"),
    AssetSpec("MEP-PLUMB-PUMP",  "Centrifugal Pump 15kW",   "mep", "plumbing",   "Horizontal centrifugal pump 15kW",                    "CI/Steel", 45000.0,  150.0, ["pump","plumbing"],      "🚰"),
    AssetSpec("MEP-ELEC-BUS",    "Busway 1600A",            "mep", "electrical", "Sandwich busway 1600A for data center",               "Al/Cu",    85000.0,   35.0, ["busway","electrical"],  "⚡"),
    AssetSpec("MEP-ELEC-UPS",    "UPS 500kVA",              "mep", "electrical", "Online UPS double-conversion 500kVA",                 "Steel",   380000.0, 1800.0, ["ups","electrical","dc"],"⚡"),
    AssetSpec("MEP-FIRE-SPRINK", "Upright Sprinkler K80",   "mep", "fire_protection","Standard response upright sprinkler K80",         "Bronze",    2500.0,    1.5, ["fire","sprinkler"],     "🔥"),
    AssetSpec("MEP-FIRE-HALON",  "FM-200 System 50kg",      "mep", "fire_protection","Clean agent fire suppression FM-200 50kg",        "Steel",   120000.0,   85.0, ["fire","fm200","clean"], "🔥"),
    # ── Finishes ─────────────────────────────────────────────────────────────
    AssetSpec("FIN-FLOOR-ESD",   "ESD Raised Floor 600×600","finish","flooring",  "Electrostatic dissipative raised access floor",       "Steel/ESD",  8800.0,  36.0, ["floor","esd","raised"],  "🟫"),
    AssetSpec("FIN-FLOOR-TILE",  "Porcelain Tile 600×600",  "finish","flooring",  "Anti-slip porcelain tile 600×600mm",                  "Ceramic",    1200.0,  22.0, ["tile","floor"],          "🟫"),
    AssetSpec("FIN-CEIL-ACT",    "ACT Ceiling 600×600",     "finish","ceiling",   "Acoustic ceiling tile 600×600mm, NRC 0.7",            "Mineral",    1500.0,   8.0, ["ceiling","acoustic"],    "⬜"),
    AssetSpec("FIN-CEIL-GYP",    "Gypsum Board Ceiling",    "finish","ceiling",   "Double-layer gypsum board suspended ceiling",         "Gypsum",     900.0,   18.0, ["ceiling","gypsum"],      "⬜"),
    AssetSpec("FIN-FAC-GRC",     "GRC Facade Panel",        "finish","facade",    "Glass-reinforced concrete facade panel 50mm",         "GRC",       12000.0, 120.0, ["facade","grc"],          "🏢"),
    AssetSpec("FIN-FAC-GLASS",   "Low-E Double Glazing",    "finish","glazing",   "6+12A+6 Low-E insulated glazing unit",                "Glass",      8500.0,  30.0, ["glazing","low-e"],       "🪟"),
]

# Category → sub-categories
CATEGORIES = {
    "structural": {"label": "🏗️ Structural", "emoji": "🏗️"},
    "mep":        {"label": "⚙️ MEP",        "emoji": "⚙️"},
    "finish":     {"label": "🎨 Finishes",   "emoji": "🎨"},
}


# ---------------------------------------------------------------------------
# Asset Card widget
# ---------------------------------------------------------------------------

class _AssetCard(QFrame):
    """A single asset card showing icon, name, specs, and Replace button."""

    replace_requested = Signal(str)  # asset_id

    def __init__(self, spec: AssetSpec, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._spec = spec
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setStyleSheet("""
            _AssetCard, QFrame {
                background: #1e2a3a;
                border: 1px solid #334;
                border-radius: 6px;
            }
            QFrame:hover {
                border: 1px solid #4CAF50;
            }
        """)
        self.setFixedWidth(180)
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Icon + name
        icon_label = QLabel(spec.icon_emoji)
        icon_label.setStyleSheet("font-size: 28px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        name_label = QLabel(spec.name)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("font-weight: bold; font-size: 11px; color: white;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Sub-category
        sub_label = QLabel(spec.subcategory.upper())
        sub_label.setStyleSheet("font-size: 9px; color: #888;")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub_label)

        # Cost
        cost_label = QLabel(f"NT${spec.unit_cost_twd:,.0f}")
        cost_label.setStyleSheet("font-size: 10px; color: #4CAF50;")
        cost_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(cost_label)

        layout.addStretch()

        # Replace button
        btn = QPushButton("Replace")
        btn.setFixedHeight(24)
        btn.setStyleSheet("""
            QPushButton {
                background: #2196F3; color: white;
                border-radius: 3px; font-size: 11px;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        btn.clicked.connect(lambda: self.replace_requested.emit(spec.asset_id))
        layout.addWidget(btn)

    @property
    def spec(self) -> AssetSpec:
        return self._spec


# ---------------------------------------------------------------------------
# Asset Grid Panel
# ---------------------------------------------------------------------------

class _AssetGrid(QScrollArea):
    """Scrollable grid of AssetCard widgets."""

    replace_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._container = QWidget()
        self._grid = QGridLayout(self._container)
        self._grid.setSpacing(8)
        self._grid.setContentsMargins(8, 8, 8, 8)
        self.setWidget(self._container)
        self._cards: list[_AssetCard] = []

    def load_assets(self, assets: list[AssetSpec]) -> None:
        # Clear existing
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards.clear()

        cols = 3
        for i, spec in enumerate(assets):
            card = _AssetCard(spec)
            card.replace_requested.connect(self.replace_requested)
            self._grid.addWidget(card, i // cols, i % cols)
            self._cards.append(card)

        # Add spacer
        self._grid.setRowStretch(max(1, len(assets) // cols + 1), 1)
        logger.debug("AssetGrid loaded %d assets", len(assets))


# ---------------------------------------------------------------------------
# Main Asset Browser
# ---------------------------------------------------------------------------

class AssetBrowser(QWidget):
    """Three-category asset browser with search and replace.

    Signals
    -------
    replace_requested(str, str) : (asset_id, component_label) — user clicked Replace
    """

    replace_requested = Signal(str, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._selected_component: str = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        header_row = QHBoxLayout()
        title = QLabel("📦 零件庫 — Asset Browser")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        header_row.addWidget(title)
        header_row.addStretch()

        self._component_label = QLabel("Target: —")
        self._component_label.setStyleSheet("color: #888; font-size: 11px;")
        header_row.addWidget(self._component_label)
        layout.addLayout(header_row)

        # Search bar
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("🔍"))
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search assets (e.g. column, hvac, glass)…")
        self._search.textChanged.connect(self._on_search_changed)
        search_row.addWidget(self._search, stretch=1)
        layout.addLayout(search_row)

        # Tab widget: Structural | MEP | Finishes
        self._tabs = QTabWidget()
        self._grids: dict[str, _AssetGrid] = {}

        for cat_id, cat_info in CATEGORIES.items():
            grid = _AssetGrid()
            grid.replace_requested.connect(lambda aid, cid=cat_id: self._on_replace(aid))
            self._tabs.addTab(grid, cat_info["label"])
            self._grids[cat_id] = grid

        layout.addWidget(self._tabs, stretch=1)

        # Status
        self._status = QLabel("24 assets loaded | 3 categories")
        self._status.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self._status)

        # Initial load
        self._reload_all("")

    def _reload_all(self, query: str) -> None:
        q = query.lower()
        for cat_id, grid in self._grids.items():
            assets = [
                a for a in ASSET_LIBRARY
                if a.category == cat_id
                and (
                    not q
                    or q in a.name.lower()
                    or q in a.description.lower()
                    or any(q in t for t in a.tags)
                    or q in a.subcategory.lower()
                )
            ]
            grid.load_assets(assets)
        total = sum(
            1 for a in ASSET_LIBRARY
            if not q or q in a.name.lower() or any(q in t for t in a.tags)
        )
        self._status.setText(f"{total} assets matching '{q}'" if q else f"{len(ASSET_LIBRARY)} assets loaded | 3 categories")

    def _on_search_changed(self, text: str) -> None:
        self._reload_all(text)

    def _on_replace(self, asset_id: str) -> None:
        spec = next((a for a in ASSET_LIBRARY if a.asset_id == asset_id), None)
        if spec is None:
            return
        logger.info("Replace requested: %s → %s", self._selected_component or "(none)", asset_id)
        self.replace_requested.emit(asset_id, self._selected_component)

    def set_target_component(self, label: str) -> None:
        """Set the component label that will be replaced."""
        self._selected_component = label
        display = label[:30] + "…" if len(label) > 30 else label
        self._component_label.setText(f"Target: {display}")

    def get_asset(self, asset_id: str) -> AssetSpec | None:
        return next((a for a in ASSET_LIBRARY if a.asset_id == asset_id), None)
