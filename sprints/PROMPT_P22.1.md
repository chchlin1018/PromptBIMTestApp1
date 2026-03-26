# PROMPT_P22.1.md — Code Quality + Test Gap + Demo Data

> **Sprint:** P22.1 | **目標版本:** v2.9.1 | **基於:** P22 Senior Code Review + AuditReport_03261820
> **CLAUDE.md:** v1.16.2 | **SKILL.md:** v3.2（唯讀）
> **前置:** P22 完成（v2.9.0, 974 tests）
> **範圍:** 5 Parts / 27 Tasks — 代碼品質 + 測試缺口 + Demo Data + 建構驗證 + 審計推送
> **審查來源:** 資深軟體品質工程師全面代碼審查 (AuditReport_03261820.md)

---

## ★★★ 絕對第一步：定義 notify 函數 + 發送啟動通知 ★★★

```bash
# ===== ★★★ Sprint 絕對第一步：定義 notify 函數 ★★★ =====
notify() {
    local msg="$1"
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"chchlin1018@icloud.com\" of targetService
            send \"$msg\" to targetBuddy
        end tell
    " 2>/dev/null || \
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"+886972535899\" of targetService
            send \"$msg\" to targetBuddy
        end tell
    " 2>/dev/null || \
    osascript -e "display notification \"$msg\" with title \"PromptBIM\"" 2>/dev/null || \
    echo "[NOTIFY FALLBACK] $msg"
}
echo "✅ notify 函數已定義"

TASK_TOTAL=27
PART_TOTAL=5
TASK_DONE=0
PART_DONE=0

MSG="🏗️ PromptBIM Sprint P22.1 啟動
📋 Code Quality + Test Gap + Demo Data
🎯 27 Tasks / 5 Parts → v2.9.1
📊 Part A: 代碼品質 | Part B: 測試 | Part C: Demo Data | Part D: 建構 | Part E: 審計
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## 關鍵文件完整性檢查

```bash
CLAUDE_SIZE=$(wc -c < CLAUDE.md 2>/dev/null | tr -d ' ')
SKILL_SIZE=$(wc -c < SKILL.md 2>/dev/null | tr -d ' ')
if [ "$CLAUDE_SIZE" -lt 5000 ] 2>/dev/null || [ "$SKILL_SIZE" -lt 20000 ] 2>/dev/null; then
    MSG="⛔ 關鍵文件損壞！CLAUDE=${CLAUDE_SIZE}B SKILL=${SKILL_SIZE}B"
    echo "$MSG" && notify "$MSG" && exit 1
fi
echo "✅ 關鍵文件完整"
```

---

## 環境檢查

```bash
echo "========================================"
echo "🖥️  環境檢查 — $(hostname)"
echo "========================================"
if [ -n "$ANTHROPIC_API_KEY" ]; then
    MSG="⛔ PromptBIM Sprint 中止 — 偵測到 ANTHROPIC_API_KEY
🔧 修復: unset ANTHROPIC_API_KEY
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG" && exit 1
fi
echo "✅ 認證: Claude Max 訂閱"
```

---

## 必讀文件

```
1. 本文件 sprints/PROMPT_P22.1.md
2. docs/audit-reports/AuditReport_03261820.md ← 品質審查報告
3. docs/audit-reports/Sprint22_AuditReport.md
4. SKILL.md ← 唯讀，不得修改
5. CLAUDE.md ← v1.16.2，絕對不得修改
```

---

## Part A: 代碼品質修復 — Critical + High (7 Tasks)

### Task 1: Cache `get()` 加入讀取鎖 [QA-01 CRITICAL]

**檔案:** `src/promptbim/cache/store.py`
**修復:** `get()` 中用 `fcntl.LOCK_SH` 共享讀鎖保護讀取。

```bash
TASK_DONE=1
MSG="🏗️ PromptBIM P22.1
✅ Task 1/27: Cache get() LOCK_SH [QA-01]
📊 進度: Task 1/27 | Part 0/5 | 4%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Task 2: Orchestrator `modify()` 修復 `_output_dir` [QA-02 CRITICAL]

**檔案:** `src/promptbim/agents/orchestrator.py`
**修復:** `__init__` 保存 `self._output_dir`。`modify()` 用 `self._output_dir`。

> Task 2/27 | 7%

### Task 3: Orchestrator 封裝性修復 [QA-03 + QA-04 + QA-05]

**修復:** TYPE_CHECKING import CheckResult、屬性改 `_` prefix + `@property`、移除對 builder `_output_dir` 存取。

> Task 3/27 | 11%

### Task 4: Orchestrator DRY 重構 [QA-06]

**修復:** 提取 `_prepare_pipeline()`、`_build_result_obj()`、`_store_cache()` 共用方法。

> Task 4/27 | 15%

### Task 5: PBResult 整合到 NativeBIMBridge [QA-07]

**修復:** `generateIFC`/`generateUSD`/`parseLandGeoJSON` 加入 `PBResult<T>` 回傳版本。

> Task 5/27 | 19%

### Task 6: PythonBridge pipe deadlock 修復 [QA-08]

**修復:** 先讀 pipe data 再等 process exit，避免 buffer 滿導致 deadlock。

> Task 6/27 | 22%

### Task 7: `validate_api_key` 加 `.strip()` [QA-09]

> Task 7/27 | 26%

### Part A 完成通知

```bash
PART_DONE=1
MSG="🏗️ PromptBIM P22.1 Part A ✅
🔧 代碼品質修復 (7 tasks)
✅ Cache lock + Orchestrator 封裝 + DRY + PBResult + Pipe fix
📊 進度: Task 7/27 | Part 1/5 | 26%
⏭️ 下一步: Part B — 測試缺口 (8 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part B: 測試缺口修復 (8 Tasks)

### Task 8: pytest — Cache 併行讀寫測試 (+3 tests)
> Task 8/27 | 30%

### Task 9: pytest — Orchestrator DI 測試 (+4 tests)
> Task 9/27 | 33%

### Task 10: pytest — Orchestrator `modify()` + `_output_dir` (+3 tests)
> Task 10/27 | 37%

### Task 11: pytest — Constraint dedup 測試 (+2 tests)
> Task 11/27 | 41%

### Task 12: pytest — MEP registry + Cost warning (+4 tests)
> Task 12/27 | 44%

### Task 13: pytest — config `validate_api_key` 邊界 (+4 tests)
> Task 13/27 | 48%

### Task 14: GoogleTest — C++ 測試補齊 (+13 tests)

目標: 139 → ≥152。
- IFC `gmtime_r` thread safety (3)
- IFC NaN/infinity validation (3)
- IFC overflow protection (2)
- GIS non-convex setback edge cases (3)
- CMake sanitizer flag (2)

> Task 14/27 | 52%

### Task 15: XCTest — PBResult + 整合測試 (+5 tests)
> Task 15/27 | 56%

### Part B 完成通知

```bash
PART_DONE=2
MSG="🏗️ PromptBIM P22.1 Part B ✅
🧪 測試缺口修復 (8 tasks)
✅ pytest +20 | GoogleTest +13 | XCTest +5
📊 進度: Task 15/27 | Part 2/5 | 56%
⏭️ 下一步: Part C — Demo Data 內建展示資料 (5 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part C: 內建 Demo Data — App 啟動即有展示 (5 Tasks)

> ⚠️ **目標:** App 啟動時不再是空白畫面，而是展示一個完整的範例專案。
> ⚠️ **使用者可以看完展示後，清除並重新用 AI 生成自己的建築。**
> ⚠️ **資料來源: 從現有測試 fixtures + examples/ 提取。**

### Task 16: 建立 Demo Data 模組 `src/promptbim/demo/`

建立 `src/promptbim/demo/__init__.py` + `src/promptbim/demo/sample_project.py`。

包含:
- **Demo 土地:** 台北信義區 600㎡ L 型土地（硬編碼座標）
- **Demo 分區規則:** 住宅區，容積率 2.0，建蔽率 0.6，高度 15m
- **Demo BuildingPlan:** 3 層住宅，含客廳/臥室/廚房/衛浴，BCR=55%, FAR=1.65
- **Demo 成本預算:** NT$ 18,500,000 (包含結構/裝修/MEP)
- **Demo 法規檢查結果:** 全通過

函數:
```python
def get_demo_land() -> LandParcel: ...
def get_demo_zoning() -> ZoningRules: ...
def get_demo_plan() -> BuildingPlan: ...
def get_demo_cost_summary() -> dict: ...
def get_demo_compliance() -> dict: ...
def get_demo_generation_result() -> GenerationResult: ...
```

> Task 16/27 | 59%

### Task 17: Demo IFC + USD 檔案預生成

用 `BuilderAgent.build(demo_plan)` 在 `examples/demo/` 目錄生成:
- `examples/demo/demo_building.ifc`
- `examples/demo/demo_building.usda`
- `examples/demo/demo_floorplan.svg`
- `examples/demo/demo_site_plan.svg`
- `examples/demo/demo_summary.json`

這些檔案隨專案 commit，App 啟動時直接讀取。

> Task 17/27 | 63%

### Task 18: GUI 啟動時載入 Demo Data

**檔案:** `src/promptbim/gui/main_window.py`
**修改:**
- App 啟動時檢查是否有已存的專案，若無則載入 Demo
- 左側專案樹顯示 "Demo Project (台北信義區 3F 住宅)"
- 2D Tab 顯示土地輪廓 + 建築 footprint + 退縮線
- 3D Tab 顯示 PyVista 3D 模型（從 demo .usda 或 .ifc 載入）
- 屬性面板顯示: 面積 330㎡、樓層 3、容積率 1.65、建蔽率 55%、預算 NT$18.5M
- Chat 面板顯示: "歡迎使用 PromptBIM! 這是一個範例專案..."

> Task 18/27 | 67%

### Task 19: 「清除展示」功能

**檔案:** `src/promptbim/gui/main_window.py`
加入 Menu: `File > Clear Demo & Start Fresh` 或 toolbar 按鈕。

功能:
1. 清除左側專案樹
2. 清除 2D/3D 視圖
3. 清除屬性面板
4. Chat 顯示: "已清除展示。請匯入土地或輸入描述開始新專案。"
5. `Orchestrator` 重置狀態

> Task 19/27 | 70%

### Task 20: Demo Data 測試 (+3 tests)

- 測試 `get_demo_plan()` 回傳合法 BuildingPlan
- 測試 demo IFC/USD 檔案存在且可讀
- 測試清除後 Orchestrator 狀態重置

> Task 20/27 | 74%

### Part C 完成通知

```bash
PART_DONE=3
MSG="🏗️ PromptBIM P22.1 Part C ✅
🏠 Demo Data 內建展示 (5 tasks)
✅ 台北信義區 3F 住宅 | 3D 模型 | BIM 資料 | 預算 | 清除功能
📊 進度: Task 20/27 | Part 3/5 | 74%
⏭️ 下一步: Part D — 建構驗證 + 文件同步 (4 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part D: 建構驗證 + 文件同步 (4 Tasks)

### Task 21: xcodebuild + pytest + GoogleTest + XCTest 驗證

```bash
xcodebuild -project PromptBIMTestApp1.xcodeproj -scheme PromptBIMTestApp1 -configuration Debug build 2>&1 | tail -5
python -m pytest tests/ -x --tb=short -q
cd libpromptbim/build && ctest --output-on-failure && cd ../..
```

驗收: xcodebuild SUCCEEDED + pytest ≥843 + GoogleTest ≥152 + XCTest ≥20
> Task 21/27 | 78%

### Task 22: 全量文件同步 (8項)

```
☐ TODO.md — P22.1 tasks ✅ + Demo Data
☐ CHANGELOG.md — v2.9.1 條目 (含 Demo Data feature)
☐ README.md — 測試數 + Demo Data 說明
☐ pyproject.toml — version = "2.9.1"
☐ __init__.py — __version__ = "2.9.1"
☐ Info.plist — 2.9.1 / build 23
☐ CMakeLists.txt — 2.9.1
☐ docs/PromptBIM_Context_Prompt.md — 同步
```

> Task 22/27 | 81%

### Task 23: pbxproj 完整性檢查

確認所有 .swift 在 pbxproj 中（含新增的 demo 相關檔案）。

> Task 23/27 | 85%

### Task 24: Xcode 8/8 完整性檢查

```
☐ xcodebuild BUILD SUCCEEDED
☐ 所有 .swift 在 pbxproj 中
☐ Info.plist 2.9.1 / build 23
☐ NSSupportsAutomaticTermination = false
☐ NSSupportsSuddenTermination = false
☐ Signing: ad-hoc
☐ Bundle ID = com.realitymatrix.PromptBIMTestApp1
☐ 新增 Swift 檔案已加入 Compile Sources
```

> Task 24/27 | 89%

### Part D 完成通知

```bash
PART_DONE=4
MSG="🏗️ PromptBIM P22.1 Part D ✅
🛠️ 建構驗證 + 文件同步 (4 tasks)
✅ Build OK + Tests OK + Docs 8/8 + pbxproj 8/8
📊 進度: Task 24/27 | Part 4/5 | 89%
⏭️ 下一步: Part E — 審計 + 推送 (3 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part E: 審計 + 推送 (3 Tasks)

### Task 25: 自我審計報告

產生 `docs/audit-reports/Sprint22.1_AuditReport.md`（代碼 + 文檔 8/8 + Xcode 8/8）。
> Task 25/27 | 93%

### Task 26: Git Commit + Push + Tags

```bash
git add -A
git commit -m "release: v2.9.1 — Sprint P22.1 Code Quality + Test Gap + Demo Data"
git push origin main
git tag v2.9.0  # P22 漏推的
git tag v2.9.1
git push origin --tags
```

> Task 26/27 | 96%

### Task 27: 產生 PROMPT_P23.md

依 CLAUDE.md v1.16.2 合規性檢查創建。
必須包含: notify 函數定義 + 啟動通知 + 文件完整性檢查 + 環境檢查 + 進度通知。
> Task 27/27 | 100%

### Part E 完成通知 + Sprint 最終通知

```bash
PART_DONE=5
MSG="🏗️ PromptBIM P22.1 Part E ✅
📦 審計 + 推送 (3 tasks)
✅ Audit + Tagged v2.9.0 + v2.9.1 + PROMPT_P23
📊 進度: Task 27/27 | Part 5/5 | 100%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"

MSG="🏗️ PromptBIM Sprint P22.1 完成 🎉
📋 Code Quality + Test Gap + Demo Data
🏷️ v2.9.1 | 27 Tasks / 5 Parts
🧪 GoogleTest ≥152 + pytest ≥843 + XCTest ≥20
🔧 Fixed: 2 Critical + 4 High + 5 Medium
🏠 Demo: 台北信義區 3F 住宅 | 3D | BIM | 預算
📊 完成度: 100% ✅
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## 執行指令

1. **第一步: 定義 notify + 啟動通知** (在做任何事之前)
2. **關鍵文件完整性檢查** (CLAUDE.md ≥5000B, SKILL.md ≥20000B)
3. **環境檢查** (含 ANTHROPIC_API_KEY 衝突檢查)
4. **每 Task notify 含進度** (Task N/27 | Part N/5 | %)
5. **每 Part notify 含下一步預告**
6. **不得修改 CLAUDE.md / SKILL.md / docs/backups/**
7. **不得中途詢問用戶**
8. **審計報告存放:** `docs/audit-reports/Sprint22.1_AuditReport.md`

---

## 驗收標準

```
☐ 啟動通知已收到
☐ QA-01: Cache get() 有 LOCK_SH
☐ QA-02: Orchestrator modify() 不再 crash
☐ QA-03~06: Orchestrator 封裝 + DRY
☐ QA-07: PBResult 已整合到 NativeBIMBridge
☐ QA-08: PythonBridge pipe 不再 deadlock
☐ Demo Data: App 啟動有 3D 模型 + BIM 資料 + 預算
☐ Demo Data: 清除後可重新生成
☐ xcodebuild BUILD SUCCEEDED
☐ GoogleTest ≥ 152
☐ pytest ≥ 843
☐ XCTest ≥ 20
☐ git tag v2.9.0 + v2.9.1
☐ docs/audit-reports/Sprint22.1_AuditReport.md
☐ sprints/PROMPT_P23.md 已建立
☐ 每個 Task 都有 notify（含進度 %）
☐ 最終完成 notify (100%)
```

---

*sprints/PROMPT_P22.1.md v2.0 | 2026-03-26*
*審查來源: AuditReport_03261820.md*
*notify: chchlin1018@icloud.com / +886972535899*
*通知: Task N/27 | Part N/5 | N%*
