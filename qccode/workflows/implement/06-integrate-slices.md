# Step: Integrate Slices

## Purpose

Serially integrate all slice outputs and ensure repository consistency.

## Inputs

- Required:
  - `implementation-todos.md`
  - `parallelization.md`
  - Slice result notes from step 05
- Repository context:
  - Read and write access to project files for integration
  - Exec access for integration validation

## Actions

- Review all changes from all slices
- Check imports and dependencies
- Check naming consistency across slices
- Check cross-file contracts and interfaces
- Resolve any conflicts between slices
- Ensure no file ownership violations occurred
- Perform final integration serially (coordinator must do this)
- Update `implementation-todos.md` with integration completion status
- Update `coordinator-log.md` with integration summary

## Output

- Integrated repository state
- Updated `implementation-todos.md`
- Updated `coordinator-log.md`

## Must Not

- Do not skip integration after parallel work.
- Do not assume child agent work is final.
- Do not ignore conflicting changes.
- Do not allow parallel agents to perform final integration.
