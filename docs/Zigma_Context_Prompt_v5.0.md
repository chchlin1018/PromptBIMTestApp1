# Zigma PromptToBuild 專案接續開發 — Context Prompt v5.7

> **更新:** 2026-03-29 01:00 CST
> **前次對話:** M1-SCENE(22T)+M2-ENV(8T) 完成 + IDTF v3.5 分析 + TSMC Demo 場景定義 + 4 Sprint PROMPT 推送
> **本文件用途:** 在新 Claude 對話中貼入，接續工作

---

## 第一步（新對話啟動必做）

```
github:get_file_contents → SKILL.md (預期 v4.3)
github:get_file_contents → PROJECT.md
github:list_commits → HEAD ≥ e02bb94
```

---

## 角色

Michael Lin 的資深架構師與 CTO 顧問。負責 Sprint 審查、架構設計、PROMPT 建立、文件維護、GitHub MCP、Notion 同步。

## 專案資訊

| 項目 | 值 |
|------|---|
| 品牌 | **Zigma** (Reality Matrix Inc.) |
| GitHub | chchlin1018/PromptBIMTestApp1 (private) |
| Repo | **~/Dev/PromptBIMTestApp1** (Mac Mini + MacBook) |
| HEAD | **e02bb94** |
| Tags | **mvp-v0.2.1** (latest) + mvp-v0.2.0 + mvp-v0.1.0 |
| Notion | 330f154a-6472-81ae (workspace) / 320f154a-6472-804f (parent) |

## 治理文件

| 文件 | 版本 |
|------|------|
| CLAUDE.md | v1.23.3 |
| SKILL.md | **v4.3** |
| PROJECT.md | v1.8 |

---

## 當前狀態

### ✅ 已完成 (110T 累計)

| Sprint | Tasks | 產出 | Tag |
|--------|:-----:|------|-----|
| M1-MVP | 68T ✅ | Qt Quick 3D + AgentBridge + 13 QML panels | mvp-v0.1.0 |
| MEDIA-DL | 12T ✅ | 37 files (81MB) → iCloud ~/ZigmaMedia/ | media-v1.0 |
| **M1-SCENE** | **22T** ✅ | ZigmaLogger + DemoScene TSMC fab + BIMView3D rewrite | **mvp-v0.2.0** |
| **M2-ENV** | **8T** ✅ | Environment verification + AuditReport | **mvp-v0.2.1** |

### 🔵 待執行 Sprint (PROMPT 已在 sprints/)

| Sprint | Tasks | Tag | 核心 |
|--------|:-----:|-----|------|
| **M2-BRIDGE** | 25T | mvp-v0.3.0 | AgentBridge 雙向 + BIMEntity C++ + SceneGraph |
| **M2-ENTITY** | 20T | mvp-v0.4.0 | 具名場景圖 + CUB 設備資料庫 + PropertyPanel |
| **M2-MEP-DEMO** | 25T | mvp-v0.5.0 | 冰水主機 Demo + MEP 管線 + 成本連動 |
| **P30-USD-REVIT** | 25T | v3.0.0 | USD→Revit + IFC + Omniverse |

### TSMC Demo 核心場景

```
用戶: 「請將那台冰水主機移動到右側柱子旁邊」
AI: (chiller-A 移動到 column-C3 旁邊, 管線自動重連)
AI: 「已移動冰水主機-A。管路增加 12m，成本增加 NT$180,000。」
```

需要: BIMEntity 具名 + Scene Query/Operate + 碰撞檢測 + 管線重路由 + 成本連動

### IDTF v3.5 — Python 後端 90% 已完成

- `agents/modifier.py` (25KB) + `orchestrator.py` (19KB) — AI 多 Agent
- `bim/mep/pathfinder.py` + `clash_detect.py` — 管線+碰撞
- `bim/cost/cost_delta.py` + `unit_prices_tw.py` — 成本 (NT$)
- `bim/io_usd/exporter.py` + `omniverse.py` — USD+Omniverse

---

## ★★★ 關鍵 Build 經驗 ★★★

- CMake: C++ 絕對路徑 + QML 相對路徑 + ShaderTools
- QML: onPropertyChanged 放 root, 不放 Canvas
- main.cpp: `qrc:/Zigma/qml/main.qml`
- .env: 不放空 ANTHROPIC_API_KEY
- Sprint: PROMPT 推 sprints/ → tmux + 短 Claude Code 指令讀檔 (英文)
- MikeRunClaudeSafe line 36 路徑需修正

---

## Sprint 執行指令 (Mac Mini)

```bash
cd ~/Dev/PromptBIMTestApp1 && git pull origin main
tmux new-session -d -s {NAME}
tmux send-keys -t {NAME} 'cd ~/Dev/PromptBIMTestApp1 && conda activate promptbim && claude --dangerously-skip-permissions -p "Sprint {NAME}. Read CLAUDE.md and SKILL.md first, follow ALL rules strictly including notify functions. Then read sprints/PROMPT_{NAME}.md and execute all Tasks. Send iMessage notifications for every task. Tag {TAG} when done."' Enter
```

## Notion 頁面

| 頁面 | ID |
|------|-----|
| Zigma Parent | 320f154a-6472-804f |
| 狀態總覽 | 331f154a-6472-81f5 |
| TSMC Demo 場景 | 331f154a-6472-8164 |
| IDTF 分析報告 | 331f154a-6472-8155 |
| M1-SCENE 報告 | 331f154a-6472-812b |

---

*Context Prompt v5.7 | 2026-03-29*
*110T done | TSMC Demo roadmap: M2-BRIDGE→ENTITY→MEP-DEMO→P30*
