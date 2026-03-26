# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.17.0 | **更新:** 2026-03-26
> **版本控制:** 本文件由人工維護，Claude Code 不得直接修改
> ⚠️ 本文件中標記為 **[MANDATORY]** 的規則必須嚴格執行，不得跳過
> ⚠️ **P18 違規修改本文件，導致 v1.13.0 完整內容被截斷。本版本為人工恢復。**

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

## [MANDATORY] notify 函數定義 — Sprint 的絕對第一步

> ⚠️ **這是每個 Sprint 的第一個動作。在讀取任何其他文件之前，必須先定義 notify 函數。**
> ⚠️ **P22 教訓: Claude Code `-p` 模式不載入 `.zshrc`，所以 shell 中的 `notify` 函數不存在。**
> ⚠️ **所有新建的 PROMPT 必須在最前面包含此定義。沒有 notify 定義的 PROMPT 不合規。**

### notify 函數實作（複製到每個 PROMPT 的最前面）

> ⚠️ **主要收件人: `+886972535899`（手機號碼，確保收到）**
> ⚠️ **備用收件人: `chchlin1018@icloud.com`**

```bash
# ===== ★★★ Sprint 絕對第一步：定義 notify 函數 ★★★ =====
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
echo "✅ notify 函數已定義"
```

### iMessage 收件人

```
★ 主要: +886972535899          ← 手機號碼，最優先
  備用: chchlin1018@icloud.com  ← iCloud 帳號
```

### Sprint 啟動順序（不可調換）

```
1. 讀取 sprints/PROMPT_P{X}.md
2. ★ 定義 notify 函數 ★           ← 絕對第一步
3. ★ 發送啟動 iMessage ★          ← 緊接第二步
4. ★ 執行關鍵文件完整性檢查 ★      ← 第三步
5. 執行環境檢查腳本（含 API Key 衝突檢查）
6. 讀取其他必讀文件（SKILL.md, TODO.md 等）
7. 開始執行 Task 1
```

---

## [MANDATORY] 通知規則 — 每個 Task/Part 的「啟動」和「結束」都必須 notify

> ⚠️ **這是 v1.17.0 最重要的新增規則。**
> ⚠️ **不是只在完成時 notify，而是「開始做」和「做完」都要各發一次。**
> ⚠️ **這讓用戶即時知道 Claude Code 正在做什麼、何時做完。**
> ⚠️ **缺少任何一則啟動或結束通知的 PROMPT 不合規。**

### 通知時機表（全部必須執行，不可省略）

| # | 時機 | echo | notify | 內容 |
|---|------|:----:|:------:|------|
| 1 | **Sprint 啟動** | ✅ | ✅ | 總覽（Tasks/Parts 數量 + 目標版本） |
| 2 | **每個 Task ▶️ 啟動** | ✅ | ✅ | `▶️ Task N 開始: {描述}` + 進度% |
| 3 | **每個 Task ✅ 結束** | ✅ | ✅ | `✅ Task N 完成: {描述}` + 進度% |
| 4 | **每個 Part ▶️ 啟動** | ✅ | ✅ | `▶️ Part X 開始: {描述}` + 含幾個 Tasks |
| 5 | **每個 Part ✅ 結束** | ✅ | ✅ | `✅ Part X 完成` + 進度% + ⏭️ 下一步 |
| 6 | **Task 失敗** | ✅ | ✅ | `⚠️ Task N 失敗` + 錯誤 + 嘗試修復 |
| 7 | **修復嘗試** | ✅ | ✅ | 嘗試次數 + 修復方式 |
| 8 | **中斷（3次失敗）** | ✅ | ✅ | 停止位置 + 原因 + 完成度% |
| 9 | **關鍵文件損壞** | ✅ | ✅ | 恢復命令 |
| 10 | **審計完成** | ✅ | ✅ | 評分摘要 |
| 11 | **Git 推送完成** | ✅ | ✅ | commit hash + tag |
| 12 | **Sprint 最終完成** | ✅ | ✅ | 100% + 測試數 |

### 通知模板（嚴格範本 — 新建 PROMPT 必須照抄）

#### Task 啟動通知 ▶️

```bash
TASK_DONE=$((TASK_DONE))  # 尚未完成，不加 1
PCT=$((TASK_DONE * 100 / TASK_TOTAL))
MSG="🏗️ PromptBIM P${SPRINT}
▶️ Task ${TASK_NUM}/${TASK_TOTAL} 開始: ${TASK_DESCRIPTION}
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Task 結束通知 ✅

```bash
TASK_DONE=$((TASK_DONE + 1))
PCT=$((TASK_DONE * 100 / TASK_TOTAL))
MSG="🏗️ PromptBIM P${SPRINT}
✅ Task ${TASK_NUM}/${TASK_TOTAL} 完成: ${TASK_DESCRIPTION}
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Part 啟動通知 ▶️

```bash
MSG="🏗️ PromptBIM P${SPRINT}
▶️ Part ${PART} 開始: ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Part 結束通知 ✅

```bash
PART_DONE=$((PART_DONE + 1))
PCT=$((TASK_DONE * 100 / TASK_TOTAL))
MSG="🏗️ PromptBIM P${SPRINT} Part ${PART} ✅
📋 ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
⏭️ 下一步: Part ${NEXT_PART} (${NEXT_PART_TASKS} tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Task 失敗通知 ⚠️

```bash
MSG="🏗️ PromptBIM P${SPRINT}
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)...
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### 中斷通知 ❌

```bash
MSG="🏗️ PromptBIM
❌ Sprint P${SPRINT} 中斷
📍 停在: Task ${TASK_NUM}/${TASK_TOTAL} (${TASK_DESCRIPTION})
❗ 原因: ${ERROR_DESCRIPTION}
📊 完成度: ${PCT}% (${TASK_DONE}/${TASK_TOTAL} tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Sprint 完成通知 🎉

```bash
MSG="🏗️ PromptBIM Sprint P${SPRINT} 完成 🎉
📋 ${SPRINT_DESCRIPTION}
🏷️ v${VERSION} | ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts
📊 完成度: 100% ✅
🧪 Tests: ${TEST_SUMMARY}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## [MANDATORY] 關鍵文件保護與備份機制

### 受保護文件

| 文件 | 最低大小 | 恢復命令 |
|------|---------|---------|
| `CLAUDE.md` | 5,000 bytes | `git checkout 9599bc08 -- CLAUDE.md` |
| `SKILL.md` | 20,000 bytes | `git checkout 15fc0efe -- SKILL.md` |

### Sprint 啟動時的完整性檢查（MANDATORY）

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

## [MANDATORY] 專案檔案夾架構與檔名規則

### Sprint Prompt: `sprints/PROMPT_P{X}.md`
### Audit Report: `docs/audit-reports/Sprint{X}_AuditReport.md`

---

## [MANDATORY] 自動執行模式 — 不得詢問用戶

唯一例外: API Key 未設定 / Git push 衝突 / Xcode 簽名 / ANTHROPIC_API_KEY / 關鍵文件損壞

---

## [MANDATORY] 新建 PROMPT 檔案前的嚴格合規性檢查

> ⚠️ **每一條都必須滿足，否則 PROMPT 不合規，不得推送。**

```
☐ 最前面有 notify 函數定義（主要: +886972535899 / 備用: chchlin1018@icloud.com）
☐ notify 定義後緊接啟動通知
☐ 啟動通知後有關鍵文件完整性檢查
☐ 啟動通知後有環境檢查（含 ANTHROPIC_API_KEY 衝突）
☐ 存放路徑: sprints/PROMPT_P{X}.md
☐ ★ 每個 Task 有「啟動 ▶️」和「結束 ✅」兩則 notify ★
☐ ★ 每個 Part 有「啟動 ▶️」和「結束 ✅」兩則 notify ★
☐ 每則 notify 含進度（Task N/Total | Part N/Total | %）
☐ Part 結束 notify 含 ⏭️ 下一步預告
☐ 包含 Task 失敗 + 中斷通知模板（含進度）
☐ 驗收標準含 xcodebuild + pytest + 文件同步 + pbxproj + 審計
☐ Audit Report 路徑: docs/audit-reports/Sprint{X}_AuditReport.md
☐ Sprint 結束必須產生下一個 PROMPT
```

---

## [MANDATORY] Xcode pbxproj 完整性檢查

```
☐ xcodebuild BUILD SUCCEEDED
☐ 所有 .swift 在 pbxproj 中
☐ Info.plist 版本正確
☐ NSSupportsAutomaticTermination = false
☐ NSSupportsSuddenTermination = false
☐ Signing: ad-hoc
☐ Bundle ID = com.realitymatrix.PromptBIMTestApp1
☐ 新增 Swift 檔案已加入 Compile Sources
```

---

## [MANDATORY] Sprint 完成後自我審計（三大領域）

> 審計報告: `docs/audit-reports/Sprint{X}_AuditReport.md`

### A. 代碼品質 | B. 文檔 8/8 | C. Xcode 8/8 | D. 評分

---

## [MANDATORY] Sprint 執行流程（完整 22 步）

```
1. 讀 PROMPT → 2. 定義 notify → 3. 啟動 notify（含總覽）
4. 關鍵文件檢查 → 5. 環境檢查 → 6. 讀其他文件
7. Part ▶️ 啟動 notify → 8. Task ▶️ 啟動 notify → 9. 執行 Task
10. Task ✅ 結束 notify → 11. 重複 8-10 直到 Part 完畢
12. Part ✅ 結束 notify（含下一步）→ 13. 重複 7-12 直到全部完畢
14. 錯誤 notify（如發生）
15. xcodebuild → 16. pytest → 17. pbxproj → 18. 文件同步
19. 審計報告 → 20. Git push + tag → 21. 產生下一個 PROMPT
22. Sprint 完成 notify（100%）
```

---

## [MANDATORY] 嚴格檢查清單

```
□ notify 函數已定義（第一步，主要收件人 +886972535899）
□ 啟動通知已發送
□ 關鍵文件完整性通過
□ 環境檢查通過
□ ★ 每個 Task 啟動有 ▶️ notify
□ ★ 每個 Task 結束有 ✅ notify
□ ★ 每個 Part 啟動有 ▶️ notify
□ ★ 每個 Part 結束有 ✅ notify（含下一步）
□ 錯誤和修復都有 notify
□ xcodebuild BUILD SUCCEEDED
□ pytest 全部通過
□ 文件版本同步
□ 審計報告已產生
□ git push + tag 完成
□ 下一個 PROMPT 已建立
□ 最終完成 notify 已發送（100%）
```

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
- ⚠️ **★ 每個 Task/Part 的啟動和結束都必須 notify（共 2 則）★**
- ⚠️ **★ notify 主要收件人: +886972535899 ★**
- ⚠️ **每次錯誤必須立即 notify**
- ⚠️ **notify 函數必須在 PROMPT 最前面顯式定義**
- ⚠️ **Sprint 啟動時必須檢查 CLAUDE.md + SKILL.md 大小**
- ⚠️ **Sprint 結束必須產生下一個 PROMPT**

---

## 版本演進歷史

| 版本 | 關鍵變更 |
|------|----------|
| v1.8.0~v1.13.0 | 基礎治理框架建立 |
| v1.14.0 | P18 違規截斷事件 |
| v1.14.1 | 人工恢復 |
| v1.15.0 | 專案檔案夾重整 (sprints/ + docs/audit-reports/) |
| v1.15.1 | 通知系統強化 (Task 級通知) |
| v1.16.0 | notify 函數顯式定義 + iMessage 收件人 + 啟動順序修正 |
| v1.16.1 | 關鍵文件保護機制 — backup SHA + 完整性檢查 |
| v1.16.2 | 通知進度追蹤 — Task N/Total + Part N/Total + 完成% |
| **v1.17.0** | **★ Task/Part 啟動+結束雙向通知 + 主要收件人改 +886972535899 + 嚴格範本 ★** |

---

*CLAUDE.md v1.17.0 | 2026-03-26*
*★ 核心變更: 每個 Task/Part 啟動 ▶️ 和結束 ✅ 都必須 notify*
*★ 主要收件人: +886972535899 | 備用: chchlin1018@icloud.com*
