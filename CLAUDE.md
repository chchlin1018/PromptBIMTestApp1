# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.13.0 | **更新:** 2026-03-26
> **版本控制:** 本文件由人工維護，Claude Code 不得直接修改
> ⚠️ 本文件中標記為 **[MANDATORY]** 的規則必須嚴格執行，不得跳過

---

## 開發前必讀順序

```
1. PROMPT_P{X}.md ← 當前 Sprint 的執行指令（最重要！）
2. SKILL.md       ← 專案 SSOT（架構、Schema、Agent Prompt、開發規範）
3. TODO.md        ← 確認當前 Sprint 狀態
4. 對應 Addendum   ← 依當前 Sprint 讀取技術規格
5. CLAUDE.md      ← 本文件（行為規範）
```

---

## 專案本質

這是一個 **概念驗證 (POC)** macOS 桌面應用，使用 **Xcode 專案** 包裝 Python 核心。

---

## [MANDATORY] 自動執行模式 — 不得詢問用戶

> ⚠️ **Claude Code 在執行 Sprint 時，不得中途停下來詢問用戶任何問題。**
> ⚠️ **所有決策由 Claude Code 自行判斷並執行。答案永遠是 Yes / OK。**

### 規則

1. **不要問「是否要繼續？」** — 直接繼續
2. **不要問「要用 A 還是 B 方案？」** — 自己選擇最佳方案並執行
3. **不要問「這樣可以嗎？」** — 直接做，不需確認
4. **遇到錯誤不要問** — 自己修復，修到通過為止
5. **遇到模糊需求** — 參考 SKILL.md 和 Addendum 自行決定
6. **需要安裝新套件** — 直接安裝
7. **檔案衝突** — 以 SKILL.md 為準

### 唯一例外

只有在以下情況可以停下來通知用戶：
- `.env` 中的 API Key 未設定
- Git push 因為 remote 衝突失敗
- Xcode 缺少必要的 signing certificate

---

## [MANDATORY] 每個 Sprint 一個 PROMPT 檔案

> ⚠️ **每個 Sprint 必須有獨立的 Prompt 檔案。**

### CLI 啟動格式

```bash
claude --dangerously-skip-permissions -p "請讀取 PROMPT_P{X}.md 並執行所有 task。不要問任何問題。"
```

---

## [MANDATORY] Sprint 啟動通知必須是第一個動作

> ⚠️ **讀完必讀文件後、執行任何 Task 之前，第一個動作必須是發送啟動 iMessage。**
> ⚠️ **不得先執行 Task 1 再補發通知。啟動通知是所有工作的前提。**

### 啟動順序（不可調換）

```
1. 讀取 PROMPT_P{X}.md + 必讀文件
2. 執行環境檢查腳本
3. ★ 發送啟動 iMessage（下方模板）★  ← 必須在此時發送
4. 開始執行 Task 1
```

### 啟動通知模板

```bash
MSG="🏗️ PromptBIM
🚀 Sprint ${SPRINT} 開始執行
📋 Task: ${TASK_COUNT} 項（${PART_COUNT} Parts）
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## [MANDATORY] 新建 PROMPT 檔案前的合規性檢查

> ⚠️ **在建立新的 PROMPT_P{X+1}.md 之前，必須檢查以下合規性項目：**

### 合規性檢查清單

```
☐ 重新讀取 CLAUDE.md — 確認新 PROMPT 符合所有 [MANDATORY] 規則
☐ 重新讀取 SKILL.md — 確認新 PROMPT 不違反專案架構與開發規範
☐ 新 PROMPT 包含「執行指令」段落，且包含以下提醒：
   - 全量文件同步提醒
   - Xcode pbxproj 檢查提醒
   - iMessage 通知提醒（含啟動通知 + Part 完成通知 + 最終完成通知）
☐ 新 PROMPT 在 Part A 之前有明確的「啟動通知步驟」（不只是提醒文字）
☐ 新 PROMPT 的 Task 清單與 TODO.md 一致
☐ 新 PROMPT 的前置 Sprint 狀態正確（已完成的標記為 ✅）
☐ 新 PROMPT 的驗收標準包含 xcodebuild + pytest + 文件同步 + pbxproj 檢查
```

### PROMPT 檔案必含內容

每個 `PROMPT_P{X}.md` 必須包含：

1. **啟動通知步驟**（在所有 Part/Task 之前，作為獨立段落）
2. **執行指令段落**（含全量文件同步 + pbxproj + iMessage 提醒）

---

## [MANDATORY] Xcode pbxproj 完整性檢查

> ⚠️ **每次 Sprint 完成後，必須驗證 Xcode 專案的完整性和正確性。**

### pbxproj 檢查清單

```
☐ xcodebuild BUILD SUCCEEDED
☐ 所有 .swift 檔案都在 pbxproj 中被正確引用（無孤立檔案）
☐ Info.plist 設定正確：
   - CFBundleShortVersionString = 正確版本
   - CFBundleVersion = 正確 build number（與 Sprint 號對應）
   - NSSupportsAutomaticTermination = false
   - NSSupportsSuddenTermination = false
☐ Signing 設定正確：ad-hoc signing, ENABLE_USER_SCRIPT_SANDBOXING = NO
☐ Bundle ID 一致：com.realitymatrix.PromptBIMTestApp1
☐ macOS Deployment Target 正確（14.0+）
☐ 新增的 Swift 檔案已加入 Compile Sources build phase
☐ 新增的支援檔案類型已加入 CFBundleDocumentTypes
```

### 自動檢查腳本（Sprint 完成時執行）

```bash
xcodebuild -project PromptBIMTestApp1.xcodeproj \
    -scheme PromptBIMTestApp1 -destination 'platform=macOS' build 2>&1 | tail -5
for f in PromptBIMTestApp1/*.swift; do
    fname=$(basename "$f")
    grep -q "$fname" PromptBIMTestApp1.xcodeproj/project.pbxproj || echo "❌ $fname 未在 pbxproj 中引用"
done
plutil -p PromptBIMTestApp1/Info.plist | grep -E 'CFBundleVersion|CFBundleShortVersion|SuddenTermination|AutomaticTermination'
```

---

## [MANDATORY] iMessage 通知系統

> ⚠️ **Sprint 的完整通知流程：啟動 → 每個 Part 完成 → 最終完成。**
> ⚠️ **如果 Sprint 執行中遇到錯誤或中斷，也必須發送通知。**
> ⚠️ **所有 notify 呼叫都必須搭配 echo，讓訊息同步出現在 terminal 上。**

### 通知方式（三種，按優先順序嘗試）

```bash
# 方式 1（推薦）: 全域 notify 命令
notify "訊息內容"
# 方式 2: 專案腳本
./scripts/notify_imessage.sh "訊息內容"
# 方式 3（fallback）: 直接寫觸發檔
echo "訊息內容" > /tmp/imessage_notify.txt
```

### ⚠️ 每次發送通知：先 echo 再 notify

```bash
# ✅ 正確：echo + notify 同步
MSG="🏗️ PromptBIM ..."
echo "$MSG"
notify "$MSG"

# ❌ 錯誤：只有 notify，terminal 沒有輸出
notify "..."
```

---

## [MANDATORY] 錯誤或中斷時必須發送通知

> ⚠️ **Sprint 執行中發生無法自行修復的錯誤或中斷，必須在中斷前 echo + notify。**

### 錯誤通知模板

```bash
MSG="🏗️ PromptBIM
❌ Sprint ${SPRINT} 執行中斷
📍 停在: ${CURRENT_TASK_OR_PART}
❗ 原因: ${ERROR_DESCRIPTION}
🧪 pytest: ${TEST_COUNT_SO_FAR}
💡 建議: ${SUGGESTED_ACTION}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### 需要發送錯誤通知的情況

| 情況 | 通知內容 |
|------|----------|
| `.env` API Key 未設定 | 停在哪個 Task + 需要設定 API Key |
| Git push remote 衝突 | 衝突的 branch + 建議 `git pull --rebase` |
| pytest 修 3 次仍失敗 | 失敗的測試名稱 + 錯誤訊息摘要 |
| xcodebuild 修 3 次仍失敗 | build error 摘要 |
| 依賴安裝失敗 | 套件名 + 錯誤訊息 |
| Context window 即將耗盡 | 當前進度 + 已完成的 Part/Task |

---

## [MANDATORY] Sprint 完成後自我審計

> ⚠️ **每次 Sprint 完成後，在最終 commit 之前，必須執行自我審計並產出以下文件。**
> ⚠️ **這些步驟在全量文件同步之後、git commit 之前執行。**
> ⚠️ **審計範圍包含代碼、文檔、Xcode 專案三大領域，缺一不可。**

### 步驟 1: 產生 Sprint 審計報告

- 檔案名稱：`docs/reports/Sprint{X}_AuditReport.md`
- 格式參考：專案根目錄的 `AuditReport.md`（全專案審計報告）
- **必須包含以下所有審計項目：**

#### A. 代碼品質審計
  - 本次 Sprint 新增/修改的檔案列表（含行數統計）
  - 代碼品質觀察（DRY、命名、例外處理、型別提示）
  - 測試覆蓋觀察（新增測試數、覆蓋率變化、是否有未測試的路徑）
  - 潛在問題或技術債

#### B. 文檔完整性審計
  - 逐一驗證以下 8 項文件是否已更新到最新狀態：

```
☐ TODO.md — 所有 task 標記 ✅，版本號正確
☐ CHANGELOG.md — 有新版本條目，版本對照表已更新
☐ README.md — 測試數、版本號正確
☐ docs/PromptBIM_Context_Prompt.md — Sprint 完成狀態、版本、測試數正確
☐ pyproject.toml — version 與 CHANGELOG 一致
☐ src/promptbim/__init__.py — __version__ 與 pyproject.toml 一致
☐ Info.plist — CFBundleShortVersionString 與 pyproject.toml 一致
☐ SKILL.md — 如有架構變更，是否需要更新（標記需要/不需要）
```

  - 如有任何文件不一致，**必須在審計報告中標記為 ❌ 並說明差異**

#### C. Xcode pbxproj 完整性審計
  - 執行 pbxproj 檢查腳本，將結果納入報告：

```
☐ xcodebuild BUILD SUCCEEDED
☐ 所有 .swift 檔案在 pbxproj 中正確引用
☐ Info.plist CFBundleVersion = {Sprint 號}
☐ Info.plist CFBundleShortVersionString = {目標版本}
☐ NSSupportsAutomaticTermination = false
☐ NSSupportsSuddenTermination = false
☐ Signing 設定正確
☐ Bundle ID = com.realitymatrix.PromptBIMTestApp1
```

  - 如有任何項目未通過，**必須在審計報告中標記為 ❌ 並說明問題**

#### D. 評分
  - 綜合評分：A / B / C / D
  - 代碼品質分數
  - 文檔完整性分數（8 項中幾項 ✅）
  - Xcode 完整性分數（8 項中幾項 ✅）

- 完成後在 terminal 印出：

```bash
echo "📋 已產生 Sprint 審計報告: docs/reports/Sprint${X}_AuditReport.md"
echo "📊 評分: ${GRADE} | 代碼: ${CODE_GRADE} | 文檔: ${DOC_SCORE}/8 | Xcode: ${XCODE_SCORE}/8"
```

### 步驟 2: 根據審計報告產生建議 Sprint Prompt

- 如果審計報告發現問題或改善建議，自動產生建議修復的 Prompt 檔案
- 檔案名稱：`PROMPT_P{X}.1.md`（建議性質，非必須執行）
- 內容：根據審計報告中的潛在問題和技術債，整理為可執行的 Task 清單
- 必須通過 CLAUDE.md 合規性檢查
- 如果審計報告評分為 A 且文檔 8/8 且 Xcode 8/8，可以跳過：

```bash
echo "✅ Sprint 審計評分 A（文檔 8/8, Xcode 8/8），無需產生建議修復 Prompt"
```

- 如果有產生建議 Prompt：

```bash
echo "📋 已產生建議修復 Prompt: PROMPT_P${X}.1.md（根據審計報告建議）"
```

### 步驟 3: Git 推送並顯示最新狀態

- 所有文件（包含審計報告和建議 Prompt）必須在同一個 commit 中推送
- 推送完成後，必須在 terminal 顯示 Git 最新狀態：

```bash
echo "========================================"
echo "📦 Git 推送完成 — 最新狀態"
echo "========================================"
git log --oneline -3
echo ""
echo "📄 本次變更檔案:"
git diff --name-only HEAD~1
echo ""
echo "🏷️ Tags:"
git tag --sort=-creatordate | head -3
echo "========================================"
```

- 同時發送 notify（包含 git 狀態摘要）：

```bash
MSG="🏗️ PromptBIM
📦 Sprint ${SPRINT} Git 推送完成
📝 最新 commit: $(git log --oneline -1)
📄 變更 $(git diff --name-only HEAD~1 | wc -l | tr -d ' ') 個檔案
🏷️ git tag ${VERSION}
📋 審計: ${GRADE} | 文檔 ${DOC_SCORE}/8 | Xcode ${XCODE_SCORE}/8
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## [MANDATORY] Sprint 完成輸出模板

> ⚠️ **不得用英文一行帶過。必須使用中文 checklist 格式。**

### 完成 Checklist

```
Sprint P{X} complete. Checklist:

✅ xcodebuild BUILD SUCCEEDED
✅ Xcode pbxproj 完整性檢查通過
✅ pytest {N} passed
✅ TODO.md 已更新 (P{X} section + v{VERSION})
✅ CHANGELOG.md 已更新 ([{VERSION}] section + version table)
✅ README.md 已更新 (badges: {N} tests, v{VERSION})
✅ docs/PromptBIM_Context_Prompt.md 已同步至最新狀態
✅ pyproject.toml version 已同步
✅ __init__.py __version__ 已同步
✅ Sprint 審計報告已產生 (docs/reports/Sprint{X}_AuditReport.md)
✅ 審計: {GRADE} | 文檔 {DOC_SCORE}/8 | Xcode {XCODE_SCORE}/8
✅ 建議修復 Prompt 已產生（或審計全 A 免產生）
✅ git commit + push 完成（含審計報告）
✅ Git 最新狀態已顯示在 terminal + notify
✅ PROMPT_P{X+1}.md 已建立（已通過合規性檢查）
✅ iMessage 通知已發送（啟動 + 每個 Part 完成 + 審計 + 最終完成）
✅ git tag v{VERSION} 已建立並推送
```

### 下次繼續指令（必須輸出）

```
====================================================
下次繼續開發，在任何一台 Mac 上執行：
====================================================

cd ~/Documents/MyProjects/PromptBIMTestApp1
conda activate promptbim
claude --dangerously-skip-permissions -p "請讀取 PROMPT_P{X+1}.md 並執行所有 task。不要問任何問題。"

目前進度: Sprint P{X} ✅ 已完成
下一個: Sprint P{X+1}: {名稱}
上次 xcodebuild: ✅ BUILD SUCCEEDED
上次 pytest: ✅ {N} passed
執行機器: {hostname}
審計報告: docs/reports/Sprint{X}_AuditReport.md

====================================================
```

> ⚠️ **三個部分（Checklist + 下次指令 + iMessage）缺一不可。**

---

## [MANDATORY] Sprint 完成全量文件同步

> ⚠️ **每個 Sprint 完成時，必須將所有專案文件更新到反映最新狀態。**

### 必須更新的文件清單

| # | 文件 | 必須反映的最新資訊 | 必要性 |
|---|------|--------------------|:------:|
| 1 | `TODO.md` | 當前 Sprint 所有 task 標記 ✅ | **必須** |
| 2 | `CHANGELOG.md` | 新增版本條目 + 版本對照表 | **必須** |
| 3 | `README.md` | 最新測試數、版本號 | **必須** |
| 4 | `docs/PromptBIM_Context_Prompt.md` | 反映最新 Sprint、版本、測試數 | **必須** |
| 5 | `pyproject.toml` | version 欄位 | **必須** |
| 6 | `src/promptbim/__init__.py` | `__version__` | **必須** |
| 7 | `docs/reports/Sprint{X}_AuditReport.md` | 自我審計報告 | **必須** |
| 8 | `SKILL.md` | 僅在 PROMPT 明確要求時 | 條件 |

---

## [MANDATORY] 跨機器環境檢查

> ⚠️ **每次 Sprint 開始前，必須先檢查執行環境。**

### 環境檢查腳本

```bash
echo "========================================"
echo "🖥️  環境檢查 — $(hostname)"
echo "========================================"
echo "Hostname: $(hostname)"
echo "macOS: $(sw_vers -productVersion)"
echo "Git: $(git --version 2>/dev/null || echo '❌')"
echo "Xcode: $(xcodebuild -version 2>/dev/null | head -1 || echo '❌')"
echo "Python: $(python3 --version 2>/dev/null || echo '❌')"
echo "Conda: $(conda --version 2>/dev/null || echo '❌')"
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then echo "✅ 本地與遠端同步"
else echo "⚠️ 執行 git pull..."; git pull origin main; fi
```

---

## [MANDATORY] Sprint 執行流程（完整順序）

> ⚠️ **以下是 Sprint 從開始到結束的完整流程，順序不可調換。**

### 開始階段
1. 讀取 PROMPT_P{X}.md + 必讀文件
2. 執行環境檢查腳本
3. **★ echo + notify 啟動 iMessage ★**

### 執行階段
4. 依序執行 Task / Part
5. 每完成一個 Part → **echo + notify Part 完成 iMessage**
6. 遇到無法修復的錯誤 → **echo + notify 錯誤通知**

### 收尾階段
7. xcodebuild 驗證 ✅
8. pytest 驗證 ✅
9. Xcode pbxproj 完整性檢查 ✅
10. 全量文件同步 ✅

### 自我審計階段
11. **★ 產生 `docs/reports/Sprint{X}_AuditReport.md`（含代碼 + 文檔 + Xcode 三項審計）★**
12. **★ 如有建議，產生 `PROMPT_P{X}.1.md` ★**
13. echo 審計報告 + 評分 + 建議 Prompt 產生狀態

### 推送階段
14. Git Commit + Push（含審計報告）✅
15. **★ echo Git 最新狀態到 terminal ★**
16. **★ echo + notify Git 推送完成（含審計評分摘要）★**
17. git tag v{VERSION} + push tags

### 完成階段
18. 建立下一個 PROMPT（通過合規性檢查）✅
19. 輸出 Sprint 完成報告（依模板）✅
20. **★ echo + notify 最終完成 iMessage ★**

---

## [MANDATORY] 嚴格檢查清單（工作結束前逐項確認）

```
□ xcodebuild BUILD SUCCEEDED
□ Xcode pbxproj 完整性檢查通過
□ pytest 全部通過
□ TODO.md 已更新
□ CHANGELOG.md 已更新
□ README.md 已更新
□ docs/PromptBIM_Context_Prompt.md 已同步
□ pyproject.toml + __init__.py version 已同步
□ Sprint 審計報告已產生（含代碼 + 文檔 8/8 + Xcode 8/8 檢查）
□ 建議修復 Prompt 已處理（產生或全 A 免產生）
□ git commit + push 完成（含審計報告）
□ Git 最新狀態已顯示在 terminal + notify
□ 下一個 PROMPT_P{X+1}.md 已建立
□ Sprint 完成報告已按模板輸出
□ iMessage 已發送（啟動 + Part 完成 + 審計 + Git 推送 + 最終完成）
□ 所有通知都有 echo 到 terminal
```

**如果任何一項未完成，不得結束工作。**

---

## 文件版本控制矩陣

| 文件 | 誰更新 | 何時更新 | Claude Code 可改？ |
|------|--------|----------|:-----------------:|
| `SKILL.md` | 人工 | 架構變更 | ❌ 禁止 |
| `CLAUDE.md` | 人工 | 規範變更 | ❌ 禁止 |
| `docs/addendum/*.md` | 人工 | 規格變更 | ❌ 禁止 |
| `PROMPT_P{X}.md` | **Claude Code** | Sprint 完成時 | ✅ 必須建立 |
| `docs/reports/Sprint{X}_AuditReport.md` | **Claude Code** | Sprint 完成時 | ✅ **必須產生** |
| `PROMPT_P{X}.1.md` | **Claude Code** | 審計後有建議時 | ✅ 條件產生 |
| `README.md` | **Claude Code** | 每次 Sprint 完成 | ✅ 必須更新 |
| `TODO.md` | **Claude Code** | 每完成 1 個 task | ✅ 必須更新 |
| `CHANGELOG.md` | **Claude Code** | 每完成 1 個 Sprint | ✅ 必須更新 |
| `docs/PromptBIM_Context_Prompt.md` | **Claude Code** | 每完成 1 個 Sprint | ✅ **必須同步** |
| `pyproject.toml` | **Claude Code** | 版本變更時 | ✅ 必須同步 |
| `*.swift` / `*.xcodeproj` | **Claude Code** | Xcode 整合時 | ✅ 可更新 |

---

## Git Commit 規範

```
[P{X}] {Sprint描述} — session end: build OK, tests OK, docs updated
```

---

## 重要限制

- ⚠️ **不使用任何商業軟體或函式庫**
- ⚠️ Builder Agent **不使用 LLM**
- ⚠️ 所有座標使用**公尺制本地座標系**
- ⚠️ IFC 只用 `ifcopenshell.api.run()` 高階 API
- ⚠️ USD 只用 `pxr.Usd`, `pxr.UsdGeom`, `pxr.UsdShade`
- ⚠️ **xcodebuild 必須通過才能結束工作**
- ⚠️ **pytest 必須通過才能結束工作**
- ⚠️ **不得在 Sprint 執行中詢問用戶任何問題**

---

## 開發環境

- **平台:** macOS (Apple Silicon)
- **Python:** 3.11+
- **Xcode:** 16.0+ (SwiftUI, macOS target)
- **Swift:** 6.0+
- **套件管理:** Conda (Miniforge) + pip
- **IDE:** Claude Code CLI (`--dangerously-skip-permissions`)
- **Git:** main branch

---

*CLAUDE.md v1.13.0 | 2026-03-26 | 變更: 自我審計擴充為三大領域（A.代碼品質 + B.文檔完整性 8 項逐一驗證 + C.Xcode pbxproj 8 項逐一驗證）+ 審計評分含文檔分數和 Xcode 分數 + notify 含審計評分摘要*
