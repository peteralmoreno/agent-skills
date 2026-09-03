# Step: Assign Implementation Slices

## Purpose

Assign work slices to coordinator or subagents with clear file ownership and dependencies.

## Inputs

- Required:
  - `implementation-todos.md`
  - `parallelization.md`
- Repository context:
  - Read access to project files for slice boundaries

## Actions

- Update `implementation-todos.md` with slice owners (coordinator or subagent names)
- Include explicit file ownership for each slice
- Include dependencies between slices
- Include validation expectation per slice
- If parallel mode is approved, prepare child-agent task prompts with:
  - Clear file list
  - Narrow task scope
  - Clear output requirements
  - File ownership constraints
- Ensure no vague or open-ended subagent assignments

## Output

- Updated `implementation-todos.md` with owners and assignments
- Child-agent task prompts if parallel mode is used

## Must Not

- Do not assign the same file to multiple parallel owners.
- Do not launch vague subagents.
- Do not assign architecture decisions to child agents.
