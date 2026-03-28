# PROJECT_STATUS v2.1

> Last updated: 2026-03-29 | HEAD: ba2fae2

## Current State

**Version:** mvp-v0.2.1 (M2-ENV complete)
**Build:** ✅ OK (cmake + ninja) | ctest 2/2 PASS
**Repo:** ~/Dev/PromptBIMTestApp1 (Mac Mini + MacBook)
**Next Sprint:** M2-BRIDGE (25T → mvp-v0.3.0)

## Sprint History

| # | Sprint | Tasks | Tag | Date | Status |
|:-:|--------|:-----:|:---:|:----:|:------:|
| 1 | M1-MVP | 68T | mvp-v0.1.0 | 2026-03-26 | ✅ |
| 2 | MEDIA-DL | 12T | — | 2026-03-27 | ✅ |
| 3 | M1-SCENE | 22T | mvp-v0.2.0 | 2026-03-28 | ✅ |
| 4 | M2-ENV | 8T | mvp-v0.2.1 | 2026-03-28 | ✅ |

**Total completed: 110 Tasks across 4 Sprints**

## Planned Sprints (PROMPTs on GitHub)

| # | Sprint | Tasks | Tag | Goal |
|:-:|--------|:-----:|:---:|------|
| 5 | M2-BRIDGE | 25T | mvp-v0.3.0 | AgentBridge bidirectional + BIMEntity + SceneGraph |
| 6 | M2-ENTITY | 20T | mvp-v0.4.0 | Named DemoScene + CUB equipment catalog |
| 7 | M2-MEP-DEMO | 25T | mvp-v0.5.0 | Full chiller Demo + MEP pipes + cost linkage |
| 8 | P30-USD-REVIT | 25T | v3.0.0 | USD→Revit→IFC+Omniverse pipeline |

## Architecture

```
┌─ Qt Quick 3D Frontend (C++) ─────────────────┐
│ main.cpp → BIMView3D.qml → DemoScene.qml     │
│ AgentBridge.cpp ←→ Python (QProcess + JSON)   │
│ ZigmaLogger.cpp (file + stderr, 5-level)      │
│ BIMSceneBuilder / MaterialLib / GeometryProv   │
│ ChatPanel / CostPanel / SchedulePanel / Prop   │
└───────────────────────────────────────────────┘
         ↕ JSON stdio (AgentBridge)
┌─ Python AI Backend (IDTF v3.5) ──────────────┐
│ agent_runner.py → orchestrator → modifier     │
│ bim/mep/ (pathfinder, clash_detect, systems)  │
│ bim/cost/ (estimator, cost_delta, qto, tw$)   │
│ bim/io_usd/ (exporter, importer)              │
│ bim/omniverse.py, ifc_generator.py            │
└───────────────────────────────────────────────┘
```

## TSMC Demo Target

**核心場景:** 「請將那台冰水主機移動到右側柱子旁邊」
- BIMEntity (id/type/name/position/cost) — M2-ENTITY
- Scene Query/Operate API — M2-BRIDGE
- MEP 管線重路由 + 碰撞檢測 — M2-MEP-DEMO
- 成本即時回報 (NT$) — M2-MEP-DEMO
- USD→Omniverse/Revit/IFC — P30

**IDTF v3.5:** Python 後端 90% 已完成 (agents 100KB + mep 54KB + cost 38KB + io_usd 31KB)

## Known Issues

| ID | Issue | Status |
|----|-------|:------:|
| BUILD-005 | Repo migrated to ~/Dev/ | ✅ Fixed |
| BUILD-006 | MikeRunClaudeSafe path ~/Documents/ | ⚠️ Pending |
| BUILD-007 | Sprint PROMPT too long for shell | ✅ Fixed (file) |
| BUILD-008 | DemoScene anonymous Primitives | 🔵 M2-ENTITY |

## Governance Documents

| File | Version |
|------|---------|
| CLAUDE.md | v1.23.3 |
| SKILL.md | v4.3 |
| PROJECT_STATUS.md | v2.1 (this) |
| Context Prompt | v5.7 |
