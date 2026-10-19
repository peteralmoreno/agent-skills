# Storycraft 🌯

A portable [Agent Skill](https://agentskills.io/) for turning rough briefs, notes, Markdown, or HTML into polished **single-file interactive HTML stories**.

It supports three visual modes aligned with the distinct visual systems in Drift Map Presenter: **Dark**, **Morrito**, and **Gilded**. The design changes; the underlying explanation does not.

## Quickstart

Requires Python 3.9+. The renderer uses only the standard library.

```bash
# From the directory containing storycraft/
python3 storycraft/scripts/render_story.py \
  storycraft/examples/burrito-blaster.story.json \
  --style all --out-dir ./scratch/burrito/
```

Open `./scratch/burrito/burrito-blaster-dark.html`, `...-morrito.html`, and `...-gilded.html` in your browser. All pages are self-contained; there are no external fonts, scripts, images, CDNs, or build steps.

## How to use it with an agent

Put the entire `storycraft/` folder where your agent reads skills, then use a prompt such as:

> Use the Storycraft skill to redesign `./scratch/rough.html`. Preserve the source's claims and exact process branches. Use the **Morrito** style, generate one standalone HTML file, test it at desktop and phone widths, and report the QA results.

Or request all three visual variants:

> Use Storycraft with `--style all` on `./scratch/idea.md`. Create a shared `idea.story.json` first, then produce Dark, Morrito, and Gilded pages from that one model. Save the outputs in `./scratch/story/`. Mark speculative details explicitly and do not invent facts or evidence.

Examples of possible local installation paths:

| Agent | Folder |
| --- | --- |
| Codex / general Agent Skills | `.agents/skills/storycraft/` |
| Claude Code | `.claude/skills/storycraft/` |
| Oh My Pi | `.omp/skills/storycraft/` (check your local discovery configuration) |

The `SKILL.md` goes directly inside that directory. Project-local paths are examples; consult your particular agent's configured skill search paths.

## Programmatic commands

```bash
# Dark is default
python3 storycraft/scripts/render_story.py example.story.json --out overview.html

# Choose a style
python3 storycraft/scripts/render_story.py example.story.json --style gilded --out gilded.html

# Generate all three
python3 storycraft/scripts/render_story.py example.story.json --style all --out-dir output/

# Audit offline page structure
python3 storycraft/scripts/check_story.py output/*.html

# Optional browser screenshots: Playwright + local Chromium
python3 -m pip install playwright
python3 -m playwright install chromium
python3 storycraft/scripts/preview_story.py output/burrito-blaster-dark.html --out-dir previews/

# Run unit tests
python3 -m unittest discover -s storycraft/tests -v
```

The renderer rejects unknown node references, disconnected primary path edges, unsafe IDs, unsupported link schemes, and replacement of an existing output without explicit `--force`.

## Signature visual components

These are real bundled components, not descriptions of colors:

| Theme | Distinctive components in rendered output |
| --- | --- |
| **Dark** | Graphite panels, red gradient brandmark, coral-red title and selected stages |
| **Morrito** | Gold star with eyes, explicit important/question notes, outlined cream boxes, **longer green/orange/red glossy route pipes with collars on both ends**, illustrated hills/grass/earth footer |
| **Gilded** | Ornate parchment, beveled sage stone, violet-and-gold controls, sword, wand, **golden riding-bird mascot**, the same riding-bird art reused at small size with a floating question mark |

Both Gilded bird components—the main riding-bird mascot and the small curious/question marker—use **one identical artwork source**. Storycraft searches installed sibling `driftmap-presenter` skills for the original `assets/gilded-bird.png` and embeds it automatically when present. If the original is not installed locally, both use the bundled `assets/gilded-bird.svg`.

To **import the original Presenter asset** into this self-contained skill, try the local copy first:

```bash
python3 storycraft/scripts/sync_presenter_bird.py
```

If the sibling skill isn't installed, you can explicitly fetch the exact original file from the linked public `peteralmoreno/agent-skills` repo:

```bash
python3 storycraft/scripts/sync_presenter_bird.py --download
```

The import verifies Git blob SHA-1 `d8c10c7f485c1e7ff2c4cbf946344ec0609cf269` before using the image. The optional one-time download requires internet, but the **rendered HTML never does**. Rerender your Gilded page after the import to embed the original art. The star, landscape, pipes, sword and wand are bundled directly with Storycraft.

Important and uncertain notes can be included explicitly in a `callouts` array. See [the Storycraft schema](references/story-schema.md).

## Bring your own artwork

Storycraft can incorporate **user-supplied mascots, sprites, logos, icons, and scenery** without abandoning its three visual styles. The agent should inspect and reuse an explicitly supplied local asset, check that it can be used, and embed it into the finished one-file HTML. Avoid external image URLs, hidden network requirements, and unsanitized SVG.

For the built-in Gilded bird slot, install your own licensed PNG (the large mascot and the small question-note bird will share it):

```bash
cp ./my-assets/yellow-bird.png storycraft/assets/gilded-bird.png
python3 storycraft/scripts/render_story.py storycraft/examples/burrito-blaster.story.json \
  --style gilded --out ./scratch/burrito-gilded-custom.html
```

Or leave the skill's files unchanged and point it at your artwork for a single render:

```bash
STORYCRAFT_PRESENTER_BIRD=./my-assets/yellow-bird.png \
  python3 storycraft/scripts/render_story.py storycraft/examples/burrito-blaster.story.json \
  --style gilded --out ./scratch/burrito-gilded-custom.html
```

*Note:* `STORYCRAFT_PRESENTER_BIRD` works for this named Gilded PNG slot; it is **not** a general-purpose override for every illustration. For other custom placements, use the skill's bespoke-HTML path or extend its renderer explicitly. The skill preserves the story model and diagram topology regardless of theme or artwork. See [importing custom assets](references/custom-assets.md).

## Skill layout

```text
storycraft/
  SKILL.md
  README.md
  references/
    story-architecture.md
    story-schema.md
    custom-assets.md
    style-systems.md
    visual-qa.md
  scripts/
    render_story.py
    check_story.py
    preview_story.py
    sync_presenter_bird.py
  assets/
    common-story.css
    dark-presenter.css
    morrito-presenter.css
    gilded-presenter.css
    morrito-star.svg
    morrito-question-block.svg
    morrito-scene.svg
    gilded-sword.svg
    gilded-wand.svg
    gilded-bird.svg
  examples/
    burrito-blaster-rough.md
    burrito-blaster-rough.html
    burrito-blaster.story.json
    burrito-blaster-dark.html
    burrito-blaster-morrito.html
    burrito-blaster-gilded.html
  tests/
    test_storycraft.py
```

## Scope

Storycraft is a **presentation system**, not an application runtime. Clicking a stage previews explanatory details. Replay is a non-executing illustration. A polished frontend cannot prove a claim not supported by the source.

Its built-in renderer intentionally uses a constrained narrative schema, with a primary route and explicitly labeled alternatives. For unusual layouts or complex diagrams, the skill allows agent-authored standalone HTML with the same design principles and QA gates.
