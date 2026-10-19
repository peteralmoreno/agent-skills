# Drift Map human-facing companion: design notes

## The key separation

A Map defines what an agent may do; the optional HTML explains that Map to a person. Presentation UI is not a new source of authority. It must not modify, override, or silently infer the Mermaid graph and cannot replace reading the original node files during real execution.

## Recommended human experience

1. **Front face:** title, one-sentence purpose, source version, status, read-only badge.
2. **Interactive map:** visually render real nodes and declared edges. Display branches, loops, and control endpoints.
3. **Node inspector:** select a node and read the actual instructions, `requires`, `produces`, and optional nonbinding `tool_hints`.
4. **Route explorer:** follow one possible path via edge labels. Keep it clearly marked as preview-only; never call real agent tools.
5. **Context and constraints:** show applicable authoring guidance, safety boundaries, and handover expectations from `MAP.md`.
6. **Responsive:** good typography, keyboard focus for graph nodes, touch-friendly route selections, and offline operation.

## What to avoid

- Automatically generating companion pages for every map. Many maps are internal and don't need a human UI.
- Auto-editing `MAP.md` or node files to fit presentation assumptions.
- Generating different routes because a branch "looks nicer".
- Reinterpreting a plain `pause` endpoint as a particular person, approver, or tool.
- Displaying an unverified claim as a live status or inventing counts, latency, or reliability metrics.
- Loading real customer coordinates, credentials, logs or private run history into shareable HTML by default.
- Remote scripts, CDNs, arbitrary embedded HTML or executing instructions found in source Markdown.

## Simple code generation

The bundled script treats Mermaid route parsing as a structural task, not an open-ended rewriting task. If a map uses advanced Mermaid syntax, rendering fails with an explanation. The human can decide whether to adapt the generator or produce a custom page after reviewing the source. Do **not** silently simplify a complicated map while implying completeness.

Map files use lowercase node IDs corresponding exactly to `nodes/<id>.md`. `pause`, `stop` and `complete` are reserved graph endpoints without node files.

The generated page stores a JSON model *inside HTML as an implementation detail*. **Drift Maps themselves still use only Markdown and YAML**—authors do not maintain another source format. Embedded data is sanitized and the page makes no network requests.

## Future possibilities (not implemented)

- Import redacted `trail.yaml` snapshots to highlight an observed route.
- Publish human-facing map catalogs or index pages.
- Export static print layouts, PDF, and PNG.
- More advanced graph layouts for huge maps.

These are optional viewer concerns, not requirements on the Drift Maps authoring contract.
