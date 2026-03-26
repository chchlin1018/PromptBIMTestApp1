# PROMPT_P11.md — Sprint P11: Xcode ↔ PySide6 GUI 整合 + E2E 流程修復

> 版本: v1.0.0 | 建立時間: 2026-03-25
> 前置 Sprint: P0~P10.3 全部完成
> 依賴: P0 (Xcode), P4 (AI Agent), P9 (AI 圖像辨識), P10.3 (啟動檢查)

## Sprint 目標

修復 Xcode SwiftUI App 與 Python PySide6 GUI 的整合問題，讓使用者透過 **Xcode Run (Cmd+R)** 就能啟動完整功能的 App，包括：
- 土地圖片拖放匯入 + AI 辨識
- Chat Prompt 生成建築
- 3D 預覽、法規檢查、成本估算、MEP、施工模擬
- 啟動環境檢查 (P10.3)
- Debug 模式 (P10.2)

同時執行 End-to-End 整合測試，確保從圖片輸入到最終匯出的完整流程。

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。

## 必讀文件
1. SKILL.md
2. TODO.md
3. CLAUDE.md
4. `PromptBIMTestApp1/ContentView.swift` — 現有 SwiftUI 介面
5. `PromptBIMTestApp1/PythonBridge.swift` — 現有 Python 橋接
6. `src/promptbim/gui/main_window.py` — PySide6 完整 GUI
7. `src/promptbim/__main__.py` — CLI 進入點

---

## 問題分析

### 根本原因

目前架構有兩個獨立的 GUI：

1. **Xcode SwiftUI** (`ContentView.swift`) — 只是 UI 骨架，沒有連接完整的 Python 互動功能
2. **Python PySide6** (`python -m promptbim gui`) — 完整功能的 GUI

使用者用 Xcode Run (`Cmd+R`) 啟動 App 時，看到的是 SwiftUI 空殼，
按 Generate 沒反應、不能拖放圖片、沒有啟動檢查。

### 解決方案

**方案 A（推薦）：Xcode Run 直接啟動 PySide6 GUI**

修改 `PythonBridge.swift`，讓 Xcode `Cmd+R` 直接啟動 PySide6 GUI，
SwiftUI 只顯示「正在啟動 Python GUI...」的 splash screen。

---

## Task 清單

### Task 1: 修改 PythonBridge.swift — 啟動 PySide6 GUI

- ⬜ 修改 `PythonBridge.swift`
  ```swift
  // 自動偵測 conda promptbim 環境的 Python 路徑
  // 優先順序: miniforge3 > miniconda3 > system python
  func findCondaPython() -> String {
      let home = NSHomeDirectory()
      let candidates = [
          "\(home)/miniforge3/envs/promptbim/bin/python",
          "\(home)/miniconda3/envs/promptbim/bin/python",
          "/opt/homebrew/Caskroom/miniforge/base/envs/promptbim/bin/python",
      ]
      return candidates.first { FileManager.default.fileExists(atPath: $0) }
          ?? "/usr/bin/python3"
  }
  
  // 啟動 PySide6 GUI
  func launchPySide6GUI() {
      let process = Process()
      process.executableURL = URL(fileURLWithPath: findCondaPython())
      process.arguments = ["-m", "promptbim", "gui"]
      process.currentDirectoryURL = projectRootURL  // 專案根目錄
      
      // 傳過環境變數（含 API Key）
      var env = ProcessInfo.processInfo.environment
      // 從 .env 檔讀取 API Key
      if let dotenv = loadDotEnv() {
          env.merge(dotenv) { _, new in new }
      }
      // Debug mode
      env["PROMPTBIM_DEBUG"] = "1"
      process.environment = env
      
      process.launch()
  }
  ```

- ⬜ 新增 `loadDotEnv()` 函式 — 讀取 .env 檔案並解析為 Dictionary
- ⬜ 新增 `findProjectRoot()` 函式 — 從 Bundle 或 working directory 找專案根目錄

### Task 2: 修改 ContentView.swift — Splash Screen + 狀態顯示

- ⬜ 修改 `ContentView.swift`
  - 顯示「PromptBIM 正在啟動...」splash screen
  - 顯示 Python 環境狀態（找到/未找到）
  - 顯示 PySide6 GUI 啟動狀態
  - 如果 Python 環境未找到，顯示安裝指引（連結到 SETUP.md）
  - 提供「重新啟動」按鈕

### Task 3: 修改 PromptBIMTestApp1App.swift — App 生命週期

- ⬜ 修改 `PromptBIMTestApp1App.swift`
  - App 啟動時自動呼叫 `PythonBridge.launchPySide6GUI()`
  - App 關閉時終止 Python process
  - 處理 Python process crash/exit 的狀態

### Task 4: .env 讀取問題修復

- ⬜ 修改 `src/promptbim/config.py`
  - 支援多個 .env 路徑搜尋（working dir, 專案根目錄, home dir）
  - 如果所有路徑都找不到 .env，fallback 到環境變數
  - 添加 debug log 記錄從哪裡讀到 API Key
  ```python
  # 搜尋順序
  env_paths = [
      Path.cwd() / ".env",                          # 當前目錄
      Path(__file__).parent.parent.parent / ".env",  # src/promptbim/../../.env
      Path.home() / "Documents" / "MyProjects" / "PromptBIMTestApp1" / ".env",
      Path.home() / "documents" / "myprojects" / "PromptBIMTestApp1" / ".env",
  ]
  ```

### Task 5: PySide6 GUI 拖放功能驗證

- ⬜ 確認 `gui/dialogs/import_land.py` 拖放功能正常
  - dragEnterEvent 接受 image/* MIME types
  - dropEvent 取得檔案路徑
  - 觸發 AI 辨識流程
- ⬜ 確認 File → Import Land 選單功能正常
  - GeoJSON / Shapefile / DXF / Image (AI) 四個 Tab
- ⬜ 確認圖片 AI 辨識後的 confirm_boundary.py 流程
  - 原圖 + 邊界疊合
  - 拖曳微調
  - 確認/重試

### Task 6: Chat → Generate 完整流程驗證

- ⬜ 確認無土地時 Chat 輸入「在 200 坪地上蓋3層別墅」可生成
  - Orchestrator pipeline: Enhancer → Planner → Builder → Checker
  - 生成後 2D/3D Tab 自動更新
  - 匯出按鈕啟用
- ⬜ 確認有土地時生成流程
  - 土地顯示在 2D Map
  - AI 生成建築置在土地上
  - BCR/FAR 檢查正常
- ⬜ 確認修改指令流程
  - 「改為9層」→ 即時更新
  - 「撤銷」→ 復原

### Task 7: End-to-End 整合測試

- ⬜ 建立 `tests/test_e2e_integration.py`
  - 測試 1: 無土地 + Prompt → 生成 IFC + USD
  - 測試 2: GeoJSON 土地 + Prompt → 完整流程
  - 測試 3: 圖片 AI 辨識 → 確認 → 生成 (mock Vision API)
  - 測試 4: 生成 → 修改 → 撤銷
  - 測試 5: 生成 → 法規檢查 → 成本估算 → MEP → 監控點
  - 測試 6: 生成 → 全部匯出 (IFC + USD + USDZ + SVG + JSON + GIF)
- ⬜ 使用 `Pic_MyLand/` 圖片做圖像辨識測試

### Task 8: Info.plist + pbxproj 更新

- ⬜ 更新 `Info.plist`
  - 加入支援的檔案類型（.geojson, .shp, .dxf, .kml, .jpg, .png, .tiff）
  - 加入拖放支援的 UTI
  - `CFBundleDocumentTypes` 註冊
- ⬜ 更新 `project.pbxproj`
  - `MARKETING_VERSION` 確認為 `1.0.0`
  - `CURRENT_PROJECT_VERSION` 更新

### Task 9: 測試 + 收尾

- ⬜ Xcode `Cmd+R` → 自動啟動 PySide6 GUI
- ⬜ PySide6 GUI 在 Xcode 運行時能拖放圖片
- ⬜ PySide6 GUI 在 Xcode 運行時能 Chat 生成
- ⬜ `python -m promptbim gui` 獨立啟動仍正常
- ⬜ `python -m promptbim check` 仍正常
- ⬜ 所有現有 pytest 仍通過 + E2E 新測試
- ⬜ xcodebuild BUILD SUCCEEDED
- ⬜ iMessage 通知已發送

---

## 驗收標準

1. **Xcode `Cmd+R`** → 自動啟動完整功能的 PySide6 GUI
2. **PySide6 GUI** 可拖放圖片 → AI 辨識 → 確認邊界 → 生成建築
3. **Chat 輸入** 「在200坪地上蓋3層別墅」 → 完整生成流程
4. **E2E 測試** 6 個流程全部通過
5. **向下相容** — `python -m promptbim gui` 獨立啟動仍正常
6. xcodebuild BUILD SUCCEEDED
7. pytest 全部通過
8. iMessage 通知已發送

---

## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
**先修復 Swift 整合（Task 1-3），再修復 Python 問題（Task 4-5），最後跑 E2E 測試（Task 6-7）。**
使用 P10.2 的 debug.py logger，不要用 print()。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
