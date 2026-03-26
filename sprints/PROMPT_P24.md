# PROMPT_P24.md — Advanced BIM Features + CI/CD + Integration Testing

> **Sprint:** P24 | **目標版本:** v2.11.0 | **基於:** P23 (v2.10.0)
> **CLAUDE.md:** v1.17.0 | **SKILL.md:** v3.3（唯讀）
> **前置:** P23 完成（v2.10.0, ~1060+ tests）
> **範圍:** TBD Parts / TBD Tasks

---

## ★★★ 絕對第一步：定義 notify 函數 + 發送啟動通知 ★★★

> ⚠️ Claude Code `-p` 模式不載入 `.zshrc`，notify 函數不存在，必須顯式定義。
> ⚠️ 主要收件人: `+886972535899`（手機號碼，最優先）

```bash
# ===== ★★★ Sprint 絕對第一步：定義 notify 函數 ★★★ =====
notify() {
    local msg="$1"
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"+886972535899\" of targetService
            send \"$msg\" to targetBuddy
        end tell
    " 2>/dev/null || \
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"chchlin1018@icloud.com\" of targetService
            send \"$msg\" to targetBuddy
        end tell
    " 2>/dev/null || \
    osascript -e "display notification \"$msg\" with title \"PromptBIM\"" 2>/dev/null || \
    echo "[NOTIFY FALLBACK] $msg"
}
echo "✅ notify 函數已定義"

TASK_TOTAL=TBD
PART_TOTAL=TBD
TASK_DONE=0
PART_DONE=0

MSG="🏗️ PromptBIM Sprint P24 啟動
📋 Advanced BIM + CI/CD + Integration
🎯 TBD Tasks / TBD Parts → v2.11.0
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
echo "✅ 關鍵文件完整: CLAUDE=${CLAUDE_SIZE}B SKILL=${SKILL_SIZE}B"
```

---

## 環境檢查

```bash
if [ -n "$ANTHROPIC_API_KEY" ]; then
    MSG="⛔ PromptBIM Sprint 中止 — 偵測到 ANTHROPIC_API_KEY
🔧 修復: unset ANTHROPIC_API_KEY"
    echo "$MSG" && notify "$MSG" && exit 1
fi
echo "✅ 認證: Claude Max 訂閱"
```

---

## 必讀文件

```
1. 本文件 sprints/PROMPT_P24.md
2. docs/audit-reports/Sprint23_AuditReport.md ← P23 審計結果
3. SKILL.md ← v3.3 唯讀，不得修改
4. CLAUDE.md ← v1.17.0，絕對不得修改
5. TODO.md
```

---

## ★ 通知規則（本 Sprint 全程適用）★

> ⚠️ **遵守 CLAUDE.md v1.17.0：每個 Task/Part 啟動 ▶️ 和結束 ✅ 都必須 notify。**
> ⚠️ **主要收件人: +886972535899**

### Task 啟動通知 ▶️
```bash
MSG="🏗️ PromptBIM P24
▶️ Task ${TASK_NUM}/${TASK_TOTAL} 開始: ${TASK_DESCRIPTION}
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Task 結束通知 ✅
```bash
TASK_DONE=$((TASK_DONE + 1))
PCT=$((TASK_DONE * 100 / TASK_TOTAL))
MSG="🏗️ PromptBIM P24
✅ Task ${TASK_NUM}/${TASK_TOTAL} 完成: ${TASK_DESCRIPTION}
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Part 啟動通知 ▶️
```bash
MSG="🏗️ PromptBIM P24
▶️ Part ${PART} 開始: ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Part 結束通知 ✅
```bash
PART_DONE=$((PART_DONE + 1))
MSG="🏗️ PromptBIM P24 Part ${PART} ✅
📋 ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
⏭️ 下一步: Part ${NEXT_PART} (${NEXT_PART_TASKS} tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Task 失敗通知 ⚠️
```bash
MSG="🏗️ PromptBIM P24
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)...
📊 進度: ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Suggested Focus Areas for P24

### A. Advanced BIM Features
- Multi-building site plan generation
- Parking structure auto-generation
- Landscape design integration
- MEP routing optimization

### B. CI/CD Pipeline
- GitHub Actions workflow enhancement
- Automated test matrix (macOS 14/15)
- Coverage reporting
- Release automation

### C. Integration Testing
- End-to-end pipeline tests
- MCP server integration tests
- Cross-platform validation

### D. Performance
- Startup time optimization (target < 2s)
- Memory profiling
- Large model handling

---

## 驗收標準

```
☐ 啟動通知已收到（+886972535899）
☐ ★ 每 Task 有 ▶️ 啟動 + ✅ 結束 notify
☐ ★ 每 Part 有 ▶️ 啟動 + ✅ 結束 notify
☐ xcodebuild BUILD SUCCEEDED
☐ pytest 全部通過
☐ 文件版本同步
☐ 審計報告: docs/audit-reports/Sprint24_AuditReport.md
☐ git push + tag
☐ 下一個 PROMPT 已建立
☐ 最終完成 notify (100%)
```

---

*sprints/PROMPT_P24.md v1.0 | 2026-03-26*
*★ 主要收件人: +886972535899 | 備用: chchlin1018@icloud.com*
*★ 雙向通知: 每 Task/Part 啟動 ▶️ + 結束 ✅*
*CLAUDE.md: v1.17.0 | SKILL.md: v3.3*
