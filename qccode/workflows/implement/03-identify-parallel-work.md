# Step: Identify Parallel Work

## Purpose

Decide whether implementation should be serial or parallel based on file ownership and safety constraints.

## Inputs

- Required:
  - `implementation-todos.md`
  - `plan.md`
  - `structure.md`
- Repository context:
  - Read access to project files to assess dependencies

## Actions

- Inspect planned file changes from implementation-todos.md
- Identify independent file-owned slices that could run in parallel
- Identify shared files that require serial handling
- Identify serial setup tasks (shared types, interfaces, configuration)
- Classify execution mode as:
  - `serial` (default, safest)
  - `parallel-partial` (some safe parallel work)
  - `parallel-full` (all work can be parallelized)
- Apply hard rule: no two parallel slices may own the same file
- Document the decision and reasoning

## Output

- Write `parallelization.md` with decision, reasoning, safe slices, serial slices, file ownership, and conflict risks

## Must Not

- Do not parallelize by default.
- Do not allow two slices to own the same file.
- Do not parallelize shared contracts unless serial setup defines them first.
