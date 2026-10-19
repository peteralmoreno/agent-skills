#!/usr/bin/env python3
"""Build one self-contained read-only HTML front face for a Drift Map.

Uses PyYAML for safe YAML parsing. Supports a documented Mermaid subset: flowchart TD/TB/LR,
one --> edge per line, optional |labels|, and basic named node shapes.
Unsupported routing syntax fails rather than misrepresenting the map.
"""
import argparse
import base64
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "viewer-template.html"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from map_format import (CONTROL as CONTROLS, MapError, frontmatter as read_md,
                        node_frontmatter, graph)

FENCE_MARK = chr(96) * 3


def render_md(markdown):
    """Small intentionally conservative renderer. Raw HTML is escaped."""
    out, para, listing, code = [], [], False, False
    def flush():
        if para:
            out.append("<p>" + " ".join(para) + "</p>")
            para.clear()
    for line in markdown.splitlines():
        s = line.strip()
        if s.startswith(FENCE_MARK):
            flush()
            if listing:
                out.append("</ul>"); listing = False
            out.append("</code></pre>" if code else "<pre><code>")
            code = not code
            continue
        if code:
            out.append(html.escape(line) + "\n")
            continue
        if not s:
            flush()
            if listing:
                out.append("</ul>"); listing = False
            continue
        head = re.match(r"^(#{1,4})\s+(.+)$", s)
        if head:
            flush()
            if listing:
                out.append("</ul>"); listing = False
            h = min(len(head.group(1)) + 1, 5)
            out.append(f"<h{h}>{html.escape(head.group(2))}</h{h}>")
        elif s.startswith("- "):
            flush()
            if not listing:
                out.append("<ul>"); listing = True
            note = re.match(r"(Important|Uncertain):\s", s[2:], re.I)
            attrs = ' class="note-' + note.group(1).lower() + '"' if note else ""
            out.append("<li" + attrs + ">" + html.escape(s[2:]) + "</li>")
        else:
            if listing:
                out.append("</ul>"); listing = False
            para.append(html.escape(s))
    flush()
    if listing:
        out.append("</ul>")
    if code:
        out.append("</code></pre>")
    return "\n".join(out)


def load_map(map_file):
    path = Path(map_file).expanduser().resolve()
    if path.name != "MAP.md" or not path.is_file():
        raise MapError("Select an existing MAP.md file")
    meta, body = read_md(path)
    names, edges, chart = graph(body)
    nodes = []
    for ident, title in names.items():
        node = {"id": ident, "label": title, "control": ident in CONTROLS,
                "file": "", "requires": [], "produces": [], "tool_hints": [], "html": ""}
        if not node["control"]:
            file = path.parent / "nodes" / (ident + ".md")
            if not file.is_file():
                raise MapError(f"Missing node referenced in graph: {file}")
            props, text = node_frontmatter(file)
            for prop in ("requires", "produces", "tool_hints"):
                if isinstance(props.get(prop), list):
                    node[prop] = props[prop]
            node["max_visits"] = props.get("max_visits")
            node["file"] = "nodes/" + ident + ".md"
            node["html"] = render_md(text)
        nodes.append(node)
    extras = sorted(
        f.name for f in (path.parent / "nodes").glob("*.md")
        if f.stem not in names
    )
    if extras:
        print("Note: unreferenced nodes: " + ", ".join(extras), file=sys.stderr)
    return {"name": str(meta.get("name", path.parent.name)),
            "title": str(meta.get("name", path.parent.name)).replace("-", " ").title(),
            "version": str(meta.get("version", "unspecified")),
            "status": str(meta.get("status", "unspecified")),
            "overview": render_md(body.replace(chart, "", 1)),
            "nodes": nodes, "edges": edges}


def create(map_file, output, force=False, style="default"):
    if style not in ("default", "morrito", "gilded"):
        raise MapError("Unknown style: " + style)
    model = load_map(map_file)
    target = Path(output).expanduser().resolve()
    source = Path(map_file).expanduser().resolve()
    if target == source or target.suffix.lower() not in (".html", ".htm"):
        raise MapError("Output must be a distinct .html file")
    if target.exists() and not force:
        raise MapError(f"Output exists: {target}. Use --force only after review.")
    payload = json.dumps(model, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count("__MAP_DATA__") != 1:
        raise MapError("Viewer template must have exactly one payload placeholder")
    if style != "default":
        css = (ROOT / "assets" / (style + ".css")).read_text(encoding="utf-8")
        template = template.replace("</style>", css + "\n</style>", 1).replace(
            '<meta name="color-scheme" content="dark">',
            '<meta name="color-scheme" content="light">')
    if style == "morrito":
        star = base64.b64encode((ROOT / "assets" / "morrito-star.svg").read_bytes()).decode("ascii")
        template = template.replace("__MORRITO_STAR__", "data:image/svg+xml;base64," + star)
        scene = (ROOT / "assets" / "morrito-scene.html").read_text(encoding="utf-8")
        template = template.replace('<footer class="wrap foot">', scene + '<footer class="wrap foot">', 1)
    if style == "gilded":
        bird = base64.b64encode((ROOT / "assets" / "gilded-bird.png").read_bytes()).decode("ascii")
        template = template.replace("__GILDED_BIRD__", "data:image/png;base64," + bird)
    output_html = template.replace("__MAP_DATA__", payload)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(output_html, encoding="utf-8")
    return target, model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", help="Canonical MAP.md path")
    parser.add_argument("--out", help="Optional HTML output (defaults to map's overview.html)")
    parser.add_argument("--style", choices=("default", "morrito", "gilded"), default="default",
                        help="Visual style only: default dark, bright Morrito, or parchment Gilded")
    parser.add_argument("--force", action="store_true", help="Replace existing generated HTML")
    args = parser.parse_args()
    target = args.out or str(Path(args.map).expanduser().resolve().parent / "overview.html")
    try:
        output, model = create(args.map, target, args.force, args.style)
    except (MapError, OSError, UnicodeError) as exc:
        print("Error:", exc, file=sys.stderr)
        return 2
    print(f"Generated: {output} ({len(model['nodes'])} nodes; {len(model['edges'])} transitions)")
    print("HTML is read-only. MAP.md and nodes were not modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
