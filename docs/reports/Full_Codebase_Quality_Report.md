# PromptBIMTestApp1 — 全專案代碼品質與架構分析報告

> 分析師: Claude Opus 4.6（資深軟體品質與架構分析師）
> 日期: 2026-03-26
> 範圍: 全部 Python 源碼（14 子模組）+ Swift 源碼（3 檔案）+ 測試（668 tests）+ 文件
> 基於: GitHub main branch commit `8880328`

---

## 1. 執行摘要

### 1.1 專案統計

| 指標 | 數值 |
|------|------|
| Python 模組 | 14 子模組, 50+ .py 檔案 |
| Swift 檔案 | 3 檔案 + Info.plist + Entitlements |
| 測試數 | 668 passed |
| AI Agents | 7 個（enhancer/planner/builder/checker/modifier/orchestrator/land_reader）|
| 法規引擎 | 15+ 規則（建築/耐震/防火/無障礙）|
| BIM 輸出 | IFC + USD + USDZ |
| GUI 介面 | PySide6（完整）+ SwiftUI（Splash）+ Streamlit（Web）|
| Sprint 完成 | P0~P11（18 個）|

### 1.2 總體評分

| 維度 | 評分 | 說明 |
|------|:----:|------|
| 架構設計 | 8.5/10 | 模組化良好，Agent pipeline 清晰 |
| 代碼品質 | 7.5/10 | 整體乾淨，但有幾處重要缺失 |
| 測試覆蓋 | 8.0/10 | 668 tests 涵蓋面廣，但 E2E 全 mock |
| 文件完整 | 7.0/10 | CHANGELOG/TODO 齊全，但版本不一致 |
| Swift 整合 | 6.0/10 | 功能可用，但有 3 個 Critical bug |
| 安全性 | 6.5/10 | API Key 管理可改進 |

**綜合分數: 7.3/10**

---

## 2. 架構分析

### 2.1 整體架構（優）

```
Xcode SwiftUI App
  └─ PythonBridge.swift (Process())
       └─ python -m promptbim gui
            └─ PySide6 MainWindow
                 ├─ ChatPanel → Orchestrator
                 │    ├─ EnhancerAgent → Claude API
                 │    ├─ PlannerAgent  → Claude API / Fallback
                 │    ├─ BuilderAgent  → IFC + USD (pure Python)
                 │    └─ CheckerAgent  → Taiwan Code Engine
                 ├─ ModelView → PyVista 3D
                 ├─ MapView → Matplotlib 2D
                 ├─ CostPanel → QTO + Estimator
                 ├─ MEPToggle → A* Pathfinder
                 ├─ SimulationTab → 4D Scheduler
                 └─ MonitorToggle → Auto-placement
```

**優點：**
- Agent Pipeline 遵循 Chain of Responsibility，Orchestrator 編排清晰
- Pydantic schemas 作為跨模組資料契約，型別安全
- Fallback 策略完善：每個 Agent 在 API 失敗時有 deterministic fallback
- 雙輸出（IFC + USD）解耦為獨立 generator

### 2.2 Agent 系統（優良）

- `BaseAgent`: Lazy init Anthropic client, JSON extraction 三層策略（直接/markdown/brace scan）
- `Orchestrator`: 迭代修正機制（max 2 iterations），Check → fix → re-Plan
- `ModifierAgent`: 版本歷史 + undo，影響傳播矩陣

**問題:**
- Orchestrator 在 module level 導入所有 Agent（非 lazy），影響啟動速度

---

## 3. 發現問題（新發現 + P11 遺留）

### 3.1 🔴 Critical

#### C1: `generate` CLI 命令未實作

**位置:** `__main__.py` line ~63
```python
elif args.command == "generate":
    print(f"[promptbim] Generate not yet implemented. Prompt: {args.prompt}")
```

**影響:** CLI 的核心功能無法使用。用戶/自動化腳本無法從命令列生成建築。

#### C2: pyproject.toml 版本為 `0.1.0`，實際已是 v1.3.0

**位置:** `pyproject.toml` line 3
```toml
version = "0.1.0"
```

**影響:** `python -m promptbim --version` 顯示錯誤版本，pip install 安裝錯誤版本。

#### C3: `pydantic-settings` 未列入 dependencies

**位置:** `pyproject.toml` dependencies + `config.py`
```python
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings  # Fallback 會失去 .env 讀取能力
```

**影響:** 新安裝環境 fallback 到 BaseModel，.env 功能完全失效。

#### C4: Web optional-dep 與實際不符

**位置:** `pyproject.toml`
```toml
web = ["fastapi>=0.100", "uvicorn>=0.25"]
```
但 `web/app.py` 使用 Streamlit，不是 FastAPI。

#### C5-C7: P11 遺留（PythonBridge 雙實例 / App 未終止進程 / SuddenTermination）

已在 P11 品質報告中詳述，P12 修復中。

### 3.2 🟡 Medium

#### M1: Orchestrator 無部分結果恢復

Builder 失敗時（例如 ifcopenshell 版本不相容），已完成的 Plan 和 Check 結果丟失。應在 except 中保存 partial result。

#### M2: `_poly_area()` shoelace 函式重複

Orchestrator 中有 `_poly_area()`，BIM geometry 中也有 `polygon_area()`。應統一到 `bim/geometry.py` 並全域引用。

#### M3: Agent error handling 不一致

EnhancerAgent 在 API 失敗時有 fallback，但 Orchestrator.modify() 在 API 失敗時直接返回失敗，不嘗試 fallback。

#### M4: GUI thread safety

ChatPanel 使用 QThread 執行 Orchestrator，但 Orchestrator 透過 callback 更新 GUI 狀態。如果 callback 直接修改 UI widget（而非透過 signal/slot），會造成 thread safety 問題。

#### M5: 缺少 `conftest.py` pytest fixtures

668 個測試中，很多 fixture 在各測試檔案中重複定義（如 `_make_land`, `_make_plan`）。應統一到 `conftest.py`。

#### M6: P11 遺留 Medium（MacBook 小寫路徑 / 文件版本 / process.launch() 棄用）

已在 P12 修復中。

### 3.3 🟢 Low

| ID | 問題 | 位置 |
|----|------|------|
| L1 | `imageio` 未列入 dependencies | pyproject.toml |
| L2 | `sounddevice` 未列入 voice optional-dep | pyproject.toml |
| L3 | SKILL.md 未更新 P11 資訊 | SKILL.md |
| L4 | 缺少 `py.typed` marker | src/promptbim/ |
| L5 | 缺少 `__all__` export 定義 | 多個 `__init__.py` |
| L6 | f3d_path 在 Settings 中但從未使用 | config.py |
| L7 | `rich` 在 dependencies 但從未使用 | pyproject.toml |

---

## 4. 安全性分析

| 項目 | 狀態 | 建議 |
|------|:----:|------|
| API Key 儲存 | ⚠️ | .env + 環境變數，可接受但建議加入 keyring |
| Sandbox | ✅ | `com.apple.security.app-sandbox = false`（POC 合理）|
| 依賴安全 | ⚠️ | 建議加入 `pip-audit` 到 CI |
| 輸入驗證 | ✅ | Pydantic schema 提供型別驗證 |
| Process 注入 | ⚠️ | PythonBridge 直接將 prompt 傳入 CLI args，需驗證 |

---

## 5. 效能觀察

| 區域 | 觀察 | 嚴重度 |
|------|------|:------:|
| 模組載入 | 所有 Agent 在 Orchestrator init 時 eager import | 🟡 |
| CLI 啟動 | `--version` 需載入 config + debug 模組 | 🟡 |
| IFC 生成 | 使用 `ifcopenshell.api.run()` 高階 API，效能已優化 | ✅ |
| MEP A* | 3D grid voxelisation 可能對大型建築較慢 | 🟢 |
| E2E Mock | 全 mock 測試無法驗證真實效能 | 🟡 |

---

## 6. 與規格需求對照

| P11 規格要求 | 完成度 | 備註 |
|-------------|:------:|------|
| Xcode Cmd+R 啟動 PySide6 | ✅ | 運作正常 |
| Splash Screen 三態 | ✅ | Python 找到/未找到/GUI 運行中 |
| .env 多路徑搜尋 | ⚠️ | 缺 MacBook 小寫路徑 |
| 拖放圖片 AI 辨識 | ✅ | Mock 驗證通過 |
| Chat → Generate 流程 | ✅ | Mock 驗證通過 |
| E2E 6 類測試 | ✅ | 23 tests, 但全 mock |
| App 生命週期管理 | ❌ | 未實作 terminateGUI on close |
| Info.plist 文件類型 | ✅ | 完整 |

| 全專案功能需求 | 完成度 |
|---------------|:------:|
| 土地匯入（5 格式）| ✅ |
| AI Agent Pipeline | ✅ |
| IFC + USD 雙輸出 | ✅ |
| 台灣法規 15+ 規則 | ✅ |
| 互動式修改 + 撤銷 | ✅ |
| 語音輸入 | ✅ |
| 成本估算 (5D) | ✅ |
| MEP 管線 | ✅ |
| 施工模擬 (4D) | ✅ |
| 智慧監控 | ✅ |
| CLI `generate` 命令 | ❌ 未實作 |
| MCP Server | ✅ |
| Web UI | ✅ |
| PDF OCR | ❌ 未開始 |
| CI/CD | ❌ 未開始 |

---

## 7. Sprint 13/14 建議

### P13: CLI 完整化 + 依賴修復 + PDF OCR

核心目標：修復 Critical 依賴問題，實作 `generate` CLI，新增 PDF OCR。

### P14: CI/CD + 安全強化 + 文件最終化

核心目標：GitHub Actions CI，依賴安全掃描，最終文件更新，git tag v2.0.0。

---

## 8. 結論

PromptBIMTestApp1 作為 POC 已展示完整的 AI-driven BIM 生成能力，從土地匯入到建築生成、法規檢查、成本估算、MEP 規劃、施工模擬、智慧監控，功能鏈完整。

主要改進方向：
1. **依賴管理** — pyproject.toml 有多處與實際不符
2. **CLI 完整性** — `generate` 命令是核心功能卻未實作
3. **Swift 整合品質** — P12 正在修復的 3 個 Critical
4. **CI/CD** — 無自動化測試/部署流程

建議在 P12（品質修復 + 效能）完成後，P13/P14 聚焦在依賴修復、CLI 完整化、PDF OCR、CI/CD。

---

*報告由 Claude Opus 4.6 自動生成，基於 GitHub 全部源碼完整審查。*
