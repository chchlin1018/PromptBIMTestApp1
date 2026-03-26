# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.16.2 | **更新:** 2026-03-26
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

```bash
# ===== ★★★ Sprint 絕對第一步：定義 notify 函數 ★★★ =====
notify() {
    local msg="$1"
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"chchlin1018@icloud.com\" of targetService
            send \"$msg\" to targetBuddy
        end tell
    " 2>/dev/null || \
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"+886972535899\" of targetService
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
主要: chchlin1018@icloud.com
備用: +886972535899
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

## [MANDATORY] 關鍵文件保護與備份機制

> ⚠️ **這些文件一旦損壞，整個治理框架失效。必須有保護機制。**

### 受保護文件

| 文件 | 最低大小 | 已知良好 SHA | 恢復命令 |
|------|---------|------------|---------|
| `CLAUDE.md` | 5,000 bytes | `dfcf0de7` | `git checkout 9599bc08 -- CLAUDE.md` |
| `SKILL.md` | 20,000 bytes | `5a0c0620` | `git checkout 15fc0efe -- SKILL.md` |

### Sprint 啟動時的完整性檢查（MANDATORY）

```bash
# ===== 關鍵文件完整性檢查 =====
CLAUDE_SIZE=$(wc -c < CLAUDE.md 2>/dev/null | tr -d ' ')
SKILL_SIZE=$(wc -c < SKILL.md 2>/dev/null | tr -d ' ')

if [ "$CLAUDE_SIZE" -lt 5000 ] 2>/dev/null; then
    MSG="⛔ CLAUDE.md 已損壞！大小: ${CLAUDE_SIZE} bytes (應 >= 5000)
🔧 恢復: git checkout 9599bc08 -- CLAUDE.md"
    echo "$MSG" && notify "$MSG"
    exit 1
fi

if [ "$SKILL_SIZE" -lt 20000 ] 2>/dev/null; then
    MSG="⛔ SKILL.md 已損壞！大小: ${SKILL_SIZE} bytes (應 >= 20000)
🔧 恢復: git checkout 15fc0efe -- SKILL.md"
    echo "$MSG" && notify "$MSG"
    exit 1
fi

echo "✅ 關鍵文件完整性: CLAUDE.md ${CLAUDE_SIZE}B, SKILL.md ${SKILL_SIZE}B"
```

### 備份規則

1. **Claude Code 絕對禁止修改** `CLAUDE.md`、`SKILL.md`、`docs/backups/`
2. `docs/backups/README.md` 記錄恢復指南 + SHA 表
3. `scripts/backup_verify.sh` 可在 Sprint 前後手動執行

---

## [MANDATORY] 專案檔案夾架構與檔名規則

> ⚠️ **P22 起生效。**

### Sprint Prompt: `sprints/PROMPT_P{X}.md`
### Audit Report: `docs/audit-reports/Sprint{X}_AuditReport.md`
### 根目錄只保留: CLAUDE.md, SKILL.md, README.md, SETUP.md, TODO.md, CHANGELOG.md, LICENSE, pyproject.toml

---

## [MANDATORY] 自動執行模式 — 不得詢問用戶

> ⚠️ **Claude Code 在執行 Sprint 時，不得中途停下來詢問用戶任何問題。**

### 唯一例外（停下來通知用戶）

- `.env` 中的 API Key 未設定
- Git push 因為 remote 衝突失敗
- Xcode 缺少必要的 signing certificate
- **偵測到 ANTHROPIC_API_KEY 環境變數**
- **關鍵文件完整性檢查失敗**

---

## [MANDATORY] 每個 Sprint 一個 PROMPT 檔案

```bash
claude --dangerously-skip-permissions -p "請讀取 sprints/PROMPT_P{X}.md 並執行所有 task。不要問任何問題。"
```

---

## [MANDATORY] iMessage 通知系統 — 含進度追蹤

> ⚠️ **所有 notify 必須搭配 echo。**
> ⚠️ **每則通知必須包含進度資訊：完成數 / 總數 + 完成百分比。**
> ⚠️ **讓用戶一看通知就知道：做完什麼、還剩多少、完成度幾 %。**

### 通知時機（全部必須執行）

| # | 時機 | echo | notify | 進度 |
|---|------|:----:|:------:|:----:|
| 1 | **Sprint 啟動** | ✅ | ✅ | 總覽 |
| 2 | **每個 Task 完成** | ✅ | ✅ | ✅ |
| 3 | **每個 Part 完成** | ✅ | ✅ | ✅ |
| 4 | **Task 失敗** | ✅ | ✅ | ✅ |
| 5 | **修復嘗試** | ✅ | ✅ | ✅ |
| 6 | **中斷（3次失敗）** | ✅ | ✅ | ✅ |
| 7 | **關鍵文件損壞** | ✅ | ✅ | — |
| 8 | **審計完成** | ✅ | ✅ | ✅ |
| 9 | **Git 推送完成** | ✅ | ✅ | ✅ |
| 10 | **Sprint 最終完成** | ✅ | ✅ | 100% |

### 通知模板（含進度追蹤）

> ⚠️ **PROMPT 創建時，必須在每個 Task/Part 通知中計算並帶入以下變數：**
> - `TASK_DONE` / `TASK_TOTAL` — 已完成 Task 數 / 總 Task 數
> - `PART_DONE` / `PART_TOTAL` — 已完成 Part 數 / 總 Part 數
> - `PCT` — 完成百分比（= TASK_DONE * 100 / TASK_TOTAL）

#### Task 完成通知

```bash
MSG="🏗️ PromptBIM P${SPRINT}
✅ Task ${TASK_NUM}: ${TASK_DESCRIPTION}
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

**範例輸出：**
```
🏗️ PromptBIM P22
✅ Task 7: IFC thread safety fixed (IFC-01 + IFC-02)
📊 進度: Task 7/36 | Part 0/6 | 19%
📍 MichaeldeMac-mini | 03/26 17:55
```

#### Part 完成通知

```bash
MSG="🏗️ PromptBIM P${SPRINT} Part ${PART} ✅
📋 ${PART_DESCRIPTION} (${TASK_COUNT} tasks)
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
⏭️ 下一步: Part ${NEXT_PART} (${NEXT_PART_TASKS} tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

**範例輸出：**
```
🏗️ PromptBIM P22 Part A ✅
📋 C++ Critical + Robustness (7 tasks)
📊 進度: Task 13/36 | Part 1/6 | 36%
⏭️ 下一步: Part B (8 tasks)
📍 MichaeldeMac-mini | 03/26 18:10
```

#### Task 失敗通知

```bash
MSG="🏗️ PromptBIM P${SPRINT}
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)...
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### 中斷通知（3 次修復失敗）

```bash
MSG="🏗️ PromptBIM
❌ Sprint P${SPRINT} 中斷
📍 停在: Task ${TASK_NUM}/${TASK_TOTAL} (${TASK_DESCRIPTION})
❗ 原因: ${ERROR_DESCRIPTION}
📊 完成度: ${PCT}% (${TASK_DONE}/${TASK_TOTAL} tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

#### Sprint 最終完成通知

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

## [MANDATORY] 新建 PROMPT 檔案前的合規性檢查

```
☐ 最前面有 notify 函數定義（含 chchlin1018@icloud.com + +886972535899）
☐ notify 定義後緊接啟動通知
☐ 啟動通知後有關鍵文件完整性檢查
☐ 存放路徑: sprints/PROMPT_P{X}.md
☐ 每個 Task 通知含進度（Task N/Total | Part N/Total | %）
☐ 每個 Part 通知含進度 + 下一步預告
☐ 包含 Task 失敗 + 中斷通知模板（含進度）
☐ 驗收標準含 xcodebuild + pytest + 文件同步 + pbxproj + 審計
☐ Audit Report 路徑: docs/audit-reports/Sprint{X}_AuditReport.md
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

## [MANDATORY] Sprint 執行流程

```
1. 讀 PROMPT → 2. 定義 notify → 3. 啟動 notify（含總覽）
4. 關鍵文件檢查 → 5. 環境檢查 → 6. 讀其他文件
7. 執行 Tasks → 8. 每 Task notify（含進度%）→ 9. 每 Part notify（含進度% + 下一步）
10. 錯誤 notify（含進度%）→ 11. xcodebuild → 12. pytest
13. pbxproj → 14. 文件同步 → 15. 審計報告
16. Git push → 17. notify Git → 18. tag
19. 下個 PROMPT → 20. 完成報告 → 21. 最終 notify（100%）
```

---

## [MANDATORY] 嚴格檢查清單

```
□ notify 函數已定義（第一步）
□ 啟動通知已發送（第二步，含 Sprint 總覽）
□ 關鍵文件完整性通過（第三步）
□ 環境檢查通過
□ xcodebuild BUILD SUCCEEDED
□ pytest 全部通過
□ 每個 Task 都有 echo + notify（含進度 %）
□ 每個 Part 都有 echo + notify（含進度 % + 下一步）
□ 錯誤和修復都有 echo + notify（含進度 %）
□ 文件版本同步
□ 審計報告已產生
□ git push 完成
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
- ⚠️ **每個 Task/Part notify 必須含進度（N/Total + %）**
- ⚠️ **每次錯誤必須立即 notify（含進度 %）**
- ⚠️ **notify 函數必須在 PROMPT 最前面顯式定義**
- ⚠️ **Sprint 啟動時必須檢查 CLAUDE.md + SKILL.md 大小**

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
| **v1.16.2** | **通知進度追蹤 — Task N/Total + Part N/Total + 完成% + 下一步預告** |

---

*CLAUDE.md v1.16.2 | 2026-03-26*
*通知必須含: Task 7/36 | Part 1/6 | 19% | ⏭️ 下一步: Part B*
*iMessage: chchlin1018@icloud.com / +886972535899*
