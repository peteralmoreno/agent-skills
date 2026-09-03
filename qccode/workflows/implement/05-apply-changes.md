# Step: Apply Changes

## Purpose

Perform serial setup and implementation slices according to the parallelization decision and slice assignments.

## Inputs

- Required:
  - `implementation-todos.md`
  - `parallelization.md`
  - `plan.md`
  - `worktree.md`
- Repository context:
  - Read and write access to project files for implementation
  - Exec access for validation commands

## Actions

- Perform serial setup tasks first (shared types, interfaces, configuration)
- If parallel mode is approved and tools are available:
  - Launch safe parallel subagents only for approved slices
  - Ensure each subagent stays within assigned file ownership
- Otherwise, execute all slices serially as coordinator
- Use Claude Code tools: read, edit, exec, grep, Glob
- Track progress using TodoWrite if available, or update implementation-todos.md
- Ensure each slice stays within its file ownership boundaries

## Output

- Changed files
- Slice result notes (from subagents or coordinator)
- Updated `implementation-todos.md` with completion status

## Must Not

- Do not let subagents modify unowned files.
- Do not expand implementation scope.
- Do not redesign architecture.
- Do not continue if plan is invalid (stop and return to Design Discussion or Structure).
