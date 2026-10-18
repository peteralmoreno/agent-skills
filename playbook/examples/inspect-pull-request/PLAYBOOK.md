---
name: inspect-pull-request
description: Examine an existing code diff for risks and produce a private evidence-backed review, without posting on GitHub.
version: "1.0.0"
status: active
---

# Inspect a Pull Request

## Goal

Review a supplied code change and report actionable observations to the requester. This playbook is deliberately read-only and does not submit a GitHub review.

## When to use

- **Use when:** A requester provides an accessible PR, diff, or commit range and asks for an offline code review.
- **Do not use when:** The user wants to publish comments, approve a PR, push changes, or implement a fix; those are different authorized operations.

## Inputs

| Input | Required? | Authority / validation |
|---|---|---|
| Repository or diff | Yes | Must be accessible through approved read-only tools |
| Target branch or baseline | Yes | Confirm actual comparison target rather than assuming main |
| Relevant requirements or tests | When available | Identify source; mark missing context rather than inventing it |

## Procedure

1. Confirm the repository, comparison target, commit range and review scope.
2. Retrieve the actual diff using approved read-only tools. Stop if the diff is unavailable.
3. Read directly affected interfaces, relevant tests and applicable project conventions.
4. Look for specific regressions, contract breaks, security implications and missing test coverage.
5. If a finding depends on an unverified assumption, label it as such instead of asserting a defect.
6. For each finding, cite a file/line or reproducible observation and suggest a concrete next action.
7. Check the proof claims and write the review report to the requester; do not post it to GitHub.

## Tools and permissions

- **Read-only:** Approved repository browsing, diff inspection, and existing documentation.
- **Writes / side effects:** None. Publishing review comments, opening issues, approving or merging PRs requires a separately requested procedure.
- **Approval checkpoint:** Ask before any action that changes remote or local repository state.
- **Toolbox references:** Use existing diff/review tools if available; no mandatory external CLI.

## Proof of completion

- **P1:** Comparison target and reviewed change range are explicitly identified; evidence: actual diff source and commit refs.
- **P2:** Each asserted finding includes an inspectable source reference or reproduction evidence; evidence: report citations.
- **P3:** Report distinguishes verified findings from risks, open questions and unexamined areas; evidence: review report.
- **P4:** No GitHub review, comment, approval or code change was made; evidence: execution action log.

## Output

- **Artifact:** Human-readable review report with summary, severity-qualified findings, evidence, unknowns and next steps.
- **Report:** Outcome and evidence mapped to P1–P4; state any limits due to incomplete context.

## Failure and recovery

- **Blocked:** Cannot access the diff or identify the comparison baseline; request missing input.
- **Retryable:** Read-only transient repository access issues may be retried within host limits.
- **Failed:** Evidence is insufficient to support a finding; report uncertainty, never invent code facts.

## Learning

- Record repeated missed regression classes or noisy checks in an execution record.
- Propose a separate candidate revision and a regression case before changing this document.
