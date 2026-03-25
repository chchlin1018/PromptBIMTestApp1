# PromptBIMTestApp1 — TODO / 開發計劃追蹤

> **版本:** v1.1.0 | **更新:** 2026-03-25 | **版本控制:** 本文件由 Claude Code 自動維護

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
| P7 | MEP 管線自動生成 | 4 | ⬜ | P4 |
| P8 | 施工模擬 (4D) | 3 | ⬜ | P2 |
| P8.5 | 智慧監控點自動配置 | 3 | ⬜ | P4, P7 |

**預估總開發時間: ~34 天**

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

- ⬜ `bim/mep/pathfinder.py` — 3D 正交 A* 尋路
- ⬜ `bim/mep/systems.py` — MEP 系統定義模板
- ⬜ `bim/mep/planner.py` — AI MEP 規劃
- ⬜ `bim/mep/ifc_mep.py` + `usd_mep.py` — 雙輸出
- ⬜ `bim/mep/clash_detect.py` — 基本碰撞偵測
- ⬜ `viz/mep_overlay.py` — 四色管線 3D 疊合
- ⬜ `gui/mep_toggle.py` — 系統顯示開關
- ⬜ 測試 + xcodebuild 通過

**驗收標準:** 一鍵 Auto MEP → 四大系統管線 + IFC/USD 含 MEP

---

## P8: 施工模擬 (~3 天)

- ⬜ `bim/simulation/construction_phases.py` — 階段模板
- ⬜ `bim/simulation/scheduler.py` — AI 排程
- ⬜ `bim/simulation/animator.py` — PyVista 4D 動畫
- ⬜ `viz/gantt_chart.py` — 甘特圖
- ⬜ `gui/simulation_tab.py` — 時間軸滑桿 + 播放
- ⬜ 匯出 GIF 動畫
- ⬜ 測試 + xcodebuild 通過

**驗收標準:** 拖動滑桿看施工進度 + 匯出動畫 + 甘特圖

---

## P8.5: 智慧監控點自動配置 (~3 天)

- ⬜ `bim/monitoring/monitor_types.py` — 48 種監控點定義
- ⬜ `bim/monitoring/auto_placement.py` — 自動配置演算法
- ⬜ `bim/monitoring/rules_engine.py` — 配置密度規則
- ⬜ `bim/monitoring/ifc_monitor.py` — IFC IfcSensor/IfcActuator 輸出
- ⬜ `bim/monitoring/usd_monitor.py` — USD monitor: namespace 輸出 (IDTF)
- ⬜ `bim/monitoring/dashboard_data.py` — 儀表板 JSON 匯出
- ⬜ `gui/monitor_toggle.py` — 3D 監控點顯示/隱藏開關
- ⬜ 監控點成本加入 5D 估算
- ⬜ 測試 + xcodebuild 通過

**驗收標準:** 一鍵 Auto Monitor → 顯示所有監控點 + 匯出清單

---

## 未來 Backlog

- ⬜ PDF 地籍圖 OCR 解析 (pdfplumber)
- ⬜ KML 匯入 + 衛星底圖疊加
- ⬜ MCP Server (Claude Desktop 整合)
- ⬜ USDZ 打包 (Apple Vision Pro / Quick Look)
- ⬜ 多建築 template (學校/醫院/廠房)
- ⬜ Windows 測試 + 打包 (.exe)
- ⬜ 地形高程整合
- ⬜ Web UI (Streamlit/Gradio)
- ⬜ NVIDIA Omniverse 連接測試
- ⬜ Sederes API 整合 (精確耐震參數)
