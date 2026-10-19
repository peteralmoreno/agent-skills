---
requires: [pr, worklog]
produces: [pr, assessment, worklog]
tool_hints: [github_read, git_read]
---

# Decide from fresh evidence

Fetch the current remote head/base, mergeability, check results, review decisions, and all relevant comments/review threads, following pagination. Include Copilot findings, human blockers, and prior local verification failures. Read failure details before classifying them. An outdated comment is not necessarily resolved; an unknown mergeability result is not a conflict.

Update `assessment` with evidence URLs, commit identities, and outstanding work. Use this order to choose exactly one outcome:

1. **PR closed or merged**: stop active work and record its actual state.
2. **blocked or uncertain**: unclear scope, missing permission/evidence needed for the next action, external infrastructure failure needing a human, or disputed findings. Explain what is needed. Don't change code to appease an unrelated infrastructure failure. Missing final human approval need not block otherwise authorized repairs; pause for it once the actionable work is done.
3. **repair or main sync needed**: actionable findings, relevant local/CI failures other than a confirmed stale comment gate, conflicts, or latest base not incorporated in the branch. Assess findings rather than blindly accepting suggestions. Include all known issues in the next repair plan.
4. **fresh Copilot review needed**: no completed review covers the current changes, or significant changes since the last completed review need re-review, and no suitable review is already pending. Behavior/control-flow changes, public interfaces, dependencies, security changes, and substantial conflict resolutions are significant. Formatting-only changes normally are not; record why an existing review remains applicable. New review findings must still be handled.
5. **confirmed stale comment gate**: the only problem with that check is a stale unresolved-thread condition, every referenced thread is now confirmed resolved, and the provider supports targeting that check/job. Do not classify an ordinary queued/running check, code failure, or missing approval this way. If the gate is already being rerun, treat it as pending. If the same head and resolution state already had one completed rerun and remains stuck, pause rather than repeatedly rerun it.
6. **checks or review pending**: required CI, requested Copilot review, or mergeability computation is legitimately in progress.
7. **blocked or uncertain** if only a required human approval or other external decision remains. Otherwise **candidate ready**: no known remaining issue; perform the final independent freshness check.

Never count checks from an obsolete head as evidence for the current head. For merge/test commits or merge queues, verify the result corresponds to the actual head/base combination required by repository policy.
