# PromptBIMTestApp1 — Context Prompt

> Paste this into a new conversation to continue PromptBIM development.
> Updated: 2026-03-26 | Based on: Sprint P23 (v2.10.0)

---

## 1. Project Info

- **Name:** PromptBIMTestApp1 -- AI-Powered BIM Building Generator
- **GitHub:** https://github.com/chchlin1018/PromptBIMTestApp1 (private)
- **Org:** Reality Matrix Inc. / Michael Lin
- **Type:** POC (Proof of Concept)
- **Version:** v2.10.0 (P23)
- **Tests:** ~1060+ total (pytest ~860 + GoogleTest ~165 + XCTest ~35)

---

## 2. Architecture

### Dual GUI
1. **Xcode SwiftUI** -- Splash + Python detection + PySide6 launcher + 3D preview + 2D cadastral view
2. **Python PySide6** -- Full-featured GUI (launched via PythonBridge)

### Python Backend (14+ submodules)
- `agents/` -- 7 AI Agents (enhancer/planner/builder/checker/modifier/orchestrator/land_reader)
- `bim/` -- geometry + IFC/USD/USDZ generation + cost + MEP + monitoring + simulation
- `codes/` -- Taiwan building code compliance (15+ rules)
- `gui/` -- PySide6 GUI
- `land/` -- Land import (GeoJSON/SHP/DXF/KML/PDF/Image)
- `mcp/` -- FastMCP Server (10 tools, 2 resources, async generation)
- `voice/` -- STT (faster-whisper + macOS native)
- `web/` -- Streamlit UI
- `viz/` -- 3D/2D visualization

### C++ (libpromptbim v2.10.0)
- C ABI for compliance, cost, IFC/USD generation, GIS
- Swift interop via NativeBIMBridge (dlopen/dlsym)

### Swift Sources (7 files)
- `ContentView.swift` -- Dark/Light theme, collapsible sidebar, 2D/3D views, voice input, pipeline progress
- `PythonBridge.swift` -- Thread-safe conda detection + PySide6 lifecycle
- `SceneKitView.swift` -- SceneKit 3D wrapper
- `BIMSceneBuilder.swift` -- JSON/USDA scene building with path injection protection
- `NativeBIMBridge.swift` -- C ABI bridge with safe string conversion
- `PBResult.swift` -- Cross-layer error propagation
- `PromptBIMTestApp1App.swift` -- App entry point

---

## 3. Sprint History

| Sprint | Description | Tests |
|--------|------------|:-----:|
| P0-P18 | Foundation + V2 Migration | 820 |
| P19-P21 | BIM/GIS/USD engines | 957 |
| P22-P22.1 | Audit fixes + quality | 1012 |
| **P23** | **Audit fixes + GUI + MCP + Voice** | **1060+** |

---

## 4. Dev Environment

### Mac Mini M4 (Claude Code)
- Path: `~/Documents/MyProjects/PromptBIMTestApp1`
- Python: conda `promptbim` (3.11)

---

## 5. Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` v1.17.0 | Claude Code behavior rules |
| `SKILL.md` v3.3 | Project SSOT |
| `docs/API.md` v2.10.0 | API documentation |
| `docs/DesignDocForV2.md` | V2 hybrid architecture |
| `sprints/PROMPT_P{X}.md` | Sprint prompts |
| `docs/audit-reports/` | Audit reports |

---

*Context Prompt v2.10.0 | 2026-03-26 | Sprint P23*
