---
requires: [pr, assessment, worklog]
produces: [pr, assessment, worklog]
tool_hints: [github_read, git_read]
---

# Ready means verified at these heads

Fetch fresh PR state rather than trusting the previous assessment. Confirm:

- The intended branch is pushed, the PR is open and not draft, and current main is incorporated without conflicts.
- Relevant findings are addressed, no unresolved review threads or outstanding change requests remain, and required approvals are present. Copilot has completed the needed review, including significant changes made during this run.
- Required checks apply to the current head/base and satisfy repository rules. Pending, missing, or failing required checks block readiness. Neutral/skipped results count only when the repository's policy accepts them. Any other observed failure has an explicit, supported disposition; don't hide hanging issues behind a green summary.
- Local verification and the final diff support the original scope. No known work remains in the checkout that should have been pushed.

If the head/base or actionable state changed, choose **state changed**. Unknown requirements, unreadable evidence, missing human approval, or unresolved ambiguity choose **blocked or uncertain**. Record any merge-queue or final human action still required; don't bypass it or call queue-required integration checks completed before they run.

Choose **ready at recorded heads** only with supporting evidence. Record head/base SHAs and observation time for the handover. Recommend the human's final merge decision; never perform the merge or enable auto-merge here.
