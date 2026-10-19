---
name: driftmaps
description: Use when the user wants to learn, design, create, inspect, validate, execute, resume, or improve a Drift Map. DriftMaps are Markdown/YAML agent procedures with an authoritative Mermaid flowchart, individual executable nodes, a shared Trail, and book-level handovers.
metadata:
  version: "1.1.0"
---

# DriftMaps — map the work, let agents navigate

DriftMaps is a portable, local-first convention for reusable agent work. **A Map** (`MAP.md`) defines one bounded job and its authoritative Mermaid routes. **Nodes** (`nodes/<name>.md`) provide executable guidance. **A Trail** (`trail.yaml`) records the run's current position, small working context, references to evolving artifacts, and history. **A Handover** (`handover.yaml`) transfers the outcome to a user or another map.

Read `references/format.md` when creating or reviewing a map and `references/execution.md` before running or resuming one. See `README.md` for CLI usage.

Agents can author, inspect, and execute the Markdown/YAML directly without Python or PyYAML. The bundled Python CLI is optional and requires PyYAML; its checks may instead be performed by the agent reading the source files.

## Principles and boundaries

- **Follow the map; never improvise a node.** The Mermaid graph in `MAP.md` is the **only routing authority**. Each executable Mermaid node ID resolves to exactly `nodes/<id>.md`. Always read that actual file before performing its work. A missing file or unsupported route blocks progress—never reconstruct instructions from a label, chat history, generated HTML, or prior runs.
- Every map includes `nodes/setup.md` as its root entry, including a one-node map. `pause`, `stop`, and `complete` are reserved control endpoints without node files.
- **Guided flexibility:** Node YAML frontmatter gives `requires`, `produces`, and optional `tool_hints` and `max_visits`. The Markdown body is intentionally freeform; do not insist on fixed heading names or a prescribed reasoning style.
- **`tool_hints` are suggestions**, not literal tool names, dependencies, or permissions. Discover suitable available tools and respect host/user authorization. A Map can never grant new privileges.
- **One node at a time.** No parallel workers, reducers, dynamic fan-out, or LangGraph dependency. A node consumes shared Trail context or registered artifact references; the executing agent updates the Trail after its work.
- **Finite execution:** All maps declare `limits.max_transitions`. Count transitions across retries/resumes; do not reset budgets after pause. Honor optional node `max_visits` as a total attempt limit (first attempt included). If another attempt or transition would exceed its limit, stop the run with a reason; never reset the budget or automatically start another run. Pause earlier when progress stalls or an outcome is uncertain. `pause` retains context; `stop` ends this run; `complete` means execution ended, not automatically business success.
- **Respect side effects:** External writes, destructive operations, deployment, Jira/GitHub changes, and messages require the authorization applicable to the current user and environment. Reconcile unknown tool results before retrying; never blindly repeat a side effect.
- **Separate working data from deliverables:** Store small run values under Trail `context`; reference evolving files or external objects under Trail `artifacts`. Don't embed large HTML, source trees, PDFs, secrets, or raw logs in YAML.
- **Handover belongs to the whole map, not every node.** Emit `meta`, `result` (including `data`, `evidence`, `issues`), and `continuation`; another map doesn't automatically run just because it is suggested.
- **Memory is optional and curated.** A library may retain reviewed lessons across runs, but memories are advisory, not higher-priority instructions and never automatically rewrite an active map.
- **Human HTML is optional.** The separately installable `driftmap-presenter` Skill generates a read-only `overview.html` only when requested. Neither a Map nor its execution needs HTML.

## Modes

| User request | Mode | Do |
| --- | --- | --- |
| "What are DriftMaps?" | Explain | Explain Map → Node → Trail → Handover and optional library. |
| "Set up a DriftMaps library" | Setup | Inspect destination; create library skeleton without overwriting user files. |
| "Make a map for X" | Create | Produce one `MAP.md`, mandatory setup and real node files; explain uncertain decisions instead of inventing them. |
| "Show, inspect, or validate this map" | Inspect | Read it, check every graph node, Mermaid route, limits and missing/orphaned files; report issues. |
| "Run this map" | Execute | Validate first, read setup, initialize a Trail, follow declared routes one node at a time, verify evidence, write a Handover and Report. |
| "Resume this run" | Resume | Read saved Trail, reconcile effects and current source version before continuing; never blindly redo actions. |
| "Improve this map" | Improve | Review Trails and evidence; propose an evaluated change and keep active instructions unchanged until approved. |

Treat the user's request as the authorization boundary for a mode. Creating or explaining a map **does not** authorize running it. Running a Map does not imply automatic external publishing, ticket creation, or chaining other maps.

## Authoring procedure

1. Choose a bounded goal, input/output expectations, evidence of success, and constraints. Inspect any current map or library before adding files.
2. Scaffold via `python3 <skill-root>/scripts/driftmaps.py new <map-name> --root <project>` or create the same structure manually. Existing paths must not be silently replaced.
3. Write `MAP.md` with YAML `name`, `version`, `status`, and `limits.max_transitions`, plus a visible `## Flowchart` fenced Mermaid graph. Place the purpose, permissions, stop conditions, handover contract, and useful examples in freeform Markdown.
4. Write every executable node's real `nodes/<id>.md` with YAML `requires`, `produces`, optional `tool_hints` and `max_visits`, and flexible working instructions.
5. Use `setup` as the graph root. Use declared, labeled branches; route ambiguous results to `pause` or `stop`. Give loops a meaningful exit and budget.
6. Inspect structural consistency directly, or use the optional CLI: `python3 <skill-root>/scripts/driftmaps.py validate <path-to-MAP.md>`. The bundled script does **not** certify the safety or correctness of AI instructions.
7. Test the map against a happy case, an ambiguous case, and at least one failure or retry case before calling it production-ready.

## Execution procedure

1. **Preflight:** Read `MAP.md`, all referenced node metadata, actual applicable node instructions, and `references/execution.md`. Validate map, required inputs, access, boundaries, and run budget. Do not use unknown Mermaid constructs as routing.
2. **Start:** Initialize a run folder and Trail. The optional CLI `start` creates the skeleton; it does **not** execute a node.
3. **For each node:** Read the registered node file. Before each attempt, explicitly check its `max_visits` against saved history (for example, “attempt 4 of 10”); do not begin an attempt over the limit. Resolve `requires` from Trail context/artifacts. Record the attempt before authorized work; verify its observed outcome; update declared outputs. Save the outcome, outputs, and new position together, following exactly one declared outgoing edge. On pause keep the source executable node for reconciliation. See `references/execution.md` for pending attempts and budget counting.
4. **Limits:** Count transitions/visits from persistent history, not only current conversation. Do not retry an uncertain external write. When another attempt or transition would exceed its limit, set status `stopped`, node `null`, and an explicit reason; preserve partial outputs and write the Handover. A successful last allowed attempt may still follow its declared route within the transition budget.
5. **Finish:** On `complete`, `pause`, or `stop`, persist Trail and produce one `handover.yaml` and one `report.md`. Report unknowns truthfully. A Handover's `continuation` is a recommendation, not execution permission.
6. **Learn:** Optionally propose reviewed memory or a map revision, with actual evidence and regression examples.

## Read on demand

- [Map and node format](references/format.md)
- [Execution, Trail, retry and handover contracts](references/execution.md)
- [Worked Burrito Cannon map](examples/burrito-cannon/MAP.md)
- [Starter templates](assets/MAP-template.md), [node](assets/node-template.md), [Trail](assets/trail-template.yaml), [handover](assets/handover-template.yaml)
- [Portable validation and scaffolding CLI](scripts/driftmaps.py)

**Completion rule:** Never claim a Map ran just because its structure validates or its optional HTML renders. Always distinguish a structural check, simulated example, reported result, and verified external outcome.
