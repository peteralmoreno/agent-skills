# RAY HTML — use and authoring notes

This is **RAY, not RAY 2**: three fields, same angle grades and no hidden specification. The default presentation is HTML; explicit Markdown or Jira-ready output wins. Inputs can be HTML, Markdown, plain text or Jira content regardless of output. The skill is independently usable.

## Example: Kafka intent

- **Result**: downstream services receive domain change notifications without every integration changing the producer.
- **Angle**: `[3:Strong]` favor a new Kafka topic, open to a persuasive alternative; `[4:Required]` preserve current consumer compatibility, with authority checked during PRISM.
- **Why**: new integrations currently require coordinated changes and slow delivery.

HTML serializes these in `data-ray-field` sections and list items with `data-grade`. The grades must ALSO appear in visible text. `data-grade="3"` **is not** a 3/4 of confidence or a mandate to use Kafka.

## Draft → coaching → final

Draft quickly from the source; offer at most three meaningful recommendations, then one or a few questions only when answers change intent. Put coaching outside the RAY `<main>` element so an extractor doesn't accidentally treat it as a fourth field. Do not add constraints, scope, tests or acceptance criteria to RAY just to fill a layout.

## Format crossover

- HTML ticket → Markdown RAY: ignore scripts/styles; extract visible R/A/Y and decision grades; emit canonical `Intent` text.
- Plain-language request → HTML RAY: ask about missing author decisions, not about CSS; use the template for semantic accessible HTML.
- HTML RAY → PRISM Markdown: preserve the author's R/Y and grades, but make the downstream skill validate assumptions; do not claim existing Jira tooling can ingest HTML without an adapter.
- Unstructured HTML with missing grades: ask about commitment instead of deriving a grade from color or typography.

HTML output is a *rendering*, not a new version of the intent or an approval mechanism. Escape untrusted source text, preserve uncertainty and prefer standalone static HTML only when no format is specified.
