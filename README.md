# Agent Skills

Reusable agent skills by Peter Moreno.

## Skills

### Playbook

[`playbook`](playbook/) is a portable meta-skill for **learning, setting up, creating, discovering, executing, reviewing, and improving AI playbooks**. Playbooks are independently versioned procedures with inputs, explicit permissions, decision branches, reusable tools, and evidence requirements—not automatically specialized agents or Skills.

Use `/playbook` in Claude Code, `$playbook` in Codex, or ask an agent to use the `playbook` skill. The Skill can initialize a `playbooks/` library in another project and scaffold individual `PLAYBOOK.md` files. Its optional standard-library CLI prepares pinned run records and checks the *structure* of self-reported proof; the agent performs execution with its separately authorized tools. **Playbook Bank** mode lets users choose an independent folder as the source across projects, with persistent per-playbook run history and explicitly reviewed memory. See [the Bank guide](playbook/references/bank.md). See [the quickstart and usage guide](playbook/README.md).

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

Install Playbook for Claude Code or a portable Agent Skills runtime:

```powershell
Copy-Item -Recurse playbook "$env:USERPROFILE\.claude\skills\playbook"
# Or: Copy-Item -Recurse playbook "$env:USERPROFILE\.agents\skills\playbook"
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

For runtimes that recognize the cross-runtime skills directory, install PRISM under `~/.agents/skills/prism`, RAY under `~/.agents/skills/ray`, LENS under `~/.agents/skills/lens`, and Playbook under `~/.agents/skills/playbook`.

Review an existing installation before using `-Force`; it can replace files with the same names.

## Validation

Test the Playbook Skill's local utility (Python standard library only):

```powershell
python -m unittest discover -s playbook/tests -v
```

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

