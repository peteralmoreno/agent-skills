---
requires: [pr, assessment, worklog]
produces: [pr, assessment, worklog]
tool_hints: [git_fetch, git_switch, git_merge, source_edit]
---

# Bring current main into the PR branch

Preserve a clean, committed PR worktree before switching branches. Inspect remotes and branch tracking rather than assuming names. For a normal checkout:

1. Switch to the local `main` tracking the PR's base repository.
2. Pull that remote's `main` with fast-forward-only behavior. If local main has diverged, pause; don't reset it or merge unrelated local main commits into the PR.
3. Switch back to the verified PR branch.
4. Merge the refreshed base into the PR branch if not already incorporated.

If main is checked out in another worktree or using a local main would disturb unrelated work, fetching the base repository's `main` and merging that exact fetched commit into the PR branch is an acceptable equivalent. Record the chosen method and base SHA. This node never pushes main.

Resolve straightforward conflicts while preserving both the PR's original purpose and current main behavior. Inspect the resulting diff. Stop before a resolution that requires a product decision or materially expands scope; choose **scope drift or uncertain conflict**, preserving the merge state and explaining what needs deciding. Don't choose one entire side just to remove conflict markers.

Record any significant conflict resolution for re-review. Choose **main incorporated** when the intended base commit is incorporated and the merge is complete. On interruption inspect the existing merge and commit state before attempting another merge.
