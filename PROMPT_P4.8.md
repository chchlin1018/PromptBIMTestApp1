# PROMPT_P4.8.md — Sprint P4.8: Interactive Modification Engine

> Version: v1.0.0 | Created: 2026-03-25
> Previous Sprint: P4.5 ✅ Completed
> Dependencies: P4

## Environment Check

Execute the environment check script from CLAUDE.md. Confirm conda env `promptbim` exists and all dependencies can be imported.

## Required Reading
1. SKILL.md — Overall architecture
2. TODO.md — Confirm P4.8 task list
3. CLAUDE.md — Behavioral rules

## Task List for This Sprint

- ⬜ `agents/modifier.py` — Modifier Agent (Claude analyzes modification intent)
- ⬜ Impact propagation matrix logic
- ⬜ Version history + diff comparison (ModificationRecord)
- ⬜ GUI: modification impact summary panel + confirm/undo
- ⬜ Incremental recalculation (only recalculate affected parts)
- ⬜ Tests + xcodebuild pass

## Execution Instructions
All answers are Yes. Do not interrupt to ask questions.
Follow CLAUDE.md [MANDATORY] steps strictly before ending work.

## Acceptance Criteria
1. User says "change to 9 stories" → instant update of all related data + show comparison
2. Modification history with undo capability
3. Impact propagation shows affected items
4. xcodebuild BUILD SUCCEEDED
5. pytest all pass
