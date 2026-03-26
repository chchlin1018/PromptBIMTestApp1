# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.15.1 | **更新:** 2026-03-26
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

## [MANDATORY] 專案檔案夾架構與檔名規則

> ⚠️ **P22 起生效。所有新建的 Sprint Prompt 和 Audit Report 必須遵守以下路徑規則。**

### Sprint Prompt 檔案

```
位置:  sprints/PROMPT_P{X}.md
範例:  sprints/PROMPT_P22.md
       sprints/PROMPT_P22.1.md  (修補 Sprint)
       sprints/PROMPT_P23.md
```

- **所有** Sprint Prompt 檔案存放在 `sprints/` 資料夾
- 檔名格式: `PROMPT_P{Sprint號碼}.md`（與歷史命名一致）
- 修補 Sprint 用小數點: `PROMPT_P{X}.{patch}.md`
- Claude Code 執行命令讀取路徑: `sprints/PROMPT_P{X}.md`

### Audit Report 檔案

```
位置:  docs/audit-reports/Sprint{X}_AuditReport.md
範例:  docs/audit-reports/Sprint22_AuditReport.md
       docs/audit-reports/Sprint22.1_AuditReport.md
       docs/audit-reports/AuditReport_Full_v2.8.0.md  (全面審計)
```

- **所有** Audit Report 存放在 `docs/audit-reports/` 資料夾
- Sprint 審計檔名: `Sprint{X}_AuditReport.md`
- 全面架構審計檔名: `AuditReport_{描述}_{版本}.md`
- 舊的 `docs/reports/` 資料夾保留非審計報告（Performance Comparison 等）

### 專案根目錄保留檔案（不放 Sprint/Audit 文件）

```
根目錄只保留:
  CLAUDE.md, SKILL.md, README.md, SETUP.md, TODO.md, CHANGELOG.md,
  LICENSE, pyproject.toml, requirements-frozen.txt, .env.example, .gitignore
```

### 完整目錄架構

```
PromptBIMTestApp1/
├── CLAUDE.md                          ← 治理規範（人工維護）
├── SKILL.md                           ← 專案 SSOT（人工維護）
├── README.md / SETUP.md / TODO.md / CHANGELOG.md
├── pyproject.toml / requirements-frozen.txt
├── sprints/                           ← ★ Sprint Prompt 檔案 ★
│   ├── PROMPT_P0.md ~ PROMPT_P22.md
│   └── PROMPT_P{X}.md (未來)
├── docs/
│   ├── audit-reports/                 ← ★ Audit Reports ★
│   │   ├── Sprint{X}_AuditReport.md
│   │   └── AuditReport_{desc}.md
│   ├── reports/                       ← 效能報告等非審計文件
│   ├── addendum/                      ← 技術規格（人工維護）
│   ├── reviews/                       ← Review 文件
│   └── DesignDocForV2.md, API.md, etc.
├── PromptBIMTestApp1/                 ← Swift 源碼
├── libpromptbim/                      ← C++ Core
├── src/promptbim/                     ← Python Backend
├── tests/                             ← Python Tests
├── examples/                          ← 範例
├── scripts/                           ← 工具腳本
└── output/                            ← 生成輸出
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
claude --dangerously-skip-permissions -p "請讀取 sprints/PROMPT_P{X}.md 並執行所有 task。不要問任何問題。"
```

> ⚠️ P22 起，PROMPT 檔案在 `sprints/` 資料夾。

---

## [MANDATORY] Sprint 啟動通知必須是第一個動作

> ⚠️ **讀完必讀文件後、執行任何 Task 之前，第一個動作必須是發送啟動 iMessage。**

### 啟動順序（不可調換）

```
1. 讀取 sprints/PROMPT_P{X}.md + 必讀文件
2. 執行環境檢查腳本（含 API Key 衝突檢查）
3. ★ 發送啟動 iMessage ★  ← 必須在此時發送
4. 開始執行 Task 1
```

---

## [MANDATORY] iMessage 通知系統 — Task + Part + 錯誤 全覆蓋

> ⚠️ **所有 notify 呼叫都必須搭配 echo，讓訊息同步出現在 terminal 上。**
> ⚠️ **通知粒度包含 Task 和 Part 兩個層級，加上錯誤和中斷通知。**

```bash
# ✅ 正確：echo + notify 同步
MSG="🏗️ PromptBIM ..."
echo "$MSG"
notify "$MSG"
```

### 通知時機（全部必須執行，不可省略）

| # | 時機 | echo | notify | 說明 |
|---|------|:----:|:------:|------|
| 1 | **Sprint 啟動** | ✅ | ✅ | 第一個動作 |
| 2 | **每個 Task 完成** | ✅ | ✅ | 含 Task 編號 + 簡述 |
| 3 | **每個 Part 完成** | ✅ | ✅ | 含 Part 名稱 + 摘要 |
| 4 | **Task 執行失敗（首次）** | ✅ | ✅ | 含 Task 編號 + 錯誤描述 + 「嘗試修復中」 |
| 5 | **修復嘗試（第 2、3 次）** | ✅ | ✅ | 含嘗試次數 + 修復方式 |
| 6 | **修復 3 次仍失敗（中斷）** | ✅ | ✅ | 含停止位置 + 原因 + 建議 |
| 7 | **審計完成** | ✅ | ✅ | 含評分摘要 |
| 8 | **Git 推送完成** | ✅ | ✅ | 含 commit hash + tag |
| 9 | **Sprint 最終完成** | ✅ | ✅ | 含總結 |

### Task 完成通知模板

```bash
MSG="🏗️ PromptBIM P${SPRINT}
✅ Task ${TASK_NUM}: ${TASK_DESCRIPTION}
📋 ${ISSUE_IDS_FIXED}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Part 完成通知模板

```bash
MSG="🏗️ PromptBIM P${SPRINT} Part ${PART} ✅
📋 ${PART_DESCRIPTION} (${TASK_COUNT} tasks)
✅ ${KEY_ACHIEVEMENTS}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Task 失敗通知模板

```bash
MSG="🏗️ PromptBIM P${SPRINT}
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)...
🔧 修復方式: ${FIX_APPROACH}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### 中斷通知模板（3 次修復失敗）

```bash
MSG="🏗️ PromptBIM
❌ Sprint P${SPRINT} 執行中斷
📍 停在: Task ${TASK_NUM} (${TASK_DESCRIPTION})
❗ 原因: ${ERROR_DESCRIPTION}
🔄 已嘗試修復 3 次均失敗
💡 建議: ${SUGGESTED_ACTION}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## [MANDATORY] 新建 PROMPT 檔案前的合規性檢查

```
☐ 重新讀取 CLAUDE.md — 確認新 PROMPT 符合所有 [MANDATORY] 規則
☐ 重新讀取 SKILL.md — 確認新 PROMPT 不違反專案架構與開發規範
☐ 新 PROMPT 存放路徑: sprints/PROMPT_P{X}.md（不在根目錄）
☐ 新 PROMPT 包含啟動通知步驟 + 執行指令段落
☐ 新 PROMPT 在 Part A 之前有明確的「啟動通知步驟」
☐ 新 PROMPT 每個 Task 有 echo + notify 完成通知
☐ 新 PROMPT 每個 Part 有 echo + notify 完成通知
☐ 新 PROMPT 包含 Task 失敗 + 中斷通知模板
☐ 新 PROMPT 的驗收標準包含 xcodebuild + pytest + 文件同步 + pbxproj + 審計
☐ Audit Report 存放路徑: docs/audit-reports/Sprint{X}_AuditReport.md
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

## [MANDATORY] Sprint 完成後自我審計（三大領域）

> ⚠️ **審計範圍包含代碼、文檔、Xcode 專案三大領域，缺一不可。**
> ⚠️ **審計報告存放位置: `docs/audit-reports/Sprint{X}_AuditReport.md`**

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
☐ SKILL.md — 如有架構變更，評估是否需要人工更新
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
- 否則自動產生 `sprints/PROMPT_P{X}.1.md`

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
1. 讀取 `sprints/PROMPT_P{X}.md` + 必讀文件
2. 執行環境檢查腳本（**含 API Key 衝突檢查**）
3. **★ echo + notify 啟動 iMessage ★**

### 執行階段
4. 依序執行 Task / Part
5. 每完成一個 Task → **echo + notify Task 完成**
6. 每完成一個 Part → **echo + notify Part 完成**
7. Task 失敗 → **echo + notify 錯誤通知**（立即，不等 3 次）
8. 自行修復，每次嘗試 → **echo + notify 修復狀態**
9. 修復 3 次仍失敗 → **echo + notify 中斷通知**

### 收尾階段
10. xcodebuild 驗證 ✅
11. pytest 驗證 ✅
12. Xcode pbxproj 完整性檢查 ✅
13. 全量文件同步 ✅

### 自我審計階段
14. **★ 產生 `docs/audit-reports/Sprint{X}_AuditReport.md`（代碼 + 文檔 8/8 + Xcode 8/8）★**
15. **★ 如有建議，產生 `sprints/PROMPT_P{X}.1.md` ★**
16. **★ echo + notify 審計完成（含評分）★**

### 推送階段
17. Git Commit + Push ✅
18. **★ echo + notify Git 推送完成（含 commit hash + 審計評分）★**
19. git tag + push tags

### 完成階段
20. 建立下一個 PROMPT（通過合規性檢查，存放在 `sprints/`）✅
21. 輸出 Sprint 完成報告（依模板）✅
22. **★ echo + notify 最終完成 iMessage ★**

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
□ Sprint 審計報告已產生（docs/audit-reports/Sprint{X}_AuditReport.md）
□ git commit + push 完成
□ 下一個 PROMPT 已建立（sprints/PROMPT_P{X+1}.md）
□ 每個 Task 完成都有 echo + notify
□ 每個 Part 完成都有 echo + notify
□ 錯誤和修復嘗試都有 echo + notify
□ iMessage 已發送（啟動 + Tasks + Parts + 審計 + Git + 最終）
□ 所有通知都有 echo 到 terminal
```

---

## 文件版本控制矩陣

| 文件 | 誰更新 | Claude Code 可改？ |
|------|--------|:-----------------:|
| `SKILL.md` | 人工 | ❌ 禁止 |
| `CLAUDE.md` | 人工 | ❌ **絕對禁止**（P18 違規已記錄）|
| `docs/addendum/*.md` | 人工 | ❌ 禁止 |
| `sprints/PROMPT_P{X}.md` | Claude Code | ✅ 必須建立 |
| `docs/audit-reports/Sprint{X}_AuditReport.md` | Claude Code | ✅ 必須產生 |
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
- ⚠️ **Sprint Prompt 必須放在 `sprints/` 資料夾**
- ⚠️ **Audit Report 必須放在 `docs/audit-reports/` 資料夾**
- ⚠️ **每個 Task 和 Part 完成後必須 echo + notify**
- ⚠️ **每次錯誤和修復嘗試都必須 echo + notify**

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

## 版本演進歷史

| 版本 | 關鍵變更 |
|------|----------|
| v1.8.0 | 起始版本（PROMPT 合規性檢查 + pbxproj 檢查）|
| v1.9.0 | Part 完成 iMessage 通知規則 |
| v1.10.0 | Sprint 啟動通知必須是第一個動作 |
| v1.11.0 | 錯誤/中斷 notify + 所有 notify 必須同步 echo |
| v1.12.0 | Sprint 完成後自我審計 |
| v1.13.0 | 三大領域審計（代碼 + 文檔 8/8 + Xcode 8/8）|
| v1.14.0 | P18 違規修改 — 截斷 18KB→1.7KB，只剩 API Key 檢查 |
| v1.14.1 | 人工恢復 — 完整治理 + 保留 API Key 檢查 + 「絕對禁止修改」警告 |
| v1.15.0 | 專案檔案夾重整 — sprints/ + docs/audit-reports/ + 檔名規則 |
| **v1.15.1** | **通知系統強化 — Task 級通知 + 錯誤即時通知 + 修復嘗試通知 + 4 種模板** |

---

*CLAUDE.md v1.15.1 | 2026-03-26 | 通知系統強化: Task 完成 notify、Task 失敗 notify、修復嘗試 notify、中斷 notify — 全部 [MANDATORY]*
