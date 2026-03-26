# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.8.0 | **更新:** 2026-03-26
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

## [MANDATORY] 新建 PROMPT 檔案前的合規性檢查

> ⚠️ **在建立新的 PROMPT_P{X+1}.md 之前，必須檢查以下合規性項目：**

### 合規性檢查清單

```
☐ 重新讀取 CLAUDE.md — 確認新 PROMPT 符合所有 [MANDATORY] 規則
☐ 重新讀取 SKILL.md — 確認新 PROMPT 不違反專案架構與開發規範
☐ 新 PROMPT 包含「執行指令」段落，且包含以下提醒：
   - 全量文件同步提醒
   - Xcode pbxproj 檢查提醒
   - iMessage 通知提醒
☐ 新 PROMPT 的 Task 清單與 TODO.md 一致
☐ 新 PROMPT 的前置 Sprint 狀態正確（已完成的標記為 ✅）
☐ 新 PROMPT 的驗收標準包含 xcodebuild + pytest + 文件同步 + pbxproj 檢查
```

### PROMPT 檔案必含內容

每個 `PROMPT_P{X}.md` 的「執行指令」段落必須包含：

```markdown
## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + 完成）。
```

---

## [MANDATORY] Xcode pbxproj 完整性檢查

> ⚠️ **每次 Sprint 完成後，必須驗證 Xcode 專案的完整性和正確性。**
> ⚠️ **不只是 xcodebuild BUILD SUCCEEDED，還要檢查專案配置的一致性。**

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
# 1. Build 驗證
xcodebuild -project PromptBIMTestApp1.xcodeproj \
    -scheme PromptBIMTestApp1 \
    -destination 'platform=macOS' \
    build 2>&1 | tail -5

# 2. 檢查 Swift 檔案是否都在 pbxproj 中
for f in PromptBIMTestApp1/*.swift; do
    fname=$(basename "$f")
    if ! grep -q "$fname" PromptBIMTestApp1.xcodeproj/project.pbxproj; then
        echo "❌ $fname 未在 pbxproj 中引用"
    fi
done

# 3. 檢查 Info.plist 關鍵設定
plutil -p PromptBIMTestApp1/Info.plist | grep -E 'CFBundleVersion|CFBundleShortVersion|SuddenTermination|AutomaticTermination'
```

---

## [MANDATORY] iMessage 通知系統

> ⚠️ **每次 Sprint 開始和結束時，必須透過 iMessage 發送通知給 Michael。**

### 通知方式（三種，按優先順序嘗試）

```bash
# 方式 1（推薦）: 全域 notify 命令
notify "訊息內容"

# 方式 2: 專案腳本
./scripts/notify_imessage.sh "訊息內容"

# 方式 3（fallback）: 直接寫觸發檔
echo "訊息內容" > /tmp/imessage_notify.txt
```

### Sprint 啟動時通知

```bash
notify "🏗️ PromptBIM
🚀 Sprint ${SPRINT} 開始執行
📋 Task: ${TASK_COUNT} 項
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
```

### Sprint 成功完成時通知

```bash
notify "🏗️ PromptBIM
✅ Sprint ${SPRINT} 完成
🧪 pytest: ${TEST_COUNT}
🔨 xcode: BUILD SUCCEEDED
📝 ${LAST_COMMIT}
➡️ 下一個: Sprint ${NEXT_SPRINT}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
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
✅ git commit + push 完成
✅ PROMPT_P{X+1}.md 已建立（已通過合規性檢查）
✅ iMessage 通知已發送（啟動 + 完成）
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

====================================================
```

> ⚠️ **三個部分（Checklist + 下次指令 + iMessage）缺一不可。**

---

## [MANDATORY] Sprint 完成全量文件同步

> ⚠️ **每個 Sprint 完成時，必須將所有專案文件更新到反映最新狀態。**
> ⚠️ **新建立的 PROMPT_P{X+1}.md 也必須包含本規則的提醒。**

### 必須更新的文件清單

| # | 文件 | 必須反映的最新資訊 | 必要性 |
|---|------|--------------------|:------:|
| 1 | `TODO.md` | 當前 Sprint 所有 task 標記 ✅，版本號更新 | **必須** |
| 2 | `CHANGELOG.md` | 新增當前 Sprint 的版本條目 + 更新版本對照表 | **必須** |
| 3 | `README.md` | 最新測試數、版本號、功能狀態 | **必須** |
| 4 | `docs/PromptBIM_Context_Prompt.md` | 反映最新完成的 Sprint、版本、測試數、下一步 | **必須** |
| 5 | `pyproject.toml` | version 欄位與 CHANGELOG 一致 | **必須** |
| 6 | `src/promptbim/__init__.py` | `__version__` 與 pyproject.toml 一致 | **必須** |
| 7 | `SETUP.md` | 如果安裝步驟有變更 | 條件 |
| 8 | `SKILL.md` | 僅在 PROMPT 明確要求時更新 | 條件 |

### 同步驗證清單

```
☐ TODO.md 中當前 Sprint 所有 task 為 ✅
☐ CHANGELOG.md 有 [v{VERSION}] 新條目
☐ CHANGELOG.md 版本對照表包含當前 Sprint
☐ README.md 中的 test count 和 version 是最新的
☐ docs/PromptBIM_Context_Prompt.md 的 Sprint 完成狀態、版本、測試數正確
☐ pyproject.toml version 與 CHANGELOG 一致
☐ __init__.py __version__ 與 pyproject.toml 一致
```

### 常見遺漏（過去發生過的問題）

| 問題 | 後果 | 防止方式 |
|------|------|----------|
| Context Prompt 仍寫 P12 待執行，但 P13 已完成 | 新對話讀取到過時資訊 | 每次更新 Context Prompt |
| pyproject.toml 版本 0.1.0 但 CHANGELOG 已到 1.4.0 | `--version` 顯示錯誤 | 每次同步 version |
| P13 完成但未發送 iMessage | 用戶不知道完成 | checklist 強制檢查 |
| pbxproj 中新增 Swift 檔未加入 | Xcode 編譯成功但缺少檔案 | pbxproj 完整性檢查 |

---

## [MANDATORY] 跨機器環境檢查

> ⚠️ **每次 Sprint 開始前，必須先檢查執行環境。**

### 環境檢查腳本（每次 Sprint 開始前必須執行）

```bash
echo "========================================"
echo "🖥️  環境檢查 — $(hostname)"
echo "========================================"
echo ""
echo "Hostname: $(hostname)"
echo "macOS: $(sw_vers -productVersion)"
echo "Git: $(git --version 2>/dev/null || echo '❌')"
echo "Xcode: $(xcodebuild -version 2>/dev/null | head -1 || echo '❌')"
echo "Python: $(python3 --version 2>/dev/null || echo '❌')"
echo "Conda: $(conda --version 2>/dev/null || echo '❌')"
echo ""
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then echo "✅ 本地與遠端同步"
else echo "⚠️ 執行 git pull..."; git pull origin main; fi
```

### 環境差異自動處理

| 情況 | 處理 |
|------|------|
| `git pull` 有新 commits | 自動 pull |
| Conda env 不存在 | 自動建立 + 安裝依賴 |
| `.env` 不存在 | 停下通知用戶填入 API Key |
| Xcode 未安裝 | 停下通知用戶安裝 |

---

## [MANDATORY] 每次工作結束必須執行的步驟

> ⚠️ **以下步驟是強制性的，不得省略。**

### Step 1: xcodebuild 驗證 ✅
### Step 2: pytest 驗證 ✅
### Step 3: Xcode pbxproj 完整性檢查 ✅
### Step 4: 全量文件同步 ✅
### Step 5: Git Commit + Push ✅
### Step 6: 建立下一個 PROMPT（通過合規性檢查）✅
### Step 7: 輸出 Sprint 完成報告（依模板）✅
### Step 8: iMessage 通知 ✅

---

## [MANDATORY] 嚴格檢查清單（工作結束前逐項確認）

```
□ xcodebuild BUILD SUCCEEDED
□ Xcode pbxproj 完整性檢查通過（Swift 檔案、Info.plist、Signing）
□ pytest 全部通過
□ TODO.md 已更新
□ CHANGELOG.md 已更新
□ README.md 已更新
□ docs/PromptBIM_Context_Prompt.md 已同步
□ pyproject.toml + __init__.py version 已同步
□ git commit + push 完成
□ 下一個 PROMPT_P{X+1}.md 已建立（已通過合規性檢查）
□ Sprint 完成報告已按模板輸出
□ iMessage 通知已發送（啟動 + 完成）
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

*CLAUDE.md v1.8.0 | 2026-03-26 | 變更: 新增 PROMPT 合規性檢查 + Xcode pbxproj 完整性檢查 + 精簡重複內容*
