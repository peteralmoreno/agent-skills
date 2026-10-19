# Structured Storycraft schema (v1)

`render_story.py` accepts an authored JSON object. The agent must construct this from the input; this tool is **not an automatic HTML-to-story extractor**.

## Required top-level fields

```json
{
  "schema_version": 1,
  "eyebrow": "Fictional demonstration",
  "title": "One clear idea, beautifully told.",
  "summary": "A precise short description with no fabricated facts.",
  "source_note": "Example only: no real actions are performed."
}
```

Optional top-level fields: `hero_label`, `badge`, `panel_title`, `panel_body`, `hero_symbol` (`spark`, `burrito`, `leaf`, `compass`), `highlights`, `callouts`, `flow`, `chapters`, `sources`.

Callouts contain `{ "kind": "important" | "uncertain", "title": "...", "text": "..." }`. They must be **supported by input**. Morrito illustrates them as an eyed gold star or a question box; Gilded as a sword/ornament or question panel; Dark as crisp red/blue semantic callouts. No more than 5 callouts.

Highlights contain `{ "eyebrow", "title", "description" }`. Chapters contain `{ "eyebrow", "title", "body", "points": ["..."] }`. Sources are `{ "label", "url" }` using explicit `https:`, `http:`, or `mailto:` URLs. Never add fabricated source URLs.

## Flow

```json
{
  "flow": {
    "title": "Journey title",
    "description": "What the reader is exploring, and what buttons do not execute.",
    "nodes": [
      {"id": "begin", "title": "Start", "summary": "Short label", "detail": "Real step guidance"},
      {"id": "finish", "title": "End", "summary": "Short label", "detail": "Actual outcome"}
    ],
    "edges": [{"from": "begin", "to": "finish", "label": "ready"}],
    "primary_path": ["begin", "finish"]
  }
}
```

The renderer enforces:

- `schema_version = 1`, nonblank required text.
- `flow.nodes` between 2 and 20 with safe unique IDs.
- Every edge references an existing node; no more than 50 edges.
- `primary_path` contains 2+ distinct known node IDs, each consecutive pair backed by a declared edge.
- Nodes excluded from the primary route must participate in at least one declared edge.
- No more than 5 highlights, 5 callouts, 8 chapters, or 30 source links.
- HTML escaping and script-data escaping prevent story copy from becoming executable code.

A primary path is for **explanation**; alternate edges are shown separately and remain selectable. Loops may be present as alternate edges but are never auto-replayed indefinitely. For exceptionally complex graphs, create a custom HTML representation rather than hiding branches.

Use one JSON file for all styles to guarantee content parity. `--style all --out-dir ...` creates three separate standalone HTML pages, each with the same story and graph.
