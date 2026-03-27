# Zigma PromptToBuild — Demo Script v2.0

> **Version:** v2.0 (Qt Quick 3D Edition) | **Duration:** 7 minutes
> **Platform:** macOS (Metal) | **Build:** mvp-v0.1.0

---

## 0:00–0:30 — Opening & Splash

1. Launch `ZigmaApp` — Splash screen with Zigma branding appears
2. App loads into dark-themed 3D workspace
3. Point out: **3-panel layout** (Chat | 3D Viewport | Properties)

> "Zigma is an AI-powered BIM platform. You describe what you want in natural language, and it generates a complete building model."

---

## 0:30–1:30 — Scene 1: Villa with Pool (S1)

1. Click **Scenes** tab → Select **S1 Villa** (30×40m)
2. Loading overlay appears: "Generating..."
3. 3D model renders with walls, slabs, columns, roof
4. **Rotate** the model (mouse drag), **zoom** (scroll)
5. Press **1-4** keys to switch views (Perspective / Top / Front / Right)
6. Press **F** to fit-to-view
7. Click a wall → **Properties panel** shows type, material, dimensions

> "In under 5 seconds, we have a complete 2-story villa with structural columns, slabs, and a flat roof."

---

## 1:30–2:30 — Cost & Schedule

1. Click **Cost** tab → Pie chart shows breakdown (Structure / Envelope / MEP / Interior)
2. Point out **total cost in NT$** with comma formatting
3. Click **Schedule** tab → Gantt chart with 16 phases
4. Click **Play** → 4D timeline animation shows construction sequence
5. Adjust speed: **1× → 5× → 10×**
6. Click on a Gantt bar → timeline jumps to that phase

> "Cost estimation and construction scheduling are generated automatically. The 4D timeline shows exactly when each phase starts."

---

## 2:30–3:30 — Modification (Delta)

1. Type in Chat: *"Add a third floor"*
2. Loading overlay → model updates with 3F added
3. Click **Delta** tab → shows cost/GFA changes
4. Compare before/after values

> "Any modification is instantly reflected in the 3D model, cost, and schedule. The delta panel tracks all changes."

---

## 3:30–4:30 — Scene 2: TSMC Fab (S2)

1. Click **Scenes** tab → Select **S2 TSMC Fab** (120×80m)
2. 4-story fabrication facility generates with cleanroom spaces
3. Switch to **Top** view (press **2**)
4. Point out element count in status bar
5. Click elements to inspect properties

> "This is a semiconductor fabrication plant. 4 stories including basement, with cleanroom spaces and industrial-grade structural design."

---

## 4:30–5:30 — Scene 3: Data Center (S3)

1. Select **S3 Data Center** (80×60m)
2. 3-story facility with server rooms
3. Check **Cost** tab → larger budget for MEP
4. Check **Schedule** → longer timeline for specialized construction

> "A 3-story data center with server halls on each floor. Note the higher MEP costs and specialized construction schedule."

---

## 5:30–6:15 — Theme & UI Polish

1. Press **T** → toggle to **Light theme**
2. Show all panels adapt to light colors
3. Press **T** again → back to dark theme
4. Open **Assets** tab → browse 24 components across 7 categories
5. Search for "steel" → filtered results

> "The interface supports both dark and light themes. The asset browser lets you explore all available building components."

---

## 6:15–7:00 — Architecture & Closing

1. Show **StatusBar**: connection status, progress indicator
2. Explain architecture:
   - **Qt Quick 3D** with Metal rendering on macOS
   - **Python AI backend** connected via JSON stdio protocol
   - **Crash recovery**: if Python crashes, auto-reconnect with 3 retries
3. Final message in Chat: *"Thank you for watching!"*

> "Zigma runs on Qt6 Quick 3D with Metal acceleration. The Python AI backend communicates via a JSON protocol with automatic crash recovery. This is version 0.1.0 — our MVP foundation for the full BIM platform."

---

## Key Stats

| Metric | Value |
|--------|-------|
| Build System | CMake + Ninja + Qt 6.11 |
| Rendering | Qt Quick 3D / Metal (macOS) |
| AI Protocol | JSON stdio (QProcess) |
| Scenes | 3 templates (Villa, Fab, DC) |
| Assets | 24 components / 7 categories |
| C++ Tests | 18 (7 AgentBridge + 11 BIM) |
| Python Tests | 27+ (unit + E2E) |
| Lines of Code | ~4,000 (C++ + QML + Python) |

---

*Zigma PromptToBuild v0.1.0 — Demo Script v2.0*
