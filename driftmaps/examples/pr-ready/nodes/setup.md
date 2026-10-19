---
requires: [pr_url, checkout]
produces: [pr, assessment, worklog]
tool_hints: [github_read, git_read]
---

# Establish the PR and its boundaries

Read the existing PR, its full diff, repository guidance, head repository/branch, base branch, and relevant check/review requirements. Confirm the target is `main` and that the local checkout corresponds to this PR, including fork remotes where applicable. Do not assume `origin` is the base repository.

Confirm the scope of authorized edits and GitHub writes from the user's request. Preserve unrelated work: if the checkout is dirty or has an unfinished merge, use an appropriate isolated worktree or pause; don't reset, discard, or silently stash someone else's changes.

Create the `worklog` artifact with original intent, in/out-of-scope boundaries, initial head/base SHAs, required verification, and authorized operations. Initialize `pr` with verified identities and `assessment` with no assumed successes. Record existing Copilot reviews and their reviewed commits; don't assume an old review covers the current head.

Choose **ready** when identity, scope, access, and working directory are sufficient. Choose **input or access missing** for ambiguity or missing authorization, with a concrete question. The map itself supplies no authorization.
