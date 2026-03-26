# PromptBIM API Documentation

> Version: v2.12.0 | Updated: 2026-03-27

---

## Overview

PromptBIM is an AI-powered BIM (Building Information Modeling) building generator. It takes natural language descriptions and real land parcel data to produce IFC, USD/USDZ building models with compliance checking and cost estimation.

**v2.12.0 Highlights:**
- Pipeline performance benchmarks with CI integration
- IFC/USD generation optimization (material pre-warming)
- Memory leak detection and startup time analysis
- Windows platform support (CI, path compat, setup scripts)
- Auto-generated API documentation (pdoc)
- Cross-platform test markers and compatibility tests

---

## Quick Start

```python
from promptbim.agents.orchestrator import Orchestrator
from promptbim.schemas.land import LandParcel
from promptbim.schemas.zoning import ZoningRules

# 1. Define land
land = LandParcel(
    name="My Site",
    boundary=[(0, 0), (40, 0), (40, 30), (0, 30)],
    area_sqm=1200.0,
)

# 2. Set zoning rules
zoning = ZoningRules(city="Taipei")

# 3. Generate
orch = Orchestrator(output_dir="./output")
result = orch.generate("5-story residential building", land, zoning)

# 4. Use results
if result.success:
    print(f"Building: {result.building_name}")
    print(f"IFC: {result.ifc_path}")
    print(f"USD: {result.usd_path}")
```

---

## Core Schemas

### LandParcel

```python
from promptbim.schemas.land import LandParcel

parcel = LandParcel(
    name="Site A",
    boundary=[(0, 0), (50, 0), (50, 40), (0, 40)],
    area_sqm=2000.0,
    source_type="manual",  # manual | geojson | shapefile | dxf | kml | image | mcp
)
```

### BuildingPlan

```python
from promptbim.schemas.plan import BuildingPlan

plan = BuildingPlan(
    name="Villa",
    num_stories=3,
    story_height=3.2,
    footprint=[(0, 0), (20, 0), (20, 15), (0, 15)],
)
```

### ZoningRules

```python
from promptbim.schemas.zoning import ZoningRules

zoning = ZoningRules(
    zone_type="residential",
    far_limit=2.0,
    bcr_limit=0.6,
    height_limit_m=15.0,
    setback_front_m=5.0,
)
```

---

## Agents

### Orchestrator (Pipeline Manager)

```python
from promptbim.agents.orchestrator import Orchestrator

orch = Orchestrator(output_dir="./output")
result = orch.generate(prompt, land, zoning)

# Modify existing building
new_plan, record = orch.modify("add rooftop garden", zoning)
```

### Individual Agents

```python
# Enhancer: Expand user prompt into detailed requirements
from promptbim.agents.enhancer import EnhancerAgent
enhancer = EnhancerAgent()
requirements = enhancer.enhance("3-story villa")

# Planner: Generate building plan
from promptbim.agents.planner import PlannerAgent
planner = PlannerAgent()
plan = planner.plan(requirements, land, zoning)

# Builder: Generate IFC + USD files
from promptbim.agents.builder import BuilderAgent
builder = BuilderAgent(output_dir="./output")
paths = builder.build(plan)

# Checker: Run compliance checks
from promptbim.agents.checker import CheckerAgent
checker = CheckerAgent()
report = checker.check(plan, land, zoning)

# Modifier: Apply modifications
from promptbim.agents.modifier import ModifierAgent
modifier = ModifierAgent()
new_plan = modifier.modify(plan, "change to 9 floors")
```

---

## Land Parsers

```python
from promptbim.land.parsers.geojson import parse_geojson
from promptbim.land.parsers.shapefile import parse_shapefile
from promptbim.land.parsers.dxf import parse_dxf
from promptbim.land.parsers.kml import parse_kml
from promptbim.land.parsers.pdf_ocr import PDFLandParser
from promptbim.land.parsers.image_ai import parse_land_image

parcels = parse_geojson("site.geojson")
parcels = parse_shapefile("site.shp")
parcels = parse_dxf("site.dxf")
parcels = parse_kml("site.kml")
parcels = PDFLandParser().parse("cadastral.pdf")  # requires [pdf]
parcel = parse_land_image("aerial.jpg")            # requires API key
```

---

## BIM Generators

```python
from promptbim.bim.ifc_generator import IFCGenerator
from promptbim.bim.usd_generator import USDGenerator
from promptbim.bim.usdz_packer import pack_usdz

gen = IFCGenerator()
ifc_path = gen.generate(plan, output_dir="./output")

gen = USDGenerator()
usd_path = gen.generate(plan, output_dir="./output")
usdz_path = pack_usdz(usd_path)
```

---

## Code Compliance

```python
from promptbim.codes.registry import run_all_checks, get_compliance_summary

results = run_all_checks(plan, land, zoning)
summary = get_compliance_summary(results)
```

---

## Cost Estimation

```python
from promptbim.bim.cost.estimator import CostEstimator

estimator = CostEstimator()
cost = estimator.estimate(plan)
print(f"Total: NT${cost.total:,.0f}")
```

---

## MEP (Mechanical/Electrical/Plumbing)

```python
from promptbim.bim.mep.planner import MEPPlanner

planner = MEPPlanner()
mep_result = planner.plan(plan)
```

---

## Construction Simulation

```python
from promptbim.bim.simulation.scheduler import generate_schedule

schedule = generate_schedule(plan)
```

---

## Monitoring Points

```python
from promptbim.bim.monitoring.auto_placement import AutoPlacement

placer = AutoPlacement()
monitor_plan = placer.place(plan)
```

---

## MCP Server (v2.10.0)

Claude Desktop integration via Model Context Protocol.

```bash
python -m promptbim.mcp.server
```

**Claude Desktop config** (`claude_desktop_config.json`):
```json
{
    "mcpServers": {
        "promptbim": {
            "command": "python",
            "args": ["-m", "promptbim.mcp.server"],
            "env": {"PYTHONPATH": "src"}
        }
    }
}
```

**Available MCP Tools (10):**
- `import_land` -- Import land parcel by boundary coordinates
- `set_zoning` -- Set zoning rules (BCR, FAR, height, setbacks)
- `generate_building` -- Generate from natural language prompt
- `agenerate_building` -- Async generation with timeout protection
- `modify_building` -- Apply modifications to current building
- `check_compliance` -- Run Taiwan building code compliance
- `estimate_cost` -- Estimate construction cost (TWD)
- `auto_monitor` -- Place smart monitoring sensors
- `clear_cache` -- Clear session state
- `get_session_info` -- Get current session summary

**MCP Resources (2):**
- `building://current` -- Current building state
- `building://land` -- Current land parcel

---

## Voice Input (v2.10.0)

Speech-to-text for natural language building generation.

```python
from promptbim.voice.stt import VoiceInput

vi = VoiceInput()
vi.start_recording()
# ... user speaks ...
text = vi.stop_and_transcribe_sync()
# text = "5-story residential building with rooftop garden"
```

**Backends:** faster-whisper (local, no API key) > macOS native (fallback)

---

## Web UI (Streamlit)

```bash
streamlit run src/promptbim/web/app.py
```

---

## C++ Native Library (libpromptbim v2.10.0)

C ABI for Swift/Python/WebAssembly interop.

```c
const char* pb_version(void);                    // "2.10.0"
char* pb_check_compliance(plan, land, zoning);   // JSON result
char* pb_estimate_cost(plan_json);               // JSON result
PBPlan* pb_plan_from_json(json_str);             // Parse plan
int pb_generate_ifc(plan, output_path);          // Write IFC4
int pb_generate_usd(plan, output_path);          // Write USDA
int pb_generate_usdz(usd_path, output_path);     // Pack USDZ
```

---

## Configuration

`.env` file:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
CLAUDE_MODEL=claude-sonnet-4-20250514
OUTPUT_DIR=./output
DEFAULT_CITY=Taipei
DEBUG_MODE=false
```

```python
from promptbim.config import get_settings
settings = get_settings()
```

---

## CLI

```bash
python -m promptbim --version
python -m promptbim gui
python -m promptbim generate "5-story office building"
python -m promptbim check [--ai]
```

---

## Auto-Generated API Docs

Full API reference can be generated locally:

```bash
pip install pdoc
python scripts/generate_api_docs.py --output docs/api
# Open docs/api/index.html in your browser
```

---

*API.md v2.12.0 | 2026-03-27 | Sprint P25*
