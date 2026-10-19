# Worked scenarios

These are tabletop examples of routing decisions, not claims of a live PR execution. Every arrow below must exist in `MAP.md`; the source graph remains authoritative.

## Already clean

Input: an open PR with current main incorporated, a completed applicable Copilot review, resolved findings, approvals, and green required checks.

`setup → inspect → final-check → complete`

Expected: a ready handover with the exact head/base and evidence. No push, rerun, new review request, or merge.

## Review finding, conflict, and a CI failure

A Copilot finding and a newer main need work:

`setup → inspect → repair → sync-main → verify-push → inspect → review → wait → inspect`

The first round fixes the finding, switches to main and pulls, returns to the PR branch, resolves a focused conflict, verifies, and pushes. The conflict resolution changes behavior significantly within scope, so review is requested for the pushed head. If CI subsequently reports an actionable failure:

`inspect → repair → sync-main → verify-push → inspect`

This is repair round two, not a new run. The agent requests another Copilot review only if the new changes require it. Once review and CI are settled, `inspect → final-check → complete`. No merge is performed.

## Resolved comments but a stale gate

The current-head gate still reports unresolved comments, but each referenced thread is confirmed resolved and the provider supports targeting that job:

`inspect → rerun-gate → wait → inspect → final-check → complete`

Expected: one targeted rerun, with job/check ID and receipt. An interrupted response is reconciled before any retry. A second stale result for the same head and resolution state pauses; it does not trigger an endless rerun loop. If only whole-workflow rerun is available, `rerun-gate → pause` explains the limitation.

## Scope drift or disputed fix

A suggested fix would replace the application's architecture to address a small bug:

`inspect → repair → pause`

Expected: no redesign. Explain the mismatch with original intent and propose the smallest alternative. If the drift is discovered during conflict resolution, `sync-main → pause` preserves the merge state. Human clarification may resume the saved operation; it doesn't erase earlier repair attempts.

## Ten attempts and still failing

Repeat the declared repair cycle as failures arrive. After ten `repair` attempts, including interrupted attempts, another required repair stops the run under the standard budget rule before attempt eleven. Preserve partial results and report remaining failures. Success on attempt ten may still proceed through CI/review and final readiness. Pausing after attempt nine and resuming leaves only one repair attempt.

## Pending, unknown, and changing evidence

- CI remains queued: `inspect → wait → pause` after one bounded observation window. Pending is not failure and causes no speculative code changes.
- Mergeability or approval requirements cannot be established: pause with the missing evidence; never report ready.
- Someone pushes after the apparent green result: `final-check → inspect`; reassess the new head. Never reuse old check results as proof for it.
- A push response is lost: reconcile the remote SHA at `verify-push`. If it already matches, continue without another push; an unexpected remote commit pauses for reconciliation.
