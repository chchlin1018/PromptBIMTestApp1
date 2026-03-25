# PROMPT_P5.md — Sprint P5: Voice Input + Export

> Version: v1.0.0 | Created: 2026-03-25
> Previous Sprint: P4.8 ✅ Completed
> Dependencies: P4

## Environment Check

Execute the environment check script from CLAUDE.md. Confirm conda env `promptbim` exists and all dependencies can be imported.

## Required Reading
1. SKILL.md — Overall architecture
2. TODO.md — Confirm P5 task list
3. CLAUDE.md — Behavioral rules

## Task List for This Sprint

- ⬜ `voice/stt.py` — faster-whisper local speech recognition
- ⬜ Voice button integration into Chat panel
- ⬜ Export dialog (IFC + USD + SVG + JSON one-click package)
- ⬜ `viz/floorplan.py` — per-floor plan SVG generation
- ⬜ Tests + xcodebuild pass

## Execution Instructions
All answers are Yes. Do not interrupt to ask questions.
Follow CLAUDE.md [MANDATORY] steps strictly before ending work.

## Acceptance Criteria
1. Voice description → complete generation → one-click export 5-piece set
2. SVG floor plans for each story
3. xcodebuild BUILD SUCCEEDED
4. pytest all pass
