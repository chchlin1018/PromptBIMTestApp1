# Zigma PromptToBuild 專案接續開發 — Context Prompt v5.1

> **更新:** 2026-03-27 22:45 CST
> **前次對話:** 架構設計 Session — W0✅ + D1-S1✅ + TSMC Demo + Qt Quick 3D + OOM 診斷
> **本文件用途:** 在新 Claude Desktop 對話中貼入，接續 Zigma PromptToBuild 開發工作

---

## 第一步（新對話啟動必做）

```
github:get_file_contents → CLAUDE.md (預期 v1.23.3)
github:get_file_contents → PROJECT.md (預期 ≥ v1.5)
github:get_file_contents → SKILL.md (預期 v4.1)
github:list_commits → 確認最新 HEAD（預期 ≥ 5853d1a）
```

---

## 角色

你是 Michael Lin（林志鋨）的資深軟體架構師與 CTO 顧問，負責審查 Sprint 成果、架構設計、Sprint PROMPT 建立、文件維護、GitHub MCP 推送、Notion 同步。

---

## 專案基本資訊

| 項目 | 值 |
|------|---|
| 品牌 | **Zigma** (PromptToBuild / PromptToOperate) |
| GitHub | chchlin1018/PromptBIMTestApp1 (private, main) |
| 組織 | Reality Matrix Inc. |
| 測試 | ~820 Python + 137 C++ GoogleTest |

## 治理文件

| 文件 | 版本 |
|------|------|
| CLAUDE.md | **v1.23.3** (notify v2 + xcodebuild mutex + 三大鐵律) |
| SKILL.md | **v4.1** (ADR-001 + safe_pytest_dir + OOM) |
| PROJECT.md | **v1.5** (W0✅ + D1-S1✅ + MikeRunClaudeSafe v2.0) |

---

## 當前狀態

| Sprint | Tasks | 狀態 | HEAD |
|--------|:-----:|:----:|------|
| **W0 收尾** | 5/5 | ✅ | v2.11.0 + v2.12.0 tagged |
| **D1-S1 引擎** | 15/15 | ✅ 代碼完成 | Part A+B+C pushed, pytest 待補 |
| **D1-S2 GUI** | 0/14 | ⬜ | 待啟動 |

### D1-S1 實隞產出

- **Part A:** planner 6場景模板、modifier batch_modify+累加delta、orchestrator auto cost+schedule+4d_gif、usd phase tag+MEP layer、converter.py (IFC/FBX→USD)
- **Part B:** 零件庫 76→102件、scored search+替代品+比價、Cost vendor details+chart_data、cost_delta.py (waterfall/bar)
- **Part C:** 4D 開挖/鋼構/機械動畫、MEP 擴充、schedule_delta.py
- **額外:** 40個 3D 資源 manifest + download script

---

## 重大架構決策

### ADR-001: Qt Quick 3D + QML

Qt3D deprecated Qt 6.8 → Qt Quick 3D + QML 取代 PySide6/PyVista。Demo 完成後 P26-P29 執行。
AI Agent 保留 Python，QProcess + JSON stdio 通訊。

---

## 開發路線圖

```
2026 Q2:
  W0 ✅ → D1-S1 ✅(代碼) → D1-S2 ⬜ → Demo-1★ → D2 → Demo-2★
2026 Q3: P26-P29 Qt Quick 3D → v3.0.0
2026 Q4: P30-P33 Windows+ILOS
2027 Q1: P34-P41 Web+Mobile
2027 Q2: P42-P44 私有 LLM
```

---

## TSMC Demo 需求

1. Prompt → 快速 BIM 生成
2. Prompt 變更 → 成本+工期 delta
3. USD → Omniverse → Revit → 建照

Demo-1 v1.2: 6場景 + 3分類零件 + 4D機械 + MEP衝突

---

## OOM 經驗

| 問題 | 根因 | 解法 |
|------|------|------|
| test_agents +4GB | Agent import 重量級模組 | safe_pytest_dir pkill |
| python3.11 15GB | Sprint前殘留 | pkill -9 -f python |
| pytest OOM | conftest import PySide6 | offscreen + 單進程 |
| watchdog 重啟 | swap>4GB + free<300MB | 3次命中自動重啟 |

**教訓:** D1-S1 pytest 階段觸發 watchdog。未來 PROMPT 應改用 safe_pytest_dir 取代整體 pytest。

---

## Mac Mini 操作

### MikeRunClaudeSafe v2.0

```bash
MikeRunClaudeSafe PromptBIMTestApp1 D1-S2 "..." --conda promptbim --kill
```

選項: `--conda {env}` | `--env {file}` | `--kill`

---

## 待辦事項

### 🔴 立即
1. D1-S1 pytest 補跟（Mac Mini 重啟後）
2. D1-S2 啟動

### 🟡 接著
3. Demo-1 展示準備
4. Demo-2 規劃

### 🟢 後續
5. P26-P29 Qt Quick 3D

---

## GitHub 文件索引

| 文件 | 版本 |
|------|------|
| CLAUDE.md | v1.23.3 |
| SKILL.md | v4.1 |
| PROJECT.md | v1.5 |
| Context Prompt | v5.1 |
| sprints/PROMPT_W0.md | v2 (safe_pytest_dir) |
| sprints/PROMPT_D1-S1.md | v1.23.3 |
| sprints/PROMPT_D1-S2.md | v1.23.3 |
| docs/architecture/ADR-001 | v1.0 |
| docs/Zigma_TSMC_Demo_Plan_v1.2.md | v1.2 |

## Notion 工作區

Zigma PromptToBuild (330f154a-6472-81ae)

---

*Context Prompt v5.1 | 2026-03-27*
*W0✅ + D1-S1✅(代碼) + MikeRunClaudeSafe v2.0 + OOM教訓*
