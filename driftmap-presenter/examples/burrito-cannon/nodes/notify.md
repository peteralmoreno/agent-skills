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

# Notify the customer

After simulated delivery confirmation, check recorded SMS consent.

If consent is valid, use a fictional SMS simulator and record its result. Otherwise record skipped, not sent. A missing simulator or uncertain result follows **notification unavailable**.

Do not send a real message or claim one was sent.
