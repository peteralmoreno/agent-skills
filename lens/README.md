# LENS — From specification to delivery plan

**L**imits · **E**xecution plan · **N**eeds · **S**ignals

LENS is an independent Agent Skill that converts an approved [PRISM](../prism/) engineering specification into **one implementation-ready Markdown plan**. It can scope an increment of a larger spec while preserving the complete source contract. Its optional validator checks structure and some traceability; it cannot verify architecture, feasibility, or approvals.

## Workflow

```text
RAY (Intent)  ->  PRISM (Specification)  ->  LENS (Scope & Plan)
                                                      |
                                             Implementation-ready
                                             (not yet authorized)
```

LENS does not write code, create Git branches, change tickets, run implementation or produce implementation reports. No additional execution skill is required by LENS itself.

## Use

- `/lens specs/feature-prism.md` — start a delivery plan.
- `/lens review plans/feature-lens.md` — review an existing plan.
- `/lens finalize` — finalize a previously discussed plan **after user approval**.
- Ask an agent to **use the `lens` skill** when slash commands aren't recognized.

The generated artifact defaults to `plans/<short-slug>-lens.md` and references its source PRISM file. PRISM doesn't have to originate from RAY.

## Install

Copy the `lens/` directory to a skill discovery path supported by your agent. For example:

```powershell
# Claude Code
Copy-Item -Recurse lens "$env:USERPROFILE\.claude\skills\lens"

# Codex / cross-runtime skills
Copy-Item -Recurse lens "$env:USERPROFILE\.agents\skills\lens"
```

Use your runtime's actual skill location and review an existing installation before replacing it.

## Validate a plan (optional)

```bash
node lens/scripts/validate-plan.mjs plans/feature-lens.md --prism specs/feature-prism.md
node lens/scripts/validate-plan.mjs plans/feature-lens.md --json
```

The validator checks headings, requirement coverage, W# references, dependencies, planned signals, and (when a local source spec is available) PRISM IDs. It does not read Jira, run tests or authorize implementation. If the source is a URL or unavailable locally, supply `--prism` for stronger checking.

Run the skill tests from the repository root:

```bash
node --test lens/tests/*.test.mjs
```

## What to put in each section

| Section | Write this | Avoid this |
| --- | --- | --- |
| **Limits** | Now/Later/Outside plus a reason and destination for every `R#` | Removing a PRISM requirement by calling it out of scope |
| **Execution plan** | Small `W#` outcomes, dependencies, PRISM links, and observable completion | Line-by-line code instructions or invented file paths |
| **Needs** | Real blockers, risks, questions, and resolution checkpoints | An obligatory but meaningless risk register |
| **Signals** | Future test/demo/metric evidence mapped from each `W#` to `M#` | Claiming implementation tests already passed |

**Start with the [practical, annotated authoring guide](references/guide.md)** for a fully worked Kafka example, decision notes, good/bad wording, and a one-minute readiness checklist. The [plan template](assets/plan-template.md) has removable HTML authoring prompts; omit these comments from a completed plan.

## Details

- [Human authoring guide](references/guide.md)
- [PRISM ID and handoff rules](references/prism-mapping.md)
- [Worked examples](references/examples.md)
- [Readiness rubric](references/review-rubric.md)
- [Blank plan template](assets/plan-template.md)
