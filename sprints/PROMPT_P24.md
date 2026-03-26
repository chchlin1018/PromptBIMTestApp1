# PROMPT_P24.md v4.0 — Demo 3D + Advanced BIM (CLAUDE.md v1.21.0 合規)

> **Sprint:** P24 | **目標:** v2.11.0 | **CLAUDE.md:** v1.21.0 | **SKILL.md:** v3.6
> **★ v4.0 核心: task_start/task_done 封裝函數 — 每個 Task 必須呼叫 ★**

---

## ★★★ 絕對第一步：完整函數定義 + 殭屍清理 ★★★

```bash
# ===== 函數定義 =====
notify() {
    local msg="$1"
    osascript -e "tell application \"Messages\" to send \"$msg\" to participant \"+886972535899\" of (1st account whose service type = iMessage)" 2>/dev/null || \
    osascript -e "tell application \"Messages\" to send \"$msg\" to participant \"chchlin1018@icloud.com\" of (1st account whose service type = iMessage)" 2>/dev/null || \
    echo "[NOTIFY] $msg"
}
get_mem() {
    local ps=$(sysctl -n hw.pagesize 2>/dev/null||echo 4096)
    local tb=$(sysctl -n hw.memsize 2>/dev/null||echo 0)
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
    [ "$(echo "${f:-0}<2.0"|bc 2>/dev/null)" = "1" ] && notify "⚠️ 低記憶體 💾$m"
    return 0
}
task_start() {
    local num=$1; local desc="$2"; TASK_NUM=$num; TASK_DESC="$desc"
    PCT=$((TASK_DONE*100/TASK_TOTAL)); local m=$(get_mem)
    MSG="🏗️ P${SPRINT} ▶️ Task ${num}/${TASK_TOTAL}: ${desc}
📊 ${TASK_DONE}/${TASK_TOTAL}|Part ${PART_DONE}/${PART_TOTAL}|${PCT}%
💾${m}|$(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
task_done() {
    TASK_DONE=$((TASK_DONE+1)); PCT=$((TASK_DONE*100/TASK_TOTAL))
    MSG="🏗️ P${SPRINT} ✅ Task ${TASK_NUM}/${TASK_TOTAL}: ${TASK_DESC}
📊 ${TASK_DONE}/${TASK_TOTAL}|Part ${PART_DONE}/${PART_TOTAL}|${PCT}%
$(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
part_start() {
    local id="$1"; local desc="$2"; local cnt=$3
    PART_ID="$id"; PART_DESC="$desc"
    check_mem || { notify "⛔ OOM at Part $id"; exit 1; }
    local m=$(get_mem)
    MSG="🏗️ P${SPRINT} ▶️ Part ${id}: ${desc} (${cnt} tasks)
📊 ${TASK_DONE}/${TASK_TOTAL}|Part ${PART_DONE}/${PART_TOTAL}|${PCT}%
💾${m}|$(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
part_done() {
    PART_DONE=$((PART_DONE+1)); PCT=$((TASK_DONE*100/TASK_TOTAL))
    local next="$1"
    git add -A && git commit -m "[P${SPRINT}] Part ${PART_ID}: ${PART_DESC}" 2>/dev/null && git push origin main 2>/dev/null
    MSG="🏗️ P${SPRINT} Part ${PART_ID} ✅ ${PART_DESC}
📊 ${TASK_DONE}/${TASK_TOTAL}|Part ${PART_DONE}/${PART_TOTAL}|${PCT}%
⏭️ ${next}|$(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}

# 殭屍清理 + 環境
pkill -f "python.*pytest" 2>/dev/null; pkill -f "python.*promptbim" 2>/dev/null; sleep 1
export QT_QPA_PLATFORM=offscreen
echo "✅ 函數+環境就緒"
```

## 啟動

```bash
SPRINT=24; TASK_TOTAL=28; PART_TOTAL=5; TASK_DONE=0; PART_DONE=0; PCT=0
check_mem || exit 1
git pull origin main 2>/dev/null
MEM=$(get_mem)
notify "🏗️ P24 啟動 | 28 Tasks/5 Parts → v2.11.0 | 💾${MEM}"

# 文件檢查
CLAUDE_SIZE=$(wc -c < CLAUDE.md 2>/dev/null|tr -d ' ')
SKILL_SIZE=$(wc -c < SKILL.md 2>/dev/null|tr -d ' ')
[ "$CLAUDE_SIZE" -lt 5000 ] && { notify "⛔ CLAUDE.md 損壞"; exit 1; }
[ "$SKILL_SIZE" -lt 20000 ] && { notify "⛔ SKILL.md 損壞"; exit 1; }
[ -n "$ANTHROPIC_API_KEY" ] && { notify "⛔ ANTHROPIC_API_KEY 衝突"; exit 1; }
echo "✅ 檢查通過"
```

---

## Part A: Demo 3D 自動生成 (8 Tasks)

```bash
part_start "A" "Demo 3D 自動生成" 8
```

### Task 1-8（每個 Task 必須用 task_start/task_done 包夾）

```bash
task_start 1 "Generate Demo IFC from demo_data.py"
# 新增 generate_demo_ifc() → resources/demo/demo_building.ifc
task_done

task_start 2 "Generate Demo USDA from demo_data.py"
# 新增 generate_demo_usda() → resources/demo/demo_building.usda
task_done

task_start 3 "Generate Demo 2D SVG floorplans"
# demo_floorplan_1f/2f/3f.svg + demo_site_plan.svg
task_done

task_start 4 "Download free IFC sample model (fallback)"
# github.com/youshengCode/IfcSampleFiles → resources/demo/sample_house.ifc
task_done

task_start 5 "generate_all_demo_resources() 整合"
# 整合 Task 1-4 到統一入口
task_done

task_start 6 "GUI 啟動載入 Demo 3D"
# main_window.py 啟動時自動載入 IFC/USDA
task_done

task_start 7 "Swift SceneKit 載入 Demo USDA"
# ContentView.swift + BIMSceneBuilder.swift
task_done

task_start 8 "Demo 3D Tests (+5)"
# 生成有效性 + GUI 非空 + 清除重生成
task_done
```

```bash
part_done "Part B — Advanced BIM (6 tasks)"
```

---

## Part B: 進階 BIM (6 Tasks)

```bash
part_start "B" "進階 BIM 功能" 6

task_start 9 "Multi-story 停車場生成"
# 1F 自動停車場配置
task_done

task_start 10 "建築材質系統 PBR"
# 牆壁/地板/天花板材質
task_done

task_start 11 "結構系統自動生成"
# 柱/梁/基礎
task_done

task_start 12 "MEP 管線自動路由"
# 簡易水電管線
task_done

task_start 13 "樓梯/電梯自動生成"
# 根據樓層數自動配置
task_done

task_start 14 "進階 BIM Tests (+6)"
task_done

part_done "Part C — CI/CD + 啟動優化 (6 tasks)"
```

---

## Part C: CI/CD + 啟動優化 (6 Tasks)

```bash
part_start "C" "CI/CD + 啟動優化" 6

task_start 15 "GitHub Actions 修復"
# Linux-only pytest + lint
task_done

task_start 16 "App 啟動時間優化 (<3s)"
# lazy import + 延遲 3D
task_done

task_start 17 "版本同步腳本 sync_version.sh"
task_done

task_start 18 "開發者 setup 腳本 dev_setup.sh"
task_done

task_start 19 "Pre-commit hooks"
task_done

task_start 20 "CI/CD Tests (+4)"
task_done

part_done "Part D — 整合測試 (4 tasks)"
```

---

## Part D: 整合測試 (4 Tasks)

```bash
part_start "D" "整合測試" 4

task_start 21 "E2E Pipeline 整合測試 (+5)"
# prompt → IFC + USDA 完整 pipeline
task_done

task_start 22 "MCP Server 整合測試 (+3)"
task_done

task_start 23 "Swift ↔ Python 整合測試 (+4)"
task_done

task_start 24 "覆蓋率門檻 70→75%"
task_done

part_done "Part E — 驗收推送 (4 tasks)"
```

---

## Part E: 驗收推送 (4 Tasks)

```bash
part_start "E" "驗收 + 推送" 4

task_start 25 "xcodebuild + pytest 全通過"
# ★ pytest 必須用安全模式 ★
export QT_QPA_PLATFORM=offscreen
pkill -f "python.*pytest" 2>/dev/null; sleep 1
python -m pytest tests/ --timeout=10 --ignore=tests/test_gui --ignore=tests/test_mcp -x -m "not api and not slow" --tb=short -q
pkill -f "python.*pytest" 2>/dev/null
task_done

task_start 26 "全量文件同步 v2.11.0"
# TODO/CHANGELOG/README/pyproject/__init__/Info.plist
task_done

task_start 27 "審計報告 + git tag v2.11.0"
# docs/audit-reports/Sprint24_AuditReport.md
task_done

task_start 28 "產生 PROMPT_P25.md (合規 v1.21.0)"
# 必須包含 task_start/task_done 封裝函數
task_done

part_done "Sprint 完成"
```

## Sprint 完成

```bash
MEM=$(get_mem)
notify "🏗️ P24 完成 🎉 | v2.11.0 | 28/28 Tasks | 100% ✅ | 💾${MEM}"
pkill -f "python.*pytest" 2>/dev/null
```

---

## 驗收標準

```
☐ ★ 28 個 task_start + 28 個 task_done 通知已發送
☐ ★ 5 個 part_start + 5 個 part_done 通知已發送
☐ ★ 5 次 Part 結束 git commit+push
☐ App 啟動即顯示 3D 建築模型
☐ Demo IFC + USDA + SVG 自動生成
☐ xcodebuild BUILD SUCCEEDED
☐ pytest (QT_QPA_PLATFORM=offscreen --timeout=10 -x)
☐ git tag v2.11.0
☐ docs/audit-reports/Sprint24_AuditReport.md
☐ sprints/PROMPT_P25.md（合規 v1.21.0 含 task_start/task_done）
```

---

*PROMPT_P24.md v4.0 | CLAUDE.md v1.21.0 | SKILL.md v3.6*
*★ 每個 Task 必須用 task_start/task_done 包夾 — 28 個 Task 共 56 則 iMessage ★*
