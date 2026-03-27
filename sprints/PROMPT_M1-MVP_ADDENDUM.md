# PROMPT_M1-MVP_ADDENDUM.md — 強化通知 + 錯誤處理 + 記憶體監控規則

> **適用:** PROMPT_M1-MVP.md 的補充規則，優先級等同 CLAUDE.md [MANDATORY]
> **版本:** v1.0 | 2026-03-28

---

## ★★★ [MANDATORY] 通知密度規則 ★★★

### 每個 Task 必須發出 2 條 iMessage

```
task_start N "描述"   → 📱 iMessage #1: ▶️ Task N 開始
  ... 執行工作 ...
task_done             → 📱 iMessage #2: ✅ Task N 完成
```

**絕對不可以跳過任何一個 task_start 或 task_done。** 68 Tasks = 136 條 Task 通知。

### 每個 Part 必須發出 2 條 iMessage

```
part_start "X" "描述" N  → 📱 iMessage: ▶️ Part X 開始
  ... N 個 tasks ...
part_done "下一個"        → 📱 iMessage: ✅ Part X 完成 + git push
```

9 Parts = 18 條 Part 通知。

### Sprint 啟動/完成各 1 條

**總計預期: ~156+ 條 iMessage**

### 額外通知時機（越多越好）

| 時機 | 必須 notify |
|------|-----------|
| cmake build 成功 | ✅ `notify "🔨 cmake build 成功"` |
| cmake build 失敗 | ✅ `notify "❌ cmake build 失敗: $ERROR"` |
| ctest 結果 | ✅ `notify "🧪 ctest: N/M PASS"` |
| pytest 結果 | ✅ `notify "🧪 pytest: N PASS"` |
| git tag 建立 | ✅ `notify "🏷️ tag xxx 已建立"` |
| git push 成功 | ✅ `notify "📤 Part X pushed to GitHub"` |
| 記憶體 < 2GB | ✅ `notify "⚠️ 記憶體偏低 💾..."` |
| 記憶體 < 1GB | ✅ `notify "⛔ OOM!..."` + **暫停** |

---

## ★★★ [MANDATORY] 錯誤處理規則 ★★★

### 遇到任何錯誤必須做 3 件事

```bash
# 1. 立即 notify 錯誤詳情
ERR_MSG="❌ P${SPRINT} Task ${TASK_NUM} 失敗
🔍 錯誤: ${ERROR_DETAIL}
💾 $(get_mem) | $(hostname -s) $(date '+%m/%d %H:%M')"
notify "$ERR_MSG"

# 2. 記錄到錯誤日誌
echo "$ERR_MSG" >> /tmp/zigma-m1-errors.log

# 3. 記錄到 PROJECT_STATUS.md
cat >> docs/PROJECT_STATUS.md << ERREOF

### ❌ Error at Task ${TASK_NUM} — $(date '+%Y-%m-%d %H:%M')
- **Task:** ${TASK_DESC}
- **錯誤:** ${ERROR_DETAIL}
- **記憶體:** $(get_mem)
ERREOF
git add docs/PROJECT_STATUS.md && git commit -m "[error] Task ${TASK_NUM}: ${TASK_DESC}" && git push origin main 2>/dev/null
```

### 錯誤後的決策

| 錯誤類型 | 處理 |
|----------|------|
| cmake/build 失敗 | 嘗試修復 → 重試 → 失敗 2 次就 notify + 跳到下一個 Task |
| ctest/pytest 部分失敗 | notify 失敗數量 → 繼續（不阻塞） |
| Python import 失敗 | notify 詳細錯誤 → 嘗試 pip install → 重試 |
| OOM (< 1GB) | **立即暫停** → notify → pkill cleanup → check_mem → 恢復時 notify |
| git push 失敗 | git pull --rebase → 重試 → 失敗就 notify 繼續 |
| QProcess crash | notify → 自動重啟 → 繼續 |

### Sprint 非正常結束（OOM/斷線/crash）

```bash
# 必須執行（即使在 trap EXIT 中）
MEM=$(get_mem)
MSG="⛔ P${SPRINT} 非正常結束
📊 完成: ${TASK_DONE}/${TASK_TOTAL} (${PCT}%)
💾 ${MEM}
🔍 原因: ${EXIT_REASON}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')
💡 可從 Task $((TASK_DONE+1)) 繼續"
notify "$MSG"

# 更新 PROJECT_STATUS.md
cat >> docs/PROJECT_STATUS.md << ABORTEOF

### ⚠️ Sprint M1-MVP 中斷 — $(date '+%Y-%m-%d %H:%M')
- **進度:** ${TASK_DONE}/${TASK_TOTAL} (${PCT}%)
- **停在:** Task ${TASK_NUM}: ${TASK_DESC}
- **原因:** ${EXIT_REASON}
- **記憶體:** ${MEM}
ABORTEOF
git add -A && git commit -m "[abort] M1-MVP at Task ${TASK_NUM}" && git push origin main 2>/dev/null
```

---

## ★★★ [MANDATORY] 記憶體監控規則 ★★★

### 檢查頻率

| 時機 | 動作 |
|------|------|
| 每個 Part 開始 | `check_mem` (已在 part_start 中) |
| 每個 Task 開始 | `task_start` 已包含 `get_mem` 顯示 |
| cmake build 前 | `check_mem` |
| pytest/ctest 前 | `check_mem` + `pkill` 清理 |
| 每 10 個 Task | 額外 `check_mem` + notify 記憶體報告 |

### 每 10 個 Task 的記憶體報告

```bash
# 在 Task 10, 20, 30, 40, 50, 60 後額外發送
if [ $((TASK_DONE % 10)) -eq 0 ]; then
    MEM=$(get_mem)
    notify "📊 M1-MVP 進度報告
✅ ${TASK_DONE}/${TASK_TOTAL} (${PCT}%)
💾 ${MEM}
⏱️ $(date '+%m/%d %H:%M')"
fi
```

### cmake build 前的記憶體保護

```bash
# 每次 cmake --build 前
check_mem || { notify "⛔ build 前 OOM 💾$(get_mem)"; exit 1; }
pkill -f "python.*pytest" 2>/dev/null  # 確保沒有殭屍
```

---

## ★★★ [MANDATORY] Git 上傳規則 ★★★

### 每個 Part 結束必須 git push

`part_done()` 函數已包含:
```bash
git add -A && git commit -m "[P${SPRINT}] Part ${PART_ID}: ${PART_DESC}" && git push origin main
```

### push 失敗的處理

```bash
git push origin main 2>/dev/null || {
    notify "⚠️ git push 失敗，嘗試 rebase..."
    git pull --rebase origin main
    git push origin main 2>/dev/null || notify "❌ git push 仍然失敗"
}
```

### Tag 推送

3 個 tag 各自 push:
```bash
# Part C 後
git tag mvp-v0.1.0-alpha && git push origin mvp-v0.1.0-alpha

# Part F 後
git tag mvp-v0.1.0-beta && git push origin mvp-v0.1.0-beta

# Part I 後
git tag mvp-v0.1.0 && git push origin mvp-v0.1.0
```

---

## 通知統計預估

| 類型 | 數量 |
|------|------|
| Sprint 啟動/完成 | 2 |
| Part 啟動/完成 | 18 |
| Task 啟動/完成 | 136 |
| cmake build 結果 | ~10 |
| ctest/pytest 結果 | ~10 |
| git tag 通知 | 3 |
| 每10T 進度報告 | 6 |
| 錯誤通知 | 看運氣 |
| **最低總計** | **~185+** |

---

*PROMPT_M1-MVP_ADDENDUM.md v1.0 | 2026-03-28*
*通知密度最大化 + 錯誤必須 notify + 記憶體每 Task 監控*
