---
requires: [pr, assessment, worklog]
produces: [pr, assessment, worklog]
tool_hints: [local_checks, git_commit, git_push, github_read]
---

# Verify the combined result and push

Review the total diff against the original intent, including conflict resolutions. Scope drift or ambiguous behavior chooses **blocked or uncertain** before pushing. Run the repository's relevant checks on the combined result. A diagnosed, actionable failure chooses **local checks failed**, recording it for the next bounded repair round. Missing tools or unrelated infrastructure trouble pause instead of inventing a pass.

Commit only intended changes. Record the intended commit and target remote branch before pushing. Push normally to the PR's verified head repository/branch, never to main and never with force. Confirm the remote head matches the intended commit, then choose **pushed or already current**. Record whether fresh review is needed.

After a timeout/disconnection, inspect the remote head before repeating the push. If someone else changed the branch, preserve their work and choose **blocked or uncertain** for reconciliation; do not overwrite it. A successful push is not evidence that CI or review succeeded.
