# PROMPT_D1-S2.md — Demo-1 Sprint 2: GUI + 多場景 + 展示

> **Sprint:** D1-S2 | **版本:** demo1-v0.1.0 | **Tasks:** 14 | **Parts:** 3
> **目標:** GUI 整合 + 4D Player + 多場景 + 零件庫 GUI + TSMC 展示準備
> **平台:** Win RTX 4090 + Mac Mini
> **前置:** D1-S1 完成
> **依賴:** CLAUDE.md v1.23.1 | SKILL.md v4.0 | PROJECT.md v1.3

---

```bash
# ===== ★★★ Sprint 絕對第一步 ★★★ =====

SPRINT="D1-S2"
VERSION="demo1-v0.1.0"
SPRINT_DESC="Demo-1 S2: GUI + 4D Player + 多場景 + TSMC 展示"
TASK_TOTAL=14
TASK_DONE=0
PART_TOTAL=3
PART_DONE=0
PCT=0

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
    osascript -e "display notification \"$msg\" with title \"Zigma\"" 2>/dev/null || \
    echo "[NOTIFY FALLBACK] $msg"
}
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

echo "🧹 清理櫨屍..."
pkill -f "python.*pytest" 2>/dev/null
pkill -f "python.*promptbim" 2>/dev/null
pkill -f "python.*PySide6" 2>/dev/null
sleep 1
export QT_QPA_PLATFORM=offscreen
echo "✅ 函數+環境已就緒"

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
# Part A: GUI 面板升級 (5 tasks)
# ============================================================
part_start "A" "GUI + 3D + 4D Player" 5

task_start 1 "Win RTX 4090 部署 + GPU 渲染確認"
# Windows: conda activate promptbim && python -c "import pyvista; p=pyvista.Plotter(); print(p.render_window)"
# 確認 OpenGL GPU 加速
task_done

task_start 2 "GUI 一氣呵成: Prompt→3D→Cost→4D"
# 修改 src/promptbim/gui/main_window.py
# 串接: ChatPanel → ModelView + CostPanel + SimulationTab
# 生成後自動切換到 3D tab
task_done

task_start 3 "3D: 樓層切換 + 點擊零件 + MEP分層"
# 修改 src/promptbim/gui/model_view.py + mep_toggle.py
# 點擊 mesh → 顯示零件名稱 + 供應商 + 單價
# MEP 圖層 checkbox 加入 HVAC
task_done

task_start 4 "4D Player: 甘特圖 ↔ 4D 聯動"
# 修改 src/promptbim/gui/simulation_tab.py
# 點擊甘特圖 phase → 4D slider 跳到對應週
# 加入施工機械顯示開關
task_done

task_start 5 "變更對照面板: 3D+Cost+Schedule+4D"
# 新建 src/promptbim/gui/delta_panel.py
# 並排顯示: before/after 3D + 成本差異 + 工期差異
task_done

part_done "Part B: 場景+零件庫"

# ============================================================
# Part B: 多場景 + 零件庫 GUI (4 tasks)
# ============================================================
part_start "B" "場景模板 + 零件庫 GUI" 4

task_start 6 "場景 S1: 3層別墅+泳池"
# 新建 src/promptbim/bim/templates/villa.py
# 參考現有 factory.py (P10) 格式
# 包含: 1F客廳+泳池, 2F臥室, 3F書房
task_done

task_start 7 "場景 S2: 半導體廠房 + S3: 數據中心"
# 新建 src/promptbim/bim/templates/datacenter.py
# 廠房場景用現有 factory.py 擴充
# 數據中心: 機架室 + 冷却通道 + 電力室
task_done

task_start 8 "零件庫 GUI: 3分類瀏覽 + 搜尋 + 替換"
# 新建 src/promptbim/gui/asset_browser.py
# QTreeWidget: 家用/建築/工廠 3 分類
# 點擊零件 → 顯示規格+供應商+單價
# 「替換」按鈕 → 調用 cost swap
task_done

task_start 9 "台灣法規 + 匯出擴充"
# 修改 codes/ + gui/
# 容積/建蔽/高度檢查強化
# 匯出加入: Cost CSV + Schedule JSON + BOM
task_done

part_done "Part C: 展示準備"

# ============================================================
# Part C: 展示準備 (5 tasks)
# ============================================================
part_start "C" "展示準備" 5

task_start 10 "3 場景 E2E 測試"
# S1(別墅) + S2(廠房) + S3(數據中心) 全流程
# NL → BIM → Cost → Schedule → 4D → 變更 → 對照
task_done

task_start 11 "效能: 全流程 < 3 分鐘"
# 計時測試各場景
task_done

task_start 12 "Demo 腳本 7min + 排練"
# 更新 docs/DEMO_SCRIPT.md (已有 P12 版本)
task_done

task_start 13 "TSMC 簡報 10頁 + 螢幕錄影"
# Keynote/PPTX + OBS/ScreenFlow 錄影
task_done

task_start 14 "Demo-1 審計 + PROJECT.md + tag"
# 審計報告 + git tag demo1-v0.1.0
git tag demo1-v0.1.0 2>/dev/null && git push origin demo1-v0.1.0 2>/dev/null
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
🌟 Demo-1 Ready for TSMC!
💾 ${MEM}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
notify "$MSG"
pkill -f "python.*pytest" 2>/dev/null
echo "★ Demo-1 完成! Tag: demo1-v0.1.0 ★"
echo "→ 下一步: Demo-2 (Omniverse → Revit → 建照)"
```

---

## 合規性自檢

```
☑ 函數定義: notify + get_mem + check_mem + task_start + task_done + part_start + part_done + sprint_finalize
☑ 櫨屍清理 + offscreen
☑ ★ 鐵律 1: 100% CLAUDE.md MANDATORY
☑ ★ 鐵律 2: 啟動讀取 PROJECT.md
☑ ★ 鐵律 3: task_done → PROJECT.md sed
☑ ★ 鐵律 3: sprint_finalize()
☑ 通知多行 + 啟動順序 + pytest 安全
☑ 命名: [D1-S2] commit prefix
☑ Sprint 結束 tag: demo1-v0.1.0
☑ 不修改 CLAUDE.md / SKILL.md
```
