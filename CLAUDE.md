# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.2.0 | **更新:** 2026-03-25
> **版本控制:** 本文件由人工維護，Claude Code 不得直接修改
> ⚠️ 本文件中標記為 **[MANDATORY]** 的規則必須嚴格執行，不得跳過

---

## 開發前必讀順序

```
1. PROMPT.md    ← 執行指令 + 文件檢查清單（最重要！）
2. SKILL.md     ← 專案 SSOT（架構、Schema、Agent Prompt、開發規範）
3. TODO.md      ← 確認當前 Sprint 狀態
4. 對應 Addendum ← 依當前 Sprint 讀取技術規格
5. CLAUDE.md    ← 本文件（行為規範）
```

---

## 專案本質

這是一個 **概念驗證 (POC)** macOS 桌面應用，使用 **Xcode 專案** 包裝 Python 核心。

用戶只需要：
- 輸入土地資料（或隨意描述面積）
- 輸入 AI Prompt（如 "帶游泳池的3層別墅"）

系統自動完成所有後續工作（BIM 生成、MEP、法規、4D/5D、監控點、即時修改）。

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

### Xcode 建置架構

```
Xcode macOS App (Swift/SwiftUI)
  └── Build Phases:
       ├── 1. Compile Swift Sources
       ├── 2. Run Script: Python Environment Check
       │     conda activate promptbim && python -c "import promptbim"
       ├── 3. Run Script: pytest
       │     conda activate promptbim && python -m pytest tests/ -v --tb=short
       └── 4. Run Script: Python Lint
             conda activate promptbim && ruff check src/
```

### xcodebuild 命令

```bash
# 標準建置驗證命令
xcodebuild -project PromptBIMTestApp1.xcodeproj \
           -scheme PromptBIMTestApp1 \
           -destination 'platform=macOS' \
           build 2>&1 | tail -5

# 預期輸出最後一行:
# ** BUILD SUCCEEDED **
```

---

## [MANDATORY] 每次工作結束必須執行的步驟

> ⚠️ **以下步驟是強制性的，每次 Claude Code 工作結束前必須完整執行。**
> ⚠️ **不得省略任何步驟。不得以「下次再做」為由跳過。**

### Step 1: xcodebuild 驗證 ✅

```bash
# 必須執行且必須通過
xcodebuild -project PromptBIMTestApp1.xcodeproj \
           -scheme PromptBIMTestApp1 \
           -destination 'platform=macOS' \
           build 2>&1 | tail -20

# 如果 BUILD FAILED:
#   1. 修復所有錯誤
#   2. 重新 build 直到 BUILD SUCCEEDED
#   3. 不得在 build 失敗的狀態下結束工作
```

### Step 2: pytest 驗證 ✅

```bash
conda activate promptbim
python -m pytest tests/ -v --tb=short

# 如果有測試失敗:
#   1. 修復所有失敗的測試
#   2. 重新執行直到全部通過
#   3. 不得在測試失敗的狀態下結束工作
```

### Step 3: 更新所有專案文件 ✅

**必須更新以下文件（按順序）：**

| # | 文件 | 更新內容 | 範例 |
|---|------|---------|------|
| 1 | `TODO.md` | 將已完成的 task 標記為 ✅ | `- ✅ bim/geometry.py` |
| 2 | `CHANGELOG.md` | 如果完成了一個 Sprint，加入新版本條目 | `## [0.2.0] - 2026-03-26` |
| 3 | `SETUP.md` | 如果安裝步驟有變更，更新指南 | 新增依賴說明 |
| 4 | `README.md` | 如果功能有重大變更，在表格中更新狀態 | 功能標記 ✅ |

### Step 4: Git Commit + Push ✅

```bash
# 統一提交格式
git add -A
git status  # 確認變更內容
git commit -m "[P{X}] {Sprint描述} — session end: build OK, tests OK, docs updated"
git push origin main
```

### Step 5: 產生下一步驟的 Prompt ✅

在工作結束前，**必須在 terminal 輸出**下次繼續開發的 prompt：

```
====================================================
📋 下次繼續開發請貼上以下 prompt:
====================================================

請讀取 PROMPT.md，先執行 Step 1 檢查所有文件。
然後讀取 SKILL.md、TODO.md、{對應Addendum}，
繼續執行 Sprint P{X} 的剩餘 task:
- [ ] {未完成的 task 1}
- [ ] {未完成的 task 2}

目前進度: Sprint P{X} 完成 {N}/{M} 個 task
上次 xcodebuild: ✅ BUILD SUCCEEDED
上次 pytest: ✅ {N} passed

====================================================
```

---

## [MANDATORY] 嚴格檢查清單（工作結束前逐項確認）

```
□ xcodebuild BUILD SUCCEEDED
□ pytest 全部通過
□ TODO.md 已更新（完成的 task 標記 ✅）
□ CHANGELOG.md 已更新（如果完成 Sprint）
□ SETUP.md 已更新（如果安裝步驟變更）
□ git commit + push 完成
□ 下次繼續的 prompt 已輸出
```

**如果任何一項未完成，不得結束工作。**

---

## 文件版本控制矩陣

| 文件 | 誰更新 | 何時更新 | Claude Code 可改？ |
|------|--------|----------|:-----------------:|
| `SKILL.md` | 人工 | 架構變更 | ❌ 禁止 |
| `PROMPT.md` | 人工 | 流程變更 | ❌ 禁止 |
| `CLAUDE.md` | 人工 | 規範變更 | ❌ 禁止 |
| `docs/addendum/*.md` | 人工 | 規格變更 | ❌ 禁止 |
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
[P0] Add xcodebuild script phases
[P1] Add GeoJSON land parser
[P2] Implement IFC wall generation
[P4.8] Implement modification engine with delta computation
[P8.5] Add auto monitor placement for HVAC system
```

工作結束 commit 必須包含 session end 標記：
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

- **平台:** macOS (Apple Silicon)
- **Python:** 3.11+
- **Xcode:** 16.0+ (含 SwiftUI, macOS target)
- **Swift:** 6.0+
- **套件管理:** Conda (Miniforge) + pip
- **IDE:** Claude Code CLI + Xcode
- **Git:** main branch

---

*CLAUDE.md v1.2.0 | 2026-03-25 | 新增 Xcode 專案要求 + [MANDATORY] 工作結束步驟 + 下次 prompt 產生*
