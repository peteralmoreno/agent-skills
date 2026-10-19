---
requires:
  - customer_ref
produces:
  - coordinates
  - isMember
  - sms_opt_in
  - phone_ref
tool_hints:
  - customer_lookup
  - address_validate
---

# Locate the hungry human

Look up **fictional, authorized** customer data. Return verified coordinates, membership, and notification consent.

A verified `isMember: false` is a valid boolean, not an absent value. If the destination is unknown or ambiguous, pause rather than inventing coordinates.

Don't retain raw phone numbers or private addresses in Trail or shared reports.
