# PROMPT_P25.md v2.1 — Performance + Windows + Documentation

> **Sprint:** P25 | **目標:** v2.12.0 | **基於:** P24 (v2.11.0)
> **CLAUDE.md:** v1.22.0 | **SKILL.md:** v3.7
> **範圍:** 3 Parts / 18 Tasks
> **v2.1 變更:** 加入 PROJECT_STATUS.md 讀取/更新 + 通知統一多行格式

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

# --- 3. Task/Part 封裝函數 (CLAUDE.md v1.21.0+ MANDATORY) ---
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

# --- 4. 殭屍清理 + 環境 ---
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
SPRINT=25; TASK_TOTAL=18; PART_TOTAL=3; TASK_DONE=0; PART_DONE=0; PCT=0
SPRINT_DESC="Performance + Windows + Documentation"
VERSION="2.12.0"

# ★ 讀取 PROJECT_STATUS.md (CLAUDE.md v1.22.0 MANDATORY) ★
echo "📋 讀取 PROJECT_STATUS.md..."
cat docs/PROJECT_STATUS.md
echo "✅ 專案狀態已讀取"

check_mem || exit 1
git pull origin main 2>/dev/null

# ★ 啟動通知（多行格式 — CLAUDE.md v1.22.0 MANDATORY）★
MEM=$(get_mem)
MSG="🏗️ PromptBIM Sprint P${SPRINT} 啟動
📋 ${SPRINT_DESC}
🎯 ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts → v${VERSION}
💾 ${MEM}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
notify "$MSG"

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

task_start 1 "Pipeline benchmark 自動化 CI"
# scripts/benchmark_pipeline.py → GitHub Actions integration
task_done

task_start 2 "IFC 生成優化 (<2s/3層建築)"
# Profile + optimize IFCGenerator.generate()
task_done

task_start 3 "USD 生成優化 (<1.5s/3層建築)"
# Profile + optimize USDGenerator.generate()
task_done

task_start 4 "記憶體分析 + 洩漏偵測"
# 加入記憶體 benchmark 到 CI
task_done

task_start 5 "啟動時間分析器"
# scripts/measure_startup.py
task_done

task_start 6 "Performance Tests (+5)"
task_done

part_done "Part B — Windows 平台支援 (6 tasks)"
```

---

## Part B: Windows 平台支援 (6 Tasks)

```bash
part_start "B" "Windows 平台支援" 6

task_start 7 "Windows CI runner in GitHub Actions"
# .github/workflows/ci.yml add windows-latest
task_done

task_start 8 "Windows 路徑相容性審查"
# Path() vs os.path across all modules
task_done

task_start 9 "Windows conda setup 腳本更新"
# scripts/setup_windows.ps1 update
task_done

task_start 10 "跨平台 test markers"
# @pytest.mark.skipif(sys.platform == 'win32')
task_done

task_start 11 "Windows 特定 bug 修復"
# Fix platform-specific issues found in CI
task_done

task_start 12 "Windows Tests (+4)"
task_done

part_done "Part C — Documentation + API (6 tasks)"
```

---

## Part C: Documentation + API (6 Tasks)

```bash
part_start "C" "Documentation + API" 6

task_start 13 "Auto-generate API docs (pdoc/sphinx)"
task_done

task_start 14 "架構圖更新 v3"
# docs/architecture/v3_architecture.svg
task_done

task_start 15 "Demo 腳本 + 影片指南更新"
# docs/DEMO_SCRIPT.md for v2.12.0
task_done

task_start 16 "Contributing 指南 (CONTRIBUTING.md)"
task_done

task_start 17 "Security 政策 (SECURITY.md)"
task_done

task_start 18 "文件測試 (+3)"
# 連結檢查、代碼範例驗證
task_done

part_done "Sprint 完成"
```

---

## Sprint 完成

```bash
# ★ 最終 pytest（安全模式 — CLAUDE.md MANDATORY）★
export QT_QPA_PLATFORM=offscreen
pkill -f "python.*pytest" 2>/dev/null; sleep 1
python -m pytest tests/ \
    --timeout=10 \
    --ignore=tests/test_gui \
    --ignore=tests/test_mcp \
    --ignore=tests/test_e2e_integration.py \
    -x --tb=short -q
pkill -f "python.*pytest" 2>/dev/null

# 文件同步 v2.12.0
# TODO/CHANGELOG/README/pyproject/__init__/Info.plist

# 審計報告
# docs/audit-reports/Sprint25_AuditReport.md

# Git push + tag
git add -A && git commit -m "[P25] Sprint complete — v2.12.0" && git push origin main
git tag v2.12.0 && git push origin v2.12.0

# 產生 PROMPT_P26.md（合規 v1.22.0）

# ★ 更新 PROJECT_STATUS.md (CLAUDE.md v1.22.0 MANDATORY) ★
cat >> docs/PROJECT_STATUS.md << EOF

### Sprint P${SPRINT} 執行結果 — $(date '+%Y-%m-%d %H:%M')
- **狀態:** ✅ 完成
- **版本:** v${VERSION}
- **Tasks:** ${TASK_DONE}/${TASK_TOTAL}
- **記憶體:** $(get_mem)
EOF
git add docs/PROJECT_STATUS.md && git commit -m "[status] P${SPRINT} complete" && git push origin main 2>/dev/null

# ★ 完成通知（多行格式 — CLAUDE.md v1.22.0 MANDATORY）★
MEM=$(get_mem)
MSG="🏗️ PromptBIM Sprint P${SPRINT} 完成 🎉
🏷️ v${VERSION} | ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts
📊 完成度: 100% ✅
💾 ${MEM}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
notify "$MSG"

pkill -f "python.*pytest" 2>/dev/null
```

---

## 驗收標準

```
☐ ★ 18 個 task_start + 18 個 task_done 通知已發送
☐ ★ 3 個 part_start + 3 個 part_done 通知已發送
☐ ★ 3 次 Part 結束 git commit+push
☐ ★ 啟動時讀取 PROJECT_STATUS.md
☐ ★ 完成時更新 PROJECT_STATUS.md
☐ ★ 所有通知為多行格式（不得單行）
☐ Pipeline benchmark < 5s (3層住宅)
☐ Windows CI green on GitHub Actions
☐ API documentation auto-generated
☐ xcodebuild BUILD SUCCEEDED
☐ pytest 安全模式通過
☐ git tag v2.12.0
☐ docs/audit-reports/Sprint25_AuditReport.md
☐ sprints/PROMPT_P26.md（合規 v1.22.0）
☐ 不得修改 CLAUDE.md / SKILL.md
```

---

## pytest 安全規則（MANDATORY）

> ⚠️ **禁止同時跑多個 pytest 進程（Mac Mini 16GB 會 OOM）**

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

*PROMPT_P25.md v2.1 | 2026-03-27*
*CLAUDE.md: v1.22.0 | SKILL.md: v3.7*
*★ 3 Parts / 18 Tasks | 預期 ~42 則 iMessage*
*★ v2.1: PROJECT_STATUS.md 讀取/更新 + 通知統一多行格式*
