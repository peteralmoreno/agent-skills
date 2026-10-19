# Agent Skills

Reusable agent skills by Peter Moreno.

## Skills

### DriftMaps

[`driftmaps`](driftmaps/) is a portable, **flowchart-first Agent Skill** for creating, inspecting, executing, and improving reusable AI procedures. `MAP.md` defines the authorized routes, `nodes/*.md` contains real operating guidance, `trail.yaml` checkpoints working context and referenced artifacts, and `handover.yaml` transfers the outcome.

Every map begins with `nodes/setup.md`. Agents must read actual node files instead of inventing steps; `tool_hints` are nonbinding discovery hints, and finite transition budgets bound loops. DriftMaps is Markdown/YAML-first and requires no special agent framework or HTML viewer.

```bash
python3 driftmaps/scripts/driftmaps.py init --root /path/to/project
python3 driftmaps/scripts/driftmaps.py new my-map --root /path/to/project
python3 driftmaps/scripts/driftmaps.py validate /path/to/project/maps/my-map/MAP.md
```

The separately installable [Drift Map Presenter Skill](driftmap-presenter/) is an optional human-facing interactive HTML companion, not a dependency. See the [full DriftMaps guide](driftmaps/README.md) and [Burrito Cannon example](driftmaps/examples/burrito-cannon/MAP.md).

### Drift Map Presenter (optional)

[`driftmap-presenter`](driftmap-presenter/) generates a **self-contained, interactive HTML front face** for an existing Drift Map: clickable nodes, a read-only route explorer, and readable map/node instructions. It uses the authoritative `MAP.md` Mermaid flowchart and `nodes/*.md` files; it never executes the map or becomes required for AI agents.

**Opt-in only:** not every map needs a human UI. Ask an agent to use the `driftmap-presenter` skill when a visual overview would help, or run:

```bash
python3 driftmap-presenter/scripts/render_map.py path/to/my-map/MAP.md
```

See the [Skill guide](driftmap-presenter/README.md), [human-view design notes](driftmap-presenter/references/design.md), and [Burrito Cannon example](driftmap-presenter/examples/burrito-cannon/MAP.md).

### Storycraft

[`storycraft`](storycraft/) turns rough HTML, Markdown, briefs, and notes into polished, **self-contained interactive HTML stories**. It preserves source claims, links, transitions, and alternate routes while offering three [Drift Map Presenter-aligned visual styles](storycraft/references/style-systems.md): coral-red **Dark**, playful **Morrito** with stars and pipes, and fantasy **Gilded** with a yellow riding bird.

It includes an authored-story renderer, a fictional Burrito Blaster example, offline structural audits, browser QA, and [custom asset import guidance](storycraft/references/custom-assets.md) for approved local mascots, sprites, icons, and backgrounds. Storycraft is independent of Drift Maps and never executes the processes it illustrates.

```bash
python3 storycraft/scripts/render_story.py storycraft/examples/burrito-blaster.story.json --style all --out-dir ./scratch/storycraft/
python3 -m unittest discover -s storycraft/tests -v
```

See the [Storycraft guide](storycraft/README.md) and [Agent Skill instructions](storycraft/SKILL.md).

### Q-C-Code

[`qccode`](qccode/) adapts the QRSPI workflow for Claude Code:

```text
Questions -> Research -> Design Discussion -> Structure -> Plan -> Worktree -> Implement
```

It uses Claude-specific tools and conventions, including `Agent`, `AskUserQuestion`, `argument-hint`, and dedicated stage workflows. It is published here without changing that source contract and should be treated as a Claude Code skill.

### RAY

[`ray`](ray/) is a lightweight, author-friendly engineering story intent that comes **before** PRISM:

```text
Result -> Angle -> Why
```

It drafts Jira-ready intents, offers targeted recommendations and clarifications, and grades each early decision from **1:Consider** to **4:Required**. A strong preference may still be challenged by a better solution. RAY is independently installable and includes a human guide, examples, a structural linter, and tests. It does **not** automatically write a PRISM spec, plan work, or change Jira.

Use `/ray` in Claude Code, `$ray` in Codex, or ask your agent to use the `ray` skill. Each Angle decision has its own commitment grade: **1 — Consider**, **2 — Prefer**, **3 — Strong**, or **4 — Required**. Only grade 4 is binding unless the requester explicitly authorizes a change; preferences must never silently become requirements. Unknowns and an open Angle are valid.

The conceptual progression is **RAY → PRISM → LENS → engineering execution**: clarify intent, establish the specification, focus it into one delivery plan, then execute under separate authorization. Each skill remains independently usable.

### PRISM

[`prism`](prism/) turns vague or overloaded engineering requests into five connected specification views:

```text
Problem -> Requirements -> Invariants -> Solution -> Measures
```

It can explain the framework, build a specification, or review an existing specification. Its output connects requirements to protected invariants, solution decisions, and objective evidence through explicit traceability.

PRISM uses portable skill metadata and can be installed in Claude Code, Codex, or another runtime that supports the Agent Skills format.

### LENS

[`lens`](lens/) focuses one approved PRISM specification into a delivery plan using four sections:

```text
Limits -> Execution plan -> Needs -> Signals
```

It identifies which PRISM requirements are delivered now or later, breaks the current increment into dependency-ordered work units, surfaces blockers, and maps planned verification back to PRISM measures. It produces **one standalone LENS Markdown plan** referencing the authoritative PRISM spec and stops before code changes, branches, or PRs.

Use `/lens` in Claude Code, `$lens` in Codex, or ask your agent to use the `lens` skill. LENS can be used independently with any approved PRISM spec; it does not require an earlier RAY conversation.

## HTML-first companions (format-flexible)

The original `ray`, `prism`, and `lens` remain **Markdown/text-first**. Their standalone HTML-first companions are **`ray-html`**, **`prism-html`**, and **`lens-html`**. They retain exactly the same workflow and approval rules; only the default presentation is different.

| Stage | Text/Markdown-first | HTML-first | Both accept / can emit |
| --- | --- | --- | --- |
| Intent | [`ray`](ray/) | [`ray-html`](ray-html/) | HTML, Markdown, prose, Jira text |
| Specification | [`prism`](prism/) | [`prism-html`](prism-html/) | HTML, Markdown, source content |
| Delivery plan | [`lens`](lens/) | [`lens-html`](lens-html/) | HTML, Markdown, source PRISM |

Examples:

```text
/ray-html Design an event notification feature
/prism-html specs/event-notifications.md --output HTML
/prism spec.html --output Markdown
/lens-html specs/event-notifications-prism.md --output plans/event-lens.md
/lens specs/event-notifications-prism.html --output HTML
```

Explicit requested output wins, then the destination or host format contract, then the skill's default. **Input HTML does not force output HTML**, and HTML is not an implementation/approval shortcut. HTML files are static, accessible documents with stable semantic `data-*` markers; the existing RAY and LENS Markdown validators do not read HTML. See the [format interoperability guide](docs/format-interoperability.md).

Install any HTML variant by copying its entire folder into your agent's skill directory (e.g. `~/.claude/skills/prism-html/` or `~/.agents/skills/lens-html/`). No sibling skill installation is required.

HTML contract checks (Python standard library / Node built-ins):

```bash
python -m unittest discover -s tests -p 'test_html_contract.py' -v
node --test tests/html-format-skills.test.mjs
python scripts/validate-semantic-html.py ray-html/assets/intent-example.html --skill ray
```

The HTML checker verifies limited structural metadata; it does not evaluate engineering quality, convert arbitrary HTML/Jira ADF, or substitute for the stage-specific agent's review.

## Installation

Clone the repository:

```powershell
git clone https://github.com/peteralmoreno/agent-skills.git
Set-Location agent-skills
```

Install Q-C-Code for Claude Code:

```powershell
Copy-Item -Recurse -Force qccode "$env:USERPROFILE\.claude\skills\qccode"
```

Install RAY for Claude Code:

```powershell
Copy-Item -Recurse -Force ray "$env:USERPROFILE\.claude\skills\ray"
```

Install RAY for Codex:

```powershell
Copy-Item -Recurse -Force ray "$env:USERPROFILE\.agents\skills\ray"
```

Install PRISM for Claude Code:

```powershell
Copy-Item -Recurse -Force prism "$env:USERPROFILE\.claude\skills\prism"
```

Install PRISM for Codex:

```powershell
Copy-Item -Recurse -Force prism "$env:USERPROFILE\.codex\skills\prism"
```

Install LENS for Claude Code:

```powershell
Copy-Item -Recurse -Force lens "$env:USERPROFILE\.claude\skills\lens"
```

Install LENS for Codex:

```powershell
Copy-Item -Recurse -Force lens "$env:USERPROFILE\.agents\skills\lens"
```

For runtimes that recognize the cross-runtime skills directory, install PRISM under `~/.agents/skills/prism`, RAY under `~/.agents/skills/ray`, and LENS under `~/.agents/skills/lens`.

Review an existing installation before using `-Force`; it can replace files with the same names.

## Validation

The repository tests use only Node.js built-ins:

```powershell
node --test tests/qccode-package.test.mjs tests/repository-safety.test.mjs prism/tests/skill-contract.test.mjs ray/tests/skill-contract.test.mjs lens/tests/skill-contract.test.mjs lens/tests/validator.test.mjs
```

Validate the RAY structural parser with Python:

```powershell
python -m unittest discover -s ray/tests -v
```

Validate a LENS document and its local PRISM source:

```powershell
node lens/scripts/validate-plan.mjs plans/example-lens.md --prism specs/example-prism.md
```

Validate PRISM with Codex's bundled skill validator:

```powershell
$validator = Join-Path $env:USERPROFILE '.codex\skills\.system\skill-creator\scripts\quick_validate.py'
$env:PYTHONUTF8 = '1'
python $validator prism
```

Q-C-Code's package contract is covered by the repository tests. Codex's validator reports its Claude-specific `argument-hint` field as unsupported; this is expected and is why Q-C-Code is labeled Claude-specific.

## License

MIT

