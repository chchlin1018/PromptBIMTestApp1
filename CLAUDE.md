# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.22.0 | **更新:** 2026-03-27
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
| 🔴 P24d | Task 通知全被跳過 | Claude Code 只發 Part 通知 | **task_start()/task_done() 封裝函數** |
| 🔴 P24e | pytest 反覆 OOM (4次) | conftest import PySide6 + 多 pytest 同時跑 | **conftest.py 頂部 + 禁止多 pytest + ignore e2e** |
| 🟧 P24c | Git 遠端分歧 | Claude.ai 同時推 commit | **Sprint 前 git pull** |

---

## [MANDATORY] PROJECT_STATUS.md — 專案狀態追蹤 (v1.22.0 新增)

> ⚠️ **Sprint 啟動時必須先讀取 `docs/PROJECT_STATUS.md`，了解專案最新狀態**
> ⚠️ **Sprint 結束時（無論成功或失敗）必須更新 `docs/PROJECT_STATUS.md`**
> ⚠️ **錯誤、中斷、OOM 等異常也必須記錄到 PROJECT_STATUS.md**

### 啟動時讀取（MANDATORY — 在定義函數之後、check_mem 之前）

```bash
# ★★★ 讀取專案狀態 ★★★
echo "📋 讀取 PROJECT_STATUS.md..."
cat docs/PROJECT_STATUS.md
echo "✅ 專案狀態已讀取"
```

### 結束時更新（MANDATORY — 無論成功或失敗都要執行）

Sprint 結束時（步驟 23 之後），必須更新 `docs/PROJECT_STATUS.md` 的以下內容：

```markdown
## 2. Sprint 進度
| P{X} | v{X} | ✅ 完成 / ❌ 失敗 / ⚠️ 部分完成 | 說明 |

## 最後更新
- 更新時間: $(date)
- Sprint: P{X}
- 結果: 成功/失敗/中斷
- 錯誤: （如有）
- 完成 Tasks: N/Total
- 記憶體: $(get_mem)
```

### 錯誤/中斷時也必須更新

```bash
# 在錯誤處理或中斷時，除了發送 notify，還必須更新 PROJECT_STATUS.md
# 範例：
cat >> docs/PROJECT_STATUS.md << EOF

### ⚠️ Sprint P${SPRINT} 異常記錄 — $(date '+%Y-%m-%d %H:%M')
- **狀態:** 中斷/失敗
- **停在:** Task ${TASK_NUM}/${TASK_TOTAL} (${TASK_DESC})
- **原因:** ${ERROR_DESCRIPTION}
- **記憶體:** $(get_mem)
- **需要:** 人工介入處理
EOF
git add docs/PROJECT_STATUS.md && git commit -m "[status] P${SPRINT} error log" && git push origin main 2>/dev/null
```

---

## [MANDATORY] Sprint 啟動函數 — 絕對第一步

> ⚠️ 每個 PROMPT 最前面必須包含以下完整定義
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

# --- Task/Part 封裝函數 (v1.21.0) ---
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

# --- 殭屍清理 + 環境 ---
echo "🧹 清理殭屍 Python..."
pkill -f "python.*pytest" 2>/dev/null
pkill -f "python.*promptbim" 2>/dev/null
pkill -f "python.*PySide6" 2>/dev/null
sleep 1
export QT_QPA_PLATFORM=offscreen
echo "✅ 全部函數+環境已就緒"
```

### iMessage 收件人
```
★ 主要: +886972535899 | 備用: chchlin1018@icloud.com
```

---

## [MANDATORY] Sprint 啟動順序（不可調換）

```
 1. 讀 PROMPT
 2. ★ 定義函數(notify+get_mem+check_mem+task_start+task_done+part_start+part_done)
 3. ★ 殭屍清理 + QT_QPA_PLATFORM=offscreen
 4. ★ 讀取 docs/PROJECT_STATUS.md（了解專案最新狀態）     ← v1.22.0 新增
 5. ★ check_mem（<1GB 中止）
 6. ★ git pull origin main
 7. 啟動 notify（含 💾）
 8. 文件檢查（CLAUDE ≥5000B, SKILL ≥20000B）
 9. 環境檢查（ANTHROPIC_API_KEY）
10. 開始 Part A → Task 1
```

---

## [MANDATORY] pytest 安全規則

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
☐ ★ 啟動時讀取 docs/PROJECT_STATUS.md ★                          ← v1.22.0 新增
☐ 啟動順序: 函數→清理→讀PROJECT_STATUS→check_mem→git pull→notify→文件檢查→環境檢查
☐ ★ 每個 Task 用 task_start/task_done 包夾 ★
☐ ★ 每個 Part 用 part_start/part_done 包夾 ★
☐ pytest: offscreen + --timeout=10 + --ignore=test_gui + --ignore=test_e2e + -x + pkill 前後
☐ ★ Sprint 結束時更新 docs/PROJECT_STATUS.md（成功/失敗/錯誤）★  ← v1.22.0 新增
☐ ★ 錯誤/中斷時也必須更新 docs/PROJECT_STATUS.md ★               ← v1.22.0 新增
☐ Sprint 結束產生下一個 PROMPT（合規本版本）
☐ 不修改 CLAUDE.md / SKILL.md
```

---

## [MANDATORY] 執行流程（28 步）

```
 1. 讀 PROMPT → 2. 定義函數 → 3. pkill + offscreen
 4. ★ 讀取 docs/PROJECT_STATUS.md ★                    ← v1.22.0 新增
 5. check_mem → 6. git pull → 7. 啟動 notify(💾)
 8. 文件檢查 → 9. 環境檢查
10. part_start → 11. task_start → 12. 執行 → 13. task_done
14. 重複 11-13 → 15. Part git commit+push → 16. part_done
17. 重複 10-16 → 18. 錯誤 notify(💾)
19. xcodebuild → 20. pytest(安全模式，單進程) → 21. pbxproj
22. 文件同步 → 23. 審計報告 → 24. git push+tag
25. 產生下一個 PROMPT
26. ★ 更新 docs/PROJECT_STATUS.md（結果+錯誤）★        ← v1.22.0 新增
27. Sprint ✅ notify → 28. pkill 清理
```

---

## 版本歷史

| 版本 | 變更 |
|------|------|
| v1.17.0 | 雙向通知 + +886972535899 |
| v1.18.0 | P24a OOM → get_mem + check_mem |
| v1.19.0 | 歷史教訓 + Git 安全 + 26 步 |
| v1.20.0 | P24b 殭屍 → pkill + offscreen + pytest 安全 |
| v1.21.0 | P24d Task 通知跳過 → task_start/task_done 封裝 |
| v1.21.0+ | P24e pytest 反覆 OOM → conftest.py + 禁止多 pytest + ignore e2e |
| **v1.22.0** | **★ PROJECT_STATUS.md: 啟動時讀取 + 結束時更新（含錯誤記錄）+ 28 步流程** |

---

*CLAUDE.md v1.22.0 | 2026-03-27*
*★ v1.22.0: Sprint 啟動讀 PROJECT_STATUS.md + 結束更新（含錯誤）+ 28 步流程*
*★ 主要收件人: +886972535899 | 備用: chchlin1018@icloud.com*
