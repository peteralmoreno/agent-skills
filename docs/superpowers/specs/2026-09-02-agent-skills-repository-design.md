# Agent Skills Repository Design

## Purpose

Create a public GitHub repository at `peteralmoreno/agent-skills` that publishes two reusable agent skills without exposing local history, backups, credentials, or machine-specific state:

- `qccode`: the authoritative Claude Code Q-C-Code/QRSPI workflow currently stored under `~/.claude/skills/qccode`.
- `prism`: a new portable skill based on the standalone PRISM framework: Problem, Requirements, Invariants, Solution, and Measures.

## Repository shape

```text
agent-skills/
|-- README.md
|-- LICENSE
|-- qccode/
|   |-- SKILL.md
|   |-- agents/
|   |-- references/
|   |-- workflows/
|   `-- CHANGELOG.md
|-- prism/
|   |-- SKILL.md
|   |-- agents/
|   |-- references/
|   `-- tests/
`-- docs/superpowers/
    |-- specs/
    `-- plans/
```

The repository will use the MIT License, matching Peter Moreno's existing public skill-oriented work. The root README will explain the purpose, compatibility, installation, and validation commands for each skill.

## Q-C-Code package

Copy the current `C:\Users\peter\.claude\skills\qccode` tree without copying the timestamped backup. Preserve its Claude-specific behavior and metadata, including its hierarchical sub-agent workflows and `AskUserQuestion` conventions.

Do not claim that this package is natively portable to Codex. Its `argument-hint` frontmatter and Claude tool names are intentionally Claude-specific. The README will state that limitation clearly.

Before publication:

- verify every referenced Markdown file exists;
- verify every workflow stage contains `workflow.md`;
- scan for credential values, local absolute paths, and generated run artifacts;
- document the Codex validator's expected `argument-hint` warning rather than silently changing the source contract.

## PRISM package

Build `prism` as a concise, cross-runtime skill rather than renaming the existing `spec-writer` skill. The standalone `PRISM_Spec_Framework.md` remains the source of truth because `spec-writer` uses a different six-stage interview and does not identify itself as PRISM.

The skill will support three modes:

- Explain: teach the five PRISM views and traceability.
- Build: turn a vague request into a PRISM specification, confirming uncertain content rather than inventing it.
- Review: evaluate an existing specification for missing or disconnected PRISM elements and propose revisions.

The output contract will contain Problem, numbered Requirements, numbered Invariants, numbered Solution decisions, numbered Measures, and a traceability section connecting each important requirement to its protections, solution decisions, and evidence.

The complete framework text will live in `prism/references/prism-spec-framework.md`. `SKILL.md` will stay focused on triggers, mode selection, workflow, output contract, and safety boundaries. `agents/openai.yaml` will provide portable UI metadata.

## Testing and validation

PRISM will be developed test-first:

1. Record baseline agent behavior on realistic ambiguous-spec and review scenarios without the new skill.
2. Add contract tests that fail until the required PRISM structure and metadata exist.
3. Implement the smallest skill and reference material that satisfy those contracts.
4. Run forward scenarios with the skill and record the observed improvement.

Both packages will run through the Codex skill validator where applicable. PRISM must pass cleanly. Q-C-Code must pass all structural checks, with its known Claude-specific frontmatter difference reported separately. All automated tests must pass before publication.

## Publication workflow

Create one initial commit containing the design, both skill packages, root documentation, license, and tests. Create the public GitHub repository `peteralmoreno/agent-skills`, set it as `origin`, push `main`, and verify the remote commit and public repository contents.

No source files in the original Claude or study-card folders will be modified or deleted.

## Success criteria

- The public repository is reachable as `https://github.com/peteralmoreno/agent-skills`.
- `qccode/` matches the authoritative live Claude skill and excludes the backup.
- `prism/` accurately implements the five-view PRISM framework rather than the unrelated six-stage Spec Writer model.
- PRISM's contract tests and skill validation pass.
- Q-C-Code's references and workflow entrypoints resolve, and its Claude-specific compatibility note is visible.
- The published tree contains no secrets, session data, run artifacts, or machine-specific absolute paths.
