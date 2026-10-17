# LENS HTML — practical planning guide

A **LENS** artifact turns one chosen PRISM spec into one implementable delivery plan. The HTML-first variant changes the preferred rendering, **not** the limits of the planning method. It reads HTML or Markdown, and can produce either independently of the input format.

## L — Limits

Classify **every approved PRISM R#** as Now, Later or Outside this delivery, with a destination for every deferred commitment. Example: `R1 Now — new event publication`; `R2 Later — existing consumer migration in increment 2`. Do not move an invariant that protects R1 to Later just because R2 is deferred. A completed delivery increment does not mean the full PRISM is complete.

## E — Execution plan

Use `W1`, `W2` etc. for independently reviewable work outcomes, explicit prior-work dependencies, R/I/S traceability, and a verifiable `Done when`. Example: `W1 — add publication path; Depends on None; R1/I1/S1; Done when change events can be published without disrupting existing consumers.` Skip fabricated file paths, named owners, dates or nonessential implementation details.

## N — Needs

Separate `Blocker` (must resolve before this work), `Risk` (manage/mitigate), and `Question` (needs confirmation by checkpoint). Example: `N1 Question — who owns consumer migration? Resolve before the next increment.` Do not add generic risk boilerplate or infer approval.

## S — Signals

Describe **future evidence** mapped to source PRISM M#, not outcomes already achieved. Example: `W1 → M1 integration-test evidence; W2 → M2 backward-compatibility evidence.` If M2 is missing or contradicts an invariant, return to PRISM rather than making up a threshold.

## Handoff

The plan remains one artifact. Include exact PRISM reference, known revision, readiness status, remaining blockers, and a suggested first step **if separately authorized**. `approved` is only valid after author approval. Plan handoff does not authorize Git mutation or implementation.

## HTML structure and interoperability

Use semantic tables/list markup and visible metadata. Main attributes carry `data-skill`, `data-format`, status, source path, source status and delivery target. Coverage rows carry R# and `data-delivery`; W# rows carry dependencies and spec links; N# rows carry type; signal rows carry M# links and evidence. Never rely only on colors/badges for status.

For Markdown output, render the canonical YAML frontmatter plus L/E/N/S/Handoff tables; the existing Markdown validator can check those. It **cannot** validate the HTML rendering. A limited repository HTML checker verifies the static HTML DOM markers but not planning feasibility.
