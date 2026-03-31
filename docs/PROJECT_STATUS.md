# PROJECT_STATUS v2.8

> Last updated: 2026-04-01 | HEAD: (S-PTB-AI-LAYER)

## Current State

**Version:** mvp-v0.9.0-ai (S-PTB-AI-LAYER complete)
**Build:** ✅ cmake clean build | ctest 69/69 PASS | pytest N/A (ISS-042)
**Repo:** ~/Dev/PromptBIMTestApp1 (Mac Mini) + C:\Dev\ (ProArt13 Win11)
**Audit:** A (96/100) — PTB-FAR-AI-001
**Next Sprint:** S-PTB-INTEGRATION v0.10.0

## Sprint History

| # | Sprint | Tasks | Tag | Date | Status |
|:-:|--------|:-----:|:---:|:----:|:------:|
| 1 | M1-MVP | 68T | mvp-v0.1.0 | 2026-03-26 | ✅ |
| 2 | MEDIA-DL | 12T | — | 2026-03-27 | ✅ |
| 3 | M1-SCENE | 22T | mvp-v0.2.0 | 2026-03-28 | ✅ |
| 4 | M2-ENV | 8T | mvp-v0.2.1 | 2026-03-28 | ✅ |
| 5 | M2-BRIDGE | 25T | mvp-v0.3.0 | 2026-03-29 | ✅ |
| 6 | M2-ENTITY | 20T | mvp-v0.4.0-entity | 2026-03-30 | ✅ |
| 7 | M2-MEP-DEMO | 25T | mvp-v0.5.0-demo | 2026-03-30 | ✅ |
| 8 | S-PTBWIN-2 | 25T | mvp-v0.5.1-win | 2026-03-31 | ✅ |
| 9 | S-PTB-RESTRUCTURE | 25T | mvp-v0.7.0-restructure | 2026-03-31 | ✅ |
| 10 | S-PTB-CODE-AUDIT | 20T | mvp-v0.7.1-codeaudit | 2026-03-31 | ✅ |
| 11 | S-PTB-GUI-CONNECT | 20T | mvp-v0.8.0-gui | 2026-03-31 | ✅ |
| 12 | S-PTB-AI-LAYER | 15T | mvp-v0.9.0-ai | 2026-04-01 | ✅ |

**Total completed: 285 Tasks across 12 Sprints**

### Sprint M2-BRIDGE 執行結果 — 2026-03-29

- **狀態:** ✅ 完成
- **版本:** mvp-v0.3.0
- **Tasks:** 25/25
- **ctest:** 4/4 PASS (AgentBridge, BIMComponents, BIMEntity, SceneGraph)
- **新增檔案:**
  - `zigma/src/BIMEntity.h/.cpp` — C++ QObject 資料模型
  - `zigma/src/BIMSceneGraph.h/.cpp` — 場景圖管理器
  - `zigma/tests/test_bim_entity.cpp` — BIMEntity 單元測試
  - `zigma/tests/test_scene_graph.cpp` — SceneGraph 單元測試
- **修改檔案:**
  - `AgentBridge.h/.cpp` — 13 個新 Q_INVOKABLE (query/operate/cost)
  - `DemoScene.qml` — 22 具名 entity (Chiller/Column/CoolingTower/ExhaustStack)
  - `BIMView3D.qml` — Entity picking via SceneGraph
  - `PropertyPanel.qml` — 完整 BIMEntity 屬性面板
  - `CostPanel.qml` — Cost delta 指示器
  - `ChatPanel.qml` — 操作結果 + undo/redo stack
  - `agent_runner.py` — scene_action handler + IDTF 整合
  - `main.cpp` — SceneGraph context + AgentBridge 連接

## Planned Sprints (PROMPTs on GitHub)

| # | Sprint | Tasks | Tag | Goal |
|:-:|--------|:-----:|:---:|------|
| 8 | P30-USD-REVIT | 25T | v3.0.0 | USD→Revit→IFC+Omniverse pipeline |

### CHAIN-DEMO (M2-ENTITY + M2-MEP-DEMO) — 2026-03-30

- **狀態:** ✅ 完成
- **版本:** mvp-v0.5.0-demo
- **Tasks:** 45/45 (Phase 2: 20T + Phase 3: 25T)
- **ctest:** 5/5 PASS
- **新增 C++ 類:** BIMEntityModel, SceneGraphModel, SpatialParser, DemoController, DemoScript
- **新增 Data:** equipment_catalog.json (7 types)
- **新增 QML:** MEP pipes, selection highlight
- **TSMC Demo:** 4-step scenario (info → move → add → resize)

## Architecture

```
┌─ Qt Quick 3D Frontend (C++) ─────────────────┐
│ main.cpp → BIMView3D.qml → DemoScene.qml     │
│ BIMEntity.cpp + BIMSceneGraph.cpp (M2-BRIDGE) │
│ AgentBridge.cpp ←→ Python (QProcess + JSON)   │
│   ├─ Scene Query: query/get_position/nearby   │
│   ├─ Scene Operate: move/rotate/resize/add/del│
│   └─ Cost/Schedule: cost_delta/schedule_impact│
│ ZigmaLogger.cpp (file + stderr, 5-level)      │
│ BIMSceneBuilder / MaterialLib / GeometryProv   │
│ ChatPanel / CostPanel / SchedulePanel / Prop   │
└───────────────────────────────────────────────┘
         ↕ JSON stdio (AgentBridge)
┌─ Python AI Backend (IDTF v3.5) ──────────────┐
│ agent_runner.py → orchestrator → modifier     │
│   └─ handle_scene_action (M2-BRIDGE)          │
│ bim/mep/ (pathfinder, clash_detect, systems)  │
│ bim/cost/ (estimator, cost_delta, qto, tw$)   │
│ bim/io_usd/ (exporter, importer)              │
│ bim/omniverse.py, ifc_generator.py            │
└───────────────────────────────────────────────┘
```

## TSMC Demo Target

**核心場景:** 「請將那台冰水主機移動到右側柱子旁邊」
- BIMEntity (id/type/name/position/cost) — ✅ M2-BRIDGE
- Scene Query/Operate API — ✅ M2-BRIDGE
- 具名 DemoScene (22 entities) — ✅ M2-BRIDGE
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
| BUILD-008 | DemoScene anonymous Primitives | ✅ Fixed (M2-BRIDGE) |

## Governance Documents

| File | Version |
|------|---------|
| CLAUDE.md | v1.23.3 |
| SKILL.md | v4.3 |
| PROJECT_STATUS.md | v2.5 (this) |
| Context Prompt | v5.7 |

### Sprint S-PTB-RESTRUCTURE 執行結果 — 2026-03-31

- **狀態:** ✅ 完成
- **版本:** mvp-v0.7.0-restructure
- **Tasks:** 25/25
- **ctest:** 69/69 PASS (14 legacy + 55 new bim_core)
- **記憶體:** 8.9/16.0GB(free:7.0GB)
- **AuditReport:** PTB-FAR-RESTRUCTURE-001 (A 98/100)
- **新增 C++ 模組:**
  - `cpp/core/BIMEntity.h/.cpp` — 22 entity types, JSON serialization
  - `cpp/core/BIMSceneGraph.h/.cpp` — Scene management, spatial queries
  - `cpp/core/AgentBridge.h/.cpp` — 13 agent actions
  - `cpp/core/GeometryEngine.h/.cpp` — Area/volume/AABB collision
  - `cpp/core/PropertyManager.h/.cpp` — Materials, property templates
  - `cpp/core/CostCalculator.h/.cpp` — NT$ cost estimation
  - `cpp/core/BIMTypes.h` — EntityType enum, Vec3
  - `cpp/binding/bim_core_module.cpp` — pybind11 Python binding
- **新增測試:** 4 test files (55 tests)
- **新增文檔:** ARCHITECTURE.md
- **CEO決策執行:** 全面重構完成，pytest 完全消除

### Sprint S-PTB-CODE-AUDIT 執行結果 — 2026-03-31 23:22
- **狀態:** ✅ 完成
- **版本:** mvp-v0.7.1-codeaudit
- **Tasks:** 20/20
- **ctest:** 69/69 PASS (⛔零pytest)
- **記憶體:** 9.7/16.0GB(free:6.2GB)
- **AuditReport:** PTB-CAR-001 (A 97/100)
- **修改:** 11 core files, 2 dead files deleted
- **關鍵改善:**
  - [[nodiscard]] + noexcept 50+ methods
  - Buffer overflow fix in executeJson
  - Removed duplicate cpp/bindings/

### Sprint S-PTB-GUI-CONNECT 執行結果 — 2026-03-31 23:45
- **狀態:** ✅ 完成
- **版本:** mvp-v0.8.0-gui
- **Tasks:** 20/20
- **ctest:** 69/69 PASS (⛔零pytest)
- **記憶體:** 9.7/16.0GB(free:6.2GB)
- **AuditReport:** PTB-FAR-GUI-001 (A 95/100)
- **新增檔案:**
  - `src/promptbim/gui/bim_core_bridge.py` — C++ ↔ Python gateway (SceneGraph, AgentBridge, PropertyManager, CostCalculator)
  - `src/promptbim/gui/scene_graph_widget.py` — Tree view of entities grouped by type
  - `src/promptbim/gui/entity_list_view.py` — Flat table listing all BIMEntity
  - `src/promptbim/gui/property_panel.py` — Right-side property inspector from C++ core
  - `src/promptbim/gui/viewport_3d.py` — Top-down 2D projection of SceneGraph geometry
- **修改檔案:**
  - `main_window.py` — Bridge + 3 new panels + C++ 3D View tab
  - `chat_panel.py` — AgentBridge scene command routing
  - `cost_panel.py` — C++ CostCalculator integration
  - CMake: bim_core_static rename, pybind11 build enabled
- **關鍵改善:**
  - 22-entity TSMC demo scene
  - BIMCoreBridge singleton for shared state
  - AgentBridge JSON action routing from ChatPanel

### Sprint S-PTB-AI-LAYER 執行結果 — 2026-04-01 07:55
- **狀態:** ✅ 完成
- **版本:** mvp-v0.9.0-ai
- **Tasks:** 15/15
- **ctest:** 69/69 PASS (⛔零pytest)
- **記憶體:** 9.2/16.0GB(free:6.7GB)
- **AuditReport:** PTB-FAR-AI-001 (A 96/100)
- **新增檔案:**
  - `src/promptbim/ai/__init__.py` — AI package exports
  - `src/promptbim/ai/nl_parser.py` — Two-stage NL parser (regex+LLM), 22 entity types, CJK/EN
  - `src/promptbim/ai/claude_client.py` — Anthropic SDK wrapper with mock mode
  - `src/promptbim/ai/intent_router.py` — 14 IntentTypes → 13 AgentBridge JSON actions
  - `src/promptbim/ai/conversation_history.py` — Rolling context window, token trimming
  - `src/promptbim/ai/error_handler.py` — Bilingual error recovery + suggestions
- **修改檔案:**
  - `chat_panel.py` — _AIWorker thread, NLParser→IntentRouter→AgentBridge pipeline
- **關鍵改善:**
  - NL→Intent→bim_core 完整接通 (13 actions)
  - 雙語支援 (中文+英文)
  - Claude LLM fallback for ambiguous inputs
  - Mock mode for API-free testing
