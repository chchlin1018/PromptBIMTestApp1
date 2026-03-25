# PROMPT_P8.md — Sprint P8: Construction Simulation (4D)

> Version: v1.0.0 | Created: 2026-03-25
> Previous Sprint: P7 ✅ Completed
> Dependencies: P2

## Environment Check

Execute the environment check script from CLAUDE.md. Confirm conda env `promptbim` exists and all dependencies can be imported.

## Required Reading
1. SKILL.md — Overall architecture
2. TODO.md — Confirm P8 task list
3. CLAUDE.md — Behavioral rules
4. docs/addendum/02_sim_cost_mep.md — Construction simulation spec (Module A)

## Task List for This Sprint

- ⬜ `bim/simulation/construction_phases.py` — Construction phase templates
- ⬜ `bim/simulation/scheduler.py` — AI scheduling (phase assignment + duration)
- ⬜ `bim/simulation/animator.py` — PyVista 4D animation engine
- ⬜ `viz/gantt_chart.py` — Gantt chart (matplotlib)
- ⬜ `gui/simulation_tab.py` — Timeline slider + play/pause + Gantt panel
- ⬜ Export GIF animation
- ⬜ Tests + xcodebuild pass

## Execution Instructions
All answers are Yes. Do not interrupt to ask questions.
Follow CLAUDE.md [MANDATORY] steps strictly before ending work.

## Acceptance Criteria
1. Drag timeline slider to see construction progress in 3D
2. Gantt chart syncs with 3D view (active phase highlighted)
3. Play/pause button auto-advances timeline
4. GIF export of construction animation
5. xcodebuild BUILD SUCCEEDED
6. pytest all pass
