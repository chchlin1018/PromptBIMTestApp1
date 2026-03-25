# PROMPT_P0.md — Sprint P0: 專案骨架 + Xcode + 環境

> **版本:** v1.0.0 | **建立:** 2026-03-25
> **前置 Sprint:** 無（第一個 Sprint）
> **依賴:** 無

---

## 環境檢查

**必須先執行環境檢查腳本（見 CLAUDE.md [MANDATORY] 跨機器環境檢查）。**

核心確認項：
- `git pull origin main` 同步完成
- `conda activate promptbim` 或建立新環境
- `xcodebuild -version` 確認 Xcode 已安裝
- `.env` 已設定 API Key

---

## 必讀文件

1. `SKILL.md` — 專案架構、技術棧、Schema、Agent Prompt
2. `TODO.md` — Sprint P0 的完整 task 清單
3. `CLAUDE.md` — 開發行為規範 + [MANDATORY] 規則

---

## 本 Sprint Task 清單

### Xcode 專案
- [ ] 建立 `PromptBIMTestApp1.xcodeproj` (macOS app target, SwiftUI, Apple Silicon)
- [ ] `PromptBIMTestApp1/PromptBIMTestApp1App.swift` — App entry point
- [ ] `PromptBIMTestApp1/ContentView.swift` — 主介面骨架
- [ ] `PromptBIMTestApp1/PythonBridge.swift` — Process() 呼叫 Python 後端
- [ ] `PromptBIMTestApp1/Info.plist` + `Assets.xcassets` + `Entitlements`
- [ ] Build Phase Script: Python 環境檢查
- [ ] Build Phase Script: pytest 執行
- [ ] `xcodebuild build` → BUILD SUCCEEDED

### Python 骨架
- [ ] 完整目錄結構 (所有 `__init__.py`)
- [ ] `pyproject.toml` (含所有依賴)
- [ ] `.env.example` + `config.py` (Pydantic BaseSettings)
- [ ] PySide6 空白主視窗可啟動 (`gui/main_window.py`)
- [ ] CLI skeleton (`__main__.py`: `promptbim gui` / `promptbim --version`)
- [ ] 所有 `schemas/` Pydantic models 骨架
- [ ] 驗證: ifcopenshell + pxr + anthropic + PySide6 全部可 import

### 收尾
- [ ] pytest 通過
- [ ] xcodebuild 通過
- [ ] 更新 TODO.md + CHANGELOG.md
- [ ] 建立 PROMPT_P1.md（下一個 Sprint）
- [ ] `git commit + push`

---

## 驗收標準

1. `xcodebuild -project PromptBIMTestApp1.xcodeproj -scheme PromptBIMTestApp1 build` → **BUILD SUCCEEDED**
2. `python -m promptbim --version` → 顯示版本號
3. `python -m promptbim gui` → 跑出空白 Qt 視窗

---

## 執行規則

- 所有問題答案都是 Yes，不要中斷詢問
- 遇到錯誤自行修復，不要停下來問
- 工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟
- 必須建立 PROMPT_P1.md 給下一個 Sprint

---

## CLI 啟動命令

```bash
cd ~/Documents/MyProjects/PromptBIMTestApp1
conda activate promptbim
claude --dangerously-skip-permissions -p "請讀取 PROMPT_P0.md 並執行所有 task。不要問任何問題。"
```
