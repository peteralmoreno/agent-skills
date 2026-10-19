---
requires:
  - check_input
produces:
  - check_result
max_visits: 10
---

# Check the result

Attempt the fictional check once and record check_result.

- If it passes, select passed.
- If it fails and fewer than ten attempts have occurred, select failed and attempts remain.
- Important: If the tenth attempt fails, select failed on attempt ten and stop the run.

Ten means ten total attempts, including the first. Success on attempt ten is allowed. Never start attempt eleven or reset the count after a pause.

The HTML route explorer does not enforce this limit. These instructions apply to the executing agent, using persisted Trail history.
