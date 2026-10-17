---
format: lens/v1
status: draft
source_spec: specs/<slug>-prism.md
source_status: approved
delivery_target: <increment or milestone>
# source_revision: <commit SHA or document version, only if known>
---

# LENS — <Delivery plan title>

A concise delivery plan for the referenced PRISM specification. This file is a **plan**, not permission to implement.

## L — Limits

### Now

- <Outcome included in this delivery increment>

### Later

- <Deferred requirement or increment, with owner/next destination if known>

### Outside this delivery

- <Adjacent work excluded from this delivery, without changing PRISM product scope>

### Requirement coverage

| PRISM ID | Delivery | Reason / next step |
| --- | --- | --- |
| R1 | Now | <Delivered via W1> |
| R2 | Later | <Future increment / follow-up reference> |

## E — Execution plan

| Work ID | Deliverable / action | Depends on | PRISM links | Done when |
| --- | --- | --- | --- | --- |
| W1 | <Small testable work outcome> | None | R1, I1, S1 | <Observable completion condition> |

Sequence and concurrency notes (only when helpful): <dependencies, parallel opportunities, checkpoints>.

## N — Needs

| Need ID | Type | Description | Resolve before |
| --- | --- | --- | --- |
| N1 | Risk | <Risk and mitigation or contingency> | <W2 / approval / release> |

If none remain, replace the table rows with `None — confirmed`; don't invent risks to complete a form.

## S — Signals

| Work ID | PRISM measures | Evidence to collect |
| --- | --- | --- |
| W1 | M1 | <Test/demo/metric or other verifiable evidence; not a fabricated result> |

## Handoff

- **Readiness:** Draft — needs decisions
- **Next step:** <What an implementation agent should do first *if separately authorized*>
- **Remaining blockers:** <List N# blockers or `None — confirmed`>
- **Authority:** Refer to `source_spec` for requirements, invariants, decisions, and measures. This plan does not authorize implementation or Git changes.
