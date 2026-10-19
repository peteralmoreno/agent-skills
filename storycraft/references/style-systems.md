# Storycraft visual systems — Presenter-faithful, not generic theme swaps

These are concrete visual systems intentionally aligned with the source styles used in **driftmap-presenter**. The independent Storycraft renderer keeps all three styles available offline even when the other skill is absent.

## Shared design contract

- Structure, claims, steps, decisions, links, and simulation boundaries come from the **same story model**.
- Theme-specific drawings are *decorative*; they do not create routes, redefine statuses, or hide evidence.
- Keep a clear story arc and a useful diagram. Do not copy a different subject's text or fabricated run data.
- No external assets, libraries, CSS CDN, or web fonts at runtime. The renderer embeds local SVG or a verified local PNG as a data URI.
- A visual theme is not fully implemented unless its **signature motifs** are present in the actual page, not merely described in agent instructions.

## Dark — red-accented engineering presenter

Use the `driftmap-presenter` default dark language rather than generic neon-blue SaaS.

**Required features:**

- Charcoal near-black canvas (`#0a0b0f`), graphite panels (`#151922`), finely stroked edges (`#292e3a`).
- **Coral red is the primary highlight** (`#ef5b53`); red brand icon, red hero emphasis, red selected path/step and red primary action.
- Rose secondary (`#fa918b`); cool blue reserved for other semantics, and green reserved for good/completed *only if supported by the source*.
- Header micro-labels, restrained gradients, strong white title, readable panel typography, subtle status emphasis.
- No blue-dominant theme substitution.

## Morrito — cheerful, physical retro-game world

The core vocabulary is **not just sky blue and black borders**. Required motifs:

- Bright sky-blue header, patterned pale-blue sky, cream panels and **strong thick black borders with offset black shadows**.
- A **gold five-point star with eyes** (bundled `assets/morrito-star.svg`) for important, source-grounded annotations. Do not automatically add an “Important” claim with fabricated text.
- A **question box** for explicit uncertainty notes; uncertainty does not imply that the process succeeded or failed.
- Horizontal glossy **pipe segments** for every primary connection, and colored pipes on declared detours: green for normal path, orange for explicit pause/wait, red for explicit stop/failure, blue for other unclassified targets.
- The tube colors are decorations derived from the actual declared destinations; they do not add branches or execution instructions.
- Big tactile gold controls and yellow selection.
- A **continuous landscape footer** with rounded eyed hills, bushes, bright green turf, and brown earth (bundled `assets/morrito-scene.svg`).
- Local system display fonts and thick outlines; no remote assets.

## Gilded — parchment / stone / tactical RPG

Mere beige cards do not qualify. Include recognizable fantasy-presenter furniture:

- Parchment background (`#e5dcc4`) with restrained texture; gold ornamentation; serif title lettering with engraved strokes.
- **Stone-and-sage beveled panels** with inset highlights and hard corners.
- **Dark violet buttons and gold lettering**, with tactile bevel/highlight/shadow.
- **Sword** beside the interactive journey/heading (`assets/gilded-sword.svg`).
- **Magic wand** beside the node/stage guidance (`assets/gilded-wand.svg`).
- A **yellow fantasy riding-bird mascot** in the specimen or exploration surface: `assets/gilded-bird.svg` is a bundled standalone fallback. When the original local `driftmap-presenter/assets/gilded-bird.png` is installed alongside Storycraft, the generator prefers that PNG and embeds it into the output. No network download.
- A genuinely legible mobile heading: do not split long uppercase words in the middle.

## Component correspondence

| Visual purpose | Dark | Morrito | Gilded |
| --- | --- | --- | --- |
| Primary hue | Coral red | Royal blue + golden yellow | Old gold + deep violet |
| Panels | Graphite, fine border | Cream, bold black border/shadow | Sage stone, bevel |
| Active stage | Red outline + muted red fill | Yellow fill + blue selected edge | Pale gold fill + antique-gold border |
| Main link | Red arrow | Green 3D pipe | Bronze/gold arrow |
| Pause/stop | Labels remain explicit | Orange/red pipes | Explicit labels and muted antique line |
| Emphasis | Red coral | Eyed gold star | Sword / gold medallion |
| Instruction view | Monospace detail | Chunky inspector / question note | Wand-and-parchment inspector |
| Signature art | Red brandmark | Star + hills/grass/earth footer | Sword + wand + yellow riding-bird |

## Assets and intentional compatibility

`assets/` belongs to **Storycraft**. Its built-in sprites and illustrations are embedded at generation time. It does not need Drift Maps, Mermaid, `MAP.md`, node execution, or access to `driftmap-presenter`.

For closer fidelity where the original Gilded bird PNG is available *locally*, the renderer reuses that existing owned asset via relative sibling skill paths. If absent, it uses its own original SVG mascot. No hidden internet dependency or accidental asset copying from unrelated projects.

For user-provided artwork, follow [custom asset import guidance](custom-assets.md). Keep the same three theme identities, independent story model, and offline embedding requirement.

## Anti-patterns

- Dark mode recolored cyan/teal with almost no red.
- Morrito built as plain rounded cards with a grass-colored footer but no character star, pipe connections, or outlined world.
- Gilded built as beige text panels without sword/wand/bird iconography.
- Status pills where the source gives no status.
- A fake success story, altered diagram, or branch omitted for aesthetic simplicity.
- An ornamental SVG preventing keyboard focus, overflowing mobile widths, or misleading a route direction.
