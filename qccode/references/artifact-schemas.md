# Q-C-Code Artifact Schemas

These schemas define the expected shape of stage artifacts. Keep artifacts concise. The goal is enough context for the next stage, not a full transcript.

---

## `run.md`

```md
# Q-C-Code Run

## Run ID

`<run-id>`

## User Request

<original user request>

## Current Stage

questions | research | design-discussion | structure | plan | worktree | implement | complete | blocked | archived

## Completed Stages

- questions
- research

## Next Stage

<next stage name>

## Status

active | blocked | complete | archived

## Last Updated

<timestamp if available, otherwise omit>

## Notes

<short operational notes>
```

---

## `coordinator-log.md`

```md
# Coordinator Log

## Run ID

`<run-id>`

## Timeline

- <stage>: <summary>

## Decisions

- <decision and source>

## Blockers

- <blocker or none>

## User Gates

- <gate requested>
- <user decision>
```

---

## `questions.md`

```md
# Questions Stage

## User Request

<original request>

## Known Facts

- <fact>

## Unknowns

- <unknown>

## User Answers

- <answer>

## Constraints

- <constraint>

## Decisions

- <decision>

## Output for Research

<brief handoff>
```

---

## `research.md`

```md
# Research Stage

## Summary

<brief summary>

## Relevant Files

- `<path>`: <why it matters>

## Current Behavior

<what the code currently does>

## Constraints Found

- <constraint>

## Risks

- <risk>

## Open Questions

- <question or none>

## Output for Design Discussion

<brief handoff>
```

---

## `design-discussion.md`

```md
# Design Discussion Stage

## Problem

<problem being solved>

## Options Considered

### Option A

<summary>

Pros:
- <pro>

Cons:
- <con>

### Option B

<summary>

Pros:
- <pro>

Cons:
- <con>

## Recommended Direction

<recommendation>

## User Decision

<decision or "not required">

## Output for Structure

<brief handoff>
```

---

## `structure.md`

```md
# Structure Stage

## Target Shape

<high-level structure>

## Files and Responsibilities

- `<path>`: <responsibility>

## Interfaces and Contracts

- <contract>

## Data Flow

<brief flow>

## Boundaries

- <boundary>

## Output for Plan

<brief handoff>
```

---

## `plan.md`

```md
# Plan Stage

## Implementation Goal

<goal>

## Task List

1. <task>
2. <task>

## File Plan

- `<path>`: <planned change>

## Test Plan

- <test or validation command>

## Risks

- <risk>

## User Gate

<approval status or "not required">

## Output for Worktree

<brief handoff>
```

---

## `worktree.md`

```md
# Worktree Stage

## Decision

use existing branch | create branch | create worktree | user declined

## Branch or Worktree

<branch/worktree information>

## Environment Notes

<notes>

## Gitignored Files

<none, documented only, or user-approved copies>

## Approval

<user approval if required>

## Output for Implement

<brief handoff>
```

---

## `implementation-todos.md`

```md
# Implementation Todos

## Execution Mode

serial | parallel-partial | parallel-full

## Serial Setup Tasks

- [ ] <task>

## Implementation Slices

### Slice A: <name>

Owner: <coordinator or subagent name>

Files:
- `<path>`

Tasks:
- [ ] <task>

Dependencies:
- <dependency or none>

### Slice B: <name>

Owner: <coordinator or subagent name>

Files:
- `<path>`

Tasks:
- [ ] <task>

Dependencies:
- <dependency or none>

## Serial Integration Tasks

- [ ] <task>

## Validation Tasks

- [ ] <task>
```

---

## `parallelization.md`

```md
# Parallelization Review

## Decision

serial | parallel-partial | parallel-full

## Reason

<why this decision was made>

## Safe Slices

- <slice and reason>

## Serial Slices

- <slice and reason>

## File Ownership

- `<path>`: <owner>

## Conflict Risks

- <risk or none>

## Execution Order

1. <step>
2. <step>

## Do Not Parallelize

- <items that must remain serial>
```

---

## `implementation-notes.md`

```md
# Implementation Notes

## Status

complete | blocked | partial | not-started

## Execution Mode

serial | parallel-partial | parallel-full

## Changed Files

- `<path>`: <summary>

## Validation

Level: 0 | 1 | 2 | 3 | 4

Commands:
- `<command>`: passed | failed | not run

## Deviations From Plan

- <deviation or none>

## Blockers

- <blocker or none>

## Follow-ups

- <follow-up or none>

## Output for User

<short final summary>
```
