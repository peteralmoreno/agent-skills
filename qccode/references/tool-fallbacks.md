# Q-C-Code Tool Fallbacks

The skill may run in environments with different tools. Do not hard-lock the skill to one agent platform.

## User Questions

If a native structured question tool exists, use it.

Examples:

- `AskUserQuestion`
- equivalent structured approval/choice tool

If no structured question tool exists, ask in normal chat with numbered options.

## Todo Tracking

If a native todo tool exists, use it.

Examples:

- `TodoWrite`
- equivalent checklist tool

If no todo tool exists, maintain:

```text
.qccode/active/<run-id>/implementation-todos.md
```

## Subagents

If native subagent execution exists, use it only when helpful.

Examples:

- `Agent`
- returned `Agent` results
- equivalent child-agent system

If subagents are unavailable, execute stages directly while preserving artifact boundaries.

## Parallel Subagents

If parallel subagents are unavailable, use serial execution.

Do not fake parallel execution.

## File Search

If native semantic file search exists, use it.

If not, use repository search commands such as:

```bash
find .
grep -R
rg
```

Use whatever is available in the local environment.

## Git

If git is available, inspect branch status before worktree or branch changes.

If git is unavailable, write that limitation in `worktree.md` and continue only if safe.

## Validation

If commands cannot be run, record validation as Level 0 or Level 1 in `implementation-notes.md`.
