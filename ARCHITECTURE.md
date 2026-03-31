# PromptBIM Architecture — C++ Core + Python Binding

> Version: mvp-v0.7.1-codeaudit | Updated: 2026-03-31

## Overview

```
┌─────────────────────────────────────────────┐
│  Qt GUI (PySide6)                           │  ← Thin UI layer
├─────────────────────────────────────────────┤
│  Python App Layer                           │  ← AI/LLM agents, orchestrator
│  src/promptbim/ (7-agent pipeline)          │
├─────────────────────────────────────────────┤
│  Python Binding (pybind11)                  │  ← import bim_core
│  cpp/binding/bim_core_module.cpp            │
├─────────────────────────────────────────────┤
│  C++ Core (bim_core)                        │  ← BIM logic, zero OOM risk
│  cpp/core/                                  │
│  ├── BIMEntity        (22 entity types)     │
│  ├── BIMSceneGraph    (scene management)    │
│  ├── AgentBridge      (13 agent actions)    │
│  ├── GeometryEngine   (area/volume/AABB)    │
│  ├── PropertyManager  (materials/costs)     │
│  └── CostCalculator   (NT$ estimation)      │
├─────────────────────────────────────────────┤
│  C++ Engines                                │
│  cpp/src/     (compliance + cost)           │
│  libpromptbim/ (8 engines: compliance,      │
│    cost, MEP, simulation, IFC, USD, GIS,    │
│    geometry)                                │
├─────────────────────────────────────────────┤
│  ctest (C++ unit tests)                     │  ← Zero OOM risk
│  69 tests: 14 legacy + 55 bim_core         │
└─────────────────────────────────────────────┘
```

## C++ Core Modules (cpp/core/)

| Module | Header | Purpose |
|--------|--------|---------|
| BIMEntity | BIMEntity.h | Entity with 22 BIM types, properties, connections, JSON serialization |
| BIMSceneGraph | BIMSceneGraph.h | Scene container, spatial queries, CRUD operations |
| AgentBridge | AgentBridge.h | 13 agent actions (5 query + 6 operate + 2 cost/schedule) |
| GeometryEngine | GeometryEngine.h | Polygon area, volumes, AABB collision detection |
| PropertyManager | PropertyManager.h | Material registry, property templates, cost lookup |
| CostCalculator | CostCalculator.h | Per-entity costing, summary, delta calculation |
| BIMTypes | BIMTypes.h | EntityType enum (22 types), Vec3, shared definitions |

## Python Binding

```python
import bim_core

# Create scene
sg = bim_core.BIMSceneGraph()
entity = bim_core.BIMEntity("ch-01", bim_core.EntityType.Chiller, "Chiller 1")
entity.set_position(bim_core.Vec3(0, 0, 0))
sg.add_entity(entity)

# Agent bridge
bridge = bim_core.AgentBridge(sg)
result = bridge.query_by_type("Chiller")
print(result.data)  # JSON
```

## Build

```bash
cmake -B build -DBUILD_TESTS=ON
cmake --build build
ctest --test-dir build
```

## Directory Structure

```
PromptBIMTestApp1/
├── cpp/
│   ├── core/           # NEW: bim_core standalone C++ library
│   │   ├── BIMTypes.h
│   │   ├── BIMEntity.h/.cpp
│   │   ├── BIMSceneGraph.h/.cpp
│   │   ├── AgentBridge.h/.cpp
│   │   ├── GeometryEngine.h/.cpp
│   │   ├── PropertyManager.h/.cpp
│   │   ├── CostCalculator.h/.cpp
│   │   └── CMakeLists.txt
│   ├── binding/        # pybind11 bindings (bim_core + promptbim_cpp)
│   ├── src/            # Legacy compliance + cost engines
│   └── tests/          # GoogleTest (promptbim_tests + bim_core_tests)
├── libpromptbim/       # Full C++ library (8 engines)
├── zigma/              # Qt6/QML desktop app
├── src/promptbim/      # Python app layer
└── CMakeLists.txt      # Root build config
```

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| No Qt in core | C++17 STL only | Standalone, testable without GUI |
| nlohmann/json | JSON serialization | Industry standard, header-only |
| ctest only | No pytest | ISS-042: pytest+PySide6 causes OOM |
| pybind11 | Python binding | Seamless C++↔Python |
| EntityType enum | 22 types | Matches zigma/ BIMEntity spec |
| AABB collision | GeometryEngine | Fast O(n²) broad-phase detection |
| [[nodiscard]] | Core API safety | Prevent silent discard of results |
| noexcept | Vec3/AABB/trivial | Enables compiler optimizations |
