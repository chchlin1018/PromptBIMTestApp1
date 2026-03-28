# PROJECT_STATUS v2.0

> Last updated: 2026-03-28 | HEAD: 1b5307f

## Current State

**Version:** mvp-v0.2.1 (M2-ENV complete)
**Build:** ✅ OK (cmake + ninja) | ctest 2/2 PASS
**Repo:** ~/Dev/PromptBIMTestApp1 (migrated from ~/Documents/MyProjects/)

## Sprint History

| # | Sprint | Tasks | Tag | Date | Status |
|:-:|--------|:-----:|:---:|:----:|:------:|
| 1 | M1-MVP | 68T | mvp-v0.1.0 | 2026-03-26 | ✅ |
| 2 | MEDIA-DL | 12T | — | 2026-03-27 | ✅ |
| 3 | M1-SCENE | 22T | mvp-v0.2.0 | 2026-03-28 | ✅ |
| 4 | M2-ENV | 8T | mvp-v0.2.1 | 2026-03-28 | ✅ |

**Total completed: 110 Tasks across 4 Sprints**

## Planned Sprints (PROMPTs on GitHub)

| # | Sprint | Tasks | Tag | Goal | PROMPT |
|:-:|--------|:-----:|:---:|------|:------:|
| 5 | M2-BRIDGE | 25T | mvp-v0.3.0 | AgentBridge bidirectional + BIMEntity + SceneGraph | ✅ |
| 6 | M2-ENTITY | 20T | mvp-v0.4.0 | Named DemoScene + CUB equipment catalog | ✅ |
| 7 | M2-MEP-DEMO | 25T | mvp-v0.5.0 | Full chiller Demo + MEP pipes + cost | ✅ |
| 8 | P30-USD-REVIT | 25T | v3.0.0 | USD→Revit→IFC pipeline | ✅ |

## Key Deliverables (M1-SCENE)

- `zigma/src/ZigmaLogger.h/.cpp` — C++ singleton debug logging (5-level, file+stderr, rotation)
- `zigma/qml/DemoScene.qml` — TSMC fab 3D scene (11 building elements)
- `zigma/qml/BIMView3D.qml` — Camera + 3-Light + OrbitController
- `debuglog/` — Runtime log directory with .gitkeep

## Architecture Overview

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
- 每個 3D 物件 = BIMEntity (id/type/name/position/cost)
- AI 可查詢 + 操作場景 (scene.query / scene.move)
- 管線自動重路由 + 碰撞檢測
- 成本差異即時回報 (NT$)
- USD → Omniverse / Revit / IFC 三條管線

## Known Issues

| ID | Issue | Severity | Fix Sprint |
|----|-------|:--------:|:----------:|
| BUILD-005 | Repo migrated to ~/Dev/ (resolved) | ✅ Fixed | — |
| BUILD-006 | MikeRunClaudeSafe path still ~/Documents/ | Medium | Manual fix |
| BUILD-007 | Sprint PROMPT too long for shell -p | ✅ Fixed | Use file |
| BUILD-008 | DemoScene objects are anonymous Primitives | High | M2-ENTITY |

## File Statistics

- C++ source: 8 files (zigma/src/)
- QML files: 7 files (zigma/qml/)
- Python backend: ~40 files (src/promptbim/)
- Sprint PROMPTs: 5 files (sprints/)
- Docs: 25+ files (docs/)
- Tests: 2 ctest (C++) + pytest (Python)
