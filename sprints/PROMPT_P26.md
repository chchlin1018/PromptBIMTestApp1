# PROMPT_P26.md v1.0 — Testing Hardening + Quality Gates

> **Sprint:** P26 | **目標:** v2.13.0 | **基於:** P25 (v2.12.0)
> **CLAUDE.md:** v1.21.0 | **SKILL.md:** v3.7
> **範圍:** 3 Parts / 18 Tasks

---

## ★★★ 絕對第一步：完整函數定義 + 殭屍清理 ★★★

```bash
# ===== ★★★ Sprint 絕對第一步 ★★★ =====

# --- 1. notify ---
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

# --- 3. Task/Part 封裝函數 (CLAUDE.md v1.21.0 MANDATORY) ---
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
    PART_ID="$id"; PART_DESC="$desc"
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

# --- 4. 殭屍清理 + 環境 (P24b+P24e MANDATORY) ---
echo "🧹 清理殭屍 Python..."
pkill -f "python.*pytest" 2>/dev/null
pkill -f "python.*promptbim" 2>/dev/null
pkill -f "python.*PySide6" 2>/dev/null
sleep 1
export QT_QPA_PLATFORM=offscreen
echo "✅ 全部函數+環境已就緒"
```

---

## 啟動

```bash
SPRINT=26; TASK_TOTAL=18; PART_TOTAL=3; TASK_DONE=0; PART_DONE=0; PCT=0
check_mem || exit 1
git pull origin main 2>/dev/null
MEM=$(get_mem)
notify "🏗️ P26 啟動 | 18 Tasks/3 Parts → v2.13.0 | 💾${MEM}"

# 文件檢查
CLAUDE_SIZE=$(wc -c < CLAUDE.md 2>/dev/null|tr -d ' ')
SKILL_SIZE=$(wc -c < SKILL.md 2>/dev/null|tr -d ' ')
[ "$CLAUDE_SIZE" -lt 5000 ] && { notify "⛔ CLAUDE.md 損壞"; exit 1; }
[ "$SKILL_SIZE" -lt 20000 ] && { notify "⛔ SKILL.md 損壞"; exit 1; }
[ -n "$ANTHROPIC_API_KEY" ] && { notify "⛔ ANTHROPIC_API_KEY 衝突"; exit 1; }
echo "✅ 檢查通過"
```

---

## Part A: Test Coverage + Quality (6 Tasks)

```bash
part_start "A" "Test Coverage + Quality" 6

task_start 1 "Coverage 報告整合 CI (target 80%)"
task_done

task_start 2 "補充 agent tests (+6)"
task_done

task_start 3 "補充 land parser tests (+4)"
task_done

task_start 4 "補充 code compliance tests (+4)"
task_done

task_start 5 "Integration smoke test 強化"
task_done

task_start 6 "Mutation testing 試點"
task_done

part_done "Part B — Error Handling + Resilience (6 tasks)"
```

---

## Part B: Error Handling + Resilience (6 Tasks)

```bash
part_start "B" "Error Handling + Resilience" 6

task_start 7 "Retry 機制審查 + 增強"
task_done

task_start 8 "Error boundary 統一化"
task_done

task_start 9 "Timeout 保護 (全管線)"
task_done

task_start 10 "Input validation 強化"
task_done

task_start 11 "Graceful degradation 模式"
task_done

task_start 12 "Error handling tests (+5)"
task_done

part_done "Part C — CI/CD Enhancement (6 tasks)"
```

---

## Part C: CI/CD Enhancement (6 Tasks)

```bash
part_start "C" "CI/CD Enhancement" 6

task_start 13 "PR 自動檢查 (ruff + test + coverage)"
task_done

task_start 14 "Release workflow (自動 tag + changelog)"
task_done

task_start 15 "Dependency update 自動化"
task_done

task_start 16 "Test matrix 擴展 (Python 3.12)"
task_done

task_start 17 "Build cache 最佳化"
task_done

task_start 18 "CI/CD tests (+3)"
task_done

part_done "Sprint 完成"
```

---

## Sprint 完成

```bash
# ★ 最終 pytest（安全模式 — P24e 合規）★
export QT_QPA_PLATFORM=offscreen
pkill -f "python.*pytest" 2>/dev/null; sleep 1
python -m pytest tests/ \
    --timeout=10 \
    --ignore=tests/test_gui \
    --ignore=tests/test_mcp \
    --ignore=tests/test_e2e_integration.py \
    -x --tb=short -q
pkill -f "python.*pytest" 2>/dev/null

# 文件同步
# TODO/CHANGELOG/README/pyproject/__init__/Info.plist → v2.13.0

# 審計報告
# docs/audit-reports/Sprint26_AuditReport.md

# Git push + tag
git add -A && git commit -m "[P26] Sprint complete — v2.13.0" && git push origin main
git tag v2.13.0 && git push origin v2.13.0

# 產生 PROMPT_P27.md（合規 v1.21.0）

# 最終通知
MEM=$(get_mem)
notify "🏗️ P26 完成 🎉 | v2.13.0 | 18/18 Tasks | 100% ✅ | 💾${MEM}"
pkill -f "python.*pytest" 2>/dev/null
```

---

## pytest 安全規則（P24e 合規 — MANDATORY）

> ⚠️ **禁止同時跑多個 pytest 進程（Mac Mini 16GB 會 OOM）**
> ⚠️ **每次 pytest 前後都必須 pkill**

```bash
export QT_QPA_PLATFORM=offscreen
pkill -f "python.*pytest" 2>/dev/null; sleep 1
python -m pytest tests/ \
    --timeout=10 \
    --ignore=tests/test_gui \
    --ignore=tests/test_mcp \
    --ignore=tests/test_e2e_integration.py \
    -x --tb=short -q
pkill -f "python.*pytest" 2>/dev/null
```

---

*PROMPT_P26.md v1.0 | 2026-03-27*
*CLAUDE.md: v1.21.0 | SKILL.md: v3.7*
*★ 3 Parts / 18 Tasks*
*★ 完整合規: task_start/task_done + pkill + offscreen + ignore e2e*
