# PROMPT_P22.1.md — Code Quality Remediation + Test Gap Fix

> **Sprint:** P22.1 | **目標版本:** v2.9.1 | **基於:** P22 Senior Code Review
> **CLAUDE.md:** v1.16.2 | **SKILL.md:** v3.2（唯讀）
> **前置:** P22 完成（v2.9.0, 974 tests）
> **範圍:** 4 Parts / 20 Tasks — 代碼品質修復 + 測試缺口 + 治理合規
> **審查來源:** 資深軟體品質工程師全面代碼審查 (2026-03-26)

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

TASK_TOTAL=20
PART_TOTAL=4
TASK_DONE=0
PART_DONE=0

MSG="🏗️ PromptBIM Sprint P22.1 啟動
📋 Code Quality Remediation + Test Gap Fix
🎯 20 Tasks / 4 Parts → v2.9.1
📊 審查來源: 資深 QA 全面代碼審查
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

## 必讀文件

```
1. 本文件 sprints/PROMPT_P22.1.md
2. docs/audit-reports/Sprint22_AuditReport.md
3. SKILL.md ← 唯讀
4. CLAUDE.md ← v1.16.2（絕對不得修改）
```

---

## 審查發現摘要

| ID | 嚴重度 | 檔案 | 問題描述 |
|----|--------|------|----------|
| QA-01 | 🟥 CRITICAL | cache/store.py | `get()` 無檔案鎖，併行讀寫可讀到不完整 JSON |
| QA-02 | 🟥 CRITICAL | orchestrator.py | `modify()` 引用 `self._output_dir` 但未設定，執行時 crash |
| QA-03 | 🟧 HIGH | orchestrator.py | `CheckResult` 在 `__init__` 中使用但未 import |
| QA-04 | 🟧 HIGH | orchestrator.py | `self.requirement/plan/build_result/check_result` 為 public，遍反封裝原則 |
| QA-05 | 🟧 HIGH | orchestrator.py | `generate()` 存取 builder 的私有屬性 `_output_dir` |
| QA-06 | 🟧 HIGH | orchestrator.py | `generate()` 與 `agenerate()` 80% 程式碼重複（DRY 違規） |
| QA-07 | 🟨 MEDIUM | PBResult.swift | 定義了但未整合到 NativeBIMBridge，是 dead code |
| QA-08 | 🟨 MEDIUM | PythonBridge.swift | `runCommand` pipe 讀取在 process 結束後，大輸出可能 deadlock |
| QA-09 | 🟨 MEDIUM | config.py | `validate_api_key` 未測試邊界情況（空字串、空白、過短） |
| QA-10 | 🟨 MEDIUM | 全局 | GoogleTest 139 < 目標 152，pytest 820 < 目標 840 |
| QA-11 | 🟨 MEDIUM | 治理 | 未推送 `git tag v2.9.0`，未產生 PROMPT_P23.md |

---

## Part A: 代碼品質修復 — Critical + High (7 Tasks)

### Task 1: Cache `get()` 加入讀取鎖 [QA-01]

**檔案:** `src/promptbim/cache/store.py`
**問題:** `put()` 用 `fcntl.LOCK_EX` 保護寫入，但 `get()` 用 `path.read_text()` 無鎖。併行讀寫時可讀到截斷的 JSON。
**修復:** `get()` 中用 `fcntl.LOCK_SH`（共享讀鎖）保護讀取。

```python
def get(self, key: str) -> dict | None:
    path = self._key_path(key)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except (json.JSONDecodeError, OSError):
        ...
```

> 完成後: `MSG="... ✅ Task 1/20 | Part 0/4 | 5% ..."` && notify

### Task 2: Orchestrator `modify()` 修復 `_output_dir` 引用 [QA-02]

**檔案:** `src/promptbim/agents/orchestrator.py`
**問題:** `modify()` 第 277 行 `self._output_dir` 未定義，執行時 `AttributeError`。
**修復:** `__init__` 中保存 `self._output_dir = Path(output_dir) if output_dir else None`。同時移除 `generate()` 中對 `self._builder._output_dir` 的存取。

> 完成後: `MSG="... ✅ Task 2/20 | Part 0/4 | 10% ..."` && notify

### Task 3: Orchestrator 封裝性修復 [QA-03 + QA-04 + QA-05]

**問題:**
- `CheckResult` 在 `__init__` 中使用但未加入 `TYPE_CHECKING` import
- `self.requirement` / `self.plan` / `self.build_result` / `self.check_result` 是 public
- `generate()` 存取 `self._builder._output_dir`（私有屬性）

**修復:**
1. `TYPE_CHECKING` 區塊加入 `from promptbim.agents.checker import CheckResult`
2. 將四個屬性改為 `_requirement` / `_plan` / `_build_result` / `_check_result`
3. 加入 `@property` 唯讀存取器
4. 移除對 `self._builder._output_dir` 的存取，改用 `self._output_dir`

> 完成後: `MSG="... ✅ Task 3/20 | Part 0/4 | 15% ..."` && notify

### Task 4: Orchestrator DRY 重構 [QA-06]

**問題:** `generate()` 與 `agenerate()` 共享 80%+ 的邏輯（cache lookup, setback, result construction）。
**修復:** 提取共用方法：
- `_prepare_pipeline(prompt, land, zoning, use_cache)` → cache + setback
- `_build_result_obj(plan, build_result, check_result, ...)` → GenerationResult 建構
- `_store_cache(cache_key, result)` → 快取儲存

> 完成後: `MSG="... ✅ Task 4/20 | Part 0/4 | 20% ..."` && notify

### Task 5: PBResult 整合到 NativeBIMBridge [QA-07]

**檔案:** `PromptBIMTestApp1/NativeBIMBridge.swift`
**問題:** `PBResult<T>` 定義了但未使用，`generateIFC` / `generateUSD` 仍回傳 `Bool`。
**修復:** 將 `generateIFC` / `generateUSD` / `parseLandGeoJSON` 回傳型別改為 `PBResult<T>`，保留 Bool 版本作為 backward compat wrapper。

> 完成後: `MSG="... ✅ Task 5/20 | Part 0/4 | 25% ..."` && notify

### Task 6: PythonBridge pipe deadlock 修復 [QA-08]

**檔案:** `PromptBIMTestApp1/PythonBridge.swift`
**問題:** `runCommand` 先 `waitUntilExit()` 再 `readDataToEndOfFile()`。如果 stdout buffer 滿了，process 會 hang 等待 buffer 被讀，但 Swift 還在等 exit。
**修復:** 在另一個 thread 讀 pipe data，確保不會 deadlock。

```swift
// 先讀 pipe，再等 exit
let data = stdoutPipe.fileHandleForReading.readDataToEndOfFile()
process.waitUntilExit()
// 或用 readabilityHandler 非同步讀取
```

> 完成後: `MSG="... ✅ Task 6/20 | Part 0/4 | 30% ..."` && notify

### Task 7: config.py `validate_api_key` 邊界情況 [QA-09]

**問題:** `validate_api_key(" ")` 返回 True（空白字串不是空，且以 "sk-ant-" 開頭檢查失敗所以返回 False... 實際上此處正確，但應加 `.strip()` 確保）
**修復:** `key = key.strip()` 在最前面。

> 完成後: `MSG="... ✅ Task 7/20 | Part 0/4 | 35% ..."` && notify

### Part A 完成通知

```bash
PART_DONE=1
MSG="🏗️ PromptBIM P22.1 Part A ✅
🔧 代碼品質修復 (7 tasks)
✅ Cache read lock + Orchestrator 封裝 + DRY + PBResult + Pipe fix
📊 進度: Task 7/20 | Part 1/4 | 35%
⏭️ 下一步: Part B — 測試缺口修復 (8 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part B: 測試缺口修復 (8 Tasks)

### Task 8: pytest — Cache 併行讀寫測試 (+3 tests)

測試 `get()` 與 `put()` 併行執行不會 crash。用 `threading` 模擬。
> Task 8/20 | 40%

### Task 9: pytest — Orchestrator DI 測試 (+4 tests)

測試注入自定義 agent 、確認使用注入的而非預設。
> Task 9/20 | 45%

### Task 10: pytest — Orchestrator `modify()` + `_output_dir` (+3 tests)

測試 `modify()` 不會 crash，測試 `_output_dir` 正確傳遞。
> Task 10/20 | 50%

### Task 11: pytest — Constraint dedup 測試 (+2 tests)

測試同一 constraint 不會重複加入。
> Task 11/20 | 55%

### Task 12: pytest — MEP registry + Cost warning (+4 tests)

測試 `register_system()` 、測試 missing category 會產生 warning log。
> Task 12/20 | 60%

### Task 13: pytest — config `validate_api_key` 邊界 (+4 tests)

測試：空字串、空白、太短、正確格式、錯誤 prefix。
> Task 13/20 | 65%

### Task 14: GoogleTest — C++ 測試補齊 (+13 tests)

目標: 139 → ≥152。新增:
- IFC `gmtime_r` thread safety (3 tests)
- IFC NaN/infinity validation (3 tests)
- IFC overflow protection (2 tests)
- GIS non-convex setback edge cases (3 tests)
- CMake sanitizer flag (2 tests: compile check)

> Task 14/20 | 70%

### Task 15: XCTest — PBResult + 整合測試 (+5 tests)

- PBResult.ok / PBResult.fail 建構
- PBError 各種 case 的 errorDescription
- NativeBIMBridge PBResult 回傳值

> Task 15/20 | 75%

### Part B 完成通知

```bash
PART_DONE=2
MSG="🏗️ PromptBIM P22.1 Part B ✅
🧪 測試缺口修復 (8 tasks)
✅ pytest +20 | GoogleTest +13 | XCTest +5
📊 進度: Task 15/20 | Part 2/4 | 75%
⏭️ 下一步: Part C — 建構驗證 + 文件同步 (3 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part C: 建構驗證 + 文件同步 (3 Tasks)

### Task 16: 建構 + 測試驗證

```bash
# xcodebuild
xcodebuild -project PromptBIMTestApp1.xcodeproj -scheme PromptBIMTestApp1 -configuration Debug build 2>&1 | tail -5

# pytest
python -m pytest tests/ -x --tb=short -q

# GoogleTest
cd libpromptbim/build && ctest --output-on-failure
```

驗收: xcodebuild SUCCEEDED + pytest ≥840 + GoogleTest ≥152 + XCTest ≥20
> Task 16/20 | 80%

### Task 17: 全量文件同步 (8項)

```
☐ TODO.md — P22.1 tasks ✅
☐ CHANGELOG.md — v2.9.1 條目
☐ README.md — 測試數更新
☐ pyproject.toml — version = "2.9.1"
☐ __init__.py — __version__ = "2.9.1"
☐ Info.plist — 2.9.1 / build 23
☐ CMakeLists.txt — 2.9.1
☐ Context Prompt — 同步
```

> Task 17/20 | 85%

### Task 18: pbxproj 完整性檢查

確認所有 .swift 在 pbxproj 中。
> Task 18/20 | 90%

### Part C 完成通知

```bash
PART_DONE=3
MSG="🏗️ PromptBIM P22.1 Part C ✅
🛠️ 建構驗證 + 文件同步 (3 tasks)
✅ Build OK + Docs 8/8 + pbxproj OK
📊 進度: Task 18/20 | Part 3/4 | 90%
⏭️ 下一步: Part D — 審計 + 推送 (2 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part D: 審計 + 推送 (2 Tasks)

### Task 19: 自我審計報告 + Git push + Tag

產生 `docs/audit-reports/Sprint22.1_AuditReport.md`。
推送 git tag v2.9.0 + v2.9.1。
> Task 19/20 | 95%

### Task 20: 產生 PROMPT_P23.md

依 CLAUDE.md v1.16.2 合規性檢查創建下一個 Sprint Prompt。
內容: 待定（可以是 Future Features P23-P26 的任意一個）。
> Task 20/20 | 100%

### Part D 完成通知 + 最終通知

```bash
PART_DONE=4
MSG="🏗️ PromptBIM P22.1 Part D ✅
📦 審計 + 推送 (2 tasks)
✅ Audit + Tagged v2.9.1 + PROMPT_P23 已建立
📊 進度: Task 20/20 | Part 4/4 | 100%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"

MSG="🏗️ PromptBIM Sprint P22.1 完成 🎉
📋 Code Quality Remediation + Test Gap Fix
🏷️ v2.9.1 | 20 Tasks / 4 Parts
🧪 GoogleTest ≥152 + pytest ≥840 + XCTest ≥20
🔧 Fixed: 2 Critical + 4 High + 4 Medium
📊 完成度: 100% ✅
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## 執行指令

1. **第一步: 定義 notify + 啟動通知**
2. **每 Task notify 含進度** (Task N/20 | Part N/4 | %)
3. **每 Part notify 含下一步預告**
4. **不得修改 CLAUDE.md / SKILL.md**
5. **不得中途詢問用戶**

---

## 驗收標準

```
☐ 啟動通知已收到
☐ QA-01: Cache get() 有 LOCK_SH
☐ QA-02: Orchestrator modify() 不再 crash
☐ QA-03~06: Orchestrator 封裝 + DRY
☐ QA-07: PBResult 已整合到 NativeBIMBridge
☐ QA-08: PythonBridge pipe 不再 deadlock
☐ xcodebuild BUILD SUCCEEDED
☐ GoogleTest ≥ 152
☐ pytest ≥ 840
☐ XCTest ≥ 20
☐ git tag v2.9.0 + v2.9.1
☐ docs/audit-reports/Sprint22.1_AuditReport.md
☐ sprints/PROMPT_P23.md 已建立
☐ 每個 Task 都有 notify（含進度 %）
☐ 最終完成 notify (100%)
```

---

*sprints/PROMPT_P22.1.md v1.0 | 2026-03-26*
*審查來源: 資深軟體品質工程師全面代碼審查*
*notify: chchlin1018@icloud.com / +886972535899*
*通知包含進度: Task N/20 | Part N/4 | N%*
