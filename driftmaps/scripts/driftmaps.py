#!/usr/bin/env python3
"""DriftMaps: local scaffolding, map validation, inspection, Trail initialization.
Stdlib only. This is not a workflow/AI runtime or a permissions validator.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

HERE = Path(__file__).resolve().parents[1]
CONTROL = {"pause", "stop", "complete"}
SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
HEADER = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---\s*\r?\n", re.S)
FENCE = re.compile(re.escape(chr(96) * 3) + r"mermaid[ \t]*\n(.*?)\n" +
                   re.escape(chr(96) * 3), re.S | re.I)
NODE = re.compile(r"^([a-z][a-z0-9-]*)(.*)$")
SHAPES = [re.compile(x) for x in (
    r'^\["([^"]+)"\]$', r'^\(\["([^"]+)"\]\)$',
    r'^\("([^"]+)"\)$', r'^\[([^\]]+)\]$')]


class MapError(Exception):
    pass


def slug(value):
    if not SLUG.fullmatch(value):
        raise MapError("Invalid lowercase kebab-case name: " + value)
    return value


def frontmatter(file):
    text = file.read_text(encoding="utf-8")
    m = HEADER.match(text)
    if not m:
        raise MapError("Missing YAML frontmatter: " + str(file))
    data, key = {}, None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        top = re.fullmatch(r"([a-z][a-z0-9_]*):\s*(.*)", line)
        sub = re.fullmatch(r"  ([a-z][a-z0-9_]*):\s*(.*)", line)
        item = re.fullmatch(r"  - (.+)", line)
        if top:
            key, val = top.groups()
            data[key] = val.strip().strip('"').strip("'") if val else []
        elif sub and key:
            if not isinstance(data[key], dict):
                data[key] = {}
            data[key][sub.group(1)] = sub.group(2).strip().strip('"').strip("'")
        elif item and key and isinstance(data.get(key), list):
            data[key].append(item.group(1).strip().strip('"').strip("'"))
        else:
            raise MapError("Unsupported header line in " + str(file) + ": " + line)
    return data, text[m.end():]


def node(token):
    match = NODE.fullmatch(token.strip().rstrip(";").strip())
    if not match:
        raise MapError("Unsupported graph node: " + token)
    key, shape = match.groups()
    slug(key)
    if shape.strip() and not any(p.fullmatch(shape.strip()) for p in SHAPES):
        raise MapError("Unsupported node shape: " + token)
    return key


def graph(body):
    start = re.search(r"^## Flowchart\s*$", body, re.M)
    if not start:
        raise MapError("MAP.md requires ## Flowchart")
    m = FENCE.search(body, start.end())
    if not m:
        raise MapError("Flowchart requires fenced Mermaid")
    lines = m.group(1).splitlines()
    if not lines or not re.fullmatch(r"\s*flowchart\s+(TD|TB|LR)\s*", lines[0]):
        raise MapError("Expected flowchart TD, TB, or LR")
    vertices, edges = set(), []
    for raw in lines[1:]:
        line = raw.strip()
        if not line or line.startswith("%%") or re.match(r"^(classDef|class|style|linkStyle)\b", line):
            continue
        if "-->" not in line:
            vertices.add(node(line))
            continue
        if line.count("-->") != 1:
            raise MapError("One --> transition per line: " + line)
        left, right = line.split("-->", 1)
        src, right, label = node(left), right.strip(), ""
        if right.startswith("|"):
            pieces = right.split("|", 2)
            if len(pieces) != 3 or not pieces[1].strip():
                raise MapError("Bad edge label: " + line)
            label, right = pieces[1].strip(), pieces[2].strip()
        dst = node(right)
        vertices.update((src, dst))
        edges.append((src, label, dst))
    if not edges or "setup" not in vertices:
        raise MapError("Map needs a setup node and transitions")
    return vertices, edges


def analyze(source):
    path = Path(source).expanduser().resolve()
    if path.name != "MAP.md" or not path.is_file():
        raise MapError("Select an existing MAP.md")
    props, body = frontmatter(path)
    verts, edges = graph(body)
    problems = []
    if props.get("name") != path.parent.name:
        problems.append("name must match the map directory")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(props.get("version", ""))):
        problems.append("version must be major.minor.patch")
    if props.get("status") not in ("draft", "active", "example"):
        problems.append("status must be draft, active, or example")
    limits = props.get("limits")
    max_transitions = str(limits.get("max_transitions", "")) if isinstance(limits, dict) else ""
    if not max_transitions.isdigit() or int(max_transitions) < 1:
        problems.append("limits.max_transitions must be a positive integer")
    if not any(src == "setup" for src, _, _ in edges):
        problems.append("setup must have an outgoing edge")
    if any(dst == "setup" for _, _, dst in edges):
        problems.append("setup cannot have incoming edges")
    if any(src in CONTROL for src, _, _ in edges):
        problems.append("control endpoints cannot have outgoing edges")
    if not any(dst in CONTROL for _, _, dst in edges):
        problems.append("no completion, pause or stop path")
    reached = {"setup"}
    while True:
        nxt = reached | {dst for src, _, dst in edges if src in reached}
        if reached == nxt:
            break
        reached = nxt
    for name in sorted(verts - reached):
        problems.append("unreachable node: " + name)
    for name in sorted(verts - CONTROL):
        file = path.parent / "nodes" / (name + ".md")
        if not file.is_file():
            problems.append("missing node file: nodes/" + name + ".md")
            continue
        try:
            meta, _ = frontmatter(file)
            for field in ("requires", "produces"):
                if not isinstance(meta.get(field), list):
                    problems.append(name + ": " + field + " must be a YAML list")
            if "tool_hints" in meta and not isinstance(meta["tool_hints"], list):
                problems.append(name + ": tool_hints must be a list")
            if "max_visits" in meta:
                val = str(meta["max_visits"])
                if not val.isdigit() or int(val) < 1:
                    problems.append(name + ": invalid max_visits")
        except MapError as exc:
            problems.append(str(exc))
        outs = [label for src, label, _ in edges if src == name]
        if not outs:
            problems.append(name + " has no outgoing transition")
        if len(outs) > 1 and (not all(outs) or len(set(outs)) != len(outs)):
            problems.append(name + " needs unique, nonempty branch labels")
    for file in (path.parent / "nodes").glob("*.md"):
        if file.stem not in verts - CONTROL:
            problems.append("unregistered node: " + file.name)
    return {"name": props.get("name"), "version": props.get("version"),
            "status": props.get("status"), "map": str(path),
            "max_transitions": int(max_transitions) if max_transitions.isdigit() else None,
            "nodes": sorted(verts), "edges": edges, "errors": problems}


def require_valid(path):
    result = analyze(path)
    if result["errors"]:
        raise MapError("Invalid map:\n" + "\n".join(result["errors"]))
    return result


def init(args):
    root = Path(args.root).expanduser().resolve()
    (root / "maps").mkdir(parents=True, exist_ok=True)
    folder = root / ".driftmaps"
    folder.mkdir(exist_ok=True)
    (folder / "runs").mkdir(exist_ok=True)
    (folder / "memory").mkdir(exist_ok=True)
    ignore = folder / ".gitignore"
    if not ignore.exists():
        ignore.write_text("*\n!.gitignore\n", encoding="utf-8")
    print("Initialized:", root)


def create(args):
    name = slug(args.name)
    folder = Path(args.root).expanduser().resolve() / "maps" / name
    if folder.exists():
        raise MapError("Refusing to overwrite: " + str(folder))
    folder.mkdir(parents=True)
    (folder / "nodes").mkdir()
    template = (HERE / "assets" / "MAP-template.md").read_text(encoding="utf-8")
    (folder / "MAP.md").write_text(template.replace("REPLACE_NAME", name).replace(
        "REPLACE_TITLE", name.replace("-", " ").title()), encoding="utf-8")
    node_template = (HERE / "assets" / "node-template.md").read_text(encoding="utf-8")
    for name in ("setup", "work"):
        (folder / "nodes" / (name + ".md")).write_text(
            node_template.replace("# TODO: Node instructions", "# " + name.title()),
            encoding="utf-8")
    print("Created draft:", folder)


def listing(args):
    folder = Path(args.root).expanduser().resolve() / "maps"
    if not folder.exists():
        raise MapError("No map library; run init")
    for path in sorted(folder.glob("*/MAP.md")):
        props, _ = frontmatter(path)
        print(path.parent.name, props.get("status", "?"), props.get("version", "?"))


def validate(args):
    result = analyze(args.map)
    print("Map:", result["name"], "| nodes:", len(result["nodes"]),
          "| transitions:", len(result["edges"]))
    for error in result["errors"]:
        print("ERROR:", error)
    if result["errors"]:
        raise MapError("Structural validation failed")
    print("Structural validation passed; no AI execution or verification performed.")


def inspect(args):
    result = analyze(args.map)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["name"])
        for src, label, dst in result["edges"]:
            print(src, "--", label or "continue", "-->", dst)
        print(len(result["errors"]), "structural issue(s)")
    if result["errors"]:
        raise MapError("Map requires fixes")


def inputs(path):
    if not path:
        return "  {}\n"
    raw = Path(path).expanduser().read_text(encoding="utf-8")
    seen, records = set(), []
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.fullmatch(r"([A-Za-z][A-Za-z0-9_]*):[ \t]+(.+?)\s*", line)
        if not m:
            raise MapError("Input YAML must use flat key: value entries")
        key, value = m.groups()
        if key in seen:
            raise MapError("Duplicate input key: " + key)
        seen.add(key)
        if value.startswith("!") or "\x00" in value or "&" in value or "*" in value:
            raise MapError("Unsupported input YAML: " + key)
        records.append("  " + key + ": " + value + "\n")
    return "".join(records) if records else "  {}\n"


def digest(path):
    files = [path] + sorted((path.parent / "nodes").glob("*.md"))
    sha = hashlib.sha256()
    for item in files:
        sha.update(item.relative_to(path.parent).as_posix().encode("utf-8") + b"\0")
        sha.update(item.read_bytes() + b"\0")
    return sha.hexdigest()


def start(args):
    model = require_valid(args.map)
    if model["status"] == "draft" and not args.allow_draft:
        raise MapError("Draft maps require --allow-draft for a supervised run")
    source = Path(args.map).expanduser().resolve()
    # Validate input before creating any runtime directories.
    context = inputs(args.input_file)
    root = Path(args.root).expanduser().resolve() / ".driftmaps" / "runs"
    root.mkdir(parents=True, exist_ok=True)
    run_id = model["name"] + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    output = root / run_id
    output.mkdir(exist_ok=False)
    (output / "artifacts").mkdir()
    trail = output / "trail.yaml"
    def q(x):
        return json.dumps(str(x))
    trail.write_text(
        "meta:\n  run: " + q(run_id) + "\n  map: " + q(model["name"]) +
        "\n  version: " + q(model["version"]) +
        "\n  source: " + q(source) +
        "\n  source_sha256: " + q(digest(source)) +
        "\n  max_transitions: " + str(model["max_transitions"]) +
        "\ncurrent:\n  status: running\n  node: setup\n" +
        "context:\n" + context + "artifacts: {}\nhistory: []\n",
        encoding="utf-8")
    print("Prepared Trail:", trail)
    print("No node was executed; the agent must read MAP.md and nodes/setup.md.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init"); p.add_argument("--root", default="."); p.set_defaults(fn=init)
    p = sub.add_parser("new"); p.add_argument("name"); p.add_argument("--root", default="."); p.set_defaults(fn=create)
    p = sub.add_parser("list"); p.add_argument("--root", default="."); p.set_defaults(fn=listing)
    p = sub.add_parser("validate"); p.add_argument("map"); p.set_defaults(fn=validate)
    p = sub.add_parser("inspect"); p.add_argument("map"); p.add_argument("--json", action="store_true"); p.set_defaults(fn=inspect)
    p = sub.add_parser("start"); p.add_argument("map"); p.add_argument("--root", default=".")
    p.add_argument("--input-file"); p.add_argument("--allow-draft", action="store_true"); p.set_defaults(fn=start)
    args = parser.parse_args()
    try:
        args.fn(args)
    except (MapError, OSError, UnicodeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
