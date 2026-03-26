# PROMPT_P22.md — Senior Audit Full Remediation

> **Sprint:** P22 | **目標版本:** v2.9.0 | **基於:** AuditReport_Full_v2.8.0
> **CLAUDE.md:** v1.16.0 | **SKILL.md:** v3.2（唯讀）
> **前置:** P21 完成（v2.8.0, 957 tests）
> **範圍:** Part 0 清理 + 5 Critical + 8 High + 12 Medium + 5 Finalization = **36 Tasks / 6 Parts**

---

## ★★★ 絕對第一步：定義 notify 函數 + 發送啟動通知 ★★★

> ⚠️ **這是整個 Sprint 的第一個動作。Claude Code -p 模式不載入 .zshrc，所以 notify 函數不存在。**
> ⚠️ **必須在做任何事之前，先執行以下 bash 指令定義 notify 並發送啟動通知。**

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

# ===== ★★★ 立即發送啟動通知 ★★★ =====
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
4. CLAUDE.md ← v1.16.0 行為規範（絕對不得修改）
5. TODO.md ← 確認當前狀態
```

---

## ★ 通知規則（本 Sprint 全程適用）★

> ⚠️ **每個 Task 和 Part 完成後都必須 echo + notify。**
> ⚠️ **錯誤發生時立即 echo + notify，不等 3 次失敗。**

### Task 完成通知模板

```bash
MSG="🏗️ PromptBIM P22
✅ Task ${TASK_NUM}: ${TASK_DESCRIPTION}
📋 ${ISSUE_IDS_FIXED}
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

> ⚠️ **Idempotent — 已搬遷的檔案跳過。每步都 notify。**

### Task 1: 搬遷 Sprint Prompt 到 sprints/
```bash
MOVED=0
for f in PROMPT.md PROMPT_P*.md; do
    [ -f "$f" ] && git mv "$f" "sprints/$f" 2>/dev/null && MOVED=$((MOVED+1))
done
MSG="🏗️ PromptBIM P22
✅ Task 1: Moved $MOVED PROMPT files to sprints/
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Task 2: 搬遷 Audit Report 到 docs/audit-reports/
```bash
MOVED=0
for f in docs/reports/*AuditReport*.md; do
    [ -f "$f" ] && git mv "$f" "docs/audit-reports/$(basename $f)" 2>/dev/null && MOVED=$((MOVED+1))
done
[ -f "AuditReport.md" ] && git mv AuditReport.md docs/audit-reports/AuditReport_Legacy_P16.md 2>/dev/null && MOVED=$((MOVED+1))
[ -f "docs/audit-reports/AuditReport_03261630.md" ] && git mv "docs/audit-reports/AuditReport_03261630.md" "docs/audit-reports/AuditReport_Full_v2.8.0.md" 2>/dev/null
MSG="🏗️ PromptBIM P22
✅ Task 2: Moved $MOVED AuditReport files
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Task 3-6: 清理 + 驗證 + Commit
> 每個 Task 完成後都必須 echo + notify（同上模式）

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

> Task 7-13，每個完成後 echo + notify。詳細內容見先前版本。

### Part A 完成通知
```bash
MSG="🏗️ PromptBIM P22 Part A ✅
🔧 C++ Critical + Robustness (7 tasks)
✅ IFC thread safety + CMake + GIS + dlsym
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part B: Python Critical + High Fixes（8 Tasks）

> Task 14-21，每個完成後 echo + notify。

### Part B 完成通知
```bash
MSG="🏗️ PromptBIM P22 Part B ✅
🐍 Python Critical + High (8 tasks)
✅ Cache + DI + async + MEP + Cost
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part C: Swift Fixes + XCTest（5 Tasks）

> Task 22-26，每個完成後 echo + notify。

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

> Task 27-31，每個完成後 echo + notify。

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

> Task 32-36，每個完成後 echo + notify。

### Part E 完成通知
```bash
MSG="🏗️ PromptBIM P22 Part E ✅
📦 Finalization (5 tasks)
✅ Docs 8/8 + Build + Tagged v2.9.0
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

1. **第一步：定義 notify + 發送啟動通知**（在做任何事之前）
2. **每個 Task 完成 → echo + notify**
3. **每個 Part 完成 → echo + notify**
4. **錯誤發生 → 立即 echo + notify**
5. **Part 0 idempotent**（已搬的跳過）
6. **不得修改 CLAUDE.md / SKILL.md**
7. **不得中途詢問用戶**

---

## 驗收標準

```
☐ 啟動通知已收到（Sprint 第一條 iMessage）
☐ Part 0: 檔案整理完成
☐ xcodebuild BUILD SUCCEEDED
☐ GoogleTest ≥ 152 + pytest ≥ 840 + XCTest ≥ 15
☐ 5 Critical + 8 High issues 全修
☐ Info.plist: 2.9.0 / 22
☐ docs/audit-reports/Sprint22_AuditReport.md
☐ git tag v2.9.0
☐ 每個 Task 都有 notify
☐ 每個 Part 都有 notify
☐ 最終完成通知已發送
```

---

*sprints/PROMPT_P22.md v3.1 | 2026-03-26*
*notify: chchlin1018@icloud.com / +886972535899*
*P22 教訓: Claude Code -p 模式不載入 .zshrc，notify 必須顯式定義*
