# Q-C-Code Structure Outline Workflow

## Purpose
Define the execution shape before implementation by outlining phases, dependencies, and validation strategy.

## Steps
1. **01-read-design.md** – Read design-discussion.md to understand design constraints and recommended direction
2. **02-define-structure.md** – Define execution shape, module boundaries, data flow, and phases
3. **03-present-structure.md** – Prepare structure options for coordinator approval with `AskUserQuestion`
4. **04-write-artifact.md** – Write structure.md with phases, dependencies, and validation approach

## Triggered By
Completion of design-discussion.md with a populated `Output for next stage` section.

## Required Input
- `design-discussion.md` — with design constraints from Design Discussion stage

## Optional Input
- `research.md` — for additional context on module boundaries and dependencies

## Output
- `structure.md` — with execution shape, phases, validation approach, and `Output for next stage`

## Gates
Review gate: If structure changes module boundaries, ownership, data contracts, or validation strategy in a non-obvious way, step 03 writes a `User-facing checkpoint` to the artifact and returns. The coordinator presents the structure with `AskUserQuestion` and records approval under `User checkpoint response`. The coordinator then relaunches Structure to complete step 04.

If structure is obvious and low-risk, step 03 is skipped.

## Rules
- **Review gate**: Ask for approval only when structure changes module boundaries, ownership, data contracts, or validation strategy meaningfully
- If structure is obvious and low-risk, record and continue without user interaction
- Define execution shape, not detailed implementation pseudocode
- Write structure.md with: affected modules, data flow, interfaces, ordered phases, dependency direction, test locations, validation approach
- Produce `Output for next stage`: structure definition that Plan must convert into tasks

## Failure Behavior
- If design-discussion.md is missing or contradictory: return to Design Discussion stage.
- If structure cannot be determined without user input: write the User-facing checkpoint and return to coordinator.

## Must Not
- Do not use `AskUserQuestion` directly — the coordinator does this.
- Do not invent new architecture when existing patterns fit.
- Do not create unnecessary abstractions.
- Do not sneak implementation details into the structure definition.
- Do not modify source code.
