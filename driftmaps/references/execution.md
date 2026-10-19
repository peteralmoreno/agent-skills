# DriftMaps — execution, Trail, and handover

## 1. Preflight and pinning

Read `MAP.md`; check the graph and nodes directly, or use the optional Python validator. Python and PyYAML are not required for agent execution. Before executing, record source version and preferably a computed digest of the Map plus node files. Read `nodes/setup.md` first. The graph is the authority for routing; edge labels identify observed outcomes. Check user authorization, available tools, and the map's instructions. A map alone does not grant permission.

Every run has a unique folder under `.driftmaps/runs/`, separate from the reusable `maps/` source. Keep runtime data out of Git by default, particularly if it includes private coordinates, customer IDs, logs, or service information.

## 2. Single-node lifecycle

1. Read `trail.yaml` and resolve the current node ID from the Mermaid graph.
2. Resolve that node's `requires` keys from `context` or `artifacts`; missing information means pause, not a guessed value.
3. Read the actual `nodes/<id>.md` file. Before starting work, check the saved budgets and append a history entry with `node`, `outcome: pending`, and `next: null`; save it before any side effect. Apply the Markdown guidance using appropriate *authorized* tools. `tool_hints` are nonbinding.
4. Record the observed outcome and evidence. Validate that the selected outgoing edge actually exists and its label is supported by observations. If no route matches, pause for clarification rather than inventing an edge.
5. Update only declared `produces` in Trail `context` or `artifacts`. An artifact entry points to a local file or external reference, optionally with version/digest; never embed its full contents in Trail.
6. Finish the pending history entry with the observed outcome and selected destination. Update outputs, that entry, and `current` together, then save the whole Trail by replacing it with a temporary file. Never save a completed transition with the old running-node pointer. For an executable destination, keep status `running` and set its node; for `complete` or `stop`, set status `completed` or `stopped` and node `null`.
7. A visited node may be re-entered through a declared loop. If it does, investigate whether previous actions had side effects; avoid duplicate sends, pushes, dispatches, or deployments.

## 3. Trail layout

```yaml
meta:
  run: burrito-0042
  map: burrito-cannon
  version: "0.1.0"
  # record a real source digest when available

current:
  status: running
  node: blast

context:
  order_ref: ORD-42
  burrito_ref: BUR-42
  coordinates: [30.45, -97.62]
  isMember: false

artifacts:
  specification:
    path: artifacts/spec.html
    revision: 3

history:
  - node: setup
    outcome: ready
    next: prepare
  - node: prepare
    outcome: wrapped
    next: locate
  - node: locate
    outcome: verified coordinates
    next: blast
```

Use `current.status`: `running`, `paused`, `completed`, or `stopped`. `current.node` is the executable node to work on or reconcile; it is `null` after completion or stop. On a `pause` route, keep the source executable node and set status `paused`—never set the current node to the control ID `pause`. A missing input pauses at the current executable node. An exhausted retry/transition budget stops the run as described below, without inventing a graph edge. `context` is **current** small values; `history` records execution attempts in order. Complete the pending entry after its work; never rewrite completed entries. `artifacts` is a registry of pointers to evolving outputs. A node may update an existing artifact; record version/provenance where meaningful.

The Trail must never be treated as a secret vault, raw transcript, or source of instructions higher than the Map. Checkpoint by writing a safe temporary file and replacing the previous Trail where the environment permits. Record enough information with a pending history entry to identify an intended side effect and any returned receipt; reconcile if the agent loses connection afterward; YAML alone does not guarantee exactly-once execution.

## 4. Loop bounds and resumption

Use optional node `max_visits` for “try this node at most N times.” It counts total execution attempts, including the first attempt and interrupted attempts, across the entire run. Count that node's history entries except `kind: decision`. Reading instructions or checking an existing effect is not another attempt. Each retry must follow a declared Mermaid route and create a new attempt entry; do not hide repeated node executions inside one visit.

For example, `max_visits: 10` allows attempts 1 through 10. If attempt 10 succeeds, continue along its success route normally. If another attempt is needed, give up: set `current.status: stopped`, `current.node: null`, and `current.reason: "max_visits exhausted for <node>: 10 attempts"`. Preserve history and outputs, and write a Handover explaining what failed and what remains usable. Do not start attempt 11, reset the counter on resume, or automatically create another run.

The map's `limits.max_transitions` is the overall backstop. Count history entries with a non-null `next`, including transitions to controls. Before taking a transition, check that budget remains. If exhausted, stop with a reason rather than start more work; an already-selected terminal outcome remains terminal. Budget exhaustion is a safety stop, not an invented Mermaid route. Read-only reconciliation remains allowed, but cannot reset a budget or restart a stopped run. A separately requested new run starts its own budget. Before either limit is reached, pause early if progress stalls or an outcome is uncertain.

On resume, check pinned map version/digest and reconcile completed or possibly completed external actions. A pending history entry means work may already have happened: inspect its evidence before doing anything again. Checking an existing effect does not consume another visit; actually repeating node work requires a new history entry and remaining budget. After a pause, resolve the reason at the saved executable node, then select only an observed outgoing route from that node. If the existing entry is still pending, finish it. If it already recorded a pause, append a new routing-only entry with `kind: decision`, `node`, `outcome`, and `next`; it counts toward transitions but not `max_visits`. Save the selected route, evidence, and updated current position together. If an interrupted attempt must be repeated, first mark its entry `outcome: interrupted` with `next: null`, then start a new attempt within the existing budget. Never blindly repeat a node. If the source changed, use a deliberate migration/new run rather than silently executing different instructions.

## 5. Final artifacts

`handover.yaml` should carry **exactly three top-level sections**:

```yaml
meta:
  format: drift-handover/v1
  source:
    map: burrito-cannon
    version: "0.1.0"
    run: burrito-0042

result:
  status: ready
  data:
    order_ref: ORD-42
    isMember: false
    delivery_ref: DEL-42
  evidence:
    - check: delivery-confirmed
      status: passed
      ref: receipt-42
  issues: []

continuation:
  map: customer-feedback
  intent: Ask whether the burrito arrived intact
```

The `result.status` indicates usability (`ready`, `partial`, `blocked`, `failed`), not graph position. `continuation` can be `null`. It communicates intent, **not authorization** for automatic map chaining. The receiving map must validate values, provenance, timeliness, and access. A verified `isMember: false` differs from missing, null, or unknown.

Generate `report.md` as a readable, trustworthy outcome explanation with YAML frontmatter (`map`, `run`, `outcome`). It is derivative presentation, never a second data authority.

## 6. Memory

A Map Library may keep approved cross-run observations separately from Trail under `.driftmaps/memory/<map>.yaml`. Proposed observations remain proposals until reviewed; each should link to actual run evidence. Never let memory silently change route edges or override authorization. The `MAP.md` and nodes remain separately versioned canonical instructions.

## 7. No built-in engine

The optional CLI scaffolds/validates/initializes; it is not a model runner, a permissions service, a transactional state manager, or a promise of external correctness. A capable agent executes nodes using the tools available to it.
