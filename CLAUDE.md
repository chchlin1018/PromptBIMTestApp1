# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.5.0 | **更新:** 2026-03-25
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

用戶只需要：
- 輸入土地資料（或隨意描述面積）
- 輸入 AI Prompt（如 "帶游泳池的3層別墅"）

系統自動完成所有後續工作（BIM 生成、MEP、法規、4D/5D、監控點、即時修改）。

---

## [MANDATORY] 自動執行模式 — 不得詢問用戶

> ⚠️ **Claude Code 在執行 Sprint 時，不得中途停下來詢問用戶任何問題。**
> ⚠️ **所有決策由 Claude Code 自行判斷並執行。答案永遠是 Yes / OK。**

### 規則

1. **不要問「是否要繼續？」** — 直接繼續
2. **不要問「要用 A 還是 B 方案？」** — 自己選擇最佳方案並執行
3. **不要問「這樣可以嗎？」** — 直接做，不需確認
4. **遇到錯誤不要問** — 自己修復，修到通過為止
5. **遇到模糊需求** — 參考 SKILL.md 和 Addendum 自行決定，不要問
6. **需要安裝新套件** — 直接安裝，不要問
7. **檔案衝突** — 以 SKILL.md 為準，不要問

### 唯一例外

只有在以下情況可以停下來通知用戶（不是問問題，是通知）：
- `.env` 中的 API Key 未設定（無法繼續）
- Git push 因為 remote 衝突失敗（需要手動 resolve）
- Xcode 缺少必要的 signing certificate

**通知格式：**
```
⚠️ 無法繼續: {原因}
請手動處理後，重新執行: claude --dangerously-skip-permissions -p "繼續 Sprint P{X}"
```

---

## [MANDATORY] 每個 Sprint 一個 PROMPT 檔案

> ⚠️ **每個 Sprint 必須有獨立的 Prompt 檔案，用於啟動和追蹤該 Sprint。**

### 命名規則

```
PROMPT.md        ← 總覽（Sprint 目錄 + 通用規則）
PROMPT_P0.md     ← Sprint P0 專用執行指令
PROMPT_P1.md     ← Sprint P1 專用執行指令
PROMPT_P2.md     ← Sprint P2 專用執行指令
...
PROMPT_P8.5.md   ← Sprint P8.5 專用執行指令
```

### Sprint 完成時，必須建立下一個 Sprint 的 PROMPT 檔案

每個 `PROMPT_P{X}.md` 必須包含：

```markdown
# PROMPT_P{X}.md — Sprint P{X}: {名稱}

> 版本: v1.0.0 | 建立時間: {日期}
> 前置 Sprint: P{X-1} ✅ 已完成
> 依賴: {列出依賴的 Sprint}

## 環境檢查（見下方 [MANDATORY] 環境檢查）

## 必讀文件
1. SKILL.md
2. TODO.md
3. CLAUDE.md
4. {對應的 Addendum 檔案}

## 本 Sprint 的 Task 清單
（從 TODO.md 複製該 Sprint 的所有 task）

## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。

## 驗收標準
{從 TODO.md 複製}
```

### CLI 啟動格式

```bash
# 每個 Sprint 獨立啟動
claude --dangerously-skip-permissions -p "請讀取 PROMPT_P0.md 並執行所有 task。不要問任何問題。"
claude --dangerously-skip-permissions -p "請讀取 PROMPT_P1.md 並執行所有 task。不要問任何問題。"
claude --dangerously-skip-permissions -p "請讀取 PROMPT_P2.md 並執行所有 task。不要問任何問題。"
```

---

## [MANDATORY] iMessage 通知系統

> ⚠️ **每次 Sprint 開始和結束時，必須透過 iMessage 發送通知給 Michael。**
> Mac Mini 上已設定全域 `notify` 命令 + LaunchAgent 自動發送。

### 通知方式（三種，按優先順序嘗試）

```bash
# 方式 1（推薦）: 全域 notify 命令
notify "訊息內容"

# 方式 2: 專案腳本
./scripts/notify_imessage.sh "訊息內容"

# 方式 3（fallback）: 直接寫觸發檔
echo "訊息內容" > /tmp/imessage_notify.txt
```

> ⚠️ 觸發檔路徑必須是 `/tmp/imessage_notify.txt`（不是 promptbim_notify.txt）
> ⚠️ 通知失敗不影響 Sprint 成功/失敗判定（best-effort）

### Sprint 啟動時通知（環境檢查完成後立即執行）

```bash
SPRINT="P{X}"
TASK_COUNT=$(grep -c "^- ⬜" PROMPT_P${SPRINT#P}.md 2>/dev/null || echo "?")
notify "🏗️ PromptBIM
🚀 Sprint ${SPRINT} 開始執行
📋 Task: ${TASK_COUNT} 項
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
```

### Sprint 成功完成時通知

```bash
SPRINT="P{X}"
NEXT_SPRINT="P{X+1}"
TEST_COUNT=$(python -m pytest tests/ --tb=no -q 2>&1 | tail -1)
LAST_COMMIT=$(git log --oneline -1)
notify "🏗️ PromptBIM
✅ Sprint ${SPRINT} 完成
🧪 pytest: ${TEST_COUNT}
🔨 xcode: BUILD SUCCEEDED
📝 ${LAST_COMMIT}
➡️ 下一個: Sprint ${NEXT_SPRINT}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
```

### Sprint 失敗或中斷時通知

```bash
notify "🏗️ PromptBIM
❌ Sprint ${SPRINT} 失敗
❗ ${ERROR_DESCRIPTION}
🧪 pytest: ${TEST_RESULT}
⚠️ 需要人工介入
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
```

---

## [MANDATORY] 跨機器環境檢查

> ⚠️ **每次 Sprint 開始前，必須先檢查執行環境。**
> ⚠️ **開發者可能從 MacBook Air、Mac Mini 等不同機器執行 Claude Code。**

### 環境檢查腳本（每次 Sprint 開始前必須執行）

```bash
echo "========================================"
echo "🖥️  環境檢查 — $(hostname)"
echo "========================================"
echo ""

# 1. 機器識別
echo "--- 機器資訊 ---"
echo "Hostname: $(hostname)"
echo "macOS: $(sw_vers -productVersion)"
echo "Chip: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo 'Apple Silicon')"
echo "User: $(whoami)"
echo ""

# 2. 開發工具
echo "--- 開發工具 ---"
echo "Git: $(git --version 2>/dev/null || echo '❌ 未安裝')"
echo "Xcode: $(xcodebuild -version 2>/dev/null | head -1 || echo '❌ 未安裝')"
echo "Python: $(python3 --version 2>/dev/null || echo '❌ 未安裝')"
echo "Conda: $(conda --version 2>/dev/null || echo '❌ 未安裝')"
echo ""

# 3. Git 狀態
echo "--- Git 狀態 ---"
git remote -v
git log --oneline -3
echo "Current branch: $(git branch --show-current)"
echo "Uncommitted changes: $(git status --porcelain | wc -l | tr -d ' ')"
echo ""

# 4. 同步遠端
echo "--- 同步遠端 ---"
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ 本地與遠端同步"
else
    echo "⚠️ 本地落後遠端，執行 git pull..."
    git pull origin main
fi
echo ""

# 5. Python 環境
echo "--- Python 環境 ---"
if conda info --envs 2>/dev/null | grep -q promptbim; then
    echo "✅ Conda env 'promptbim' 存在"
    conda activate promptbim 2>/dev/null || source activate promptbim 2>/dev/null
    python -c "
import sys; print(f'Python: {sys.version}')
try:
    import ifcopenshell; print(f'✅ IfcOpenShell {ifcopenshell.version}')
except: print('❌ IfcOpenShell 未安裝')
try:
    from pxr import Usd; print('✅ OpenUSD')
except: print('❌ OpenUSD 未安裝')
try:
    from PySide6.QtWidgets import QApplication; print('✅ PySide6')
except: print('❌ PySide6 未安裝')
try:
    import anthropic; print('✅ Anthropic SDK')
except: print('❌ Anthropic SDK 未安裝')
"
else
    echo "❌ Conda env 'promptbim' 不存在"
    echo "→ 執行: conda create -n promptbim python=3.11 -y"
    echo "→ 然後依照 SETUP.md 安裝依賴"
fi
echo ""

# 6. .env 檢查
echo "--- API Key ---"
if [ -f ".env" ]; then
    if grep -q "ANTHROPIC_API_KEY=sk-" .env; then
        echo "✅ .env 已設定 API Key"
    else
        echo "⚠️ .env 存在但 API Key 未設定"
    fi
else
    echo "❌ .env 不存在 → cp .env.example .env 並填入 API Key"
fi
echo ""

# 7. 必要文件檢查
echo "--- 必要文件 ---"
missing=0
for f in SKILL.md TODO.md CLAUDE.md PROMPT.md pyproject.toml; do
    if [ -f "$f" ]; then echo "✅ $f"; else echo "❌ $f"; missing=$((missing+1)); fi
done
echo ""

if [ $missing -eq 0 ]; then
    echo "========================================"
    echo "✅ 環境檢查通過，可以開始開發！"
    echo "========================================"
else
    echo "========================================"
    echo "⚠️ 有 $missing 個問題需要修復"
    echo "========================================"
fi
```

### 環境差異自動處理

| 情況 | Claude Code 自動處理方式 |
|------|-------------------------|
| `git pull` 有新 commits | 自動 pull，不問 |
| Conda env 不存在 | 自動建立 + 安裝依賴 |
| `.env` 不存在 | 複製 `.env.example`，**停下通知用戶填入 API Key** |
| `pip` 套件缺失 | 自動 `pip install`，不問 |
| Xcode 未安裝 | **停下通知用戶安裝 Xcode** |
| 檔案缺失 | 自動 `git pull`，如果還缺失則報錯 |

---

## [MANDATORY] Xcode 專案要求

### P0 必須建立 Xcode 專案

Sprint P0 必須建立 `PromptBIMTestApp1.xcodeproj`，包含：

```
PromptBIMTestApp1.xcodeproj/
└── project.pbxproj

PromptBIMTestApp1/                  # Xcode 原始碼群組
├── PromptBIMTestApp1App.swift      # macOS App Entry (SwiftUI)
├── ContentView.swift               # 主介面（嵌入 Python 後端）
├── PythonBridge.swift              # Process() 呼叫 Python 後端
├── Info.plist
├── Assets.xcassets/
│   └── AppIcon.appiconset/
└── Entitlements.entitlements
```

### xcodebuild 命令

```bash
xcodebuild -project PromptBIMTestApp1.xcodeproj \
           -scheme PromptBIMTestApp1 \
           -destination 'platform=macOS' \
           build 2>&1 | tail -5

# 預期: ** BUILD SUCCEEDED **
```

---

## [MANDATORY] 每次工作結束必須執行的步驟

> ⚠️ **以下步驟是強制性的，不得省略，不得以「下次再做」為由跳過。**

### Step 1: xcodebuild 驗證 ✅

```bash
xcodebuild -project PromptBIMTestApp1.xcodeproj \
           -scheme PromptBIMTestApp1 \
           -destination 'platform=macOS' \
           build 2>&1 | tail -20
# BUILD FAILED → 修復 → 重新 build → 直到 BUILD SUCCEEDED
```

### Step 2: pytest 驗證 ✅

```bash
conda activate promptbim
python -m pytest tests/ -v --tb=short
# 失敗 → 修復 → 重新跑 → 直到全部通過
```

### Step 3: 更新所有專案文件 ✅

| # | 文件 | 更新內容 |
|---|------|---------|
| 1 | `TODO.md` | 已完成的 task 標記 ✅ |
| 2 | `CHANGELOG.md` | 如果完成 Sprint，加入新版本條目 |
| 3 | `SETUP.md` | 如果安裝步驟有變更 |
| 4 | `README.md` | 如果功能有重大變更 |

### Step 4: Git Commit + Push ✅

```bash
git add -A
git commit -m "[P{X}] {Sprint描述} — session end: build OK, tests OK, docs updated"
git push origin main
```

### Step 5: 建立下一個 Sprint 的 PROMPT 檔案 ✅

```bash
# 例如完成 P0 後，建立 PROMPT_P1.md
# 內容格式見上方「每個 Sprint 一個 PROMPT 檔案」規則
```

### Step 6: 輸出下次繼續的 CLI 命令 ✅

```
====================================================
📋 下次繼續開發，在任何一台 Mac 上執行:
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

### Step 7: iMessage 通知 ✅

> 見上方「[MANDATORY] iMessage 通知系統」章節的「Sprint 成功完成時通知」

---

## [MANDATORY] 嚴格檢查清單（工作結束前逐項確認）

```
□ xcodebuild BUILD SUCCEEDED
□ pytest 全部通過
□ TODO.md 已更新（完成的 task 標記 ✅）
□ CHANGELOG.md 已更新（如果完成 Sprint）
□ SETUP.md 已更新（如果安裝步驟變更）
□ README.md 已更新（如果功能變更）
□ git commit + push 完成
□ 下一個 Sprint 的 PROMPT_P{X+1}.md 已建立
□ 下次繼續的 CLI 命令已輸出
□ iMessage 通知已發送（啟動 + 完成/失敗都要通知）
```

**如果任何一項未完成，不得結束工作。**

---

## 文件版本控制矩陣

| 文件 | 誰更新 | 何時更新 | Claude Code 可改？ |
|------|--------|----------|:-----------------:|
| `SKILL.md` | 人工 | 架構變更 | ❌ 禁止 |
| `CLAUDE.md` | 人工 | 規範變更 | ❌ 禁止 |
| `docs/addendum/*.md` | 人工 | 規格變更 | ❌ 禁止 |
| `PROMPT.md` | 人工 | 總覽變更 | ❌ 禁止 |
| `PROMPT_P{X}.md` | **Claude Code** | Sprint 完成時建立下一個 | ✅ 必須建立 |
| `README.md` | **Claude Code** | 功能/狀態變更 | ✅ 必須更新 |
| `TODO.md` | **Claude Code** | 每完成 1 個 task | ✅ 必須更新 |
| `CHANGELOG.md` | **Claude Code** | 每完成 1 個 Sprint | ✅ 必須更新 |
| `SETUP.md` | **Claude Code** | 安裝步驟變更 | ✅ 可更新 |
| `src/**/*.py` | **Claude Code** | 開發時 | ✅ 核心工作 |
| `tests/**/*.py` | **Claude Code** | 開發時 | ✅ 核心工作 |
| `*.swift` | **Claude Code** | Xcode 整合時 | ✅ 可更新 |
| `*.xcodeproj` | **Claude Code** | 專案結構變更 | ✅ 可更新 |

---

## Git Commit 規範

```
[Sprint ID] 簡短描述

範例:
[P0] Init Xcode project + Python scaffold
[P1] Add GeoJSON land parser
[P4.8] Implement modification engine
```

工作結束 commit：
```
[P2] Complete IFC generator — session end: build OK, tests OK, docs updated
```

---

## 重要限制

- ⚠️ **不使用任何商業軟體或函式庫**
- ⚠️ Builder Agent **不使用 LLM**（純 Python 確定性程式碼）
- ⚠️ 所有座標使用**公尺制本地座標系**
- ⚠️ IFC 只用 `ifcopenshell.api.run()` 高階 API
- ⚠️ USD 只用 `pxr.Usd`, `pxr.UsdGeom`, `pxr.UsdShade`
- ⚠️ 修改指令用**增量更新**，不從頭重新生成
- ⚠️ 監控點輸出必須含 `monitor:` USD namespace（IDTF 對接）
- ⚠️ **xcodebuild 必須通過才能結束工作**
- ⚠️ **pytest 必須通過才能結束工作**
- ⚠️ **不得在 Sprint 執行中詢問用戶任何問題**

---

## 測試要求

- 每個新 module 至少有 1 個 pytest 測試
- BIM 生成必須驗證 IFC 檔案可被 IfcOpenShell 重新讀取
- USD 生成必須驗證 stage 可被 pxr.Usd.Stage.Open() 開啟
- GUI 測試使用 pytest-qt
- 修改引擎需驗證版本歷史一致性
- **xcodebuild build 必須成功**（每次 session 結束前）

---

## 開發環境

- **平台:** macOS (Apple Silicon) — 可能在 MacBook Air 或 Mac Mini 上執行
- **Python:** 3.11+
- **Xcode:** 16.0+ (含 SwiftUI, macOS target)
- **Swift:** 6.0+
- **套件管理:** Conda (Miniforge) + pip
- **IDE:** Claude Code CLI (`--dangerously-skip-permissions` 模式)
- **Git:** main branch
- **執行方式:** `claude --dangerously-skip-permissions -p "請讀取 PROMPT_P{X}.md 並執行所有 task。不要問任何問題。"`

---

*CLAUDE.md v1.5.0 | 2026-03-25 | 變更: 統一 iMessage 通知為全域 notify 命令 + 新增 Sprint 啟動通知 + 修正觸發檔路徑*
