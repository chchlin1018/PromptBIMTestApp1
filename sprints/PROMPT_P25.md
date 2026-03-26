# PROMPT_P25.md v1.0 — Performance + Windows + Documentation (CLAUDE.md v1.21.0 合規)

> **Sprint:** P25 | **目標:** v2.12.0 | **CLAUDE.md:** v1.21.0 | **SKILL.md:** v3.7
> **★ v1.0 核心: task_start/task_done 封裝函數 — 每個 Task 必須呼叫 ★**

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
SPRINT=25; TASK_TOTAL=24; PART_TOTAL=4; TASK_DONE=0; PART_DONE=0; PCT=0
check_mem || exit 1
git pull origin main 2>/dev/null
MEM=$(get_mem)
notify "🏗️ P25 啟動 | 24 Tasks/4 Parts → v2.12.0 | 💾${MEM}"

# 文件檢查
CLAUDE_SIZE=$(wc -c < CLAUDE.md 2>/dev/null|tr -d ' ')
SKILL_SIZE=$(wc -c < SKILL.md 2>/dev/null|tr -d ' ')
[ "$CLAUDE_SIZE" -lt 5000 ] && { notify "⛔ CLAUDE.md 損壞"; exit 1; }
[ "$SKILL_SIZE" -lt 20000 ] && { notify "⛔ SKILL.md 損壞"; exit 1; }
[ -n "$ANTHROPIC_API_KEY" ] && { notify "⛔ ANTHROPIC_API_KEY 衝突"; exit 1; }
echo "✅ 檢查通過"
```

---

## Part A: Performance + Benchmarks (6 Tasks)

```bash
part_start "A" "Performance + Benchmarks" 6

task_start 1 "Pipeline benchmark automation in CI"
# scripts/benchmark_pipeline.py → GitHub Actions integration
task_done

task_start 2 "IFC generation optimization (<2s for 3-story)"
# Profile and optimize IFCGenerator.generate()
task_done

task_start 3 "USD generation optimization (<1.5s for 3-story)"
# Profile and optimize USDGenerator.generate()
task_done

task_start 4 "Memory profiling + leak detection"
# Add memory benchmarks to CI
task_done

task_start 5 "Startup profiler (measure actual startup time)"
# scripts/measure_startup.py
task_done

task_start 6 "Performance Tests (+5)"
task_done

part_done "Part B — Windows Support (6 tasks)"
```

---

## Part B: Windows Support (6 Tasks)

```bash
part_start "B" "Windows 平台支援" 6

task_start 7 "Windows CI runner in GitHub Actions"
# .github/workflows/ci.yml add windows-latest
task_done

task_start 8 "Windows path compatibility audit"
# Path() vs os.path across all modules
task_done

task_start 9 "Windows conda setup script"
# scripts/setup_windows.ps1 update
task_done

task_start 10 "Cross-platform test markers"
# @pytest.mark.skipif(sys.platform == 'win32')
task_done

task_start 11 "Windows-specific bug fixes"
# Fix any platform-specific issues found in CI
task_done

task_start 12 "Windows Tests (+4)"
task_done

part_done "Part C — Documentation (6 tasks)"
```

---

## Part C: Documentation + API (6 Tasks)

```bash
part_start "C" "Documentation + API" 6

task_start 13 "Auto-generate API docs from docstrings"
# pdoc or sphinx integration
task_done

task_start 14 "Architecture diagram update (v3)"
# docs/v3_architecture.svg update
task_done

task_start 15 "Demo script + video guide update"
# docs/DEMO_SCRIPT.md for v2.11.0
task_done

task_start 16 "Contributing guide (CONTRIBUTING.md)"
task_done

task_start 17 "Security policy (SECURITY.md)"
task_done

task_start 18 "Documentation Tests (+3)"
# Check links, verify code samples compile
task_done

part_done "Part D — 驗收推送 (6 tasks)"
```

---

## Part D: 驗收推送 (6 Tasks)

```bash
part_start "D" "驗收 + 推送" 6

task_start 19 "xcodebuild + pytest 全通過"
# ★ pytest 必須用安全模式 ★
export QT_QPA_PLATFORM=offscreen
pkill -f "python.*pytest" 2>/dev/null; sleep 1
python -m pytest tests/ --timeout=10 --ignore=tests/test_gui --ignore=tests/test_mcp -x -m "not api and not slow" --tb=short -q
pkill -f "python.*pytest" 2>/dev/null
task_done

task_start 20 "Coverage 75→80%"
task_done

task_start 21 "全量文件同步 v2.12.0"
# TODO/CHANGELOG/README/pyproject/__init__/Info.plist
task_done

task_start 22 "審計報告 + git tag v2.12.0"
# docs/audit-reports/Sprint25_AuditReport.md
task_done

task_start 23 "產生 PROMPT_P26.md (合規 v1.21.0)"
# 必須包含 task_start/task_done 封裝函數
task_done

task_start 24 "pip-audit 安全掃描"
task_done

part_done "Sprint 完成"
```

## Sprint 完成

```bash
MEM=$(get_mem)
notify "🏗️ P25 完成 🎉 | v2.12.0 | 24/24 Tasks | 100% ✅ | 💾${MEM}"
pkill -f "python.*pytest" 2>/dev/null
```

---

## 驗收標準

```
☐ ★ 24 個 task_start + 24 個 task_done 通知已發送
☐ ★ 4 個 part_start + 4 個 part_done 通知已發送
☐ ★ 4 次 Part 結束 git commit+push
☐ Pipeline benchmark < 5s for 3-story residential
☐ Windows CI green on GitHub Actions
☐ API documentation auto-generated
☐ xcodebuild BUILD SUCCEEDED
☐ pytest (QT_QPA_PLATFORM=offscreen --timeout=10 -x)
☐ Coverage >= 80%
☐ git tag v2.12.0
☐ docs/audit-reports/Sprint25_AuditReport.md
☐ sprints/PROMPT_P26.md（合規 v1.21.0 含 task_start/task_done）
```

---

*PROMPT_P25.md v1.0 | CLAUDE.md v1.21.0 | SKILL.md v3.7*
*★ 每個 Task 必須用 task_start/task_done 包夾 — 24 個 Task 共 48 則 iMessage ★*
