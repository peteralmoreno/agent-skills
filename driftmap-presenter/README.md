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

The Python CLI uses PyYAML for safe, consistent YAML parsing. Install it once:

```bash
python3 -m pip install -r driftmap-presenter/requirements.txt
```


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

The generator uses PyYAML plus the Python standard library and a bundled HTML/CSS/JS template. The generated HTML itself has no dependencies. It supports only the documented Mermaid subset and a basic *safe* Markdown renderer. Fancy Mermaid structures or advanced Markdown features may require custom presentation work; unsupported routes are rejected rather than being guessed.

No CDN, server, iframe, remote API, database, or workflow engine is required. The HTML is responsive and supports mouse/keyboard selection and route exploration.

Run tests:

```bash
python3 -m unittest discover -s driftmap-presenter/tests -v
```

See [design notes](references/design.md) for fidelity, security, accessibility, and scope.

Both Skills bundle an identical `scripts/map_format.py` so each remains independently installable. Keep the copies synchronized; the regression tests check their equality when both packages are present.

## Optional styles

The existing dark presentation remains the default. Choose `--style morrito` for a bright, game-inspired presentation: sky-blue header, cream panels, bold black borders and offset shadows, yellow highlights, small stars with eyes for important notes, question blocks for uncertainty notes, horizontal green/orange/red route pipes, and a continuous hills/grass/earth footer. Typography uses local system fonts; there are no remote assets.

```bash
python3 driftmap-presenter/scripts/render_map.py path/to/MAP.md --style morrito --out morrito.html
```

Styles change presentation only. Routing, instructions, and attempt limits come from the same source map. All styles produce one standalone HTML file.

Use `--style gilded` for a tactical-RPG-inspired alternative: a parchment title screen, muted stone-and-sage panels, thin beveled borders, dark violet buttons with gold lettering, and a prominent gold attempt-limit panel. It uses local fonts, CSS ornamentation, and an embedded generated bird mascot, with no remote assets.

```bash
python3 driftmap-presenter/scripts/render_map.py path/to/MAP.md --style gilded --out gilded.html
```

In Markdown lists, start a bullet with `Important:` or `Uncertain:` to give it the corresponding Morrito icon. The words remain visible and readable to agents; the Presenter does not guess which instructions are important or uncertain. The attempt-limit heading also receives a small star. Pipes decorate existing route choices and do not add routes.

Gilded pairs a sword with the workflow heading, an original yellow riding-bird mascot with the route explorer, and a magic wand with the map guidance. These embedded decorative icons accompany text labels and do not change execution.

## Retry example

`examples/retry-check/MAP.md` demonstrates a ten-attempt node, explicit important/uncertain notes, and success/retry/stop routes. Generate any of the three styles from the same source:

```bash
python3 driftmap-presenter/scripts/render_map.py driftmap-presenter/examples/retry-check/MAP.md --style morrito --out retry-morrito.html
python3 driftmap-presenter/scripts/render_map.py driftmap-presenter/examples/retry-check/MAP.md --style gilded --out retry-gilded.html
```

The route explorer is manual preview only; it does not enforce the attempt budget.
