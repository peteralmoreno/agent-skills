# Q-C-Code Validation Levels

Use validation levels in `implementation-notes.md`.

## Level 0: Not Run

No validation was run.

Use when:

- commands are unavailable
- environment is missing
- implementation did not start
- user explicitly skipped validation

## Level 1: Static Inspection

The agent inspected files, imports, syntax, or obvious logic manually.

No automated command was run.

## Level 2: Targeted Validation

A targeted test, type check, lint, or build command was run against the changed area.

Examples:

```bash
npm test -- auth
pytest tests/test_auth.py
npm run lint -- src/components/LoginPanel.tsx
```

## Level 3: Full Project Validation

A full project validation command was run.

Examples:

```bash
npm test
npm run build
npm run lint
pytest
mvn test
```

## Level 4: Manual Runtime Verification

The implementation was manually exercised in a running app or service.

Examples:

- started app locally
- tested affected UI flow
- called endpoint
- verified expected runtime behavior

## Required Reporting

Always report:

```md
## Validation

Level: <0-4>

Commands:
- `<command>`: passed | failed | not run

Notes:
<brief notes>
```

Do not claim validation passed if it was not run.
