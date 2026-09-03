# Q-C-Code Implement Workflow

## Purpose
Execute implementation using controlled parallelization when safe, with serial integration and always-written implementation notes.

## Triggered By
Completion of Worktree stage with approved plan and execution environment.

## Required Input
- `plan.md` - Implementation tasks and file plan
- `worktree.md` - Execution environment and policy
- `structure.md` - Code structure and interfaces
- `run.md` - Current run state

## Optional Input
- `research.md` - Additional context if needed

## Steps
1. **01-read-inputs.md** – Read plan, worktree, structure, and run artifacts to understand context
2. **02-create-execution-todos.md** – Create implementation-todos.md before code changes begin
3. **03-identify-parallel-work.md** – Decide serial vs parallel execution and write parallelization.md
4. **04-assign-implementation-slices.md** – Assign slices to coordinator or subagents with file ownership
5. **05-apply-changes.md** – Perform serial setup and implementation slices
6. **06-integrate-slices.md** – Serially integrate all slice outputs
7. **07-validate-changes.md** – Validate implementation at highest practical level
8. **08-write-artifact.md** – Always write implementation-notes.md

## Required Output
- `implementation-notes.md` - Always written with execution summary
- `implementation-todos.md` - Created before code changes
- `parallelization.md` - Created when reviewing parallelization opportunities

## Gates
No user gate required unless plan is invalid or blockers are encountered.

## Failure Behavior
- If plan is invalid, stop and return to Design Discussion or Structure stage
- If blockers are encountered, document in implementation-notes.md and update run.md status to blocked
- If validation fails, attempt fixes or document and ask user for guidance

## Must Not
- Do not let parallel subagents modify the same file
- Do not skip serial integration after parallel work
- Do not redesign architecture during implementation
- Do not skip writing implementation-notes.md
- Do not claim validation passed if not run