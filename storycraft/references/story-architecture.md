# Story architecture and source fidelity

## What the reader should understand

A first screen should usually answer: what is this, why should I care, and where do I go next? A second look should reveal the mechanics and consequences. Deep details should remain available without dominating the page.

Treat a narrative as a set of editorial decisions—not a fixed layout. Depending on the input, useful arcs include:

- **Concept:** promise → example → operation → details → limitations.
- **Process:** result → sequence → branches → inspect stages → human action.
- **Proposal:** problem → proposed change → trade-offs → implementation steps → verification needed.
- **Tutorial:** goal → prerequisites → first success → exceptions → troubleshooting.

Avoid unearned credibility sections. Real links can be surfaced if supplied. A fictional example can be useful without invented usage statistics.

## Fact ledger

Before authoring, record a table for yourself:

| Statement | Source phrase / file | Classification | Must preserve? |
| --- | --- | --- | --- |
| Flow has a pause branch on a missing order | Input process notes | Stated | Yes |
| Simulated launch is not a real mechanical event | Input boundary | Stated | Yes |
| Hypothetical time savings | Not mentioned | Unsupported | Do not add |
| “Mission control” as a visual metaphor | Editorial choice | Illustration | Can add, label appropriately |

Keep the **source's nouns, edges, and conditions** accurate. If a step is conditional, do not present it as inevitable. If two possible endings exist, depict both or clearly label the simplified view as partial. If the final UI shows an alternative route, give the user an interaction to inspect its destination.

## Synthesis vs invention

It is acceptable to:
- Improve headline quality and sentence rhythm.
- Group source facts into a new section.
- Express a supplied process through an accurate static or interactive diagram.
- Add metaphorical imagery when the image cannot be mistaken for factual evidence.

It is not acceptable to:
- Invent a customer, number, date, duration, dollar amount, incident, success rate, or verified status.
- Convert unknown status into green/success.
- Add links to made-up evidence or pretend a walkthrough did real work.
- Omit inconvenient failure routes to make a tidy graphic.

When converting source material to `*.story.json`, trace each meaningful assertion to the source. If insufficient source detail exists, leave the field out, add a clearly marked illustrative assumption, or ask a focused question if necessary.

## Example safety boundary

A fictional Burrito Blaster can show “Order → Wrap → Verify → Simulate → Notify → Complete” while also showing “missing order → Pause,” “ingredient issue → Stop,” and several other pauses. Buttons may explore those routes, but must not claim to fire a device or send SMS.
