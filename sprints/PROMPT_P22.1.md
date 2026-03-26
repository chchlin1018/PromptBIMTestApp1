# PROMPT_P22.1.md — Code Quality + Test Gap + Demo Data

> **Sprint:** P22.1 | **目標版本:** v2.9.1 | **基於:** P22 Senior Code Review + AuditReport_03261820
> **CLAUDE.md:** v1.16.2 | **SKILL.md:** v3.2（唯讀）
> **前置:** P22 完成（v2.9.0, 974 tests）
> **範圍:** 5 Parts / 27 Tasks — 代碼品質 + 測試缺口 + Demo Data + 建構驗證 + 治理合規
> **審查來源:** docs/audit-reports/AuditReport_03261820.md

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
    MSG="⛔ 關鍵文件損壞！CLAUDE=${CLAUDE_SIZE}B SKILL=${SKILL_SIZE}B
🔧 恢復: git checkout 9599bc08 -- CLAUDE.md && git checkout 15fc0efe -- SKILL.md"
    echo "$MSG" && notify "$MSG" && exit 1
fi
echo "✅ 關鍵文件完整: CLAUDE.md ${CLAUDE_SIZE}B, SKILL.md ${SKILL_SIZE}B"
```

---

## 環境檢查（含 API Key 衝突）

```bash
echo "========================================"
echo "🖥️  環境檢查 — $(hostname)"
echo "========================================"
if [ -n "$ANTHROPIC_API_KEY" ]; then
    MSG="⛔ PromptBIM Sprint 中止 — 偵測到 ANTHROPIC_API_KEY
❗ 會走 API 計費而非 Max 訂閱
🔧 修復: unset ANTHROPIC_API_KEY
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG" && exit 1
fi
echo "✅ 認證: Claude Max 訂閱（無 API Key 衝突）"
```

---

## 必讀文件

```
1. 本文件 sprints/PROMPT_P22.1.md
2. docs/audit-reports/AuditReport_03261820.md ← QA 審查報告
3. docs/audit-reports/Sprint22_AuditReport.md ← P22 自審報告
4. SKILL.md ← 唯讀，不得修改
5. CLAUDE.md ← v1.16.2，絕對不得修改
6. TODO.md
```

---

## ★ 通知規則（本 Sprint 全程適用）★

> ⚠️ **每個 Task / Part 通知必須包含進度：Task N/27 | Part N/5 | N%**
> ⚠️ **錯誤發生時立即 notify，不等 3 次失敗。**

### Task 完成通知
```bash
TASK_DONE=$((TASK_DONE+1))
PCT=$((TASK_DONE*100/TASK_TOTAL))
MSG="🏗️ PromptBIM P22.1
✅ Task ${TASK_DONE}: ${TASK_DESCRIPTION}
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Task 失敗通知
```bash
MSG="🏗️ PromptBIM P22.1
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)...
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### 中斷通知（3 次修復失敗）
```bash
MSG="🏗️ PromptBIM
❌ Sprint P22.1 中斷
📍 停在: Task ${TASK_DONE}/${TASK_TOTAL} (${TASK_DESCRIPTION})
❗ 原因: ${ERROR_DESCRIPTION}
📊 完成度: ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part A: 代碼品質修復 (7 Tasks)

### Task 1: Cache `get()` 加入讀取鎖 [QA-01 CRITICAL]
**檔案:** `src/promptbim/cache/store.py`
`get()` 中用 `fcntl.LOCK_SH` 共享讀鎖保護讀取。
> ✅ Task 1/27 | Part 0/5 | 4%

### Task 2: Orchestrator `modify()` 修復 `_output_dir` [QA-02 CRITICAL]
**檔案:** `src/promptbim/agents/orchestrator.py`
`__init__` 中保存 `self._output_dir`。移除 `generate()` 中對 `self._builder._output_dir` 的存取。
> ✅ Task 2/27 | Part 0/5 | 7%

### Task 3: Orchestrator 封裝性修復 [QA-03+04+05]
`TYPE_CHECKING` import `CheckResult`。四個屬性改 `_` prefix + `@property`。移除對 builder 私有屬性存取。
> ✅ Task 3/27 | Part 0/5 | 11%

### Task 4: Orchestrator DRY 重構 [QA-06]
提取 `_prepare_pipeline()` + `_build_result_obj()` + `_store_cache()` 共用方法。
> ✅ Task 4/27 | Part 0/5 | 15%

### Task 5: PBResult 整合到 NativeBIMBridge [QA-07]
`generateIFC` / `generateUSD` 回傳 `PBResult<T>`，保留 Bool wrapper 向後相容。
> ✅ Task 5/27 | Part 0/5 | 19%

### Task 6: PythonBridge pipe deadlock 修復 [QA-08]
先讀 pipe 再等 exit，或用 `readabilityHandler` 非同步讀取。
> ✅ Task 6/27 | Part 0/5 | 22%

### Task 7: `validate_api_key` 加 `.strip()` [QA-09]
> ✅ Task 7/27 | Part 0/5 | 26%

### Part A 完成通知
```bash
PART_DONE=1
MSG="🏗️ PromptBIM P22.1 Part A ✅
🔧 代碼品質修復 (7 tasks)
✅ Cache lock + Orchestrator 封裝 + DRY + PBResult + Pipe fix
📊 進度: Task 7/27 | Part 1/5 | 26%
⏭️ 下一步: Part B — 測試缺口修復 (8 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part B: 測試缺口修復 (8 Tasks)

### Task 8: pytest — Cache 併行讀寫測試 (+3)
> ✅ Task 8/27 | 30%

### Task 9: pytest — Orchestrator DI 測試 (+4)
> ✅ Task 9/27 | 33%

### Task 10: pytest — Orchestrator modify() 測試 (+3)
> ✅ Task 10/27 | 37%

### Task 11: pytest — Constraint dedup 測試 (+2)
> ✅ Task 11/27 | 41%

### Task 12: pytest — MEP registry + Cost warning (+4)
> ✅ Task 12/27 | 44%

### Task 13: pytest — validate_api_key 邊界 (+4)
> ✅ Task 13/27 | 48%

### Task 14: GoogleTest — C++ 測試補齊 (+13)
目標: 139 → ≥152。IFC thread safety (3) + NaN validation (3) + overflow (2) + GIS non-convex (3) + sanitizer (2)。
> ✅ Task 14/27 | 52%

### Task 15: XCTest — PBResult + 整合測試 (+5)
PBResult.ok / .fail + PBError errorDescription + NativeBIMBridge PBResult。
> ✅ Task 15/27 | 56%

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

## Part C: Demo Data 內建展示資料 (5 Tasks)

> ⚠️ **目標：App 啟動時不是空白畫面，而是展示一個完整的 BIM 專案，讓使用者立即看到系統能力。**
> ⚠️ **使用者可以清除展示資料後重新生成。**

### Task 16: 建立 Demo 土地資料

**檔案:** `src/promptbim/demo/demo_data.py` (新建)
**內容:**
- 一筆台北市信義區住宅用地（約 500 平方公尺，梯形）
- LandParcel 完整座標、面積、周長
- ZoningRules：住宅區、容積率 2.4、建蔽率 0.6、高度 21m、退縮 5/3/2/2m
- 提供 `get_demo_land()` 和 `get_demo_zoning()` 函數

> ✅ Task 16/27 | Part 2/5 | 59%

### Task 17: 建立 Demo 建築計畫

**檔案:** `src/promptbim/demo/demo_data.py` (繼續)
**內容:**
- 一棟 3 層電梯住宅的完整 BuildingPlan JSON
- 1F: 大廳 + 停車場 + 機房
- 2F-3F: 各 2 戶50~60㎡住宅單元（客廳 + 臥室 + 廉所 + 廚房）
- 屋頂: 平屋頂 + 太陽能板區域
- 包含 BCR / FAR / 面積等計算
- 提供 `get_demo_plan()` 函數

> ✅ Task 17/27 | Part 2/5 | 63%

### Task 18: 產生 Demo IFC + USD + 成本估算 + 合規檢查

**檔案:** `src/promptbim/demo/demo_data.py` + `resources/demo/`
**內容:**
- 用 BuilderAgent 從 demo plan 產生 IFC + USD 檔案
- 儲存到 `resources/demo/model.ifc` + `resources/demo/model.usda`
- 產生成本估算 JSON: `resources/demo/cost_estimate.json`
- 產生合規檢查 JSON: `resources/demo/compliance_report.json`
- 產生平面圖 SVG: `resources/demo/floorplan_1f.svg` / `2f` / `3f`
- 提供 `get_demo_result()` 函數回傳完整 GenerationResult

> ✅ Task 18/27 | Part 2/5 | 67%

### Task 19: App 啟動載入 Demo Data

**檔案:** `src/promptbim/gui/main_window.py` + `PromptBIMTestApp1/ContentView.swift`
**內容:**
- GUI 啟動時檢查是否有現有專案，如果沒有則載入 demo data
- 2D 地籍圖 Tab 顯示 demo 土地 + 建築 footprint
- 3D Tab 顯示 demo 建築模型（PyVista 或 SceneKit）
- 屬性面板顯示面積 / 容積率 / 建蔽率 / 成本估算
- Chat 面板顯示「歡迎使用 PromptBIM！這是一個範例專案...」
- Swift ContentView 也顯示 "Demo Project Loaded"

> ✅ Task 19/27 | Part 2/5 | 70%

### Task 20: 「清除展示」功能

**檔案:** `src/promptbim/gui/main_window.py`
**內容:**
- 在 GUI 中加入 "清除展示資料" 按鈕（或選單 File > Clear Demo）
- 點擊後清除所有 demo data，回到空白狀態
- 使用者可以重新輸入土地 + 用 AI 生成新建築
- CLI 也支援: `python -m promptbim demo --load` / `--clear`

> ✅ Task 20/27 | Part 2/5 | 74%

### Part C 完成通知
```bash
PART_DONE=3
MSG="🏗️ PromptBIM P22.1 Part C ✅
🏠 Demo Data 內建展示 (5 tasks)
✅ 台北信義區 3層住宅 | IFC+USD+3D+成本+合規
✅ App 啟動即顯示 | 可清除重新生成
📊 進度: Task 20/27 | Part 3/5 | 74%
⏭️ 下一步: Part D — 建構驗證 + 文件 (4 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part D: 建構驗證 + 文件同步 (4 Tasks)

### Task 21: xcodebuild + pytest + GoogleTest 驗證
驗收: xcodebuild SUCCEEDED + pytest ≥840 + GoogleTest ≥152 + XCTest ≥20
> ✅ Task 21/27 | 78%

### Task 22: 全量文件同步 (8項)
```
☐ TODO.md — P22.1 tasks ✅ + demo data
☐ CHANGELOG.md — v2.9.1 條目
☐ README.md — 測試數 + demo data 說明
☐ pyproject.toml — version = "2.9.1"
☐ __init__.py — __version__ = "2.9.1"
☐ Info.plist — 2.9.1 / build 23
☐ CMakeLists.txt — 2.9.1
☐ docs/PromptBIM_Context_Prompt.md — 同步
```
> ✅ Task 22/27 | 81%

### Task 23: pbxproj 完整性檢查
確認所有 .swift 在 pbxproj 中。確認新增的 demo 資源檔已加入 Copy Bundle Resources。
> ✅ Task 23/27 | 85%

### Task 24: Demo Data 功能測試 (+3 pytest)
測試 `get_demo_land()` / `get_demo_plan()` / `get_demo_result()` 回傳值正確。
> ✅ Task 24/27 | 89%

### Part D 完成通知
```bash
PART_DONE=4
MSG="🏗️ PromptBIM P22.1 Part D ✅
🛠️ 建構驗證 + 文件同步 (4 tasks)
✅ Build OK + Docs 8/8 + pbxproj OK + Demo tests
📊 進度: Task 24/27 | Part 4/5 | 89%
⏭️ 下一步: Part E — 審計 + 推送 (3 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part E: 審計 + 推送 + 治理合規 (3 Tasks)

### Task 25: 自我審計報告
產生 `docs/audit-reports/Sprint22.1_AuditReport.md`（代碼 + 文檔 8/8 + Xcode 8/8）。
> ✅ Task 25/27 | 93%

### Task 26: Git Commit + Push + Tag
- `git tag v2.9.0`（補 P22 缺少的 tag）
- `git tag v2.9.1`
- `git push origin main --tags`
> ✅ Task 26/27 | 96%

### Task 27: 產生 PROMPT_P23.md
依 CLAUDE.md v1.16.2 合規性檢查創建下一個 Sprint Prompt。
必須包含: notify 定義 + 啟動通知 + 文件檢查 + 環境檢查 + 通知模板 + 進度追蹤。
> ✅ Task 27/27 | 100%

### Part E 完成通知 + 最終通知
```bash
PART_DONE=5
MSG="🏗️ PromptBIM P22.1 Part E ✅
📦 審計 + 推送 + 治理 (3 tasks)
✅ Audit + Tagged v2.9.0 + v2.9.1 + PROMPT_P23
📊 進度: Task 27/27 | Part 5/5 | 100%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"

MSG="🏗️ PromptBIM Sprint P22.1 完成 🎉
📋 Code Quality + Test Gap + Demo Data
🏷️ v2.9.1 | 27 Tasks / 5 Parts
🧪 GoogleTest ≥152 + pytest ≥843 + XCTest ≥20
🔧 Fixed: 2 Critical + 4 High + 5 Medium
🏠 Demo: 台北信義區 3層住宅 | 啟動即顯示
📊 完成度: 100% ✅
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## 執行指令

1. **第一步: 定義 notify + 啟動通知**
2. **關鍵文件完整性檢查**（CLAUDE.md ≥5000B, SKILL.md ≥20000B）
3. **環境檢查**（含 API Key 衝突）
4. **每 Task notify 含進度** (Task N/27 | Part N/5 | %)
5. **每 Part notify 含下一步預告**
6. **錯誤發生 → 立即 notify**
7. **3 次修復失敗 → 中斷 notify**
8. **不得修改 CLAUDE.md / SKILL.md / docs/backups/**
9. **不得中途詢問用戶**

---

## 驗收標準

```
☐ 啟動通知已收到（含 27 Tasks / 5 Parts 總覽）
☐ 關鍵文件檢查通過
☐ 環境檢查通過（無 ANTHROPIC_API_KEY）
☐ QA-01: Cache get() 有 LOCK_SH
☐ QA-02: Orchestrator modify() 不再 crash
☐ QA-03~06: Orchestrator 封裝 + DRY
☐ QA-07: PBResult 已整合
☐ QA-08: PythonBridge pipe 不再 deadlock
☐ Demo: App 啟動即顯示 3D 模型 + BIM 資料
☐ Demo: 可清除展示資料後重新生成
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
*審查來源: AuditReport_03261820.md + 資深 QA 代碼審查*
*notify: chchlin1018@icloud.com / +886972535899*
*通知含進度: Task N/27 | Part N/5 | N%*
*CLAUDE.md v1.16.2 合規性檢查: ✅ 通過*
