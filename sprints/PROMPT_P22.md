# PROMPT_P22.md — Senior Audit Full Remediation

> **Sprint:** P22 | **目標版本:** v2.9.0 | **基於:** AuditReport_Full_v2.8.0
> **CLAUDE.md:** v1.15.1 | **SKILL.md:** v3.2（唯讀）
> **前置:** P21 完成（v2.8.0, 957 tests）
> **範圍:** Part 0 清理 + 5 Critical + 8 High + 12 Medium + 5 Finalization = **36 Tasks / 6 Parts**

---

## ★★★ 第一步：定義 notify 函數 + 發送啟動通知 ★★★

> ⚠️ **這是整個 Sprint 的第一個動作。在讀取任何其他文件之前，必須先執行以下指令。**
> ⚠️ **如果 notify 函數已存在（由 shell profile 定義），直接使用。否則用下方定義。**

```bash
# ===== 定義 notify 函數（如果尚未定義）=====
if ! type notify &>/dev/null; then
    notify() {
        local msg="$1"
        # 方法 1: 嘗試用已知的 iMessage AppleScript
        osascript -e "
            tell application \"Messages\"
                set targetService to 1st account whose service type = iMessage
                set targetBuddy to participant \"michaellin@me.com\" of targetService
                send \"$msg\" to targetBuddy
            end tell
        " 2>/dev/null || \
        # 方法 2: fallback 到 macOS 通知中心
        osascript -e "display notification \"$msg\" with title \"PromptBIM\"" 2>/dev/null || \
        # 方法 3: 最後 fallback 只 echo
        echo "[NOTIFY FALLBACK] $msg"
    }
    echo "✅ notify 函數已定義（fallback 模式）"
else
    echo "✅ notify 函數已存在（系統定義）"
fi

# ===== 立即發送啟動通知 =====
MSG="🏗️ PromptBIM Sprint P22 啟動
📋 Senior Audit Full Remediation
🎯 36 Tasks / 6 Parts → v2.9.0
📊 Part 0: 專案清理 + 5 Critical + 8 High + 12 Medium
🔔 通知: 每 Task + 每 Part + 錯誤即時
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## 必讀文件（啟動通知發送後才讀）

```
1. 本文件 sprints/PROMPT_P22.md ← 已讀
2. docs/audit-reports/AuditReport_Full_v2.8.0.md ← 審計報告（所有 issue ID 來源）
   ⚠️ 如果路徑不存在，嘗試 docs/reports/AuditReport_03261630.md（舊路徑）
3. SKILL.md ← 專案 SSOT（唯讀，不得修改）
4. CLAUDE.md ← v1.15.1 行為規範（絕對不得修改）
5. TODO.md ← 確認當前狀態
```

---

## ★ 通知規則（本 Sprint 全程適用）★

> ⚠️ **每個 Task 和 Part 完成後都必須 echo + notify。**
> ⚠️ **錯誤發生時立即 echo + notify，不等 3 次失敗。**
> ⚠️ **所有 notify 呼叫前必須確認 notify 函數已定義（第一步已處理）。**

### Task 完成通知模板

```bash
MSG="🏗️ PromptBIM P22
✅ Task ${TASK_NUM}: ${TASK_DESCRIPTION}
📋 ${ISSUE_IDS_FIXED}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Part 完成通知模板

```bash
MSG="🏗️ PromptBIM P22 Part ${PART} ✅
📋 ${PART_DESCRIPTION} (${TASK_COUNT} tasks)
✅ ${KEY_ACHIEVEMENTS}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Task 失敗通知模板（錯誤發生時立即）

```bash
MSG="🏗️ PromptBIM P22
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)...
🔧 修復方式: ${FIX_APPROACH}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### 中斷通知模板（3 次修復失敗後）

```bash
MSG="🏗️ PromptBIM
❌ Sprint P22 執行中斷
📍 停在: Task ${TASK_NUM} (${TASK_DESCRIPTION})
❗ 原因: ${ERROR_DESCRIPTION}
🔄 已嘗試修復 3 次均失敗
💡 建議: ${SUGGESTED_ACTION}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## 環境檢查

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

if [ -n "$ANTHROPIC_API_KEY" ]; then
    MSG="⛔ PromptBIM Sprint 中止 — 偵測到 ANTHROPIC_API_KEY
🔧 修復: unset ANTHROPIC_API_KEY
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
    echo "$MSG"
    notify "$MSG"
    exit 1
fi
echo "✅ 認證: Claude Max 訂閱"
```

---

## Part 0: 專案檔案重整（6 Tasks）

> ⚠️ **如果檔案已搬遷（前次部分執行），跳過已完成的步驟。每步都 notify。**

### Task 1: 搬遷 Sprint Prompt 到 sprints/
```bash
# Idempotent: 只搬尚未搬遷的檔案
MOVED=0
for f in PROMPT.md PROMPT_P*.md; do
    if [ -f "$f" ]; then
        git mv "$f" "sprints/$f" 2>/dev/null && MOVED=$((MOVED+1))
    fi
done
echo "✅ Task 1: Moved $MOVED PROMPT files to sprints/"
MSG="🏗️ PromptBIM P22
✅ Task 1: Moved $MOVED PROMPT files to sprints/
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Task 2: 搬遷 Audit Report 到 docs/audit-reports/
```bash
MOVED=0
if [ -d "docs/reports" ]; then
    for f in docs/reports/*AuditReport*.md; do
        [ -f "$f" ] && git mv "$f" "docs/audit-reports/$(basename $f)" 2>/dev/null && MOVED=$((MOVED+1))
    done
fi
[ -f "AuditReport.md" ] && git mv AuditReport.md docs/audit-reports/AuditReport_Legacy_P16.md 2>/dev/null && MOVED=$((MOVED+1))
# 重命名 03261630 → Full_v2.8.0（如果存在）
[ -f "docs/audit-reports/AuditReport_03261630.md" ] && git mv "docs/audit-reports/AuditReport_03261630.md" "docs/audit-reports/AuditReport_Full_v2.8.0.md" 2>/dev/null
MSG="🏗️ PromptBIM P22
✅ Task 2: Moved $MOVED AuditReport files to docs/audit-reports/
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Task 3: 清理 docs/reports/ 殘留
```bash
MSG="🏗️ PromptBIM P22
✅ Task 3: docs/reports/ cleaned
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Task 4: 刪除 sprints/.gitkeep
```bash
git rm sprints/.gitkeep 2>/dev/null || true
MSG="🏗️ PromptBIM P22
✅ Task 4: sprints/.gitkeep removed
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Task 5: 驗證檔案結構
```bash
SPRINT_COUNT=$(ls sprints/PROMPT_P*.md 2>/dev/null | wc -l | tr -d ' ')
AUDIT_COUNT=$(ls docs/audit-reports/*.md 2>/dev/null | wc -l | tr -d ' ')
ROOT_PROMPTS=$(ls PROMPT*.md 2>/dev/null | wc -l | tr -d ' ')
MSG="🏗️ PromptBIM P22
✅ Task 5: Structure verified
📁 sprints/: ${SPRINT_COUNT} files
📁 audit-reports/: ${AUDIT_COUNT} files
📁 Root PROMPTs: ${ROOT_PROMPTS} (should be 0)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Task 6: Commit 檔案重整
```bash
git add -A
git diff --cached --quiet || git commit -m "refactor: project reorganization per CLAUDE.md v1.15.1"
MSG="🏗️ PromptBIM P22
✅ Task 6: Reorganization committed
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Part 0 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part 0 ✅
🗂️ 專案檔案重整 (6 tasks)
✅ sprints/ + docs/audit-reports/ 整理完成
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part A: C++ Critical + Robustness Fixes（7 Tasks）

> ⚠️ **每個 Task 完成後 echo + notify。失敗時立即 notify。**

### Task 7: IFC Generator 線程安全 [CRITICAL: IFC-01 + IFC-02]
gmtime() → gmtime_r() + std::mutex 保護。
> 完成後 notify: Task 7: IFC thread safety fixed (IFC-01 + IFC-02) ✅
> 失敗時 notify: Task 7 ⚠️ IFC thread safety — {error} — 嘗試修復...

### Task 8: IFC 輸入驗證 + 溢位保護 [MEDIUM: IFC-03 + IFC-04]
> 完成後 notify: Task 8: IFC input validation (IFC-03 + IFC-04) ✅

### Task 9: CMake Build Hardening [MEDIUM: CMAKE-01~03]
> 完成後 notify: Task 9: CMake hardening (CMAKE-01~03) ✅

### Task 10: GIS Non-Convex Setback [MEDIUM: GIS-01]
> 完成後 notify: Task 10: GIS non-convex setback (GIS-01) ✅

### Task 11: GIS DXF + Shapefile Enhancement [MEDIUM: GIS-02 + GIS-03]
> 完成後 notify: Task 11: GIS DXF/SHP parser (GIS-02 + GIS-03) ✅

### Task 12: C++ GoogleTest [ALL C++ FIXES]
目標: ≥ 15 新增（137 → ≥ 152）。
> 完成後 notify: Task 12: GoogleTest N/152+ passed ✅

### Task 13: NativeBIMBridge dlsym [CRITICAL: SW-05 + SW-06]
> 完成後 notify: Task 13: dlsym null check + pb_version (SW-05 + SW-06) ✅

### Part A 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part A ✅
🔧 C++ Critical + Robustness (7 tasks)
✅ IFC thread safety + input validation
✅ CMake hardening + GIS fixes + dlsym
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part B: Python Critical + High Fixes（8 Tasks）

> ⚠️ **每個 Task 完成後 echo + notify。**

### Task 14: Cache Store File Locking [CRITICAL: CACHE-01]
> 完成後 notify: Task 14: Cache file locking (CACHE-01) ✅

### Task 15: Orchestrator DI [HIGH: PY-01]
> 完成後 notify: Task 15: Orchestrator DI (PY-01) ✅

### Task 16: Async Builder Non-Blocking [HIGH: PY-02]
> 完成後 notify: Task 16: Async non-blocking (PY-02) ✅

### Task 17: Constraint Dedup + API Key [MEDIUM: PY-03 + PY-04]
> 完成後 notify: Task 17: Constraint dedup + API key (PY-03 + PY-04) ✅

### Task 18: Config validate_api_key [MEDIUM: CFG-01]
> 完成後 notify: Task 18: validate_api_key fix (CFG-01) ✅

### Task 19: Cost Missing Category [HIGH: COST-01]
> 完成後 notify: Task 19: Cost missing category (COST-01) ✅

### Task 20: MEP Grid + Registry [HIGH: MEP-01 + MEP-02]
> 完成後 notify: Task 20: MEP grid + registry (MEP-01 + MEP-02) ✅

### Task 21: Python Tests for Part B
目標: ≥ 20 新增（820 → ≥ 840）。
> 完成後 notify: Task 21: pytest N/840+ passed ✅

### Part B 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part B ✅
🐍 Python Critical + High (8 tasks)
✅ Cache locking + Orchestrator DI + async
✅ Cost + MEP + Config fixes
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part C: Swift Fixes + XCTest（5 Tasks）

> ⚠️ **每個 Task 完成後 echo + notify。**

### Task 22: PythonBridge Timeout + Termination [HIGH: SW-01 + SW-02]
> 完成後 notify: Task 22: PythonBridge timeout + termination ✅

### Task 23: PythonBridge Stderr + Path [MEDIUM: SW-03 + SW-04]
> 完成後 notify: Task 23: PythonBridge stderr + path ✅

### Task 24: BIMSceneBuilder.swift 獨立檔案
> ⚠️ **新增 Swift 檔案必須加入 pbxproj Compile Sources！**
> 完成後 notify: Task 24: BIMSceneBuilder.swift extracted ✅

### Task 25: Cross-Layer PBResult Error Propagation
> 完成後 notify: Task 25: PBResult struct implemented ✅

### Task 26: Swift XCTest Suite [CRITICAL: SW-07]
目標: ≥ 15 XCTest cases。
> ⚠️ **XCTest target + 檔案都必須加入 xcodeproj。**
> 完成後 notify: Task 26: XCTest N/15+ cases ✅

### Part C 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part C ✅
🍎 Swift Fixes + XCTest (5 tasks)
✅ PythonBridge + BIMSceneBuilder + PBResult + XCTest
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part D: Subsystem Fixes（5 Tasks）

> ⚠️ **每個 Task 完成後 echo + notify。**

### Task 27: Monitoring Sensor-Space Validation [MEDIUM: MON-01]
> 完成後 notify: Task 27: Sensor-space validation ✅

### Task 28: Simulation Enum Classification [MEDIUM: SIM-01]
> 完成後 notify: Task 28: Enum classification ✅

### Task 29: Orchestrator Encapsulation [LOW: PY-05 + PY-06]
> 完成後 notify: Task 29: Orchestrator encapsulation ✅

### Task 30: pybind11 .pyi Type Stubs
> 完成後 notify: Task 30: .pyi type stubs ✅

### Task 31: Plugin System Activation [HIGH: PLG-01]
> 完成後 notify: Task 31: Plugin system activated ✅

### Part D 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part D ✅
🔌 Subsystem Fixes (5 tasks)
✅ Sensor + Enum + Plugin + .pyi stubs
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part E: Finalization（5 Tasks）

> ⚠️ **每個 Task 完成後 echo + notify。**

### Task 32: Context Prompt Update
> 完成後 notify: Task 32: Context Prompt → v2.9.0 ✅

### Task 33: Full Document Sync（8 項）
> 完成後 notify: Task 33: Doc sync 8/8 ✅

### Task 34: Build + Test Verification
> 完成後 notify: Task 34: Build OK — GoogleTest N + pytest N + XCTest N ✅
> 失敗時 notify: Task 34 ⚠️ Build failed — {error}

### Task 35: Self-Audit Report
產生 `docs/audit-reports/Sprint22_AuditReport.md`。
> 完成後 notify: Task 35: Audit — Code {grade} / Docs N/8 / Xcode N/8 ✅

### Task 36: Git Commit + Push + Tag
> 完成後 notify: Task 36: Git pushed + tagged v2.9.0 ✅

### Part E 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part E ✅
📦 Finalization (5 tasks)
✅ Docs 8/8 + Build verified + Tagged v2.9.0
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## ★ Sprint 最終完成通知 ★

```bash
MSG="🏗️ PromptBIM Sprint P22 完成 🎉
📋 Senior Audit Full Remediation
🏷️ v2.9.0 | 36 Tasks / 6 Parts
🧪 GoogleTest ≥152 + pytest ≥840 + XCTest ≥15
🔧 Fixed: 5 Critical + 8 High + 12 Medium
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## 執行指令

1. **第一步必須是定義 notify + 發送啟動通知**（在讀其他文件之前）
2. **每個 Task 完成 → echo + notify**（36 次）
3. **每個 Part 完成 → echo + notify**（6 次）
4. **錯誤發生 → 立即 echo + notify**
5. **Part 0 必須 idempotent**（已搬遷的檔案跳過）
6. **pbxproj：** 6 Swift 檔案（含 BIMSceneBuilder.swift）
7. **審計報告:** `docs/audit-reports/Sprint22_AuditReport.md`
8. **不得修改 CLAUDE.md / SKILL.md**
9. **不得中途詢問用戶**

---

## 驗收標準

```
☐ 啟動通知已收到（Sprint 開始第一條 iMessage）
☐ Part 0: sprints/ + docs/audit-reports/ 整理完成
☐ xcodebuild BUILD SUCCEEDED
☐ GoogleTest ≥ 152 + pytest ≥ 840 + XCTest ≥ 15
☐ 5 Critical + 8 High issues 全修
☐ Info.plist: 2.9.0 / 22
☐ docs/audit-reports/Sprint22_AuditReport.md 產生
☐ git tag v2.9.0
☐ 每個 Task 都有 notify（36 次）
☐ 每個 Part 都有 notify（6 次）
☐ 最終完成通知已發送
```

---

*sprints/PROMPT_P22.md v3.0 | 2026-03-26 | 修復: notify 函數顯式定義 + 啟動通知最前置 + Part 0 idempotent*
