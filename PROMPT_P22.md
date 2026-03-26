# PROMPT_P22.md — Senior Audit Full Remediation

> **Sprint:** P22 | **目標版本:** v2.9.0 | **基於:** AuditReport_03261630.md
> **CLAUDE.md:** v1.14.1 | **SKILL.md:** v3.2（唯讀）
> **前置:** P21 完成（v2.8.0, 957 tests, HEAD `fa5a64fc`）
> **範圍:** 5 Critical + 8 High + 12 Medium + 5 Finalization = **30 Tasks / 5 Parts**

---

## 必讀文件

```
1. 本文件 PROMPT_P22.md ← 最重要
2. docs/reports/AuditReport_03261630.md ← 審計報告（所有 issue ID 來源）
3. SKILL.md ← 專案 SSOT（唯讀，不得修改）
4. CLAUDE.md ← v1.14.1 行為規範（絕對不得修改）
5. TODO.md ← 確認當前狀態
```

---

## 環境檢查（Sprint 開始前必須執行）

```bash
echo "========================================"
echo "🖥️  環境檢查 — $(hostname)"
echo "========================================"
echo "Hostname: $(hostname)"
echo "macOS: $(sw_vers -productVersion)"
echo "Git: $(git --version 2>/dev/null || echo '❌')"
echo "Xcode: $(xcodebuild -version 2>/dev/null | head -1 || echo '❌')"
echo "Python: $(python3 --version 2>/dev/null || echo '❌')"
echo "Conda: $(conda --version 2>/dev/null || echo '❌')"

# ★ API Key 衝突檢查 ★
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "⛔ ANTHROPIC_API_KEY 已設定！會走 API 計費而非 Max 訂閱"
    echo "🔧 修復: unset ANTHROPIC_API_KEY"
    MSG="⛔ PromptBIM Sprint 中止 — 偵測到 ANTHROPIC_API_KEY 環境變數
❗ 這會走 API 計費（$/token）而非 Claude Max 訂閱
🔧 修復: unset ANTHROPIC_API_KEY
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
    echo "$MSG"
    notify "$MSG"
    exit 1
fi
echo "✅ 認證: Claude Max 訂閱（無 API Key 衝突）"

git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then echo "✅ 本地與遠端同步"
else echo "⚠️ 執行 git pull..."; git pull origin main; fi
```

---

## ★ 啟動通知（必須在 Part A 之前執行）★

> ⚠️ 讀完必讀文件 + 環境檢查後，**第一個動作**必須是發送啟動 iMessage。

```bash
MSG="🏗️ PromptBIM Sprint P22 啟動
📋 Senior Audit Full Remediation
🎯 30 Tasks / 5 Parts → v2.9.0
📊 修復: 5 Critical + 8 High + 12 Medium + 5 Final
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part A: C++ Critical + Robustness Fixes（7 Tasks）

> 修復 IFC 線程安全（IFC-01, IFC-02）、輸入驗證（IFC-03, IFC-04）、CMake 強化（CMAKE-01~03）、GIS 修復（GIS-01, GIS-02, GIS-03）

### Task 1: IFC Generator 線程安全 [CRITICAL: IFC-01 + IFC-02]

**IFC-01:** `ifc_generator.cpp` 中 `gmtime()` 回傳 static buffer，非 thread-safe。
- 替換為 `gmtime_r()`（POSIX）或 `gmtime_s()`（Windows），用 `#ifdef` 分平台

**IFC-02:** `IFCGenerator` 有 `next_id_` + `entities_` 成員狀態，並行呼叫會損壞。
- 方案 A（推薦）：加 `std::mutex` 保護 `generate_ifc_string()` 整體
- 方案 B：改為每次呼叫建立新實例（thread-local pattern）

**修改檔案:** `libpromptbim/src/bim/ifc_generator.cpp`, `libpromptbim/include/promptbim/ifc_generator.hpp`

### Task 2: IFC 輸入驗證 + 溢位保護 [MEDIUM: IFC-03 + IFC-04]

**IFC-03:** `next_id_` 無整數溢位保護。加 `if (next_id_ >= INT32_MAX) throw`。

**IFC-04:** 座標無 NaN/infinity 驗證。在 `add_wall()`, `add_slab()` 入口加 `std::isfinite()` 檢查，不合格 throw `std::invalid_argument`。

**修改檔案:** `libpromptbim/src/bim/ifc_generator.cpp`

### Task 3: CMake Build Hardening [MEDIUM: CMAKE-01 + CMAKE-02 + CMAKE-03]

**CMAKE-01:** 加編譯器安全旗標
```cmake
target_compile_options(promptbim PRIVATE
    -fstack-protector-strong
    -D_FORTIFY_SOURCE=2
    -Wformat -Wformat-security)
```

**CMAKE-02:** 加 symbol visibility 控制
```cmake
set(CMAKE_C_VISIBILITY_PRESET hidden)
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)
```

**CMAKE-03:** 加 sanitizer 開發模式
```cmake
option(ENABLE_SANITIZERS "Enable ASan/UBSan" OFF)
if(ENABLE_SANITIZERS)
    target_compile_options(promptbim PRIVATE -fsanitize=address,undefined)
    target_link_options(promptbim PRIVATE -fsanitize=address,undefined)
endif()
```

**修改檔案:** `libpromptbim/CMakeLists.txt`

### Task 4: GIS Non-Convex Setback Fix [MEDIUM: GIS-01]

**問題:** 以重心收縮 (centroid-relative shrinking) 計算 setback，遇非凸多邊形會自交。
**修復:** 實作 Minkowski offset 近似（沿每條邊法線方向平移 → 重新計算交點），或在 setback 前檢測凸性，非凸時回傳 error + 原多邊形。

**修改檔案:** `libpromptbim/src/gis/gis_engine.cpp`

### Task 5: GIS DXF + Shapefile Parser 增強 [MEDIUM: GIS-02 + GIS-03 + P21 技術債]

**GIS-02:** DXF 目前只讀 LWPOLYLINE，增加 POLYLINE + ARC + CIRCLE entity 解析。
**GIS-03:** DXF 增加 Z 座標 (code 30) 讀取支援。
**P21 技術債:** Shapefile parser 只讀第一個 polygon → 改為讀取所有 polygon，回傳 vector。

**修改檔案:** `libpromptbim/src/gis/gis_engine.cpp`, `libpromptbim/include/promptbim/gis_engine.hpp`

### Task 6: C++ 新增 GoogleTest [ALL C++ FIXES]

為 Task 1-5 的所有修改新增 GoogleTest：
- IFC 線程安全測試：`std::thread` 並行 generate 不 crash
- IFC NaN/infinity 輸入 → 預期 throw
- IFC ID 溢位邊界測試
- GIS non-convex setback 測試（L-shape, U-shape）
- GIS DXF POLYLINE + ARC 解析測試
- GIS Shapefile 多 polygon 測試

**目標:** 新增 ≥ 15 GoogleTest cases（137 → ≥ 152）

### Task 7: NativeBIMBridge dlsym Null Check [CRITICAL: SW-05]

**問題:** `NativeBIMBridge.swift` 的 `dlsym()` 回傳值未做 null check，`unsafeBitCast(nil)` 是 undefined behavior。

**修復:** 每個 `dlsym()` 呼叫後加 `guard let` 或 `if sym == nil { ... return }`。

**同時修復 SW-06:** 加入 C++ library 版本檢查函數：
- C++ 端新增 `pb_version()` 回傳版本字串
- Swift 端載入後呼叫 `pb_version()` 比對，不一致則 log 警告

**修改檔案:** `PromptBIMTestApp1/NativeBIMBridge.swift`, `libpromptbim/include/promptbim/promptbim.h`, `libpromptbim/src/` (add version function)

> ⚠️ **NativeBIMBridge.swift 已在 pbxproj 中，無需新增。如有新增 Swift 檔案，必須加入 Compile Sources build phase。**

### Part A 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part A ✅
🔧 C++ Critical + Robustness (7 tasks)
✅ IFC thread safety (mutex + gmtime_r)
✅ IFC input validation (NaN/overflow)
✅ CMake hardening (ASan/UBSan/visibility)
✅ GIS non-convex setback + DXF/SHP parser
✅ NativeBIMBridge dlsym null check + version
✅ GoogleTest ≥ 152
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part B: Python Critical + High Fixes（8 Tasks）

> 修復 Cache race condition（CACHE-01）、Orchestrator DI + async（PY-01, PY-02）、API validation（PY-03, PY-04, CFG-01）、Cost validation（COST-01）、MEP extensibility（MEP-01, MEP-02）

### Task 8: Cache Store File Locking [CRITICAL: CACHE-01]

**問題:** `cache/store.py` 的 `put()` 無 file locking，SwiftUI host 並行呼叫會 race condition。
**修復:** 使用 `fcntl.flock()` 加排他鎖：
```python
import fcntl
with open(lock_path, 'w') as lock_file:
    fcntl.flock(lock_file, fcntl.LOCK_EX)
    # write cache file
    fcntl.flock(lock_file, fcntl.LOCK_UN)
```

**修改檔案:** `src/promptbim/cache/store.py`

### Task 9: Orchestrator Dependency Injection [HIGH: PY-01]

**問題:** Orchestrator 內部建立 agents，無法注入 mock 測試。
**修復:** Constructor 接受 optional agent 參數：
```python
def __init__(self, enhancer=None, planner=None, checker=None, builder=None, ...):
    self._enhancer = enhancer or EnhancerAgent()
    ...
```

**修改檔案:** `src/promptbim/agents/orchestrator.py`

### Task 10: Async Builder Non-Blocking [HIGH: PY-02]

**問題:** `agenerate()` 內 `_builder.build()` 是同步呼叫，會凍結 SwiftUI thread。
**修復:**
```python
self.build_result = await asyncio.to_thread(self._builder.build, self.plan)
```

**修改檔案:** `src/promptbim/agents/orchestrator.py`

### Task 11: Orchestrator Constraint Dedup + API Key Early Validation [MEDIUM: PY-03 + PY-04]

**PY-03:** 迭代修正迴圈中 constraints 重複堆疊。修正：在加入新 constraint 前做去重（set 比對 description）。

**PY-04:** `BaseAgent.__init__()` 中直接驗證 API key，而非延遲到 property getter。失敗時 raise `ValueError`。

**修改檔案:** `src/promptbim/agents/orchestrator.py`, `src/promptbim/agents/base.py`

### Task 12: Config validate_api_key Fix [MEDIUM: CFG-01]

**問題:** `validate_api_key()` 對空字串回傳 True — 誤導。
**修復:** 空字串或 None → 回傳 False。

**修改檔案:** `src/promptbim/config.py`

### Task 13: Cost Estimator Missing Category Error [HIGH: COST-01]

**問題:** QTO category 在 price mapping 中不存在時被 silently skipped — 資料遺失。
**修復:** 改為 log warning + 在結果中標記 `unpriced_categories` 清單，讓上層可察覺。

**修改檔案:** `src/promptbim/bim/cost/estimator.py`

### Task 14: MEP Configurable Grid + System Registry [HIGH: MEP-01 + MEP-02]

**MEP-01:** Grid size 0.3m 硬編碼。改為 constructor 參數 `grid_size: float = 0.3`，並根據建築 span 自動調整（span > 50m → 0.5m, span > 100m → 1.0m）。

**MEP-02:** 新增 `MEPSystemRegistry` class：
```python
class MEPSystemRegistry:
    _systems: dict[str, MEPSystemDef] = {}
    @classmethod
    def register(cls, name, system_def): ...
    @classmethod
    def get(cls, name): ...
```
將現有 4 系統從 `systems.py` 重構為 registry 模式。新增 MEP system 只需 1 行 `register()` 呼叫。

**修改檔案:** `src/promptbim/bim/mep/pathfinder.py`, `src/promptbim/bim/mep/systems.py`（新增 `registry.py` 如需要）

### Task 15: Python Tests for Part B

為 Task 8-14 新增 pytest：
- Cache file locking 並行寫入測試（`threading.Thread`）
- Orchestrator DI mock agent 測試
- Async builder non-blocking 驗證
- Constraint dedup 測試
- Empty API key → False 測試
- Cost missing category warning 測試
- MEP grid auto-adjust 測試
- MEP system registry CRUD 測試

**目標:** 新增 ≥ 20 pytest cases（820 → ≥ 840）

### Part B 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part B ✅
🐍 Python Critical + High (8 tasks)
✅ Cache file locking (fcntl)
✅ Orchestrator DI + async non-blocking
✅ Constraint dedup + API key validation
✅ Cost missing category warning
✅ MEP configurable grid + system registry
✅ pytest ≥ 840
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part C: Swift Fixes + XCTest [CRITICAL: SW-07]（5 Tasks）

> 修復 PythonBridge 問題（SW-01~04）、建立 XCTest 套件（SW-07）、BIMSceneBuilder 一致性修復

### Task 16: PythonBridge Subprocess Timeout + Termination Pairing [HIGH: SW-01 + SW-02]

**SW-01:** `process.waitUntilExit()` 無 timeout。改用 `DispatchQueue.global().asyncAfter` 設定 30 秒 timeout，超時 `process.terminate()`。

**SW-02:** `disableSuddenTermination()` / `enableSuddenTermination()` 在 early dealloc 時不成對。使用 defer pattern 或在 deinit 中確保 enable 被呼叫。

**修改檔案:** `PromptBIMTestApp1/PythonBridge.swift`

### Task 17: PythonBridge Stderr Separation + Path Robustness [MEDIUM: SW-03 + SW-04]

**SW-03:** stdout + stderr 混入同一 pipe。分別建立 `standardOutput` 和 `standardError` 的 Pipe，stderr 走 warning log。

**SW-04:** 路徑偵測使用 6 層向上遍歷 + 硬編碼。改用 `Bundle.main.resourcePath` 或 `FileManager.default.currentDirectoryPath` 為基點，最多向上 3 層。

**修改檔案:** `PromptBIMTestApp1/PythonBridge.swift`

### Task 18: BIMSceneBuilder.swift 獨立檔案 [Context Prompt 不一致修復]

**問題:** Context Prompt v3.0 列出 `BIMSceneBuilder.swift` 為獨立檔案，但 repo 中該邏輯被合併在 `SceneKitView.swift` 或 `NativeBIMBridge.swift` 中。

**修復:** 從 SceneKitView.swift 中提取 `BIMSceneBuilder` class 為獨立檔案 `PromptBIMTestApp1/BIMSceneBuilder.swift`。

> ⚠️ **新增 Swift 檔案必須加入 pbxproj Compile Sources build phase！**
> 執行 `xcodebuild` 前確認 BIMSceneBuilder.swift 已在 project.pbxproj 中。

**新增檔案:** `PromptBIMTestApp1/BIMSceneBuilder.swift`
**修改檔案:** `PromptBIMTestApp1/SceneKitView.swift`（移除提取出的程式碼）

### Task 19: Cross-Layer Error Propagation [MEDIUM: Audit Section 5.3]

**問題:** C++ exception → empty string → Swift nil → generic log，錯誤資訊全部遺失。

**修復:** 定義 C ABI error result struct：
```c
// promptbim.h
typedef struct {
    int code;           // 0 = success, nonzero = error
    const char* data;   // success: result string, error: error message
} PBResult;
```

更新 Swift bridge 讀取 error code + message，log 具體錯誤。
更新 C++ 端 catch 區塊填入 `PBResult` 而非回傳 empty string。

**修改檔案:** `libpromptbim/include/promptbim/promptbim.h`, C++ engine files (wrap returns), `PromptBIMTestApp1/NativeBIMBridge.swift`

### Task 20: Swift XCTest Suite [CRITICAL: SW-07]

**問題:** 全部 5（→6）個 Swift 檔案零 XCTest 覆蓋。

**建立:** `PromptBIMTestApp1Tests/` 目錄 + XCTest target：
- `PythonBridgeTests.swift` — conda 路徑偵測、.env 載入、version 讀取
- `NativeBIMBridgeTests.swift` — dlopen fallback、dlsym null 處理、PBResult 解析
- `BIMSceneBuilderTests.swift` — JSON → SceneKit node 轉換
- `ContentViewTests.swift` — Tab 切換、版本顯示

> ⚠️ **XCTest target 需加入 xcodeproj。** 如果 xcodeproj 中尚無 test target，需建立 Unit Test bundle target，並將測試檔加入 Compile Sources。用 `xcodebuild test` 驗證。

**目標:** ≥ 15 XCTest cases

**新增檔案:** `PromptBIMTestApp1Tests/*.swift`

### Part C 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part C ✅
🍎 Swift Fixes + XCTest (5 tasks)
✅ PythonBridge timeout + termination + stderr
✅ BIMSceneBuilder.swift extracted (6 Swift files)
✅ Cross-layer PBResult error propagation
✅ XCTest suite ≥ 15 cases
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part D: Medium Priority Subsystem Fixes（5 Tasks）

> 修復 Monitoring（MON-01）、Simulation（SIM-01）、Orchestrator 封裝（PY-05, PY-06）、pybind11 type stubs、Plugin 系統活化（PLG-01）

### Task 21: Monitoring Sensor-Space Validation [MEDIUM: MON-01]

**問題:** 停車場感測器可被放在臥室 — 無 sensor-to-space type 驗證。
**修復:** 在 `auto_placement.py` 加入 `valid_space_types` 映射表，placement 前檢查 sensor 是否適用於該 space type。不合格 log warning + skip。

**修改檔案:** `src/promptbim/bim/monitoring/auto_placement.py`

### Task 22: Simulation Enum-Based Classification [MEDIUM: SIM-01]

**問題:** Component 分類用 string matching（如 `"wall_exterior_frame"`），容易錯分。
**修復:** 建立 `ComponentCategory` Enum，mapping table 取代 string 比對。

**修改檔案:** `src/promptbim/bim/simulation/scheduler.py`

### Task 23: Orchestrator Encapsulation + Callback Typing [LOW: PY-05 + PY-06]

**PY-05:** `on_status` callback 加型別標註 `Callable[[PipelineStatus], None]`。
**PY-06:** 將 `requirement`, `plan`, `build_result` 改為 property（getter only），移除直接屬性暴露。

**修改檔案:** `src/promptbim/agents/orchestrator.py`

### Task 24: pybind11 .pyi Type Stubs [MEDIUM: Audit Section 3.3]

**問題:** pybind11 module `_native` 無 `.pyi` stub，IDE 無法提供自動完成。
**修復:** 建立 `src/promptbim/codes/_native.pyi`，覆蓋所有 pybind11 暴露的 class + function 簽章。

**新增檔案:** `src/promptbim/codes/_native.pyi`

### Task 25: Plugin System Activation for Building Codes [HIGH: PLG-01]

**問題:** Plugin 架構在 P17 建立但**完全未使用** — building code rules 仍硬編碼在 `codes/registry.py`。
**修復:** 
1. 將 15 條 Taiwan building code rules 包裝為 `TaiwanBuildingCodePlugin`
2. 在 `codes/registry.py` 改為透過 plugin system 載入
3. 保持向下相容（預設啟用 TW plugin）
4. 新增地區只需建立新 plugin class

**修改檔案:** `src/promptbim/codes/registry.py`, `src/promptbim/plugins/` (new plugin file)

### Part D 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part D ✅
🔌 Subsystem Fixes (5 tasks)
✅ Monitoring sensor-space validation
✅ Simulation enum classification
✅ Orchestrator encapsulation
✅ pybind11 .pyi type stubs
✅ Plugin system activated for building codes
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part E: Build Verification + Documentation + Finalization（5 Tasks）

### Task 26: Context Prompt Update

更新 `docs/PromptBIM_Context_Prompt.md`：
- Swift 源碼表：6 檔案（加入 BIMSceneBuilder.swift）
- P22 加入已完成 Sprint 表
- 版本 v2.9.0
- 測試數更新
- 修正任何與 repo 不一致的描述

**修改檔案:** `docs/PromptBIM_Context_Prompt.md`

### Task 27: Full Document Sync（8 項逐一驗證）

```
☐ TODO.md — P22 ✅ + v2.9.0 + 所有 tasks 列表
☐ CHANGELOG.md — v2.9.0 條目（列出所有修復的 issue ID）
☐ README.md — 測試數 + v2.9.0
☐ docs/PromptBIM_Context_Prompt.md — Sprint P22 + v2.9.0 + 測試數
☐ pyproject.toml — version = "2.9.0"
☐ src/promptbim/__init__.py — __version__ = "2.9.0"
☐ Info.plist — CFBundleShortVersionString = "2.9.0", CFBundleVersion = "22"
☐ SKILL.md — 唯讀，不修改（但審計中評估是否需要人工更新）
```

### Task 28: Build + Test Verification

```bash
# C++ GoogleTest
cd libpromptbim && mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release && make -j$(sysctl -n hw.ncpu) && ctest --output-on-failure
# 目標: ≥ 152 passed

# Python pytest
cd ~/Documents/MyProjects/PromptBIMTestApp1
conda activate promptbim
python -m pytest tests/ -x -q
# 目標: ≥ 840 passed

# Xcode build
xcodebuild -project PromptBIMTestApp1.xcodeproj -scheme PromptBIMTestApp1 build
# 必須: BUILD SUCCEEDED

# Xcode test (if test target exists)
xcodebuild -project PromptBIMTestApp1.xcodeproj -scheme PromptBIMTestApp1 test 2>/dev/null || echo "XCTest target 需要手動設定"
```

### Task 29: Self-Audit Report

產生 `docs/reports/Sprint22_AuditReport.md`，包含：

**A. 代碼品質審計**
- 新增/修改檔案列表（含行數）
- 每個 audit issue 修復狀態（ID + ✅/❌）
- 新測試數（GoogleTest + pytest + XCTest）
- 殘留技術債

**B. 文檔完整性審計（8/8）**

**C. Xcode pbxproj 完整性審計（8/8）**
```
☐ xcodebuild BUILD SUCCEEDED
☐ 所有 .swift 在 pbxproj（6 files: App, ContentView, PythonBridge, SceneKitView, NativeBIMBridge, BIMSceneBuilder）
☐ Info.plist CFBundleVersion = 22
☐ Info.plist CFBundleShortVersionString = 2.9.0
☐ NSSupportsAutomaticTermination = false
☐ NSSupportsSuddenTermination = false
☐ Signing: ad-hoc (CODE_SIGN_IDENTITY = "-")
☐ Bundle ID = com.realitymatrix.PromptBIMTestApp1
```

**D. 綜合評分**

### Task 30: Git Commit + Push + Tag

```bash
git add -A
git commit -m "[P22] Senior Audit Full Remediation — 30 fixes, v2.9.0

Part A: C++ Critical + Robustness (IFC thread safety, CMake hardening, GIS fixes)
Part B: Python Critical + High (Cache locking, Orchestrator DI/async, MEP registry)
Part C: Swift Fixes + XCTest (subprocess timeout, BIMSceneBuilder, PBResult, 15+ XCTests)
Part D: Subsystem Fixes (sensor validation, enum classification, plugin activation)
Part E: Documentation + Build Verification

Fixes: IFC-01, IFC-02, IFC-03, IFC-04, CACHE-01, SW-01~07, PY-01~06,
       MEP-01, MEP-02, COST-01, CFG-01, GIS-01, GIS-02, GIS-03,
       CMAKE-01~03, MON-01, SIM-01, PLG-01 + PBResult error propagation

Tests: pytest ≥840 + GoogleTest ≥152 + XCTest ≥15 = ≥1007 total
Audit: Code + Docs 8/8 + Xcode 8/8

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"

git push origin main
git tag -a v2.9.0 -m "v2.9.0 — Senior Audit Full Remediation (P22)"
git push origin v2.9.0
```

### Part E 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part E ✅
📦 Finalization (5 tasks)
✅ Context Prompt updated (6 Swift files)
✅ Full doc sync 8/8
✅ Build: GoogleTest ≥152 + pytest ≥840 + XCTest ≥15
✅ Audit report generated
✅ Git pushed + tagged v2.9.0
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## 執行指令

> ⚠️ 以下規則在整個 Sprint 期間有效，不可忽略。

1. **全量文件同步：** Task 27 列出的 8 項必須逐一驗證
2. **pbxproj 完整性：** 6 個 Swift 檔案（含新增的 BIMSceneBuilder.swift）都必須在 Compile Sources 中
3. **iMessage 通知：** 啟動 + 每個 Part + 審計 + Git + 最終 = 至少 8 次 notify
4. **所有 notify 必須搭配 echo**
5. **自我審計：** 必須產生 Sprint22_AuditReport.md（代碼 + 文檔 8/8 + Xcode 8/8）
6. **不得修改 CLAUDE.md** — 絕對禁止（P18 違規已記錄）
7. **不得修改 SKILL.md** — 唯讀
8. **不得中途詢問用戶** — 所有決策自行判斷
9. **遇到錯誤自行修復** — 嘗試 3 次仍失敗才發送中斷通知
10. **新增 Swift 檔案（BIMSceneBuilder.swift + XCTest files）必須加入 pbxproj**

---

## 驗收標準

```
☐ xcodebuild BUILD SUCCEEDED
☐ Xcode pbxproj 完整性 8/8（含 BIMSceneBuilder.swift）
☐ GoogleTest ≥ 152 passed
☐ pytest ≥ 840 passed
☐ XCTest ≥ 15 passed（如 test target 可建立）
☐ 全部 5 Critical issues 修復（IFC-01, IFC-02, CACHE-01, SW-05, SW-07）
☐ 全部 8 High issues 修復（PY-01, PY-02, MEP-01, MEP-02, COST-01, PLG-01, SW-01, SW-02）
☐ Info.plist: CFBundleShortVersionString = "2.9.0", CFBundleVersion = "22"
☐ 6 處版本一致（pyproject + __init__ + Info.plist + README + TODO + Context Prompt）
☐ Sprint22_AuditReport.md 產生（代碼 + 文檔 8/8 + Xcode 8/8）
☐ git tag v2.9.0 已推送
☐ iMessage 已發送（啟動 + 5 Parts + Git + 最終）
```

---

## Issue 完整追蹤表

| ID | Severity | Part | Task | Issue |
|----|----------|------|------|-------|
| IFC-01 | **CRITICAL** | A | 1 | gmtime() thread-unsafe |
| IFC-02 | **CRITICAL** | A | 1 | Stateful generator, no mutex |
| CACHE-01 | **CRITICAL** | B | 8 | No file locking |
| SW-05 | **CRITICAL** | A | 7 | dlsym() not null-checked |
| SW-07 | **CRITICAL** | C | 20 | Zero Swift unit tests |
| PY-01 | HIGH | B | 9 | Orchestrator no DI |
| PY-02 | HIGH | B | 10 | Async builder blocks |
| MEP-01 | HIGH | B | 14 | Hardcoded grid 0.3m |
| MEP-02 | HIGH | B | 14 | No MEP system registry |
| COST-01 | HIGH | B | 13 | Silent skip missing price |
| PLG-01 | HIGH | D | 25 | Plugin system unused |
| SW-01 | HIGH | C | 16 | No subprocess timeout |
| SW-02 | HIGH | C | 16 | Unpaired termination calls |
| IFC-03 | MEDIUM | A | 2 | No integer overflow protection |
| IFC-04 | MEDIUM | A | 2 | NaN/infinity accepted |
| CMAKE-01 | MEDIUM | A | 3 | No compiler hardening |
| CMAKE-02 | MEDIUM | A | 3 | No symbol visibility |
| CMAKE-03 | MEDIUM | A | 3 | No sanitizer support |
| GIS-01 | MEDIUM | A | 4 | Centroid setback non-convex fail |
| GIS-02 | MEDIUM | A | 5 | DXF limited to LWPOLYLINE |
| GIS-03 | MEDIUM | A | 5 | No Z-coordinate in DXF |
| PY-03 | MEDIUM | B | 11 | Constraint deduplication |
| PY-04 | MEDIUM | B | 11 | Late API key validation |
| CFG-01 | MEDIUM | B | 12 | validate_api_key True for empty |
| SW-03 | MEDIUM | C | 17 | stdout/stderr mixed |
| SW-04 | MEDIUM | C | 17 | Fragile path detection |
| SW-06 | MEDIUM | A | 7 | No version check |
| MON-01 | MEDIUM | D | 21 | No sensor-space validation |
| SIM-01 | MEDIUM | D | 22 | String-based classification |
| PY-05 | LOW | D | 23 | on_status not typed |
| PY-06 | LOW | D | 23 | Leaky abstraction |

---

*PROMPT_P22.md v1.0 | 2026-03-26 | Generated by Senior Architect Review*
*CLAUDE.md v1.14.1 合規性檢查: ✅ 通過*
