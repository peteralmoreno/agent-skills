# Q-C-Code Parallel Implementation Policy

Parallel implementation is allowed only as a controlled optimization.

It is not the default.

The coordinator is responsible for deciding whether the implementation can be parallelized.

## Required Review

Before modifying code, the implementation workflow must create or update:

```text
parallelization.md
implementation-todos.md
```

## Safe Conditions for Parallel Work

Parallel subagents may be used only when all of these are true:

- each slice has exclusive file ownership
- required interfaces are already defined
- slices do not depend on unfinished work from other slices
- each subagent has a narrow task
- each subagent has a clear file list
- each subagent has a clear output requirement
- final integration is performed serially by the coordinator

## Hard Rule

No two parallel subagents may modify the same file.

If two slices need the same file, do one of these:

1. merge the slices
2. make the shared edit first as a serial setup task
3. define the shared interface first, then parallelize dependent work

## Usually Safe to Parallelize

Parallel work is usually safer when slices touch:

- different files
- different directories
- different layers
- independent tests
- documentation separate from code
- isolated UI components
- isolated service methods
- isolated test files

## Usually Unsafe to Parallelize

Do not parallelize changes to:

- shared types
- public interfaces
- API contracts
- database schema
- migrations
- package/dependency configuration
- routing files
- central configuration files
- test setup files
- build configuration
- authentication contracts
- shared utilities used by multiple slices

These may be handled as serial setup tasks before parallel work begins.

## Required Execution Pattern

Use this pattern:

1. read inputs
2. create implementation todos
3. review parallelization opportunities
4. perform required serial setup
5. launch only safe parallel slices
6. collect subagent outputs
7. perform serial integration
8. run validation
9. write implementation notes

## Subagent Output Contract

Each parallel subagent must report:

```md
# Slice Result

## Slice

<slice name>

## Files Changed

- `<path>`: <summary>

## Tasks Completed

- <task>

## Validation

<commands run or not run>

## Risks

<risk or none>

## Handoff Notes

<notes for integration>
```

## Coordinator Integration

The coordinator must review all slice outputs.

The coordinator must check for:

- overlapping file changes
- missing tasks
- inconsistent naming
- broken imports
- test failures
- contract drift

The coordinator performs final integration serially.

Child agents do not decide the final repository state.
