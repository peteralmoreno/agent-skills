# Q-C-Code Plan Workflow

## Purpose
Convert the structure into small implementation slices with clear tasks, dependencies, and validation expectations.

## Steps
1. **01-read-structure.md** – Read structure.md to understand execution shape and phases
2. **02-create-tasks.md** – Convert structure into ordered tasks with dependencies and validation
3. **03-present-plan.md** – Prepare plan options for coordinator approval with `AskUserQuestion`
4. **04-write-artifact.md** – Write plan.md with tasks, dependencies, and first execution slice

## Triggered By
Completion of structure.md with a populated `Output for next stage` section.

## Required Input
- `structure.md` — with execution shape from Structure stage

## Optional Input
- `design-discussion.md` — for constraint cross-check
- `questions.md` — for original success criteria

## Output
- `plan.md` — with ordered tasks, file plan, validation expectations, first execution slice, and `Output for next stage`

## Gates
Review gate: Step 03 writes a `User-facing checkpoint` (plan summary table + first execution slice) to the artifact and returns. The coordinator presents the plan with `AskUserQuestion` and records the user's approval under `User checkpoint response`. The coordinator then relaunches Plan to complete step 04.

Exception: For truly tiny, mechanical changes (single-file, zero-risk), collapse the review gate and proceed directly to step 04 — record the reason in plan.md.

## Rules
- **Review gate**: Present plan summary and ask approval before Worktree unless user pre-approved implementation
- For truly tiny mechanical changes, record why review gate was collapsed
- Convert structure into small, independently reviewable steps
- Write plan.md with: ordered tasks, affected files, dependencies, validation expectations, rollback concerns, first execution slice
- Produce `Output for next stage`: worktree setup and first implementation slice

## Failure Behavior
- If structure.md is missing or too vague to create tasks: return to Structure stage.
- If user requests revisions at the review gate: incorporate feedback and rewrite plan.md before proceeding.

## Must Not
- Do not use `AskUserQuestion` directly — the coordinator does this.
- Do not create giant plans with hidden surprises.
- Do not combine unrelated concerns into single tasks.
- Do not hide risky or high-complexity work in the plan table.
- Do not modify source code.
