# Q-C-Code Step Template

Every step file should use this structure.

## Purpose

State what this step is responsible for.

## Inputs

List the artifacts, files, or context this step may read.

Use this format:

- Required:
  - `<artifact-name>.md`
- Optional:
  - `<optional-artifact>.md`
- Repository context:
  - specific files, directories, tests, or commands allowed for this step

## Actions

List the actions the agent should perform.

Use concrete verbs.

Examples:

- read
- inspect
- summarize
- identify
- compare
- write
- validate

## Output

State exactly what this step must produce or update.

Examples:

- update `coordinator-log.md`
- write `research.md`
- produce candidate implementation slices
- update `implementation-todos.md`

## Must Not

List actions this step must not perform.

Examples:

- Do not modify source code.
- Do not ask the user unless required information is missing.
- Do not redesign architecture.
- Do not expand implementation scope.
- Do not copy secrets.
