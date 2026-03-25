# PROMPT_P12.md — Sprint P12: P11 品質修復 + Demo 準備 + 文件同步

> 版本: v1.0.0 | 建立時間: 2026-03-26
> 前置 Sprint: P0~P11 全部完成
> 依賴: P11 (Xcode ↔ PySide6 整合)
> 品質分析: docs/reports/P11_Quality_Analysis_Report.md

## Sprint 目標

修復 P11 Sprint 品質分析報告中發現的 3 個 Critical 問題、5 個 Medium 問題，
並完成 Demo 影片腳本準備與所有文件同步。

**重點：修復 Python 進程洩漏 + App 生命週期 + 文件一致性。**

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。

## 必讀文件
1. SKILL.md
2. CLAUDE.md
3. docs/reports/P11_Quality_Analysis_Report.md（⚠️ 必讀，所有修復項目來自此報告）
4. `PromptBIMTestApp1/PromptBIMTestApp1App.swift`
5. `PromptBIMTestApp1/ContentView.swift`
6. `PromptBIMTestApp1/PythonBridge.swift`
7. `src/promptbim/config.py`

---

## Task 清單

### Task 1: 🔴 修復 PythonBridge 雙實例問題 (C1)

- ⬜ 修改 `PromptBIMTestApp1App.swift`
  - App 層持有唯一 `@StateObject private var bridge = PythonBridge()`
  - 透過 `.environmentObject(bridge)` 或 init 注入傳遞給 ContentView
- ⬜ 修改 `ContentView.swift`
  - 改用 `@EnvironmentObject var bridge: PythonBridge` 或 `@ObservedObject`
  - 移除 `@StateObject private var bridge = PythonBridge()`
- ⬜ 確保只有一個 PythonBridge 實例在整個 App 生命週期中存在
- ⬜ PythonBridge 需要 conform to `ObservableObject`（已有）

### Task 2: 🔴 修復 App 關閉未終止 Python Process (C2)

- ⬜ 修改 `PromptBIMTestApp1App.swift`
  - 監聽 `NSApplication.willTerminateNotification`
  - 在 App 終止時呼叫 `bridge.terminateGUI()`
  - 使用 `@Environment(\.scenePhase)` 監控場景變化
  ```swift
  // 範例結構
  @main
  struct PromptBIMTestApp1App: App {
      @StateObject private var bridge = PythonBridge()
      @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
      
      var body: some Scene {
          WindowGroup {
              ContentView()
                  .environmentObject(bridge)
          }
          .windowStyle(.titleBar)
          .defaultSize(width: 800, height: 500)
      }
  }
  
  class AppDelegate: NSObject, NSApplicationDelegate {
      func applicationWillTerminate(_ notification: Notification) {
          // 取得 bridge 並終止 GUI
      }
  }
  ```
- ⬜ 驗證 Cmd+Q 後 `ps aux | grep promptbim` 無殘留進程

### Task 3: 🔴 修復 NSSupportsSuddenTermination 衝突 (C3)

- ⬜ 修改 `Info.plist`
  ```xml
  <key>NSSupportsAutomaticTermination</key>
  <false/>
  <key>NSSupportsSuddenTermination</key>
  <false/>
  ```
- ⬜ 或在 `PythonBridge.launchPySide6GUI()` 中加入：
  ```swift
  ProcessInfo.processInfo.disableSuddenTermination()
  ```
  並在 `terminateGUI()` 中：
  ```swift
  ProcessInfo.processInfo.enableSuddenTermination()
  ```

### Task 4: 🟡 修復 MacBook 小寫路徑問題 (M1)

- ⬜ 修改 `src/promptbim/config.py` `_find_env_file()`
  ```python
  env_paths = [
      Path.cwd() / ".env",
      Path(__file__).parent.parent.parent / ".env",
      Path.home() / "Documents" / "MyProjects" / "PromptBIMTestApp1" / ".env",
      Path.home() / "documents" / "myprojects" / "PromptBIMTestApp1" / ".env",  # MacBook
  ]
  ```
- ⬜ 修改 `PythonBridge.swift` `findProjectRoot()`
  ```swift
  // 加入 MacBook 小寫路徑
  let macbookPath = URL(fileURLWithPath: "\(home)/documents/myprojects/PromptBIMTestApp1")
  ```

### Task 5: 🟡 文件版本同步 (M2-M4)

- ⬜ 更新 `CHANGELOG.md` 版本對照表，新增：
  ```
  | 1.1.0 | P10.2 完成 | Debug 系統 |
  | 1.2.0 | P10.3 完成 | 啟動健檢 |
  | 1.3.0 | P11 完成 | Xcode↔PySide6 整合 |
  | 1.4.0 | P12 完成 | 品質修復 + Demo |
  ```
- ⬜ 更新 `TODO.md` 頂部版本為 `v1.4.0` 並加入 P12 section
- ⬜ 更新 `docs/PromptBIM_Context_Prompt.md` 反映 P11 已完成 + P12 狀態
- ⬜ 確認 `pyproject.toml` version 與 CHANGELOG 一致

### Task 6: 🟡 修復 process.launch() 棄用 (M5)

- ⬜ 修改 `PythonBridge.swift` `runCommand()` 方法
  - 將 `process.launch()` 改為 `try process.run()`
  - 加入 proper error handling
- ⬜ 修改 `generateBuilding()` 同理
- ⬜ 統一所有 Process 使用 `try process.run()` pattern

### Task 7: 🟡 加入真實整合測試標記 (L1)

- ⬜ 在 `tests/test_e2e_integration.py` 中加入 `@pytest.mark.integration` 裝飾器
  - 標記需要真實 API Key 的測試為 `@pytest.mark.slow` 或 `@pytest.mark.api`
  - 加入 `conftest.py` 中 `pytest.ini` 設定：
    ```ini
    markers =
        integration: marks tests requiring real API (deselect with '-m "not integration"')
        api: marks tests requiring Claude API key
    ```
- ⬜ 加入至少 2 個非 mock 的 smoke test（跳過如 API key 不存在）

### Task 8: 🟡 變數名修復 + git tag (L2-L4)

- ⬜ 修改 `PythonBridge.swift` `launchPySide6GUI()`
  - 將區域變數 `let pythonPath = ...` 改名為 `let srcPath = ...`
  - 避免與 class property `self.pythonPath` 混淆
- ⬜ 確認 `pyproject.toml` 版本號一致
- ⬜ 在完成 P12 後打 git tag: `git tag -a v1.4.0 -m "P12: Quality fixes + Demo prep"`

### Task 9: Demo 影片腳本

- ⬜ 建立 `docs/DEMO_SCRIPT.md`
  - 場景 1: Xcode Cmd+R → Splash → PySide6 GUI 啟動
  - 場景 2: 拖放 Pic_MyLand 圖片 → AI 辨識 → 確認邊界
  - 場景 3: Chat 輸入「在200坪地上蓋3層別墅」→ 完整生成
  - 場景 4: 3D 預覽 + 樓層切換 + 法規報告 + 成本估算
  - 場景 5: 「改為9層」→ 即時更新 + 撤銷
  - 場景 6: MEP 管線 + 施工模擬 + 監控點
  - 場景 7: 一鍵匯出 (IFC + USD + USDZ + SVG)
  - 場景 8: `python -m promptbim check` 健康檢查
  - 每場景含：操作步驟、預期畫面、旁白稿

### Task 10: 測試 + 收尾

- ⬜ 所有 Critical 修復驗證：
  - 確認只有 1 個 PythonBridge 實例（加 init log 驗證）
  - 確認 Cmd+Q 後無殘留 Python 進程
  - 確認 SuddenTermination 已禁用或正確管理
- ⬜ MacBook 小寫路徑驗證（在 MacBook 上測試 .env 讀取）
- ⬜ 所有現有 pytest 仍通過
- ⬜ xcodebuild BUILD SUCCEEDED
- ⬜ `python -m promptbim check` 通過
- ⬜ git tag v1.4.0
- ⬜ iMessage 通知已發送

---

## 驗收標準

1. **PythonBridge 單一實例** — App 生命週期中只有一個 bridge 物件
2. **進程清理** — Cmd+Q 或 window close 後，`ps aux | grep promptbim` 返回空
3. **MacBook 相容** — 在 MacBook（小寫路徑）上 .env 可被正確讀取
4. **文件一致** — CHANGELOG / TODO / Context Prompt / pyproject.toml 版本號一致
5. **Demo 腳本** — DEMO_SCRIPT.md 涵蓋 8 個場景
6. **向下相容** — `python -m promptbim gui` 獨立啟動仍正常
7. **所有測試通過** + xcodebuild BUILD SUCCEEDED

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
**先修復 Critical 問題（Task 1-3），再修復 Medium（Task 4-6），最後文件 + Demo（Task 5,9）。**
使用 P10.2 的 debug.py logger，不要用 print()。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
