# Zigma PromptToBuild 專案管理

> **版本:** v1.7 | **最後更新:** 2026-03-30
> **專案:** Zigma PromptToBuild (PromptBIMTestApp1)
> **組織:** Reality Matrix Inc.
> **HEAD Tag:** mvp-v0.2.1

---

## 1. 版本控制

| 標籤 | Sprint | 日期 | 狀態 |
|------|--------|------|:----:|
| v2.10.0 | P23 | 2026-03 | ✅ |
| v2.11.0 | P24 | 2026-03-27 | ✅ |
| v2.12.0 | P25 | 2026-03-27 | ✅ |
| demo1-v0.1.0 | D1 | 2026-03-27 | ✅ Demo-1 Ready |
| mvp-v0.1.0 | M1-MVP | 2026-03-28 | ✅ Qt Quick 3D MVP |
| mvp-v0.2.0 | M1-SCENE | 2026-03-28 | ✅ DemoScene + Logger |
| mvp-v0.2.1 | M2-ENV | 2026-03-28 | ✅ 環境驗證 |
| **mvp-v0.3.0** | **M2-BRIDGE** | **2026-03-30** | **🔵 執行中** |
| mvp-v0.4.0 | M2-ENTITY | — | ⬜ |
| mvp-v0.5.0 | M2-MEP-DEMO | — | ⬜ |
| v3.0.0 | P30-USD-REVIT | — | ⬜ |

## 2. 治理文件

| 文件 | 版本 |
|------|------|
| CLAUDE.md | v1.23.3 |
| SKILL.md | v4.3 |
| PROJECT.md | **v1.7** |

## 3. 開發路線圖

| Sprint | Tasks | 版本 | 狀態 | 日期 |
|--------|:-----:|------|:----:|------|
| W0 | 5/5 | v2.11+v2.12 | ✅ | 03-27 |
| D1-S1 | 15/15 | demo1-alpha | ✅ | 03-27 |
| D1-S2 | 14/14 | demo1-v0.1.0 | ✅ | 03-27 |
| M1-MVP | 68/68 | mvp-v0.1.0 | ✅ | 03-28 |
| MEDIA-DL | 12/12 | media-v1.0 | ✅ | 03-27 |
| M1-SCENE | 22/22 | mvp-v0.2.0 | ✅ | 03-28 |
| M2-ENV | 8/8 | mvp-v0.2.1 | ✅ | 03-28 |
| **M2-BRIDGE** | **0/25** | **mvp-v0.3.0** | **🔵** | **03-30** |
| M2-ENTITY | 20T | mvp-v0.4.0 | ⬜ | — |
| M2-MEP-DEMO | 25T | mvp-v0.5.0 | ⬜ | — |
| P30-USD-REVIT | 25T | v3.0.0 | ⬜ | — |

**已完成: 110 Tasks | 執行中: M2-BRIDGE 25T | 待排: 70T**

## 4. M2-BRIDGE Sprint 內容 (執行中)

> TSMC Demo 核心:「把冰水主機移到右側柱子旁邊」

| Part | Tasks | 內容 | 狀態 |
|------|:-----:|------|:----:|
| PA | T1-T7 | BIMEntity C++ QObject + BIMSceneGraph + DemoScene 具名化 | 🔵 |
| PB | T8-T14 | AgentBridge JSON protocol (query/operate/cost) + IDTF 對接 | ⬜ |
| PC | T15-T20 | QML 即時更新 (PropertyPanel + CostPanel + ChatPanel) | ⬜ |
| PD | T21-T25 | ctest + PROJECT_STATUS 更新 + tag mvp-v0.3.0 | ⬜ |

## 5. 已知問題

| ID | 問題 | 狀態 |
|----|------|:----:|
| ENV-001 | agent_runner.py 在 repo root | 🟡 待整理 |
| ENV-002 | pybind11 not found | 🟡 低優先 |
| ENV-003 | Sketchfab 8 GLB 手動下載 | 🟡 待辦 |
| ISSUE-004 | PySide6 記憶體 | 🔴 P29 |
| OOM-001 | test_agents +4GB | 🟡 safe_pytest_dir |

## 6. TSMC Demo 技術鏈

| 能力 | Sprint | 狀態 |
|------|--------|:----:|
| 實體辨識 (BIMEntity) | M2-ENTITY | ⬜ |
| 空間查詢 (SceneQuery) | M2-BRIDGE | 🔵 |
| 即時移動 (SceneOperate) | M2-BRIDGE | 🔵 |
| 管線重路由 (pathfinder) | M2-MEP-DEMO | ⬜ |
| 碰撞檢測 (clash_detect) | M2-MEP-DEMO | ⬜ |
| 成本連動 (cost_delta) | M2-MEP-DEMO | ⬜ |
| USD→Revit→IFC | P30 | ⬜ |

## 7. 里程碑

```
2026 Q2: W0✅→D1✅→M1-MVP✅→M1-SCENE✅→M2-ENV✅→M2-BRIDGE🔵→M2-ENTITY→M2-MEP-DEMO→Demo-2★
2026 Q3: P26-P29 → v3.0.0
2026 Q4: P30-P33 Windows+ILOS
2027 Q1: P34-P41 Web+Mobile
```

## 8. 變更日誌

| 版本 | 變更 |
|------|------|
| v1.0-v1.4 | 初始 → ADR-001 + 路線圖 |
| v1.5 | Demo-1 完成 (34T). pytest 60/60. OOM診斷. |
| v1.6 | M1-MVP 完成 (68T). Qt Quick 3D + AgentBridge. mvp-v0.1.0. |
| **v1.7** | **M1-SCENE(22T)+M2-ENV(8T) 完成. 累計110T. M2-BRIDGE(25T) 執行中. Notion Job: 332f154a-6472-819c.** |

---

*PROJECT.md v1.7 | Zigma PromptToBuild | 2026-03-30*
