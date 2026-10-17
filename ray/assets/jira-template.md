# RAY Jira template

Copy this to the **top** of a Jira story description and replace the placeholders. Remove unused Angle bullets. A is allowed to be open.

```text
Intent
R — Result: <what should become true; who benefits>
A — Angle:
- [1:Consider] <possible approach>
- [2:Prefer] <mild preference>
- [3:Strong] <expected approach, open to convincing alternatives>
- [4:Required] <binding condition; owner/source if known>
Y — Why: <observed problem/opportunity, affected party, impact>
```

If there is no early engineering direction, replace A and its bullet lines with:

```text
A — Angle: Open — no early decisions yet.
```

## Filled example

```text
Intent
R — Result: New downstream systems can respond to account lifecycle events without producer-specific integration work.
A — Angle:
- [3:Strong] Introduce a dedicated Kafka topic for the new events; this is our baseline, not an irrevocable choice.
- [2:Prefer] Reuse existing publishing infrastructure when practical.
- [4:Required] Existing consumers remain compatible during the transition (owner-confirmed; contract details pending verification).
Y — Why: Every new integration currently requires coordination with the producing team, slowing delivery and increasing coupling.
```

Keep discussion, recommendations, assumptions, links and other Jira context **outside** the Intent block, under another heading.
