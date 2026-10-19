#!/usr/bin/env python3
"""Build one self-contained read-only HTML front face for a Drift Map.

Standard library only. Supports a documented Mermaid subset: flowchart TD/TB/LR,
one --> edge per line, optional |labels|, and basic named node shapes.
Unsupported routing syntax fails rather than misrepresenting the map.
"""
import argparse
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "viewer-template.html"
SLUG = re.compile(r"^[a-z][a-z0-9_-]*$")
CONTROLS = {"pause", "stop", "complete"}
FENCE_MARK = chr(96) * 3
FENCE = re.compile(re.escape(FENCE_MARK) + r"mermaid[ \t]*\n(.*?)\n" + re.escape(FENCE_MARK), re.S | re.I)
HEADER = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", re.S)
NODE = re.compile(r"^([A-Za-z][\w-]*)(.*)$")
SHAPES = (
    re.compile(r'^\["([^"]+)"\]$'),
    re.compile(r'^\(\["([^"]+)"\]\)$'),
    re.compile(r'^\("([^"]+)"\)$'),
    re.compile(r'^\[([^\]]+)\]$'),
)


class MapError(Exception):
    pass


def read_md(path):
    source = path.read_text(encoding="utf-8")
    match = HEADER.match(source)
    if not match:
        raise MapError(f"{path}: missing YAML frontmatter")
    meta, key = {}, None
    for line in match.group(1).splitlines():
        property_match = re.match(r"^([a-z][a-z0-9_-]*):\s*(.*)$", line)
        if property_match:
            key, raw = property_match.groups()
            val = raw.strip().strip('"').strip("'")
            meta[key] = val if val else []
        else:
            item = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if item and key and isinstance(meta.get(key), list):
                meta[key].append(item.group(1).strip().strip('"').strip("'"))
    return meta, source[match.end():]


def node_token(raw):
    token = raw.strip().rstrip(";").strip()
    match = NODE.fullmatch(token)
    if not match:
        raise MapError(f"Invalid Mermaid node token: {token!r}")
    node_id, decoration = match.groups()
    if not SLUG.fullmatch(node_id):
        raise MapError(f"Node IDs must be lowercase filename-safe names: {node_id}")
    if not decoration.strip():
        return node_id, None
    for shape in SHAPES:
        match = shape.fullmatch(decoration.strip())
        if match:
            return node_id, match.group(1)
    raise MapError(f"Unsupported Mermaid shape for {node_id}: {decoration}")


def graph(body):
    found = re.search(r"^## Flowchart[ \t]*$", body, re.M | re.I)
    if not found:
        raise MapError("MAP.md needs a ## Flowchart heading")
    fenced = FENCE.search(body, found.end())
    if not fenced:
        raise MapError("## Flowchart needs a Mermaid code block")
    lines = fenced.group(1).splitlines()
    if not lines or not re.fullmatch(r"\s*flowchart\s+(TD|TB|LR)\s*", lines[0]):
        raise MapError("Supported declarations: flowchart TD, TB, LR")
    nodes, edges = {}, []
    for original in lines[1:]:
        line = original.strip()
        if not line or line.startswith("%%") or re.match(r"^(classDef|class|style|linkStyle)\b", line):
            continue
        if "-->" not in line:
            key, title = node_token(line)
            nodes.setdefault(key, title or key.replace("-", " ").title())
            continue
        if line.count("-->") != 1:
            raise MapError(f"Use one directed Mermaid edge per line: {line}")
        from_part, to_part = line.split("-->", 1)
        source, source_title = node_token(from_part)
        to_part, label = to_part.strip(), ""
        if to_part.startswith("|"):
            components = to_part.split("|", 2)
            if len(components) != 3:
                raise MapError(f"Unclosed edge label: {line}")
            label, to_part = components[1].strip(), components[2].strip()
        target, target_title = node_token(to_part)
        nodes.setdefault(source, source_title or source.replace("-", " ").title())
        nodes.setdefault(target, target_title or target.replace("-", " ").title())
        if source_title:
            nodes[source] = source_title
        if target_title:
            nodes[target] = target_title
        edges.append({"from": source, "to": target, "label": label})
    if not edges or "setup" not in nodes or not any(e["from"] == "setup" for e in edges):
        raise MapError("Graph requires a setup entry and directed edges")
    return nodes, edges, fenced.group(0)


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
            out.append("<li>" + html.escape(s[2:]) + "</li>")
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
            props, text = read_md(file)
            for prop in ("requires", "produces", "tool_hints"):
                if isinstance(props.get(prop), list):
                    node[prop] = props[prop]
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


def create(map_file, output, force=False):
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
    output_html = template.replace("__MAP_DATA__", payload)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(output_html, encoding="utf-8")
    return target, model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", help="Canonical MAP.md path")
    parser.add_argument("--out", help="Optional HTML output (defaults to map's overview.html)")
    parser.add_argument("--force", action="store_true", help="Replace existing generated HTML")
    args = parser.parse_args()
    target = args.out or str(Path(args.map).expanduser().resolve().parent / "overview.html")
    try:
        output, model = create(args.map, target, args.force)
    except (MapError, OSError, UnicodeError) as exc:
        print("Error:", exc, file=sys.stderr)
        return 2
    print(f"Generated: {output} ({len(model['nodes'])} nodes; {len(model['edges'])} transitions)")
    print("HTML is read-only. MAP.md and nodes were not modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
