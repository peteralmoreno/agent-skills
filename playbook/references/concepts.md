# Playbooks: concepts and source references

## Elevator pitch

A playbook is a reusable operational contract that teaches an agent **what job to do, when, with which authorized tools, and what evidence should be produced**. The same general-purpose agent can apply different playbooks without creating a new specialized agent for each job.

"Playbook" is a **design pattern**, not a proprietary standard or universal file schema. An AI playbook may be as simple as Markdown or as elaborate as a versioned, evaluated package.

| Concept | Main concern | Where it lives | Connection |
|---|---|---|---|
| **Playbook** | Expertise + procedure + evidence contract | Markdown in a repository or registry | May reference Skills, runbooks, tools |
| **Agent Skill** | Discover and supply capability/instructions | `SKILL.md` package with optional resources | May implement/expose a playbook |
| **Runbook** | Known operational symptom and repeatable diagnosis/remediation | Operational documentation; sometimes a Skill | May be selected by a playbook |
| **Workflow** | Manage sequencing, state, retries and approvals | Workflow definition or orchestration engine | May launch agents and playbooks |
| **Toolbox** | Reuse approved scripts/templates/API adapters | Shared source-controlled packages | Playbooks refer to stable tool identifiers |

These overlap. A runbook may be a playbook. A playbook may fit inside a Skill. The differences are **responsibilities**, not file extensions.

## Operating principles

1. **Delegate well:** capture expert behavior, not merely a prompt persona.
2. **Bound autonomy:** state read/write permissions, decision rules, and authorization checkpoints.
3. **Reuse:** refer to tested assets rather than repeatedly regenerating scripts.
4. **Prove work:** make evidence and its provenance visible; LLM self-checks alone are weaker than independently observed signals.
5. **Version and learn:** record failures and propose new versions; test before promotion.
6. **Keep boundaries:** a playbook about planning should not autonomously create tickets or deploy code unless those effects are part of its requested and authorized job.

## Architectural options

- **Simple:** one Markdown playbook + human/agent execution + manual review.
- **Skill adapter:** a lightweight Agent Skill discovers/loads a canonical playbook; the playbook remains independently versioned.
- **Managed:** catalog, reusable toolbox, run ledger, automatic structural checks, evaluation suite, approval-based promotion. An optional user-chosen **Playbook Bank** can provide a shared directory with local history and curated memory, without placing procedures inside the Skill installation.
- **Orchestrated:** use a workflow engine for durable state, retries, parallelism, approvals, and deterministic gates; use playbooks for domain expertise.

Choose the simplest effective approach. Adding orchestration does not automatically make the content a better playbook.

See [Playbook Bank](bank.md) for a portable implementation of that shared directory.

## Caveats behind popular claims

- "One agent plus playbooks beats many agents" is **not a universal empirical result**. Specialization, isolation and parallel work may justify multiple agents.
- "The system learns from failures" requires a feedback capture, regression tests, and a controlled update mechanism. Markdown does not learn by itself.
- "Proof guarantees correctness" overstates it. Explicit `P#` checks improve auditability; independent deterministic evidence is still preferable.
- Skills can evolve, but the Skill format alone is not a self-improvement framework.

## Primary references

- [Agent Skills specification](https://agentskills.io/specification) — discoverable `SKILL.md` packages and optional scripts/references/assets.
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — workflows vs agents; simplicity and control.
- [Anthropic: Lessons from building Claude Code — how we use Skills](https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills) — examples of runbook-style Skills and executable helper tools.
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — evaluation and proof approaches.
- [Claude Code Skills documentation](https://code.claude.com/docs/en/skills) — discovery and installed Skill behavior.
- [OpenAI Codex Skills documentation](https://developers.openai.com/codex/skills) — skill packaging and loading (confirm host-specific details before use).

These sources support the architectural ingredients; they do **not** establish a universally standardized `PLAYBOOK.md` format. The template used here is this Skill's proposed convention.
