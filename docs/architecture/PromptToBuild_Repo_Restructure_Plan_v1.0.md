# PromptToBuild Repo 重構計劃 — Zigma 品牌化

> **版本:** v1.0 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **Sprint:** RS-S1 (Restructure Sprint 1)
> **時程:** 1 週（Demo-1 之前完成）

---

## 1. Zigma 產品品牌架構

```
Zigma (整體解決方案品牌)
│
├── Zigma Core          — 共用底層框架（Plugin Bus + 6 大介面 + USD Stage）
├── Zigma PromptToBuild — 設計→建造→交付（AI 建築/工廠規劃）
├── Zigma PromptToOperate — 交付→營運→維護→退役（即時監控/預測）
├── Zigma Cloud         — 雲端基礎設施（Session Manager + Auth + Deploy）
└── Zigma NDH           — IDTF Neutral Data Hub（資料匯流排）
```

---

## 2. 現況問題

| # | 問題 | 嚴重度 |
|---|------|:------:|
| 1 | Repo 名稱 "PromptBIMTestApp1" — 測試名稱 | 🔴 |
| 2 | SwiftUI 殘留 — .xcodeproj + PromptBIMTestApp1/ | 🔴 |
| 3 | 扁平混亂 — docs/sprints/scripts/reference/logs/output 散落 | 🟡 |
| 4 | 無多產品分離 — 全混在 src/promptbim/ | 🟡 |
| 5 | Python package "promptbim" — 需演進為 zigma | 🟡 |
| 6 | 舊版殘留 — PROJECT_STATUS.md、TODO.md、reference/ | 🟢 |
| 7 | Sprint 管理散落 — sprints/ vs audit-reports/ 不統一 | 🟢 |

---

## 3. 目標結構

```
zigma/                                 ← Repo 重命名
│
├── CLAUDE.md                          ← 治理：最高規則
├── SKILL.md                           ← 治理：技術 SSOT
├── PROJECT.md                         ← 治理：專案管理
├── README.md / LICENSE / SECURITY.md / CONTRIBUTING.md / CHANGELOG.md
├── CMakeLists.txt / CMakePresets.json / vcpkg.json / pyproject.toml
│
├── core/                              ← Zigma Core（共用框架）
│   ├── include/zigma/                 ← C++ Plugin 介面 headers
│   └── src/                           ← Core 引擎 C++
│
├── build/                             ← Zigma PromptToBuild
│   ├── src/zigma_build/               ← Python package（從 src/promptbim 遷移）
│   │   ├── agents/ bim/ codes/ land/ schemas/ cache/
│   └── plugins/                       ← Build 專屬 Plugin
│
├── operate/                           ← Zigma PromptToOperate（未來）
│   ├── src/zigma_operate/
│   └── plugins/
│
├── cloud/                             ← Zigma Cloud（Phase 4+）
│   ├── server/ web/ mobile/ session/ deploy/
│
├── shell/                             ← UI Shell Plugin
│   ├── qt6/ web/ headless/
│
├── render/                            ← Render Backend Plugin
│   ├── vtk/ hydra/ omniverse/ null/
│
├── demo/                              ← Demo 腳本
│   ├── demo1/ demo2/ fixtures/
│
├── docs/                              ← 文件
│   ├── architecture/ partner/ api/
│
├── governance/                        ← 治理
│   ├── audit-reports/ prompts/ sprints/
│
├── legacy/                            ← 舊版（deprecated）
│   ├── PromptBIMTestApp1/ .xcodeproj/ libpromptbim/ reference/
│
├── cpp/                               ← C++ 原生引擎
├── scripts/                           ← 工具腳本
└── .github/workflows/                 ← CI/CD
```

---

## 4. 重構 Sprint: RS-S1（30 Tasks, 1 週）

### RS-S1-PA: Repo 重命名 + 基礎結構（Day 1-2, 8T）

| Task ID | 說明 | 驗收 |
|---------|------|------|
| RS-S1-PA-T1 | GitHub Repo 重命名: PromptBIMTestApp1 → zigma | 新 URL 可存取 |
| RS-S1-PA-T2 | 建立頂層目錄: core/ build/ operate/ cloud/ shell/ render/ demo/ governance/ legacy/ | 目錄存在 |
| RS-S1-PA-T3 | 移動 SwiftUI 到 legacy/ | legacy/ 中可見 |
| RS-S1-PA-T4 | 移動 libpromptbim/ → legacy/ | legacy/ 中可見 |
| RS-S1-PA-T5 | 移動 sprints/ → governance/sprints/ | governance/ 中可見 |
| RS-S1-PA-T6 | 建立 governance/audit-reports/ + governance/prompts/ | 目錄存在 |
| RS-S1-PA-T7 | 移動 reference/ → legacy/reference/ | legacy/ 中可見 |
| RS-S1-PA-T8 | 建立 legacy/README_LEGACY.md | 說明為何保留 |

### RS-S1-PB: 原始碼遷移（Day 2-3, 8T）

| Task ID | 說明 | 驗收 |
|---------|------|------|
| RS-S1-PB-T1 | src/promptbim/agents/ → build/src/zigma_build/agents/ | import 正確 |
| RS-S1-PB-T2 | src/promptbim/bim/ → build/src/zigma_build/bim/ | import 正確 |
| RS-S1-PB-T3 | src/promptbim/codes/ → build/src/zigma_build/codes/ | import 正確 |
| RS-S1-PB-T4 | src/promptbim/land/ → build/src/zigma_build/land/ | import 正確 |
| RS-S1-PB-T5 | src/promptbim/schemas/ → build/src/zigma_build/schemas/ | import 正確 |
| RS-S1-PB-T6 | src/promptbim/cache/ → build/src/zigma_build/cache/ | import 正確 |
| RS-S1-PB-T7 | src/promptbim/gui/ → shell/qt6/ 或 legacy/ | 位置正確 |
| RS-S1-PB-T8 | src/promptbim/viz/ → render/vtk/ 或 legacy/ | 位置正確 |

### RS-S1-PC: 設定檔更新（Day 3-4, 8T）

| Task ID | 說明 | 驗收 |
|---------|------|------|
| RS-S1-PC-T1 | pyproject.toml: name="zigma-build", packages=["zigma_build"] | pip install -e . |
| RS-S1-PC-T2 | 全部 Python import: promptbim → zigma_build | grep 無殘留 |
| RS-S1-PC-T3 | CMakeLists.txt: project(zigma) | cmake 成功 |
| RS-S1-PC-T4 | .github/workflows/ CI 更新 | CI pass |
| RS-S1-PC-T5 | CLAUDE.md 更新: 反映新結構 | 內容正確 |
| RS-S1-PC-T6 | SKILL.md 更新: Zigma 品牌 | 內容正確 |
| RS-S1-PC-T7 | PROJECT.md 更新: Zigma + 新目錄 | 內容正確 |
| RS-S1-PC-T8 | README.md 更新: Zigma 品牌 | 內容正確 |

### RS-S1-PD: 測試 + 驗證（Day 4-5, 6T）

| Task ID | 說明 | 驗收 |
|---------|------|------|
| RS-S1-PD-T1 | pytest 全通過（新路徑） | pass |
| RS-S1-PD-T2 | CLI: python -m zigma_build --help | 可執行 |
| RS-S1-PD-T3 | C++ ctest 通過 | pass |
| RS-S1-PD-T4 | docs/ 文件連結正確 | 無斷連 |
| RS-S1-PD-T5 | git tag restructure-v1.0 | tag 存在 |
| RS-S1-PD-T6 | RS-S1 AuditReport + PROMPT_D1 | 文件推送 |

---

## 5. 分段執行建議

建議不要一次全做，分 3 個子階段：

### 階段 1: 目錄建立 + legacy 搬移（低風險）
- RS-S1-PA 全部（8T）
- 不影響任何現有程式碼功能

### 階段 2: 原始碼遷移 + import 更新（中風險）
- RS-S1-PB + RS-S1-PC（16T）
- 需要一次性完成（import 路徑改一半會全壞）

### 階段 3: 測試驗證 + 治理文件更新（低風險）
- RS-S1-PD（6T）
- 確認一切正常後才 tag

---

*PromptToBuild Repo 重構計劃 v1.0*
*Reality Matrix Inc. | 2026-03-27*
