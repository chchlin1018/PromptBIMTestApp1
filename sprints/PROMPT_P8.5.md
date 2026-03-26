# PROMPT_P8.5.md — Sprint P8.5: Smart Monitoring Auto-Placement

> Version: v1.0.0 | Created: 2026-03-25
> Previous Sprint: P8 ✅ Completed
> Dependencies: P4, P7

## Environment Check

Execute the environment check script from CLAUDE.md. Confirm conda env `promptbim` exists and all dependencies can be imported.

## Required Reading
1. SKILL.md — Overall architecture
2. TODO.md — Confirm P8.5 task list
3. CLAUDE.md — Behavioral rules
4. docs/addendum/02_sim_cost_mep.md — Reference for sensor types

## Task List for This Sprint

- ⬜ `bim/monitoring/monitor_types.py` — 48 sensor/actuator type definitions
- ⬜ `bim/monitoring/auto_placement.py` — Automatic placement algorithm
- ⬜ `bim/monitoring/rules_engine.py` — Placement density rules
- ⬜ `bim/monitoring/ifc_monitor.py` — IFC IfcSensor/IfcActuator output
- ⬜ `bim/monitoring/usd_monitor.py` — USD monitor: namespace output (IDTF)
- ⬜ `bim/monitoring/dashboard_data.py` — Dashboard JSON export
- ⬜ `gui/monitor_toggle.py` — 3D monitoring point show/hide toggle
- ⬜ Monitoring cost integration into 5D estimation
- ⬜ Tests + xcodebuild pass

## Execution Instructions
All answers are Yes. Do not interrupt to ask questions.
Follow CLAUDE.md [MANDATORY] steps strictly before ending work.

## Acceptance Criteria
1. One-click "Auto Monitor" places all sensor types
2. 3D view shows monitoring points with toggle
3. IFC + USD contain monitoring entities
4. Dashboard JSON export with sensor list
5. Monitoring costs added to 5D estimate
6. xcodebuild BUILD SUCCEEDED
7. pytest all pass
