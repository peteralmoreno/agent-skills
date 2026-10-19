"""Shared parsing rules, bundled identically in each independently installable Skill."""
from pathlib import Path
import re

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Install YAML support: python -m pip install 'PyYAML>=6.0,<7'") from exc

CONTROL = {"pause", "stop", "complete"}
SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
HEADER = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)", re.S)
FENCE = re.compile(r"^```mermaid[ \t]*\n(.*?)\n```[ \t]*$", re.S | re.M)
NODE = re.compile(r"^([a-z][a-z0-9-]*)(.*)$")
SHAPES = [re.compile(x) for x in (
    r'^\["([^"]+)"\]$', r'^\(\["([^"]+)"\]\)$',
    r'^\("([^"]+)"\)$', r'^\[([^\]]+)\]$')]


class MapError(ValueError):
    pass


class UniqueSafeLoader(yaml.SafeLoader):
    """Safe YAML, with duplicate mapping keys rejected instead of overwritten."""


def _mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str):
            raise MapError("YAML mapping keys must be strings")
        if key in result:
            raise MapError("Duplicate YAML key: " + key)
        result[key] = loader.construct_object(value_node)
    return result


UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def read_yaml(text):
    try:
        data = yaml.load(text, Loader=UniqueSafeLoader)
    except yaml.YAMLError as exc:
        raise MapError("Invalid YAML: " + str(exc)) from exc
    if not isinstance(data, dict):
        raise MapError("Expected a YAML mapping")
    return data


def frontmatter(path):
    text = Path(path).read_text(encoding="utf-8")
    match = HEADER.match(text)
    if not match:
        raise MapError("Missing YAML frontmatter: " + str(path))
    try:
        return read_yaml(match.group(1)), text[match.end():]
    except MapError as exc:
        raise MapError(str(path) + ": " + str(exc)) from exc


def node_frontmatter(path):
    meta, body = frontmatter(path)
    for field in ("requires", "produces", "tool_hints"):
        if field == "tool_hints" and field not in meta:
            continue
        value = meta.get(field)
        if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
            raise MapError(str(path) + ": " + field + " must be a YAML list of nonempty strings")
    if "max_visits" in meta and (type(meta["max_visits"]) is not int or meta["max_visits"] < 1):
        raise MapError(str(path) + ": max_visits must be a positive integer")
    return meta, body


def node_token(raw):
    token = raw.strip()
    match = NODE.fullmatch(token)
    if not match or not SLUG.fullmatch(match.group(1)):
        raise MapError("Invalid lowercase kebab-case node: " + token)
    ident, shape = match.groups()
    if not shape.strip():
        return ident, None
    for pattern in SHAPES:
        label = pattern.fullmatch(shape.strip())
        if label:
            return ident, label.group(1)
    raise MapError("Unsupported node shape: " + token)


def graph(body):
    # Ignore headings inside code fences and stop at the next peer/parent heading.
    headings, fence = [], None
    for match in re.finditer(r"^.*$", body, re.M):
        line = match.group(0)
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            marks, suffix = marker.groups()
            if fence is None:
                fence = marks
            elif marks[0] == fence[0] and len(marks) >= len(fence) and not suffix.strip():
                fence = None
            continue
        if fence is None and re.match(r"^#{1,2} ", line):
            headings.append(match)
    starts = [h for h in headings if h.group(0).rstrip() == "## Flowchart"]
    if len(starts) != 1:
        raise MapError("MAP.md requires exactly one ## Flowchart section")
    start = starts[0]
    end = next((h.start() for h in headings if h.start() > start.start()), len(body))
    section = body[start.end():end]
    blocks = list(FENCE.finditer(section))
    # Require the graph directly in the section; no nested/example fences.
    if len(blocks) != 1 or section[:blocks[0].start()].strip() or section[blocks[0].end():].strip():
        raise MapError("Flowchart section must contain exactly one fenced Mermaid graph")
    block = blocks[0]
    lines = block.group(1).splitlines()
    if not lines or not re.fullmatch(r"\s*flowchart\s+(TD|TB|LR)\s*", lines[0]):
        raise MapError("Expected flowchart TD, TB, or LR")
    nodes, edges = {}, []
    for raw in lines[1:]:
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        line = line.removesuffix(";").rstrip()
        if ";" in line:
            raise MapError("Use one Mermaid statement per line: " + raw)
        if re.match(r"^(classDef|class|style|linkStyle)\s+", line):
            style = r"(?:classDef|style|linkStyle)\s+[a-zA-Z0-9_,-]+\s+[a-zA-Z-]+:[#a-zA-Z0-9.%() -]+(?:,[a-zA-Z-]+:[#a-zA-Z0-9.%() -]+)*"
            classes = r"class\s+[a-z0-9,-]+\s+[a-zA-Z][a-zA-Z0-9_-]*"
            if not re.fullmatch(style, line) and not re.fullmatch(classes, line):
                raise MapError("Unsupported style statement: " + raw)
            continue
        if "-->" not in line:
            ident, title = node_token(line)
            nodes[ident] = title or nodes.get(ident, ident.replace("-", " ").title())
            continue
        if line.count("-->") != 1:
            raise MapError("One --> transition per line (one directed Mermaid edge): " + line)
        left, right = line.split("-->")
        src, title = node_token(left)
        nodes[src] = title or nodes.get(src, src.replace("-", " ").title())
        right, label = right.strip(), ""
        if right.startswith("|"):
            parts = right.split("|", 2)
            if len(parts) != 3 or not parts[1].strip():
                raise MapError("Bad edge label: " + line)
            label, right = parts[1].strip(), parts[2]
        dst, title = node_token(right)
        nodes[dst] = title or nodes.get(dst, dst.replace("-", " ").title())
        edges.append({"from": src, "to": dst, "label": label})
    if not edges or not any(e["from"] == "setup" for e in edges):
        raise MapError("Graph requires a setup entry and directed edges")
    return nodes, edges, block.group(0)
