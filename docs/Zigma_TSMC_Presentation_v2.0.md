# Zigma PromptToBuild — TSMC Presentation v2.0

> **10 Pages** | **mvp-v0.1.0** | Qt Quick 3D Edition

---

## Page 1: Cover

**Zigma PromptToBuild**
*AI-Powered BIM Generation Platform*

- Version: mvp-v0.1.0
- Platform: macOS / Metal
- Presented to: TSMC Facilities Division

---

## Page 2: The Problem

### Current BIM Workflow Challenges

- **Weeks** to produce initial building concepts
- Manual modeling in Revit/ArchiCAD requires specialized skills
- Cost estimation disconnected from design iteration
- Schedule planning happens after design freeze
- Each design change requires manual update across all documents

### Zigma's Promise
> **Natural language → Complete BIM model in seconds**

---

## Page 3: Zigma Architecture

```
┌─────────────────────────────────────────────┐
│              Qt Quick 3D (Metal)             │
│  ┌──────┐ ┌──────────┐ ┌─────────────────┐  │
│  │ Chat │ │ 3D View  │ │ Properties/Cost │  │
│  │ Panel│ │ (PBR)    │ │ Schedule/Delta  │  │
│  └──┬───┘ └────┬─────┘ └────────┬────────┘  │
│     │     AgentBridge (JSON stdio)           │
│     └──────────┼─────────────────┘           │
├────────────────┼─────────────────────────────┤
│  Python AI     │                             │
│  ┌─────────────▼──────────────────┐          │
│  │ Orchestrator → BuildingPlan    │          │
│  │ MeshSerializer → 3D Geometry   │          │
│  │ CostEstimator → NT$ Breakdown  │          │
│  │ SchedulePlanner → Gantt + 4D   │          │
│  └────────────────────────────────┘          │
└─────────────────────────────────────────────┘
```

- **C++ Frontend**: Qt 6.11 Quick 3D with Metal rendering
- **Python Backend**: AI orchestration via JSON stdio protocol
- **Crash Recovery**: Auto-reconnect with 3 retry attempts

---

## Page 4: TSMC Fab Demo (S2)

### 120m × 80m Fabrication Facility

| Parameter | Value |
|-----------|-------|
| Footprint | 120 × 80m (9,600 m²) |
| Stories | 4 (B1F + 1F-3F) |
| Floor Height | 5.0–6.0m |
| Structure | RC walls 300mm + columns |
| Cleanroom | 6,000 m² per floor |
| BCR | 60% |

### Generated in < 5 seconds
- 400+ structural elements per scene
- PBR materials: concrete, steel, glass
- All elements clickable with property inspection

---

## Page 5: Cost Estimation

### Automated NT$ Cost Breakdown

| Category | Typical % | Example |
|----------|-----------|---------|
| Structure | 35-45% | RC frame, columns, slabs |
| Envelope | 15-20% | Curtain wall, exterior walls |
| MEP | 25-35% | HVAC, electrical, plumbing |
| Interior | 10-15% | Raised floor, ceiling, partitions |

### Key Features
- Real-time cost update on every modification
- NT$ formatting with comma separators
- Pie chart visualization
- Delta tracking for cost impact of changes

---

## Page 6: 4D Construction Schedule

### Gantt Chart + Timeline Animation

- **16 construction phases** with color coding
- **Timeline Slider**: scrub through construction sequence
- **Play/Pause** with speed control (1×/2×/5×/10×)
- **Click-to-seek**: click Gantt bar to jump to phase
- **Visual state**: solid=done, translucent=in-progress, gray=pending

### Phase Visibility in 3D
As the timeline advances, building elements appear in construction order — demonstrating the build sequence visually.

---

## Page 7: Modification & Delta Tracking

### Natural Language Modifications

Examples:
- *"Add a third floor"*
- *"Make the cleanroom larger"*
- *"Change exterior to curtain wall"*

### Delta Panel
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Cost | NT$ 85M | NT$ 102M | +NT$ 17M |
| GFA | 38,400 m² | 48,000 m² | +9,600 m² |
| Schedule | 540 days | 620 days | +80 days |

- Undo stack (max 10 entries)
- Color-coded: red=increase, green=decrease

---

## Page 8: UI/UX Polish

### Dark & Light Themes
- Press **T** to toggle
- All panels adapt automatically
- ThemeManager singleton with 15+ color tokens

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| F | Fit to view |
| 1-4 | Camera presets |
| T | Toggle theme |
| Ctrl+N | New scene |
| Ctrl+Q | Quit |

### Loading & Recovery
- Animated loading overlay during AI generation
- Branded splash screen on startup
- Auto-reconnect on Python crash (3 retries)

---

## Page 9: Technical Metrics

| Metric | Value |
|--------|-------|
| Language | C++17 / QML / Python 3.11 |
| Framework | Qt 6.11 Quick 3D |
| Rendering | Metal (macOS) |
| Build | CMake + Ninja |
| Protocol | JSON stdio (newline-delimited) |
| Heartbeat | 120s timeout + auto-restart |
| Materials | 4 PBR (concrete, glass, steel, wood) |
| Assets | 24 components / 7 categories |
| Scenes | 3 templates (Villa, Fab, DC) |
| C++ Tests | 18 passing |
| Python Tests | 27+ passing |
| E2E Scenarios | 6 (3 scenes × 2 operations) |
| Memory | < 500MB overhead per scene |

---

## Page 10: Roadmap & Next Steps

### MVP Complete (v0.1.0)
- Full prompt-to-BIM pipeline
- 3 demo scenes with cost + schedule
- Dark/Light theme + keyboard shortcuts
- Crash recovery + auto-reconnect

### Phase 2 Plans
- **USD Import/Export** with ILOS metadata (foundation ready)
- **Multi-user collaboration** via MCP protocol
- **Windows support** (DirectX/Vulkan)
- **IFC import** for existing BIM model integration
- **Cloud deployment** for team access
- **Revit/ArchiCAD plugin** for industry tool integration

### For TSMC
- Custom cleanroom templates with ISO class validation
- Vibration analysis integration
- Chemical resistance material database
- Fab-specific code compliance (TW-IND series)

---

*Zigma PromptToBuild v0.1.0 — TSMC Presentation v2.0*
*Confidential — For TSMC Facilities Division Only*
