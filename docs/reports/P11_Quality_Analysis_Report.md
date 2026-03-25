# PromptBIMTestApp1 — Sprint P11 品質分析報告

> 分析師: Claude Opus 4.6 (資深軟體品質與架構分析師)
> 日期: 2026-03-26
> Sprint: P11 (Xcode ↔ PySide6 GUI Integration + E2E)
> Commit: ac45f03 ([P11] Complete Xcode ↔ PySide6 GUI integration + E2E testing)

---

## 1. 執行摘要

Sprint P11 的核心目標是解決 Xcode SwiftUI 空殼問題，讓 `Cmd+R` 能自動啟動完整功能的 PySide6 GUI。程式碼已提交至 main branch，CHANGELOG 已更新至 v1.3.0，TODO.md 中 P11 所有 task 已標記完成（668 tests passed, xcodebuild BUILD SUCCEEDED）。

**總體評價: 功能基本達標，但存在 3 個需立即修復的架構問題。**

---

## 2. 分析範圍

| 類別 | 檔案 | 分析重點 |
|------|------|----------|
| Swift UI 層 | `PromptBIMTestApp1App.swift` | App 生命週期管理 |
| Swift UI 層 | `ContentView.swift` | Splash Screen + 狀態顯示 |
| Swift Bridge | `PythonBridge.swift` | Python 偵測 + GUI 啟動 + .env |
| Python Config | `config.py` | .env 多路徑搜尋 |
| Python E2E | `test_e2e_integration.py` | 23 項 E2E 測試 |
| Xcode Config | `Info.plist` / `Entitlements` | 文件類型 + 沙盒 |
| 文件 | CHANGELOG / TODO / Context Prompt | 一致性與完整性 |

---

## 3. 發現問題

### 3.1 🔴 Critical — 必須立即修復

#### C1: PythonBridge 雙實例問題

**位置:** `PromptBIMTestApp1App.swift` + `ContentView.swift`

**問題:** App 和 ContentView 各自創建獨立的 `PythonBridge()` 實例：

```swift
// PromptBIMTestApp1App.swift
@StateObject private var bridge = PythonBridge()  // 實例 #1（未使用）

// ContentView.swift
@StateObject private var bridge = PythonBridge()  // 實例 #2（實際使用）
```

**影響:**
- 兩個 PythonBridge 同時執行 `checkPython()`，浪費系統資源
- App 層的 bridge 從未傳遞給 ContentView，違反 Single Source of Truth
- 如果 App 層加入生命週期管理（如 P11 Task 3 要求的 terminateGUI），會操作錯誤的 bridge 實例

**建議修復:**
```swift
// PromptBIMTestApp1App.swift
@StateObject private var bridge = PythonBridge()
var body: some Scene {
    WindowGroup {
        ContentView(bridge: bridge)  // 注入同一實例
    }
}

// ContentView.swift
@ObservedObject var bridge: PythonBridge  // 接收注入，不再自行建立
```

---

#### C2: App 關閉時未終止 Python Process

**位置:** `PromptBIMTestApp1App.swift`

**問題:** P11 PROMPT 明確要求 Task 3：「App 關閉時終止 Python process + 處理 Python process crash/exit 的狀態」，但目前 App.swift 中**完全沒有**生命週期管理程式碼。

**影響:**
- 關閉 Xcode App 後，PySide6 GUI 的 Python process 會變成孤兒進程（zombie process）
- 每次 Cmd+R 都會累積一個 Python 進程，最終耗盡系統記憶體

**建議修復:**
```swift
@main
struct PromptBIMTestApp1App: App {
    @StateObject private var bridge = PythonBridge()
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            ContentView(bridge: bridge)
        }
        .onChange(of: scenePhase) { _, newPhase in
            if newPhase == .background {
                bridge.terminateGUI()
            }
        }
    }
    
    init() {
        // 監聽 App 終止事件
        NSApplication.shared.publisher(for: \.isTerminated)
            ... bridge.terminateGUI()
    }
}
```

---

#### C3: NSSupportsSuddenTermination 與進程管理衝突

**位置:** `Info.plist`

**問題:**
```xml
<key>NSSupportsAutomaticTermination</key>
<true/>
<key>NSSupportsSuddenTermination</key>
<true/>
```

`NSSupportsSuddenTermination = true` 允許 macOS 在不發送任何通知的情況下直接殺掉 App。這意味著即使實作了 App termination handler，也可能永遠不會被調用。

**影響:** Python GUI 進程幾乎**一定**會變成孤兒進程。

**建議修復:** 將兩項都改為 `false`，或在啟動 GUI 時呼叫 `ProcessInfo.processInfo.disableSuddenTermination()`。

---

### 3.2 🟡 Medium — 建議在 P12 修復

#### M1: MacBook 小寫路徑未覆蓋

**位置:** `config.py` + `PythonBridge.swift`

Context Prompt 明確記載 MacBook 路徑為 `~/documents/myprojects/PromptBIMTestApp1`（小寫），但：
- `config.py._find_env_file()` 只有大寫路徑
- `PythonBridge.findProjectRoot()` 只有大寫路徑

**影響:** 在 MacBook 上 Cmd+R 可能找不到 .env 和專案根目錄。

**建議:** 加入 `~/documents/myprojects/PromptBIMTestApp1` 到兩處搜尋清單。

---

#### M2: CHANGELOG 版本表未更新

**位置:** `CHANGELOG.md` 底部「版本對照表」

表格最後一列仍為：
```
| 1.0.0 | 全部完成 | POC 完整版 |
```
缺少 P10.2 / P10.3 / P11 三個版本的對照行。

---

#### M3: Context Prompt 仍描述 P11 為「待執行」

**位置:** `docs/PromptBIM_Context_Prompt.md`

文件仍然寫著：
- 「P11（Xcode↔PySide6 整合）PROMPT 已建立，待執行」
- Swift 源碼尺寸仍列為原始值（229B / 2649B / 2688B）

---

#### M4: TODO.md 版本標頭過時

`TODO.md` 頂部寫 `版本: v1.1.0` 但實際已是 v1.3.0。

---

#### M5: process.launch() 已棄用

**位置:** `PythonBridge.swift` 中的 `runCommand()` 和 `generateBuilding()`

`launchPySide6GUI()` 正確使用了 `try process.run()`，但 `runCommand()` 仍使用已棄用的 `process.launch()`。應統一改為 `try process.run()`。

---

### 3.3 🟢 Low — 可在後續迭代處理

#### L1: E2E 測試全為 Mock，缺少真實整合路徑

23 項 E2E 測試全部使用 `unittest.mock.patch` 模擬 AI Agent 回應。這對 CI 友善，但缺少一組標記為 `@pytest.mark.integration` 的真實 API 測試（可設為 opt-in）。

#### L2: 缺少 v1.3.0 git tag

最近的 git tag 是 v1.0.0，P11 完成後未打 v1.3.0 tag。

#### L3: pyproject.toml 版本可能過時

未檢查 `pyproject.toml` 中的 version 欄位是否與 CHANGELOG 一致。

#### L4: PythonBridge pythonPath 與 env PYTHONPATH 變數名衝突

`launchPySide6GUI()` 中：
```swift
let pythonPath = projectRoot.appendingPathComponent("src").path  // 區域變數
```
此名稱與 class property `self.pythonPath`（conda Python 路徑）相同，造成混淆。建議改名為 `srcPath`。

---

## 4. 架構評估

### 4.1 雙 GUI 架構（SwiftUI + PySide6）

**設計意圖:** SwiftUI 作為 macOS native 啟動器 (splash screen)，PySide6 作為功能完整的 GUI。

**評價:** 這是一個合理的 POC 架構。SwiftUI 提供 native macOS 體驗（dock icon、app lifecycle），PySide6 提供跨平台功能完整性。但長期來看，維護兩個 UI 層會增加複雜度。

### 4.2 Python 後端架構（14 子模組）

**結構:** agents / bim / codes / gui / land / startup / mcp / web / viz / voice + schemas / config / debug

**評價:** 模組化良好，職責分明。Agent pipeline（enhancer → planner → builder → checker → modifier）遵循 Chain of Responsibility 模式，orchestrator 負責編排。Pydantic schemas 作為跨模組的資料契約。

### 4.3 測試覆蓋

| 類別 | 測試數 | 涵蓋範圍 |
|------|:------:|----------|
| P0 骨架 | 29 | ✅ 結構驗證 |
| P1 土地 | 19 | ✅ 4 格式 + 退縮 + 投影 |
| P2 BIM | 34 | ✅ IFC + USD + 幾何 |
| P2.5 零件 | 18 | ✅ 76 元件 |
| P3 3D | 19 | ✅ 視覺化 |
| P4 Agent | 37 | ✅ 5 Agent |
| P4.5 法規 | 47 | ✅ 15 規則 |
| P4.8 修改 | 24 | ✅ 修改 + 撤銷 |
| P5 語音匯出 | 30 | ✅ STT + SVG |
| P6 成本 | 28 | ✅ QTO + 估算 |
| P7 MEP | 45 | ✅ A* + 碰撞 |
| P8 模擬 | 50 | ✅ 排程 + 動畫 |
| P8.5 監控 | 52 | ✅ 48 類型 |
| P9 影像AI | 76 | ✅ Vision + MCP + Web |
| P10 整合 | 75 | ✅ 效能 + 邊界 |
| P10.2 Debug | 12 | ✅ Logger |
| P10.3 啟動 | 42 | ✅ 12 健檢 |
| P11 E2E | 23 | ⚠️ 全 Mock |
| **總計** | **668** | |

---

## 5. P11 Task 完成度對照

| Task | 規格要求 | 實際完成度 | 評分 |
|------|----------|:----------:|:----:|
| T1 | PythonBridge: findCondaPython + launchPySide6GUI + loadDotEnv | ✅ 完整實作 | 9/10 |
| T2 | ContentView: Splash + 狀態 + 安裝指引 + 重啟 | ✅ 三態 UI | 9/10 |
| T3 | App 生命週期: 自動啟動 + 關閉終止 + crash 處理 | ⚠️ 缺終止邏輯 | 4/10 |
| T4 | .env 多路徑搜尋 | ✅ 已實作 (缺小寫路徑) | 8/10 |
| T5 | PySide6 拖放功能驗證 | ✅ 測試通過 | 8/10 |
| T6 | Chat → Generate 完整流程 | ✅ Mock 驗證通過 | 7/10 |
| T7 | E2E 測試 6 類流程 | ✅ 23 測試 (全 Mock) | 7/10 |
| T8 | Info.plist + pbxproj 更新 | ✅ 完整 | 9/10 |
| T9 | 收尾測試 | ⚠️ 缺 xcodebuild 實測驗證 | 6/10 |

**綜合分數: 7.4 / 10**

---

## 6. 建議修復優先級

| 優先級 | ID | 問題 | Sprint |
|:------:|:--:|------|:------:|
| P0 | C1 | PythonBridge 雙實例 | P12 T1 |
| P0 | C2 | App 關閉未終止 Python | P12 T2 |
| P0 | C3 | SuddenTermination 衝突 | P12 T3 |
| P1 | M1 | MacBook 小寫路徑 | P12 T4 |
| P1 | M2-M4 | 文件版本不一致 | P12 T5 |
| P1 | M5 | process.launch() 棄用 | P12 T6 |
| P2 | L1 | 缺真實整合測試 | P12 T7 |
| P2 | L2-L4 | Tag + 版本 + 變數名 | P12 T8 |

---

## 7. 結論

P11 Sprint 在功能面達成了核心目標：PySide6 GUI 可透過 PythonBridge 從 Xcode 啟動。ContentView 的三態 Splash Screen 設計合理，.env 多路徑搜尋解決了路徑依賴問題，E2E 測試覆蓋了 6 大流程類別。

但在 **App 生命週期管理** 方面存在明顯缺失（C1-C3），將導致 Python 進程洩漏。這些問題在 Sprint P12 中必須優先修復。

---

*報告由 Claude Opus 4.6 自動生成，基於 GitHub 代碼完整審查。*
