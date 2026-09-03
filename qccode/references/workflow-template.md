# Q-C-Code Workflow Template

Every workflow `workflow.md` file should use this structure.

## Purpose

Describe the purpose of this stage.

## Triggered By

Describe what previous artifact or user command starts this workflow.

## Required Input

List required inputs.

## Optional Input

List optional inputs.

## Steps

List step files in execution order.

Example:

1. `01-read-inputs.md`
2. `02-do-stage-work.md`
3. `03-write-artifact.md`

## Required Output

List the artifact this workflow must write.

## Gates

List any required user approval or decision points.

If no gate is required, write:

```text
No user gate required unless required information is missing.
```

## Failure Behavior

Explain what to do if the stage cannot complete.

Examples:

- write a blocker note
- return to Questions
- return to Design Discussion
- ask user for one decision
- stop before modifying code

## Must Not

List things the workflow must not do.
