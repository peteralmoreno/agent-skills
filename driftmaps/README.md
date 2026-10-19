# DriftMaps

**A map shows possible routes. Nodes describe the work. A Trail records the real journey. A Handover carries the result.**

DriftMaps is a portable Agent Skill for creating, inspecting, and running reusable agent procedures without introducing a workflow engine. Maps use only Markdown and YAML for authoring, and a **Mermaid flowchart** in `MAP.md` for authoritative routing.

## Install

Copy the whole `driftmaps/` directory into a Skill discovery location supported by your agent:

```powershell
# Claude Code
Copy-Item -Recurse driftmaps "$env:USERPROFILE\.claude\skills\driftmaps"
# Codex / shared Agent Skills location
Copy-Item -Recurse driftmaps "$env:USERPROFILE\.agents\skills\driftmaps"
```

Use `/driftmaps`, `$driftmaps`, or ask your agent to use the DriftMaps Skill.

## Create and inspect a map

```bash
python3 driftmaps/scripts/driftmaps.py init --root /path/to/project
python3 driftmaps/scripts/driftmaps.py new burrito-cannon --root /path/to/project
python3 driftmaps/scripts/driftmaps.py list --root /path/to/project
python3 driftmaps/scripts/driftmaps.py validate /path/to/project/maps/burrito-cannon/MAP.md
python3 driftmaps/scripts/driftmaps.py inspect /path/to/project/maps/burrito-cannon/MAP.md
```

The `new` command creates a **draft** with `MAP.md`, `nodes/setup.md` and `nodes/work.md`; customize before use. No commands above execute the map.

## Prepare a run

```bash
python3 driftmaps/scripts/driftmaps.py start \
  /path/to/project/maps/burrito-cannon/MAP.md \
  --root /path/to/project \
  --input-file /path/to/inputs.yaml
```

This writes a `trail.yaml` in a unique `.driftmaps/runs/<run-id>/` folder. It **does not** execute the Map. The agent performs authorized nodes and updates Trail according to the [execution rules](references/execution.md).

## Consistent layout

```text
project/
├── maps/
│   └── burrito-cannon/
│       ├── MAP.md
│       └── nodes/
│           ├── setup.md
│           ├── prepare.md
│           ├── locate.md
│           ├── blast.md
│           └── notify.md
└── .driftmaps/                 # runtime data, Git ignored by default
    ├── runs/
    │   └── <run-id>/
    │       ├── trail.yaml
    │       ├── artifacts/
    │       ├── handover.yaml
    │       └── report.md
    └── memory/                # optional approved, durable lessons
```

Only the authored `MAP.md` and `nodes/` are required to define a Map. A real run produces a Trail and, at exit, a Handover and Report.

## Key contracts

- **MAP.md** — frontmatter with `name`, `version`, `status`, and `limits.max_transitions`. Its Mermaid graph is the one routing authority; no separate step aliases, `next`, or numbered filenames.
- **nodes/*.md** — YAML `requires` and `produces` lists, optional `tool_hints` and `max_visits`; flexible Markdown instructions.
- **trail.yaml** — `meta`, `current`, `context`, `artifacts`, `history`. Shared state and artifact pointers, never entire large documents.
- **handover.yaml** — `meta`, `result` (status/data/evidence/issues), `continuation`. An external handoff to user or another Map, not one file per node.
- **report.md** — human-facing summary with YAML frontmatter, generated after execution.

`pause` preserves resumable progress; `stop` records blocked or failed work; `complete` ends the graph without asserting business success. One node runs at a time. A global transition limit prevents infinite loops even across multi-node cycles; optional node visit limits apply locally.

## Optional human-facing HTML

For a polished interactive HTML graph and clickable nodes, install the **separate** `driftmap-presenter` Skill. It renders a read-only snapshot **only when requested**, and never replaces the Map source. It is not a runtime dependency.

## Example and tests

Read [the complete Burrito Cannon sample](examples/burrito-cannon/MAP.md), [format guide](references/format.md), and [execution guide](references/execution.md).

```bash
python3 -m unittest discover -s driftmaps/tests -v
```

This validates scaffolding and structural parsing. It does not test model reasoning, authenticate evidence, or send messages/launch anything.
