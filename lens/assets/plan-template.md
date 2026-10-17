---
format: lens/v1
status: draft
source_spec: specs/<slug>-prism.md
source_status: unknown
delivery_target: <increment or milestone>
# source_revision: <commit SHA or document version, only if known>
---

# LENS — <Delivery plan title>

<!-- Authoring notes are prompts, not part of the finished plan. Delete HTML comments before handing off. Follow references/guide.md for a filled, explained example. -->

One delivery plan for the referenced PRISM specification. This file is **not permission to implement**.

## L — Limits

<!-- Answer: What is delivered now? What remains for later? Why this split? Every PRISM R# must appear exactly once in coverage. Never defer an invariant protecting Now work. -->

### Now

- <Outcome included in this delivery increment>

### Later

- <Deferred requirement or increment, with next destination/owner if known>

### Outside this delivery

- <Adjacent work not part of this effort; don't silently cancel any PRISM R#>

### Requirement coverage

| PRISM ID | Delivery | Reason / next step |
| --- | --- | --- |
| R1 | Now | <Delivered via W1> |
| R2 | Later | <Separate increment or follow-up; requirement still applies> |

## E — Execution plan

<!-- Write reviewable W# outcomes, not a line-by-line coding recipe. Dependencies use W# or None. Link real PRISM R/I/S IDs. Done when describes a completion condition; proof belongs in Signals. -->

| Work ID | Deliverable / action | Depends on | PRISM links | Done when |
| --- | --- | --- | --- | --- |
| W1 | <Small testable work outcome> | None | R1, I1, S1 | <Observable completion condition> |

Sequence and concurrency notes (only when helpful): <prerequisites, safe parallel work, checkpoints>.

## N — Needs

<!-- Include only material unknowns. Blocker = cannot proceed; Risk = may go wrong, mitigation needed; Question = confirm at an appropriate checkpoint. If none remain, use None — confirmed. -->

| Need ID | Type | Description | Resolve before |
| --- | --- | --- | --- |
| N1 | Risk | <Potential issue and mitigation> | <W# or checkpoint> |

## S — Signals

<!-- Identify future evidence, mapped to PRISM M#; do not claim tests passed or invent acceptance thresholds. Every W# needs a Signals row. -->

| Work ID | PRISM measures | Evidence to collect |
| --- | --- | --- |
| W1 | M1 | <Which test, demonstration, inspection, metric, or record to collect later> |

## Handoff

<!-- Short closing summary inside this same file, not a separate handoff document. Approved LENS status requires genuine user approval and an approved PRISM source. -->

- **Readiness:** Draft — needs decisions
- **Next step:** <What an implementation agent should inspect or do first, if separately authorized>
- **Remaining blockers:** <N# blockers or `None — confirmed`>
- **Authority:** Refer to `source_spec` for requirements, invariants, decisions, and measures. This plan does not authorize implementation or Git changes.
