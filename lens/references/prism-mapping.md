# PRISM → LENS mapping and contract

LENS consumes a **chosen, approved PRISM spec**, as defined by the sibling [`prism` skill](../../prism/SKILL.md). The following is an intended local skill contract, not an existing Shipwright service integration.

| PRISM component | How LENS uses it | What LENS must not do |
| --- | --- | --- |
| Problem | Preserve outcome and affected parties as planning context | Reframe the original problem to match an easier plan |
| Requirements `R#` | Cover all IDs in Limits; connect Now IDs to W# | Cancel or downgrade requirements |
| Invariants `I#` | Apply all relevant protections to Now work units | Mark mandatory invariants as optional or defer them |
| Solution `S#` | Plan against the approved decision, with scope-appropriate tasks | Turn an unapproved alternative into a selected architecture |
| Measures `M#` | Link each work unit to planned evidence | Invent acceptance thresholds or claim execution success |
| Traceability | Maintain the `R# → I# → S# → M#` relationships when relevant | Invent phantom IDs or substitute plan W# for PRISM requirements |
| Assumptions/open questions | Surface genuinely blocking uncertainty in Needs | Treat a guess as user approval |

## Plan ownership versus specification ownership

PRISM defines the **product promise**. LENS defines the **delivery slice** and **sequence** by which that promise will be pursued. A single PRISM may give rise to one or several LENS increments.

A deferred requirement is still a required outcome. Specify its destination (another increment, explicit follow-up issue, or unresolved delivery ownership). If delivery will be called complete before all R# are fulfilled, distinguish **increment complete** from **PRISM outcome complete**.

## Stable references and version drift

Use `source_spec` as a stable project-relative Markdown path or an accessible URL. Record `source_revision` (Git commit, tagged document version, or other stable revision) when known. Never fabricate one. Before execution, the consumer should verify that PRISM is still authoritative; if it has materially changed, re-evaluate LENS coverage, W# work and Signals.

The validator can inspect a local PRISM source when provided `--prism <path>`. It validates only mechanical references, not semantic equivalence or source approval.

## RAY Angle grades

RAY decisions are context. Grades 1–3 are not binding architectural requirements merely because they appeared in the original Intent. A RAY grade-4 claim should have been validated by PRISM. LENS follows **approved PRISM** rather than deciding from RAY on its own. If the sources conflict, flag the conflict for a human decision.

## Plan contract for external agents

The downstream agent needs only:

1. The LENS Markdown file, including a source reference, delivery target and readiness status.
2. The referenced approved PRISM spec, for the authoritative product/technical contract.
3. Repository access and any separate execution policy/authorization.

It does **not** require access to the chat or upstream RAY text. It may map W# units into tickets or implementation tasks using its own authorized process; LENS itself neither creates those tickets nor imposes a Git workflow.

## Open decisions and competing solutions

- If the PRISM S view holds **alternative options** rather than an approved selected design, LENS can plan decision-making but **not** claim a ready implementation plan.
- If different PRISM variants share one RAY, name exactly which variant the plan uses. Don't blend the requirements of A and the solution of B silently.
- If an implementation insight requires a material R/I/S/M revision, propose returning to PRISM and recording the new decision; do not silently patch PRISM from within LENS.
