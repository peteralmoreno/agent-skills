# Step: Validate Changes

## Purpose

Validate implementation using the highest practical validation level available.

## Inputs

- Required:
  - `plan.md`
  - `implementation-todos.md`
- Repository context:
  - Exec access for validation commands
  - Read access to test files and build configuration

## Actions

- Choose highest practical validation level (0-4) based on environment availability
- Run targeted or full validation commands if available:
  - Level 2: Targeted tests, type check, lint against changed area
  - Level 3: Full project test, build, lint
  - Level 4: Manual runtime verification if possible
- Inspect failures and analyze root causes
- Decide whether to fix, document, or block based on severity
- If validation cannot be run, record as Level 0 or Level 1
- Document validation results for implementation-notes.md

## Output

- Validation notes for `implementation-notes.md` including:
  - Validation level (0-4)
  - Commands run and their results
  - Any failures and how they were handled

## Must Not

- Do not claim tests passed if not run.
- Do not hide validation failures.
- Do not perform major redesign to make validation pass (return to Design Discussion if needed).
