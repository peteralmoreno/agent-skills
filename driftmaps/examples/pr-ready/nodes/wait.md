---
requires: [pr, assessment, worklog]
produces: [assessment, worklog]
tool_hints: [github_check_read, github_review_read]
---

# Observe pending work without an endless polling loop

Use an available completion notification or one bounded observation window, at most five minutes. If polling is necessary, use a reasonable interval (for example 30 seconds), respect rate limits, and keep the user informed. Don't block the user's session indefinitely. Record the observed check/review identities and time in the worklog.

If meaningful state changed (completion, failure, new findings, or a new head/base), choose **state changed**. Mere elapsed time is not progress. If still pending at the deadline, tooling cannot wait, or evidence cannot be fetched, choose **still pending or unavailable**. Preserve the current node and pending identities, and tell the user what the run is waiting for. Resume by reconciling those same operations; don't trigger new reviews or checks merely because the conversation resumed.
