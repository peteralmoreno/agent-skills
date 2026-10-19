---
name: driftmap-presenter
description: Use when the user explicitly wants a human-readable, interactive HTML overview, graph explorer, or shareable presentation of an existing Drift Map. Generate a read-only optional front face from MAP.md and nodes without changing how agents consume or execute the map.
metadata:
  version: "1.0.0"
---

# Drift Map Presenter

A Drift Map is an agent-readable procedure defined by a `MAP.md` with an authoritative Mermaid flowchart and `nodes/*.md` instructions. **Drift Map Presenter is an optional, separate skill.** It produces a polished HTML interpretation for humans, not an execution plan or another authoritative map.

## Core contract

- **Opt-in only.** Do not generate HTML when somebody merely asks to create, review or run a Drift Map. Invoke this skill only for a human-facing view, diagram explorer, presentation, HTML overview, or an explicit request for the presenter.
- Source of truth is still `MAP.md` and its node files. A presentation is a **read-only snapshot**. Never modify graph edges, node instructions, YAML, or run history as a side effect.
- **Graph fidelity:** show only declared nodes and transitions. Do not invent a nicer happy path, omit failure branches, or claim the diagram authorizes tool use. The graph is explanatory; routing and actual agent work still come from the original map.
- **Node fidelity:** read each referenced file. The visible inspector shows the node's instructions plus `requires`, `produces`, and optional `tool_hints`. Treat tool hints as suggestions, not mandatory tool identifiers or permissions.
- **No fake live status:** route exploration is a simulated walkthrough for understanding decisions, not execution. Do not claim a node ran or an SMS, GitHub action, or deployment occurred.
- **Secure by default:** escape embedded Markdown/HTML and untrusted node content. Do not execute scripts found in source files, resolve untrusted remote assets, use external CDNs, or load sensitive run records without explicit request and sanitization. The generated viewer is offline and self-contained.
- **Respect user work:** write only the requested generated HTML file. Do not overwrite an existing file without examining it and obtaining appropriate authorization. `--force` must be deliberate.

## Modes

| User intent | Mode | Output |
| --- | --- | --- |
| "Show me an interactive view of this map" | **Present** | Standalone `overview.html` (default) |
| "Refresh the human overview after map changes" | **Refresh** | Regenerated HTML, after review of existing output |
| "Is this map suitable for the presenter?" | **Inspect** | Explain supported Mermaid subset and missing files; do not create HTML unless requested |
| "What does this presenter do?" | **Explain** | Clear comparison of AI-readable map vs human-facing companion |

## Workflow

1. Confirm the user chose to have the human-facing output for this map; never default other maps to requiring HTML.
2. Locate the exact `MAP.md` and its `nodes/` directory. If the map isn't present, explain the missing input rather than inventing a graph.
3. Read the source map and applicable node files. Check that named Mermaid nodes actually have corresponding `nodes/<id>.md` files, except the reserved control endpoints `pause`, `stop`, and `complete`.
4. Use the bundled standard-library generator to create a single standalone HTML file:

   `python3 <skill-root>/scripts/render_map.py <project>/maps/<name>/MAP.md --out <project>/maps/<name>/overview.html`

5. Confirm the output exists and inspect it in a browser when a browser tool is available. On phone, provide a normal downloadable file and suggest an external browser if the app won't preview HTML.
6. Explain that clicking graph nodes shows guidance and selecting routes is a non-executing preview. Show which source files the presentation reflects.
7. When regeneration is requested, review any existing HTML before using `--force`, because it will replace that file.

The generator intentionally supports a **small Mermaid subset**: `flowchart TD`, `TB`, or `LR`; one `-->` per line; optional `|edge label|`; and basic node labels. Unsupported graph syntax errors instead of being silently flattened. For complex maps, improve the generator or make an explicitly reviewed custom presentation while keeping `MAP.md` authoritative.

## Human-first quality bar

- Make the purpose and boundaries readable before diving into details.
- Display **every** branch, loop, pause, stop, and completion route from the source.
- Let users inspect nodes by clicking and see their guidance without leaving the page.
- Provide a clear, explicitly simulated path explorer. Never call the preview "Run Map".
- Use responsive accessible styling, keyboard-operable controls, readable contrast and no required external network calls.
- Keep graph control nodes distinct from executable nodes.
- Include a clear origin/version label and mark the page as a presentation snapshot.
- Keep AI-facing paths free of this dependency: agents should never need to open `overview.html`.

## References

- [Human guide and CLI quickstart](README.md)
- [Presenter design notes](references/design.md)
- [Offline HTML generator](scripts/render_map.py)
- [Illustrative Burrito Cannon Map](examples/burrito-cannon/MAP.md)
- [Offline regression tests](tests/test_presenter.py)

## Completion boundary

Report whether the HTML was generated, what Map was used, whether unsupported syntax/missing files blocked generation, and where to view the result. **Never claim that presentation generation executed the Drift Map.**
