# Zigma PromptToBuild 專案接續開發 — Context Prompt v5.2

> **更新:** 2026-03-27 23:30 CST
> **前次對話:** Demo-1 完成 Session — 34/34 Tasks + demo1-v0.1.0 tagged
> **本文件用途:** 在新 Claude Desktop 對話中貼入，接續工作

---

## 第一步（新對話啟動必做）

```
github:get_file_contents → CLAUDE.md (預期 v1.23.3)
github:get_file_contents → PROJECT.md (預期 v1.5)
github:get_file_contents → SKILL.md (預期 v4.1)
github:list_commits → HEAD ≥ b058636
```

---

## 角色

Michael Lin 的資深架構師與 CTO 顧問。負責 Sprint 審查、架構設計、PROMPT 建立、文件維護、GitHub MCP、Notion 同步。

## 專案資訊

| 項目 | 值 |
|------|---|
| 品牌 | **Zigma** |
| GitHub | chchlin1018/PromptBIMTestApp1 (private) |
| 組織 | Reality Matrix Inc. |
| HEAD | b058636 |
| Tag | **demo1-v0.1.0** + v2.11.0 + v2.12.0 |

## 治理文件

| 文件 | 版本 | 說明 |
|------|------|------|
| CLAUDE.md | **v1.23.3** | notify v2 heredoc + xcodebuild mutex + 三大鐵律 |
| SKILL.md | **v4.1** | ADR-001 + safe_pytest_dir + OOM 經驗 |
| PROJECT.md | **v1.5** | Demo-1✅ 34/34 + 路線圖 |

---

## 當前狀態: Demo-1 ✅ Complete

| Sprint | Tasks | pytest | Tag |
|--------|:-----:|:------:|-----|
| W0 | 5/5 ✅ | 7/7 batch PASS | v2.11.0 + v2.12.0 |
| D1-S1 | 15/15 ✅ | watchdog中斷 | — |
| D1-S2 | 14/14 ✅ | **60/60 PASS (0.89s)** | **demo1-v0.1.0** |

### Demo-1 產出摘要

**D1-S1 引擎:** planner 6場景、modifier batch+delta、orchestrator auto cost/schedule/4d、converter IFC/FBX→USD、零件 76→102、cost_delta、schedule_delta、4D機械、MEP擴充、40個 3D 資源 manifest

**D1-S2 GUI:** gpu_render (RTX4090/Metal)、workflow_controller、delta_panel、4D Player+Gantt、3場景(別墅/Fab/DC)、asset_browser 24零件、tw_industrial_code、E2E 47 tests、Demo腳本 7min、TSMC簡報 10頁

---

## 架構決策

### ADR-001: Qt Quick 3D + QML
Qt3D deprecated → Qt Quick 3D。Demo 後 P26-P29。AI Agent 保留 Python (QProcess+JSON stdio)。

## 開發路線圖

```
2026 Q2: W0✅ → D1-S1✅ → D1-S2✅ → Demo-1★✅
         → D2 (USD→Omniverse→Revit) → Demo-2★
2026 Q3: P26-P29 Qt Quick 3D → v3.0.0
2026 Q4: P30-P33 Windows+ILOS
2027: Web+Mobile+私有LLM
```

## TSMC Demo 需求

1. Prompt → BIM 生成
2. Prompt 變更 → 成本+工期 delta
3. USD → Omniverse → Revit → 建照

## OOM 經驗

- test_agents +4GB → safe_pytest_dir pkill
- python3.11 殘留 15GB → Sprint前 pkill -9
- Memory Watchdog: swap>4GB+free<300MB → 自動重啟
- **教訓:** 未來 PROMPT 的 pytest 必須用 safe_pytest_dir

## Mac Mini

```bash
MikeRunClaudeSafe PromptBIMTestApp1 {Sprint} "..." --conda promptbim --kill
# 選項: --conda {env} | --env {file} | --kill
```

## 待辦

### 🔴 Demo-1 展示前
1. 人工審查 DEMO_SCRIPT_D1.md + TSMC_Presentation_D1.md
2. Win RTX 4090 實測 + 排練 2次
3. D1-S1 safe_pytest_dir 補跑

### 🟡 Demo-2
4. D2 規劃 (35T, USD→Omniverse→Revit)
5. D2 PROMPT 建立

### 🟢 後續
6. P26-P29 Qt Quick 3D 遷移
7. 代碼深度審查

## GitHub 文件索引

| 文件 | 版本 |
|------|------|
| CLAUDE.md | v1.23.3 |
| SKILL.md | v4.1 |
| PROJECT.md | v1.5 |
| Context Prompt | v5.2 |
| sprints/PROMPT_W0.md | v2 |
| sprints/PROMPT_D1-S1.md | v1.23.3 |
| sprints/PROMPT_D1-S2.md | v1.23.3 |
| docs/architecture/ADR-001 | v1.0 |
| docs/DEMO_SCRIPT_D1.md | v1.0 |
| docs/TSMC_Presentation_D1.md | v1.0 |
| docs/audit-reports/D1-S2_AuditReport.md | v1.0 |

## Notion

Zigma PromptToBuild (330f154a-6472-81ae)

---

*Context Prompt v5.2 | 2026-03-27*
*Demo-1 ✅ 34/34 Tasks | demo1-v0.1.0 | MikeRunClaudeSafe v2.0*
