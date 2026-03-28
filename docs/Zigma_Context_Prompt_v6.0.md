# Zigma Context Prompt v6.0

> Last updated: 2026-03-28 | HEAD: e02bb94

## Identity

**Zigma PromptToBuild** — NL→3D BIM generation platform for semiconductor fabs.
Developer: Michael Lin (CEO, Reality Matrix Inc.)
Repo: chchlin1018/PromptBIMTestApp1 (private)
Local: ~/Dev/PromptBIMTestApp1 (Mac Mini + MacBook)

## Architecture

Frontend: Qt Quick 3D (C++) — cross-platform (macOS Metal / Windows D3D12)
Backend: Python AI Agents (IDTF v3.5) — via AgentBridge (QProcess + JSON stdio)
3D Engine: Qt Quick 3D (RHI abstraction)
Geometry: OCCT kernel (future)
Output: OpenUSD → Omniverse / Revit / IFC

## Completed Sprints

| Sprint | Tasks | Tag | Key Output |
|--------|:-----:|:---:|------------|
| M1-MVP | 68T | mvp-v0.1.0 | Qt Quick 3D + AgentBridge + ChatPanel + 4 BIM panels |
| MEDIA-DL | 12T | — | 37 files (81MB) → iCloud ~/ZigmaMedia/ |
| M1-SCENE | 22T | mvp-v0.2.0 | ZigmaLogger + DemoScene.qml (TSMC fab) + BIMView3D |
| M2-ENV | 8T | mvp-v0.2.1 | Environment verification + AuditReport |

## Planned Sprints (PROMPT files on GitHub)

| Sprint | Tasks | Tag | Goal |
|--------|:-----:|:---:|------|
| M2-BRIDGE | 25T | mvp-v0.3.0 | BIMEntity C++ + AgentBridge bidirectional + SceneGraph |
| M2-ENTITY | 20T | mvp-v0.4.0 | DemoScene named entities + CUB equipment catalog |
| M2-MEP-DEMO | 25T | mvp-v0.5.0 | Full "冰水主機" demo + MEP pipes + cost linkage |
| P30-USD-REVIT | 25T | v3.0.0 | USD→Revit DirectShape + Native MEP + IFC export |

## TSMC Demo Core Scene

「請將那台冰水主機移動到右側柱子旁邊」
→ AI 語義辨識 + 空間推理 + 即時 3D 移動 + 管線重路由 + 成本差異回報

## IDTF v3.5 Available Modules (Python Backend ~90% ready)

| Module | File | Size | Demo Value |
|--------|------|------|:----------:|
| Orchestrator | agents/orchestrator.py | 19KB | ★★★★★ |
| Modifier | agents/modifier.py | 25KB | ★★★★★ |
| Planner | agents/planner.py | 20KB | ★★★★ |
| MEP PathFinder | bim/mep/pathfinder.py | 9KB | ★★★★★ |
| Clash Detect | bim/mep/clash_detect.py | 5KB | ★★★★★ |
| MEP Systems | bim/mep/systems.py | 14KB | ★★★★ |
| Cost Delta | bim/cost/cost_delta.py | 9KB | ★★★★★ |
| Unit Prices TW | bim/cost/unit_prices_tw.py | 5KB | ★★★★★ |
| Cost Estimator | bim/cost/estimator.py | 18KB | ★★★★ |
| USD Generator | bim/usd_generator.py | 17KB | ★★★★ |
| USD Exporter | bim/io_usd/exporter.py | 3KB | ★★★★ |
| Omniverse | bim/omniverse.py | 8KB | ★★★ |
| IFC Generator | bim/ifc_generator.py | 11KB | ★★★ |

## Key Files

| File | Purpose |
|------|---------|
| CLAUDE.md | Claude Code rules (v1.23.3) — notify functions, BUILD rules |
| SKILL.md | v5.0 — build lessons, architecture, Sprint patterns |
| PROJECT_STATUS.md | v2.0 — current state |
| zigma/CMakeLists.txt | Build config (C++ absolute / QML relative) |
| zigma/src/main.cpp | Entry: qrc:/Zigma/qml/main.qml |
| zigma/src/AgentBridge.cpp | Python↔C++ bridge (QProcess + JSON) |
| zigma/src/ZigmaLogger.cpp | Debug logging (5-level, file+stderr, rotation) |
| zigma/qml/BIMView3D.qml | 3D viewport (Camera + 3-Light + Orbit) |
| zigma/qml/DemoScene.qml | TSMC fab scene (11 building elements) |
| agent_runner.py | Python AI entry point |

## BUILD Rules (鐵律)

1. CMake: C++ uses `${CMAKE_CURRENT_SOURCE_DIR}/src/` absolute paths
2. CMake: QML uses relative paths `qml/xxx.qml`
3. QML: onPropertyChanged handler on property owner (root), not Canvas
4. main.cpp: `qrc:/Zigma/qml/main.qml`
5. .env: NEVER put empty ANTHROPIC_API_KEY (breaks Claude Code)
6. Sprint PROMPT: push to `sprints/PROMPT_xxx.md`, Claude Code reads file

## Dev Environment

| Device | Role | Path |
|--------|------|------|
| Mac Mini M4 | Build/execute server (24/7) | ~/Dev/PromptBIMTestApp1 |
| MacBook Air | Xcode/design | ~/Dev/PromptBIMTestApp1 |
| Windows RTX4090 | Omniverse/Revit (future) | TBD |
| iPhone 16 Pro | RDC mobile command | — |

## Notion Pages

| Page | ID |
|------|----|
| Workspace | 330f154a-6472-81ae |
| Parent | 320f154a-6472-804f |
| 狀態總覽 | 331f154a-6472-81f5 |
| TSMC Demo 分析 | 331f154a-6472-8164 |
| IDTF 分析 | 331f154a-6472-8155 |
| M1-SCENE 報告 | 331f154a-6472-812b |
