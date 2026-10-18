# Setup and authoring guide

Read for `setup` and `create` modes.

## 1. Decide where playbooks belong

Prefer a version-controlled `playbooks/` directory in the consuming project when procedures depend on that project's environment. Prefer a central repository when the procedures are cross-project and inputs are portable.

**Optional Playbook Bank:** for a shared source outside this project, use `pb.py bank init <user-selected-folder>` and then `--bank <folder>` for `new`, `list`, `validate`, and `prepare`. The Bank stores versioned procedures under `playbooks/` and persistent history plus curated memory under ignored `.state/`. It does not merge with the project-local library or silently adopt a nonempty directory. Read [Bank setup and usage](bank.md) before configuring it.

Keep canonical playbooks independent of the agent's installation directory. It should be possible to upgrade the playbook without rebuilding or reinstalling a Skill.

Sample workspace:

```text
project/
  playbooks/
    README.md
    git-create-branch/PLAYBOOK.md
    write-spec/PLAYBOOK.md
    plan-work/PLAYBOOK.md
    implement-change/PLAYBOOK.md
    github-open-pr/PLAYBOOK.md
    .gitignore
    .runs/                  # local artifacts, private by default
```

Each operation should have one job and one output contract. **Do not hide lifecycle orchestration inside a playbook**: for example, writing a spec should not automatically create a branch, issue, comment or PR. A caller may choose to invoke those tasks separately.

A playbook can reference another Skill (e.g., use PRISM to build a specification) but must state preconditions; do not assume it is installed or that invocation grants permission for unrelated actions.

## 2. Interview the task owner

Ask about:
- **Job:** outcome, trigger, exclusions, frequency, target users.
- **Inputs:** required data, sources of truth, examples and ambiguity.
- **Decisions:** which judgment calls the agent can make, which must return to the user.
- **Procedure:** normal path, branch conditions, repeated steps, known counterexamples.
- **Toolbox:** existing approved scripts, templates and integrations; where to find them.
- **Authority:** allowed read/write scopes, production vs test boundaries, credentials, approvals.
- **Output:** filenames, schemas, consumers and handoff.
- **Proof:** measurable claims and how to retrieve independently observable evidence.
- **Recovery:** retryable cases, hard stops, compensation/rollback, escalation.
- **Improvement:** failure signals, real examples, candidate evaluation method.

Do not turn this into a form. Draft with clearly marked unknowns when enough is known; ask a small number of high-value questions only when necessary.

## 3. Author with an explicit contract

Use `assets/playbook-template.md`. Required frontmatter:

```yaml
---
name: investigate-api
description: Diagnose API incidents and provide an evidence-backed report
version: "0.1.0"
status: draft
---
```

Keep title, name and folder aligned. Keep the description useful for discovery. `version` is the document version, not the agent runtime version. Promote `status: active` only after review and at least representative trials.

A high-quality procedure has explicit branches:

```text
1. Collect symptoms and time window.
2. If incident target is ambiguous -> Blocked, ask for target.
3. Run approved read-only diagnostics.
4. If no evidence found -> report Unknown, do not speculate.
5. Correlate competing causes.
6. Verify each required P# claim.
7. Produce the report with sources.
```

Write "P1 — report cites timestamps and a primary source" rather than "make a good report." If certain proof needs human judgment, declare the reviewer and signal.

## 4. Prepare a reusable toolbox

Reference tested scripts by path, version or stable identifier. Identify dependencies and required permissions. Distinguish reusable tools from ephemeral working files. An AI-created script is **candidate**, not approved, until reviewed and tested.

Avoid embedding tokens or private environment data. Use the host's approved tool integration rather than telling an agent to bypass access controls.

## 5. Validate and trial

- Run `pb.py validate` for structure; read warnings for drafts.
- Try the playbook against at least one successful case, one ambiguous case and one known failure.
- Inspect evidence quality, side effects, refusal/stop behavior and time-to-completion.
- Save outcomes in separate local run records.
- Ask for an explicit decision before promoting a candidate playbook.

## 6. Minimum viable operating model

Do not build a registry service merely to store Markdown. An optional user-managed Bank is a directory, not a service. Start with Git, a catalog and explicit review. Add an execution ledger and evaluations once the same task recurs enough to justify it.

The `pb.py` utility manages simple directories and structured records. It does not implement an AI runtime, Git integrations, approvals service, task scheduling, or model evaluations.
