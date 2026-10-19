# Drift Map Presenter

An **optional Agent Skill** that makes interactive, human-readable HTML companion pages for Drift Maps.

The normal AI-facing map continues to consist of `MAP.md` plus the files in `nodes/`. A presentation is only generated on request. No renderer or browser is required to **run** a Drift Map through its agent.

## Quickstart

From the root of the `agent-skills` repository:

```bash
python3 driftmap-presenter/scripts/render_map.py \
  driftmap-presenter/examples/burrito-cannon/MAP.md \
  --out /tmp/burrito-overview.html
```

Open the generated HTML in a normal browser. It has an interactive graph, selectable nodes, a route explorer that **simulates navigation without doing any work**, and human-readable guidance. It makes no network requests.

For a real map, the default output is a sibling `overview.html`:

```bash
python3 driftmap-presenter/scripts/render_map.py \
  /path/to/maps/my-map/MAP.md
```

If a generated HTML already exists and you want to replace it, inspect it first, then pass `--force`. The source map and nodes are never modified by the command.

## Install

Copy the entire `driftmap-presenter/` folder to a supported Agent Skills discovery path:

```powershell
# Claude Code
Copy-Item -Recurse driftmap-presenter "$env:USERPROFILE\.claude\skills\driftmap-presenter"

# Portable / Codex Agent Skills location
Copy-Item -Recurse driftmap-presenter "$env:USERPROFILE\.agents\skills\driftmap-presenter"
```

Invoke with `/driftmap-presenter` when supported, or ask your agent to *use the Drift Map Presenter skill to make a human-facing view*. This Skill is independent of PRISM, LENS, GitHub and noMoreDrift runtimes.

## Example structure

```text
maps/
  burrito-cannon/
    MAP.md
    nodes/
      setup.md
      prepare.md
      locate.md
      blast.md
      notify.md
    overview.html    # OPTIONAL, generated only on request
```

## Why this is separate

| Artifact | Audience | Authority |
| --- | --- | --- |
| `MAP.md` and `nodes/*.md` | Agents and authors | Authoritative execution map and instructions |
| `overview.html` | People viewing/reviewing the process | Read-only derived presentation |
| `trail.yaml` and `handover.yaml` | Execution tools and downstream consumers | Actual run state and output; **not** needed to display the authored map |

The HTML is a snapshot. Refresh it after source changes when the user wants an up-to-date display. Never treat an interactive walkthrough as an actual execution.

## Implementation scope

The generator uses the Python standard library and a bundled HTML/CSS/JS template. It supports only the documented Mermaid subset and a basic *safe* Markdown renderer. Fancy Mermaid structures or advanced Markdown features may require custom presentation work; unsupported routes are rejected rather than being guessed.

No CDN, server, iframe, remote API, database, or workflow engine is required. The HTML is responsive and supports mouse/keyboard selection and route exploration.

Run tests:

```bash
python3 -m unittest discover -s driftmap-presenter/tests -v
```

See [design notes](references/design.md) for fidelity, security, accessibility, and scope.
