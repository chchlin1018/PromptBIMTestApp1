# PromptBIMTestApp1 — TODO / 開發計劃追蹤

> **版本:** v2.7.0 | **更新:** 2026-03-26 | **版本控制:** 本文件由 Claude Code 自動維護

---

## 版本控制規則

- 本文件每完成一個 task 由 Claude Code 自動更新
- ✅ = 已完成 | ⬜ = 待開發 | 🔄 = 進行中 | ❌ = 取消
- 每個 Sprint 完成後在 CHANGELOG.md 記錄變更
- **[MANDATORY]** 每次工作結束前必須 xcodebuild 通過 + 更新本文件

---

## Sprint 總覽

| Sprint | 名稱 | 預估天數 | 狀態 | 依賴 |
|--------|------|:--------:|:----:|------|
| P0 | 專案骨架 + Xcode + 環境 | 1 | ✅ | — |
| P1 | 土地匯入 + 2D 視圖 | 3 | ✅ | P0 |
| P2 | IFC + USD 生成核心 | 3 | ✅ | P0 |
| P2.5 | 建築零件庫 | 3 | ✅ | P2 |
| P3 | 3D 互動預覽 | 2 | ✅ | P2 |
| P4 | AI Agent Pipeline | 3 | ✅ | P1, P2 |
| P4.5 | 台灣法規引擎 | 3 | ✅ | P4 |
| P4.8 | 互動式修改引擎 | 2 | ✅ | P4 |
| P5 | 語音 + 匯出 | 2 | ✅ | P4 |
| P6 | 成本估算 (5D) | 2 | ✅ | P2.5 |
| P7 | MEP 管線自動生成 | 4 | ✅ | P4 |
| P8 | 施工模擬 (4D) | 3 | ✅ | P2 |
| P8.5 | 智慧監控點自動配置 | 3 | ✅ | P4, P7 |
| P9 | AI 土地圖像辨識 + Backlog | 3 | ✅ | P1, P4 |
| P10 | Polish + Remaining Backlog | 2 | ✅ | P0~P9 |
| P10.2 | Debug Logging System | 1 | ✅ | All |
| P10.3 | Startup Health Check + AI Validation | 1 | ✅ | P0, P4, P10.2 |
| P11 | Xcode ↔ PySide6 GUI 整合 + E2E | 1 | ✅ | P0~P10.3 |
| P12 | 品質修復 + 效能優化 + Demo 準備 | 1 | ✅ | P0~P11 |
| P13 | CLI 完整化 + 依賴修復 + PDF OCR | 1 | ✅ | P4, P9, P12 |
| P14 | CI/CD + 安全強化 + 文件最終化 | 1 | ✅ | P0~P13 |
| P16 | 全面品質修整 (Quality Remediation) | 1 | ✅ | P14, AuditReport |
| P17 | 全面修整 + 架構強化 + Async + 快取 | 1 | ✅ | P16 |
| P18 | V2 Migration Phase 0-1 — C++ 骨架 + Engine 遷移 | 1 | ✅ | P17 |
| P19 | V2 Migration Phase 2 — MEP + Simulation C++ + P18 技術債 | 1 | ✅ | P18 |
| P20 | V2 Migration Phase 3 — BIM Core (IFC + USD C++) | 1 | ✅ | P19 |

**預估總開發時間: ~50 天**

---

## P0: 專案骨架 + Xcode + 環境 (~1 天)

### Xcode 專案
- ✅ 建立 `PromptBIMTestApp1.xcodeproj` (macOS app target, SwiftUI, Apple Silicon)
- ✅ `PromptBIMTestApp1/PromptBIMTestApp1App.swift` — App entry point
- ✅ `PromptBIMTestApp1/ContentView.swift` — 主介面骨架
- ✅ `PromptBIMTestApp1/PythonBridge.swift` — Process() 呼叫 Python 後端
- ✅ `PromptBIMTestApp1/Info.plist` + `Assets.xcassets` + `Entitlements`
- ✅ Build Phase Script: Python 環境檢查
- ⬜ Build Phase Script: pytest 執行 (deferred — requires conda env on build machine)
- ✅ `xcodebuild -project PromptBIMTestApp1.xcodeproj -scheme PromptBIMTestApp1 build` → BUILD SUCCEEDED

### Python 骨架
- ✅ 完整目錄結構 (所有 `__init__.py`)
- ✅ `pyproject.toml` (含所有依賴)
- ✅ `.env.example` + `config.py` (Pydantic BaseSettings)
- ✅ PySide6 空白主視窗可啟動 (`gui/main_window.py`)
- ✅ CLI skeleton (`__main__.py`: `promptbim gui` / `promptbim --version`)
- ✅ 所有 `schemas/` Pydantic models 骨架
- ⬜ 驗證: ifcopenshell + pxr + anthropic + PySide6 全部可 import (deferred — requires conda env with full deps)

### 收尾
- ✅ pytest 通過 (29 passed)
- ✅ xcodebuild 通過 (BUILD SUCCEEDED)
- ✅ 更新 TODO.md + CHANGELOG.md
- ✅ `git commit [P0] + push main`

**驗收標準:**
1. `xcodebuild ... build` → **BUILD SUCCEEDED**
2. `python -m promptbim --version` → 顯示版本
3. `python -m promptbim gui` → 跑出空白 Qt 視窗

---

## P1: 土地匯入 + 2D 視圖 (~3 天)

- ✅ `land/parsers/geojson.py` — GeoJSON 讀取
- ✅ `land/parsers/shapefile.py` — Shapefile 讀取
- ✅ `land/parsers/dxf.py` — DXF 讀取
- ✅ `land/parsers/manual.py` — 手動座標輸入
- ✅ `schemas/land.py` — LandParcel Pydantic model (P0 已完成，P1 驗證通過)
- ✅ `schemas/zoning.py` — ZoningRules model (P0 已完成，P1 驗證通過)
- ✅ `land/setback.py` — 退縮線計算 (shapely buffer + per-side)
- ✅ `land/projection.py` — 座標系轉換 (pyproj, WGS84→TWD97)
- ✅ `gui/map_view.py` — matplotlib 嵌入 Qt 顯示土地
- ✅ `gui/land_panel.py` — 土地資訊面板
- ✅ `gui/dialogs/import_land.py` — 拖放/選檔匯入
- ✅ 測試 + xcodebuild 通過 (48 tests passed, BUILD SUCCEEDED)

**驗收標準:** 拖放 sample_parcel.geojson → 顯示土地輪廓 + 面積 + 退縮線

---

## P2: IFC + USD 生成核心 (~3 天)

- ✅ `bim/geometry.py` — 牆/板/屋頂 mesh 生成 (wall_mesh, slab_mesh, flat_roof_mesh, gable_roof_mesh)
- ✅ `bim/ifc_generator.py` — IfcOpenShell 高階封裝 (IFCGenerator, 只用 ifcopenshell.api.run())
- ✅ `bim/usd_generator.py` — pxr USD 封裝 (USDGenerator, pxr.Usd/UsdGeom/UsdShade)
- ✅ `bim/materials.py` — 材質定義 (IFC + USD 雙映射, 9 種內建材質)
- ✅ `schemas/plan.py` — BuildingPlan 完整 schema (P0 已完成，P2 驗證通過)
- ✅ `examples/01_simple_box.py` — 硬編碼方盒 → .ifc + .usda
- ✅ `examples/02_l_shaped_office.py` — L型辦公樓 2 層 → .ifc + .usda
- ✅ 測試 + xcodebuild 通過 (82 tests passed, BUILD SUCCEEDED)

**驗收標準:** `python examples/01_simple_box.py` → .ifc + .usda 都可開啟 ✅

---

## P2.5: 建築零件庫 (~3 天)

- ✅ `bim/components/base.py` — ComponentDef + SupplierInfo + PriceRange + ComponentCategory
- ✅ `bim/components/registry.py` — ComponentRegistry (search, get, list_by_category)
- ✅ 結構構件 (12 種) 參數化定義 + 供應商
- ✅ 垂直運輸 (12 種) 參數化定義 + 供應商 (7 家電梯、4 家電扶梯)
- ✅ 開口 (10 種) 參數化定義 + 供應商
- ✅ 其他類別定義: 外殼(10) + 室內(6) + MEP(11) + 衛浴(9) + 基地(6) = 42 種
- ⬜ 下載 5-10 個免費 GLB 模型 (Sketchfab CC0) (deferred — models placeholder ready)
- ✅ 供應商/價格 seed data (台灣市場)
- ✅ 測試 + xcodebuild 通過 (108 tests passed, BUILD SUCCEEDED)

**驗收標準:** `ComponentRegistry.search(["電梯"])` 回傳完整定義含供應商

---

## P3: 3D 互動預覽 (~2 天)

- ✅ `viz/model_3d.py` — BuildingPlan → PyVista mesh 組裝
- ✅ `gui/model_view.py` — pyvistaqt 嵌入 Qt
- ✅ 樓層剖面切換
- ✅ `viz/site_plan.py` — 2D 配置圖 (土地+建築疊合)
- ✅ 測試 + xcodebuild 通過 (127 tests passed, BUILD SUCCEEDED)

**驗收標準:** 生成後 3D Tab 自動顯示可旋轉的建築模型

---

## P4: AI Agent Pipeline (~3 天)

- ✅ `agents/base.py` — Claude API wrapper (BaseAgent)
- ✅ `agents/enhancer.py` — Agent 1: 需求增強
- ✅ `agents/planner.py` — Agent 2: 建築規劃 (含土地+法規 context)
- ✅ `agents/builder.py` — Agent 3: IFC+USD 雙輸出 (純 Python)
- ✅ `agents/checker.py` — Agent 4: 規則檢查 + 迭代修正
- ✅ `agents/orchestrator.py` — Pipeline 編排
- ✅ `gui/chat_panel.py` — Chat UI 整合
- ✅ 測試 + xcodebuild 通過 (164 tests passed, BUILD SUCCEEDED)

**驗收標準:** Chat 輸入描述 → 自動在土地上生成建築 → 2D+3D 同步更新

---

## P4.5: 台灣法規引擎 (~3 天)

- ✅ `codes/base.py` — BaseRule + CheckResult + Severity
- ✅ `codes/tw_building_code.py` — 建蔽率/容積率/高度/樓梯/走廊/電梯/停車 (8 rules)
- ✅ `codes/tw_seismic_code.py` — 震區簡化表 + 結構概估規則 (20 cities)
- ✅ `codes/tw_fire_code.py` — 防火區劃/逃生距離/安全梯 (5 rules)
- ✅ `codes/tw_accessibility_code.py` — 無障礙設施
- ✅ `codes/tw_zoning_data.py` — 各縣市分區 BCR/FAR JSON (6 cities + non-urban)
- ✅ `codes/registry.py` — 規則註冊 + 批次檢查 (15 rules)
- ✅ `codes/report.py` — 合規報告 JSON + 表格
- ✅ 整合到 Checker Agent + Planner prompt
- ✅ 測試 + xcodebuild 通過 (211 tests passed, BUILD SUCCEEDED)

**驗收標準:** 生成建築後自動執行 15+ 條法規檢查，輸出合規報告

---

## P4.8: 互動式修改引擎 (~2 天)

- ✅ `agents/modifier.py` — Modifier Agent (Claude 分析修改意圖)
- ✅ 影響傳播矩陣邏輯
- ✅ 版本歷史 + 差異比較 (ModificationRecord)
- ✅ GUI: 修改影響摘要面板 + 確認/撤銷
- ✅ 增量重算（只重算受影響部分）
- ✅ 測試 + xcodebuild 通過 (235 tests passed, BUILD SUCCEEDED)

**驗收標準:** 用戶說「改為9層」→ 即時更新所有關聯數據 + 顯示比較

---

## P5: 語音 + 匯出 (~2 天)

- ✅ `voice/stt.py` — faster-whisper 本地語音辨識
- ✅ 語音按鈕整合到 Chat 面板
- ✅ 匯出對話框 (IFC + USD + SVG + JSON 一鍵打包)
- ✅ `viz/floorplan.py` — 各層平面圖 SVG
- ✅ 測試 + xcodebuild 通過 (265 tests passed, BUILD SUCCEEDED)

**驗收標準:** 語音描述 → 完整生成 → 一鍵匯出 5 件套

---

## P6: 成本估算 (~2 天)

- ✅ `bim/cost/qto.py` — IFC 數量萃取 (QTO)
- ✅ `bim/cost/unit_prices_tw.py` — 台灣單價表
- ✅ `bim/cost/estimator.py` — 成本計算引擎
- ✅ `viz/cost_charts.py` — 圓餅圖/長條圖
- ✅ `gui/cost_panel.py` — GUI 整合
- ✅ 測試 + xcodebuild 通過 (293 tests passed, BUILD SUCCEEDED)

**驗收標準:** 生成建築後自動顯示估算總價 + 分項圓餅圖

---

## P7: MEP 管線自動生成 (~4 天)

- ✅ `bim/mep/pathfinder.py` — 3D 正交 A* 尋路 (orthogonal pathfinding, turn penalty, obstacle voxelisation)
- ✅ `bim/mep/systems.py` — MEP 系統定義模板 (office + residential, 4 systems, ceiling layer offsets)
- ✅ `bim/mep/planner.py` — MEP 規劃 (deterministic equipment/terminal placement, A* routing)
- ✅ `bim/mep/ifc_mep.py` + `usd_mep.py` — 雙輸出 (IfcPipeSegment/IfcDuctSegment/IfcCableCarrierSegment + USD cubes)
- ✅ `bim/mep/clash_detect.py` — 基本碰撞偵測 (AABB cross-system clash detection)
- ✅ `viz/mep_overlay.py` — 四色管線 3D 疊合 (PyVista tube meshes, blue/red/green/yellow)
- ✅ `gui/mep_toggle.py` — 系統顯示開關 (QCheckBox per system, show/hide all)
- ✅ 測試 + xcodebuild 通過 (338 passed, BUILD SUCCEEDED)

**驗收標準:** 一鍵 Auto MEP → 四大系統管線 + IFC/USD 含 MEP

---

## P8: 施工模擬 (~3 天)

- ✅ `bim/simulation/construction_phases.py` — 16-phase construction template with IFC class mapping
- ✅ `bim/simulation/scheduler.py` — Schedule generation (phase assignment + duration scaling)
- ✅ `bim/simulation/animator.py` — PyVista 4D animation engine + GIF export
- ✅ `viz/gantt_chart.py` — Interactive Gantt chart (matplotlib, synced with 3D view)
- ✅ `gui/simulation_tab.py` — Timeline slider + play/pause + Gantt panel + GIF export button
- ✅ 匯出 GIF 動畫 (via imageio)
- ✅ 測試 + xcodebuild 通過 (388 passed, BUILD SUCCEEDED)

**驗收標準:** 拖動滑桿看施工進度 + 匯出動畫 + 甘特圖

---

## P8.5: 智慧監控點自動配置 (~3 天)

- ✅ `bim/monitoring/monitor_types.py` — 48 種監控點定義 (8 categories, IfcSensor/IfcActuator)
- ✅ `bim/monitoring/auto_placement.py` — 自動配置演算法 (per-space, per-floor, per-building)
- ✅ `bim/monitoring/rules_engine.py` — 配置密度規則 (48 rules, 4 placement modes)
- ✅ `bim/monitoring/ifc_monitor.py` — IFC IfcSensor/IfcActuator 輸出
- ✅ `bim/monitoring/usd_monitor.py` — USD monitor: namespace 輸出 (IDTF)
- ✅ `bim/monitoring/dashboard_data.py` — 儀表板 JSON 匯出
- ✅ `gui/monitor_toggle.py` — 3D 監控點顯示/隱藏開關 (8 category toggles)
- ✅ 監控點成本加入 5D 估算 (CostEstimator accepts MonitorPlan)
- ✅ 測試 + xcodebuild 通過 (440 passed, BUILD SUCCEEDED)

**驗收標準:** 一鍵 Auto Monitor → 顯示所有監控點 + 匯出清單

---

## P9: AI 土地圖像辨識 + Backlog 優先項目 (~3 天)

### Part A: AI 土地圖像辨識
- ✅ `land/parsers/image_preprocess.py` — 圖像預處理 (resize, contrast, HEIC/PDF 轉換, base64 編碼)
- ✅ `land/parsers/image_ai.py` — AI 圖像辨識土地邊界 (Claude Vision API)
- ✅ `agents/land_reader.py` — Land Reader Agent (Vision API + 多輪修正)
- ✅ `land/boundary_confirm.py` — 邊界確認邏輯 (候選排序, 頂點微調, 驗證)
- ✅ `schemas/land.py` — 擴充 LandParcel (ai_confidence, original_image_path, ai_annotations)
- ✅ `gui/dialogs/confirm_boundary.py` — 邊界確認 GUI (原圖疊合 + 拖曳微調)
- ✅ `gui/dialogs/import_land.py` — 更新匯入對話框 (新增 Image AI Tab)
- ✅ 測試圖片 fixtures (4 張 Pic_MyLand 圖片)

### Part B1: USDZ 打包
- ✅ `bim/usdz_packer.py` — USD → USDZ (UsdUtils + ZIP fallback)
- ✅ `gui/dialogs/export_dialog.py` — 新增 USDZ 匯出選項

### Part B2: MCP Server
- ✅ `mcp/server.py` — FastMCP Server (7 tools + 2 resources)
- ✅ `mcp/config.json` — Claude Desktop 設定檔

### Part B3: Web UI
- ✅ `web/app.py` — Streamlit 完整功能 (土地匯入 + AI 生成 + 結果展示)

### 收尾
- ✅ 測試 + xcodebuild 通過 (516 passed, BUILD SUCCEEDED)

**驗收標準:** 拖放圖片 → AI 辨識 → 確認 → 生成; MCP + Streamlit 可用

---

## P10: Polish + Remaining Backlog (~2 天)

- ✅ KML 匯入 + 衛星底圖疊加 (fastkml + basemap overlay)
- ✅ 多建築 template (學校/醫院/廠房) — 3 templates + registry
- ✅ NVIDIA Omniverse 連接測試 — OmniverseConnector + config
- ✅ End-to-end 整合測試 (template → IFC → USD → USDZ → compliance → cost → MEP → simulation → monitoring)
- ✅ 效能優化 + 邊界案例修復
- ✅ 最終文件更新
- ✅ 測試 + xcodebuild 通過 (591 passed, BUILD SUCCEEDED)

**驗收標準:** 所有 backlog 項目完成 + 全部測試通過

---

## P10.2: Debug Logging System (~1 天)

- ✅ `src/promptbim/debug.py` — 統一 Logger 系統 (get_logger, enable/disable_debug, 彩色 console)
- ✅ `config.py` 加入 `debug_mode` + `__main__.py` 加入 `--debug` 參數
- ✅ 土地匯入模組 debug log (geojson, shapefile, dxf, manual, image_ai, image_preprocess, setback, projection, boundary_confirm)
- ✅ BIM 生成模組 debug log (geometry, ifc_generator, usd_generator, materials, usdz_packer)
- ✅ 零件庫 + 成本 debug log (components/registry, cost/qto, cost/estimator, cost/unit_prices_tw)
- ✅ MEP + 施工模擬 + 監控點 debug log (pathfinder, planner, clash_detect, scheduler, animator, auto_placement, rules_engine)
- ✅ AI Agent Pipeline debug log (base, enhancer, planner, builder, checker, modifier, orchestrator, land_reader)
- ✅ 法規引擎 debug log (registry, tw_building_code, tw_seismic_code, tw_fire_code, tw_accessibility_code)
- ✅ GUI + Viz debug log (main_window, chat_panel, model_view, import_land, confirm_boundary, model_3d, mep_overlay, cost_charts)
- ✅ 語音 + MCP + Web debug log (stt, server, app)
- ✅ 測試 + 整合 (12 tests for debug system, 603 total tests passed, xcodebuild BUILD SUCCEEDED)

**驗收標準:** PROMPTBIM_DEBUG=1 顯示完整 debug log, =0 無 debug 輸出, --debug CLI 參數

---

## P10.3: Startup Health Check + AI Validation (~1 天)

- ✅ `src/promptbim/startup/health_check.py` — HealthChecker engine (12 checks, 4 categories)
- ✅ `src/promptbim/startup/ai_check.py` — Claude AI connection validation (key, ping, model, vision)
- ✅ `src/promptbim/startup/auto_fix.py` — Auto-fix suggestions + execution engine
- ✅ `src/promptbim/gui/startup_check_view.py` — GUI startup check panel (real-time updates, progress bar)
- ✅ `src/promptbim/gui/main_window.py` — Integrated startup check on app launch
- ✅ `src/promptbim/__main__.py` — CLI `check` subcommand (--json, --ai, --fix)
- ✅ `src/promptbim/config.py` — New settings: startup_check_enabled, startup_check_skip_ai, ai_ping_timeout_seconds, ai_model
- ✅ Tests (42 new tests: health_check, ai_check, auto_fix, cli_check) — 645 total passed, xcodebuild BUILD SUCCEEDED

**驗收標準:** `python -m promptbim check` 顯示 12 項檢查; GUI 啟動時顯示檢查面板; --json/--ai/--fix 子選項

---

## P11: Xcode ↔ PySide6 GUI 整合 + E2E (~1 天)

- ✅ `PythonBridge.swift` — 新增 findCondaPython(), loadDotEnv(), findProjectRoot(), launchPySide6GUI(), terminateGUI()
- ✅ `ContentView.swift` — Splash screen + Python 狀態顯示 + 安裝指引
- ✅ `PromptBIMTestApp1App.swift` — App 生命週期整合
- ✅ `config.py` — .env 多路徑搜尋 (_find_env_file)
- ✅ `chat_panel.py` — 無土地時自動建立預設地塊
- ✅ `gui/dialogs/import_land.py` — 拖放功能驗證通過
- ✅ `gui/dialogs/confirm_boundary.py` — 邊界確認流程驗證通過
- ✅ `tests/test_e2e_integration.py` — 23 個 E2E 整合測試 (6 類流程)
- ✅ `Info.plist` — 支援檔案類型 (geojson, shp, dxf, kml, jpg, png, tiff) + CFBundleDocumentTypes
- ✅ `project.pbxproj` — CURRENT_PROJECT_VERSION = 11
- ✅ 測試 + xcodebuild 通過 (668 passed, BUILD SUCCEEDED)

**驗收標準:** Xcode Cmd+R → 自動啟動 PySide6 GUI; E2E 6 類測試通過; 向下相容 python -m promptbim gui

---

## P12: 品質修復 + 效能優化 + Demo 準備 (~1 天)

### Part A: 品質修復 (Critical + Medium)
- ✅ T1: 修復 PythonBridge 雙實例問題 (C1) — `@EnvironmentObject` 注入
- ✅ T2: 修復 App 關閉未終止 Python Process (C2) — `AppDelegate.applicationWillTerminate`
- ✅ T3: 修復 NSSupportsSuddenTermination 衝突 (C3) — Info.plist + programmatic management
- ✅ T4: 修復 MacBook 小寫路徑問題 (M1) — `config.py` + `PythonBridge.swift`
- ✅ T5: 修復 process.launch() 棄用 + 變數名衝突 (M5+L4) — `srcPath` rename

### Part B: 效能優化
- ✅ T6: Python 啟動速度優化 — `--version` 0.026s (已達標)
- ✅ T7: Pipeline 效能基準 — IFC<3s, USD<3s, cost<1s, compliance<1s, full<5s
- ✅ T8: Health Check 效能 — `check` ~4s (已達標), `check --ai` ~4s

### Part C: Demo 準備 + 最終 Polish
- ✅ T9: Demo 影片腳本 — `docs/DEMO_SCRIPT.md` (8 場景)
- ✅ T10: 文件版本同步 — CHANGELOG/TODO/README/pyproject.toml → v1.4.0

### Part D: 收尾驗證
- ✅ T11: 全面驗證 + Tag — 675 passed, BUILD SUCCEEDED, git tag v1.4.0

**驗收標準:** 3 Critical 修復; Pipeline < 5s; 8 場景 Demo 腳本; 675+ tests passed; git tag v1.4.0

---

## P13: CLI 完整化 + 依賴修復 + PDF OCR (~1 天)

### Part A: Critical 依賴修復
- ✅ T1: pyproject.toml — version 1.5.0, added pydantic-settings + imageio, removed rich, fixed optional-deps (web→streamlit, voice+sounddevice, pdf+PyMuPDF)
- ✅ T2: __init__.py — importlib.metadata dynamic version, removed f3d_path from config

### Part B: generate CLI 命令
- ✅ T3: _run_generate() + _load_land_file() + _cli_status() — full pipeline from CLI with --format/--city/--template
- ✅ T4: test_cli.py — 15 CLI tests (version, generate, check, help, unit tests)

### Part C: PDF OCR 土地匯入
- ✅ T5: land/parsers/pdf_ocr.py — PDFLandParser (pdfplumber text + PyMuPDF images + Claude Vision AI)
- ✅ T6: GUI import_land.py — PDF (OCR) tab + Info.plist PDF support + CFBundleVersion 13

### Part D: 測試基礎設施
- ✅ T7: tests/conftest.py — shared fixtures (sample_land, sample_plan, sample_zoning, tmp_output) + slow marker
- ✅ T8: poly_area() canonical impl in bim/geometry.py, orchestrator + modifier use shared function

### Part E: 收尾
- ✅ T9: Orchestrator — Builder failure saves plan_partial.json; modify wrapped in try/except
- ✅ T10: 705 passed, BUILD SUCCEEDED, docs updated, git tag v1.5.0

**驗收標準:** generate CLI 可用; 版本一致 1.5.0; PDF OCR 解析器; 共用 fixtures; 705+ tests passed

---

## P14: CI/CD + 安全強化 + 文件最終化 (~1 天)

### Part A: GitHub Actions CI/CD
- ✅ T1: `.github/workflows/ci.yml` — lint + test + coverage + xcodebuild + security audit
- ✅ T2: Ruff lint + format — pyproject.toml 完整設定, 274 issues auto-fixed, 215 files formatted
- ✅ T3: Coverage report — pyproject.toml coverage config, CI --cov-fail-under=70

### Part B: 安全強化
- ✅ T4: pip-audit + `requirements-frozen.txt` + `.github/dependabot.yml`
- ✅ T5: API Key 安全 — config.py validate_api_key(), .env 權限檢查, PythonBridge 權限警告, CLI 安全提示

### Part C: 文件最終化
- ✅ T6: README.md v2.0 — 完整功能列表, CLI 使用, 架構圖, 開發指南
- ✅ T7: SKILL.md v3.1 — P11-P14 功能, CLI 範例, PDF OCR 流程, CI/CD 流程
- ✅ T8: `docs/API.md` — Orchestrator, Agents, Parsers, BIM generators, MCP Server

### Part D: 最終 Polish
- ✅ T9: `py.typed` + `__all__` exports
- ✅ T10: 全量文件同步 — CHANGELOG/TODO/README/Context Prompt/pyproject.toml/__init__.py → v2.0.0
- ✅ T11: Xcode pbxproj 完整性檢查
- ✅ T12: pytest + xcodebuild + git tag v2.0.0 + iMessage

**驗收標準:** CI workflow; ruff clean; pip-audit; coverage >70%; README v2.0; SKILL.md updated; API docs; git tag v2.0.0

---

## P16: 全面品質修整 (~1 天)

### Part A: Critical 修復
- ✅ T1: API 呼叫重試機制 (C-1) — tenacity 指數退避, max 3 次, 5xx only
- ✅ T2: API 呼叫 timeout (C-2) — 30s default, configurable
- ✅ T3: 統一 Shoelace 面積計算 (C-3) — 刪除 6 處重複, 統一用 bim.geometry.poly_area

### Part B: High 修復
- ✅ T4: buildable_area 輸入驗證 (H-1) — >= 3 頂點 + 面積 > 0
- ✅ T5: ComponentRegistry 測試隔離 (H-2) — reset() + autouse fixture
- ✅ T6: 修改歷史持久化 (H-3) — save_history/load_history JSON
- ✅ T7: Planner JSON Schema 驗證 (H-4) — 必填欄位檢查
- ✅ T8: 座標精度保護 (H-5) — model_dump/model_validate 保持精度

### Part C: Medium 修復
- ✅ T9: 魔術數字提取為常數 (M-1) — constants.py
- ✅ T10: IFC/USD 生成前備份 (M-3) — .bak 保留 1 份
- ✅ T11: Swift ContentView 版本號修復 (M-5+M-6) — v2.1.0 + 刪除未用變數
- ✅ T12: CI pip-audit 修復 (P14-M1) — 移除 || true

### Part D: 文件同步與驗收
- ✅ T13: Context Prompt 精確化 — 725 passed, v2.1.0, coverage 85%+
- ✅ T14: 全量文件同步 — TODO/CHANGELOG/README/pyproject/init/AuditReport/PROMPT_P17

**驗收標準:** 725 passed; BUILD SUCCEEDED; ruff clean; 14 issues fixed; git tag v2.1.0

---

## P17: 全面修整 + 架構強化 + Async + 快取 (~1 天)

### Part A: CI/CD 緊急修復
- ✅ T1: requirements-frozen.txt 清理 — 移除無效/衝突項目
- ✅ T2: CVE 修復 — 更新有已知漏洞的套件
- ✅ T3: CI 驗證 — GitHub Actions workflow 通過

### Part B: AuditReport 殘留修復
- ✅ T4: per_side_setback 修復 — 各面退縮線正確計算
- ✅ T5: rate limiter — API 呼叫速率限制
- ✅ T6: schema version — Schema 版本管理機制
- ✅ T7: 輸入大小限制 — 防止超大輸入導致 OOM
- ✅ T8: lxml — XML 處理安全強化
- ✅ T9: ComponentRegistry 倒排索引 — 搜尋效能優化
- ✅ T10: PythonBridge conda 路徑 — 跨機器路徑相容

### Part C: V2 架構強化
- ✅ T11: Lazy Import — 延遲載入減少啟動時間
- ✅ T12: Plugin 架構 — 可擴展的外掛系統
- ✅ T13: V2 Migration Tasks — 架構遷移完成

### Part D: 測試缺口填補
- ✅ T14: network failure — 網路故障場景測試
- ✅ T15: fuzzing — 模糊測試覆蓋邊界案例
- ✅ T16: permissions tests — 權限相關測試

### Part E: Swift 修復 + 文件歸檔
- ✅ T17: ContentView 版本號動態化 — 從 Info.plist 讀取版本
- ✅ T18: AuditReport 更新 — 反映最新修復狀態
- ✅ T19: P14/P16 報告歸檔 — 歷史報告歸檔整理

### Part F: Async/Await
- ✅ T20: BaseAgent.arun() — 基礎 Agent 非同步執行
- ✅ T21: Agent subclasses async — 所有 Agent 子類非同步化
- ✅ T22: Orchestrator.agenerate() — Pipeline 非同步編排
- ✅ T23: CLI async — CLI 命令非同步支援
- ✅ T24: MCP async — MCP Server 非同步處理
- ✅ T25: parallel execution — 可平行化步驟並行執行

### Part G: Plan 快取
- ✅ T26: cache key — 快取鍵值計算邏輯
- ✅ T27: store — 快取儲存層實作
- ✅ T28: orchestrator 整合 — Pipeline 快取整合
- ✅ T29: CLI 快取 — CLI 快取命令支援
- ✅ T30: GUI 快取指示 — GUI 顯示快取命中狀態
- ✅ T31: Streamlit+MCP 整合 — Web/MCP 快取支援

### Part H: 最終文件同步
- ✅ T32: 全量文件同步 — TODO/CHANGELOG/README/Context Prompt/pyproject/init
- ✅ T33: PROMPT_P18.md — 建立下一個 Sprint 指令檔
- ✅ T34: git tag v2.4.0 — 版本標籤建立並推送

**驗收標準:** 34 tasks 全部完成; BUILD SUCCEEDED; pytest passed; async/await 可用; plan cache 可用; git tag v2.4.0

---

## P20: V2 Migration Phase 3 — BIM Core (IFC + USD C++) (~1 天)

### Part A: IFC Generator C++ 遷移
- ✅ Task 1: 研究 IfcOpenShell C++ API（結論: 直接寫 IFC-SPF 格式，避免重量級依賴）
- ✅ Task 2: IFC Generator C++ 實作 (`src/bim/ifc_generator.cpp` + `include/promptbim/ifc_generator.hpp`)
- ✅ Task 3: IFC Generator GoogleTest (`tests/test_ifc_generator.cpp` — 19 tests)
- ✅ Task 4: IFC Generator pybind11 binding + `_native_bridge.py` fallback

### Part B: USD Generator C++ + USDZ + pybind11
- ✅ Task 5: USD Generator C++ 實作 (`src/bim/usd_generator.cpp` + `include/promptbim/usd_generator.hpp`)
- ✅ Task 6: USDZ Packer C++ 實作 (uncompressed zip, 64-byte alignment)
- ✅ Task 7: BIM Engine GoogleTest (`tests/test_bim_engine.cpp` — 21 tests)
- ✅ Task 8: BIM Engine pybind11 binding + `_native_bridge.py` IFC/USD/USDZ fallback

**驗收標準:** GoogleTest 110 passed; pytest 820 passed; xcodebuild BUILD SUCCEEDED; v2.7.0

---

## 未來 Backlog

- ✅ PDF 地籍圖 OCR 解析 (pdfplumber) — P13 完成
- ✅ KML 匯入 + 衛星底圖疊加 — P10 完成
- ✅ MCP Server (Claude Desktop 整合) — P9 完成
- ✅ USDZ 打包 (Apple Vision Pro / Quick Look) — P9 完成
- ✅ 多建築 template (學校/醫院/廠房) — P10 完成
- ⬜ Windows 測試 + 打包 (.exe)
- ⬜ 地形高程整合
- ✅ Web UI (Streamlit) — P9 完成
- ✅ NVIDIA Omniverse 連接測試 — P10 完成
- ⬜ Sederes API 整合 (精確耐震參數)
