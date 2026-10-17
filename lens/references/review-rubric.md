# LENS review and readiness rubric

## Verdicts

- **Ready for handoff** — source approved, plan approved, no unresolved blockers, complete references, traceable work and validation. Means *ready to hand off*, not permission to implement.
- **Draft — needs decisions** — usable outline exists, but approval or material clarification is missing.
- **Blocked — return to PRISM** — selected source is contradictory, essential guarantee is missing or the proposed slice cannot honor an approved requirement or invariant.

## Review questions

| Dimension | Strong plan | Blocker or warning |
| --- | --- | --- |
| Source | Accessible approved PRISM, chosen variant, revision when known | Unknown source / draft spec claimed approved |
| Limits | Every R# classified Now/Later/Outside with explanations | Requirements disappear without destination |
| Units | Small, outcome-oriented W# tasks in dependency order | Vague tasks, circular dependencies, ungrounded files |
| Needs | Dependencies and material decisions recorded with gates | Assumed approvals or unresolved blocking S# choices |
| Signals | Each W# tied to future evidence and relevant M# | No proof for Now work, fabricated PASS claims |
| Contract | Invariants apply; no unapproved solution or scope changes | LENS contradicts PRISM or silently relaxes a guarantee |
| Handoff | Source + next steps sufficient for new agent | Requires unstated prior conversation |

## Coaching triggers

**Too much work in W1.** Propose an independent preparatory slice, plus a testable user-visible or service-visible slice, while keeping dependencies explicit.

**R3 absent from Limits.** Ask whether R3 belongs now or in a later increment. Never silently mark it non-goal.

**I2 deferred with R4.** If I2 protects R1 Now, flag immediately: an invariant cannot be deferred with an unrelated feature.

**Two PRISM solution options.** Ask which is approved; label the LENS as Draft or Blocked until chosen.

**M3 isn't verifiable.** Propose a measurable evidence type and ask PRISM author to confirm it instead of inventing thresholds.

**No approval.** Deliver a useful Draft, not a misleading Approved document.

## Mechanical validator limitations

The included local validator can detect missing/duplicate IDs, unknown dependencies, some cycles, incomplete mappings, and missing required headings. It cannot decide whether the plan is architecturally sound, whether a claimed approval is authentic, whether the tests actually ran, or whether a blocker is truly resolved. An external execution workflow must still check repository state and seek authorization before touching code or Git.
