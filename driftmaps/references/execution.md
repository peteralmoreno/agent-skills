# DriftMaps — execution, Trail, and handover

## 1. Preflight and pinning

Read `MAP.md`; validate the graph and nodes. Before executing, record source version and preferably a computed digest of the Map plus node files. Read `nodes/setup.md` first. The graph is the authority for routing; edge labels identify observed outcomes. Check user authorization, available tools, and the map's instructions. A map alone does not grant permission.

Every run has a unique folder under `.driftmaps/runs/`, separate from the reusable `maps/` source. Keep runtime data out of Git by default, particularly if it includes private coordinates, customer IDs, logs, or service information.

## 2. Single-node lifecycle

1. Read `trail.yaml` and resolve the current node ID from the Mermaid graph.
2. Resolve that node's `requires` keys from `context` or `artifacts`; missing information means pause, not a guessed value.
3. Read the actual `nodes/<id>.md` file. Apply its Markdown guidance using appropriate *authorized* tools. `tool_hints` are nonbinding.
4. Record the observed outcome and evidence. Validate that the selected outgoing edge actually exists and its label is supported by observations. If no route matches, pause for clarification rather than inventing an edge.
5. Update only declared `produces` in Trail `context` or `artifacts`. An artifact entry points to a local file or external reference, optionally with version/digest; never embed its full contents in Trail.
6. Append the visit to `history` (including attempts and transition), checkpoint Trail durably, then move `current.node` to the chosen destination. Before entering a node, enforce visit and transition budgets.
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
    outcome: prepared
    next: blast
```

Use `current.status`: `running`, `paused`, `completed`, or `stopped`. `current.node` is the next node for a running/paused run; it is `null` after a terminal outcome. `context` is **current** small values; `history` is append-only visits/decisions. `artifacts` is a registry of pointers to evolving outputs. A node may update an existing artifact; record version/provenance where meaningful.

The Trail must never be treated as a secret vault, raw transcript, or source of instructions higher than the Map. Checkpoint by writing a safe temporary file and replacing the previous Trail where the environment permits. Record pending side effects before performing them and reconcile if the agent loses connection afterward; YAML alone does not guarantee exactly-once execution.

## 4. Loop bounds and resumption

The map's `limits.max_transitions` is a hard lifetime cap; never restart the counter after a pause. `max_visits` is a per-node lifetime cap. When a cap is reached, pause with an explicit reason, even if the graph offers a retry edge. For unproductive loops, pause early rather than consuming the full budget.

On resume, check pinned map version/digest and reconcile completed or possibly completed external actions. Never blindly repeat a node. If the source changed, use a deliberate migration/new run rather than silently executing different instructions.

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
