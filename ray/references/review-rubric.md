# RAY Review Rubric

The purpose of the review is to **improve fidelity to the requester's intent**, not to turn RAY into a comprehensive template.

## Pass / revise / stop

| Check | Strong | Needs coaching | Hard blocker |
| --- | --- | --- | --- |
| Result (R) | Identifies the change that should become true for a consumer or system. | Vague adjective (“better”) or implementation task substituted for outcome. | No discernible desired outcome; author may want contradictory things. |
| Angle (A) | Open, or every early decision individually graded 1–4. | Ungraded solution, everything declared required, weak distinction between idea and constraint. | A grade-4 requirement conflicts with explicit requester's permission to deviate; cannot resolve without clarification. |
| Why (Y) | States observed problem/opportunity and useful impact. | Restates R; makes a causal assumption sound verified. | No coherent motivation, or mutually contradictory problem statements. |
| Trustworthiness | Hypotheses and sources are honestly identified. | Questionable assertions or unverified policy mandates. | Agent would have to invent critical facts to write any meaningful spec. |
| Freedom | Grade 1–3 may be challenged; grade 4 has explicit override route. | Suggested technology anchors exploration too narrowly. | Agent is instructed to bypass a stated hard boundary without authorization. |

A linter can only verify structure. A co-author should also test whether someone else could create a meaningful PRISM investigation from the RAY as written.

## Default coaching pattern

When a user provides rough notes, use this order:

1. **Draft RAY** immediately if possible.
2. **Up to three recommendations:** each points to something specific in the draft, with a reason.
3. **Up to three questions:** only answers that change the intent or decision grades. If little information exists, ask just one first.
4. **Revise on reply**, preserve user choices, and offer a final paste-ready block.

### High-value questions

- “What becomes easier/possible, and for whom?”
- “Is Kafka an idea (1), preference (2), default (3), or genuinely binding (4)?”
- “Would a technically superior alternative be welcome? If yes, that sounds like a 3 rather than a 4.”
- “Is the stated cause observed or suspected?”
- “Who owns this requirement, and where is it documented?”
- “Are these two approaches options to compare, or must they both exist?”

### Anti-patterns in agent behavior

- Interrogating the user with 10 questions before offering a draft.
- Increasing grades because the agent agrees with the proposed approach.
- Inventing requirements, deadlines, customer impact, or architecture facts.
- Turning an illustrative possible approach into a committed PRISM design.
- Treating grade 4 as verified policy just because the requester typed it.
- Blocking exploratory tickets because there is no Angle.
- Silently writing to Jira, starting coding, creating a branch or selecting a PRISM variant.

## Readiness message (outside the RAY block)

- **Ready for PRISM exploration:** the author-owned outcome and motivation are sufficiently concrete and decision latitude is clear.
- **Ready with assumptions:** a viable first spec investigation exists, but the author/agent should carry named assumptions into discovery.
- **Needs clarification:** without a specific missing answer, the agent is likely to solve the wrong problem or violate a claimed grade-4 condition.

Keep this readiness status conversational; it is not a fourth field or a numeric score.
