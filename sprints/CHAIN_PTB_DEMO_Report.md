# CHAIN_PTB_DEMO Report — TSMC Demo Complete

> **Date:** 2026-03-30 | **Version:** mvp-v0.5.0-demo
> **Job:** JOB-PTB-CHAIN-DEMO
> **Chain:** M2-BRIDGE → M2-ENTITY → M2-MEP-DEMO
> **Total:** 70/70 Tasks | 14 Parts | 3 Phases | 100%

## Build & Test

| Check | Status |
|-------|--------|
| cmake configure | PASS |
| cmake build | PASS (65 targets) |
| ctest 5/5 | PASS (1.72s) |
| AgentBridgeTests | PASS |
| BIMComponentTests | PASS |
| BIMEntityTests | PASS |
| SceneGraphTests | PASS |
| EntityModelTests | PASS |

## Phase Summary

### Phase 1: M2-BRIDGE (25T) — mvp-v0.3.0-bridge ✅
- AgentBridge v2 protocol (query/move/rotate/resize/add/delete/cost/nearby)
- BIMEntity C++ QObject with full properties
- BIMSceneGraph with flat map + query/operate
- DemoScene.qml with 22 named TSMC fab entities
- PropertyPanel, CostPanel, ChatPanel QML updates
- 4/4 tests PASS

### Phase 2: M2-ENTITY (20T) — mvp-v0.4.0-entity ✅
- BIMEntityModel (QAbstractListModel) — QML list binding with type filter
- SceneGraphModel (QAbstractItemModel) — hierarchy tree view
- SpatialParser — NL direction → coordinate offset (ZH/EN)
- equipment_catalog.json — 7 types with costs
- Selection highlight (green bounding box)
- 5/5 tests PASS

### Phase 3: M2-MEP-DEMO (25T) — mvp-v0.5.0-demo ✅
- MEP pipe visualization — chilled water (blue), condenser (green), power (red)
- DemoController — move/add/delete + clash detect (AABB) + cost delta
- Auto-arrange — place new equipment next to same type
- Pipe cost calculation — distance × rate (NTD 3,500/m)
- DemoScript — 4-step TSMC scenario with auto-play
- NL parser — keyword matching for move/add/delete/cost queries

## TSMC Demo 4-Step Scenario

| Step | Command | Action | Result |
|------|---------|--------|--------|
| 1 | 規劃 CUB 區域 | Scene info | Display 22 entities + cost summary |
| 2 | 把冰水主機移到右側柱子旁 | Move + clash + cost | Chiller-A → Column-C3 right, pipe reroute |
| 3 | 冷卻水塔增加到 6 座 | Add × 2 | Auto-arrange, +NT$2.4M |
| 4 | 排氣管高度改成 45 米 | Resize | Height 35→45m |

## New C++ Classes (Phase 2+3)

| Class | File | Lines | Purpose |
|-------|------|-------|---------|
| BIMEntityModel | BIMEntityModel.h/.cpp | ~120 | QAbstractListModel for entity list |
| SceneGraphModel | SceneGraphModel.h/.cpp | ~150 | QAbstractItemModel for tree view |
| SpatialParser | SpatialParser.h/.cpp | ~70 | NL direction parsing |
| DemoController | DemoController.h/.cpp | ~240 | Move/add/delete orchestration |
| DemoScript | DemoScript.h/.cpp | ~220 | 4-step demo + NL execution |

## Architecture (Final)

```
┌─ Qt Quick 3D Frontend (C++) ─────────────────────────┐
│ main.cpp v0.5.0-demo                                  │
│                                                        │
│ Models:                                                │
│   BIMEntity → BIMEntityModel (list) → SceneGraphModel │
│   BIMSceneGraph → totalCost/pipeCost                  │
│                                                        │
│ Controllers:                                           │
│   DemoController → move/add/delete + clash + cost     │
│   DemoScript → 4-step TSMC scenario + NL parser       │
│   SpatialParser → direction → offset                  │
│   AgentBridge → Python IDTF backend                   │
│                                                        │
│ QML:                                                   │
│   DemoScene (22 entities + MEP pipes)                 │
│   BIMView3D (selection highlight)                     │
│   ChatPanel / CostPanel / PropertyPanel               │
│                                                        │
│ Data:                                                  │
│   equipment_catalog.json (7 types)                    │
└───────────────────────────────────────────────────────┘
         ↕ JSON stdio (AgentBridge)
┌─ Python AI Backend (IDTF v3.5) ──────────────────────┐
│ agents/ bim/mep/ bim/cost/ bim/io_usd/ schemas/      │
│ (90% complete — orchestrator/modifier/pathfinder/     │
│  clash_detect/cost_delta/unit_prices_tw)              │
└───────────────────────────────────────────────────────┘
```

## Known Issues

| ID | Issue | Severity | Next Sprint |
|----|-------|----------|-------------|
| ISS-D01 | SceneGraphModel tree is 2-level only | Low | P30 |
| ISS-D02 | DemoScript NL parser is keyword-based (not LLM) | Expected | P42+ |
| ISS-D03 | Move animation not smooth (instant teleport) | Medium | D1-S2 |
| ISS-D04 | Pipe visualization is static (no dynamic reroute) | Medium | D1-S2 |

## Git History

| Commit | Description |
|--------|-------------|
| fe9e4b2 | [M2-ENTITY] Part 1+2: BIMEntityModel + SceneGraphModel |
| 3ce2f11 | [M2-ENTITY] Part 3: SpatialParser |
| 2fd8ec1 | [M2-ENTITY] Part 4: Finalize — 5/5 tests |
| b78752c | [M2-MEP-DEMO] Part 1: MEP pipes |
| cb3c1f2 | [M2-MEP-DEMO] Part 2: DemoController |
| f6efb39 | [M2-MEP-DEMO] Part 3: Add/delete auto-arrange |
| f1312e3 | [M2-MEP-DEMO] Part 4: DemoScript |

---
*CHAIN_PTB_DEMO Report | 2026-03-30 | Reality Matrix Inc.*
*TSMC Demo: 「請將那台冰水主機移動到右側柱子旁邊」— 完整實現*
