# CHANGELOG

> 版本控制規則: [Semantic Versioning 2.0](https://semver.org/)
> 格式: `## [版本] - 日期` + Added/Changed/Fixed/Removed
> Claude Code 每完成一個 Sprint 自動更新本文件

---

## [Unreleased]

### 規劃中
- P4~P8.5 完整開發計劃（詳見 TODO.md）

---

## [0.2.6] - 2026-03-25

### Added (Sprint P3: 3D 互動預覽)
- `viz/model_3d.py` — BuildingPlan → PyVista mesh assembly
  - `build_model()` — full building with ground slab, walls, floor slabs, roof
  - `build_model_by_floor()` — grouped by floor name for section switching
  - `clip_model_at_elevation()` — section cut at any Z elevation
  - `story_meshes()` — per-story wall + slab mesh generation
  - Material color mapping from `bim/materials.py` to hex colors
- `gui/model_view.py` — pyvistaqt QtInteractor embedded in PySide6
  - Floor section switching via combo box (All Floors / per-floor / section cut)
  - `set_plan()` API for loading BuildingPlan from other GUI components
- `viz/site_plan.py` — 2D matplotlib site plan (land + building footprint overlay)
  - Land boundary, buildable area, building footprint, per-story outlines
  - BCR/FAR annotation on building footprint
- `gui/main_window.py` — integrated 3D Model tab + Site Plan tab
  - `set_building_plan()` method for programmatic building display
- 19 new tests (127 total), xcodebuild BUILD SUCCEEDED

---

## [0.2.5] - 2026-03-25

### Fixed (Pre-Task: P2 Code Review 修復)
- `bim/geometry.py` — Replace fan triangulation with mapbox-earcut for concave polygon support (L/T-shaped footprints)
- `bim/ifc_generator.py` — Read slab thickness from `StoryPlan.slab_thickness_m` instead of hardcoded 0.2
- `bim/usd_generator.py` — Add per-face normals to USD mesh prims for Omniverse/Reality Composer compatibility
- `bim/ifc_generator.py` — Remove unused `OpeningDef` import
- `bim/materials.py` — Remove unused `field` import, fix Glass IFC style from MIRROR to GLASS
- Added edge case tests: empty plan, zero-length wall, concave slab, USD round-trip + normals

### Added (Sprint P2.5: 建築零件庫)
- `bim/components/base.py` — ComponentDef, SupplierInfo, PriceRange, ComponentCategory Pydantic models
- `bim/components/registry.py` — ComponentRegistry with search, get, list_by_category, register_many
- 76 building component definitions across 8 categories:
  - Structural (12): foundations, columns, beams, slabs, rebar, shear walls
  - Envelope (10): exterior walls, curtain wall, roofs, parapet, canopy
  - Interior (6): partitions, ceiling, raised floor, railings
  - Openings (10): doors (6 types), windows (3 types), skylight
  - Vertical Transport (12): elevators (3), escalators (2), walkway, stairs (4), ramps (2)
  - MEP (11): HVAC, ducts, pipes, sprinklers, lights, electrical
  - Fixtures (9): toilets, sinks, bathtub, shower, kitchen
  - Site (6): parking, fence, trees, pavement
- Taiwan market supplier/price seed data (7 elevator brands, 4 escalator brands, structural materials)
- `bim/components/load_all.py` — Auto-registration of all components
- 18 new component tests (108 total), xcodebuild BUILD SUCCEEDED

---

## [0.2.0] - 2026-03-25

### Added (Sprint P2: IFC + USD 生成核心)
- `bim/geometry.py` — wall/slab/roof mesh generation (wall_mesh, slab_mesh, flat_roof_mesh, gable_roof_mesh)
- `bim/ifc_generator.py` — IfcOpenShell high-level wrapper (IFCGenerator class)
  - Walls with placement/rotation, slabs with polyline profile, roof, materials
  - Only uses `ifcopenshell.api.run()` — no low-level entity manipulation
- `bim/usd_generator.py` — OpenUSD wrapper (USDGenerator class)
  - Triangle mesh generation, Z-up, metres-per-unit, PBR materials via UsdPreviewSurface
- `bim/materials.py` — 9 built-in materials with dual IFC surface style + USD PBR mapping
- `examples/01_simple_box.py` — Single-storey 10x8m box → .ifc + .usda
- `examples/02_l_shaped_office.py` — 2-storey L-shaped office → .ifc + .usda
- 34 new BIM tests (82 total), xcodebuild BUILD SUCCEEDED

---

## [0.1.1] - 2026-03-25

### Added (Sprint P1: 土地匯入 + 2D 視圖)
- Land parsers: GeoJSON, Shapefile, DXF, Manual coordinate input
  - `land/parsers/geojson.py` — FeatureCollection/Feature/bare Polygon support
  - `land/parsers/shapefile.py` — fiona-based Shapefile reader
  - `land/parsers/dxf.py` — ezdxf LWPOLYLINE/POLYLINE extraction
  - `land/parsers/manual.py` — manual coordinate entry with validation
- `land/setback.py` — uniform + per-side setback calculation (shapely buffer)
- `land/projection.py` — WGS84 ↔ TWD97 (EPSG:3826) coordinate projection (pyproj)
- `gui/map_view.py` — matplotlib FigureCanvas embedded in Qt for 2D parcel display
- `gui/land_panel.py` — land info + zoning rules display panel
- `gui/dialogs/import_land.py` — file picker + drag-and-drop import dialog
- `gui/main_window.py` — integrated land import, map view, and info panel
- Test fixture: `tests/fixtures/sample_parcel.geojson`
- 19 new land tests (48 total), xcodebuild BUILD SUCCEEDED
- Conda env `promptbim` (Python 3.11) with all GIS dependencies

---

## [0.1.0] - 2026-03-25

### Added (Sprint P0: 專案骨架 + Xcode + 環境)
- Xcode 專案 (`PromptBIMTestApp1.xcodeproj`) — macOS SwiftUI app target
  - `PromptBIMTestApp1App.swift` — App entry point
  - `ContentView.swift` — 主介面骨架 (HSplitView + TabView + Chat panel)
  - `PythonBridge.swift` — Process() 呼叫 Python 後端
  - `Info.plist`, `Assets.xcassets`, `Entitlements`
  - Build Phase Script: Python 環境檢查
- Python 專案骨架
  - `src/promptbim/__main__.py` — CLI (`--version`, `gui`, `generate`)
  - `src/promptbim/config.py` — Pydantic BaseSettings
  - `src/promptbim/gui/main_window.py` — PySide6 空白主視窗
  - `src/promptbim/schemas/` — LandParcel, ZoningRules, BuildingPlan, BuildingRequirement, GenerationResult
- 測試: 29 pytest tests 全部通過
- xcodebuild BUILD SUCCEEDED

---

## [0.0.1] - 2026-03-25

### Added
- 初始化 GitHub repo `chchlin1018/PromptBIMTestApp1`
- README.md 中文專案介紹
- TODO.md 開發計劃追蹤（P0~P8 共 11 個 Sprint）
- SKILL.md Claude Code 知識庫 (SSOT)
- CHANGELOG.md 版本變更記錄
- LICENSE (MIT)
- .gitignore / .env.example
- `docs/addendum/` 四份技術規格文件
  - 建築零件庫（74 種零件 + 供應商價格）
  - 施工模擬 + 成本估算 + MEP 管線
  - 台灣建築法規引擎（建築技術規則 + 耐震 + 防火 + 無障礙）
- `reference/` 參考資料
  - GeoJSON 土地範例
  - IFC ↔ USD 映射表
  - 測試 prompt 集
- `examples/` 範例目錄骨架

---

## 版本對照表

| 版本 | 對應 Sprint | 里程碑 |
|------|-----------|--------|
| 0.0.1 | — | 文件初始化 |
| 0.1.0 | P0 完成 | 專案骨架可執行 |
| 0.2.0 | P1+P2 完成 | 土地匯入 + BIM 核心 |
| 0.2.5 | P2.5 完成 | 建築零件庫 (76 種) |
| 0.3.0 | P3+P4 完成 | AI Agent + 3D 預覽 |
| 0.4.0 | P4.5 完成 | 法規引擎 |
| 0.5.0 | P5+P6 完成 | 語音 + 成本估算 |
| 0.6.0 | P7 完成 | MEP 管線 |
| 0.7.0 | P8 完成 | 施工模擬 |
| 1.0.0 | 全部完成 | POC 完整版 |
