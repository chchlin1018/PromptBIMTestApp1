# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.20.0 | **更新:** 2026-03-26
> **版本控制:** 本文件由人工維護，Claude Code 不得直接修改
> ⚠️ 標記 **[MANDATORY]** 的規則必須嚴格執行，不得跳過

---

## 開發前必讀順序

```
1. sprints/PROMPT_P{X}.md ← 當前 Sprint 執行指令（最重要）
2. SKILL.md                ← 專案 SSOT
3. TODO.md                 ← Sprint 狀態
4. CLAUDE.md               ← 本文件（行為規範）
```

---

## [MANDATORY] 歷史教訓（每個 Sprint 必讀）

| # | 事故 | 根因 | 規則 |
|---|------|------|------|
| 🔴 P18 | CLAUDE.md 被截斷 | Claude Code 擅自修改 | **絕對禁止修改 CLAUDE.md/SKILL.md** |
| 🔴 P22 | notify 不存在 | `-p` 不載入 .zshrc | **PROMPT 最前面顯式定義所有函數** |
| 🔴 P22.1 | 完成但沒 commit | 忘記 git push | **每個 Part 結束必須 commit+push** |
| 🔴 P24a | OOM 靜默中斷 | 16GB RAM 耗盡 | **check_mem + <1GB 暫停** |
| 🔴 P24b | 殭屍 Python 26GB | pytest GUI 建立 QApplication | **★ QT_QPA_PLATFORM=offscreen + pkill 清理 ★** |
| 🟧 P24c | Git 遠端分歧 | Claude.ai 同時推 commit | **Sprint 前 git pull** |
| 🟧 P23 | iMessage 要授權 | 第一次需按「允許」 | Sprint 前測試 iMessage |

---

## [MANDATORY] Sprint 啟動函數 + 環境設定 — 絕對第一步

> ⚠️ 每個 PROMPT 最前面必須包含：函數定義 + 殭屍清理 + 環境變數

```bash
# ===== ★★★ Sprint 絕對第一步 ★★★ =====

# --- 1. notify 函數 ---
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

# --- 2. 記憶體監控 ---
get_mem() {
    local page_size=$(sysctl -n hw.pagesize 2>/dev/null || echo 4096)
    local total_bytes=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
    local total_gb=$(echo "scale=1; $total_bytes / 1073741824" | bc 2>/dev/null || echo "?")
    local free_pages=$(vm_stat 2>/dev/null | awk '/Pages free/ {gsub(/\./,"",$3); print $3}')
    local inactive_pages=$(vm_stat 2>/dev/null | awk '/Pages inactive/ {gsub(/\./,"",$3); print $3}')
    local free_bytes=$(( (${free_pages:-0} + ${inactive_pages:-0}) * page_size ))
    local free_gb=$(echo "scale=1; $free_bytes / 1073741824" | bc 2>/dev/null || echo "?")
    local used_gb=$(echo "scale=1; ($total_bytes - $free_bytes) / 1073741824" | bc 2>/dev/null || echo "?")
    local pressure=$(memory_pressure 2>/dev/null | grep "System-wide" | awk '{print $NF}' || echo "unknown")
    echo "${used_gb}/${total_gb}GB (free:${free_gb}GB) pressure:${pressure}"
}

check_mem() {
    local MEM_INFO=$(get_mem)
    local free_gb=$(echo "$MEM_INFO" | grep -oE 'free:[0-9.]+' | grep -oE '[0-9.]+')
    if [ "$(echo "${free_gb:-0} < 1.0" | bc 2>/dev/null)" = "1" ]; then
        MSG="⛔ 記憶體不足！💾 ${MEM_INFO} — Sprint 暫停
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
        echo "$MSG" && notify "$MSG"; return 1
    elif [ "$(echo "${free_gb:-0} < 2.0" | bc 2>/dev/null)" = "1" ]; then
        MSG="⚠️ 記憶體偏低 💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
        echo "$MSG" && notify "$MSG"
    fi; return 0
}

# --- 3. ★★★ 殭屍 Python 清理 (v1.20.0) ★★★ ---
# P24b: pytest GUI 測試產生殭屍進程吃 26GB
echo "🧹 清理殭屍 Python..."
pkill -f "python.*pytest" 2>/dev/null
pkill -f "python.*promptbim" 2>/dev/null
pkill -f "python.*PySide6" 2>/dev/null
sleep 1
echo "✅ 殭屍清理完成"

# --- 4. ★★★ pytest 安全環境變數 (v1.20.0) ★★★ ---
# 禁止 PySide6 建立真正的 QApplication/OpenGL — 省數 GB 記憶體
export QT_QPA_PLATFORM=offscreen
echo "✅ QT_QPA_PLATFORM=offscreen"

echo "✅ 全部函數 + 環境已就緒"
```

### iMessage 收件人
```
★ 主要: +886972535899 | 備用: chchlin1018@icloud.com
```

---

## [MANDATORY] Sprint 啟動順序（不可調換）

```
1. 讀 PROMPT
2. ★ 定義函數 + 殭屍清理 + export QT_QPA_PLATFORM=offscreen
3. ★ check_mem（<1GB 中止）
4. ★ git pull origin main（防遠端分歧）
5. 啟動 notify（含 💾）
6. 關鍵文件檢查（CLAUDE ≥5000B, SKILL ≥20000B）
7. 環境檢查（ANTHROPIC_API_KEY 衝突）
8. 讀 SKILL.md, TODO.md
9. 開始 Task 1
```

---

## [MANDATORY] pytest 安全規則 (v1.20.0 新增)

> ⚠️ **P24b 根因: pytest 啟動 PySide6 QApplication → 每個 GUI 測試建立 OpenGL context → 殭屍進程吃 26GB**
> ⚠️ **此規則從 v1.20.0 起對所有 Sprint 強制執行**

### pytest 執行命令（MANDATORY — 所有 Sprint 必須使用此格式）

```bash
# ★★★ 標準 pytest 命令 — 所有 Sprint 統一使用 ★★★
export QT_QPA_PLATFORM=offscreen
python -m pytest tests/ \
    --timeout=10 \
    --ignore=tests/test_gui \
    --ignore=tests/test_mcp \
    -x \
    -m "not api and not slow and not gui" \
    --tb=short -q
```

### 參數說明

| 參數 | 用途 | 為何必要 |
|------|------|---------|
| `QT_QPA_PLATFORM=offscreen` | 禁止真正的 GUI 視窗 | **P24b: 省數 GB 記憶體** |
| `--timeout=10` | 每個 test 最多 10 秒 | 防止 GUI test 卡住 |
| `--ignore=tests/test_gui` | 跳過 GUI 測試 | GUI 測試需要真正的 display |
| `--ignore=tests/test_mcp` | 跳過 MCP 測試 | 需要外部服務 |
| `-x` | 第一個失敗就停 | 防止累積殭屍進程 |
| `-m "not api and not slow"` | 跳過需要 API 的測試 | 不消耗 API 額度 |

### Sprint 結束前的完整測試

```bash
export QT_QPA_PLATFORM=offscreen
# 先清理殭屍
pkill -f "python.*pytest" 2>/dev/null; sleep 1
# 執行測試
python -m pytest tests/ --timeout=10 --ignore=tests/test_gui --ignore=tests/test_mcp -x -m "not api and not slow" --tb=short -q
# 測試後再次清理
pkill -f "python.*pytest" 2>/dev/null
```

---

## [MANDATORY] 記憶體監控規則

| Free RAM | 狀態 | 動作 |
|----------|------|------|
| ≥ 2 GB | 🟢 正常 | 繼續 |
| 1~2 GB | 🟡 偏低 | 警告 |
| < 1 GB | 🔴 危險 | **暫停 Sprint + 通知** |

### Sprint 期間只保留
```
✅ Claude Code (~2.2 GB) | Terminal/tmux (~50 MB) | Messages (~100 MB) | Tailscale (~43 MB)
❌ Chrome / Notion / AnyDesk / 系統設定 / 活動監視器 → 關閉
```

---

## [MANDATORY] Git 安全規則

| # | 時機 | 動作 |
|---|------|------|
| 1 | Sprint 啟動 | `git pull origin main` |
| 2 | **每個 Part 結束** | `git add -A && git commit && git push` |
| 3 | Sprint 結束 | `git tag v{X} && git push --tags` |
| 4 | Task 失敗 3 次 | `git commit -m "wip: partial"` |

---

## [MANDATORY] 通知規則

| # | 時機 | 內容 |
|---|------|------|
| 1 | Sprint 啟動 | 總覽 + 💾 |
| 2 | Task ▶️ 啟動 | 描述 + 進度% + 💾 |
| 3 | Task ✅ 結束 | 描述 + 進度% |
| 4 | Part ▶️ 啟動 | check_mem + 描述 + 💾 |
| 5 | Part ✅ 結束 | 進度 + ⏭️ + git push |
| 6 | 失敗/中斷 | 錯誤 + 💾 |
| 7 | Sprint 完成 | 100% + tests + 💾 |

### 通知模板

#### Task ▶️（含💾）
```bash
PCT=$((TASK_DONE * 100 / TASK_TOTAL)); MEM_INFO=$(get_mem)
MSG="🏗️ P${SPRINT} ▶️ Task ${TASK_NUM}/${TASK_TOTAL}: ${TASK_DESCRIPTION}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${MEM_INFO} | $(hostname -s) $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Task ✅
```bash
TASK_DONE=$((TASK_DONE + 1)); PCT=$((TASK_DONE * 100 / TASK_TOTAL))
MSG="🏗️ P${SPRINT} ✅ Task ${TASK_NUM}/${TASK_TOTAL}: ${TASK_DESCRIPTION}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
$(hostname -s) $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Part ▶️（check_mem + 💾）
```bash
check_mem || { notify "⛔ P${SPRINT} OOM at Part ${PART} 💾 $(get_mem)"; exit 1; }
MEM_INFO=$(get_mem)
MSG="🏗️ P${SPRINT} ▶️ Part ${PART}: ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${MEM_INFO} | $(hostname -s) $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Part ✅（git commit + push）
```bash
PART_DONE=$((PART_DONE + 1)); PCT=$((TASK_DONE * 100 / TASK_TOTAL))
git add -A && git commit -m "[P${SPRINT}] Part ${PART}: ${PART_DESCRIPTION}" && git push origin main 2>/dev/null
MSG="🏗️ P${SPRINT} Part ${PART} ✅ ${PART_DESCRIPTION}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
⏭️ ${NEXT_PART} | $(hostname -s) $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## [MANDATORY] 關鍵文件保護

```bash
CLAUDE_SIZE=$(wc -c < CLAUDE.md 2>/dev/null | tr -d ' ')
SKILL_SIZE=$(wc -c < SKILL.md 2>/dev/null | tr -d ' ')
[ "$CLAUDE_SIZE" -lt 5000 ] 2>/dev/null || [ "$SKILL_SIZE" -lt 20000 ] 2>/dev/null && {
    notify "⛔ 文件損壞！CLAUDE=${CLAUDE_SIZE}B SKILL=${SKILL_SIZE}B"; exit 1; }
```

---

## [MANDATORY] PROMPT 合規性檢查

```
☐ notify + get_mem + check_mem 函數定義
☐ ★ 殭屍 Python 清理 (pkill) ★
☐ ★ export QT_QPA_PLATFORM=offscreen ★
☐ check_mem → git pull → 啟動通知(💾) → 文件檢查 → 環境檢查
☐ 每 Task: ▶️(💾) + ✅ notify
☐ 每 Part: check_mem + ▶️(💾) + ✅(git commit+push + ⏭️) notify
☐ pytest: --timeout=10 --ignore=test_gui -x + QT_QPA_PLATFORM=offscreen
☐ 失敗/中斷 notify 含 💾
☐ Sprint 結束產生下一個 PROMPT（合規 v1.20.0）
☐ 不修改 CLAUDE.md / SKILL.md
```

---

## [MANDATORY] Sprint 執行流程（26 步）

```
 1. 讀 PROMPT → 2. 定義函數 + pkill 殭屍 + QT_QPA_PLATFORM=offscreen
 3. check_mem(<1GB 中止) → 4. git pull origin main
 5. 啟動 notify(💾) → 6. 文件檢查 → 7. 環境檢查 → 8. 讀 SKILL/TODO
 9. Part ▶️ notify(check_mem+💾)
10. Task ▶️ notify(get_mem+💾) → 11. 執行 Task → 12. Task ✅ notify
13. 重複 10-12 → 14. Part git commit+push → 15. Part ✅ notify(⏭️)
16. 重複 9-15 → 17. 錯誤 notify(💾)
18. xcodebuild → 19. pytest(offscreen+timeout+ignore_gui+-x) → 20. pbxproj
21. 文件同步 → 22. 審計報告 → 23. git push+tag
24. 產生下一個 PROMPT → 25. Sprint ✅ notify(100%+💾) → 26. pkill 清理
```

---

## 版本演進歷史

| 版本 | 關鍵變更 |
|------|----------|
| v1.14.0 | 🔴 P18: 文件截斷 → 寫保護 |
| v1.16.0~v1.16.2 | notify 顯式定義 + 文件保護 + 進度 |
| v1.17.0 | 雙向通知 + +886972535899 |
| v1.18.0 | 🔴 P24a OOM → get_mem + check_mem |
| v1.19.0 | 歷史教訓 + Git 安全 + 26 步 |
| **v1.20.0** | **🔴 P24b 殭屍 Python → pkill 清理 + QT_QPA_PLATFORM=offscreen + pytest 安全規則** |

---

*CLAUDE.md v1.20.0 | 2026-03-26*
*★ v1.20.0: pkill 殭屍 + QT_QPA_PLATFORM=offscreen + pytest --timeout=10 --ignore=test_gui -x*
*★ 主要收件人: +886972535899 | 備用: chchlin1018@icloud.com*
