# LENS — Practical authoring guide

> **Focus the spec; don't respecify the product.**

**LENS** means **Limits · Execution plan · Needs · Signals**. It is the final step in a small idea-to-plan workflow:

```text
RAY (intent) → PRISM (approved engineering contract) → LENS (delivery plan)
```

LENS produces **one Markdown file** (normally `plans/<slug>-lens.md`). It is a standalone handoff *with a source reference*: a new implementation agent needs that file, the linked PRISM specification, and repository access—not the conversation that created it. LENS stops before writing code, changing Git state, opening a PR, or recording implementation results. **An approved plan is not authorization to execute.**

## Quick start for an author or agent

1. **Locate the approved PRISM.** Read its Problem, every `R#`, relevant `I#`, selected `S#`, each `M#`, and remaining open questions. Record its path and known revision; never guess approval or a commit SHA.
2. **Choose one delivery target.** Is the plan for the whole spec or a useful increment? Name that target before listing tasks.
3. **Draft L — Limits.** Classify *every* PRISM `R#` as `Now`, `Later`, or `Outside this delivery`, with a defensible reason and next destination where applicable.
4. **Draft E — Execution plan.** Break `Now` into a few independently understandable `W#` work units with dependencies, PRISM links, and observable completion conditions.
5. **Draft N — Needs.** Surface only material blockers, risks, and questions; state **when** each must be resolved.
6. **Draft S — Signals.** Define the *future evidence to collect* for every `W#`, linked to the approved PRISM `M#` measures.
7. **Review, then approve.** Ask only questions that change the plan. Mark `approved` only after explicit user approval, and include the short Handoff section in the same document.

To start a conversation: `/lens specs/event-notifications-prism.md`. To critique a plan: `/lens review plans/event-notifications-lens.md`.

## Reading PRISM correctly

| PRISM source | What LENS takes from it | What remains PRISM's job |
| --- | --- | --- |
| Problem | The outcome being served and original product boundaries | Deciding which problem to solve |
| Requirements `R#` | Complete inventory for delivery coverage | Defining required behavior |
| Invariants `I#` | Protections that apply to all included work | Defining non-negotiable guarantees |
| Solution `S#` | Approved technical direction and allowed freedom | Choosing or changing the solution |
| Measures `M#` | Proof the delivery must make possible | Setting acceptance criteria and thresholds |
| Traceability / open questions | Relevant links and blockers | Resolving contract-level ambiguity |

**RAY's graded Angle is historical context, not a substitute for PRISM approval.** For instance, Kafka could have been a `[3:Strong]` preference in RAY and later rejected during PRISM. LENS follows the approved `S#`, not the original preference. If PRISM presents competing unselected solutions, LENS may draft a decision-making plan, but cannot call a production implementation plan ready.

## A worked example: notification expansion

Assume an *illustrative*, approved PRISM establishes:

- `R1`: publish domain-change events to new subscribers;
- `R2`: support migrating existing consumers later;
- `I1`: existing consumers must remain compatible;
- `S1`: use a dedicated Kafka topic;
- `M1`: an integration test demonstrates publication;
- `M2`: an existing-consumer contract test demonstrates compatibility.

We want the **first delivery increment**, not the entire consumer migration. Here's what each section should contain—and *why*.

## L — Limits: decide what this delivery does and does not promise

**Author's question:** “Which part of the approved outcome are we delivering now?”

```md
## L — Limits

### Now
- Publish the new domain-change events for new subscribers.
- Preserve existing consumer behavior during the addition.

### Later
- Migrate current consumers in a follow-up delivery increment.

### Outside this delivery
- Unrelated redesign of the event publisher platform.

### Requirement coverage
| PRISM ID | Delivery | Reason / next step |
| --- | --- | --- |
| R1 | Now | W1 and W2 deliver event publication |
| R2 | Later | Separate consumer-migration increment; ownership to be confirmed |
```

**Why these notes matter:** `Now` is a deliverable commitment, not a wish list; `Later` preserves a real PRISM obligation and names its destination; `Outside this delivery` prevents adjacent work from silently expanding the effort. The coverage table lets a fresh agent spot a dropped `R#`.

**Important distinctions:**

- **Product scope ≠ delivery scope.** PRISM owns the complete product promise. LENS describes this delivery increment.
- `Later` is a deferred requirement with a destination, **not canceled**. `Outside this delivery` is usually an adjacent non-goal; if it applies to an approved `R#`, it still needs a path to fulfillment and cannot simply disappear.
- **Invariants cannot be deferred just because features are.** If `I1` protects `R1` today, the first increment must satisfy `I1` today.
- Do not claim “PRISM complete” after shipping only the first increment. Say “increment complete” instead.

**Weak:** `R2 | Outside this delivery | Not doing it.`

**Better:** `R2 | Later | Separate migration increment; identify its owner before declaring the overall PRISM outcome complete.`

## E — Execution plan: make the delivery actionable

**Author's question:** “What small outcomes must be produced, and which depend on others?”

```md
## E — Execution plan

| Work ID | Deliverable / action | Depends on | PRISM links | Done when |
| --- | --- | --- | --- | --- |
| W1 | Establish the agreed event contract and topic configuration | None | R1, S1, I1 | Publication contract and configuration are ready for integration |
| W2 | Add event publication through the approved topic | W1 | R1, S1, I1 | Domain changes produce the intended events without altering existing consumer behavior |
| W3 | Add publication and compatibility checks | W1, W2 | R1, I1 | Automated checks exercise the required publication and compatibility behavior |

Sequence notes: W1 is prerequisite to W2. Test design for W3 may start alongside W2 once W1 is stable; final integration evidence requires W2.
```

**Why these notes matter:** An implementer can tell what to accomplish without being told every line of code to change. The dependencies explain the sequence; the PRISM links explain the authority; **Done when** states the expected outcome, not whether a test has already passed.

Practical writing rules:

- Prefer **one coherent, reviewable outcome per `W#`**. If `W1` includes storage migration, producer changes, four consumers, and rollout, it is probably too large.
- List prerequisites using real `W#` IDs, or `None`. “Do this first” is not a dependency unless it names the work it blocks.
- Reference applicable `R#`, `I#`, and `S#`; never invent PRISM IDs to make a table look complete.
- Treat suggested file paths, test commands, task duration, ownership, or parallel safety as **proposed** until repository inspection or another source supports them.
- Avoid making every internal coding step a row. LENS is a delivery plan, **not a line-by-line patch recipe**.

**Weak:** `W1 | Implement Kafka | None | R1 | Finished.`

**Better:** `W2 | Publish domain-change events to approved topic | W1 | R1, I1, S1 | New subscribers can consume events while existing consumer behavior stays unchanged.`

## N — Needs: record friction with a resolution point

**Author's question:** “What must someone decide, confirm, or watch before this plan can succeed?”

```md
## N — Needs

| Need ID | Type | Description | Resolve before |
| --- | --- | --- | --- |
| N1 | Question | Confirm who owns the later consumer-migration increment | Closing overall PRISM delivery |
| N2 | Risk | Changes to shared publishing code could affect existing consumers; retain the compatibility check and plan a safe fallback | Completing W2 |
```

**Why these notes matter:** The next agent sees what is known, what is merely possible, and what would actually block progress. The “Resolve before” column prevents low-priority unknowns from being treated like emergency gates.

Use these types carefully:

| Type | When to use | Example |
| --- | --- | --- |
| **Blocker** | Can't responsibly start or finish affected work without resolution | The PRISM solution variant has not been selected |
| **Risk** | Work can proceed, but a plausible failure needs mitigation | Publisher changes might disrupt existing consumers |
| **Question** | Helpful missing information with a clear checkpoint | Who owns a later increment? |

Never invent a blocker to fill the table. If the author confirms no material issues remain, write **`None — confirmed`**. If a hard PRISM invariant or required solution decision is missing, flag the upstream gap rather than resolving it by assumption inside LENS. A plan with an **unresolved blocker** is not ready for approval.

## S — Signals: name proof that will be collected later

**Author's question:** “For each work unit, what evidence will demonstrate the relevant PRISM measures?”

```md
## S — Signals

| Work ID | PRISM measures | Evidence to collect |
| --- | --- | --- |
| W1 | M1 | Inspect agreed event contract and publication configuration during integration verification |
| W2 | M1, M2 | Record integration test output for publication and existing-consumer compatibility |
| W3 | M1, M2 | Record results of the automated publication and compatibility checks |
```

**Why these notes matter:** `Done when` describes a completion condition; **Signals** identifies the proof to collect to support it. Both are needed for a good handoff, but neither invents a test result before implementation.

Practical rules:

- Every `W#` should have a Signals row linked to one or more real PRISM `M#` measures. Preparatory work can identify the later verification it enables rather than inventing a new acceptance target.
- Name the evidence type: integration-test output, contract-test result, benchmark, scenario recording, metric, inspection, or other approved proof.
- Don't replace a PRISM threshold with a new number. If `M2` is too vague to prove compatibility, return that gap to PRISM.
- Never put `PASS`, `validated`, or a fabricated timestamp into a pre-implementation plan.

**Weak:** `W2 | M1 | Tests pass.`

**Better:** `W2 | M1, M2 | Capture the integration-test and compatibility-contract results for the new publishing path.`

## Handoff: the closing note inside the *same file*

Handoff is **not another skill, another planning document, or another letter**. It simply tells an implementation agent where to begin and what the planning stage established.

```md
## Handoff

- **Readiness:** Ready for implementation handoff (after explicit plan approval)
- **Next step:** With separate execution authorization, inspect existing publishing interfaces, then begin W1.
- **Remaining blockers:** None — confirmed
- **Authority:** The linked PRISM spec owns requirements, invariants, solution, and measures. LENS approval does not authorize code or Git changes.
```

Every finished document also needs YAML front matter:

```yaml
---
format: lens/v1
status: approved
source_spec: specs/event-notifications-prism.md
source_status: approved
delivery_target: Initial event publication increment
# source_revision: <only when known>
---
```

Those values are **illustrative**, not defaults. Use `status: draft` until the user actually approves the plan. Use `source_status: unknown` if approval is unverified. Never fabricate a `source_revision`.

## Good coaching: recommendations and questions, not a second PRISM interview

After reading the spec, the agent should show a **useful first draft**, then a small number of genuinely consequential suggestions. For the Kafka example:

- **Recommendation:** Defer consumer migration while keeping compatibility checks in the first increment; `I1` applies now.
- **Recommendation:** Break a broad “add Kafka support” task into publication contract, producer integration, and verification work units.
- **Question:** Is the Kafka topic configuration already provisioned, or is provisioning part of W1?
- **Question:** Who will own the follow-on consumer migration? This may remain open without blocking the first increment.

Ask **one high-impact question at a time** during conversation, at most three when presenting a draft. Do not ask for details PRISM has already answered. If the requester wants a one-pass plan, deliver a clearly marked draft with visible assumptions rather than pretending it is approved.

## When to stop and return to PRISM

| Discovery during LENS | Correct action |
| --- | --- |
| `S1` and `S2` are competing, unapproved architectures | Draft only; ask which variant is authoritative or plan an explicitly authorized investigation |
| A proposed delivery slice violates `I1` | Block the plan; revise the slice or request PRISM review |
| A critical PRISM `M#` has no meaningful way to be measured | Flag the specification gap; don't invent acceptance thresholds |
| A `R#` is impossible to deliver within the proposed increment | Assign Later with a real next destination, or revisit the increment; never erase `R#` |
| Repository findings disprove a planning assumption | Update LENS and, if they change the product contract, return to PRISM |
| The user has not approved LENS | Keep `status: draft`, even if every structural validator check passes |

## A one-minute review before handoff

Ask whether a fresh implementation agent can answer **all** of the following using only this LENS, the referenced PRISM, and the repository:

1. Which approved spec and version governs the plan? Which delivery increment is this?
2. Where is every `R#` going: `Now`, `Later`, or `Outside this delivery`?
3. Which `W#` implements each `Now` requirement, protects relevant `I#`, and follows approved `S#`?
4. What are the work dependencies and genuine blockers? Are estimates and filenames grounded rather than guessed?
5. Which PRISM `M#` and specific evidence will prove each `W#`?
6. Did the user explicitly approve the plan? Is execution authorization still separate?

A structurally valid LENS can still be an unwise plan. The included validator checks shape and some ID links, **not feasibility, authority, security, or user approval**.

## Keep the plan proportionate

A one-requirement PRISM might need one `W1`, `N — None — confirmed`, one verification row, and a short handoff. Don't invent milestones, diagrams, owners, risk registers, or extra documents to make it look substantial.

**What LENS is not:** a second spec, a Jira-ticket generator, a research report, a code editing checklist, a Git workflow, or a post-implementation review. It is the smallest *defensible delivery plan* that preserves the approved PRISM contract.

For further examples, see [`examples.md`](examples.md). For source-ID and version-change rules, see [`prism-mapping.md`](prism-mapping.md). The review checklist is also summarized in [`review-rubric.md`](review-rubric.md).
