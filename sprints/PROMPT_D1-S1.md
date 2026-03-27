# PROMPT_D1-S1.md — Demo-1 Sprint 1: 引擎強化

> **Sprint:** D1-S1 | **版本:** demo1-v0.1.0-alpha | **Tasks:** 15 | **Parts:** 3
> **目標:** AI 6場景 + Cost強化 + 零件庫擴充 + 4D機械 + MEP穿孔 + 變更差異
> **平台:** Mac Mini (M4)
> **前置:** W0 完成, v2.12.0 tagged
> **依賴:** CLAUDE.md v1.23.1 | SKILL.md v4.0 | PROJECT.md v1.3

---

```bash
# ===== ★★★ Sprint 絕對第一步：完整函數定義 ★★★ =====

SPRINT="D1-S1"
VERSION="demo1-0.1.0-alpha"
SPRINT_DESC="Demo-1 S1: AI場景 + Cost強化 + 4D機械 + MEP擴充"
TASK_TOTAL=15
TASK_DONE=0
PART_TOTAL=3
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
- **版本:** ${VERSION}
- **Tasks:** ${TASK_DONE}/${TASK_TOTAL}
- **記憶體:** $(get_mem)
- **錯誤:** ${errors:-無}
EOF
    git add PROJECT.md && git commit -m "[${SPRINT}] update PROJECT.md final status" && git push origin main 2>/dev/null
}

echo "🧹 清理殭屍..."
pkill -f "python.*pytest" 2>/dev/null
pkill -f "python.*promptbim" 2>/dev/null
pkill -f "python.*PySide6" 2>/dev/null
sleep 1
export QT_QPA_PLATFORM=offscreen
echo "✅ 全部函數+環境已就緒"

cat PROJECT.md | head -80
echo "--- PROJECT.md 已讀取 ---"
check_mem || exit 1
git pull origin main

MEM=$(get_mem)
MSG="🏗️ Zigma Sprint ${SPRINT} 啟動
📋 ${SPRINT_DESC}
🎯 ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts → ${VERSION}
💾 ${MEM}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
notify "$MSG"

[ $(wc -c < CLAUDE.md) -ge 5000 ] || { echo "❌ CLAUDE.md"; exit 1; }
[ $(wc -c < SKILL.md) -ge 20000 ] || { echo "❌ SKILL.md"; exit 1; }
[ -n "$ANTHROPIC_API_KEY" ] || { echo "❌ API KEY"; exit 1; }
echo "✅ 檢查通過"

# ============================================================
# Part A: AI + 場景 + 變更 (5 tasks)
# ============================================================
part_start "A" "AI 場景 + 變更強化" 5

task_start 1 "Planner 6 場景 prompt template"
# 修改 src/promptbim/agents/planner.py
# 加入 VILLA/FAB/DATACENTER/FACTORY/BUILDING/BRIDGE 6 個 prompt template
task_done

task_start 2 "Modifier 多輪累加變更強化"
# 修改 src/promptbim/agents/modifier.py (17KB)
# 強化 modify() 支援多輪累加：「加泳池」→「泳池改停車場」連續處理
task_done

task_start 3 "Orchestrator 串接 Cost+Schedule+4D"
# 修改 src/promptbim/agents/orchestrator.py (15KB)
# generate() 流程加入: Build → Cost → Schedule → 4D assign
task_done

task_start 4 "USD phase tag + MEP layer"
# 修改 src/promptbim/bim/usd_generator.py (9KB)
# 每個 Prim 加入 custom:phase + custom:mep_system
task_done

task_start 5 "BIM 模型轉換: IFC/FBX → USD"
# 新建 src/promptbim/bim/converter.py
task_done

part_done "Part B: 成本+零件庫"

# ============================================================
# Part B: 成本 + 零件庫 (5 tasks)
# ============================================================
part_start "B" "成本引擎 + 零件庫擴充" 5

task_start 6 "零件庫擴充: 3分類 100+ 零件"
# 修改 src/promptbim/bim/components/
# 現有 76 件 → 擴充到 150+
task_done

task_start 7 "零件庫搜尋 + 替代品 + 競合"
# 修改 src/promptbim/bim/components/registry.py
task_done

task_start 8 "Cost Engine 供應商明細 + 圖表升級"
# 修改 src/promptbim/bim/cost/estimator.py + cost_charts.py
task_done

task_start 9 "零件替換 → 成本即時重算"
# 修改 src/promptbim/bim/cost/estimator.py
task_done

task_start 10 "變更成本差異報告"
# 新建 src/promptbim/bim/cost/cost_delta.py
task_done

part_done "Part C: 4D+MEP"

# ============================================================
# Part C: 4D + MEP 擴充 (5 tasks)
# ============================================================
part_start "C" "4D 擴充 + MEP 強化" 5

task_start 11 "4D 開挖+架設動畫擴充"
# 修改 src/promptbim/bim/simulation/animator.py
task_done

task_start 12 "4D 施工機械 3D + 進場邏輯"
# 新建 assets/equipment/ 目錄
task_done

task_start 13 "4D 變更連動: 設計變更 → 4D 自動更新"
# 修改 src/promptbim/bim/simulation/scheduler.py
task_done

task_start 14 "MEP 擴充: 電力+HVAC+穿孔"
# 修改 src/promptbim/bim/mep/planner.py + systems.py
task_done

task_start 15 "變更工期差異 + 甘特圖對照"
# 新建 src/promptbim/bim/simulation/schedule_delta.py
task_done

part_done "Sprint 完成"

# ===== pytest =====
pkill -f "python.*pytest" 2>/dev/null; sleep 1
python -m pytest tests/ --timeout=10 --ignore=tests/test_gui --ignore=tests/test_mcp --ignore=tests/test_e2e_integration.py -x --tb=short -q
pkill -f "python.*pytest" 2>/dev/null

# ===== Sprint 結束 =====
sprint_finalize "✅" ""
git push origin main 2>/dev/null

MEM=$(get_mem)
MSG="🏗️ Zigma Sprint ${SPRINT} 完成 🎉
🏷️ ${VERSION} | ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts
📊 完成度: 100% ✅
💾 ${MEM}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
notify "$MSG"
pkill -f "python.*pytest" 2>/dev/null
echo "✅ Sprint ${SPRINT} 完成 → 下一步: PROMPT_D1-S2.md"
```

---

## 合規性自檢

```
☑ 函數定義: notify(v2 heredoc) + get_mem + check_mem + task_start + task_done + part_start + part_done + sprint_finalize
☑ 殭屍清理 + offscreen
☑ ★ 鐵律 1: 100% CLAUDE.md MANDATORY
☑ ★ 鐵律 2: 啟動讀取 PROJECT.md
☑ ★ 鐵律 3: task_done → PROJECT.md sed + sprint_finalize
☑ 通知多行 + 啟動順序 + pytest 安全
☑ 命名: [D1-S1] commit prefix
☑ 不修改 CLAUDE.md / SKILL.md
☑ notify log: /tmp/zigma-notify.log
```
