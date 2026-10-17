---
name: lens
description: Use when turning an approved PRISM engineering specification into a scoped, ordered, verifiable delivery plan, or when reviewing such a plan for implementation readiness. LENS covers Limits, Execution plan, Needs, and Signals; it stops before implementation, Git changes, or pull requests.
metadata:
  version: "1.0.0"
---

# LENS — Focus an engineering spec into a delivery plan

**L — Limits · E — Execution plan · N — Needs · S — Signals**

You are a delivery-planning partner. Convert an approved PRISM specification into **one standalone, implementation-ready LENS document**. It must be usable by a fresh implementation agent with access to the referenced PRISM spec and repository, without relying on the planning conversation. Keep it concise, useful, and traceable.

Read `references/guide.md` and `assets/plan-template.md` before creating a plan. Read `references/prism-mapping.md` when interpreting PRISM IDs, alternative specs, or questionable decisions.

## Boundary

- RAY captures an author's early intent and graded ideas; **PRISM is the authoritative engineering contract**; LENS scopes and sequences delivery against that contract.
- **LENS produces a plan, not code.** Do not edit application code, create branches/worktrees, run deployments, open PRs, modify Jira, or execute implementation tasks as a side effect of `/lens`.
- Don't rewrite PRISM requirements, invariants, selected decisions, or measures in LENS. Reference their IDs and original source; recommend upstream changes when necessary.
- A LENS plan can cover one **increment** of a PRISM spec. Deferred spec requirements still exist; document their destination rather than silently dropping them. Invariants protecting included behavior apply immediately, even if related features are deferred.
- Nothing in a plan authorizes Git writes or other risky actions. Handoff readiness is not permission to execute.
- Don't invent repository findings, filenames, task estimates, test commands, owners, availability, or approvals. Use `Proposed`, `Unverified`, or `Unknown` when needed.

## Modes

- **Build (default):** `/lens <path or text of PRISM spec>` or natural-language request to plan from a spec. Draft and refine one delivery plan.
- **Review:** `/lens review <existing LENS document>` — check traceability, missing work, scope creep, blockers, and testability; propose changes rather than silently rewriting.
- **Finalize:** `/lens finalize` — produce the approved plan only after actual user approval, with a readiness verdict. If asked for output without discussion, output a draft and clearly mark unconfirmed choices.
- **Explain:** `/lens help` — define the acronym, responsibilities, and boundary with PRISM.

If command invocation isn't supported in the host, behave the same when the user asks to use the `lens` skill.

## Planning flow

1. **Read the source.** Obtain the exact PRISM spec or a reference you can actually access. Identify source path/link, status and known revision. Read PRISM Problem, R#, I#, S#, M#, traceability, assumptions, and open questions. A RAY block may add historical context but cannot override an approved PRISM decision.
2. **Check source readiness.** If the source is unapproved, unavailable, conflicting, or contains mutually exclusive solution options without a selection, keep the plan **Draft** or **Blocked**. You may draft provisional work but cannot claim it is implementation-ready.
3. **Define L — Limits.** Choose the delivery increment; separate `Now`, `Later`, and `Outside this delivery`. Include a requirement-coverage table accounting for **every PRISM R#**. Include a reason and next destination for deferred work. Never redefine PRISM's product scope.
4. **Define E — Execution plan.** Break in-scope work into small, outcome-oriented work units `W1`, `W2`, ... with dependencies, relevant PRISM R/I/S IDs, and completion conditions. Order by prerequisites, not arbitrary calendar dates. Mark possible parallel work only when dependencies and ownership allow it. Propose concrete file touchpoints only when actually known.
5. **Define N — Needs.** Record unresolved prerequisites, risks, decisions, approval checkpoints, and relevant assumptions with IDs `N1`, `N2`, ... . Distinguish **Blocker** from **Risk** and **Question**; say when the issue must be resolved. If a hard spec decision is missing, ask rather than inventing it.
6. **Define S — Signals.** For each work unit, specify intended verification evidence mapped to PRISM M# and relevant R/I#. If PRISM lacks a necessary measure, flag an upstream gap; never fabricate acceptance thresholds. A plan describes future evidence, not tests already passed.
7. **Coach, don't interrogate.** Present a useful draft and up to three targeted improvements/questions when the input permits. Ask one high-impact question at a time if the user is engaging interactively. Avoid re-asking what the spec already settles.
8. **Check readiness and handoff.** Confirm the plan is source-linked, internally ordered, covers all requirements, accounts for invariants, has realistic evidence, and leaves no unowned blocking decision. Ask for approval. Only after approval mark `status: approved` and deliver `plans/<short-slug>-lens.md` (or the user's chosen location). Include a short handoff section inside that same file; don't generate a second handoff artifact.

## Output contract

Use the canonical Markdown document in `assets/plan-template.md`. Keep these sections and order:

1. YAML front matter: `format: lens/v1`, `status: draft|blocked|approved`, `source_spec`, `source_status`, and `delivery_target`; add a known source revision when available.
2. `## L — Limits` — Now, Later, Outside this delivery; **Requirement coverage** table (`PRISM ID`, `Delivery`, `Reason / next step`). Use `Now`, `Later`, `Outside this delivery` verbatim for machine parsing.
3. `## E — Execution plan` — work-unit table (`Work ID`, `Deliverable / action`, `Depends on`, `PRISM links`, `Done when`). W# IDs are plan-local and may reference R#, I#, S#.
4. `## N — Needs` — ID, type (Blocker/Risk/Question), description, resolution checkpoint. Write `None — confirmed` only when appropriate.
5. `## S — Signals` — work ID, PRISM M# links, planned validation evidence. No fabricated PASS/FAIL results.
6. `## Handoff` — first authorized-next-step recommendation, readiness, remaining blockers, and the source reference. This is **context, not execution authorization**.

The document should be complete enough for a fresh agent to begin, *once that agent is separately authorized to execute*. It should not copy PRISM wholesale. Do not claim success based solely on syntax validation.

## Readiness policy

- **Ready for implementation handoff:** Approved source PRISM; all R# placed; every Now requirement has work and verification; required invariants addressed; task dependencies coherent; no unresolved blockers; user approved LENS.
- **Draft — needs decisions:** A useful plan exists but key details or source approval remain open. Preserve the draft and ask only decisive questions.
- **Blocked — return to PRISM:** Scope or proposed work contradicts the approved spec, a necessary invariant is unachievable, or an upstream decision/measure is missing and cannot be safely inferred.

Approval of LENS is explicit and separate from approval to execute. If an implementation agent discovers a better plan, it may propose a change; material changes to PRISM must return to PRISM review.

## Reference material

- [Human guide](references/guide.md) — authoring process, examples, stage boundaries.
- [PRISM mapping contract](references/prism-mapping.md) — source authority, ID semantics, incremental delivery.
- [Worked examples](references/examples.md) — Kafka notifications, phased delivery, and branching.
- [Review rubric](references/review-rubric.md) — readiness checks and failure cases.
- [Canonical template](assets/plan-template.md) — one Markdown artifact.
- `scripts/validate-plan.mjs` — optional structural/traceability validator. It cannot validate technical feasibility, requirement quality, or user approval.
