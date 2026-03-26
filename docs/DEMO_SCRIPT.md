# PromptBIM Demo Script

> Version: v2.12.0 | Date: 2026-03-27
> Total estimated duration: ~8 minutes
> Updated: P25 — Performance benchmarks, Windows support, API docs

---

## Scene 1: Application Launch (45s)

### Steps
1. Open Xcode, select `PromptBIMTestApp1` scheme
2. Press **Cmd+R** to build and run
3. Splash screen appears: "PromptBIM is starting..."
4. PySide6 GUI window opens automatically

### Expected Screen
- Xcode: BUILD SUCCEEDED in console
- SwiftUI window: Green checkmark + "PySide6 GUI is running"
- PySide6 window: Full GUI with chat panel, 3D viewport, land panel

### Narration
> "PromptBIM is a macOS native application that bridges Xcode's SwiftUI shell with a Python-powered BIM generation backend. One click to build, one click to run. The PySide6 GUI launches automatically."

---

## Scene 2: Land Data Import (60s)

### Steps
1. Drag and drop `Pic_MyLand.jpg` image onto the land panel
2. AI vision analyzes the land boundary from the image
3. Confirm detected boundary on the site plan view
4. Show area calculation and local coordinate overlay

### Expected Screen
- Image thumbnail in land panel
- Detected polygon overlay on the image
- Site plan view with boundary, area (e.g., "662 sqm"), and north arrow

### Narration
> "Users can import land data from photos, GeoJSON, KML, Shapefile, or DXF. Here we drag a photo of the land. AI vision detects the boundary, converts to local coordinates, and calculates the buildable area."

---

## Scene 3: AI Building Generation (90s)

### Steps
1. Type in chat: "Please build a 3-story villa on 200 pyeong land"
2. AI interprets the prompt, extracts parameters
3. Builder Agent generates: floor plans, structure, walls, slabs, openings
4. Progress bar shows generation stages
5. Results appear: IFC + USD + compliance + cost

### Expected Screen
- Chat bubble with user prompt
- AI response with extracted parameters (stories: 3, type: residential)
- Generation progress: Template -> IFC -> USD -> Compliance -> Cost
- Completion summary with file sizes

### Narration
> "Just describe what you want in natural language. The AI interprets your request, and the deterministic Builder Agent generates a complete BIM model with IFC and USD outputs. No LLM is used in the generation itself, ensuring reproducible results."

---

## Scene 4: 3D Preview + Reports (60s)

### Steps
1. Rotate the 3D model in the PyVista viewport
2. Switch between floors using the floor selector
3. Open the compliance report tab
4. Open the cost estimation tab

### Expected Screen
- 3D building model with colored walls, slabs, roof
- Floor plan SVG for selected story
- Compliance table: green checkmarks for passing rules
- Cost breakdown: total TWD, per-floor, per-category chart

### Narration
> "The 3D preview is interactive, built with PyVista. Floor plans are SVG-rendered for clarity. Every generation includes Taiwan building code compliance checks and detailed cost estimation."

---

## Scene 5: Modification + Undo (60s)

### Steps
1. Type: "Change to 9 stories"
2. Modification engine processes the incremental update
3. 3D model updates showing 9 stories
4. Click "Undo" to revert to 3-story version
5. Click "Redo" to go back to 9 stories

### Expected Screen
- Chat showing modification command
- Building transitions from 3 to 9 stories
- Version history panel showing v1 (3F) and v2 (9F)
- Undo restores v1, redo restores v2

### Narration
> "Modifications are incremental. Say 'change to 9 stories' and only the affected parts are regenerated. Full version history with undo/redo is maintained. No need to start from scratch."

---

## Scene 6: MEP + Simulation + Monitoring (60s)

### Steps
1. Show MEP panel: auto-routed plumbing, HVAC, electrical
2. Show construction simulation timeline (4D)
3. Play the Gantt chart animation
4. Show monitoring point placements

### Expected Screen
- MEP routes overlaid on floor plan (color-coded by system)
- Gantt chart with construction phases
- Phase animation: foundation -> structure -> envelope -> MEP -> finish
- Monitoring points on 3D model with `monitor:` namespace labels

### Narration
> "MEP auto-routing handles plumbing, HVAC, and electrical. The 4D simulation generates a construction schedule with a Gantt chart. Monitoring points are placed automatically for IDTF integration."

---

## Scene 7: Export (45s)

### Steps
1. Click "Export" button
2. Show exported files: IFC, USDA, USDZ, SVG floor plans
3. Open the USDZ file in macOS Quick Look
4. Show the SVG floor plan in a browser

### Expected Screen
- File browser showing output directory with all exported files
- Quick Look preview of USDZ (3D model on macOS)
- SVG floor plan rendered in browser

### Narration
> "One-click export produces industry-standard IFC for BIM software, USD/USDZ for AR preview on Apple devices, and SVG floor plans. All files are generated locally, no cloud dependency."

---

## Scene 8: Health Check (30s)

### Steps
1. Open Terminal
2. Run: `python -m promptbim check`
3. Show all 12 checks passing
4. Run: `python -m promptbim check --ai` to verify AI connectivity

### Expected Screen
- Terminal output with green checkmarks for all categories
- Python env, core dependencies, AI services, filesystem all passing
- "12/12 passed" summary

### Narration
> "The built-in health check verifies the entire stack: Python environment, all dependencies, AI API connectivity, and filesystem access. This ensures the system is ready before any demo or deployment."

---

## Technical Notes for Recording

- **Resolution**: 2560x1440 or higher
- **Frame rate**: 30fps minimum
- **Audio**: Record narration separately, mix in post
- **Xcode**: Have the project pre-built to avoid long initial compile
- **API Key**: Ensure `.env` has a valid `ANTHROPIC_API_KEY`
- **Network**: Stable internet for AI ping in Scene 8
- **Clean state**: Delete `output/` directory before recording for clean demo
