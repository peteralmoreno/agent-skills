# Q-C-Code Run State Policy

## Scratch Path

Use:

```text
.qccode
```

Do not use:

```text
.devin/qccode
~/.claude/qccode
```

## Active Runs

Active runs live at:

```text
.qccode/active/<run-id>/
```

## Archived Runs

Archived runs live at:

```text
.qccode/archive/<run-id>/
```

## Required Run Manifest

Every run must have:

```text
run.md
```

The `run.md` file is the source of truth for:

- user request
- current stage
- completed stages
- next stage
- status

## Continue Behavior

When the user says:

```text
qccode continue
```

or:

```text
qccode continue <keyword>
```

follow this process:

1. Search `.qccode/active/`.
2. Inspect folder names and `run.md` files.
3. If there is exactly one matching active run, resume it.
4. If there are multiple matches, show a numbered list and ask the user to choose.
5. If there are no matches, say no active run was found.
6. Never guess between multiple active runs.

## List Behavior

When the user says:

```text
qccode list
```

show active runs from `.qccode/active/`.

For each run, show:

- run id
- status
- current stage
- short user request
- next stage

## Clear and Archive Behavior

Prefer archive over delete.

When the user says:

```text
qccode archive <run-id>
```

move the run from:

```text
.qccode/active/<run-id>/
```

to:

```text
.qccode/archive/<run-id>/
```

When the user says:

```text
qccode clear <run-id>
```

ask for confirmation before deleting.

When the user says:

```text
qccode clear all
```

ask for confirmation before deleting anything.

Never delete active run folders without explicit confirmation.
