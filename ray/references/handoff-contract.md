# RAY v1: Jira parsing and PRISM handoff contract

This is a **proposed integration contract**, not a claim that Shipwright or Jira already implements it. It describes a small, deterministic extraction surface that an eventual Spec workflow can consume. The included Python linter is a local reference prototype; it does not connect to Jira or launch PRISM.

## 1. Canonical source text

```text
Intent
R — Result: New consumers can react to domain changes without per-consumer producer changes.
A — Angle:
- [3:Strong] Dedicated Kafka topic is our baseline, open to better ideas.
- [4:Required] Existing consumer compatibility must hold (integration agreement; verify exact requirements).
Y — Why: Each integration currently increases producer-consumer coordination.
```

Also permitted, for no proposed direction:

```text
Intent
R — Result: ...
A — Angle: Open — no early decisions yet.
Y — Why: ...
```

**Contract:** one `Intent` heading; exactly one `R — Result:`, `A — Angle:`, `Y — Why:` field, in that order; a non-empty R and Y; A contains either an explicit Open statement or one or more graded bullet lines. ASCII hyphens for bullets are intentional for portability; field separator may be an em dash or a normal hyphen.

A bullet has the form `- [N:Label] <statement>`, where N and Label are exactly one of: `1:Consider`, `2:Prefer`, `3:Strong`, `4:Required`. Additional explanations can be included in the same statement. Do not interpret arbitrary numbers elsewhere in ticket text as grades.

The block should appear at the top of the Jira description. Put later ticket details under a separate heading such as `Context`. Jira may store descriptions as rich-text ADF rather than Markdown; the actual Jira adapter must normalize headings, paragraphs and list nodes to logical text before applying this contract. Regex directly against raw Jira ADF or rendered HTML is **not** a supported assumption.

## 2. Semantic requirements and validation limits

A structural parser can enforce labels, order, explicit grade markers and non-empty text. It cannot reliably determine whether:

- R is truly an outcome or merely a feature request;
- Y is an accurate diagnosis;
- Kafka is a good solution;
- a `[4:Required]` boundary is supported by actual policy or a real decision;
- a proposed solution will work.

Those checks require a human-aware agent, discovery or authoritative records. Never mark a ticket "spec ready" merely because a linter passes. Conversely, don't require a complete technical design to accept an Intent.

## 3. Suggested normalized handoff object

```json
{
  "format": "ray/v1",
  "result": "New consumers can react to domain changes without per-consumer producer changes.",
  "angles": [
    {
      "grade": 3,
      "label": "Strong",
      "text": "Dedicated Kafka topic is our baseline, open to better ideas."
    },
    {
      "grade": 4,
      "label": "Required",
      "text": "Existing consumer compatibility must hold (integration agreement; verify exact requirements)."
    }
  ],
  "angle_note": null,
  "why": "Each integration currently increases producer-consumer coordination."
}
```

`angles` is empty when A is open and `angle_note` contains the author's stated openness. The linter trims surrounding whitespace and joins multiline R/Y prose with spaces. Preserve the original source alongside this normalized text; do not otherwise rewrite the author's wording without authorization. Keep the original Jira ticket description or a stable ticket reference alongside the extracted object for provenance; do not treat the example JSON as an API schema enforced by Jira.

## 4. PRISM consumption rules

1. Treat **R** and **Y** as an author-owned trunk; do not silently replace them to justify an implementation.
2. Use R/Y to orient PRISM **Problem** and **Requirements/Measures**, but don't confuse rough intent with validated evidence or finished acceptance criteria.
3. Treat Angle grades 1 and 2 as hints, not invariants or mandatory scope.
4. Treat a grade-3 statement as an expected baseline. It can be rejected with a **reasoned comparison** to an alternative. Explain the deviation.
5. Treat grade 4 as a **proposed binding constraint**. Investigate authority/source, map to PRISM Invariants or constraints as appropriate, and seek approval before violating or downgrading it.
6. On conflict, **ask**. Don't quietly reinterpret a 4 as a 3 or assume two A options must be implemented together.
7. One RAY can lead to multiple PRISM options. Only fork into separate specifications when requested or when alternatives are materially distinct enough to justify it. Multiple Angle bullets alone do not mandate branches.
8. Do not create Jira subtasks, branch names, pull requests, or code until a later workflow step explicitly authorizes them.

## 5. Change management

RAY is deliberately mutable during discovery. When an alternative is persuasive, the requester can revise A from `[3:Strong] Kafka` to `[2:Prefer] Kafka`, remove the item, or endorse a different direction. For grade 4, use an explicit human decision and (where needed) update the authoritative policy/ADR, not an autonomous edit. A PRISM variant should record any meaningful departure from its originating RAY so reviewers can understand the decision.

## 6. Local structure linter

Run from the skill directory:

```bash
python scripts/lint_ray.py path/to/ticket-intent.md
python scripts/lint_ray.py path/to/ticket-intent.md --json
cat ticket-intent.md | python scripts/lint_ray.py --stdin --json
```

The linter emits parsing and shape errors; it does **not** determine semantic adequacy, verify policies, access Jira, or act as a PRISM gate. A future Jira adapter would need to retrieve ADF, normalize it, and pass the extracted block to a real validator.
