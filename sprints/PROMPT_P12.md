# PROMPT_P12.md — Sprint P12: 品質修復 + 效能優化 + Demo 準備 + 最終 Polish

> 版本: v2.0.0（合併版）| 建立時間: 2026-03-26
> 前置 Sprint: P0~P11 全部完成（668 tests, xcodebuild BUILD SUCCEEDED）
> 依賴: P11 (Xcode ↔ PySide6 整合)
> 品質分析: docs/reports/P11_Quality_Analysis_Report.md
> 來源: Claude Code P11 規劃（效能優化 + 最終 Polish）+ 品質分析報告（Critical/Medium 修復）+ 原始路線圖（Demo 影片）

## Sprint 目標

本 Sprint 合併三個目標：
1. **品質修復**（Priority 0）— 修復 P11 品質分析報告中 3 個 Critical + 5 個 Medium 問題
2. **效能優化**（Priority 1）— Python 後端啟動速度、模組載入、生成 pipeline 效能
3. **Demo 準備 + 最終 Polish**（Priority 2）— Demo 影片腳本、文件一致性、git tag

**執行順序: Critical 修復 → 效能優化 → Demo + Polish → 收尾驗證**

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。

## 必讀文件
1. SKILL.md
2. CLAUDE.md
3. docs/reports/P11_Quality_Analysis_Report.md（⚠️ 必讀，Critical/Medium 修復項目來自此報告）
4. `PromptBIMTestApp1/PromptBIMTestApp1App.swift`
5. `PromptBIMTestApp1/ContentView.swift`
6. `PromptBIMTestApp1/PythonBridge.swift`
7. `src/promptbim/config.py`
8. `src/promptbim/__main__.py`
9. `src/promptbim/agents/orchestrator.py`

---

## Part A: 品質修復（Critical + Medium）

### Task 1: 🔴 修復 PythonBridge 雙實例問題 (C1)

- ⬜ 修改 `PromptBIMTestApp1App.swift`
  - App 層持有唯一 `@StateObject private var bridge = PythonBridge()`
  - 透過 `.environmentObject(bridge)` 注入傳遞給 ContentView
- ⬜ 修改 `ContentView.swift`
  - 改用 `@EnvironmentObject var bridge: PythonBridge`
  - 移除 `@StateObject private var bridge = PythonBridge()`
- ⬜ 確保整個 App 生命週期中只有一個 PythonBridge 實例
- ⬜ 在 `PythonBridge.init()` 加入 debug log 驗證只呼叫一次

### Task 2: 🔴 修復 App 關閉未終止 Python Process (C2)

- ⬜ 修改 `PromptBIMTestApp1App.swift`
  - 加入 `@NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate`
  - 新增 `AppDelegate` class 實作 `applicationWillTerminate`
  - 在 App 終止時呼叫 `bridge.terminateGUI()`
  ```swift
  @main
  struct PromptBIMTestApp1App: App {
      @StateObject private var bridge = PythonBridge()
      @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
      
      var body: some Scene {
          WindowGroup {
              ContentView()
                  .environmentObject(bridge)
                  .onAppear { appDelegate.bridge = bridge }
          }
          .windowStyle(.titleBar)
          .defaultSize(width: 800, height: 500)
      }
  }
  
  class AppDelegate: NSObject, NSApplicationDelegate {
      var bridge: PythonBridge?
      
      func applicationWillTerminate(_ notification: Notification) {
          bridge?.terminateGUI()
      }
      
      func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
          true
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
- ⬜ 在 `PythonBridge.launchPySide6GUI()` 中加入：
  ```swift
  ProcessInfo.processInfo.disableSuddenTermination()
  ```
  並在 `terminateGUI()` 中：
  ```swift
  ProcessInfo.processInfo.enableSuddenTermination()
  ```

### Task 4: 🟡 修復 MacBook 小寫路徑問題 (M1)

- ⬜ 修改 `src/promptbim/config.py` `_find_env_file()`
  - 加入 `Path.home() / "documents" / "myprojects" / "PromptBIMTestApp1" / ".env"` 到搜尋清單
- ⬜ 修改 `PythonBridge.swift` `findProjectRoot()`
  - 加入 `~/documents/myprojects/PromptBIMTestApp1` 到 well-known paths

### Task 5: 🟡 修復 process.launch() 棄用 + 變數名衝突 (M5 + L4)

- ⬜ 修改 `PythonBridge.swift`
  - `runCommand()`: 將 `process.launch()` 改為 `try process.run()` + proper error handling
  - `generateBuilding()`: 同理改為 `try process.run()`
  - `launchPySide6GUI()`: 將區域變數 `let pythonPath` 改名為 `let srcPath` 避免與 class property 混淆
- ⬜ 統一所有 Process 使用 `try process.run()` pattern

---

## Part B: 效能優化

### Task 6: Python 啟動速度優化

- ⬜ 分析 `python -m promptbim gui` 的啟動時間
  ```bash
  time python -m promptbim gui --help  # 量測模組載入時間
  ```
- ⬜ 優化 `__main__.py` 的 import 結構
  - 將 heavy imports (PySide6, pyvista, ifcopenshell, pxr) 改為 lazy import
  - CLI 子命令只在需要時才載入對應模組
  ```python
  # Before: 所有模組在啟動時載入
  from promptbim.gui.main_window import MainWindow
  
  # After: 只在 gui 子命令時才載入
  def cmd_gui():
      from promptbim.gui.main_window import MainWindow
      ...
  ```
- ⬜ 確認 `python -m promptbim --version` 在 1 秒內完成

### Task 7: 生成 Pipeline 效能基準

- ⬜ 在 `tests/test_integration/test_performance.py` 中補充/驗證效能基準
  - `generate_schedule()` < 2 秒
  - `IFCGenerator.generate()` < 3 秒
  - `USDGenerator.generate()` < 3 秒
  - `CostEstimator.estimate()` < 1 秒
  - `run_all_checks()` < 1 秒
  - Orchestrator 完整 pipeline (with mock AI) < 5 秒
- ⬜ 如果超過基準，profile 並優化瓶頸
- ⬜ 加入 `@pytest.mark.benchmark` 標記

### Task 8: Startup Health Check 效能優化

- ⬜ 確認 `python -m promptbim check` 在 10 秒內完成（不含 AI ping）
- ⬜ 確認 `python -m promptbim check --ai` 在 20 秒內完成
- ⬜ 如果依賴檢查太慢，改為 parallel import check
  ```python
  import concurrent.futures
  def check_imports_parallel():
      with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
          futures = {executor.submit(check_dep, dep): dep for dep in deps}
  ```

---

## Part C: Demo 準備 + 最終 Polish

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
  - 每場景含：操作步驟、預期畫面、旁白稿、預估時長

### Task 10: 文件版本同步 + 最終 Polish

- ⬜ 更新 `CHANGELOG.md`
  - 新增 [1.4.0] P12 section
  - 更新版本對照表加入 P10.2 / P10.3 / P11 / P12
- ⬜ 更新 `TODO.md`
  - 頂部版本改為 `v1.4.0`
  - 加入 P12 完整 section（所有 task 標記完成）
- ⬜ 更新 `docs/PromptBIM_Context_Prompt.md` 反映 P12 完成狀態
- ⬜ 確認 `pyproject.toml` version 與 CHANGELOG 一致
- ⬜ 加入整合測試標記
  - `conftest.py` 中設定 `pytest.ini` markers: `integration`, `api`, `benchmark`
  - 在 `test_e2e_integration.py` 加入 `@pytest.mark.integration`
  - 加入至少 2 個非 mock 的 smoke test（跳過如 API key 不存在）
- ⬜ 確認 README.md 反映最新狀態

---

## Part D: 收尾驗證

### Task 11: 全面驗證 + Tag

- ⬜ Critical 修復驗證：
  - 確認只有 1 個 PythonBridge 實例（init log 只出現一次）
  - 確認 Cmd+Q 後 `ps aux | grep promptbim` 無殘留
  - 確認 SuddenTermination 已禁用或正確管理
- ⬜ 效能驗證：
  - `python -m promptbim --version` < 1 秒
  - `python -m promptbim check` < 10 秒
  - 所有 benchmark 測試在閾值內
- ⬜ MacBook 相容驗證（小寫路徑 .env 可讀取）
- ⬜ 所有現有 pytest 仍通過 + 新增測試通過
- ⬜ xcodebuild BUILD SUCCEEDED
- ⬜ `python -m promptbim gui` 獨立啟動仍正常
- ⬜ `python -m promptbim check --ai` 通過
- ⬜ git tag: `git tag -a v1.4.0 -m "P12: Quality fixes + Performance + Demo prep"`
- ⬜ iMessage 通知已發送

---

## 驗收標準

1. **PythonBridge 單一實例** — App 生命週期中只有一個 bridge 物件
2. **進程清理** — Cmd+Q 後無殘留 Python 進程
3. **啟動速度** — `--version` < 1s, `check` < 10s, `check --ai` < 20s
4. **Pipeline 效能** — 完整生成 pipeline (with mock) < 5 秒
5. **MacBook 相容** — 小寫路徑可讀 .env
6. **文件一致** — 所有版本號對齊 v1.4.0
7. **Demo 腳本** — DEMO_SCRIPT.md 涵蓋 8 場景
8. **向下相容** — `python -m promptbim gui` 獨立啟動正常
9. **所有測試通過** + xcodebuild BUILD SUCCEEDED + git tag v1.4.0

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
**執行順序: Part A (T1-5) → Part B (T6-8) → Part C (T9-10) → Part D (T11)**
使用 P10.2 的 debug.py logger，不要用 print()。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
