---
name: REPLACE_NAME
version: "0.1.0"
status: draft
limits:
  max_transitions: 12
---

# REPLACE_TITLE

TODO: Explain what this map accomplishes and for whom.

## Flowchart

```mermaid
flowchart TD
    setup["Setup"] -->|ready| work["Do Work"]
    setup -->|missing input| pause(["Pause"])
    work -->|finished| complete(["Complete"])
    work -->|unresolved| pause
```

## Guidance

Read each real node file before executing that node. The Mermaid flowchart determines the allowed routes; node filenames are IDs.

## Boundaries

TODO: Describe appropriate user authorization, risky operations, and explicit exclusions.

## Success

TODO: Define what evidence confirms a useful result.

## Handover

Deliver an evidence-backed result in `handover.yaml` for the user or an independently authorized next map. Do not automatically chain another map.
