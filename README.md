# PromptBIMTestApp1

## AI-Powered BIM Building Generator

> **Describe a building in natural language + provide land data = automatic architecture design, BIM models, MEP routing, code compliance, construction simulation, cost estimation, and monitoring**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![C++17](https://img.shields.io/badge/C++-17-blue.svg)]()
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)]()
[![Tests](https://img.shields.io/badge/Tests-1060%2B%20passed-green.svg)]()
[![GoogleTest](https://img.shields.io/badge/C++%20Tests-165%2B%20passed-green.svg)]()
[![POC](https://img.shields.io/badge/Stage-POC%20v2.10.0-orange.svg)]()
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-blue.svg)]()

---

## What Is This?

PromptBIMTestApp1 is a **Proof of Concept (POC)** macOS desktop application that generates complete BIM (Building Information Modeling) models from natural language prompts.

**Users only need to do two things:**
1. Provide land data (area / GeoJSON / image / PDF cadastral document)
2. Type a natural language prompt describing the building

**The system handles everything else automatically.**

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/chchlin1018/PromptBIMTestApp1.git
cd PromptBIMTestApp1
conda create -n promptbim python=3.11 -y
conda activate promptbim
conda install -c conda-forge ifcopenshell -y
pip install -e ".[dev]"
```

### 2. Configure API Key

```bash
cp .env.example .env
chmod 600 .env
nano .env
# Set: ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
```

Get your key at [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

### 3. Run

```bash
# CLI (fastest way to try)
python -m promptbim generate "3-story villa with pool" -o ./output

# Desktop GUI
python -m promptbim gui

# Health check
python -m promptbim check

# Xcode (recommended for macOS development)
open PromptBIMTestApp1.xcodeproj  # Cmd+R to launch
```

### Optional: Web UI & MCP Server

```bash
pip install -e ".[web]"
streamlit run src/promptbim/web/app.py    # Web UI

pip install -e ".[mcp]"
python -m promptbim.mcp.server            # MCP Server (Claude Desktop)
```

See **[SETUP.md](SETUP.md)** for detailed installation instructions.

---

## CLI Usage

```bash
# Generate building from prompt
python -m promptbim generate "12-story residential tower" -o ./output
python -m promptbim generate "school" --template school --land site.geojson
python -m promptbim generate "hospital" --city Kaohsiung --format ifc
python -m promptbim generate --no-cache "villa" -o ./output  # Skip cache

# Plan cache management (v2.4.0+)
python -m promptbim cache list       # List cached plans
python -m promptbim cache stats      # Cache hit rate
python -m promptbim cache clear      # Clear all cache

# System health check
python -m promptbim check              # All checks
python -m promptbim check --ai         # AI connection only
python -m promptbim check --fix        # Auto-fix issues
python -m promptbim check --json       # JSON output

# GUI
python -m promptbim gui
python -m promptbim gui --debug        # With debug logging

# Version
python -m promptbim --version          # < 0.5s (lazy import)
```

---

## Example Prompts

| Prompt | System Auto-Generates |
|--------|----------------------|
| `3-story villa with pool` | Residential plan, RC structure, pool plumbing |
| `12-story residential tower` | 4 units/floor, 2 elevators + fire stairs, full MEP |
| `100MW data center` | Hot/cold aisle, UPS + diesel gen, gas fire suppression |
| `School for 500 students` | Classrooms, corridors, offices, library (template) |
| `Change to 9 floors` | Instant update: area -25%, cost -25%, schedule -120d |

---

## Features (27 Sprints of Development)

| Feature | Description |
|---------|-------------|
| **Land Import** | GeoJSON / Shapefile / DXF / KML / PDF OCR / Manual / AI Image Recognition |
| **AI Building Generation** | Claude Multi-Agent: Enhancer -> Planner -> Builder -> Checker |
| **Async Agents** | async/await with parallel execution + rate limiter (50 RPM) |
| **Plan Cache** | SHA-256 key, LRU eviction (100 entries), TTL 7 days |
| **Dual BIM Output** | IFC (IfcOpenShell) + OpenUSD (pxr) + USDZ |
| **C++ Core Engine** | libpromptbim: Compliance, Cost, MEP, Simulation, IFC, USD, GIS |
| **SwiftUI 3D Preview** | SceneKit embedded in SwiftUI with NativeBIMBridge (C interop) |
| **Interactive Modification** | Natural language edits -> incremental update of all linked data |
| **Taiwan Building Code** | BCR/FAR/height/seismic/fire/accessibility (15+ rules, C++ & Python) |
| **MEP Auto-Routing** | Plumbing / Electrical / HVAC / Fire Protection (3D A*, C++ & Python) |
| **Construction Sim (4D)** | 16-phase animation + Gantt chart + GIF export (C++ & Python) |
| **Cost Estimation (5D)** | Auto QTO + Taiwan market unit prices (C++ & Python) |
| **GIS Engine C++** | GeoJSON/Shapefile/DXF parsing + WGS84↔TWD97 projection |
| **Smart Monitoring** | 48 M&C sensor types, auto-placement + IDTF |
| **USDZ Export** | Apple Vision Pro / Quick Look ready |
| **Plugin Architecture** | @register_plugin decorator, 3 types: agent/parser/code_rule |
| **MCP Server** | Claude Desktop integration (7 tools + 2 resources) |
| **Web UI** | Streamlit browser interface |
| **CLI** | `generate` / `check` / `cache` / `gui` commands |
| **Health Check** | 12-point system check + AI validation + auto-fix |
| **CI/CD** | GitHub Actions: lint + test + build + security audit + C++ tests |

---

## Architecture

### Dual-Layer: C++ Core + Python AI + Swift UI

```
┌────────────────────────────────────────────────────────┐
│  Xcode SwiftUI App (macOS native)                      │
│  ├─ ContentView (Dashboard + 3D Tab)                    │
│  ├─ SceneKitView (3D Preview, embedded in SwiftUI)       │
│  ├─ NativeBIMBridge (Swift ↔ libpromptbim C ABI)         │
│  └─ PythonBridge (Process() → PySide6 GUI)              │
├────────────────────────────────────────────────────────┤
│  libpromptbim (C++17 Core, CMake, pybind11)             │
│  ├─ compliance_engine (15 TW building code rules)        │
│  ├─ cost_engine (QTO + unit prices)                      │
│  ├─ mep_engine (A* pathfinding)                          │
│  ├─ simulation_engine (4D scheduler)                     │
│  ├─ ifc_generator (IFC4 SPF direct write)                │
│  ├─ usd_generator (USDA direct write + USDZ packer)      │
│  └─ gis_engine (GeoJSON/SHP/DXF + WGS84↔TWD97)          │
├────────────────────────────────────────────────────────┤
│  Python Backend (14+ submodules)                        │
│  ├─ agents/ (7 AI Agents + async + rate limiter)         │
│  ├─ bim/ (IFC/USD + components + cost + MEP + sim)       │
│  ├─ codes/ (TW building code, plugin-based)              │
│  ├─ plugins/ (PluginRegistry + @register_plugin)         │
│  ├─ cache/ (SHA-256 key + JSON store + LRU + TTL)        │
│  ├─ land/ (6 parsers + AI image recognition)             │
│  └─ gui/ + mcp/ + web/ + voice/ + viz/                   │
└────────────────────────────────────────────────────────┘
```

### Python Modules (14+ submodules)

| Module | Description |
|--------|-------------|
| `agents/` | 7 AI Agents (enhancer/planner/builder/checker/modifier/orchestrator/land_reader) + async arun() + rate_limiter |
| `bim/` | Geometry, IFC/USD generators, materials, components (76 types), cost, MEP, monitoring, simulation |
| `codes/` | Taiwan building code engine (15+ rules, plugin-based) + _native_bridge.py (C++ fallback) |
| `plugins/` | PluginRegistry + @register_plugin (3 types: agent/parser/code_rule) |
| `cache/` | Plan cache (SHA-256 key, JSON store, LRU max 100, TTL 7 days) |
| `gui/` | PySide6 desktop GUI with startup health check |
| `land/` | Land parsers (GeoJSON/SHP/DXF/KML/PDF OCR/Manual/AI Image) |
| `startup/` | Health check (12 items) + AI check + auto-fix |
| `mcp/` | FastMCP Server for Claude Desktop |
| `web/` | Streamlit web interface |
| `voice/` | Speech-to-text (faster-whisper) |
| `viz/` | 3D/2D visualization (PyVista, matplotlib) |
| `schemas/` | Pydantic models with schema_version |
| `constants.py` | Named constants (no magic numbers) |

### C++ Core (libpromptbim/)

| Engine | Tests | Description |
|--------|:-----:|-------------|
| `compliance_engine` | 12 | 15 Taiwan building code rules (BCR, FAR, height, fire, seismic, etc.) |
| `cost_engine` | 10 | QTO + unit prices (13 categories) + cost breakdown |
| `mep_engine` | 27 | A* pathfinding for MEP routing |
| `simulation_engine` | 10 | 4D construction scheduler |
| `ifc_generator` | 18 | IFC4 SPF direct write (no IfcOpenShell dependency) |
| `usd_generator` | 18 | USDA direct write + USDZ zip packer |
| `gis_engine` | 27 | GeoJSON/Shapefile/DXF parsing + WGS84↔TWD97 projection |
| `geometry` | 15 | Shared poly_area, centroid, setback, buffer |
| **Total** | **137** | All engines have pybind11 bindings + Python fallback |

---

## Development Progress

### V1 POC (P0-P14)

| Sprint | Status | Tests | Description |
|--------|:------:|------:|-------------|
| P0-P10 | Done | 591 | Foundation: Land import → AI Agent → IFC/USD → Code compliance → Cost → MEP → Simulation → Monitoring → AI Image → MCP+Web |
| P11 | Done | 668 | Xcode ↔ PySide6 GUI integration + E2E |
| P12 | Done | 675 | Quality fixes + performance optimization |
| P13 | Done | 705 | CLI + PDF OCR + dependency fixes |
| P14 | Done | 698 | CI/CD + security + documentation v2.0 |

### V1 Quality Hardening (P16-P17.1)

| Sprint | Status | Tests | Description |
|--------|:------:|------:|-------------|
| P16 | Done | 725 | constants.py + tenacity retry + pip-audit |
| P17 | Done | 792 | 8 Parts/34 Tasks: async/await, cache, plugins, rate limiter, schema versioning |
| P17.1 | Done | 799 | Audit fix + doc consistency patch |

### V2 C++ Migration (P18-P21)

| Sprint | Status | Tests | C++ | Description |
|--------|:------:|------:|:---:|-------------|
| P18 | Done | 820 | 24 | Phase 0-1: C++ skeleton + Compliance/Cost Engine + pybind11 |
| P19 | Done | 813 | 70 | Phase 2: MEP/Simulation C++ + tech debt cleanup |
| P20 | Done | 930 | 110 | Phase 3: IFC/USD/USDZ Generator C++ |
| P21 | Done | 957 | 137 | Phase 4: GIS Engine C++ + SwiftUI SceneKit 3D Preview |

### Future Features (Deferred)

| Sprint | Content | When |
|--------|---------|------|
| P22 | Web WASM + REST API + React Frontend | When deployment needed |
| P23 | Windows Qt 6 | When Windows env available |
| P24 | Cross-platform E2E testing | After P22+P23 |
| P25 | C++ performance optimization | When perf bottleneck |
| P26 | App Store / Windows Store packaging | When commercializing |

---

## Tech Stack

| Layer | Technology | License |
|-------|-----------|--------|
| macOS UI | SwiftUI + SceneKit | Apple |
| Desktop GUI | PySide6 | LGPL-3.0 |
| 3D Visualization | PyVista + pyvistaqt | MIT |
| AI | Anthropic Claude API (Multi-Agent) | MIT SDK |
| C++ Core | libpromptbim (CMake, C++17) | MIT |
| BIM | IfcOpenShell + usd-core (pxr) | LGPL / Apache-2.0 |
| GIS | geopandas + shapely + pyproj | BSD |
| Python↔C++ | pybind11 | BSD |
| Testing | pytest + GoogleTest | MIT / BSD |
| CI/CD | GitHub Actions | - |
| Lint | Ruff | MIT |

**100% open source. Zero commercial software dependencies.**

---

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run Python tests
pytest                                    # All tests (820)
pytest -m "not api and not slow" -q       # Fast tests only
pytest --cov=src/promptbim --cov-report=term-missing

# Run C++ tests (requires CMake build)
cd libpromptbim && mkdir -p build && cd build
cmake .. && make -j$(nproc) && ctest --output-on-failure  # 137 tests

# Lint
ruff check src/ tests/
ruff format src/ tests/

# Security audit
pip-audit -r requirements-frozen.txt

# Xcode build
xcodebuild -project PromptBIMTestApp1.xcodeproj \
  -scheme PromptBIMTestApp1 -destination 'platform=macOS' build
```

---

## Documentation

| File | Description |
|------|-------------|
| [SETUP.md](SETUP.md) | Installation & testing guide |
| [docs/API.md](docs/API.md) | API documentation |
| [SKILL.md](SKILL.md) | Project knowledge base (SSOT) v3.2 |
| [TODO.md](TODO.md) | Sprint progress tracking |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [CLAUDE.md](CLAUDE.md) | Claude Code behavior rules v1.14.1 |
| [docs/DesignDocForV2.md](docs/DesignDocForV2.md) | V2 mixed architecture design |
| [docs/V2_Migration_Tasks.md](docs/V2_Migration_Tasks.md) | V2 migration task breakdown (41 tasks) |
| [docs/reports/](docs/reports/) | Sprint audit reports |

---

## License

MIT License -- see [LICENSE](LICENSE)

---

## Credits

- **Developer:** Michael Lin / Reality Matrix Inc.
- **AI:** Anthropic Claude (Multi-Agent Pipeline)
- **BIM:** IfcOpenShell + OpenUSD
- **Built with:** Claude Code + Claude Desktop (AI-assisted development across 27 sprints)

*Reality Matrix Inc. / Michael Lin — 2026*
