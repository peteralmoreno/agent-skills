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

# Locate the Customer

Use an authorized source to find verified coordinates, membership status, and notification preferences.

A verified value of \`isMember: false\` is meaningful data, not a missing value.

If the destination is ambiguous, pause and ask the customer to select one. Avoid storing raw addresses or phone numbers in history.
