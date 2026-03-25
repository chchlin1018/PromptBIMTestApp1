# PROMPT_P7.md — Sprint P7: MEP Auto Routing

> Version: v1.0.0 | Created: 2026-03-25
> Previous Sprint: P6 ✅ Completed
> Dependencies: P4

## Environment Check

Execute the environment check script from CLAUDE.md. Confirm conda env `promptbim` exists and all dependencies can be imported.

## Required Reading
1. SKILL.md — Overall architecture
2. TODO.md — Confirm P7 task list
3. CLAUDE.md — Behavioral rules
4. docs/addendum/02_sim_cost_mep.md — MEP technical spec (Module C)

## Task List for This Sprint

- ⬜ `bim/mep/pathfinder.py` — 3D orthogonal A* pathfinding
- ⬜ `bim/mep/systems.py` — MEP system definition templates
- ⬜ `bim/mep/planner.py` — AI MEP planner (equipment + terminal positioning)
- ⬜ `bim/mep/ifc_mep.py` + `usd_mep.py` — Dual IFC/USD output
- ⬜ `bim/mep/clash_detect.py` — Basic collision detection
- ⬜ `viz/mep_overlay.py` — Four-colour MEP 3D overlay
- ⬜ `gui/mep_toggle.py` — System show/hide toggle
- ⬜ Tests + xcodebuild pass

## Execution Instructions
All answers are Yes. Do not interrupt to ask questions.
Follow CLAUDE.md [MANDATORY] steps strictly before ending work.

## Acceptance Criteria
1. One-click "Auto MEP" generates four system pipe routes
2. 3D view shows colour-coded MEP overlaid on building (blue/red/green/yellow)
3. IFC output includes IfcDuctSegment / IfcPipeSegment / IfcCableCarrierSegment
4. USD output includes MEP geometry
5. Basic clash detection reports overlapping segments
6. xcodebuild BUILD SUCCEEDED
7. pytest all pass
