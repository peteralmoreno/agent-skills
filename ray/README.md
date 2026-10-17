# RAY — engineering intent coach

**RAY** is a lightweight, human-authored intent for a Jira engineering story **before** a specification exists. It lives at the top of the ticket description.

- **R — Result:** The desired outcome and who benefits.
- **A — Angle:** Early directions or decisions, graded **individually** by strength of commitment.
- **Y — Why:** The current problem or opportunity and its impact.

RAY is independent of other skills. It makes a strong starting point for [PRISM](../prism/) without generating a PRISM specification, planning work, or changing Jira by default.

## Use

In Claude Code, invoke the installed skill with `/ray` (or `/ray <rough story idea>`). In Codex, use `$ray`. In other skills-enabled agents, ask to use the `ray` skill. For oh-my-pi, use `/skill:ray` or install the [optional command alias](integrations/oh-my-pi/README.md).

The coach drafts a provisional RAY, shares up to three concrete recommendations, asks only questions that materially improve it, and finalizes a paste-ready Intent on request.

```text
Intent
R — Result: New downstream systems can react to domain changes without producer-specific coordination.
A — Angle:
- [3:Strong] Start with a dedicated Kafka topic, but consider compelling alternatives.
- [4:Required] Preserve existing consumer compatibility (verify the authoritative contract in PRISM).
Y — Why: New integrations currently require coordinated producer changes and slow delivery.
```

**The grades measure commitment, not confidence:** `1:Consider`, `2:Prefer`, `3:Strong`, `4:Required`. A strong recommendation that can be challenged is grade 3. If no approach is selected, write `A — Angle: Open — no early decisions yet.`

## Install

Install/copy this entire `ray/` directory into your agent's skills directory so the final path is `<skills>/ray/SKILL.md`.

| Agent | Personal skills directory | Invocation |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/ray/` | `/ray` |
| Codex | `~/.agents/skills/ray/` | `$ray` |
| oh-my-pi | `~/.omp/agent/skills/ray/` | `/skill:ray` |

On Windows, replace `~` with your home directory. Repo-local directories are supported by agents that discover project skills. Consult your agent's documentation for exact discovery settings.

## Read and validate

- [Human guide](references/guide.md) — writing principles and the decision-grade rubric.
- [Coaching examples](references/examples.md) — rough requests, suggested RAY drafts, and clarifications.
- [Jira template](assets/jira-template.md) — canonical field labels and copyable examples.
- [Proposed parsing/PRISM handoff](references/handoff-contract.md) — how an eventual workflow could consume RAY. **Not an existing Shipwright/Jira integration.**
- [Review rubric](references/review-rubric.md) — semantic review, distinct from structural validity.

The optional Python linter checks **structure only** and extracts normalized JSON:

```bash
python ray/scripts/lint_ray.py intent.md --json
python -m unittest discover -s ray/tests -v
node --test ray/tests/skill-contract.test.mjs
```

The linter never proves the statement is true, validates a security requirement, connects to Jira, or starts PRISM.
