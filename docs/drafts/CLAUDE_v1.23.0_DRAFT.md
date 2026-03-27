# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.23.0 | **更新:** 2026-03-27
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
| 🔴 P24e | pytest 反覆 OOM (4次) | conftest import PySide6 + 多 pytest | **conftest.py 頂部 + 禁止多 pytest + ignore e2e** |
| 🟧 P24c | Git 遠端分歧 | Claude.ai 同時推 commit | **Sprint 前 git pull** |

---

## [MANDATORY] Zigma 品牌識別 (v1.23.0 新增)

> ⚠️ **所有文件、commit message、通知中使用 Zigma 品牌名稱**

```
Zigma（整體解決方案品牌）
├── Zigma Core          — 共用底層框架
├── Zigma PromptToBuild — 設計→建造→交付
├── Zigma PromptToOperate — 交付→營運→退役
├── Zigma Cloud         — 雲端基礎設施
└── Zigma NDH           — IDTF Neutral Data Hub
```

- **倉庫:** PromptBIMTestApp1（待重命名 → zigma）
- **Python package:** promptbim（待重命名 → zigma_build）
- **重命名在 RS-S1 Sprint 統一執行，此前維持現狀**

---

## [MANDATORY] PROJECT.md 同步規則 (v1.23.0 新增)

> ⚠️ **PROJECT.md 是專案狀態的唯一真相來源（Single Source of Truth）**
> ⚠️ **Claude Code 可以且應該更新 PROJECT.md**
> ⚠️ **Claude Code 禁止修改 CLAUDE.md / SKILL.md**

### 8 條同步規則

| # | 規則 | 觸發時機 |
|---|------|--------|
| 1 | PROJECT.md 是專案狀態的唯一真相來源 | 永遠 |
| 2 | 每 Task 開始前：PROJECT.md 對應狀態 → 🔵 | task_start() |
| 3 | 每 Task 完成後：PROJECT.md 對應狀態 → ✅ | task_done() |
| 4 | Sprint 完成：更新 PROJECT.md + SKILL.md + AuditReport | part_done(last) |
| 5 | Demo 完成：更新 PROJECT.md + Demo_AuditReport + git tag | Demo 結束 |
| 6 | 命名規則：全部遵循 PROJECT.md §7 | 永遠 |
| 7 | Claude Code 禁止修改 CLAUDE.md / SKILL.md | 永遠 |
| 8 | Claude Code 可以且應該更新 PROJECT.md | 每個 Task |

### PROJECT_STATUS.md 遷移

> ⚠️ **docs/PROJECT_STATUS.md 已 deprecated，功能合併到根目錄 PROJECT.md**
> ⚠️ **Sprint 啟動/結束讀寫目標：PROJECT.md（不再是 docs/PROJECT_STATUS.md）**

---

## [MANDATORY] 通知格式規範

> ⚠️ **所有 notify 必須使用多行格式，不得簡化為單行**
> ⚠️ **包括 Sprint 啟動通知、完成通知、錯誤通知都必須多行**

### Sprint 啟動通知範本（MANDATORY）

```bash
MEM=$(get_mem)
MSG="🏗️ Zigma Sprint P${SPRINT} 啟動
📋 ${SPRINT_DESC}
🎯 ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts → v${VERSION}
💾 ${MEM}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
notify "$MSG"
```

### Sprint 完成通知範本（MANDATORY）

```bash
MEM=$(get_mem)
MSG="🏗️ Zigma Sprint P${SPRINT} 完成 🎉
🏷️ v${VERSION} | ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts
📊 完成度: 100% ✅
💾 ${MEM}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
notify "$MSG"
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
    osascript -e "display notification \"$msg\" with title \"Zigma\"" 2>/dev/null || \
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
    # === v1.23.0: 更新 PROJECT.md 狀態 ===
    # sed -i '' "s/| P${SPRINT}.*T${TASK_NUM} .*/& ✅/" PROJECT.md 2>/dev/null
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
 4. ★ 讀取 PROJECT.md 確認當前 Sprint 狀態
 5. ★ check_mem（<1GB 中止）
 6. ★ git pull origin main
 7. 啟動 notify（含 💾，多行格式）
 8. 文件檢查（CLAUDE ≥5000B, SKILL ≥20000B）
 9. 環境檢查（ANTHROPIC_API_KEY）
10. 開始 Part A → Task 1
```

---

## [MANDATORY] pytest 安全規則

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

## [MANDATORY] 命名規則速查 (v1.23.0 新增)

> ⚠️ **所有 Task ID、commit message、branch、tag 必須遵循此規則**
> 詳細定義見: docs/architecture/PromptToBuild_Governance_Framework_v1.0.md

| 類型 | 格式 | 範例 |
|------|------|------|
| Demo Task | `D{N}-S{X}-P{Y}-T{Z}` | D1-S1-PA-T4 |
| Sprint Task | `P{XX}-P{Y}-T{Z}` | P26-PA-T1 |
| Git Tag | `v{M}.{m}.{p}` / `demo{N}-v{M}.{m}.{p}` | v3.0.0 / demo1-v0.1.0 |
| Git Branch | `sprint/{XX}` / `demo/{N}` | sprint/26 / demo/1 |
| Commit | `[{scope}] {type}: {desc}` | [P26] feat: IPlugin base |

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
| PROJECT.md | Claude Code 應主動更新 |

---

## [MANDATORY] PROMPT 合規性檢查

```
☐ 函數定義: notify + get_mem + check_mem + task_start + task_done + part_start + part_done
☐ 殭屍清理 (pkill) + export QT_QPA_PLATFORM=offscreen
☐ ★ 啟動時讀取 PROJECT.md ★
☐ 啟動順序: 函數→清理→讀PROJECT.md→check_mem→git pull→notify→文件檢查→環境檢查
☐ ★ 啟動/完成/錯誤通知必須多行格式（不得單行簡化）★
☐ ★ 每個 Task 用 task_start/task_done 包夾 ★
☐ ★ 每個 Part 用 part_start/part_done 包夾 ★
☐ pytest: offscreen + --timeout=10 + --ignore gui/mcp/e2e + -x + pkill 前後
☐ ★ Sprint 結束時更新 PROJECT.md（成功/失敗/錯誤）★
☐ ★ 錯誤/中斷時也必須更新 PROJECT.md ★
☐ ★ 命名規則遵循 PROJECT.md §7（v1.23.0 新增）★
☐ Sprint 結束產生下一個 PROMPT
☐ 不修改 CLAUDE.md / SKILL.md
```

---

## [MANDATORY] 執行流程（30 步, v1.23.0 更新）

```
 1. 讀 PROMPT → 2. 定義函數 → 3. pkill + offscreen
 4. ★ 讀取 PROJECT.md（取代舊 PROJECT_STATUS.md）★
 5. check_mem → 6. git pull → 7. 啟動 notify(💾，多行)
 8. 文件檢查 → 9. 環境檢查
10. part_start → 11. task_start → 12. 執行 → 13. task_done
14. ★ 更新 PROJECT.md Task 狀態 → ✅ ★
15. 重複 11-14 → 16. Part git commit+push → 17. part_done
18. 重複 10-17 → 19. 錯誤 notify(💾)
20. xcodebuild → 21. pytest(安全模式，單進程) → 22. pbxproj
23. 文件同步 → 24. 審計報告
25. ★ 最終更新 PROJECT.md（Sprint 結果 + 版本 + 日期）★
26. git push+tag
27. 產生下一個 PROMPT
28. Sprint ✅ notify(多行) → 29. pkill 清理
30. ★ 確認 PROJECT.md 已 push ★
```

---

## 版本歷史

| 版本 | 變更 |
|------|------|
| v1.17.0 | 雙向通知 + +886972535899 |
| v1.18.0 | P24a OOM → get_mem + check_mem |
| v1.19.0 | 歷史教訓 + Git 安全 + 26 步 |
| v1.20.0 | P24b 殭屍 → pkill + offscreen + pytest 安全 |
| v1.21.0 | P24d Task 通知跳過 → task_start/task_done |
| v1.22.0 | PROJECT_STATUS.md 追蹤 + 通知格式規範(多行) + 28 步 |
| **v1.23.0** | **Zigma 品牌 + PROJECT.md 同步 8 規則 + 命名規則 + 30 步** |

---

*CLAUDE.md v1.23.0 DRAFT | 2026-03-27*
*★ 主要收件人: +886972535899 | 備用: chchlin1018@icloud.com*
*⚠️ 本文件為草稿，待 Michael 審閱後替換根目錄 CLAUDE.md*
