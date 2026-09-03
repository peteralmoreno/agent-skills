# Step: Read Implementation Inputs

## Purpose

Read the plan, worktree, structure, and research artifacts to understand the implementation context before making any code changes.

## Inputs

- Required:
  - `plan.md`
  - `worktree.md`
  - `structure.md`
  - `run.md`
- Optional:
  - `research.md` (if needed for additional context)
- Repository context:
  - Read access to project files mentioned in plan
  - Read access to worktree/branch configuration

## Actions

- Read `plan.md` to understand implementation goals, task list, file plan, and validation requirements
- Read `worktree.md` to understand execution environment, branch/worktree setup, and gitignored file handling
- Read `structure.md` to understand target code structure, interfaces, and boundaries
- Read `run.md` to confirm current run state and stage
- Confirm environment is ready for implementation
- Identify any missing required information

## Output

- Update `coordinator-log.md` with implementation start and context summary
- Report any blockers or missing information

## Must Not

- Do not modify source code.
- Do not launch subagents.
- Do not ask user unless required artifacts are missing.
