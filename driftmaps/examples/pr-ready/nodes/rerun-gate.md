---
requires: [pr, assessment, worklog]
produces: [assessment, worklog]
tool_hints: [github_check_read, github_check_rerun]
---

# Refresh only the stale resolved-comments check

Recheck the current head, exact check/job identity, and referenced thread resolution state. Establish that stale thread state is the cause. If a thread is still unresolved, the head changed, or the failure has another cause, choose **unsupported or uncertain** with updated evidence; do not blindly rerun.

Use the provider's supported targeted rerun/refresh operation. GitHub Actions jobs and third-party check runs have different APIs; use the actual provider capability. If the tool can only rerun the whole workflow, pause and explain that limitation rather than silently widening the action. Never cancel a legitimately running job just to make it retry.

Record the intended check ID, head, previous attempt, and resolution-state evidence before the call. Reconcile receipts and current check state on resume. Allow at most one rerun for the same head and same thread-resolution state. If it is already active, choose **rerun accepted or already active** without repeating the call. If the call succeeds, record the receipt and choose that same outcome. If it stays stale after that rerun, pause for diagnosis. Unknown delivery chooses **unsupported or uncertain** until reconciled.
