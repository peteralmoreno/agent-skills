# RAY Examples: rough ideas, refined intents, useful coaching

These are illustrative. Do not assume that the technologies, failure modes or organizational requirements described here are present in a real project without evidence.

## A. Strong Kafka preference, alternatives welcome

**Rough note:** "I want the new feature to use a separate Kafka queue/topic. The old consumers cannot break. Still open to a great idea that isn't Kafka."

```text
Intent
R — Result: New consumers can react to domain changes without requiring producer-specific coordination for every integration.
A — Angle:
- [3:Strong] Publish the new change events to a dedicated Kafka topic; this is the expected direction, but alternatives can displace it with a compelling explanation.
- [4:Required] Preserve compatibility with current event consumers during rollout (requester-confirmed; identify authoritative compatibility contracts during PRISM).
Y — Why: Adding integrations currently increases coordination and release coupling between producers and consumers.
```

**Recommendations:** Keep Kafka out of R so the agent can challenge it. Verify whether this is a *topic* in an existing Kafka deployment rather than a genuinely new *queue*; the distinction matters later but needn't block Intent.

**Question:** "Which existing consumer contracts define the compatibility boundary?"

## B. Vague story, poorly framed as a task

**Rough note:** "Fix onboarding by making a new setup wizard."

**Provisional draft:** The beneficiary and support burden below are proposed assumptions, not facts established by the rough note. Confirm them with the author.

```text
Intent
R — Result: First-time workspace owners can complete initial setup with less manual support.
A — Angle:
- [2:Prefer] Consider a guided setup wizard; other causes of onboarding friction may need different remedies.
Y — Why: Initial setup appears to need improvement; the affected steps, impact, and causes need confirmation.
```

**Recommendations:** Move "wizard" out of R. Don't assume onboarding failure is exclusively a UI problem.

**Questions:** "Which step causes the most trouble?" and "Is the setup wizard your default (3), or just a possibility (1–2)?"

## C. Fully exploratory change

**Rough note:** "We know workflows get orphaned, but don't know why. Help us make that visible."

```text
Intent
R — Result: Teams can identify when a workflow lacks a clear owner and route it for resolution.
A — Angle: Open — no early decisions yet.
Y — Why: Some workflows outlive the teams or people responsible for them, leaving escalation and maintenance responsibility unclear. The primary cause is unknown.
```

**Recommendations:** Keep A open. Investigate registry state, source-of-truth ownership and operating processes while writing PRISM.

**Question:** "Who needs to recognize the ownership gap first—workflow operators, team leads or support?"

## D. Branching: two viable directions, one intent

**Rough note:** "We need better accountability. Maybe put ownership in the repo or platform registry. Either way."

```text
Intent
R — Result: Teams can discover and transfer workflow ownership without losing accountability.
A — Angle:
- [1:Consider] Ownership stored alongside the workflow's repository metadata.
- [1:Consider] Ownership stored in the central workflow registry.
Y — Why: Ownership is inconsistent across systems, which complicates routing and handoffs when a team changes.
```

**Downstream behavior:** Compare both; create PRISM-A and PRISM-B only if the user requests it or there is a meaningful tradeoff to investigate. Both variants keep the same intended R/Y. A is an options menu, not a list of features to combine.

**Question:** "Should the spec workflow evaluate both in one discovery pass, or produce competing variants?"

## E. High-stakes security change

**Rough note:** "Emergency credential rotation is too slow. We can't bypass separation of duties and audits."

```text
Intent
R — Result: Authorized responders can rotate emergency credentials promptly while preserving required access controls.
A — Angle:
- [4:Required] Preserve documented separation-of-duties approval and auditability (policy reference to be confirmed before PRISM formalizes an invariant).
- [1:Consider] Automate the credential-rotation steps that don't require human approvals.
Y — Why: Current emergency rotations take too long and produce inconsistent operational evidence of authorization.
```

**Recommendations:** Do not downgrade grade 4 for convenience. Ask which policy governs it; PRISM must verify the policy text and distinguish authoritative obligations from assumptions.

**Question:** "Which controls are mandatory, and can we reference their owner or policy?"

## F. High confidence, low commitment

**Rough note:** "I'm basically certain moving this to background jobs is the right fix, but I want a creative agent to surprise me."

```text
Intent
R — Result: Users can initiate large exports without waiting for the full export to finish in the request path.
A — Angle:
- [3:Strong] Move export processing to asynchronous jobs; expected design, but alternatives are explicitly welcome.
Y — Why: Large exports currently keep user-facing requests open too long, harming responsiveness and reliability.
```

**Lesson:** Feeling 95% certain isn't a 4. Grade 3 still permits challengers.

## G. An outcome masquerading as urgency

**Rough note:** "Get this done ASAP. Everyone wants the dashboard."

**Bot behavior:** Don't invent a Why. Ask one high-value question: "What decision or action is hard today without the dashboard?" If no answer is available, a provisional result is fine but mark the real problem as unconfirmed outside the block.

**Only after the author confirms batch operations as the context**, a draft could be:

```text
Intent
R — Result: Operations staff can see the status of active batch processing without assembling information across tools.
A — Angle:
- [2:Prefer] A unified status dashboard seems useful; the mechanism is not decided.
Y — Why: Operators currently rely on multiple tools to understand batch progress. The cost and frequency of this problem need confirmation.
```

**Lesson:** RAY can start exploration without fictitious severity, deadlines or acceptance criteria.

## H. Hard implementation mandate and no openness

**Rough note:** "Contractually, the external platform must receive data over SFTP, and that isn't negotiable."

```text
Intent
R — Result: The external partner receives the required export data reliably and on the agreed schedule.
A — Angle:
- [4:Required] Deliver exports using SFTP as specified by the partner contract (contract section/reference to be supplied and verified).
Y — Why: The partner cannot accept our current delivery mechanism, preventing the planned integration.
```

**Lesson:** RAY does support a fixed early technical decision when it is genuinely binding. The agent should optimize inside that boundary, not try to be clever by discarding it.
