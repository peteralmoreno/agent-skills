---
requires: [pr, assessment, worklog]
produces: [assessment, worklog]
tool_hints: [source_edit, local_checks, github_review_threads]
max_visits: 10
---

# Repair round — maximum 10 total

**Show “repair round N of 10” before starting.** Count saved attempts, including interrupted attempts; pauses do not reset the count. No round eleven. One visit is one focused repair pass, not a hidden repeat-until-green loop.

Compare the proposed fixes with the original scope in `worklog`. Prefer the smallest change that addresses the actual defect. If it requires new product behavior, broad refactoring, unrelated cleanup, or a redesign, choose **scope drift or blocked** before making that change. Give the user the finding, why it exceeds scope, and the smallest concrete proposal. Don't quietly expand the baseline.

Address justified review findings and diagnosed CI/local failures together when practical. If this round only needs a main sync, record that and leave the code alone. Use relevant tests and repository guidance; don't weaken checks to make them green.

Resolve a review thread only when its finding is demonstrably addressed and thread resolution is authorized. Keep evidence linking it to the fix. A response disagreeing with a reviewer is not proof the issue is resolved; unresolved disagreement pauses. Reconcile any previous thread update before repeating it.

Record the changes, remaining local work, and whether the change warrants a fresh Copilot review after pushing. Choose **focused repairs prepared** for the main-sync stage, or **scope drift or blocked** if safe progress is unavailable. Commit only scoped changes as needed to make branch switching safe; do not publish from this node.
