# Step: Write Implementation Artifact

## Purpose

Always write implementation-notes.md to summarize execution, changes, validation, and follow-up needs.

## Inputs

- Required:
  - `implementation-todos.md`
  - `parallelization.md`
  - Validation results from step 07
  - Slice results from step 05
- Repository context:
  - Read access to changed files for summary

## Actions

- Summarize changed files and their modifications
- Summarize execution mode (serial, parallel-partial, parallel-full)
- Summarize validation level and results
- List any deviations from the plan
- List any blockers encountered
- List any follow-up work needed
- Write `implementation-notes.md` following the artifact schema
- Update `run.md` status to complete, blocked, or partial
- Update `coordinator-log.md` with implementation completion

## Output

- `implementation-notes.md` (always written)
- Updated `run.md`
- Updated `coordinator-log.md`

## Must Not

- Do not skip this artifact.
- Do not omit validation status.
- Do not omit known blockers.
- Do not omit deviations from plan.
