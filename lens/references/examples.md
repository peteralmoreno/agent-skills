# LENS worked examples

The examples use invented engineering scenarios and invented PRISM IDs for illustration. They are not findings about a real production environment.

## Example 1 — Expanding notifications with Kafka

**Source:** `specs/event-notifications-prism.md`, approved. It defines:

- `R1` publish change events for subscribers; `R2` support consumer migration.
- `I1` existing consumers remain compatible.
- `S1` use a dedicated Kafka topic.
- `M1` integration test confirms new events; `M2` contract test confirms compatibility.

### L — Limits

Now: event publication and compatibility tests. Later: consumer migration.

| PRISM ID | Delivery | Reason / next step |
| --- | --- | --- |
| R1 | Now | Delivered through W1 and W2 |
| R2 | Later | Independent consumer-migration increment after publication is stable |

### E — Execution plan

| Work ID | Deliverable / action | Depends on | PRISM links | Done when |
| --- | --- | --- | --- | --- |
| W1 | Define and add the agreed topic publication path | None | R1, I1, S1 | Change events can be published without changing existing consumers |
| W2 | Establish compatibility and event-delivery checks | W1 | R1, I1 | Integration and contract checks can exercise the expected behavior |

### N — Needs

| Need ID | Type | Description | Resolve before |
| --- | --- | --- | --- |
| N1 | Question | Confirm consumer migration's separate delivery owner | Increment completion |

### S — Signals

| Work ID | PRISM measures | Evidence to collect |
| --- | --- | --- |
| W1 | M1 | Integration test evidence for event publication |
| W2 | M1, M2 | Repeat integration and contract tests; record outcomes |

**Meaning:** Work on R1 can start after LENS approval without prematurely building all of R2. I1 still governs W1 and W2.

## Example 2 — Exploratory solution, not yet approved

A PRISM draft contains `S1a` (central registry) and `S1b` (repository metadata) as alternatives, with no selected solution. A LENS can propose a time-boxed comparison *only if the author wants that*, but must remain `status: draft` or `blocked` and cannot call a production build ready.

Clarification: **Which solution variant or decision process is approved?** The agent must not mash S1a and S1b together just because the RAY Angle listed both.

## Example 3 — High-stakes multi-phase migration

PRISM requires `R1` migrate records and `R2` expose audit reporting, with `I1` tenant isolation and `I2` durable evidence on every write.

LENS may split migration cohorts into delivery increments, but `I1` and `I2` cannot be delayed. If the first cohort is Now, the migration and its proof must already honor both invariants. A draft plan that postpones audit logging until the final phase is **Blocked — return to PRISM or revise the plan**.

## Example 4 — Short on purpose

A simple PRISM with one requirement and one measure does not need invented milestones or risks. It can produce:

- Limits: R1 Now.
- Execution plan: W1 implements R1 and preserves I1.
- Needs: None — confirmed.
- Signals: W1 maps to M1.
- Handoff: Ready only once explicitly approved.

Keep the planning document proportionate to the work.
