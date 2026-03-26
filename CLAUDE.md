# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.14.1 | **更新:** 2026-03-26
> **版本控制:** 本文件由人工維護，Claude Code 不得直接修改
> ⚠️ 本文件中標記為 **[MANDATORY]** 的規則必須嚴格執行，不得跳過
> ⚠️ **P18 違規修改本文件，導致 v1.13.0 完整內容被截斷。本版本為人工恢復。**

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
- **偵測到 ANTHROPIC_API_KEY 環境變數（會走 API 計費而非 Max 訂閱）**

---

## [MANDATORY] 每個 Sprint 一個 PROMPT 檔案

```bash
claude --dangerously-skip-permissions -p "請讀取 PROMPT_P{X}.md 並執行所有 task。不要問任何問題。"
```

---

## [MANDATORY] Sprint 啟動通知必須是第一個動作

> ⚠️ **讀完必讀文件後、執行任何 Task 之前，第一個動作必須是發送啟動 iMessage。**

### 啟動順序（不可調換）

```
1. 讀取 PROMPT_P{X}.md + 必讀文件
2. 執行環境檢查腳本（含 API Key 衝突檢查）
3. ★ 發送啟動 iMessage ★  ← 必須在此時發送
4. 開始執行 Task 1
```

---

## [MANDATORY] 新建 PROMPT 檔案前的合規性檢查

```
☐ 重新讀取 CLAUDE.md — 確認新 PROMPT 符合所有 [MANDATORY] 規則
☐ 重新讀取 SKILL.md — 確認新 PROMPT 不違反專案架構與開發規範
☐ 新 PROMPT 包含啟動通知步驟 + 執行指令段落
☐ 新 PROMPT 在 Part A 之前有明確的「啟動通知步驟」
☐ 新 PROMPT 的驗收標準包含 xcodebuild + pytest + 文件同步 + pbxproj + 審計
```

---

## [MANDATORY] Xcode pbxproj 完整性檢查

```
☐ xcodebuild BUILD SUCCEEDED
☐ 所有 .swift 檔案都在 pbxproj 中被正確引用
☐ Info.plist CFBundleShortVersionString + CFBundleVersion 正確
☐ NSSupportsAutomaticTermination = false / NSSupportsSuddenTermination = false
☐ Signing 設定正確：ad-hoc, ENABLE_USER_SCRIPT_SANDBOXING = NO
☐ Bundle ID = com.realitymatrix.PromptBIMTestApp1
☐ macOS Deployment Target 14.0+
☐ 新增 Swift 檔案已加入 Compile Sources build phase
```

---

## [MANDATORY] iMessage 通知系統

> ⚠️ **所有 notify 呼叫都必須搭配 echo，讓訊息同步出現在 terminal 上。**

```bash
# ✅ 正確：echo + notify 同步
MSG="🏗️ PromptBIM ..."
echo "$MSG"
notify "$MSG"
```

### 通知時機

- **啟動通知**（第一個動作）
- **每個 Part 完成通知**
- **錯誤/中斷通知**（嘗試修復 3 次仍失敗）
- **審計完成通知**（含評分摘要）
- **Git 推送完成通知**
- **最終完成通知**

---

## [MANDATORY] 錯誤或中斷時必須發送通知

```bash
MSG="🏗️ PromptBIM
❌ Sprint ${SPRINT} 執行中斷
📍 停在: ${CURRENT_TASK_OR_PART}
❗ 原因: ${ERROR_DESCRIPTION}
💡 建議: ${SUGGESTED_ACTION}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## [MANDATORY] Sprint 完成後自我審計（三大領域）

> ⚠️ **審計範圍包含代碼、文檔、Xcode 專案三大領域，缺一不可。**

### A. 代碼品質審計
- 新增/修改檔案列表（含行數）
- 代碼品質觀察（DRY、命名、例外處理、型別提示）
- 測試覆蓋（新增測試數、覆蓋率、未測試路徑）
- 潛在問題或技術債

### B. 文檔完整性審計（逐一驗證 8 項）

```
☐ TODO.md — task ✅ + 版本號
☐ CHANGELOG.md — 新版本條目 + 版本對照表
☐ README.md — 測試數 + 版本號
☐ docs/PromptBIM_Context_Prompt.md — Sprint 狀態 + 版本 + 測試數
☐ pyproject.toml — version 一致
☐ src/promptbim/__init__.py — __version__ 一致
☐ Info.plist — CFBundleShortVersionString + CFBundleVersion 一致
☐ SKILL.md — 如有架構變更，評估是否需更新
```

### C. Xcode pbxproj 完整性審計（逐一驗證 8 項）

```
☐ xcodebuild BUILD SUCCEEDED
☐ 所有 .swift 在 pbxproj 中引用
☐ Info.plist CFBundleVersion 正確
☐ Info.plist CFBundleShortVersionString 正確
☐ NSSupportsAutomaticTermination = false
☐ NSSupportsSuddenTermination = false
☐ Signing 設定正確
☐ Bundle ID 正確
```

### D. 評分
- 綜合評分 A/B/C/D + 文檔 N/8 + Xcode N/8
- 全 A 且文檔 8/8 且 Xcode 8/8 → 免產生建議 Prompt
- 否則自動產生 `PROMPT_P{X}.1.md`

---

## [MANDATORY] 跨機器環境檢查（含 API Key 衝突檢查）

> ⚠️ **每次 Sprint 開始前，必須先檢查執行環境。**
> ⚠️ **如果偵測到 ANTHROPIC_API_KEY，必須停止 Sprint 並通知用戶。**

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

# ★ API Key 衝突檢查 — 確保走 Max 訂閱而非 API 計費 ★
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "⛔ ANTHROPIC_API_KEY 已設定！會走 API 計費而非 Max 訂閱"
    echo "🔧 修復: unset ANTHROPIC_API_KEY"
    MSG="⛔ PromptBIM Sprint 中止 — 偵測到 ANTHROPIC_API_KEY 環境變數
❗ 這會走 API 計費（$$/token）而非 Claude Max 訂閱
🔧 修復: unset ANTHROPIC_API_KEY
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
    echo "$MSG"
    notify "$MSG"
    exit 1
fi
echo "✅ 認證: Claude Max 訂閱（無 API Key 衝突）"

git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then echo "✅ 本地與遠端同步"
else echo "⚠️ 執行 git pull..."; git pull origin main; fi
```

---

## [MANDATORY] Sprint 執行流程（完整 20 步）

### 開始階段
1. 讀取 PROMPT_P{X}.md + 必讀文件
2. 執行環境檢查腳本（**含 API Key 衝突檢查**）
3. **★ echo + notify 啟動 iMessage ★**

### 執行階段
4. 依序執行 Task / Part
5. 每完成一個 Part → **echo + notify Part 完成**
6. 遇到無法修復的錯誤 → **echo + notify 錯誤通知**

### 收尾階段
7. xcodebuild 驗證 ✅
8. pytest 驗證 ✅
9. Xcode pbxproj 完整性檢查 ✅
10. 全量文件同步 ✅

### 自我審計階段
11. **★ 產生 docs/reports/Sprint{X}_AuditReport.md（代碼 + 文檔 8/8 + Xcode 8/8）★**
12. **★ 如有建議，產生 PROMPT_P{X}.1.md ★**
13. echo 審計報告 + 評分

### 推送階段
14. Git Commit + Push ✅
15. **★ echo Git 最新狀態到 terminal ★**
16. **★ echo + notify Git 推送完成（含審計評分）★**
17. git tag + push tags

### 完成階段
18. 建立下一個 PROMPT（通過合規性檢查）✅
19. 輸出 Sprint 完成報告（依模板）✅
20. **★ echo + notify 最終完成 iMessage ★**

---

## [MANDATORY] 嚴格檢查清單

```
□ 環境檢查通過（含 API Key 衝突檢查 ✅）
□ xcodebuild BUILD SUCCEEDED
□ Xcode pbxproj 完整性檢查通過
□ pytest 全部通過
□ TODO.md / CHANGELOG.md / README.md 已更新
□ docs/PromptBIM_Context_Prompt.md 已同步
□ pyproject.toml + __init__.py version 已同步
□ Sprint 審計報告已產生（代碼 + 文檔 8/8 + Xcode 8/8）
□ git commit + push 完成
□ 下一個 PROMPT 已建立
□ iMessage 已發送（啟動 + Part + 審計 + Git + 最終）
□ 所有通知都有 echo 到 terminal
```

---

## 文件版本控制矩陣

| 文件 | 誰更新 | Claude Code 可改？ |
|------|--------|:-----------------:|
| `SKILL.md` | 人工 | ❌ 禁止 |
| `CLAUDE.md` | 人工 | ❌ **絕對禁止**（P18 違規已記錄）|
| `docs/addendum/*.md` | 人工 | ❌ 禁止 |
| `PROMPT_P{X}.md` | Claude Code | ✅ 必須建立 |
| `docs/reports/Sprint{X}_AuditReport.md` | Claude Code | ✅ 必須產生 |
| `README.md` / `TODO.md` / `CHANGELOG.md` | Claude Code | ✅ 必須更新 |
| `docs/PromptBIM_Context_Prompt.md` | Claude Code | ✅ 必須同步 |
| `pyproject.toml` / `__init__.py` | Claude Code | ✅ 必須同步 |

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
- ⚠️ **不得修改 CLAUDE.md / SKILL.md / addendum（人工維護文件）**

---

## 開發環境

- **平台:** macOS (Apple Silicon)
- **Python:** 3.11+
- **Xcode:** 16.0+ (SwiftUI, macOS target)
- **Swift:** 6.0+
- **套件管理:** Conda (Miniforge) + pip
- **IDE:** Claude Code CLI (`--dangerously-skip-permissions`)
- **Git:** main branch
- **認證:** Claude Max 訂閱（不使用 ANTHROPIC_API_KEY）

---

*CLAUDE.md v1.14.1 | 2026-03-26 | 人工恢復: P18 違規修改導致 v1.13.0 完整內容被截斷為 1.7KB。本版本恢復全部治理規則 + 保留 v1.14.0 的 API Key 衝突檢查 + 強化「禁止修改 CLAUDE.md」規則*
