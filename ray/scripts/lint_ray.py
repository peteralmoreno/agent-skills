#!/usr/bin/env python3
"""Validate the shape of a canonical RAY intent and optionally extract JSON.

Zero dependencies beyond the Python standard library.
This is a structural aid, NOT semantic validation, Jira integration, or PRISM.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HEADER = re.compile(r"^\s*(?:#{1,2}\s+)?Intent\s*$", re.IGNORECASE)
FIELD = re.compile(r"^\s*(?P<letter>[RAY])\s*[—-]\s*(?P<label>[A-Za-z]+)\s*:\s*(?P<value>.*)$")
BULLET = re.compile(r"^\s*[-*]\s*\[(?P<grade>[1-4]):(?P<label>Consider|Prefer|Strong|Required)\]\s+(?P<text>.+?)\s*$")
NEXT_HEADING = re.compile(r"^\s*#{1,2}\s+[^#\s].*$")
SEPARATOR = re.compile(r"^\s*(?:-{3,}|\*{3,})\s*$")
EXPECTED = {"R": "Result", "A": "Angle", "Y": "Why"}
GRADE_NAMES = {1: "Consider", 2: "Prefer", 3: "Strong", 4: "Required"}


def parse_ray(content: str) -> dict[str, Any]:
    """Parse exactly one RAY block. Return errors and a normalized handoff object."""
    result: dict[str, Any] = {
        "format": "ray/v1",
        "valid": False,
        "result": "",
        "angles": [],
        "angle_note": None,
        "why": "",
        "errors": [],
        "warnings": [],
    }
    errors: list[str] = result["errors"]
    warnings: list[str] = result["warnings"]
    lines = content.splitlines()
    first = next((i for i, line in enumerate(lines) if line.strip()), None)
    if first is None:
        errors.append("Document is empty; expected an Intent heading.")
        return result
    if not HEADER.fullmatch(lines[first]):
        errors.append("Expected 'Intent' (or '## Intent') as the first non-empty line.")
        return result

    fields: dict[str, list[str]] = {}
    current: str | None = None
    observed: list[str] = []
    for line_index in range(first + 1, len(lines)):
        raw = lines[line_index]
        if SEPARATOR.fullmatch(raw) or NEXT_HEADING.fullmatch(raw):
            break
        match = FIELD.fullmatch(raw)
        if match:
            letter, label, value = match.group("letter"), match.group("label"), match.group("value")
            if label != EXPECTED[letter]:
                errors.append(f"Line {line_index+1}: expected label '{EXPECTED[letter]}' for {letter}, got '{label}'.")
            if letter in fields:
                errors.append(f"Line {line_index+1}: duplicate field {letter}.")
                current = None
                continue
            fields[letter] = [value.strip()] if value.strip() else []
            observed.append(letter)
            current = letter
            continue
        if raw.strip():
            if current is None:
                errors.append(f"Line {line_index+1}: content before the first R field or after a duplicate field.")
            else:
                fields[current].append(raw.strip())

    if observed != ["R", "A", "Y"]:
        errors.append(f"Fields must appear once and in order R, A, Y (found: {', '.join(observed) or 'none'}).")

    if "R" in fields:
        result["result"] = " ".join(fields["R"]).strip()
        if not result["result"]:
            errors.append("R — Result must not be empty.")
    if "Y" in fields:
        result["why"] = " ".join(fields["Y"]).strip()
        if not result["why"]:
            errors.append("Y — Why must not be empty.")

    if "A" in fields:
        entries = fields["A"]
        if not entries:
            errors.append("A — Angle must state Open or have at least one graded decision.")
        elif re.match(r"^open(?:$|\s|[—:;-])", entries[0], re.IGNORECASE):
            if len(entries) != 1:
                errors.append("An Open Angle cannot also have graded bullet lines; choose one representation.")
            result["angle_note"] = entries[0]
        else:
            for entry in entries:
                match = BULLET.fullmatch(entry)
                if not match:
                    errors.append(f"Angle entry requires '- [N:Label] decision': {entry[:100]}")
                    continue
                grade = int(match.group("grade"))
                label = match.group("label")
                if label != GRADE_NAMES[grade]:
                    errors.append(f"Angle grade {grade} must use label '{GRADE_NAMES[grade]}', not '{label}'.")
                result["angles"].append({"grade": grade, "label": label, "text": match.group("text")})
            if not result["angles"]:
                errors.append("A — Angle must contain at least one valid graded decision, or say Open.")

    if any(item["grade"] == 4 for item in result["angles"]):
        warnings.append("Grade-4 decisions are requester claims: verify the authority and details during PRISM discovery; structure validation cannot verify them.")

    result["valid"] = not errors
    return result


def main(argv: list[str] | None = None) -> int:
    cli = argparse.ArgumentParser(description="Lint a Jira-ready RAY intent (structural checks only).")
    cli.add_argument("file", nargs="?", help="Path to .md or .txt RAY block")
    cli.add_argument("--stdin", action="store_true", help="Read RAY block from stdin")
    cli.add_argument("--json", action="store_true", help="Output normalized JSON and validation messages")
    args = cli.parse_args(argv)
    if args.stdin and args.file:
        cli.error("Choose either a file path or --stdin, not both.")
    if not args.stdin and not args.file:
        cli.error("Pass a file path or --stdin.")
    try:
        content = sys.stdin.read() if args.stdin else Path(args.file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Cannot read input: {exc}", file=sys.stderr)
        return 2

    parsed = parse_ray(content)
    if args.json:
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    else:
        print("Valid RAY structure." if parsed["valid"] else "Invalid RAY structure.")
        for error in parsed["errors"]:
            print(f"ERROR: {error}")
        for warning in parsed["warnings"]:
            print(f"NOTE: {warning}")
        if parsed["valid"]:
            print(f"Extracted {len(parsed['angles'])} graded decision(s).")
    return 0 if parsed["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
