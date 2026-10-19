---
requires:
  - order_ref
produces:
  - order
  - customer_ref
tool_hints:
  - order_read
---

# Set up the mission

Validate the order reference using fictional sample data. Confirm simulation mode, available input, and permitted operations.

Create shared working context. If the order cannot be found, choose the **missing order** pause route. Do not invent customer details.
