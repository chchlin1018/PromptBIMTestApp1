# CHANGELOG

> 版本控制規則: [Semantic Versioning 2.0](https://semver.org/)
> 格式: `## [版本] - 日期` + Added/Changed/Fixed/Removed
> Claude Code 每完成一個 Sprint 自動更新本文件

---

## [2.5.0] - 2026-03-26

### Added (Sprint P18: V2 Migration Phase 0-1 — C++ Core Library Bootstrap)

#### libpromptbim/ — C++ Core Library Skeleton (Phase 0)
- `libpromptbim/CMakeLists.txt` — CMake 4.x project, C++17, FetchContent for deps
- `libpromptbim/vcpkg.json` — vcpkg manifest (nlohmann-json, gtest, future: gdal/geos)
- `libpromptbim/include/promptbim/promptbim.h` — Stable C ABI public header (all engines)
- `libpromptbim/include/promptbim/compliance_engine.hpp` — C++ compliance engine interface
- `libpromptbim/include/promptbim/cost_engine.hpp` — C++ cost engine interface
- `.github/workflows/ci.yml` — Added `cpp-tests` CI matrix job (macOS-14 + ubuntu-22.04)

#### Compliance Engine C++ (Phase 1)
- `libpromptbim/src/compliance/compliance_engine.cpp` — 15 Taiwan building code rules in C++17
  - BCR (Art.25), FAR (Art.161), Height (Art.24-1), Stairs (Art.33), Corridor (Art.92)
  - CeilingHeight (Art.26), Elevator (Art.55-1), Parking
  - FireConstruction, FireCompartment, FireEscape, TwoStairs, SafetyStair
  - Seismic Design, Accessibility
- Shoelace polygon area formula, JSON parse/emit via nlohmann/json
- C ABI: `pb_check_compliance()`, `pb_version()`, `pb_free_string()`

#### Cost Engine C++ (Phase 1)
- `libpromptbim/src/cost/cost_engine.cpp` — QTO + unit prices + breakdown in C++17
  - 13 price categories (structure, envelope, interior, MEP, door/window, roof, site)
  - Interior finish allowance (ceiling + floor tile per slab)
  - C ABI: `pb_estimate_cost()`

#### pybind11 Bindings (Phase 1)
- `libpromptbim/bindings/python/bindings.cpp` — pybind11 module `_native`
  - `ComplianceEngine`, `CostEngine` classes + `check_compliance()`, `estimate_cost()` free fns
- `src/promptbim/codes/_native_bridge.py` — Auto-select native C++ vs Python fallback

#### GoogleTest Suite (24 tests)
- `libpromptbim/tests/test_compliance_engine.cpp` — 10 compliance + 2 C ABI tests
- `libpromptbim/tests/test_cost_engine.cpp` — 8 cost + 2 C ABI tests
- `libpromptbim/tests/test_version.cpp` — 4 basic sanity tests

#### Python Consistency Tests (+21 tests)
- `tests/test_cpp_consistency.py` — 21 tests verifying C++ matches Python behavior
  - 9 compliance consistency tests (BCR/FAR values, rule structure, fail scenarios)
  - 8 cost consistency tests (floor area, ratios, ranges)
  - 3 native bridge integration tests

#### Test Count
- Python: 799 → 820 passed (+21 C++ consistency tests)
- GoogleTest: 24/24 passed ✅

---

## [2.4.1] - 2026-03-26

### Fixed (Sprint P17.1: 審計修復 + 文檔一致性)

#### 文檔修復
- `PROMPT_P18.md` — 修正測試數 776→792，CLAUDE.md 版本 v1.9.0→v1.13.0
- `PROMPT_P18.md` — 加入啟動通知步驟（⚠️ 第一步）
- `PROMPT_P18.md` — 加入 Part A / Part B 完成通知模板
- `docs/PromptBIM_Context_Prompt.md` — 同步 P17 測試數 776→792
- `docs/PromptBIM_Context_Prompt.md` — 更新 CLAUDE.md 版本至 v1.13.0

#### 版本同步
- `pyproject.toml` — Version bumped to 2.4.1
- `__init__.py` — Fallback version updated to 2.4.1

---

## [2.4.0] - 2026-03-26

### Added (Sprint P17: Final Polish + Architecture Hardening + CI Fix)

#### CI/CD
- `requirements-frozen.txt` — 清理 `@ file://` 本地路徑，確保跨機器可重現
- `.github/workflows/ci.yml` — pip-audit 真實 CVE 標記（移除假忽略項）

#### 架構改善
- `agents/orchestrator.py` — Lazy Import 優化，減少啟動時間
- Plugin 架構基礎: `PluginRegistry` + `@register_plugin` 裝飾器

#### 退縮計算重構
- `per_side_setback()` + `uniform_setback()` 重構
- 超過 4 邊多邊形自動 fallback 至 uniform_setback

#### API Rate Limiter
- Token bucket 演算法 (50 RPM default)
- 整合至 `BaseAgent`，所有 Agent 自動限速

#### Schema 版本控制
- `schema_version` 欄位加入所有核心 Schema
- 相容性檢查機制（載入時驗證版本）

#### 輸入大小限制
- `MAX_LAND_FILE_SIZE_MB = 50` 常數
- 所有 Land 解析器加入檔案大小檢查

#### ComponentRegistry 效能
- `_by_category` 倒排索引，查詢效能提升

#### PythonBridge 改善
- Intel Mac 路徑支援
- `which python3` fallback 機制
- `PROMPTBIM_PYTHON` 環境變數覆蓋

#### ContentView
- 版本號動態顯示 (`bridge.version`)

#### Async/Await
- `BaseAgent.arun()` 非同步執行方法
- `Orchestrator.agenerate()` 非同步生成
- 各 Agent 加入 async 方法

#### Plan 快取
- SHA-256 cache key 計算
- JSON file store 本地快取
- LRU eviction + TTL 7 天過期策略

#### CLI 快取管理
- `cache list` / `cache clear` / `cache stats` 子命令
- `--no-cache` / `--clear-cache` 旗標

#### 測試
- +51 新測試 (network failure, fuzzing, permissions, async, cache)

#### 文件
- `V2_Migration_Tasks.md` 遷移指南
- P14/P16 品質分析報告歸檔

### Changed
- `pyproject.toml` — Version bumped to 2.4.0
- `__init__.py` — Fallback version updated to 2.4.0

### Dependencies
- Added `lxml>=5.0`
- Added `pip-tools>=7.0`

### Stats
- Tests: 776 passed (+51 new)
- xcodebuild: BUILD SUCCEEDED
- ruff check: All checks passed
- git tag: v2.4.0

---

## [2.1.0] - 2026-03-26

### Fixed (Sprint P16: Comprehensive Quality Remediation)

#### Critical (C-1 ~ C-3)
- `agents/base.py` — API retry with exponential backoff (tenacity, max 3 attempts, 5xx only)
- `agents/base.py` — API call timeout (default 30s, configurable via `api_timeout_seconds`)
- Unified Shoelace area calculation — removed 6 duplicate `_shoelace_area` / `_polygon_area` functions, all now use `bim.geometry.poly_area()`

#### High (H-1 ~ H-5)
- `agents/planner.py` — `buildable_area` input validation (>= 3 vertices, area > 0)
- `bim/components/registry.py` — `reset()` class method + autouse conftest fixture for test isolation
- `schemas/modification.py` — `save_history()` / `load_history()` JSON persistence for ModificationHistory
- `agents/planner.py` — Required field validation before Pydantic parse (stories, building_footprint)
- `schemas/modification.py` — `snapshot_from_plan()` for precision-safe plan snapshots via `model_dump()`

#### Medium (M-1, M-3, M-5, M-6)
- `constants.py` — Extracted magic numbers: `DEFAULT_STORY_HEIGHT_M`, `DEFAULT_WALL_THICKNESS_M`, `API_MAX_TOKENS_*`, etc.
- `agents/builder.py` — File backup before overwrite (.bak, keeps 1 backup)
- `ContentView.swift` — Version display updated to v2.1.0, removed unused `showSetupHelp` state variable
- `.github/workflows/ci.yml` — Removed `|| true` from pip-audit, removed invalid `--ignore-vuln PYSEC-0`

### Added
- `src/promptbim/constants.py` — Project-wide named constants
- `tenacity>=8.0` in pyproject.toml dependencies
- `config.py` — `api_timeout_seconds` setting (default 30.0)
- `tests/test_quality_remediation.py` — 20 new tests for all remediation items
- `tests/test_agents/test_base_retry.py` — 7 tests for retry + timeout behaviour

### Changed
- `pyproject.toml` — Version bumped to 2.1.0
- `__init__.py` — Fallback version updated to 2.1.0

### Stats
- Tests: 725 passed (20 new)
- xcodebuild: BUILD SUCCEEDED
- ruff check: All checks passed
- git tag: v2.1.0

---

## [2.0.0] - 2026-03-26

### Added (Sprint P14: CI/CD + Security + Documentation v2.0)

#### CI/CD
- `.github/workflows/ci.yml` — GitHub Actions CI pipeline
  - macOS 14 runner with conda + Python 3.11
  - Ruff lint, pytest with coverage (>70%), xcodebuild
  - Security audit job with pip-audit
- `.github/dependabot.yml` — Automated dependency updates (pip + GitHub Actions)
- `requirements-frozen.txt` — Frozen dependency versions for reproducible builds

#### Security
- `config.py` — `validate_api_key()` function checks `sk-ant-` prefix format
- `config.py` — `.env` file permission check (warns if group/other readable)
- `PythonBridge.swift` — `loadDotEnv()` POSIX permission check with warning
- CLI epilog shows API key security best practices

#### Documentation
- `README.md` — Complete v2.0 rewrite: CLI usage, architecture diagram, full feature list, dev guide
- `docs/API.md` — Full API documentation: Orchestrator, Agents, Parsers, BIM generators, MCP Server
- `SKILL.md` — Updated to v3.1: P11-P14 features, CLI examples, PDF OCR flow, CI/CD flow

#### Code Quality
- `pyproject.toml` — Full ruff lint config (select + ignore rules), coverage config
- Ruff auto-fix: 274 issues fixed (unused imports, import sorting, format)
- `ruff format` applied to all 215 Python files
- `src/promptbim/py.typed` — PEP 561 type stub marker
- `src/promptbim/__init__.py` — Added `__all__` exports
- `pip-audit` added to dev dependencies

### Changed
- `pyproject.toml` — Version bumped to 2.0.0
- `__init__.py` — Fallback version updated to 2.0.0

### Stats
- Tests: 705+ passed
- xcodebuild: BUILD SUCCEEDED
- ruff check: All checks passed
- git tag: v2.0.0

---

## [1.5.0] - 2026-03-26

### Fixed (Sprint P13: CLI + Dependencies + PDF OCR)

#### Dependency Fixes
- **pyproject.toml** — Bumped version to 1.5.0; added `pydantic-settings>=2.0` and `imageio>=2.30` as core deps
- **pyproject.toml** — Removed unused `rich>=13.0` dependency
- **pyproject.toml** — Fixed optional deps: `web` now uses `streamlit` (not fastapi), `voice` adds `sounddevice`, `pdf` adds `PyMuPDF`
- **config.py** — Removed unused `f3d_path` setting
- **`__init__.py`** — Version now uses `importlib.metadata` for single-source-of-truth versioning

### Added

#### `generate` CLI Command (fully functional)
- `python -m promptbim generate "3-story villa" -o ./output` — runs full pipeline from CLI
- `--land` option for GeoJSON/SHP/DXF/KML land files, defaults to 30x30m parcel
- `--format` (ifc/usd/both), `--city`, `--template` options
- `_load_land_file()` auto-detects format by extension
- `_cli_status()` prints pipeline progress to console
- Outputs `result.json` with building summary

#### PDF Cadastral Document Parser
- `land/parsers/pdf_ocr.py` — `PDFLandParser` class with full extraction pipeline:
  - Text extraction via pdfplumber (area, lot number, address)
  - Table coordinate extraction
  - Image extraction via PyMuPDF + Claude Vision AI boundary recognition
  - Cadastral keyword detection (Chinese + English)
  - Square approximation fallback when only area is available
- GUI `import_land.py` — New "PDF (OCR)" tab with drag-and-drop support
- `Info.plist` — Added PDF document type, CFBundleVersion bumped to 13

#### Test Infrastructure
- `tests/conftest.py` — Shared fixtures: `sample_land`, `sample_plan`, `sample_zoning`, `tmp_output`
- `tests/test_cli.py` — CLI tests: version, generate, check, help (15 tests)
- `tests/test_land/test_pdf_ocr.py` — PDF parser tests (13 tests)
- pytest markers: added `slow: tests taking > 10 seconds` marker

### Changed
- `bim/geometry.py` — Added `poly_area()` as canonical shoelace implementation
- `agents/orchestrator.py` — Uses `poly_area` from geometry; added Builder failure recovery (saves `plan_partial.json`); wrapped modify in try/except
- `agents/modifier.py` — Uses `poly_area` from geometry (alias `_poly_area` kept for backward compat)
- `gui/dialogs/import_land.py` — Separated `PDF_EXTENSIONS` from `IMAGE_EXTENSIONS`; added KML support to `_parse_file`

### Stats
- Tests: 705 passed (from 675)
- xcodebuild: BUILD SUCCEEDED
- git tag: v1.5.0

---

## [1.4.0] - 2026-03-26

### Fixed (Sprint P12: Quality Fixes + Performance + Demo Prep)

#### Critical Fixes
- **C1: PythonBridge dual instance** — App now holds single `@StateObject` bridge, injected via `.environmentObject()` to ContentView
- **C2: App close not terminating Python Process** — Added `AppDelegate` with `applicationWillTerminate` calling `bridge.terminateGUI()`
- **C3: NSSupportsSuddenTermination conflict** — Set both `NSSupportsAutomaticTermination` and `NSSupportsSuddenTermination` to false in Info.plist; managed programmatically in PythonBridge

#### Medium Fixes
- **M1: MacBook lowercase path** — Added `~/documents/myprojects/` to search paths in both `config.py` and `PythonBridge.swift`
- **M5+L4: process.launch() deprecation + variable name conflict** — Renamed shadowing `pythonPath` to `srcPath` in `launchPySide6GUI()`

### Added
- `docs/DEMO_SCRIPT.md` — 8-scene demo video script with narration, steps, and expected screens
- `tests/test_integration/test_smoke.py` — Non-mock smoke tests (CLI version, health check, core imports)
- Performance benchmarks with `@pytest.mark.benchmark`: IFC < 3s, USD < 3s, cost < 1s, compliance < 1s, full pipeline < 5s
- pytest markers: `integration`, `api`, `benchmark` in `pyproject.toml`
- Debug log in `PythonBridge.init()` to verify single-instance creation

### Changed
- `PromptBIMTestApp1App.swift` — Added `@NSApplicationDelegateAdaptor`, `environmentObject` injection
- `ContentView.swift` — Changed from `@StateObject` to `@EnvironmentObject`
- `Info.plist` — CFBundleVersion bumped to 12, SuddenTermination disabled
- Performance test thresholds tightened (IFC 10s→3s, USD 10s→3s, compliance 2s→1s)

### Stats
- Tests: 675 passed (from 668)
- xcodebuild: BUILD SUCCEEDED
- git tag: v1.4.0

---

## [1.3.0] - 2026-03-26

### Added (Sprint P11: Xcode ↔ PySide6 GUI Integration + E2E)

- `PythonBridge.swift` — Full rewrite: auto-detect conda Python, .env loading, PySide6 GUI launch/terminate, project root discovery
- `ContentView.swift` — Splash screen with Python environment status, setup instructions for missing env, restart button
- `PromptBIMTestApp1App.swift` — App lifecycle management
- `config.py` — Multi-path .env search: cwd → src root → well-known path → env var override
- `chat_panel.py` — No-land fallback: auto-creates 30×30m default parcel when no land is loaded
- `Info.plist` — Registered document types: geojson, shp, dxf, kml, jpg, png, tiff with UTI
- `tests/test_e2e_integration.py` — 23 E2E integration tests covering 6 flow categories:
  - Test 1: No-land + Prompt → IFC + USD generation
  - Test 2: GeoJSON land + Prompt → full pipeline
  - Test 3: Image AI recognition (mocked Vision API) → boundary confirm
  - Test 4: Generate → Modify → Undo version history
  - Test 5: Compliance + Cost + MEP + Monitoring
  - Test 6: Export all formats (IFC + USD + USDZ + SVG + JSON + 4D schedule)
- CURRENT_PROJECT_VERSION bumped to 11

### Changed

- Window default size reduced to 800×500 (splash screen optimized)
- CFBundleShortVersionString updated to 1.0.0, CFBundleVersion to 11

---

## [1.2.0] - 2026-03-25

### Added (Sprint P10.3: Startup Health Check + AI Validation)

- `startup/health_check.py` — HealthChecker engine running 12 checks across 4 categories
  - Python environment: version >= 3.11, conda env active
  - Core dependencies: ifcopenshell, pxr, PySide6, anthropic, shapely+pyproj, pyvista+pyvistaqt
  - AI services: API key validation, Claude API ping test, model availability
  - Filesystem: .env exists, output/ writable
- `startup/ai_check.py` — Claude AI connection validation with timeout, error classification, response timing
- `startup/auto_fix.py` — Auto-fix suggestion engine with fix commands for all dependency checks
- `gui/startup_check_view.py` — GUI startup health check dialog with real-time updates, progress bar, category grouping
- CLI `check` subcommand: `python -m promptbim check [--json] [--ai] [--fix]`
- Config settings: `startup_check_enabled`, `startup_check_skip_ai`, `ai_ping_timeout_seconds`, `ai_model`
- 42 new tests for health check, AI check, auto-fix, and CLI

---

## [1.1.0] - 2026-03-25

### Added (Sprint P10.2: Debug Logging System)

- `debug.py` — Unified debug logging system for the entire project
  - `get_logger(module_name)` — Module-specific colored console loggers
  - `enable_debug()` / `disable_debug()` — Runtime debug mode toggle
  - `setup_file_logging()` — Optional file-based log output
  - ANSI color coding by module category (land=green, bim=blue, agents=magenta, etc.)
- Debug mode activation via 3 methods:
  - CLI: `python -m promptbim gui --debug`
  - Environment variable: `PROMPTBIM_DEBUG=1`
  - .env file: `PROMPTBIM_DEBUG=1`
- Debug logging added to all 50+ modules across the project:
  - Land parsers: file paths, feature counts, coordinate ranges
  - BIM generators: entity counts, file sizes, generation times
  - Cost engine: QTO items, line items, category breakdowns
  - MEP planner: grid sizes, A* iterations, route lengths, clash detection
  - AI agents: API requests/responses, token counts, response times, JSON parsing
  - Code engine: rule pass/fail stats, input values, compliance rates
  - GUI: window init, tab switches, user interactions
  - Voice/MCP/Web: session events, tool calls, generation requests
- `config.py` — Added `debug_mode: bool` setting
- `__main__.py` — Added `--debug` CLI flag for all subcommands
- `tests/test_debug.py` — 12 tests covering logger creation, mode toggle, env vars, production mode

---

## [1.0.0] - 2026-03-25

### Added (Sprint P10: Polish + Remaining Backlog)

#### KML Import + Satellite Basemap
- `land/parsers/kml.py` — KML/KMZ parser using fastkml
  - Supports .kml and .kmz (ZIP-wrapped) files
  - Recursive Placemark extraction (handles nested Folders/Documents)
  - pygeoif → shapely geometry conversion
- `viz/basemap.py` — Satellite basemap overlay for 2D map view
  - OpenStreetMap + Esri Satellite tile providers
  - contextily integration with placeholder fallback
  - `gui/map_view.py` — Added basemap style toggle

#### Multiple Building Templates
- `bim/templates/school.py` — School building template
  - Central corridor with classrooms on both sides
  - Configurable stories, office/library on ground floor
- `bim/templates/hospital.py` — Hospital building template
  - H-shaped layout with ER, wards, radiology
  - Configurable 1-20+ stories
- `bim/templates/factory.py` — Factory building template
  - Large production hall (70%) + office wing (30%)
  - Gable roof, roller door, optional 2nd floor
- `bim/templates/__init__.py` — Template registry with `generate_from_template()`

#### NVIDIA Omniverse Connection
- `bim/omniverse.py` — OmniverseConnector
  - omni.client integration (when available)
  - HTTP fallback for Nucleus server connectivity
  - Upload, list, and test connection operations

#### End-to-End Integration Tests
- `tests/test_integration/test_e2e_pipeline.py` — 13 E2E tests
  - template → IFC → USD → USDZ → compliance → cost → MEP → simulation → monitoring
  - KML import → LandParcel roundtrip
  - BuildingPlan JSON serialization roundtrip

#### Performance & Edge Cases
- `tests/test_integration/test_performance.py` — Performance benchmarks + edge case tests
  - Template generation, IFC/USD generation, compliance check speed limits
  - Very small land, 20-story buildings, irregular shapes, empty buildable area

### Stats
- Tests: 591 passed (from 516)
- xcodebuild: BUILD SUCCEEDED

---

## [0.9.0] - 2026-03-25

### Added (Sprint P9: AI Land Image Recognition + Backlog)

#### Part A: AI Land Image Recognition
- `land/parsers/image_preprocess.py` — Image preprocessing pipeline
  - PIL-based normalization (resize, contrast enhancement)
  - HEIC → JPG conversion (via pillow-heif)
  - PDF first page → PNG conversion (via PyMuPDF or pdfplumber)
  - Base64 encoding for Claude Vision API
  - Supports JPG, PNG, TIFF, BMP, WebP, HEIC, PDF
- `land/parsers/image_ai.py` — AI image recognition parser
  - Integrates LandReaderAgent with image preprocessing
  - AIRecognitionResult with parcels, confidence, and raw data
  - build_parcel_from_ai_data() for constructing LandParcel from AI JSON
- `agents/land_reader.py` — Land Reader Agent (new Agent 6)
  - Claude Vision API for land boundary extraction
  - Multi-round refinement with user feedback
  - Structured JSON output (boundary, area, scale, annotations, confidence)
- `land/boundary_confirm.py` — Boundary confirmation logic
  - BoundaryConfirmation with multiple candidates ranked by confidence
  - Vertex adjustment with area/perimeter recalculation
  - Polygon validation (vertex count, area, self-intersection)
- `gui/dialogs/confirm_boundary.py` — Boundary confirmation GUI
  - Matplotlib canvas with image overlay and boundary polygon
  - Draggable vertices for fine-tuning
  - Candidate switching, confidence display, validation warnings
- `gui/dialogs/import_land.py` — Updated import dialog with tabs
  - New "Image (AI)" tab for drag-and-drop image import
  - Automatic AI recognition → confirmation flow
  - Supports all image formats alongside existing GIS formats

#### Part B1: USDZ Packer (Apple Vision Pro / Quick Look)
- `bim/usdz_packer.py` — USD → USDZ packaging
  - Primary: UsdUtils.CreateNewUsdzPackage (pxr)
  - Fallback: ZIP-based packaging for environments without UsdUtils
- `gui/dialogs/export_dialog.py` — Added USDZ export checkbox

#### Part B2: MCP Server (Claude Desktop Integration)
- `mcp/server.py` — FastMCP-based MCP Server
  - 7 tools: import_land, set_zoning, generate_building, modify_building,
    check_compliance, estimate_cost, auto_monitor
  - 2 resources: building://current, building://land
  - Shared per-session state for land/zoning/plan/result
  - Claude Desktop config template in mcp/config.json
- `mcp/config.json` — Claude Desktop server configuration

#### Part B3: Web UI (Streamlit)
- `web/app.py` — Full Streamlit web interface
  - Sidebar: land import (manual/GeoJSON/AI image), zoning rules
  - Main: prompt input, generate button, results display
  - Tabs: Plan JSON, Compliance, Cost chart, File downloads

### Changed
- `schemas/land.py` — Extended LandParcel with ai_confidence, original_image_path, ai_annotations

### Dependencies
- Added `mcp>=1.0` (optional: mcp extra)
- Added `streamlit>=1.55` (optional: web extra)

### Tests
- 76 new tests (516 total), xcodebuild BUILD SUCCEEDED

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
| 0.7.0 | P7+P8 完成 | MEP 管線 + 施工模擬 |
| 0.8.5 | P8.5 完成 | 智慧監控點 |
| 0.9.0 | P9 完成 | AI 圖像辨識 + MCP + Web UI |
| 1.0.0 | P10 完成 | POC 完整版 |
| 1.1.0 | P10.2 完成 | Debug Logging System |
| 1.2.0 | P10.3 完成 | Startup Health Check |
| 1.3.0 | P11 完成 | Xcode ↔ PySide6 整合 |
| 1.4.0 | P12 完成 | 品質修復 + 效能優化 + Demo |
| 1.5.0 | P13 完成 | CLI + 依賴修復 + PDF OCR |
| 2.0.0 | P14 完成 | CI/CD + 安全 + 文件 v2.0 |
| 2.1.0 | P16 完成 | 品質修復 (retry, timeout, constants) |
| 2.4.0 | P17 完成 | 架構強化 + Async + Cache + CI 修復 |
| 2.4.1 | P17.1 完成 | 文檔一致性修復（測試數、CLAUDE.md 版本、啟動通知）|
| 2.5.0 | P18 完成 | V2 Migration Phase 0-1：C++ Core 骨架 + Compliance/Cost C++ + pybind11 + 24 GoogleTests |
