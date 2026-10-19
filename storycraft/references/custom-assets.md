# Importing custom visual assets into Storycraft

Storycraft is human-facing. It **may** present custom artwork, but artwork never authorizes new facts, steps, transitions, metrics, states, or actions. Its HTML output remains a standalone, offline file.

## Asset selection order

1. **Explicit user-provided asset:** supplied file/path/attachment and requested placement.
2. **Approved local reuse:** an asset in the current project or another installed skill that the user has identified or authorized (for example the original Presenter riding bird).
3. **Bundled Storycraft motif:** bundled star, pipes, scene, sword, wand, or bird, when no user asset is available.

Never choose a remote search result simply to decorate the page, silently scrape a logo or mascot, or pretend an unavailable asset has been imported. Confirm actual file bytes exist before using them. Do not replace one theme's essential visual vocabulary with a generic unrelated icon.

## Intake checklist

- **Origin and rights:** user-owned/approved file or properly licensed material; do not embed confidential/private images into a broadly shareable page unless requested.
- **Role:** what the asset depicts and where it appears—hero illustration, mascot, ornament, question marker, background, or diagram symbol.
- **Style scope:** `dark`, `morrito`, `gilded`, or all. It may be shared across themes without rewriting the content.
- **File checks:** existence, format (PNG/JPEG/WebP preferred), dimensions, transparency, reasonable byte size, animated vs static, and image quality.
- **Accessibility:** provide short meaningful `alt` for informative art; decorative sprites get `alt=""` / `aria-hidden="true"`.
- **Offline requirement:** generated HTML embeds assets; a file path may be an *input* at authoring time, never a required runtime resource.

## Built-in Gilded bird slot

The structured renderer already supports a specific named raster asset: `gilded-bird.png`. It reuses **exactly the same image** for the large riding bird and the small bird/question annotation. Preferred local methods:

```bash
# A) Copy a file you are permitted to use into the skill.
cp ./art/my-yellow-bird.png storycraft/assets/gilded-bird.png

# B) Or set an explicit source path without modifying the skill.
STORYCRAFT_PRESENTER_BIRD=./art/my-yellow-bird.png \
  python3 storycraft/scripts/render_story.py ./draft.story.json \
  --style gilded --out ./draft-gilded.html

# C) Reuse the matching installed Presenter asset, when available.
python3 storycraft/scripts/sync_presenter_bird.py
```

To download the *original known Presenter image* from the owner's public repository when it is not installed, use `sync_presenter_bird.py --download` **only with explicit permission for network access**. The importer verifies the Git blob SHA before copying. These methods do not alter story JSON.

**Behavior and limitations:** The renderer checks `STORYCRAFT_PRESENTER_BIRD` first when set, then the bundled Gilded PNG, then known local Presenter directories; otherwise it renders the bundled SVG bird. It accepts a valid PNG file up to 4 MB for this slot. This is not an arbitrary external image loader. Other theme SVGs are still read from Storycraft's own `assets/` directory.

## Other custom images and sprite sheets

For a new hero, background, sticker, badge, or extra character not supported as a named renderer slot, use **custom HTML composition** or explicitly extend the renderer and its tests. For example, in a bespoke authoring script, embed a local PNG as a data URI:

```python
import base64
from pathlib import Path
from html import escape

asset = Path('./art/guide.png')
raw = asset.read_bytes()
assert raw.startswith(b'\x89PNG\r\n\x1a\n'), 'Expected PNG'
assert len(raw) <= 4_000_000, 'Optimize artwork before embedding'
data_uri = 'data:image/png;base64,' + base64.b64encode(raw).decode('ascii')
alt = escape('Illustrated guide', quote=True)
img_tag = f'<img src="{data_uri}" alt="{alt}" width="320" loading="lazy">'
```

Use CSS `object-fit: contain` for mascots and logos that should never be cropped. Avoid unnecessary retina-sized assets or giant data URIs; optimize them before final packaging. For SVG, review and strip script elements, event attributes, `foreignObject`, remote references, and unsafe CSS; when uncertain, rasterize offline first. Do not execute embedded code from SVG or documents.

## Acceptance checks

1. Story, links, data, all declared graph edges, and the primary-route order match the source *before and after* substitution.
2. Every custom image is embedded or safely inline; loading the finished HTML from a disconnected browser still works.
3. All artwork is the user's approved artwork (or bundled original); no invented branded identity.
4. Mascots remain proportionate, transparent edges remain clean, and small notations/icons are readable on mobile.
5. Render at 1440, 834, 390, and 320 pixels. Check overflow, clipping, readability, and JavaScript errors. Update screenshot fixtures when the visual change is intentional.

Import is opt-in. Retain bundled art when no acceptable custom file is present. Never silently fail to use an explicitly requested asset; explain the blocker and preserve the user's original file.
