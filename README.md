# PromptBIMTestApp1

## AI-Powered BIM Building Generator

> **Describe a building in natural language + provide land data = automatic architecture design, BIM models, MEP routing, code compliance, construction simulation, cost estimation, and monitoring**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)]()
[![Tests](https://img.shields.io/badge/Tests-957%20passed-green.svg)]()
[![POC](https://img.shields.io/badge/Stage-POC%20v2.8.0-orange.svg)]()
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

# System health check
python -m promptbim check              # All checks
python -m promptbim check --ai         # AI connection only
python -m promptbim check --fix        # Auto-fix issues
python -m promptbim check --json       # JSON output

# GUI
python -m promptbim gui
python -m promptbim gui --debug        # With debug logging

# Version
python -m promptbim --version
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

## Features (20 Sprints of Development)

| Feature | Description |
|---------|-------------|
| **Land Import** | GeoJSON / Shapefile / DXF / KML / PDF OCR / Manual / AI Image Recognition |
| **AI Building Generation** | Claude Multi-Agent: Enhancer -> Planner -> Builder -> Checker |
| **Dual BIM Output** | IFC (IfcOpenShell) + OpenUSD (pxr) + USDZ |
| **Interactive Modification** | Natural language edits -> incremental update of all linked data |
| **Taiwan Building Code** | BCR/FAR/height/seismic/fire/accessibility (15+ rules) |
| **MEP Auto-Routing** | Plumbing / Electrical / HVAC / Fire Protection (3D A*) |
| **Construction Sim (4D)** | 16-phase animation + Gantt chart + GIF export |
| **Cost Estimation (5D)** | Auto QTO + Taiwan market unit prices |
| **Smart Monitoring** | 48 M&C sensor types, auto-placement + IDTF |
| **USDZ Export** | Apple Vision Pro / Quick Look ready |
| **MCP Server** | Claude Desktop integration (7 tools + 2 resources) |
| **Web UI** | Streamlit browser interface |
| **CLI** | `generate` / `check` / `gui` commands |
| **Health Check** | 12-point system check + AI validation + auto-fix |
| **Debug Logging** | Full-module debug logging with `--debug` flag |
| **CI/CD** | GitHub Actions: lint + test + build + security audit |

---

## Architecture

```
Xcode SwiftUI App
  |-- PythonBridge.swift (Process())
       |-- python -m promptbim gui
            |-- PySide6 MainWindow
                 |-- ChatPanel -> Orchestrator
                 |    |-- EnhancerAgent  -> Claude API
                 |    |-- PlannerAgent   -> Claude API / Fallback
                 |    |-- BuilderAgent   -> IFC + USD (pure Python, no LLM)
                 |    +-- CheckerAgent   -> Taiwan Code Engine
                 |-- ModelView     -> PyVista 3D
                 |-- MapView       -> Matplotlib 2D
                 |-- CostPanel     -> QTO + Estimator
                 |-- MEPToggle     -> A* Pathfinder
                 |-- SimulationTab -> 4D Scheduler
                 +-- MonitorToggle -> Auto-placement
```

### Python Modules (14+ submodules)

| Module | Description |
|--------|-------------|
| `agents/` | 7 AI Agents (enhancer/planner/builder/checker/modifier/orchestrator/land_reader) |
| `bim/` | Geometry, IFC/USD generators, materials, components (76 types), cost, MEP, monitoring, simulation |
| `codes/` | Taiwan building code engine (15+ rules across 4 categories) |
| `gui/` | PySide6 desktop GUI with startup health check |
| `land/` | Land parsers (GeoJSON/SHP/DXF/KML/PDF OCR/Manual/AI Image) |
| `startup/` | Health check (12 items) + AI check + auto-fix |
| `mcp/` | FastMCP Server for Claude Desktop |
| `web/` | Streamlit web interface |
| `voice/` | Speech-to-text (faster-whisper) |
| `viz/` | 3D/2D visualization (PyVista, matplotlib) |

---

## Development Progress

| Sprint | Status | Tests | Description |
|--------|:------:|------:|-------------|
| P0 | Done | 29 | Project skeleton + Xcode + environment |
| P1 | Done | 48 | Land import + 2D view |
| P2 | Done | 82 | IFC + USD generation core |
| P2.5 | Done | 108 | Building component library (76 types) |
| P3 | Done | 127 | 3D interactive preview |
| P4 | Done | 164 | AI Agent Pipeline |
| P4.5 | Done | 211 | Taiwan building code engine |
| P4.8 | Done | 235 | Interactive modification engine |
| P5 | Done | 265 | Voice + export |
| P6 | Done | 293 | Cost estimation (5D) |
| P7 | Done | 338 | MEP auto-routing |
| P8 | Done | 388 | Construction simulation (4D) |
| P8.5 | Done | 440 | Smart monitoring points |
| P9 | Done | 516 | AI image recognition + USDZ + MCP + Web |
| P10 | Done | 591 | Polish + remaining backlog |
| P10.2 | Done | 603 | Debug logging system |
| P10.3 | Done | 645 | Startup health check + AI validation |
| P11 | Done | 668 | Xcode <-> PySide6 GUI integration + E2E |
| P12 | Done | 675 | Quality fixes + performance optimization |
| P13 | Done | 705 | CLI + dependency fixes + PDF OCR |
| P14 | Done | 705+ | CI/CD + security + documentation v2.0 |

---

## Tech Stack (100% Open Source)

| Layer | Technology |
|-------|-----------|
| Desktop GUI | PySide6 |
| 3D Visualization | PyVista + pyvistaqt |
| AI | Anthropic Claude API (Multi-Agent) |
| BIM | IfcOpenShell + usd-core (pxr) |
| GIS | geopandas + shapely + pyproj |
| MEP | Custom 3D A* Pathfinder |
| Building Code | Custom Python Rule Engine |
| Web | Streamlit |
| MCP | FastMCP |
| CI/CD | GitHub Actions |
| Lint | Ruff |

---

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest                                    # All tests
pytest -m "not api and not slow" -q       # Fast tests only
pytest --cov=src/promptbim --cov-report=term-missing  # With coverage

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
| [SKILL.md](SKILL.md) | Project knowledge base (SSOT) |
| [TODO.md](TODO.md) | Sprint progress tracking |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [CLAUDE.md](CLAUDE.md) | Claude Code behavior rules |
| [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | Demo video script |
| [docs/reports/](docs/reports/) | Quality reports |

---

## License

MIT License -- see [LICENSE](LICENSE)

---

## Credits

- **Developer:** Michael Lin / Reality Matrix Inc.
- **AI:** Anthropic Claude (Multi-Agent Pipeline)
- **BIM:** IfcOpenShell + OpenUSD
- **Built with:** Claude Code (AI-assisted development across 20 sprints)

*Reality Matrix Inc. / Michael Lin -- 2026*
