# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.19.0 | **更新:** 2026-03-26
> **版本控制:** 本文件由人工維護，Claude Code 不得直接修改
> ⚠️ 本文件中標記為 **[MANDATORY]** 的規則必須嚴格執行，不得跳過

---

## 開發前必讀順序

```
1. sprints/PROMPT_P{X}.md ← 當前 Sprint 的執行指令（最重要！）
2. SKILL.md                ← 專案 SSOT（架構、Schema、Agent Prompt、開發規範）
3. TODO.md                 ← 確認當前 Sprint 狀態
4. 對應 Addendum            ← 依當前 Sprint 讀取技術規格
5. CLAUDE.md               ← 本文件（行為規範）
```

---

## [MANDATORY] 歷史教訓（所有 Sprint 必讀）

> ⚠️ **以下每一條都是真實事故。違反這些規則會導致 Sprint 失敗、資料遺失、或靜默中斷。**

### 🔴 P18 事故 — 治理文件被截斷
- **事件:** Claude Code 擅自修改 CLAUDE.md，導致 v1.13.0 完整內容被截斷
- **影響:** 治理規則遺失，需要人工從 git 歷史恢復
- **規則:** ❌ **絕對禁止修改 CLAUDE.md / SKILL.md / addendum / backups**

### 🔴 P22 事故 — notify 函數不存在
- **事件:** Claude Code `-p` 模式不載入 `.zshrc`，shell 中 `notify` 函數不存在
- **影響:** 整個 Sprint 沒有任何通知，用戶完全不知道執行狀態
- **規則:** ★ 每個 PROMPT 最前面必須顯式定義 notify 函數

### 🔴 P22.1 事故 — Sprint 結束但沒有 commit
- **事件:** Claude Code 執行完 Part C 後停止，但沒有 git commit + push
- **影響:** 所有工作只在本地，需要手動 commit
- **規則:** ★ **每個 Part 完成後必須 git commit**（不只是 Sprint 結束）

### 🔴 P24 事故 — 記憶體耗盡 (OOM)
- **事件:** Mac Mini 16GB RAM 全部耗盡，Claude Code (2.19GB) + Chrome (454MB) + Notion (412MB)
- **影響:** macOS 將 Claude Code「暫停」，Sprint 靜默中斷，零通知、零 commit
- **規則:** ★ 每個 Task 啟動前 get_mem + 每個 Part 啟動前 check_mem (<1GB 暫停)
- **預防:** Sprint 期間關閉 Chrome/Notion/AnyDesk

### 🟧 P24 事故 — Git 遠端分歧
- **事件:** Claude.ai 透過 GitHub API 推送文件（architecture docs），同時 Claude Code 在本地執行
- **影響:** 本地 HEAD 與 remote HEAD 分歧，git push 失敗
- **規則:** ★ **Sprint 啟動前必須 `git pull origin main`**
- **規則:** ★ **每個 Part 結束 commit 後立即 push**（減少分歧窗口）

### 🟧 P23 經驗 — 第一次 iMessage 需要授權
- **事件:** 第一次用 `+886972535899` 發送 iMessage 時，Mac Mini 彈出授權視窗
- **影響:** 必須在 Mac 前按「允許」，否則 notify 靜默失敗
- **預防:** Sprint 前手動發一次測試 iMessage

### 🟧 GitHub Actions 額度
- **事件:** 2,000 分鐘/月免費額度用完 (100%)，4/1 重置
- **影響:** CI 紅燈但不是代碼問題
- **預防:** CI 只跑 Linux pytest + lint，不跑 macOS xcodebuild runner

---

## [MANDATORY] notify + get_mem 函數定義 — Sprint 的絕對第一步

> ⚠️ **這是每個 Sprint 的第一個動作。在讀取任何其他文件之前，必須先定義函數。**

### notify + get_mem + check_mem 函數實作（複製到每個 PROMPT 最前面）

> ⚠️ **主要收件人: `+886972535899`（手機號碼，最優先）**
> ⚠️ **備用收件人: `chchlin1018@icloud.com`**

```bash
# ===== ★★★ Sprint 絕對第一步：定義 notify + get_mem + check_mem ★★★ =====
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

get_mem() {
    local page_size=$(sysctl -n hw.pagesize 2>/dev/null || echo 4096)
    local total_bytes=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
    local total_gb=$(echo "scale=1; $total_bytes / 1073741824" | bc 2>/dev/null || echo "?")
    local free_pages=$(vm_stat 2>/dev/null | awk '/Pages free/ {gsub(/\./,"",$3); print $3}')
    local inactive_pages=$(vm_stat 2>/dev/null | awk '/Pages inactive/ {gsub(/\./,"",$3); print $3}')
    local free_bytes=$(( (${free_pages:-0} + ${inactive_pages:-0}) * page_size ))
    local free_gb=$(echo "scale=1; $free_bytes / 1073741824" | bc 2>/dev/null || echo "?")
    local used_gb=$(echo "scale=1; ($total_bytes - $free_bytes) / 1073741824" | bc 2>/dev/null || echo "?")
    local pressure=$(memory_pressure 2>/dev/null | grep "System-wide" | awk '{print $NF}' || echo "unknown")
    echo "${used_gb}/${total_gb}GB (free:${free_gb}GB) pressure:${pressure}"
}

check_mem() {
    local MEM_INFO=$(get_mem)
    local free_gb=$(echo "$MEM_INFO" | grep -oE 'free:[0-9.]+' | grep -oE '[0-9.]+')
    if [ "$(echo "${free_gb:-0} < 1.0" | bc 2>/dev/null)" = "1" ]; then
        MSG="⛔ PromptBIM 記憶體嚴重不足！
💾 ${MEM_INFO}
❗ Free < 1GB — Sprint 可能被系統終止
🔧 請關閉 Chrome/Notion/AnyDesk 後重試
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
        echo "$MSG" && notify "$MSG"
        return 1
    elif [ "$(echo "${free_gb:-0} < 2.0" | bc 2>/dev/null)" = "1" ]; then
        MSG="⚠️ PromptBIM 記憶體偏低
💾 ${MEM_INFO}
⚠️ Free < 2GB — 建議關閉非必要 App
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
        echo "$MSG" && notify "$MSG"
    fi
    return 0
}

echo "✅ notify + get_mem + check_mem 函數已定義"
```

### Sprint 啟動順序（不可調換）

```
1. 讀取 sprints/PROMPT_P{X}.md
2. ★ 定義 notify + get_mem + check_mem ★     ← 絕對第一步
3. ★ check_mem（<1GB 中止）★                 ← 第二步
4. ★ git pull origin main ★                  ← 第三步（防止遠端分歧）
5. ★ 啟動 notify（含 💾 記憶體）★             ← 第四步
6. 關鍵文件完整性檢查
7. 環境檢查（ANTHROPIC_API_KEY 衝突）
8. 讀取 SKILL.md, TODO.md 等
9. 開始執行 Task 1
```

---

## [MANDATORY] 記憶體監控規則

### 記憶體門檻

| Free RAM | 狀態 | 動作 |
|----------|------|------|
| ≥ 2 GB | 🟢 正常 | 繼續 |
| 1~2 GB | 🟡 偏低 | 警告，繼續 |
| < 1 GB | 🔴 危險 | **暫停 Sprint + 通知用戶** |

### Sprint 期間只保留

```
✅ Claude Code (~2.2 GB)
✅ Terminal / tmux (~50 MB)
✅ Messages (~100 MB)
✅ Tailscale (~43 MB)
✅ Finder (~80 MB)
──────────────────
❌ Chrome / Notion / AnyDesk / 系統設定 / 活動監視器 → 全部關閉
```

---

## [MANDATORY] Git 安全規則

> ⚠️ **P22.1 + P24 教訓: 不 commit 就遺失、遠端分歧就推不上去**

### Git 檢查時機

| # | 時機 | 動作 |
|---|------|------|
| 1 | **Sprint 啟動** | `git pull origin main`（防分歧） |
| 2 | **★ 每個 Part 結束** | `git add -A && git commit && git push`（增量保存） |
| 3 | **Sprint 結束** | `git tag v{X} && git push --tags` |
| 4 | **Task 失敗 3 次** | `git stash` 或 `git commit -m "wip: partial"` |

### Part 結束 Git Commit 模板

```bash
git add -A
git commit -m "[P${SPRINT}] Part ${PART}: ${PART_DESCRIPTION}

Tasks ${FIRST_TASK}-${LAST_TASK} completed.
Tests: pytest ${PYTEST_COUNT} | Build: ${BUILD_STATUS}
💾 $(get_mem)"
git push origin main || { notify "⚠️ git push 失敗，可能有遠端衝突"; git pull --rebase origin main && git push origin main; }
```

---

## [MANDATORY] 通知規則

> ⚠️ **每個 Task/Part 啟動 ▶️ 和結束 ✅ 都必須 notify**
> ⚠️ **Task 啟動 ▶️ 必須含 💾 get_mem**
> ⚠️ **Part 啟動前必須 check_mem**

### 通知時機表

| # | 時機 | 內容 |
|---|------|------|
| 1 | Sprint 啟動 | 總覽 + 💾 記憶體 |
| 2 | **Task ▶️ 啟動** | 描述 + 進度% + 💾 記憶體 |
| 3 | **Task ✅ 結束** | 描述 + 進度% |
| 4 | **Part ▶️ 啟動** | check_mem + 描述 + 💾 記憶體 |
| 5 | **Part ✅ 結束** | 進度 + ⏭️ 下一步 |
| 6 | Task 失敗 | 錯誤 + 💾 記憶體 |
| 7 | 中斷 | 位置 + 原因 + 💾 記憶體 |
| 8 | 記憶體不足 | 💾 狀態 + 建議 |
| 9 | Git push 完成 | commit hash + tag |
| 10 | Sprint 完成 | 100% + 測試數 + 💾 記憶體 |

### 通知模板

#### Task 啟動 ▶️（含 💾）
```bash
PCT=$((TASK_DONE * 100 / TASK_TOTAL))
MEM_INFO=$(get_mem)
MSG="🏗️ PromptBIM P${SPRINT}
▶️ Task ${TASK_NUM}/${TASK_TOTAL} 開始: ${TASK_DESCRIPTION}
📊 Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Task 結束 ✅
```bash
TASK_DONE=$((TASK_DONE + 1))
PCT=$((TASK_DONE * 100 / TASK_TOTAL))
MSG="🏗️ PromptBIM P${SPRINT}
✅ Task ${TASK_NUM}/${TASK_TOTAL} 完成: ${TASK_DESCRIPTION}
📊 Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Part 啟動 ▶️（check_mem + 💾）
```bash
check_mem || { MSG="⛔ P${SPRINT} 記憶體不足暫停 at Part ${PART} 💾 $(get_mem)"; notify "$MSG"; exit 1; }
MEM_INFO=$(get_mem)
MSG="🏗️ PromptBIM P${SPRINT}
▶️ Part ${PART} 開始: ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Part 結束 ✅（含 git commit + push）
```bash
PART_DONE=$((PART_DONE + 1))
PCT=$((TASK_DONE * 100 / TASK_TOTAL))
# ★ Part 結束必須 commit + push ★
git add -A && git commit -m "[P${SPRINT}] Part ${PART}: ${PART_DESCRIPTION}" && git push origin main 2>/dev/null
MSG="🏗️ PromptBIM P${SPRINT} Part ${PART} ✅
📋 ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
⏭️ 下一步: Part ${NEXT_PART} (${NEXT_PART_TASKS} tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### 失敗 ⚠️ / 中斷 ❌ / 完成 🎉
```bash
# 失敗
MEM_INFO=$(get_mem)
MSG="🏗️ PromptBIM P${SPRINT}
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)... 💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"

# 中斷
MEM_INFO=$(get_mem)
MSG="❌ Sprint P${SPRINT} 中斷 at Task ${TASK_NUM}/${TASK_TOTAL}
❗ ${ERROR_DESCRIPTION} | ${PCT}% 💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"

# 完成
MEM_INFO=$(get_mem)
MSG="🏗️ Sprint P${SPRINT} 完成 🎉
🏷️ v${VERSION} | ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts | 100% ✅
🧪 ${TEST_SUMMARY} 💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## [MANDATORY] 關鍵文件保護

| 文件 | 最低大小 | 恢復命令 |
|------|---------|---------|
| `CLAUDE.md` | 5,000 B | `git checkout 9599bc08 -- CLAUDE.md` |
| `SKILL.md` | 20,000 B | `git checkout 15fc0efe -- SKILL.md` |

```bash
CLAUDE_SIZE=$(wc -c < CLAUDE.md 2>/dev/null | tr -d ' ')
SKILL_SIZE=$(wc -c < SKILL.md 2>/dev/null | tr -d ' ')
if [ "$CLAUDE_SIZE" -lt 5000 ] 2>/dev/null || [ "$SKILL_SIZE" -lt 20000 ] 2>/dev/null; then
    MSG="⛔ 關鍵文件損壞！CLAUDE=${CLAUDE_SIZE}B SKILL=${SKILL_SIZE}B"
    echo "$MSG" && notify "$MSG" && exit 1
fi
echo "✅ 關鍵文件完整"
```

---

## [MANDATORY] 自動執行模式 — 不得詢問用戶

唯一例外: API Key 未設定 / Git push 衝突 / Xcode 簽名 / ANTHROPIC_API_KEY / 關鍵文件損壞 / 記憶體不足 (<1GB)

---

## [MANDATORY] 新建 PROMPT 合規性檢查

> ⚠️ **每一條都必須滿足，否則 PROMPT 不合規，不得推送。**

```
☐ 最前面有 notify + get_mem + check_mem 函數定義
☐ 主要收件人: +886972535899 / 備用: chchlin1018@icloud.com
☐ 啟動順序: 函數定義 → check_mem → git pull → 啟動通知 → 文件檢查 → 環境檢查
☐ 啟動通知含 💾 記憶體
☐ ★ 每個 Task 有 ▶️ 啟動（含💾） + ✅ 結束 notify
☐ ★ 每個 Part 有 ▶️ 啟動（check_mem + 💾） + ✅ 結束 notify
☐ ★ 每個 Part 結束有 git commit + push
☐ Part 結束含 ⏭️ 下一步
☐ 失敗/中斷 notify 含 💾 記憶體
☐ 路徑: sprints/PROMPT_P{X}.md
☐ Audit Report: docs/audit-reports/Sprint{X}_AuditReport.md
☐ Sprint 結束產生下一個 PROMPT（合規 v1.19.0）
☐ 不得修改 CLAUDE.md / SKILL.md / docs/backups/
☐ 不得中途詢問用戶
```

---

## [MANDATORY] Xcode pbxproj 完整性

```
☐ xcodebuild BUILD SUCCEEDED
☐ 所有 .swift 在 pbxproj Compile Sources 中
☐ Info.plist 版本正確
☐ NSSupportsAutomaticTermination = false
☐ NSSupportsSuddenTermination = false
☐ Signing: ad-hoc
☐ Bundle ID = com.realitymatrix.PromptBIMTestApp1
```

---

## [MANDATORY] Sprint 執行流程（26 步）

```
 1. 讀 PROMPT
 2. 定義 notify + get_mem + check_mem
 3. ★ check_mem（<1GB 中止）
 4. ★ git pull origin main（防遠端分歧）
 5. 啟動 notify（含 💾）
 6. 關鍵文件檢查
 7. 環境檢查
 8. 讀 SKILL.md, TODO.md 等
 9. Part ▶️ notify（check_mem + 💾）
10. Task ▶️ notify（get_mem + 💾）
11. 執行 Task
12. Task ✅ notify
13. 重複 10-12
14. ★ Part 結束: git commit + push ★
15. Part ✅ notify（含 ⏭️）
16. 重複 9-15
17. 錯誤 notify（含 💾）
18. xcodebuild
19. pytest
20. pbxproj 檢查
21. 文件同步
22. 審計報告
23. Git push + tag
24. 產生下一個 PROMPT
25. Sprint 完成 notify（100% + 💾）
26. 確認最終記憶體
```

---

## [MANDATORY] Sprint 完成自我審計

> 路徑: `docs/audit-reports/Sprint{X}_AuditReport.md`

### A. 代碼品質 | B. 文檔 8/8 | C. Xcode 8/8 | D. 評分

---

## 文件版本控制矩陣

| 文件 | Claude Code 可改？ |
|------|:-----------------:|
| `SKILL.md` / `CLAUDE.md` / `docs/addendum/*` / `docs/backups/*` | ❌ **絕對禁止** |
| `sprints/PROMPT_P{X}.md` / `docs/audit-reports/*` | ✅ 必須建立 |
| `README.md` / `TODO.md` / `CHANGELOG.md` | ✅ 必須更新 |
| `pyproject.toml` / `__init__.py` / `Info.plist` | ✅ 必須同步 |

---

## 重要限制

- ⚠️ **不得修改 CLAUDE.md / SKILL.md / addendum / backups**
- ⚠️ **xcodebuild + pytest 必須通過才能結束**
- ⚠️ **不得在 Sprint 中詢問用戶**
- ⚠️ **★ 每 Task ▶️ notify 含 💾 記憶體 | 每 Part ▶️ 前 check_mem ★**
- ⚠️ **★ 每 Part 結束必須 git commit + push（增量保存）★**
- ⚠️ **★ Sprint 啟動前必須 git pull origin main ★**
- ⚠️ **★ notify 主要收件人: +886972535899 ★**
- ⚠️ **Sprint 結束必須產生下一個 PROMPT**

---

## 版本演進歷史

| 版本 | 關鍵變更 |
|------|----------|
| v1.8.0~v1.13.0 | 基礎治理框架建立 |
| v1.14.0 | 🔴 P18 事故: 治理文件被截斷 → 人工恢復 |
| v1.15.0~v1.15.1 | 檔案夾重整 + Task 級通知 |
| v1.16.0~v1.16.2 | notify 顯式定義 + 文件保護 + 進度追蹤 |
| v1.17.0 | Task/Part 雙向通知 + 主要收件人 +886972535899 |
| v1.18.0 | 🔴 P24 OOM 事故 → 記憶體監控 (get_mem + check_mem) |
| **v1.19.0** | **★ 歷史教訓彙整 + Git 安全(Part 增量 commit) + 啟動前 git pull + 26 步流程** |

---

## 開發環境

| 環境 | 用途 | 路徑 |
|------|------|------|
| Mac Mini M4 (16GB) | Claude Code Sprint 執行 | `~/Documents/MyProjects/PromptBIMTestApp1` |
| MacBook | Xcode + Claude Desktop | 同上 |
| Windows RTX 4090 | VS2025 + Hydra Storm (P30+) | 見 docs/DevWindows_Setup.md |

### Mac Mini 測試 iMessage
```bash
osascript -e 'tell application "Messages" to send "🏗️ test" to participant "+886972535899" of (1st account whose service type = iMessage)'
```

---

*CLAUDE.md v1.19.0 | 2026-03-26*
*★ 歷史教訓: P18 截斷 + P22 notify 遺失 + P22.1 未 commit + P24 OOM + P24 Git 分歧*
*★ Git 安全: 每 Part commit+push + Sprint 前 git pull + push 失敗自動 rebase*
*★ 記憶體: get_mem + check_mem + <1GB 暫停*
*★ 26 步執行流程（含 git pull + Part commit + 記憶體檢查）*
*★ 主要收件人: +886972535899 | 備用: chchlin1018@icloud.com*
