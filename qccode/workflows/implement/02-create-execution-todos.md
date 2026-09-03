# Step: Create Execution Todos

## Purpose

Create the implementation-todos.md artifact before any code changes begin, converting the plan into executable tasks.

## Inputs

- Required:
  - `plan.md`
  - `structure.md`
- Repository context:
  - Read access to project files to identify implementation targets

## Actions

- Convert `plan.md` task list into executable implementation tasks
- Identify files likely to be changed based on plan and structure
- Group tasks by file or responsibility for potential parallelization
- Mark unknown file ownership as a risk in the todos
- Create initial `implementation-todos.md` with:
  - Execution mode (default to serial)
  - Serial setup tasks
  - Implementation slices (if parallelization is being considered)
  - Serial integration tasks
  - Validation tasks

## Output

- Write `implementation-todos.md`

## Must Not

- Do not modify source code yet.
- Do not launch subagents yet.
- Do not finalize parallelization decisions yet.
