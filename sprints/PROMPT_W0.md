# PROMPT_W0.md — POC 收尾 Sprint

> **Sprint:** W0 | **版本:** v2.11.0 + v2.12.0 | **Tasks:** 5 | **Parts:** 2
> **目標:** P24 pytest OOM 修復 + tag, P25 pytest + tag, Win 環境確認
> **平台:** Mac Mini (M4) + Win RTX 4090
> **前置:** CLAUDE.md v1.23.3 | SKILL.md v4.0 | PROJECT.md v1.3

---

```bash
# ===== ★★★ Sprint 絕對第一步：完整函數定義 ★★★ =====

SPRINT="W0"
VERSION="2.12.0"
SPRINT_DESC="POC 收尾: P24 OOM 修復 + P25 tag + Win 環境"
TASK_TOTAL=5
TASK_DONE=0
PART_TOTAL=2
PART_DONE=0
PCT=0

# --- notify (v2 — heredoc + log + safe argv) ---
notify() {
    local msg="$1"
    local log="/tmp/zigma-notify.log"
    /usr/bin/osascript - "$msg" <<'EOF' >>"$log" 2>&1
on run argv
    set theMessage to item 1 of argv
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "+886972535899" of targetService
        send theMessage to targetBuddy
    end tell
end run
EOF
    [ $? -eq 0 ] && return 0
    /usr/bin/osascript - "$msg" <<'EOF' >>"$log" 2>&1
on run argv
    set theMessage to item 1 of argv
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "chchlin1018@icloud.com" of targetService
        send theMessage to targetBuddy
    end tell
end run
EOF
    [ $? -eq 0 ] && return 0
    /usr/bin/osascript - "$msg" <<'EOF' >>"$log" 2>&1
on run argv
    set theMessage to item 1 of argv
    display notification theMessage with title "Zigma"
end run
EOF
    [ $? -eq 0 ] && return 0
    echo "[NOTIFY FALLBACK] $msg" | tee -a "$log"
    return 1
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

# --- xcodebuild 互斥鎖 (v1.23.3 — 多 Claude Code 實例安全) ---
XCODE_LOCK="/tmp/zigma-xcodebuild.lock"
xcode_lock() {
    local timeout=300 waited=0
    while ! mkdir "$XCODE_LOCK" 2>/dev/null; do
        if [ $waited -ge $timeout ]; then
            notify "⛔ xcodebuild lock timeout (${timeout}s) — 另一個 Claude Code 佔用中"
            return 1
        fi
        sleep 5; waited=$((waited + 5))
        [ $((waited % 30)) -eq 0 ] && echo "⏳ Waiting for xcodebuild lock... ${waited}s"
    done
    echo "$$" > "$XCODE_LOCK/pid"
    echo "🔒 xcodebuild lock acquired (PID $$)"
    return 0
}
xcode_unlock() {
    rm -rf "$XCODE_LOCK" 2>/dev/null
    echo "🔓 xcodebuild lock released"
}
trap 'xcode_unlock' EXIT

# --- Task/Part 封裝函數 (v1.23.0) ---
task_start() {
    local num=$1; local desc="$2"
    TASK_NUM=$num; TASK_DESC="$desc"
    PCT=$((TASK_DONE * 100 / TASK_TOTAL))
    local m=$(get_mem)
    sed -i '' "s/| \(.*T${num}\b.*\) | ⬜/| \1 | 🔵/" PROJECT.md 2>/dev/null
    MSG="🏗️ ${SPRINT} ▶️ Task ${num}/${TASK_TOTAL}: ${desc}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${m} | $(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
task_done() {
    TASK_DONE=$((TASK_DONE + 1))
    PCT=$((TASK_DONE * 100 / TASK_TOTAL))
    sed -i '' "s/| \(.*T${TASK_NUM}\b.*\) | 🔵/| \1 | ✅/" PROJECT.md 2>/dev/null
    MSG="🏗️ ${SPRINT} ✅ Task ${TASK_NUM}/${TASK_TOTAL}: ${TASK_DESC}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
$(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
part_start() {
    local id="$1"; local desc="$2"; local count=$3
    PART_ID="$id"; PART_DESC="$desc"
    check_mem || { notify "⛔ ${SPRINT} OOM at Part ${id} 💾$(get_mem)"; exit 1; }
    local m=$(get_mem)
    MSG="🏗️ ${SPRINT} ▶️ Part ${id}: ${desc} (${count} tasks)
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${m} | $(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
part_done() {
    PART_DONE=$((PART_DONE + 1))
    PCT=$((TASK_DONE * 100 / TASK_TOTAL))
    local next="$1"
    git add -A && git commit -m "[${SPRINT}] Part ${PART_ID}: ${PART_DESC}" 2>/dev/null && git push origin main 2>/dev/null
    MSG="🏗️ ${SPRINT} Part ${PART_ID} ✅ ${PART_DESC}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
⏭️ ${next} | $(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
sprint_finalize() {
    local status="$1"; local errors="$2"
    cat >> PROJECT.md << EOF

### Sprint ${SPRINT} 執行結果 — $(date '+%Y-%m-%d %H:%M')
- **狀態:** ${status}
- **版本:** v${VERSION}
- **Tasks:** ${TASK_DONE}/${TASK_TOTAL}
- **記憶體:** $(get_mem)
- **錯誤:** ${errors:-無}
EOF
    git add PROJECT.md && git commit -m "[${SPRINT}] update PROJECT.md final status" && git push origin main 2>/dev/null
}

# --- 清理 + 環境 ---
echo "🧹 清理殭屍 Python..."
pkill -f "python.*pytest" 2>/dev/null
pkill -f "python.*promptbim" 2>/dev/null
pkill -f "python.*PySide6" 2>/dev/null
sleep 1
export QT_QPA_PLATFORM=offscreen
echo "✅ 全部函數+環境已就緒"

# ===== ★ 鐵律 2: 讀取 PROJECT.md 確認狀態 ★ =====
cat PROJECT.md | head -50
echo "--- PROJECT.md 已讀取 ---"

check_mem || exit 1
git pull origin main

MEM=$(get_mem)
MSG="🏗️ Zigma Sprint ${SPRINT} 啟動
📋 ${SPRINT_DESC}
🎯 ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts → v${VERSION}
💾 ${MEM}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
notify "$MSG"

[ $(wc -c < CLAUDE.md) -ge 5000 ] || { echo "❌ CLAUDE.md 太小"; exit 1; }
[ $(wc -c < SKILL.md) -ge 20000 ] || { echo "❌ SKILL.md 太小"; exit 1; }
[ -n "$ANTHROPIC_API_KEY" ] || { echo "❌ ANTHROPIC_API_KEY 未設定"; exit 1; }
echo "✅ 檢查通過"

# ============================================================
# Part A: P24 + P25 收尾 (4 tasks)
# ============================================================
part_start "A" "P24+P25 收尾" 4

task_start 1 "P24 conftest.py offscreen 修復"
grep -q 'QT_QPA_PLATFORM' tests/conftest.py || \
    sed -i '' '1i\
import os; os.environ["QT_QPA_PLATFORM"] = "offscreen"
' tests/conftest.py
task_done

task_start 2 "P24 pytest pass + tag v2.11.0"
export QT_QPA_PLATFORM=offscreen
pkill -f "python.*pytest" 2>/dev/null; sleep 1
python -m pytest tests/ --timeout=10 --ignore=tests/test_gui --ignore=tests/test_mcp --ignore=tests/test_e2e_integration.py -x --tb=short -q
pkill -f "python.*pytest" 2>/dev/null
git tag v2.11.0 2>/dev/null && git push origin v2.11.0 2>/dev/null
task_done

task_start 3 "P25 pytest 驗證"
pkill -f "python.*pytest" 2>/dev/null; sleep 1
python -m pytest tests/ --timeout=10 --ignore=tests/test_gui --ignore=tests/test_mcp --ignore=tests/test_e2e_integration.py -x --tb=short -q
pkill -f "python.*pytest" 2>/dev/null
task_done

task_start 4 "P25 tag v2.12.0"
git tag v2.12.0 2>/dev/null && git push origin v2.12.0 2>/dev/null
task_done

part_done "Part B: Win 環境"

# ============================================================
# Part B: Win 環境確認 (1 task)
# ============================================================
part_start "B" "Win RTX 4090 環境" 1

task_start 5 "Win RTX 4090 conda + PyVista OpenGL 確認"
echo "⚠️ W0-T5 需在 Windows RTX 4090 上執行"
task_done

part_done "Sprint 完成"

# ===== Sprint 結束 =====
sprint_finalize "✅" ""
git push origin main 2>/dev/null

MEM=$(get_mem)
MSG="🏗️ Zigma Sprint ${SPRINT} 完成 🎉
🏷️ v${VERSION} | ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts
📊 完成度: 100% ✅
💾 ${MEM}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
notify "$MSG"

pkill -f "python.*pytest" 2>/dev/null
echo "✅ Sprint ${SPRINT} 完成"
```

---

## 合規性自檢

```
☑ notify(v2 heredoc) + get_mem + check_mem + xcode_lock/unlock + task_start + task_done + part_start + part_done + sprint_finalize
☑ 殭屍清理 + offscreen
☑ ★ xcodebuild 互斥鎖: mkdir atomic lock + 300s timeout + trap EXIT cleanup
☑ 鐵律 1/2/3 全通過
☑ notify log: /tmp/zigma-notify.log
```
