# LENS — Authoring guide

> **Focus the spec; don't respecify the product.**

**LENS** stands for **Limits, Execution plan, Needs, Signals**. It is the last stage of the lightweight idea-to-plan workflow:

```text
RAY (author intent) → PRISM (engineering contract) → LENS (delivery plan)
```

This is intentionally the end of the process. Implementation conventions, Git operations, pull-request practices and post-implementation review are owned by whichever execution workflow consumes the plan. LENS doesn't prescribe or perform them.

## 1. What LENS produces

One Markdown document. It references one **authoritative PRISM specification** (possibly narrowed to a delivery increment), has an explicit status and lists the work and evidence needed for delivery. It is **standalone as a handoff**, not self-contained as a duplicate spec: an implementer can start from LENS plus the linked PRISM and repository, with no chat history.

The typical location is `plans/<slug>-lens.md`.

## 2. Inputs and source authority

Read the chosen, approved PRISM spec, not merely its title. Extract:

- **P**: user problem, outcome, original product scope and non-goals.
- **R#**: numbered required behavior; every R# must be placed in the LENS coverage table.
- **I#**: invariants, including compatibility and security promises that apply to the slice now.
- **S#**: selected technical choices, their rationale, and any recorded freedom to change.
- **M#**: acceptance evidence planned in PRISM.
- **Traceability and open questions**: links and unresolved decisions.

If more than one PRISM variant exists, **choose one explicitly**. Don't combine two proposals merely because they share a RAY intent.

If PRISM is unapproved, unavailable or internally contradictory, produce a provisional draft and identify the missing decision. Don't mark a plan ready by guessing.

## 3. L — Limits: choose *delivery* scope

Answer **what is being delivered in this run**. This is not permission to redefine PRISM's product scope.

- **Now**: what must be delivered in this increment.
- **Later**: approved features or requirements explicitly deferred; identify a destination or follow-up. Deferred != canceled.
- **Outside this delivery**: tempting adjacent work not being executed here; this does not remove it from PRISM if PRISM requires it.
- **Requirement coverage**: every PRISM `R#` assigned to `Now`, `Later`, or `Outside this delivery` with a reason/next step.

If a required result is `Outside this delivery`, there must still be a clear path to fulfillment; if the entire PRISM outcome cannot be achieved within the selected delivery unit, don't claim this increment meets the full spec. Never defer a required invariant that protects an included behavior.

**Bad:** `R3 — Out of scope; we aren't doing it.`

**Better:** `R3 — Later; dependent consumer migration is scheduled as a separate delivery increment, not included in this change.`

## 4. E — Execution plan: define doable units

One row per work unit, stable IDs `W1`, `W2`, ...

Each work unit includes:

1. **Deliverable/action**: a concrete work outcome, not `do some refactoring`.
2. **Depends on**: exact prior W#s, or `None`.
3. **PRISM links**: relevant R#, I#, S#.
4. **Done when**: an observable completion condition, not `engineer is finished`.

Sequence tasks according to dependencies; explain parallel opportunities where distinct ownership and actual isolation make them safe. Don't invent durations, owners, repositories or exact files unless known. You can add researched touchpoints if the user asked for repository inspection, but ground every assertion.

Avoid transforming LENS into a line-by-line code editing recipe; the future implementer still needs judgment.

## 5. N — Needs: expose the important friction

Include things that materially affect a sensible delivery plan:

- **Blocker:** decision or prerequisite that prevents starting or completing the affected work; record when resolution is needed.
- **Risk:** potential issue with a mitigation or contingency.
- **Question:** unknown worth confirming but not necessarily a gate.

Distinguish things PRISM must decide from things an implementer can decide during work. If a PRISM solution choice or invariant is still undecided, don't invent it here. If there are genuinely no material needs, say `None — confirmed`, rather than manufacturing a risk register.

## 6. S — Signals: plan evidence, don't claim execution

Map each W# to applicable PRISM M# measures. Specify **evidence to collect** (tests, manual scenarios, metrics, logs, reviews where relevant), keeping PRISM thresholds unchanged.

**Good:** `W2 | M3 | Verify a duplicate event produces no extra downstream effect; record integration test results.`

**Bad:** `W2 | M3 | PASS, validated` — LENS runs before implementation.

If M# is missing or inadequate, mark a PRISM gap and stop pretending the handoff is fully validated. Avoid inventing target numbers.

## 7. Interaction style

A useful LENS coaching turn should present:

1. **Proposed delivery slice and draft plan**.
2. **One to three recommendations** (e.g., separate an oversized work unit, move a prerequisite earlier, define a missing test signal).
3. **At most three decisive questions**, preferably one at a time during back-and-forth.

Use the available source context instead of asking the author to repeat known facts. A valid empty Need is better than fake structure. If the user explicitly asks for a complete plan without questions, draft with clear assumptions, and don't mark it approved.

## 8. Readiness checkpoint

A LENS is **Ready for implementation handoff** only when:

- the PRISM source is approved and identifiable;
- a single PRISM solution variant is selected where needed;
- every R# is accounted for by Now/Later/Outside this delivery;
- every Now requirement maps to one or more W# units;
- each W# has meaningful verification and planned evidence;
- the plan preserves relevant invariants and PRISM decisions;
- dependencies are possible, blockers resolved or explicitly gated;
- the user explicitly approves the LENS plan.

This readiness is **not** authorization to execute. An implementation agent must obtain or rely on its own execution approval and repository access policies.

## 9. Concrete examples

**Kafka feature:** PRISM chooses a Kafka topic and preserves existing consumers. LENS scopes publisher work and compatibility verification into this delivery, and defers consumer migration with a follow-up. It doesn't reopen Kafka-vs-alternative architecture unless a real contradiction surfaces.

**Exploratory spec:** PRISM has unresolved alternatives. LENS can draft a small discovery/decision phase, but it cannot label production implementation ready. Ask which PRISM version is authoritative.

**High-stakes migration:** Compliance invariant I4 applies now even if the migration is split across three increments. Every in-scope unit must honor I4; don't postpone it just because the migration's final phase is later.

## 10. Common failures

| Failure | Better behavior |
| --- | --- |
| Copy/pasting PRISM into LENS | Link PRISM and cross-reference IDs; add only delivery decisions. |
| Treating a plan as permission to push | End with a clear handoff; execution authorization is separate. |
| Omitting deferred R# from coverage | Account for it with a concrete follow-up path. |
| Assuming unknown repository structure | Label touchpoints as proposed or inspect when authorized. |
| Confusing Tests-with-results | Plan evidence here; collect it during implementation. |
| Splitting scope.md, plan.md and handoff.md | Keep one LENS document with a brief handoff section. |
| Silently choosing between PRISM variants | Request a decision; keep provisional planning as draft. |
