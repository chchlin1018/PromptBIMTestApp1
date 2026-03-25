# PROMPT_P4.5.md — Sprint P4.5: Taiwan Building Code Engine

> Version: v1.0.0 | Created: 2026-03-25
> Previous Sprint: P4 ✅ Completed
> Dependencies: P4

## Environment Check

Execute the environment check script from CLAUDE.md. Confirm conda env `promptbim` exists and all dependencies can be imported.

## Required Reading
1. SKILL.md — Overall architecture
2. TODO.md — Confirm P4.5 task list
3. CLAUDE.md — Behavioral rules
4. docs/addendum/03_tw_building_codes.md — Taiwan building code specifications

## Task List for This Sprint

- ⬜ `codes/base.py` — BaseRule + CheckResult + Severity
- ⬜ `codes/tw_building_code.py` — BCR/FAR/height/stairs/corridor/elevator/parking
- ⬜ `codes/tw_seismic_code.py` — Seismic zone table + structural estimation rules
- ⬜ `codes/tw_fire_code.py` — Fire compartment/egress distance/safety stairs
- ⬜ `codes/tw_accessibility_code.py` — Accessibility facilities
- ⬜ `codes/tw_zoning_data.py` — County/city zone BCR/FAR JSON data
- ⬜ `codes/registry.py` — Rule registration + batch check
- ⬜ `codes/report.py` — Compliance report JSON + table
- ⬜ Integrate into Checker Agent + Planner prompt
- ⬜ Tests + xcodebuild pass

## Execution Instructions
All answers are Yes. Do not interrupt to ask questions.
Follow CLAUDE.md [MANDATORY] steps strictly before ending work.

## Acceptance Criteria
1. After building generation, automatically run 15+ building code checks
2. Output compliance report with pass/fail per rule
3. Checker Agent uses real Taiwan building codes for suggestions
4. xcodebuild BUILD SUCCEEDED
5. pytest all pass
