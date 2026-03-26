# PromptBIMTestApp1 — 完整開發 Context Prompt

> 用途：在新對話中貼入此 Prompt，讓 Claude 接續 PromptBIM 專案的開發工作
> 更新日期：2026-03-26
> 基於：完整開發 Session（20 Sprint + 品質分析 + V2 架構設計）

---

## 1. 專案基本資訊

- **名稱：** PromptBIMTestApp1 — AI 驅動的 BIM 建築模型自動生成器
- **GitHub：** https://github.com/chchlin1018/PromptBIMTestApp1 (private, owner: chchlin1018)
- **組織：** Reality Matrix Inc. / Michael Lin (林志錚)
- **性質：** POC (Proof of Concept)
- **版本：** v2.0.0（P14 完成）
- **測試：** 705+ passed, xcodebuild BUILD SUCCEEDED

---

## 2. 技術架構

### 雙 GUI 架構

1. **Xcode SwiftUI** — Splash Screen + Python 環境偵測 + PySide6 啟動器
2. **Python PySide6** — 完整功能的 GUI（透過 PythonBridge 從 SwiftUI 啟動）

P12 已修復所有 Critical 問題（單實例 / 進程終止 / SuddenTermination）✅

### Python 後端（14+ 子模組）

- `agents/` — 7 個 AI Agent (enhancer/planner/builder/checker/modifier/orchestrator/land_reader)
- `bim/` — geometry + ifc_generator + usd_generator + materials + usdz_packer + components + cost + mep + monitoring + simulation
- `codes/` — 台灣法規引擎 15+ 條
- `gui/` — PySide6 完整 GUI + startup_check_view
- `land/` — 土地匯入（GeoJSON/SHP/DXF/KML/PDF OCR/手動/AI圖像）
- `startup/` — health_check (12項) + ai_check + auto_fix
- `mcp/` — FastMCP Server | `web/` — Streamlit | `voice/` — STT | `viz/` — 3D/2D

### CLI 命令（P13 新增）

```bash
python -m promptbim --version           # 顯示版本
python -m promptbim gui                 # 啟動 PySide6 GUI
python -m promptbim generate "prompt"   # CLI 生成建築 ✅
python -m promptbim check [--ai]        # 健康檢查
```

### Swift 源碼

- `PromptBIMTestApp1App.swift` — App entry + AppDelegate 生命週期
- `ContentView.swift` — Splash Screen 三態 UI
- `PythonBridge.swift` — conda 偵測 + .env + PySide6 啟動/終止

---

## 3. Sprint 完成狀態

| Sprint | 名稱 | 狀態 | Tests |
|--------|------|:----:|:-----:|
| P0-P11 | 基礎開發（18 Sprint）| ✅ | 668 |
| P12 | 品質修復 + 效能優化 + Demo | ✅ | 675 |
| P13 | CLI 完整化 + 依賴修復 + PDF OCR | ✅ | 705 |
| P14 | CI/CD + 安全強化 + 文件最終化 | ✅ | 705+ |

---

## 4. 開發環境

### Mac Mini M4（Claude Code 執行）
- 路徑: `~/Documents/MyProjects/PromptBIMTestApp1`
- SSH: `ssh michaellin@michaelmac-mini`

### MacBook（Xcode + 測試）
- 路徑: `~/documents/myprojects/PromptBIMTestApp1`（小寫）

---

## 5. 下一步

### POC v2.0 完成

P14 為最後一個 POC Sprint。v2.0.0 是 POC 里程碑版本。

### V2 架構設計

`docs/DesignDocForV2.md` 已建立，待審閱後拆為 Sprint Tasks。

---

## 6. 重要文件

| 文件 | 用途 |
|------|------|
| `CLAUDE.md` v1.8.0 | Claude Code 行為規範 |
| `SKILL.md` v3.1 | 專案 SSOT |
| `docs/API.md` | API 文件 |
| `docs/DesignDocForV2.md` | V2 混合架構設計 |
| `docs/DEMO_SCRIPT.md` | Demo 影片 8 場景腳本 |
| `docs/reports/` | 品質分析報告 |
| `.github/workflows/ci.yml` | CI/CD pipeline |

---

*此文件包含 PromptBIMTestApp1 專案的完整上下文。在新對話中貼入即可接續開發。*
