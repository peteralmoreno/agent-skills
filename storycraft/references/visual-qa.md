# Visual and factual quality gates

## Render before declaring success

Render at 1440, 834, 390, and 320px. For each, confirm:

- A reader can scan the hero without losing the takeaway.
- The **signature art system is present in the output**: Dark's coral-red primary accents; Morrito's eyed star, colored glossy route pipes with two distinct end collars, dimensional [?] block, thick panels and a single continuous illustrated footer; Gilded's sword, wand, large riding bird, little ?-bird on question notes, bevels and violet/gold controls.
- No second turf/soil band appears beneath the Morrito illustrated footer.
- The Morrito [?] tile is dimensional, and Gilded question notes use the curious bird, not a plain text glyph.
- The pipeline color never misrepresents the declared decision; source labels remain visible.
- Gilded uppercase headings wrap at **word boundaries**, including at 320px.
- Body text and route labels remain legible.
- Cards, buttons, branch labels, and decorative elements do not clip.
- No horizontal overflow on the page; scroll inside a diagram only if deliberate and clearly signposted.
- Arrows join intended nodes and point in the true direction.
- No status is colored “success” unless the source says success.
- Interactive selections reveal the correct node details and choices.
- Replay follows the declared primary route and does not skip into an unmarked branch.
- All links, IDs, `aria-labelledby`, and keyboard navigation work.
- Reduced-motion users receive a functional, low-motion experience.
- No external CSS, JavaScript, images, fonts, or runtime API calls are required.

**Static audit:** `python3 scripts/check_story.py FILE.html`

**Browser QA:** `python3 scripts/preview_story.py FILE.html --out-dir preview/`

Install optional dependency once: `python3 -m pip install playwright && python3 -m playwright install chromium`. Pass `--chromium /usr/bin/chromium` if a local executable is already installed.

Browser QA is a smoke test, **not** a replacement for viewing screenshots. Every generated screenshot must be opened and critiqued when the tools permit it.

## Difficult cases

**Long heading on a narrow phone:** if `documentElement.scrollWidth` is wider than `window.innerWidth`, inspect CSS text shaping of uppercase or unbreakable strings; reduce the heading size or enable `overflow-wrap:anywhere` as a fallback.

**Graph seems to “complete” before an alternative path finishes:** diagram ordering is wrong even if the animation sequence is correct. Draw the true edges and rerender.

**Tiny process steps:** move to vertical cards at smaller breakpoints; do not shrink a giant desktop diagram.

**Need a clickable “Replay” control:** all static information should remain visible. On click, sequence the actual primary route only and explain that it is a presentation, not execution.

**Evidence not supplied:** do not fabricate an evidence bar. Acknowledging unknowns is better than fake precision.

**Cannot use browser automation:** perform static checks and explain that visual browser QA is still outstanding.
