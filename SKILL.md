# PromptBIMTestApp1 — SKILL.md v3.0

> Claude Code SSOT — 開發前必讀
> 最後更新: 2026-03-25

---

## 1. 專案核心定位

**用自然語言在一塊真實土地上蓋建築。**

使用者流程：
1. 匯入土地資料（地籍圖 PDF、Shapefile、GeoJSON、手動輸入座標）
2. 在 2D 地圖上看到土地輪廓、面積、形狀
3. 用文字或語音描述想蓋的建築
4. AI 自動在這塊地上生成 3D BIM 建築模型
5. 同時輸出 IFC（BIM 語義）+ OpenUSD（Digital Twin / IDTF）
6. 桌面 3D 互動預覽（旋轉/縮放/剖面）

**⚠️ 硬性規則：零商業軟體依賴。全部使用開源 GitHub / Library。**

---

## 2. 100% 開源技術棧

```
┌──────────────────────────────────────────────────────────┐
│                  PromptBIMTestApp1                        │
│                                                          │
│  🖥️ Desktop GUI — PySide6 (LGPL-3.0)                    │
│  ├─ 2D 地籍視圖: matplotlib + shapely (嵌入 Qt)          │
│  ├─ 3D 建築視圖: PyVista + pyvistaqt (MIT)               │
│  └─ Chat 面板: QTextEdit + 語音按鈕                      │
│                                                          │
│  🗺️ GIS / 土地輸入                                       │
│  ├─ Shapefile (.shp): geopandas + fiona (BSD)            │
│  ├─ GeoJSON (.geojson): geopandas (BSD)                  │
│  ├─ KML (.kml): fastkml (LGPL)                           │
│  ├─ PDF 地籍圖: PyMuPDF/fitz (AGPL) → 圖片 + OCR        │
│  ├─ DXF (.dxf): ezdxf (MIT)                              │
│  ├─ 手動繪製: matplotlib interactive polygon              │
│  └─ 座標系轉換: pyproj (MIT)                             │
│                                                          │
│  🧠 AI — Claude API (Anthropic SDK, MIT)                 │
│  ├─ Agent 1: Enhancer（需求增強）                         │
│  ├─ Agent 2: Planner（建築規劃 + 退縮/容積計算）          │
│  └─ Agent 4: Checker（規則檢查 + 修正建議）              │
│                                                          │
│  🏗️ BIM 生成（純 Python，不用 LLM）                      │
│  ├─ IFC: IfcOpenShell 0.8+ (LGPL)                       │
│  ├─ USD: usd-core / pxr (Apache-2.0)                    │
│  ├─ 幾何: shapely (BSD) + numpy + trimesh (MIT)          │
│  └─ 材質: 內建 PBR 預設                                  │
│                                                          │
│  👁️ 3D 渲染（嵌入桌面 App）                              │
│  ├─ PyVista (MIT) — VTK Python 高階封裝                  │
│  ├─ pyvistaqt (MIT) — Qt 嵌入元件                        │
│  └─ F3D CLI (BSD) — 離線批次渲染 PNG（選用）             │
│                                                          │
│  🗣️ 語音                                                 │
│  ├─ whisper.cpp / faster-whisper (MIT) — 本地 STT        │
│  └─ 或 macOS NSSSpeechRecognizer (系統 API)              │
│                                                          │
│  💾 Storage: 本地檔案 + SQLite                           │
└──────────────────────────────────────────────────────────┘
```

### 2.1 依賴 License 審計（全部開源）

| 依賴 | License | 用途 |
|------|---------|------|
| PySide6 | LGPL-3.0 | Desktop GUI |
| PyVista | MIT | 3D 視覺化 |
| pyvistaqt | MIT | PyVista ↔ Qt 橋接 |
| IfcOpenShell | LGPL-3.0 | IFC BIM 生成 |
| usd-core (pxr) | Apache-2.0 | OpenUSD 生成 |
| anthropic SDK | MIT | Claude API |
| geopandas | BSD-3 | GIS 資料讀取 |
| shapely | BSD-3 | 2D 幾何運算 |
| fiona | BSD-3 | Shapefile/GeoJSON I/O |
| pyproj | MIT | 座標系轉換 |
| ezdxf | MIT | DXF 讀取 |
| PyMuPDF (fitz) | AGPL-3.0 | PDF 地籍圖解析 |
| fastkml | LGPL-3.0 | KML 讀取 |
| numpy | BSD-3 | 數值運算 |
| trimesh | MIT | Mesh 操作 |
| matplotlib | PSF/BSD | 2D 繪圖 (地籍+平面圖) |
| Pillow | HPND | 圖片處理 |
| faster-whisper | MIT | 本地語音辨識 |
| pydantic | MIT | 資料驗證 |
| rich | MIT | Terminal UI |

> **PyMuPDF 注意:** AGPL-3.0 要求開源分發。如需避免 AGPL，可改用 `pdfplumber`（MIT）作為 PDF 解析替代方案。

---

## 3. 桌面 App 架構

### 3.1 主視窗佈局

```
┌──────────────────────────────────────────────────────┐
│  Menu Bar: File | Edit | View | Tools | Help         │
├────────────────────┬─────────────────────────────────┤
│                    │                                 │
│   左側面板         │         中央視圖區               │
│   (350px)          │                                 │
│                    │   ┌─ Tab: 2D 地籍 ──────────┐  │
│  ┌──────────────┐  │   │                         │  │
│  │ 📁 專案樹    │  │   │  [matplotlib canvas]    │  │
│  │  └ 土地       │  │   │   土地輪廓              │  │
│  │  └ 建築      │  │   │   建築 footprint        │  │
│  │    └ 1F      │  │   │   退縮線                 │  │
│  │    └ 2F      │  │   │   面積標注               │  │
│  │    └ 3F      │  │   │                         │  │
│  └──────────────┘  │   └─────────────────────────┘  │
│                    │                                 │
│  ┌──────────────┐  │   ┌─ Tab: 3D 建築 ──────────┐  │
│  │ 📋 屬性面板  │  │   │                         │  │
│  │  面積: 450㎡  │  │   │  [PyVista QtInteractor] │  │
│  │  樓層: 3     │  │   │   3D 建築模型            │  │
│  │  容積率: 2.1 │  │   │   互動旋轉/縮放         │  │
│  │  建蔽率: 58% │  │   │   樓層剖面              │  │
│  └──────────────┘  │   │                         │  │
│                    │   └─────────────────────────┘  │
├────────────────────┴─────────────────────────────────┤
│  底部: AI Chat 面板                                   │
│  ┌───────────────────────────────────────────┬─────┐ │
│  │ 💬 在這塊地上蓋3層辦公樓，一樓停車場...    │ 🎤  │ │
│  └───────────────────────────────────────────┴─────┘ │
│  Claude: 正在分析土地形狀... 規劃建築配置中...        │
│  ✅ 已生成 3 層辦公大樓 (建蔽率 55%, 容積率 165%)     │
└──────────────────────────────────────────────────────┘
```

### 3.2 使用者流程

```
Step 1: 匯入土地
  ├─ 拖放 .shp / .geojson / .kml / .dxf / .pdf
  ├─ 或手動輸入座標 / 繪製多邊形
  └─ 自動計算: 面積、周長、形狀、方位

Step 2: 設定土地參數（可選）
  ├─ 使用分區: 住宅/商業/工業
  ├─ 容積率上限 / 建蔽率上限
  ├─ 退縮距離（前/後/左/右）
  └─ 高度限制

Step 3: AI 對話生成建築
  ├─ 文字: "在這塊地上蓋一棟3層樓住宅..."
  ├─ 語音: 按住 🎤 說話
  └─ AI 自動考慮土地形狀 + 退縮 + 容積率

Step 4: 預覽與調整
  ├─ 2D Tab: 看 footprint 是否合理
  ├─ 3D Tab: 互動瀏覽建築模型
  └─ 文字微調: "把入口移到南面" / "加一間會議室"

Step 5: 匯出
  ├─ model.ifc (BIM 完整語義)
  ├─ model.usda (OpenUSD, IDTF 接口)
  ├─ floorplan.svg (各層平面圖)
  ├─ site_plan.svg (配置圖含土地+建築)
  └─ summary.json (面積/容積率/建蔽率 等)
```

---

## 4. 專案結構

```
PromptBIMTestApp1/
├── README.md
├── SKILL.md
├── LICENSE                         # MIT
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── src/
│   └── promptbim/
│       ├── __init__.py
│       ├── __main__.py             # CLI + GUI 啟動
│       ├── config.py               # Pydantic BaseSettings
│       │
│       ├── gui/                    # === Desktop GUI (PySide6) ===
│       │   ├── __init__.py
│       │   ├── main_window.py      # 主視窗 (QMainWindow)
│       │   ├── land_panel.py       # 左側: 土地資訊面板
│       │   ├── property_panel.py   # 左側: 建築屬性面板
│       │   ├── map_view.py         # 中央 Tab: 2D 地籍/配置圖 (matplotlib)
│       │   ├── model_view.py       # 中央 Tab: 3D 建築模型 (PyVista)
│       │   ├── chat_panel.py       # 底部: AI Chat + 語音
│       │   ├── project_tree.py     # 左側: 專案結構樹
│       │   └── dialogs/
│       │       ├── import_land.py  # 匯入土地對話框
│       │       ├── export.py       # 匯出對話框
│       │       └── settings.py     # 設定對話框
│       │
│       ├── land/                   # === 土地/GIS 處理 ===
│       │   ├── __init__.py
│       │   ├── parsers/
│       │   │   ├── __init__.py
│       │   │   ├── shapefile.py    # .shp 讀取 (geopandas/fiona)
│       │   │   ├── geojson.py      # .geojson 讀取
│       │   │   ├── kml.py          # .kml 讀取 (fastkml)
│       │   │   ├── dxf.py          # .dxf 讀取 (ezdxf)
│       │   │   ├── pdf_cadastral.py # PDF 地籍圖 → 輪廓萃取
│       │   │   └── manual.py       # 手動座標/繪製
│       │   ├── land_model.py       # 土地資料模型
│       │   ├── setback.py          # 退縮線計算 (shapely buffer)
│       │   ├── zoning.py           # 使用分區規則
│       │   └── projection.py       # 座標系轉換 (pyproj)
│       │
│       ├── agents/                 # === AI Multi-Agent ===
│       │   ├── __init__.py
│       │   ├── base.py             # BaseAgent (Claude API)
│       │   ├── enhancer.py         # Agent 1: 需求增強
│       │   ├── planner.py          # Agent 2: 在土地上規劃建築
│       │   ├── builder.py          # Agent 3: 生成 IFC+USD (不用 LLM)
│       │   ├── checker.py          # Agent 4: 規則檢查
│       │   └── orchestrator.py     # Pipeline 編排
│       │
│       ├── bim/                    # === BIM 生成 ===
│       │   ├── __init__.py
│       │   ├── ifc_generator.py    # IfcOpenShell 封裝
│       │   ├── usd_generator.py    # pxr OpenUSD 封裝
│       │   ├── geometry.py         # 共用幾何 (牆體/樓板/屋頂 mesh)
│       │   ├── materials.py        # 材質定義
│       │   ├── rules.py            # BIM 規則引擎
│       │   └── templates/
│       │       ├── __init__.py
│       │       ├── office.py
│       │       ├── residential.py
│       │       └── industrial.py
│       │
│       ├── viz/                    # === 視覺化 ===
│       │   ├── __init__.py
│       │   ├── site_plan.py        # 2D 配置圖 (土地+建築 footprint)
│       │   ├── floorplan.py        # 2D 平面圖 SVG
│       │   ├── model_3d.py         # 3D 模型組裝 (PyVista mesh)
│       │   └── renderer.py         # F3D CLI 批次渲染 (選用)
│       │
│       ├── voice/                  # === 語音 ===
│       │   ├── __init__.py
│       │   └── stt.py              # faster-whisper 本地辨識
│       │
│       ├── mcp/                    # === MCP Server ===
│       │   ├── __init__.py
│       │   └── server.py
│       │
│       └── schemas/                # === Pydantic Models ===
│           ├── __init__.py
│           ├── land.py             # LandParcel (polygon, area, setbacks)
│           ├── zoning.py           # ZoningRules (FAR, BCR, height_limit)
│           ├── requirement.py      # BuildingRequirement
│           ├── plan.py             # BuildingPlan
│           └── result.py           # GenerationResult
│
├── tests/
│   ├── test_land/
│   ├── test_agents/
│   ├── test_bim/
│   ├── test_gui/
│   └── fixtures/
│       ├── sample_parcel.geojson
│       ├── sample_cadastral.pdf
│       └── sample_plan.json
│
├── examples/
│   ├── 01_import_land.py
│   ├── 02_simple_box_on_land.py
│   ├── 03_full_pipeline.py
│   └── test_prompts.txt
│
├── resources/                      # App 資源
│   ├── icons/
│   └── styles/
│       └── app.qss                 # Qt 樣式表
│
└── output/                         # .gitignore
```

---

## 5. 核心 Schema（Pydantic）

### 5.1 LandParcel（土地）

```python
# schemas/land.py
from pydantic import BaseModel
from shapely.geometry import Polygon

class LandParcel(BaseModel):
    """一筆土地的完整資訊"""
    name: str = "Untitled Parcel"
    # 幾何
    boundary: list[tuple[float, float]]  # 土地邊界座標 [(x,y), ...]
    area_sqm: float                      # 面積 (平方公尺)
    perimeter_m: float                   # 周長
    # 座標系
    crs: str = "EPSG:4326"              # 原始座標系
    local_origin: tuple[float, float] = (0, 0)  # 本地座標原點
    # 來源
    source_file: str | None = None       # 原始檔案路徑
    source_type: str = "manual"          # shapefile/geojson/kml/dxf/pdf/manual

    class Config:
        arbitrary_types_allowed = True
```

### 5.2 ZoningRules（分區規則）

```python
# schemas/zoning.py
class ZoningRules(BaseModel):
    """使用分區規則"""
    zone_type: str = "residential"       # residential/commercial/industrial
    far_limit: float = 2.0              # 容積率上限 (Floor Area Ratio)
    bcr_limit: float = 0.6             # 建蔽率上限 (Building Coverage Ratio)
    height_limit_m: float = 15.0        # 高度限制 (公尺)
    setback_front_m: float = 5.0        # 前方退縮
    setback_back_m: float = 3.0         # 後方退縮
    setback_left_m: float = 2.0         # 左側退縮
    setback_right_m: float = 2.0        # 右側退縮
    min_parking_per_unit: float = 1.0   # 每戶停車位
```

### 5.3 BuildingPlan（Agent 2 輸出）

```python
# schemas/plan.py — Agent 2 (Planner) 的輸出
class BuildingPlan(BaseModel):
    """建築規劃（在土地上的配置）"""
    name: str
    # 土地資訊（從 LandParcel 帶入）
    land_boundary: list[tuple[float, float]]
    buildable_area: list[tuple[float, float]]  # 退縮後可建範圍

    # 建築配置
    building_footprint: list[tuple[float, float]]  # 建築 footprint
    building_bcr: float                            # 實際建蔽率
    building_far: float                            # 實際容積率

    # 樓層
    stories: list[StoryPlan]

    # 屋頂
    roof: RoofPlan

class StoryPlan(BaseModel):
    name: str                    # "1F", "2F", "B1"
    elevation_m: float           # 樓層標高
    height_m: float              # 層高
    walls: list[WallDef]
    spaces: list[SpaceDef]
    openings: list[OpeningDef]
    slab_boundary: list[tuple[float, float]]

class WallDef(BaseModel):
    start: tuple[float, float]
    end: tuple[float, float]
    thickness_m: float = 0.2
    wall_type: str = "exterior"  # exterior/interior/partition

class SpaceDef(BaseModel):
    name: str                    # "客廳", "Office A"
    boundary: list[tuple[float, float]]
    space_type: str              # living/bedroom/office/meeting/corridor/bathroom
    area_sqm: float

class OpeningDef(BaseModel):
    wall_index: int
    offset_m: float              # 沿牆偏移
    width_m: float
    height_m: float
    sill_height_m: float = 0.0   # 窗台高 (門=0, 窗=0.9)
    opening_type: str = "door"   # door/window
```

---

## 6. Agent 2 (Planner) — 關鍵 Prompt 設計

Planner 是最關鍵的 Agent：它必須**在真實土地形狀上**規劃合理的建築。

```python
PLANNER_SYSTEM_PROMPT = """
You are an expert architect and urban planner. Your task is to generate a
BuildingPlan JSON that places a building on a real land parcel.

## INPUT
You will receive:
1. LandParcel: boundary coordinates, area, shape
2. ZoningRules: FAR limit, BCR limit, height limit, setbacks
3. BuildingRequirement: user's building description (enhanced by Agent 1)

## CONSTRAINTS (MUST follow)
- Building footprint MUST fit inside the buildable area (land minus setbacks)
- BCR (building footprint area / land area) MUST NOT exceed bcr_limit
- FAR (total floor area / land area) MUST NOT exceed far_limit
- Building height MUST NOT exceed height_limit_m
- All coordinates are in METERS, relative to land's local origin
- Walls must form closed polygons per floor
- Every space must be bounded by walls
- Corridors minimum 1.2m width
- Doors minimum 0.9m width, 2.1m height
- Windows minimum 0.6m width, sill height 0.9m for non-ground floors

## OUTPUT
Return a valid BuildingPlan JSON matching the schema exactly.
All coordinates must be precise to 0.01m.
"""
```

---

## 7. pyproject.toml

```toml
[project]
name = "promptbim"
version = "0.1.0"
description = "Prompt to BIM — AI-powered building generation on real land parcels"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Michael Lin", email = "michael@realitymatrix.com"}]

dependencies = [
    # GUI
    "PySide6>=6.6",
    "pyvista>=0.43",
    "pyvistaqt>=0.11",

    # AI
    "anthropic>=0.40.0",

    # BIM
    "ifcopenshell>=0.8.0",
    "usd-core>=24.0",

    # GIS / Land
    "geopandas>=0.14",
    "shapely>=2.0",
    "fiona>=1.9",
    "pyproj>=3.6",
    "ezdxf>=1.1",
    "fastkml>=1.0",

    # Geometry & Viz
    "numpy>=1.26",
    "trimesh>=4.0",
    "matplotlib>=3.8",
    "Pillow>=10.0",

    # Infra
    "pydantic>=2.0",
    "python-dotenv>=1.0",
    "rich>=13.0",
]

[project.optional-dependencies]
pdf = ["pdfplumber>=0.10"]           # PDF 地籍圖 (MIT, 替代 PyMuPDF AGPL)
voice = ["faster-whisper>=1.0"]      # 本地語音辨識 (MIT)
mcp = ["mcp>=1.0"]                   # Claude Desktop MCP
dev = ["pytest>=8.0", "ruff>=0.4", "pytest-qt>=4.3"]

[project.scripts]
promptbim = "promptbim.__main__:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## 8. 開發路線圖

### P0: 骨架 + 環境 (~1 天)
- [ ] GitHub repo + 完整目錄結構
- [ ] pyproject.toml + 所有依賴安裝驗證
- [ ] PySide6 空白主視窗可啟動
- [ ] `promptbim gui` 啟動 / `promptbim --version`
- **驗收:** macOS 上跑出空白 Qt 視窗

### P1: 土地匯入 + 2D 視圖 (~3 天)
- [ ] `land/parsers/` — GeoJSON, Shapefile, DXF, 手動座標
- [ ] `schemas/land.py` + `schemas/zoning.py`
- [ ] `land/setback.py` — 退縮線計算
- [ ] `gui/map_view.py` — matplotlib 嵌入 Qt 顯示土地
- [ ] `gui/land_panel.py` — 土地面積/形狀/分區資訊
- [ ] `gui/dialogs/import_land.py` — 拖放或選檔匯入
- **驗收:** 拖放 .geojson 進視窗 → 顯示土地輪廓 + 面積 + 退縮線

### P2: IFC + USD 生成核心 (~3 天)
- [ ] `bim/geometry.py` — 牆/板/屋頂 mesh 生成
- [ ] `bim/ifc_generator.py` — IfcOpenShell 高階封裝
- [ ] `bim/usd_generator.py` — pxr USD 封裝
- [ ] `schemas/plan.py` — BuildingPlan 完整 schema
- [ ] `examples/02_simple_box_on_land.py`
- **驗收:** 硬編碼 BuildingPlan → .ifc + .usda 雙輸出，兩者都可開啟

### P3: 3D 互動預覽 (~2 天)
- [ ] `viz/model_3d.py` — BuildingPlan → PyVista mesh 組裝
- [ ] `gui/model_view.py` — pyvistaqt 嵌入 Qt
- [ ] 樓層剖面切換
- [ ] `viz/site_plan.py` — 2D 配置圖 (土地+建築疊合)
- **驗收:** 生成後 3D Tab 自動顯示可旋轉的建築模型

### P4: AI Agent Pipeline (~3 天)
- [ ] `agents/base.py` — Claude API wrapper
- [ ] `agents/enhancer.py` — 需求增強 (含土地 context)
- [ ] `agents/planner.py` — 在土地上規劃建築 (關鍵 prompt)
- [ ] `agents/builder.py` — BuildingPlan → IFC+USD (純 Python)
- [ ] `agents/checker.py` — 容積率/建蔽率/退縮 驗證
- [ ] `agents/orchestrator.py` — 串接 + 迭代修正
- [ ] `gui/chat_panel.py` — Chat UI 整合
- **驗收:** 在 Chat 輸入描述 → 自動在土地上生成建築 → 2D+3D 同步更新

### P5: 語音 + 匯出 + 打磨 (~2 天)
- [ ] `voice/stt.py` — faster-whisper 本地辨識
- [ ] 語音按鈕整合
- [ ] 匯出對話框 (IFC + USD + SVG + JSON 一鍵打包)
- [ ] `viz/floorplan.py` — 各層平面圖 SVG
- [ ] 配置圖加建築陰影 + 方位指北針
- **驗收:** 語音描述 → 完整生成 → 一鍵匯出 5 件套

### P6: 進階 (未來)
- [ ] PDF 地籍圖 OCR 解析
- [ ] KML 匯入 + 衛星底圖疊加
- [ ] MCP Server (Claude Desktop 整合)
- [ ] USDZ 打包 (Apple Quick Look)
- [ ] 多建築 template
- [ ] Windows 測試 + 打包 (.exe)
- [ ] 地形高程整合

---

## 9. 環境設定 (Claude Code 直接執行)

```bash
# 建立 repo
cd ~/Documents/MyProjects
gh repo create chchlin1018/PromptBIMTestApp1 --private --clone
cd PromptBIMTestApp1

# Python 環境 (conda 推薦，因 ifcopenshell)
conda create -n promptbim python=3.11 -y
conda activate promptbim

# 核心依賴
conda install -c conda-forge ifcopenshell -y
pip install PySide6 pyvista pyvistaqt
pip install anthropic pydantic python-dotenv rich
pip install usd-core
pip install geopandas shapely fiona pyproj ezdxf fastkml
pip install numpy trimesh matplotlib Pillow
pip install pdfplumber  # MIT alternative to PyMuPDF

# 驗證
python -c "import ifcopenshell; print(f'IfcOpenShell {ifcopenshell.version}')"
python -c "from pxr import Usd; print('OpenUSD OK')"
python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"
python -c "import pyvista; print(f'PyVista {pyvista.__version__}')"
python -c "import geopandas; print(f'GeoPandas {geopandas.__version__}')"
python -c "import anthropic; print('Anthropic SDK OK')"
```

---

## 10. 開發規範

1. **GUI:** PySide6 + Qt Designer 風格，所有 widget 繼承 QWidget
2. **3D:** PyVista mesh (pv.PolyData) 作為中間格式，同時餵給 Qt 視圖和匯出
3. **Agent:** System prompt 作為 `SYSTEM_PROMPT` 常數存在各 agent .py
4. **Builder:** 純 Python，不用 LLM，確定性輸出
5. **土地座標:** 內部統一使用公尺制本地座標系，匯入時用 pyproj 轉換
6. **IFC:** 只用 `ifcopenshell.api.run()` 高階 API
7. **USD:** 只用 `pxr.Usd`, `pxr.UsdGeom`, `pxr.UsdShade`
8. **Git:** `[P0] Init`, `[P1] Land import`, `[P2] BIM core`, etc.
9. **測試:** pytest + pytest-qt

---

*SKILL.md v3.0 | 2026-03-25 | 100% 開源 + 桌面 App + GIS 土地輸入 + IFC/USD 雙輸出*

---

## 附錄文件 (Addendum)

完整技術規格分為三份附錄文件，位於 `docs/addendum/`：

| 文件 | 內容 | 對應 Sprint |
|------|------|------------|
| `01_component_library.md` | 74 種建築零件庫 + 供應商 + 價格 | P2.5 |
| `02_sim_cost_mep.md` | 施工模擬 (4D) + 成本估算 (5D) + MEP 管線 | P6, P7, P8 |
| `03_tw_building_codes.md` | 台灣建築法規引擎 | P4.5 |

Claude Code 開發各 Sprint 前，**必須先讀取 SKILL.md + 對應的附錄文件**。
