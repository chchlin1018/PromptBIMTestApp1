# PromptToBuild Repo 重構計劃 — Zigma 品牌化

> **版本:** v1.0 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **Sprint ID:** RS-S1 (Restructure Sprint 1)
> **時程:** 1 週（Demo-1 之前完成）

---

## 1. Zigma 產品品牌架構

```
Zigma (整體解決方案品牌)
├── Zigma Core          — 共用底層框架（Plugin Bus + 6 介面 + USD Stage）
├── Zigma PromptToBuild — 設計→建造→交付
├── Zigma PromptToOperate — 交付→營運→維護→退役
├── Zigma Cloud         — 雲端基礎設施（Session + Auth + Deploy）
└── Zigma NDH           — IDTF Neutral Data Hub
```

## 2. 現況問題

| # | 問題 | 嚴重度 |
|---|------|:------:|
| 1 | Repo 名稱 "PromptBIMTestApp1" — 測試名稱 | 🔴 |
| 2 | SwiftUI 殘留 — .xcodeproj + PromptBIMTestApp1/ | 🔴 |
| 3 | 扁平混亂 — docs/sprints/scripts/reference/logs 散落根目錄 | 🟡 |
| 4 | 無多產品分離 — 全混在 src/promptbim/ | 🟡 |
| 5 | Python package "promptbim" — 需品牌化 | 🟡 |
| 6 | 舊版殘留 — PROJECT_STATUS.md, TODO.md, reference/ | 🟢 |

## 3. 目標結構

```
zigma/
├── CLAUDE.md / SKILL.md / PROJECT.md
├── CMakeLists.txt / pyproject.toml / vcpkg.json
│
├── core/              ← Zigma Core (C++ Plugin 介面)
├── build/             ← Zigma PromptToBuild (Python + Plugins)
├── operate/           ← Zigma PromptToOperate (未來)
├── cloud/             ← Zigma Cloud (未來)
├── shell/             ← UI Shell Plugin (qt6/web/headless)
├── render/            ← Render Backend Plugin (vtk/hydra/omni)
├── demo/              ← Demo 腳本 (demo1/demo2)
├── docs/architecture/ ← 架構文件
├── governance/        ← audit-reports + prompts + sprints
├── legacy/            ← 舊版 (SwiftUI/xcodeproj/libpromptbim)
├── cpp/               ← C++ 原生引擎
├── scripts/           ← 工具腳本
└── .github/workflows/ ← CI/CD
```

## 4. RS-S1 Sprint 計劃 (30 Tasks, 1 週)

### RS-S1-PA: Repo 重命名 + 基礎結構 (Day 1-2, 8T)

| Task ID | 說明 | 驗收 |
|---------|------|------|
| RS-S1-PA-T1 | GitHub Repo rename → zigma | URL 可存取 |
| RS-S1-PA-T2 | 建立目錄: core/ build/ operate/ cloud/ shell/ render/ demo/ governance/ legacy/ | 存在 |
| RS-S1-PA-T3 | 移動 SwiftUI → legacy/ | legacy/ 可見 |
| RS-S1-PA-T4 | 移動 libpromptbim/ → legacy/ | legacy/ 可見 |
| RS-S1-PA-T5 | 移動 sprints/ → governance/sprints/ | governance/ 可見 |
| RS-S1-PA-T6 | 建立 governance/audit-reports/ + governance/prompts/ | 存在 |
| RS-S1-PA-T7 | 移動 reference/ → legacy/reference/ | legacy/ 可見 |
| RS-S1-PA-T8 | 建立 legacy/README_LEGACY.md | 說明完成 |

### RS-S1-PB: 原始碼遷移 (Day 2-3, 8T)

| Task ID | 說明 | 驗收 |
|---------|------|------|
| RS-S1-PB-T1 | agents/ → build/src/zigma_build/agents/ | import OK |
| RS-S1-PB-T2 | bim/ → build/src/zigma_build/bim/ | import OK |
| RS-S1-PB-T3 | codes/ → build/src/zigma_build/codes/ | import OK |
| RS-S1-PB-T4 | land/ → build/src/zigma_build/land/ | import OK |
| RS-S1-PB-T5 | schemas/ → build/src/zigma_build/schemas/ | import OK |
| RS-S1-PB-T6 | cache/ → build/src/zigma_build/cache/ | import OK |
| RS-S1-PB-T7 | gui/ → shell/qt6/ 或 legacy/ | 位置正確 |
| RS-S1-PB-T8 | viz/ → render/vtk/ 或 legacy/ | 位置正確 |

### RS-S1-PC: 設定檔更新 (Day 3-4, 8T)

| Task ID | 說明 | 驗收 |
|---------|------|------|
| RS-S1-PC-T1 | pyproject.toml: name = "zigma-build" | pip install OK |
| RS-S1-PC-T2 | 更新所有 import: promptbim → zigma_build | grep 無殘留 |
| RS-S1-PC-T3 | CMakeLists.txt: project(zigma) | cmake OK |
| RS-S1-PC-T4 | .github/workflows/ CI 新路徑 | CI pass |
| RS-S1-PC-T5 | 更新 CLAUDE.md | 反映新結構 |
| RS-S1-PC-T6 | 更新 SKILL.md | 反映 Zigma |
| RS-S1-PC-T7 | 更新 PROJECT.md | 反映新結構 |
| RS-S1-PC-T8 | 更新 README.md: Zigma 品牌 | 內容正確 |

### RS-S1-PD: 測試 + 驗證 (Day 4-5, 6T)

| Task ID | 說明 | 驗收 |
|---------|------|------|
| RS-S1-PD-T1 | pytest pass（新路徑） | pass |
| RS-S1-PD-T2 | CLI: python -m zigma_build --help | 可執行 |
| RS-S1-PD-T3 | C++ ctest pass | pass |
| RS-S1-PD-T4 | docs/ 連結正確 | 無斷連 |
| RS-S1-PD-T5 | git tag restructure-v1.0 | tag 存在 |
| RS-S1-PD-T6 | RS-S1 AuditReport + PROMPT_D1 | 推送 |

## 5. 執行建議：分段執行

建議分 4 天逐步推進，每天一個 Part，確認無問題後再進下一步：

```
Day 1: RS-S1-PA (目錄結構 + 搬移舊檔) → 確認 git 正常
Day 2: RS-S1-PB (原始碼遷移) → 確認 import 正常  
Day 3: RS-S1-PC (設定檔更新) → 確認 build 正常
Day 4: RS-S1-PD (測試驗證) → 確認全部 pass → tag
```

---

*PromptToBuild Repo 重構計劃 v1.0 | RS-S1 Sprint | Reality Matrix Inc.*
