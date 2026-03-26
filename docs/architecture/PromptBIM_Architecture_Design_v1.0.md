# PromptBIM 軟體架構分析與設計說明書

> **版本:** v1.0 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **專案:** PromptBIMTestApp1 — AI 驅動 BIM 建築模型自動生成器
> **範圍:** 現行架構（v2.12.0）至 P29 路線圖

---

## 1. 執行摘要

PromptBIM 是一個概念驗證（POC）系統，允許使用者用自然語言在真實土地地塊上生成符合台灣建築法規的 3D BIM 模型。系統採用多層混合架構：Python 負責 AI Agent 與 GUI，C++ 負責高效能計算引擎，透過 pybind11 橋接。

截至 P25（v2.12.0），系統已完成 25 個 Sprint，800+ 測試，涵蓋 GIS 土地匯入、4-Agent AI Pipeline、IFC/USD 雙輸出、5D 成本估算、4D 施工模擬、MEP 管線生成等完整功能鏈。

P26-P29 路線圖的核心目標是將 GUI 層從 PySide6（Python）遷移至 Qt6 C++ 原生實作，解決記憶體效能瓶頸，為 P30+ 的 Windows 跨平台部署做好準備。

---

## 2. 系統總覽

### 2.1 核心設計原則

1. **零商業軟體依賴** — 全部使用開源 Library
2. **雙輸出格式** — IFC（BIM 語義）+ OpenUSD（Digital Twin / IDTF）
3. **AI Agent + 確定性 Builder 分離** — AI 負責規劃，Python 確定性程式碼負責生成
4. **漸進式 C++ 遷移** — 計算密集模組優先遷移，AI 層保留 Python
5. **治理框架驅動** — CLAUDE.md 嚴格規範自動化開發流程

---

## 3. 分層架構（現行 v2.12.0）

```
L5 使用者介面:  PySide6 GUI | CLI | Streamlit | MCP Server
L4 AI 代理:     Orchestrator + 6 Agents + Cache + Rate Limiter
L3 業務邏輯:    BIM(IFC/USD) | 法規 | 成本 | MEP | 施工模擬 | 監控點
                C++ Native Engine (pybind11)
L2 資料存取:    GIS Parsers | Pydantic Schema | Plugin Registry
L1 基礎設施:    config | debug | constants | CI/CD
```

---

## 4. 模組架構詳解

### 4.1 AI Agent Pipeline

```
Orchestrator.generate() Flow:
  1. Cache lookup (SHA-256)  -> Hit: return cached
  2. Enhancer.run(prompt)        [10%]  (Claude API)
  3. Planner.plan(req,land,zone) [20%]  (Claude API -> JSON)
  4. Builder.build(plan)         [60%]  (Pure Python, NO AI)
  5. Checker.check(plan,codes)   [80%]  (Claude API)
     FAIL -> back to Planner (iteration)
  6. Package + cache store       [100%]
```

| Agent | Role | Uses AI? |
|-------|------|:--------:|
| Enhancer | 需求增強 | Yes |
| Planner | 建築規劃 (JSON) | Yes |
| Builder | IFC/USD 生成 | No |
| Checker | 法規檢查 | Yes |
| Modifier | 互動修改 | Yes |
| LandReader | 圖像辨識 | Yes |

### 4.2 BIM 生成引擎

```
BuildingPlan JSON
  +-> IFCGenerator -> model.ifc  (ifcopenshell / C++ IFC-SPF)
  +-> USDGenerator -> model.usda (pxr.Usd / C++ native)
  +-> USDZPacker   -> model.usdz (ZIP, 64-byte align)

_native_bridge.py: try C++ -> except fallback Python
```

### 4.3 GIS / 土地匯入

| 格式 | Parser | 方法 |
|------|--------|------|
| GeoJSON | geopandas | 直接 polygon |
| Shapefile | fiona | boundary + attribute |
| KML | fastkml | Placemark polygon |
| DXF | ezdxf | LWPOLYLINE |
| PDF | PyMuPDF + pdfplumber | OCR + image |
| Image | Claude Vision | AI boundary |
| Manual | matplotlib | User-drawn |

所有輸入 -> pyproj (WGS84<->TWD97) -> LandParcel -> Setback -> buildable_area

### 4.4 法規引擎

15+ rules: 建蔽率/容積率/高度/樓梯/走廊/電梯/停車/退縮/震區/防火/逃生/無障礙

### 4.5 C++ 原生引擎

CMake + vcpkg | macOS=Clang, Windows=MSVC
- ComplianceEngine, CostEngine, IFCGenerator(C++), USDGenerator(C++)
- pybind11 binding + Python fallback
- GoogleTest: 40+ C++ tests

---

## 5. 資料流架構

```
[土地] -> [LandParcel] -> [退縮] -> [buildable_area]
[描述] -> [Enhancer] -> [Requirement]
                              +-> [Planner] <- [ZoningRules]
                                    +-> [BuildingPlan JSON]
                    +-> [IFC Gen] -> model.ifc
                    +-> [USD Gen] -> model.usda -> model.usdz
                    +-> [Checker] -> ComplianceReport
[Plan] -> [Cost QTO] -> 成本估算
[Plan] -> [MEP A*]   -> 管線 IFC/USD
[Plan] -> [Scheduler] -> Gantt + GIF
[Plan] -> [Monitor]   -> 48種感測器
```

---

## 6. 已知技術問題與風險

| 問題 | 影響 | 根因 | Workaround |
|------|------|------|------------|
| pytest OOM 26GB | Sprint 中斷 | PySide6 import -> QApplication | offscreen + ignore e2e |
| 殭屍 Python | 系統凍結 | pytest GUI 進程未清理 | pkill + 單進程 |
| 16GB 不足 | 開發受限 | Python+PySide6 開銷大 | check_mem |
| API Timeout | CLI 卡住 | Planner 需 60-90秒 | 加大到 120s |

---

## 7. P26-P29 架構演進路線圖

### 目標架構 (P29)

```
L5: Qt6 C++ GUI (QMainWindow) | CLI(Python) | Streamlit | MCP
L4: Python AI Agents (via libpython embedding)
L3: Full C++ Engine (BIM/Compliance/Cost/MEP/Sim/Monitor)
L2: C++ GDAL/OGR + RapidJSON | Python Claude Vision (fallback)
L1: CMake + vcpkg + GitHub Actions CI
```

### Sprint 分解

| Sprint | Focus | Key Deliverables |
|--------|-------|------------------|
| P26 | Qt6 C++ GUI 骨架 | CMake Qt6, QMainWindow, 2D/3D views, libpython |
| P27 | GUI 完整 + 測試遷移 | Cost/MEP/Sim panels, Qt Test + ctest |
| P28 | Python 最小化 | GIS C++ (GDAL), 記憶體驗證 (<2GB) |
| P29 | 清理 + 穩定化 | 移除 PySide6/SwiftUI, Release v3.0.0 |

### 記憶體效能預估

| 元件 | 現行 (Python) | P29 (C++) | 節省 |
|------|:---:|:---:|:---:|
| GUI | ~800MB | ~150MB | 81% |
| BIM Engine | ~200MB | ~50MB | 75% |
| 測試 | 2-26GB | ~200MB | 99% |
| AI Agent | ~100MB | ~100MB | 0% |
| **總計** | **~1.5GB** | **~500MB** | **67%** |

---

## 8. 治理框架架構

```
CLAUDE.md (v1.22.0) -- 最高層級治理規則 (28步)
  +-> SKILL.md (v3.8) -- 專案 SSOT
  +-> PROMPT_P{X}.md -- Sprint 執行指令
  +-> PROJECT_STATUS.md -- 狀態追蹤
  +-> audit-reports/ -- Sprint 審計報告

人工維護: CLAUDE.md, SKILL.md
Claude Code 禁止修改治理文件
```

---

## 9. 版本歷程

| 版本 | Sprint | 里程碑 |
|------|--------|--------|
| v0.1.0 | P0 | 專案骨架 |
| v1.0.0 | P9 | AI Agent + GIS + MCP |
| v2.0.0 | P14 | CI/CD + 安全 |
| v2.4.0 | P17 | Async + Cache + Plugin |
| v2.10.0 | P23 | 審計修復 (最後成功 tag) |
| v2.12.0 | P25 | Performance + Windows + Docs |
| **v3.0.0** | **P29** | **Qt6 C++ GUI + 清理** |

---

*PromptBIM 軟體架構分析與設計說明書 v1.0*
*Reality Matrix Inc. | 2026-03-27*
*完整 PDF 版含詳細模組架構圖、資料流圖、治理流程圖*
