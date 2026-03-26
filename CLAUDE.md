# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.21.0 | **更新:** 2026-03-26
> **版本控制:** 本文件由人工維護，Claude Code 不得直接修改
> ⚠️ 標記 **[MANDATORY]** 的規則必須嚴格執行，不得跳過

---

## [MANDATORY] 歷史教訓（每個 Sprint 必讀）

| # | 事故 | 根因 | 規則 |
|---|------|------|------|
| 🔴 P18 | CLAUDE.md 被截斷 | Claude Code 擅自修改 | **絕對禁止修改 CLAUDE.md/SKILL.md** |
| 🔴 P22 | notify 不存在 | `-p` 不載入 .zshrc | **PROMPT 最前面顯式定義所有函數** |
| 🔴 P22.1 | 完成但沒 commit | 忘記 git push | **每個 Part 結束必須 commit+push** |
| 🔴 P24a | OOM 靜默中斷 | 16GB RAM 耗盡 | **check_mem + <1GB 暫停** |
| 🔴 P24b | 殭屍 Python 26GB | pytest GUI 建立 QApplication | **QT_QPA_PLATFORM=offscreen + pkill** |
| 🔴 P24d | **Task 通知全被跳過** | Claude Code 只發 Part 通知 | **★ task_start()/task_done() 封裝函數 ★** |
| 🟧 P24c | Git 遠端分歧 | Claude.ai 同時推 commit | **Sprint 前 git pull** |

---

## [MANDATORY] Sprint 啟動函數 — 絕對第一步

> ⚠️ 每個 PROMPT 最前面必須包含以下完整定義
> ⚠️ **★ v1.21.0: 新增 task_start/task_done/part_start/part_done 封裝函數 ★**
> ⚠️ **★ PROMPT 中每個 Task 必須用 `task_start N "描述"` 和 `task_done` 包夾 ★**

```bash
# ===== ★★★ Sprint 絕對第一步：完整函數定義 ★★★ =====

# --- notify ---
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

# --- 記憶體 ---
get_mem() {
    local ps=$(sysctl -n hw.pagesize 2>/dev/null || echo 4096)
    local tb=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
    local tg=$(echo "scale=1;$tb/1073741824"|bc 2>/dev/null||echo "?")
    local fp=$(vm_stat 2>/dev/null|awk '/Pages free/{gsub(/\./,"",$3);print $3}')
    local ip=$(vm_stat 2>/dev/null|awk '/Pages inactive/{gsub(/\./,"",$3);print $3}')
    local fb=$(((${fp:-0}+${ip:-0})*ps))
    local fg=$(echo "scale=1;$fb/1073741824"|bc 2>/dev/null||echo "?")
    local ug=$(echo "scale=1;($tb-$fb)/1073741824"|bc 2>/dev/null||echo "?")
    echo "${ug}/${tg}GB(free:${fg}GB)"
}
check_mem() {
    local m=$(get_mem); local f=$(echo "$m"|grep -oE 'free:[0-9.]+'|grep -oE '[0-9.]+')
    [ "$(echo "${f:-0}<1.0"|bc 2>/dev/null)" = "1" ] && { notify "⛔ OOM! 💾$m"; return 1; }
    [ "$(echo "${f:-0}<2.0"|bc 2>/dev/null)" = "1" ] && notify "⚠️ 記憶體偏低 💾$m"
    return 0
}

# --- ★★★ Task/Part 封裝函數 (v1.21.0 新增) ★★★ ---
# P24d 教訓: Claude Code 跳過 Task 通知，只發 Part 通知
# 解法: 用封裝函數強制每個 Task 前後都發 iMessage
task_start() {
    local num=$1; local desc="$2"
    TASK_NUM=$num; TASK_DESC="$desc"
    PCT=$((TASK_DONE * 100 / TASK_TOTAL))
    local m=$(get_mem)
    MSG="🏗️ P${SPRINT} ▶️ Task ${num}/${TASK_TOTAL}: ${desc}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${m} | $(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
task_done() {
    TASK_DONE=$((TASK_DONE + 1))
    PCT=$((TASK_DONE * 100 / TASK_TOTAL))
    MSG="🏗️ P${SPRINT} ✅ Task ${TASK_NUM}/${TASK_TOTAL}: ${TASK_DESC}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
$(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
part_start() {
    local id="$1"; local desc="$2"; local count=$3
    PART_ID="$id"; PART_DESC="$desc"; PART_TASKS=$count
    check_mem || { notify "⛔ P${SPRINT} OOM at Part ${id} 💾$(get_mem)"; exit 1; }
    local m=$(get_mem)
    MSG="🏗️ P${SPRINT} ▶️ Part ${id}: ${desc} (${count} tasks)
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${m} | $(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
part_done() {
    PART_DONE=$((PART_DONE + 1))
    PCT=$((TASK_DONE * 100 / TASK_TOTAL))
    local next="$1"
    git add -A && git commit -m "[P${SPRINT}] Part ${PART_ID}: ${PART_DESC}" 2>/dev/null && git push origin main 2>/dev/null
    MSG="🏗️ P${SPRINT} Part ${PART_ID} ✅ ${PART_DESC}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
⏭️ ${next} | $(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}

# --- 殭屍清理 + 環境 ---
echo "🧹 清理殭屍 Python..."
pkill -f "python.*pytest" 2>/dev/null
pkill -f "python.*promptbim" 2>/dev/null
pkill -f "python.*PySide6" 2>/dev/null
sleep 1
export QT_QPA_PLATFORM=offscreen
echo "✅ 全部函數+環境已就緒"
```

### PROMPT 中的使用方式（MANDATORY）

> ⚠️ **每個 Task 必須用 task_start / task_done 包夾，不可省略**

```bash
# ===== 正確寫法（MANDATORY）=====
task_start 1 "Generate Demo IFC"
# ... 實際執行 Task 1 的代碼 ...
task_done

task_start 2 "Generate Demo USDA"
# ... 實際執行 Task 2 的代碼 ...
task_done
```

```bash
# ===== 錯誤寫法（違規！）=====
# 直接執行 Task 沒有呼叫 task_start/task_done → 沒有通知
echo "Task 1..."
# ... 代碼 ...
```

---

## [MANDATORY] Sprint 啟動順序

```
1. 讀 PROMPT
2. ★ 定義函數(notify+get_mem+check_mem+task_start+task_done+part_start+part_done)
3. ★ 殭屍清理 + QT_QPA_PLATFORM=offscreen
4. ★ check_mem（<1GB 中止）
5. ★ git pull origin main
6. 啟動 notify（含 💾）
7. 文件檢查（CLAUDE ≥5000B, SKILL ≥20000B）
8. 環境檢查（ANTHROPIC_API_KEY）
9. 開始 Part A → Task 1
```

---

## [MANDATORY] pytest 安全規則

```bash
export QT_QPA_PLATFORM=offscreen
pkill -f "python.*pytest" 2>/dev/null; sleep 1
python -m pytest tests/ --timeout=10 --ignore=tests/test_gui --ignore=tests/test_mcp -x -m "not api and not slow" --tb=short -q
pkill -f "python.*pytest" 2>/dev/null
```

---

## [MANDATORY] 記憶體 / Git / 文件保護

| 規則 | 說明 |
|------|------|
| 記憶體 ≥2GB | 🟢 繼續 |
| 記憶體 1~2GB | 🟡 警告 |
| 記憶體 <1GB | 🔴 **暫停 Sprint** |
| Sprint 啟動 | `git pull origin main` |
| Part 結束 | `git add -A && git commit && git push` |
| Sprint 結束 | `git tag v{X} && git push --tags` |
| CLAUDE.md | ≥5000B，不可修改 |
| SKILL.md | ≥20000B，不可修改 |

---

## [MANDATORY] PROMPT 合規性檢查

```
☐ notify + get_mem + check_mem + task_start + task_done + part_start + part_done 函數定義
☐ 殭屍清理 (pkill) + export QT_QPA_PLATFORM=offscreen
☐ 啟動順序: 函數→清理→check_mem→git pull→notify→文件檢查→環境檢查
☐ ★ 每個 Task 用 task_start N "描述" 和 task_done 包夾（不可省略）★
☐ ★ 每個 Part 用 part_start ID "描述" N 和 part_done "下一步" 包夾 ★
☐ pytest: QT_QPA_PLATFORM=offscreen + --timeout=10 + --ignore=test_gui + -x
☐ Sprint 結束產生下一個 PROMPT（合規 v1.21.0）
☐ 不修改 CLAUDE.md / SKILL.md
```

---

## [MANDATORY] 執行流程（26 步）

```
 1. 讀 PROMPT → 2. 定義函數 → 3. pkill + offscreen
 4. check_mem → 5. git pull → 6. 啟動 notify(💾)
 7. 文件檢查 → 8. 環境檢查
 9. part_start → 10. task_start → 11. 執行 → 12. task_done
13. 重複 10-12 → 14. Part git commit+push → 15. part_done
16. 重複 9-15 → 17. 錯誤 notify(💾)
18. xcodebuild → 19. pytest(安全模式) → 20. pbxproj
21. 文件同步 → 22. 審計報告 → 23. git push+tag
24. 產生下一個 PROMPT → 25. Sprint ✅ notify → 26. pkill 清理
```

---

## 版本歷史

| 版本 | 變更 |
|------|------|
| v1.17.0 | 雙向通知 + +886972535899 |
| v1.18.0 | P24a OOM → get_mem + check_mem |
| v1.20.0 | P24b 殭屍 → pkill + offscreen + pytest 安全 |
| **v1.21.0** | **★ P24d Task 通知被跳過 → task_start/task_done 封裝函數強制執行 ★** |

---

*CLAUDE.md v1.21.0 | 2026-03-26*
*★ 核心: task_start()/task_done() 封裝函數 — 每個 Task 必須呼叫，不可省略*
*★ 主要收件人: +886972535899 | 備用: chchlin1018@icloud.com*
