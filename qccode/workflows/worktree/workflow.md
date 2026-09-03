# Q-C-Code Worktree Workflow

## Purpose
Turn the approved plan into an explicit execution context by setting up workspace, branches, and environment.

## Steps
1. **01-read-plan.md** – Read plan.md to understand implementation tasks and requirements
2. **02-check-environment.md** – Check current git status, project conventions, and workspace state
3. **03-identify-policy.md** – Identify execution policy (same workspace, branch, worktree, test-only)
4. **04-get-approval.md** – Prepare policy options for coordinator approval with `AskUserQuestion`
5. **05-setup-environment.md** – Set up execution environment (branches, worktrees, setup commands)
6. **06-write-artifact.md** – Write worktree.md with execution context and environment state

## Triggered By
Completion of plan.md with a `User checkpoint response` confirming plan approval, and an `Output for next stage` section.

## Required Input
- `plan.md` — with approved implementation tasks from Plan stage

## Optional Input
- `questions.md` — for project conventions or environment details mentioned early

## Output
- `worktree.md` — with execution policy, branch/worktree details, environment state, and `Output for next stage`

## Gates
Pause gate: Step 04 writes a `User-facing checkpoint` (execution policy options) to the artifact and returns. The coordinator presents the options with `AskUserQuestion` and records the user's choice under `User checkpoint response`. The coordinator then relaunches Worktree to complete steps 05–06.

## Rules
- **Pause gate**: Always pause before creating/changing branches, worktrees, pushing, or opening merge requests
- Identify execution policy: same workspace, branch, git worktree, main/direct, test-only
- Check current git status and project conventions before proposing changes
- Setup execution environment: branches, worktrees, dependencies, local config
- Write worktree.md with: branch status, execution policy, target branch, setup commands, CI expectations
- Produce `Output for next stage`: exact environment state and first implementation slice

## Failure Behavior
- If git status check fails or workspace is dirty in unexpected ways: write the issue in the User-facing checkpoint and ask the user how to proceed.
- If setup commands fail: diagnose the issue, document it in worktree.md, and ask the user for guidance.
- Do not start implementation in a dirty workspace.

## Must Not
- Do not use `AskUserQuestion` directly — the coordinator does this.
- Do not create branches, worktrees, or change git state before user approval is recorded in the artifact.
- Do not copy `.env`, `.env.local`, credentials, tokens, API keys, SSH keys, or ignored secret-bearing files automatically.
- Do not commit secrets or print secret values into artifacts.
- Do not start implementation before worktree.md is written with confirmed execution policy.
