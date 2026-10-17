# RAY — Engineering Intent Guide

**Version:** 1.0

**Position in the workflow:** Jira story intent → discovery and optional alternatives → PRISM specification(s) → planning/implementation

**Purpose:** Give an engineering agent enough *authored intent* to start a specification, including initial technical leanings, without making a premature implementation commitment.

> **RAY states where you want to go, why it matters, and how firmly you hold any early directions. It is a starting position—not a miniature PRISM spec and not a contract to implement the first idea.**

## 1. The three questions

| Field | Question | Good answer | Avoid |
| --- | --- | --- | --- |
| **R — Result** | What should become true, and for whom? | An observable outcome, behavior or capability. | A task list or proposed technology standing in for an outcome. |
| **A — Angle** | Which directions or early decisions do I have, and how strongly do I stand behind each? | Zero or more specifically graded ideas, choices or binding conditions. | Treating every early idea as mandatory; invented approaches to fill the field. |
| **Y — Why** | What existing problem or opportunity makes this worthwhile? | Present observation, affected people/systems, impact or consequence of inaction. | Circular justification, fabricated urgency, untested causes stated as facts. |

RAY's optics metaphor is intentional: a ray enters a prism; a single intent can refract into distinct specifications. The *same* R and Y can be the trunk of two technically different PRISM options. A should not prevent that branching unless an explicit requirement truly does.

**Use RAY at the top of a Jira ticket description, before PRISM exists.** RAY does not replace Jira's title, task metadata, linked evidence or additional context elsewhere in the ticket.

## 2. Decision strength: grades 1–4

Grade **individual Angle statements**, not the RAY block as a whole. These grades indicate **strength of commitment**, not likelihood of success or the writer's technical confidence.

| Grade | Label | What the author means | What an agent may do |
| --- | --- | --- | --- |
| **1** | **Consider** | An idea, possibility or hypothesis; no endorsement implied. | Explore or discard; compare freely. |
| **2** | **Prefer** | This seems promising; a mild leaning. | Give it fair consideration, but offer other approaches freely. |
| **3** | **Strong** | This is the expected/default direction, but I want to be persuaded if something is better. | Use as a baseline; challenge or replace with a clear tradeoff explanation. |
| **4** | **Required** | A deliberate binding decision or boundary *for this story*. | Do not silently override. Flag conflicts and request explicit authorization to change it. |

**Important distinctions:**

- **3 is not 4.** “I want a new Kafka topic unless you can convince me otherwise” is **3 — Strong**, even if the author is quite confident.
- **4 is not immutable truth.** A human with authority can revise it. The agent cannot revise it silently, and PRISM must verify any claimed technical, security or policy invariant.
- **Grade each assertion separately.** A feature may have a strongly preferred Kafka topic (3), a weak preference for an existing publisher (2), and a required compatibility boundary (4).
- **No directions is valid.** Write `A — Angle: Open — no early decisions yet.` Do not invent a grade or architectural option merely to fill A.
- **Grades aren't additive.** Two grade-2 preferences do not outrank a grade-4 requirement.
- If something is framed as **4 — Required**, specify the source or owner where known (e.g., contract, architecture decision, approved policy, named sponsor). An unsupported claim should be marked for verification, not quietly treated as an established fact.

## 3. Canonical Jira-ready format

Use these **three exact field labels**. A one-paragraph R and Y are preferred. A may have any number of separately graded statements, though 0–3 is a good default.

```text
Intent
R — Result: <desired outcome and who benefits>
A — Angle:
- [3:Strong] <early decision; it can be challenged with a better case>
- [2:Prefer] <optional preference>
- [4:Required] <binding boundary; cite authority if known>
Y — Why: <observed problem/opportunity, impact, consequence of doing nothing>
```

For a genuinely open-ended story:

```text
Intent
R — Result: <desired outcome>
A — Angle: Open — no early decisions yet.
Y — Why: <why this outcome matters>
```

If the Jira description contains other material, put it under a **separate heading after the block** (e.g., `Context`) and do not interleave unrelated notes between the RAY fields. Markdown `## Intent` is also recognized by the optional linter; plain `Intent` avoids relying on Jira's Markdown rendering.

Only R, A and Y are RAY fields. Don't quietly add fields called Scope, Constraints, Evidence, Acceptance Criteria, Implementation or Success Metric. Link to additional context elsewhere in the ticket as needed.

## 4. How to write a strong R

Start with the human, service or operational actor that should experience a change and describe the result that should be true.

**Weak:** `R — Result: Add a Kafka topic.`

**Stronger:** `R — Result: Downstream services can react to new catalog changes without tight coupling to the producing service.`

Then place the Kafka suggestion in A with the appropriate grade. This keeps the desired result separate from a chosen implementation.

Don't demand numerical thresholds yet. PRISM Measures is the right place for quantified success criteria. When a target is already genuinely binding, it can be linked or described in RAY without expanding into a complete acceptance-criteria list.

## 5. How to write a strong A

Angle is deliberately allowed to contain technology and early engineering decisions. The mistake isn't mentioning a solution; the mistake is **failing to distinguish a suggestion from an instruction**.

```text
A — Angle:
- [3:Strong] Introduce a dedicated Kafka topic. This is my expected route, but evaluate materially better options.
- [2:Prefer] Extend the existing publisher instead of building a separate service, where reasonable.
- [4:Required] Existing event consumers must remain compatible during rollout (approved integration requirement).
```

A can also describe two equally plausible options:

```text
A — Angle:
- [1:Consider] Registry-owned workflow metadata.
- [1:Consider] Repository-owned workflow metadata.
```

These are options to investigate, **not orders to build both**. The Spec workflow can compare them or produce separate PRISM variants if the approaches are materially different. The branching decision is workflow logic, not an additional RAY field.

For hard boundaries, distinguish the requirement from the route to meeting it. “Must preserve auditing” may be a genuine boundary; “must implement a new audit microservice” is an implementation choice unless a verified external obligation actually mandates it.

## 6. How to write a strong Y

Y should give the spec author the motivation and enough context to investigate.

**Weak:** `Y — Why: We need this feature.`

**Better:** `Y — Why: Each new downstream integration currently requires producer-specific coordination, slowing onboarding and increasing release coupling.`

If a cause is unverified, signal uncertainty inside Y:

`Y — Why: Several new teams stall during onboarding. We suspect access provisioning is the main cause, but have not confirmed it.`

Do not manufacture “why now” when the problem is longstanding. If a deadline, outage or business trigger truly matters, include it naturally. An opportunity, not just a current failure, can be sufficient motivation.

## 7. How a bot should coach the author

The `/ray` interaction should feel like working with a thoughtful engineer, not filling out a form.

1. **Receive rough language.** The author may give a title, messy notes, a Jira ticket or an existing RAY.
2. **Draft immediately when possible.** Show a provisional three-field block, preserving the author's intentions and uncertainty. If there's no usable idea at all, ask one opening question.
3. **Challenge gently but concretely.** Identify up to three high-value improvements: outcome vs implementation, observed problem vs suspected cause, and preferences vs requirements.
4. **Ask only the important questions.** Usually one to three concise questions. Prioritize missing outcome, affected user/system, motivation, decision strength and authority of any grade-4 item. Do not re-ask answered questions.
5. **Offer options, not invented facts.** “Should Kafka be 2, 3 or 4?” is useful. “Kafka definitely scales better” without evidence isn't.
6. **Refine collaboratively.** After answers, produce a paste-ready block and a short readiness assessment. If an open question isn't fatal, surface it without preventing handoff.
7. **Stop at the boundary.** Don't generate PRISM sections, implement code, create a branch or write to Jira unless the user separately requests the action and the runtime has the necessary tools and permissions.

An agent should distinguish **suggestions**, **questions** and **the actual Jira-ready Intent**. Recommendations and coaching stay **outside** the paste-ready block.

### Useful questions by failure mode

| Failure mode | Targeted coaching question |
| --- | --- |
| Result is a task | “What would become possible for the consumer if that task succeeded?” |
| Result is vague | “Who should experience this change, and what would be different?” |
| Angle is ungraded | “Is this worth considering (1), preferred (2), your default (3), or required (4)?” |
| Contradiction in A | “You marked Kafka required but said you are open to alternatives. Should this be a 3?” |
| Why is an assumption | “Is that the observed failure, or your current theory about its cause?” |
| Hard boundary | “Who or what makes this required? Is there a policy, contract, dependency or decision to reference?” |
| Two options | “Do you want the spec process to compare these, or develop distinct options if they cannot be combined?” |

## 8. Readiness for a PRISM specification

A RAY is **ready enough** to begin discovery/spec writing when:

- R expresses a meaningful desired outcome, not only a named implementation.
- Y provides a defensible motivation; uncertain causes are labeled as uncertain.
- A is either explicitly open or its individual decisions carry grades.
- Conflicting statements and truly binding boundaries are surfaced.
- The agent could reasonably investigate at least one solution without inventing the requester's goal.

**Not required at the RAY stage:** detailed scope, tickets, implementation steps, interfaces, measured acceptance criteria, technical solution validation, or certainty about the preferred approach.

Use three lightweight readiness states in conversation (not inside RAY):

- **Ready for PRISM exploration:** enough intent exists; unresolved details can be investigated.
- **Ready with assumptions:** some assumptions are flagged and carried as questions for discovery.
- **Needs clarification:** the objective, motivation or grade-4 authority is so unclear that proceeding would likely specify the wrong thing.

The agent's readiness opinion is not another RAY grade.

## 9. Relationship with Shipwright / PRISM

The upstream interface is intentionally small:

- **R →** informs desired outcome and eventual Requirements/Measures; do not equate R with finalized requirements.
- **Y →** informs Problem and why the work matters; separate observed symptoms from hypothesized causes.
- **A grade 1–2 →** candidate directions; exploration only, not mandatory requirements.
- **A grade 3 →** initial solution baseline; either justify retaining it or explicitly explain a superior alternative.
- **A grade 4 →** asserted hard decision/boundary; verify its source before formalizing as an Invariant or constraint. Seek explicit human approval before overriding.

PRISM's **Problem → Requirements → Invariants → Solution → Measures** is defined by its own skill and review process. RAY isn't supposed to pre-populate every PRISM section without investigation.

When there are two credible solution routes, a Spec workflow may compare them, then create **Spec A** and **Spec B** against the same R/Y trunk if requested or warranted. Do not interpret multiple Angle bullets as multiple mandatory implementations.

## 10. Anti-patterns to reject

- **Feature disguised as Result:** `R: Create an endpoint.` Ask for the capability it enables; move endpoint idea into A.
- **All ideas marked Required:** Usually defeats the point of upstream intent. Confirm whether any are actually a 3.
- **Conflating confidence and commitment:** “I'm 95% sure” doesn't automatically mean grade 4.
- **Pretending unknowns are facts:** Put uncertainty into Y, and let PRISM investigate.
- **Inventing an Angle:** “We have no ideas” is a good, valid Angle.
- **Score-based automation:** Do not average, sum, rank or automatically choose solutions by 1–4 grades.
- **Premature rigor:** Don't require a repository scan, implementation plan or acceptance test before authoring RAY.

## 11. A complete worked example

Original requester note:

> We need to expand events for new integrations. I want a new Kafka queue/topic because that's what we already use, but if there's a radically better approach I'd listen. Must not break the teams currently consuming events. Things are too coupled right now.

Good RAY:

```text
Intent
R — Result: New downstream integrations can react to domain changes without requiring producer-specific coordination.
A — Angle:
- [3:Strong] Use a dedicated Kafka topic for the new event stream; this is the expected approach, but better alternatives can replace it with justification.
- [4:Required] Preserve existing consumer compatibility during migration (requester-confirmed integration constraint; validate details during PRISM).
Y — Why: Today each new integration increases coupling and coordinated release work between producers and consumers, making expansion slower and riskier.
```

Good coaching responses:

- **Recommendation:** Keep “Kafka” in A, not R, so it remains challengeable.
- **Clarification:** Is a new Kafka *topic* required, or merely your favored implementation? You've described it as a **3 — Strong**.
- **Clarification:** Who owns the compatibility requirement, and which consumers are affected? The agent can begin discovery before those are fully enumerated.

**Outcome:** a usable PRISM starting point with meaningful human direction—without pretending architecture or acceptance criteria have already been decided.
