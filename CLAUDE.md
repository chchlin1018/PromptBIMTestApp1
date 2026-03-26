# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.16.0 | **更新:** 2026-03-26
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

### Mac Mini 測試命令

```bash
osascript -e 'tell application "Messages" to send "🏗️ PromptBIM notify test ✅" to participant "chchlin1018@icloud.com" of (1st account whose service type = iMessage)'
```

### Sprint 啟動順序（不可調換）

```
1. 讀取 sprints/PROMPT_P{X}.md
2. ★ 定義 notify 函數 ★           ← 絕對第一步
3. ★ 發送啟動 iMessage ★          ← 緊接第二步
4. 執行環境檢查腳本（含 API Key 衝突檢查）
5. 讀取其他必讀文件（SKILL.md, TODO.md 等）
6. 開始執行 Task 1
```

---

## [MANDATORY] 專案檔案夾架構與檔名規則

> ⚠️ **P22 起生效。**

### Sprint Prompt: `sprints/PROMPT_P{X}.md`
### Audit Report: `docs/audit-reports/Sprint{X}_AuditReport.md`
### 根目錄只保留: CLAUDE.md, SKILL.md, README.md, SETUP.md, TODO.md, CHANGELOG.md, LICENSE, pyproject.toml

---

## [MANDATORY] 自動執行模式 — 不得詢問用戶

> ⚠️ **Claude Code 在執行 Sprint 時，不得中途停下來詢問用戶任何問題。**
> ⚠️ **所有決策由 Claude Code 自行判斷並執行。**

### 唯一例外（停下來通知用戶）

- `.env` 中的 API Key 未設定
- Git push 因為 remote 衝突失敗
- Xcode 缺少必要的 signing certificate
- **偵測到 ANTHROPIC_API_KEY 環境變數**

---

## [MANDATORY] 每個 Sprint 一個 PROMPT 檔案

```bash
claude --dangerously-skip-permissions -p "請讀取 sprints/PROMPT_P{X}.md 並執行所有 task。不要問任何問題。"
```

---

## [MANDATORY] iMessage 通知系統 — Task + Part + 錯誤 全覆蓋

> ⚠️ **所有 notify 呼叫都必須搭配 echo。**
> ⚠️ **通知粒度: 每個 Task、每個 Part、每次錯誤、每次修復嘗試。**

### 通知時機（全部必須執行）

| # | 時機 | echo | notify |
|---|------|:----:|:------:|
| 1 | **Sprint 啟動** | ✅ | ✅ |
| 2 | **每個 Task 完成** | ✅ | ✅ |
| 3 | **每個 Part 完成** | ✅ | ✅ |
| 4 | **Task 失敗（首次）** | ✅ | ✅ |
| 5 | **修復嘗試（第 2、3 次）** | ✅ | ✅ |
| 6 | **修復 3 次仍失敗（中斷）** | ✅ | ✅ |
| 7 | **審計完成** | ✅ | ✅ |
| 8 | **Git 推送完成** | ✅ | ✅ |
| 9 | **Sprint 最終完成** | ✅ | ✅ |

### 通知模板

```bash
# Task 完成
MSG="🏗️ PromptBIM P${SPRINT}
✅ Task ${TASK_NUM}: ${TASK_DESCRIPTION}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"

# Task 失敗
MSG="🏗️ PromptBIM P${SPRINT}
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)...
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"

# 中斷（3 次失敗）
MSG="🏗️ PromptBIM
❌ Sprint P${SPRINT} 中斷
📍 停在: Task ${TASK_NUM}
❗ 原因: ${ERROR_DESCRIPTION}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## [MANDATORY] 新建 PROMPT 檔案前的合規性檢查

```
☐ 最前面有 notify 函數定義（含 chchlin1018@icloud.com + +886972535899）
☐ notify 定義後緊接啟動通知
☐ 存放路徑: sprints/PROMPT_P{X}.md
☐ 每個 Task 有 echo + notify 完成通知
☐ 每個 Part 有 echo + notify 完成通知
☐ 包含 Task 失敗 + 中斷通知模板
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

## [MANDATORY] 環境檢查（含 API Key 衝突）

> 偵測到 ANTHROPIC_API_KEY → 停止 Sprint + notify 用戶

---

## [MANDATORY] Sprint 執行流程

```
1. 讀 PROMPT → 2. 定義 notify → 3. 啟動 notify
4. 環境檢查 → 5. 讀其他文件 → 6. 執行 Tasks
7. 每 Task notify → 8. 每 Part notify → 9. 錯誤 notify
10. xcodebuild → 11. pytest → 12. pbxproj → 13. 文件同步
14. 審計報告 → 15. Git push → 16. notify Git
17. tag → 18. 下個 PROMPT → 19. 完成報告 → 20. 最終 notify
```

---

## [MANDATORY] 嚴格檢查清單

```
□ notify 函數已定義（第一步）
□ 啟動通知已發送（第二步）
□ 環境檢查通過
□ xcodebuild BUILD SUCCEEDED
□ pytest 全部通過
□ 每個 Task 都有 echo + notify
□ 每個 Part 都有 echo + notify
□ 錯誤和修復都有 echo + notify
□ 文件版本同步
□ 審計報告已產生
□ git push 完成
□ 最終完成 notify 已發送
```

---

## 文件版本控制矩陣

| 文件 | Claude Code 可改？ |
|------|:-----------------:|
| `SKILL.md` / `CLAUDE.md` / `docs/addendum/*.md` | ❌ **絕對禁止** |
| `sprints/PROMPT_P{X}.md` / `docs/audit-reports/*` | ✅ 必須建立 |
| `README.md` / `TODO.md` / `CHANGELOG.md` | ✅ 必須更新 |
| `pyproject.toml` / `__init__.py` / `Info.plist` | ✅ 必須同步 |

---

## 重要限制

- ⚠️ **不得修改 CLAUDE.md / SKILL.md / addendum**
- ⚠️ **xcodebuild + pytest 必須通過才能結束**
- ⚠️ **不得在 Sprint 中詢問用戶**
- ⚠️ **每個 Task/Part 完成必須 notify**
- ⚠️ **每次錯誤必須立即 notify**
- ⚠️ **notify 函數必須在 PROMPT 最前面顯式定義**

---

## 版本演進歷史

| 版本 | 關鍵變更 |
|------|----------|
| v1.8.0~v1.13.0 | 基礎治理框架建立 |
| v1.14.0 | P18 違規截斷事件 |
| v1.14.1 | 人工恢復 |
| v1.15.0 | 專案檔案夾重整 (sprints/ + docs/audit-reports/) |
| v1.15.1 | 通知系統強化 (Task 級通知) |
| **v1.16.0** | **notify 函數顯式定義 + iMessage 收件人 + 啟動順序修正 (P22 教訓)** |

---

*CLAUDE.md v1.16.0 | 2026-03-26*
*P22 教訓: Claude Code -p 模式不載入 .zshrc → notify 必須在 PROMPT 中顯式定義*
*iMessage: chchlin1018@icloud.com / +886972535899*
