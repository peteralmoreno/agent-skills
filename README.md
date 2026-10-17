# Agent Skills

Reusable agent skills by Peter Moreno.

## Skills

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

The conceptual progression is **RAY → PRISM → engineering execution**: clarify intent, develop a specification when requested, then execute under separate authorization. Each skill remains independently usable.

### PRISM

[`prism`](prism/) turns vague or overloaded engineering requests into five connected specification views:

```text
Problem -> Requirements -> Invariants -> Solution -> Measures
```

It can explain the framework, build a specification, or review an existing specification. Its output connects requirements to protected invariants, solution decisions, and objective evidence through explicit traceability.

PRISM uses portable skill metadata and can be installed in Claude Code, Codex, or another runtime that supports the Agent Skills format.

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

For runtimes that recognize the cross-runtime skills directory, install PRISM under `~/.agents/skills/prism` and RAY under `~/.agents/skills/ray`.

Review an existing installation before using `-Force`; it can replace files with the same names.

## Validation

The repository tests use only Node.js built-ins:

```powershell
node --test tests/qccode-package.test.mjs tests/repository-safety.test.mjs prism/tests/skill-contract.test.mjs ray/tests/skill-contract.test.mjs
```

Validate the RAY structural parser with Python:

```powershell
python -m unittest discover -s ray/tests -v
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

