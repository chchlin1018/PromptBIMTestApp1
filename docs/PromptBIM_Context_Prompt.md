# PromptBIMTestApp1 — 完整開發 Context Prompt

> 用途：在新對話中貼入此 Prompt，讓 Claude 接續 PromptBIM 專案的開發工作
> 建立日期：2026-03-25
> 基於：完整開發 Session（17 Sprint + 環境設定 + Xcode 驗證 + 問題分析）

---

## 1. 專案基本資訊

- **名稱：** PromptBIMTestApp1 — AI 驅動的 BIM 建築模型自動生成器
- **GitHub：** https://github.com/chchlin1018/PromptBIMTestApp1 (private, owner: chchlin1018)
- **組織：** Reality Matrix Inc. / Michael Lin (林志錚)
- **性質：** POC (Proof of Concept)
- **版本：** v1.0.0（已打 git tag）

---

## 2. 技術架構

### 雙 GUI 架構（⚠️ 關鍵問題）

目前有兩個獨立的 GUI：
1. **Xcode SwiftUI** (`ContentView.swift`) — 只是 UI 骨架，Generate 沒接後端，不能拖放
2. **Python PySide6** (`python -m promptbim gui`) — 完整功能的 GUI ✅

**P11 Sprint 的目標是修復此整合問題，讓 Xcode Cmd+R 直接啟動 PySide6 GUI。**

### Python 後端（14 個子模組）

- `agents/` — 7 個 AI Agent (enhancer/planner/builder/checker/modifier/orchestrator/land_reader)
- `bim/` — geometry + ifc_generator + usd_generator + materials + usdz_packer + components + cost + mep + monitoring + simulation
- `codes/` — 台灣法規引擎 15+ 條
- `gui/` — PySide6 完整 GUI + startup_check_view
- `land/` — 土地匯入（GeoJSON/SHP/DXF/手動/AI圖像）
- `startup/` — health_check (12項) + ai_check + auto_fix
- `mcp/` — FastMCP Server | `web/` — Streamlit | `voice/` — STT | `viz/` — 3D/2D

### Swift 源碼（3 個檔案）

- `PromptBIMTestApp1App.swift` (229B) — App entry
- `ContentView.swift` (2649B) — 主介面骨架（空殼）
- `PythonBridge.swift` (2688B) — Process() 呼叫 Python

### Xcode pbxproj 關鍵設定

- Bundle ID: `com.realitymatrix.PromptBIMTestApp1`
- Swift 5.0, macOS 14.0, ad-hoc signing
- MARKETING_VERSION: 1.0.0
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
- .env 載入依賴 working directory，P11 會修復

---

## 4. Sprint 完成狀態（17 個完成，645 tests）

P0~P10.3 全部 ✅ 完成。P11（Xcode↔PySide6 整合）PROMPT 已建立，待執行。

### P2 Code Review 5 項修復：全部完成 ✅

---

## 5. 已知問題

| 嚴重度 | 問題 | 狀態 |
|:------:|------|:----:|
| 🔴 | Xcode SwiftUI 是空殼 | P11 修復中 |
| 🟡 | .env 路徑問題 | P11 Task 4 |
| 🟡 | CHANGELOG 缺 P10~P10.3 | 待補 |
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

## 7. 下一步：Sprint P11

PROMPT_P11.md 已在 GitHub，9 個 Task：修改 PythonBridge.swift 啟動 PySide6 GUI、ContentView 改 Splash Screen、.env 多路徑搜尋、E2E 測試 6 個流程。

之後：P12 Demo 影片、P13 PDF OCR、P14 CI/CD。

---

## 8. iMessage 通知

Claude Code Sprint 完成會透過 LaunchAgent + osascript 發送 iMessage 到 +886972535899。

---

*此文件包含 PromptBIMTestApp1 專案的完整上下文。在新對話中貼入即可接續開發。*
