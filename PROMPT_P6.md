# PROMPT_P6.md — Sprint P6: Cost Estimation (5D)

> Version: v1.0.0 | Created: 2026-03-25
> Previous Sprint: P5 ✅ Completed
> Dependencies: P2.5

## Environment Check

Execute the environment check script from CLAUDE.md. Confirm conda env `promptbim` exists and all dependencies can be imported.

## Required Reading
1. SKILL.md — Overall architecture
2. TODO.md — Confirm P6 task list
3. CLAUDE.md — Behavioral rules

## Task List for This Sprint

- ⬜ `bim/cost/qto.py` — IFC quantity takeoff (QTO)
- ⬜ `bim/cost/unit_prices_tw.py` — Taiwan unit price table
- ⬜ `bim/cost/estimator.py` — Cost calculation engine
- ⬜ `viz/cost_charts.py` — Pie chart / bar chart visualization
- ⬜ `gui/cost_panel.py` — GUI integration
- ⬜ Tests + xcodebuild pass

## Execution Instructions
All answers are Yes. Do not interrupt to ask questions.
Follow CLAUDE.md [MANDATORY] steps strictly before ending work.

## Acceptance Criteria
1. After building generation, automatically display estimated total cost + itemized pie chart
2. Cost breakdown by category (structure, MEP, finishes, etc.)
3. Taiwan market pricing (seed data from P2.5 component registry)
4. xcodebuild BUILD SUCCEEDED
5. pytest all pass
