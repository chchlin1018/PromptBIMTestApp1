# V2 Migration Tasks — Executable Task Breakdown

> Derived from: `docs/DesignDocForV2.md` v1.0.0
> Created: 2026-03-26
> Purpose: Break down V2 architecture migration into actionable Sprint tasks

---

## Phase 0: Preparation (2-3 days)

| # | Task | Priority | Effort | Dependencies |
|---|------|:--------:|:------:|:------------:|
| V2-001 | Create `libpromptbim/` directory with CMakeLists.txt skeleton | P0 | 2h | None |
| V2-002 | Set up vcpkg.json with initial dependencies (nlohmann-json, gtest) | P0 | 1h | V2-001 |
| V2-003 | Define C ABI header `include/promptbim/promptbim.h` with all function signatures | P0 | 4h | V2-001 |
| V2-004 | Set up GoogleTest framework with sample test | P0 | 2h | V2-002 |
| V2-005 | Configure GitHub Actions CI matrix (macOS-14, windows-2022, ubuntu-22.04) | P0 | 3h | V2-001 |
| V2-006 | Create pybind11 binding skeleton for V1 backward compatibility | P1 | 4h | V2-003 |

---

## Phase 1: Pure Logic Module Migration (5-7 days)

| # | Task | Priority | Effort | Dependencies |
|---|------|:--------:|:------:|:------------:|
| V2-010 | Implement Compliance Engine C++ — port 15+ Taiwan building code rules | P0 | 2d | V2-003 |
| V2-011 | Compliance Engine GoogleTest — port Python test fixtures to C++ | P0 | 4h | V2-010 |
| V2-012 | Compliance Engine pybind11 binding — let Python call C++ version | P0 | 4h | V2-010, V2-006 |
| V2-013 | Compliance Engine Python fallback — auto-select native vs Python | P0 | 2h | V2-012 |
| V2-014 | Implement Cost Engine C++ — port QTO + cost estimation logic | P1 | 1.5d | V2-003 |
| V2-015 | Cost Engine GoogleTest + pybind11 binding | P1 | 4h | V2-014 |
| V2-016 | Verify C++ and Python output consistency (compliance + cost) | P0 | 4h | V2-012, V2-015 |

---

## Phase 2: Performance-Sensitive Modules (5-7 days)

| # | Task | Priority | Effort | Dependencies |
|---|------|:--------:|:------:|:------------:|
| V2-020 | MEP A* pathfinding C++ implementation | P0 | 2d | V2-003 |
| V2-021 | MEP Engine GoogleTest + performance benchmarks | P0 | 4h | V2-020 |
| V2-022 | MEP Engine pybind11 + Python fallback | P1 | 4h | V2-020, V2-006 |
| V2-023 | Simulation Engine C++ — 4D scheduler + GIF animation | P1 | 2d | V2-003 |
| V2-024 | Simulation Engine GoogleTest + pybind11 | P1 | 4h | V2-023 |
| V2-025 | Performance comparison report (Python vs C++) | P1 | 2h | V2-021, V2-024 |

---

## Phase 3: BIM Core (7-10 days)

| # | Task | Priority | Effort | Dependencies |
|---|------|:--------:|:------:|:------------:|
| V2-030 | Research IfcOpenShell C++ API (documentation study) | P0 | 1d | None |
| V2-031 | IFC Generator C++ — direct IfcOpenShell C++ API calls | P0 | 3d | V2-030 |
| V2-032 | USD Generator C++ — direct pxr:: namespace calls | P0 | 2d | V2-003 |
| V2-033 | USDZ Packer C++ ��� zip packaging | P1 | 4h | V2-032 |
| V2-034 | BIM Engine GoogleTest — validate against Python output | P0 | 1d | V2-031, V2-032 |
| V2-035 | BIM Engine pybind11 binding + fallback | P1 | 4h | V2-034 |

---

## Phase 4: GIS + Platform UI (10-15 days)

| # | Task | Priority | Effort | Dependencies |
|---|------|:--------:|:------:|:------------:|
| V2-040 | GIS Engine C++ — GDAL/OGR for land parsing (GeoJSON, Shapefile, DXF) | P0 | 3d | V2-003 |
| V2-041 | GIS Engine — GEOS for geometry operations (setback, buffer) | P0 | 2d | V2-040 |
| V2-042 | GIS Engine — PROJ for coordinate projection (WGS84 → TWD97) | P1 | 1d | V2-040 |
| V2-043 | GIS Engine GoogleTest + pybind11 | P0 | 1d | V2-040, V2-041 |
| V2-050 | macOS SwiftUI — 3D preview with SceneKit/RealityKit (replace PyVista) | P1 | 3d | V2-035 |
| V2-051 | macOS SwiftUI — direct libpromptbim C interop | P1 | 2d | V2-050 |
| V2-060 | Windows Qt 6 — project skeleton + CMake integration | P2 | 2d | V2-003 |
| V2-061 | Windows Qt 6 — main window + land import + 3D preview (Qt3D) | P2 | 3d | V2-060 |
| V2-062 | Windows Qt 6 — AI pipeline integration | P2 | 2d | V2-061 |

---

## Phase 5: Web + WASM (10-15 days)

| # | Task | Priority | Effort | Dependencies |
|---|------|:--------:|:------:|:------------:|
| V2-070 | Emscripten build setup for libpromptbim | P2 | 2d | V2-010, V2-014 |
| V2-071 | WASM core module — compliance + cost engines | P2 | 2d | V2-070 |
| V2-072 | React/Vue frontend skeleton with Three.js 3D viewer | P2 | 3d | None |
| V2-073 | REST API backend (FastAPI) — AI Service endpoint | P2 | 2d | None |
| V2-074 | Web frontend — land import + AI generation flow | P2 | 3d | V2-072, V2-073 |
| V2-075 | WASM progressive loading + Service Worker caching | P3 | 2d | V2-071 |
| V2-076 | Web E2E testing | P2 | 1d | V2-074 |

---

## Summary

| Phase | Tasks | Total Effort | Key Output |
|-------|:-----:|:------------:|------------|
| Phase 0 | 6 | 2-3 days | CMake skeleton, C ABI, CI matrix |
| Phase 1 | 7 | 5-7 days | Compliance + Cost in C++ with Python fallback |
| Phase 2 | 6 | 5-7 days | MEP + Simulation in C++ |
| Phase 3 | 6 | 7-10 days | IFC + USD direct C++ generation |
| Phase 4 | 9 | 10-15 days | GIS C++ + macOS SwiftUI + Windows Qt |
| Phase 5 | 7 | 10-15 days | WASM + Web frontend + REST API |
| **Total** | **41** | **~40-60 days** | Full cross-platform product |

---

## Open Decisions

| Decision | Options | Blocker For |
|----------|---------|-------------|
| Windows UI framework | Qt 6 (LGPL/Commercial) vs WinUI 3 vs Dear ImGui | Phase 4 Windows tasks |
| AI Service language | Python (current) vs Node.js | Phase 5 REST API |
| 3D Web renderer | Three.js vs Babylon.js | Phase 5 frontend |
| V2 repository | Same repo (v2 branch) vs new repo | Phase 0 |

---

*Generated from DesignDocForV2.md by Claude Code — Sprint P17 Task 13*
