# Changelog

## 0.3.0

Audit and repair run: `2026-06-28-1000-qccode-skill-audit`

- **Removed** `agents/openai.yaml` — Devin-platform artifact name; `agents/interface.yaml` is the correct Claude Code metadata file.
- **Fixed** `references/artifact-schemas.md` — renamed `## design.md` schema section to `## design-discussion.md` to match the artifact name used everywhere else.
- **Fixed** `SKILL.md` validation levels — replaced the inline Level 1/2/3 definitions (which conflicted with validation-levels.md) with a 0–4 summary that matches the reference.
- **Fixed coordinator-interaction protocol** in 5 stage step files — replaced "Wait for user feedback" and "Confirm with the user" patterns with write-checkpoint-and-return protocol: subagents now write `User-facing checkpoint` to the artifact and return; the coordinator asks the user via `AskUserQuestion` and records the answer under `User checkpoint response` before relaunching.
  - `workflows/questions/02-ask-questions.md`
  - `workflows/design-discussion/03-present-options.md`
  - `workflows/structure/03-present-structure.md`
  - `workflows/plan/03-present-plan.md`
  - `workflows/worktree/04-get-approval.md`
- **Completed** 6 workflow.md manifests — added `Triggered By`, `Failure Behavior`, and `Must Not` sections to all workflow.md files except implement (which was already correct):
  - `workflows/questions/workflow.md`
  - `workflows/research/workflow.md`
  - `workflows/design-discussion/workflow.md`
  - `workflows/structure/workflow.md`
  - `workflows/plan/workflow.md`
  - `workflows/worktree/workflow.md`
- **Added `Must Not` sections** to all 19 non-implement step files (questions, research, design-discussion, structure, plan, worktree stages).

## 0.2.0

- Standardized scratch path on `.qccode`.
- Added run manifest policy.
- Added artifact schemas.
- Added workflow template.
- Added step template.
- Added tool fallback policy.
- Added validation levels.
- Added secret handling policy.
- Added controlled parallel implementation policy.
- Updated implementation workflow to support todo creation, parallelization review, slice assignment, serial integration, validation, and always-written implementation notes.
- Added simplified initial flow menu: New, Continue, About (list and clear available as direct commands).
