# CHANGELOG

> 版本控制規則: [Semantic Versioning 2.0](https://semver.org/)
> 格式: `## [版本] - 日期` + Added/Changed/Fixed/Removed
> Claude Code 每完成一個 Sprint 自動更新本文件

---

## [0.8.5] - 2026-03-25

### Added (Sprint P8.5: Smart Monitoring Auto-Placement)
- `bim/monitoring/monitor_types.py` — 48 sensor/actuator type definitions
  - 8 categories: Environmental, Safety, Security, Energy, Structural, MEP, Smart, Accessibility
  - Each type has IFC class (IfcSensor/IfcActuator), predefined type, colour, unit cost
- `bim/monitoring/auto_placement.py` — Automatic placement algorithm
  - Per-space placement with circular distribution pattern
  - Per-floor and per-building placement for infrastructure sensors
  - MonitorPlan with grouping by floor, category, and type
- `bim/monitoring/rules_engine.py` — 48 placement density rules
  - 4 modes: per_sqm, per_space, per_floor, per_building
  - Min/max per space constraints, minimum area thresholds
- `bim/monitoring/ifc_monitor.py` — IFC output with IfcSensor/IfcActuator entities
  - Standalone generation and add-to-existing-file modes
  - Category-based colour coding
- `bim/monitoring/usd_monitor.py` — USD output with `monitor:` namespace attributes
  - IDTF-compatible custom attributes (type_id, category, floor, cost, etc.)
  - Sphere prims with category-coloured materials
- `bim/monitoring/dashboard_data.py` — Dashboard JSON export
  - Floor summary, category summary, type detail, full sensor list
- `gui/monitor_toggle.py` — 3D monitoring point visibility toggle
  - 8-category checkbox panel with colour coding
  - Show All / Hide All buttons with summary label
- Monitoring cost integration into 5D estimation
  - CostEstimator.estimate() accepts optional MonitorPlan
  - Per-type unit costs aggregated into "Smart Monitoring" category
- 52 new tests (440 total), xcodebuild BUILD SUCCEEDED

---

## [0.8.0] - 2026-03-25

### Added (Sprint P8: Construction Simulation / 4D BIM)
- `bim/simulation/construction_phases.py` — 16-phase construction template
  - Standard phases from site prep to MEP finish with IFC class mapping
  - Component classifier maps mesh labels to construction phases
- `bim/simulation/scheduler.py` — Construction schedule generator
  - Phase assignment from component labels, duration scaling by building size
  - Visibility state tracking (hidden/in_progress/completed) per day
- `bim/simulation/animator.py` — PyVista 4D animation engine
  - Frame rendering with semi-transparent orange for in-progress, grey for completed
  - GIF export via imageio with configurable FPS and window size
- `viz/gantt_chart.py` — Interactive Gantt chart (matplotlib)
  - Horizontal bar chart with phase colours, active phase highlight
  - Day marker line synchronized with timeline slider
  - SVG export for construction schedule documentation
- `gui/simulation_tab.py` — 4D Simulation Tab
  - Timeline slider to scrub construction days
  - Play/pause button with auto-advance timer
  - Gantt chart panel synchronized with 3D view
  - GIF export button with file dialog
- Integrated 4D simulation tab into MainWindow
- ModelView gains `set_simulation_frame()` for 4D rendering
- 50 new tests (388 total), xcodebuild BUILD SUCCEEDED

### Dependencies
- Added `imageio` for GIF animation export

---

## [0.7.0] - 2026-03-25

### Added (Sprint P7: MEP Auto Routing)
- `bim/mep/pathfinder.py` — 3D orthogonal A* pathfinding engine
  - Grid-based voxelisation, turn penalty, collinear path simplification
  - Obstacle generation from wall/slab bounding boxes
- `bim/mep/systems.py` — MEP system definition templates
  - Office + residential templates for HVAC, plumbing, electrical, fire protection
  - Ceiling layer Z-offset allocation, system colours, labels
- `bim/mep/planner.py` — Deterministic MEP planner (no LLM)
  - Equipment positioning (risers, panels, AHU connections)
  - Terminal distribution (sprinkler heads, grilles, outlets, plumbing fixtures)
  - A* route planning from equipment to terminals per floor
- `bim/mep/ifc_mep.py` — IFC MEP output
  - IfcPipeSegment (plumbing, fire), IfcDuctSegment (HVAC), IfcCableCarrierSegment (electrical)
  - Per-system material colours, storey assignment
- `bim/mep/usd_mep.py` — USD MEP output
  - Cube-based segment geometry with PBR materials
  - Per-system Xform hierarchy under /MEP
- `bim/mep/clash_detect.py` — AABB-based cross-system clash detection
  - ClashReport with overlap point, severity, system pair counts
- `viz/mep_overlay.py` — Four-colour PyVista tube mesh overlay
  - Blue (plumbing), Red (electrical), Green (HVAC), Yellow (fire protection)
- `gui/mep_toggle.py` — MEP system show/hide toggle panel
  - Per-system QCheckBox with colour coding, Show All / Hide All buttons
- 45 new tests (338 total), xcodebuild BUILD SUCCEEDED

---

## [0.6.0] - 2026-03-25

### Added (Sprint P6: Cost Estimation / 5D BIM)
- `bim/cost/qto.py` — Quantity Take-Off engine
  - Extracts wall area, slab area, roof area, openings, MEP allowance, site work from BuildingPlan
  - Shoelace polygon area calculation, per-story breakdown
- `bim/cost/unit_prices_tw.py` — Taiwan construction unit price table
  - 22 price entries across 8 categories (structure, envelope, interior, doors/windows, MEP, equipment, roof, site)
  - TWD pricing for 2025-2026 market reference
- `bim/cost/estimator.py` — Cost estimation engine
  - Maps QTO items to unit prices, adds interior finish allowances (ceiling + floor tile)
  - Produces CostEstimate with line items, category breakdown, cost-per-sqm
  - JSON-serializable `to_dict()` output
- `viz/cost_charts.py` — Cost visualization
  - CostPieChart — matplotlib pie chart with percentage labels
  - CostBarChart — horizontal bar chart with NT$ million labels
- `gui/cost_panel.py` — Cost estimation GUI panel
  - Summary header (total, floor area, cost/sqm)
  - Tabbed view: Pie Chart / Bar Chart / Detail Table
  - Auto-estimates on building plan generation
- Integrated into MainWindow — "Cost (5D)" tab auto-populates after building generation
- Status bar shows cost total alongside BCR/FAR
- 28 new tests (293 total), xcodebuild BUILD SUCCEEDED

---

## [0.5.0] - 2026-03-25

### Added (Sprint P5: Voice Input + Export)
- `voice/stt.py` — Speech-to-text engine
  - faster-whisper local transcription (auto-detect language)
  - AudioRecorder via sounddevice (16kHz 16-bit PCM)
  - VoiceInput high-level API with async callback support
  - Graceful fallback when faster-whisper/sounddevice unavailable
- Voice button in Chat panel — toggle recording with visual feedback
- `viz/floorplan.py` — Per-floor SVG plan generation
  - Walls (exterior/interior), spaces with labels, openings (door/window)
  - Compass indicator, auto-scaling, Y-flip for standard 2D view
  - `generate_floorplans()` file output + `generate_floorplan_svg_strings()` in-memory
- `gui/dialogs/export_dialog.py` — One-click export dialog
  - IFC + USD + SVG floor plans + JSON plan + Compliance report
  - Background thread export with progress bar
  - Copy existing files or regenerate from plan
- Export button in Chat panel (enabled after generation)
- 30 new tests (265 total)

---

## [0.4.8] - 2026-03-25

### Added (Sprint P4.8: Interactive Modification Engine)
- `agents/modifier.py` — Modifier Agent (Agent 5)
  - Claude-powered intent parsing (stories/height/footprint/roof/rooms/materials/openings)
  - Keyword-based fallback parser for offline (Chinese + English)
  - Deterministic plan modification with zoning constraint enforcement
  - Version history with full undo capability
- `schemas/modification.py` — Modification data models
  - ModificationType enum (8 types), ImpactLevel enum (4 levels)
  - ModificationIntent, ModificationRecord, ModificationHistory, ImpactItem
- Impact propagation matrix — 8 modification types × affected components
  - `compute_impacts()` compares old/new plans to generate diff report
- Incremental recalculation — `_recalculate_metrics()` updates BCR/FAR from geometry
- `gui/modification_panel.py` — Impact summary panel
  - Color-coded impact table (high=red, medium=orange, low=green)
  - Undo button + history count display
- Integrated into Orchestrator — `modify()` and `undo()` methods
- ChatPanel auto-detects modification vs generation commands
- 24 new modifier tests (235 total), xcodebuild BUILD SUCCEEDED

---

## [0.4.0] - 2026-03-25

### Added (Sprint P4.5: Taiwan Building Code Engine)
- `codes/base.py` — BaseRule abstract class + CheckResult + Severity enum
- `codes/tw_building_code.py` — 8 rules: BCR, FAR, height limit, stairs, corridors, ceiling height, elevators, parking
- `codes/tw_seismic_code.py` — Seismic zone table (20 cities) + structural estimation (column size, shear wall)
- `codes/tw_fire_code.py` — 5 rules: fire construction, compartment, egress distance, two stairs, safety stair
- `codes/tw_accessibility_code.py` — Accessibility facilities check (ramp, elevator, toilet, parking, path)
- `codes/tw_zoning_data.py` — BCR/FAR lookup for 6 major cities + non-urban land + generic fallback
- `codes/registry.py` — 15 rules registered, batch check + compliance summary
- `codes/report.py` — JSON report + human-readable text table generation

### Changed
- `agents/checker.py` — Now uses Taiwan building code engine for deterministic checks (15+ rules)
  - Code results include rule_id, law_reference, severity, suggestion
  - Compliance summary + report text included in CheckResult
- `agents/planner.py` — Injects Taiwan building code constraints into Planner prompt
  - Volume limits, evacuation safety, equipment requirements, seismic, accessibility
- `agents/orchestrator.py` — Passes compliance report through to GenerationResult
- `schemas/result.py` — Added compliance_report + compliance_text fields
- 47 new code engine tests (211 total), xcodebuild BUILD SUCCEEDED

---

## [0.3.0] - 2026-03-25

### Added (Sprint P4: AI Agent Pipeline)
- `agents/base.py` — BaseAgent Claude API wrapper with JSON extraction
  - Lazy Anthropic client init, structured AgentResponse, markdown/brace JSON parsing
- `agents/enhancer.py` — Agent 1: requirement enhancement
  - Enriches raw user prompts into structured BuildingRequirement with land/zoning context
  - Respects FAR/height limits, falls back to basic requirement on API failure
- `agents/planner.py` — Agent 2: building planner (key agent)
  - Generates BuildingPlan JSON placing building on real land parcel
  - Deterministic fallback box generator for offline/error scenarios
  - BCR/FAR/height compliance built into fallback logic
- `agents/builder.py` — Agent 3: BIM builder (pure Python, no LLM)
  - Converts BuildingPlan → IFC + USD dual output via existing generators
- `agents/checker.py` — Agent 4: rule checker
  - Deterministic checks: BCR, FAR, height, setback containment, min story height
  - Claude-powered fix suggestions when violations found
- `agents/orchestrator.py` — Pipeline orchestrator
  - Chains Enhancer → Planner → Builder → Checker with iterative correction
  - Status callbacks for GUI progress updates
- `gui/chat_panel.py` — Chat UI panel with threaded pipeline execution
  - Message history, progress bar, background QThread worker
  - Signals: plan_ready, generation_finished for GUI integration
- `gui/main_window.py` — Integrated ChatPanel replacing inline chat widgets
- 37 new agent tests (164 total), xcodebuild BUILD SUCCEEDED

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
| 0.4.8 | P4.8 完成 | 互動式修改引擎 |
| 0.5.0 | P5 完成 | 語音 + 匯出 |
| 0.6.0 | P6 完成 | 成本估算 (5D) |
| 0.6.0 | P7 完成 | MEP 管線 |
| 0.7.0 | P8 完成 | 施工模擬 |
| 1.0.0 | 全部完成 | POC 完整版 |
