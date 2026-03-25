# PromptBIMTestApp1 — 完整開發 Context Prompt

> 用途：在新對話中貼入此 Prompt，讓 Claude 接續 PromptBIM 專案的開發工作
> 更新日期：2026-03-26
> 基於：完整開發 Session（18 Sprint + 環境設定 + Xcode 驗證 + 品質分析）

---

## 1. 專案基本資訊

- **名稱：** PromptBIMTestApp1 — AI 驅動的 BIM 建築模型自動生成器
- **GitHub：** https://github.com/chchlin1018/PromptBIMTestApp1 (private, owner: chchlin1018)
- **組織：** Reality Matrix Inc. / Michael Lin (林志錚)
- **性質：** POC (Proof of Concept)
- **版本：** v1.4.0（P12 完成）
- **測試：** 675 passed, xcodebuild BUILD SUCCEEDED

---

## 2. 技術架構

### 雙 GUI 架構

1. **Xcode SwiftUI** — Splash Screen + Python 環境偵測 + PySide6 啟動器
2. **Python PySide6** — 完整功能的 GUI（透過 PythonBridge 從 SwiftUI 啟動）

**P12 已修復所有 Critical 問題：**
- C1: PythonBridge 單一實例（`@EnvironmentObject` 注入）✅
- C2: App 關閉時正確終止 Python Process（`AppDelegate`）✅
- C3: NSSupportsSuddenTermination 正確管理 ✅

### Python 後端（14+ 子模組）

- `agents/` — 7 個 AI Agent (enhancer/planner/builder/checker/modifier/orchestrator/land_reader)
- `bim/` — geometry + ifc_generator + usd_generator + materials + usdz_packer + components + cost + mep + monitoring + simulation
- `codes/` — 台灣法規引擎 15+ 條
- `gui/` — PySide6 完整 GUI + startup_check_view
- `land/` — 土地匯入（GeoJSON/SHP/DXF/KML/手動/AI圖像）
- `startup/` — health_check (12項) + ai_check + auto_fix
- `mcp/` — FastMCP Server | `web/` — Streamlit | `voice/` — STT | `viz/` — 3D/2D

### Swift 源碼（3 個檔案 + Info.plist）

- `PromptBIMTestApp1App.swift` (282B) — App entry + 生命週期（⚠️ 需修復）
- `ContentView.swift` (5950B) — Splash Screen 三態 UI
- `PythonBridge.swift` (9167B) — conda 偵測 + .env + PySide6 啟動/終止
- `Info.plist` (2523B) — 支援 geojson/shp/dxf/kml/jpg/png/tiff

### Xcode pbxproj 關鍵設定

- Bundle ID: `com.realitymatrix.PromptBIMTestApp1`
- Swift 5.0, macOS 14.0, ad-hoc signing
- MARKETING_VERSION: 1.0.0, CURRENT_PROJECT_VERSION: 11
- ENABLE_USER_SCRIPT_SANDBOXING: NO

---

## 3. 開發環境

### Mac Mini M4（Claude Code 執行）
- 路徑: `~/Documents/MyProjects/PromptBIMTestApp1`
- SSH: `ssh michaellin@MichaeldeMac-mini.local`

### MacBook（Xcode + 測試）
- 路徑: `~/documents/myprojects/PromptBIMTestApp1`（⚠️ 小寫）
- 需要: `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer`

### API Key 設定
- 用 `conda env config vars set ANTHROPIC_API_KEY=... -n promptbim`（不要依賴 .env）
- config.py 支援多路徑 .env 搜尋

---

## 4. Sprint 完成狀態（18 個完成，668 tests）

P0~P11 全部 ✅ 完成。P12（品質修復 + Demo）PROMPT 已建立，待執行。

### P11 品質分析結果
- 3 個 🔴 Critical 問題（PythonBridge 雙實例 / 進程洩漏 / SuddenTermination）
- 5 個 🟡 Medium 問題（小寫路徑 / 文件版本 / 棄用 API）
- 4 個 🟢 Low 問題（Mock 測試 / git tag / 變數名）
- 詳細報告：`docs/reports/P11_Quality_Analysis_Report.md`

---

## 5. 已知問題

| 嚴重度 | 問題 | 狀態 |
|:------:|------|:----:|
| 🔴 | PythonBridge 雙實例 | P12 T1 修復 |
| 🔴 | App 關閉未終止 Python | P12 T2 修復 |
| 🔴 | SuddenTermination 衝突 | P12 T3 修復 |
| 🟡 | MacBook 小寫路徑 | P12 T4 修復 |
| 🟡 | 文件版本不一致 | P12 T5 修復 |
| 🟡 | process.launch() 棄用 | P12 T6 修復 |
| 🟢 | PROMPT_P1.md 缺失 | Cosmetic |

---

## 6. 啟動命令

```bash
# MacBook GUI（目前唯一正確方式）
cd ~/documents/myprojects/PromptBIMTestApp1 && conda activate promptbim && PROMPTBIM_DEBUG=1 python -m promptbim gui

# 環境檢查
python -m promptbim check --ai

# Mac Mini 跑 Sprint
ssh michaellin@MichaeldeMac-mini.local
tmux new -s dev || tmux attach -t dev
cd ~/Documents/MyProjects/PromptBIMTestApp1 && git pull origin main && conda activate promptbim
claude --dangerously-skip-permissions -p "請讀取 PROMPT_P{X}.md 並執行所有 task。不要問任何問題。"
```

---

## 7. 下一步：Sprint P12

PROMPT_P12.md 已在 GitHub，10 個 Task：
- T1-T3: 修復 3 個 Critical 問題（PythonBridge 單實例 + App 終止 + SuddenTermination）
- T4: MacBook 小寫路徑修復
- T5: 文件版本同步（CHANGELOG / TODO / Context Prompt / pyproject.toml）
- T6: process.launch() 棄用修復
- T7: 真實整合測試標記
- T8: 變數名修復 + git tag
- T9: Demo 影片腳本（8 場景）
- T10: 驗證 + 收尾

之後：P13 PDF OCR、P14 CI/CD。

---

## 8. iMessage 通知

Claude Code Sprint 完成會透過 LaunchAgent + osascript 發送 iMessage 到 +886972535899。

---

*此文件包含 PromptBIMTestApp1 專案的完整上下文。在新對話中貼入即可接續開發。*
