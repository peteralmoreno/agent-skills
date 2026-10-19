---
requires:
  - delivery_status
  - sms_opt_in
  - phone_ref
produces:
  - notification_status
tool_hints:
  - sms_simulator
---

# Notify Customer

Only consider notification after delivery is confirmed.

If the customer has consented, use the authorized **SMS simulator** and record its receipt. If opted out, record that the notification was skipped.

Do not claim that any real SMS was sent.
