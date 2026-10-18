#!/usr/bin/env python3
"""Portable playbook library utility. Python 3.9+, standard library only.

This tool scaffolds and validates files and records reported evidence.
It does NOT run an AI agent, call tools, or independently verify claims.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

import bank as banklib

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_ROOT / "assets" / "playbook-template.md"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEADINGS = [
    "Goal", "When to use", "Inputs", "Procedure",
    "Tools and permissions", "Proof of completion", "Output",
    "Failure and recovery", "Learning",
]
FRONT_KEYS = ("name", "description", "version", "status")
STATUSES = {"draft", "active", "deprecated"}


class PlaybookError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def library(root):
    return Path(root).expanduser().resolve() / "playbooks"


def safe_slug(value):
    if not SLUG.fullmatch(value):
        raise PlaybookError("Name must be a lowercase slug, e.g. investigate-api")
    return value


def selected_root(args):
    """Choose an explicit, initialized bank or the legacy project-local location."""
    if getattr(args, "bank", None):
        return banklib.bank_dir(args.bank)
    return Path(getattr(args, "root", None) or ".").expanduser().resolve()


def add_source_args(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--root", help="Project directory; playbooks live in PROJECT/playbooks")
    group.add_argument("--bank", help="Previously initialized bank directory (outside agent Skills)")


def doc_path(root, slug):
    return library(root) / safe_slug(slug) / "PLAYBOOK.md"


def read_document(path):
    if not path.is_file():
        raise PlaybookError(f"No playbook found: {path}")
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", text, re.S)
    if not match:
        raise PlaybookError(f"{path}: missing YAML-style frontmatter")
    meta = {}
    for line in match.group(1).splitlines():
        part = re.match(r"^([a-z][a-z0-9_-]*):\s*(.*?)\s*$", line)
        if part:
            meta[part.group(1)] = part.group(2).strip().strip("'\"")
    return text, meta


def proof_ids(text):
    return re.findall(r"^\s*-\s*\*\*(P[1-9][0-9]*):\*\*", text, re.M)


def validate_file(path):
    errors, warnings = [], []
    try:
        text, meta = read_document(path)
    except (PlaybookError, UnicodeDecodeError) as exc:
        return [str(exc)], []
    for field in FRONT_KEYS:
        if not meta.get(field):
            errors.append(f"missing frontmatter: {field}")
    if meta.get("name") != path.parent.name:
        errors.append("frontmatter name must match parent directory")
    if meta.get("status") not in STATUSES:
        errors.append("status must be draft, active, or deprecated")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", meta.get("version", "")):
        errors.append("version must be major.minor.patch")
    for heading in HEADINGS:
        if not re.search(r"^## " + re.escape(heading) + r"\s*$", text, re.M):
            errors.append(f"missing section: {heading}")
    ids = proof_ids(text)
    if not ids:
        errors.append("missing enumerated proof checks (P1, P2, ...)")
    if len(ids) != len(set(ids)):
        errors.append("duplicate proof check IDs")
    if "TODO" in text:
        if meta.get("status") == "active":
            errors.append("active playbook contains TODO placeholders")
        else:
            warnings.append("draft contains TODO placeholders")
    return errors, warnings


def init_cmd(args):
    target = library(args.root)
    target.mkdir(parents=True, exist_ok=True)
    catalog = target / "README.md"
    if not catalog.exists():
        catalog.write_text(
            "# Playbook Library\n\n"
            "One directory per task, with a PLAYBOOK.md containing an "
            "explicit contract and proof checks.\n\n"
            "Use the playbook Skill to create, find, execute, and improve procedures.\n"
            "Local execution records are under .runs/ and are not published by default.\n",
            encoding="utf-8",
        )
    ignore = target / ".gitignore"
    if not ignore.exists():
        ignore.write_text(".runs/\n", encoding="utf-8")
    elif ".runs/" not in ignore.read_text(encoding="utf-8").splitlines():
        print("WARNING: existing .gitignore does not exclude .runs/; add it manually", file=sys.stderr)
    (target / ".runs").mkdir(exist_ok=True)
    print(f"Initialized (preserved existing files): {target}")


def new_cmd(args):
    safe_slug(args.name)
    target = doc_path(selected_root(args), args.name)
    if target.exists() or target.parent.exists():
        raise PlaybookError(f"Refusing to overwrite existing path: {target.parent}")
    if args.description and ("\n" in args.description or "\r" in args.description):
        raise PlaybookError("Description must be one line")
    target.parent.mkdir(parents=True, exist_ok=False)
    body = TEMPLATE.read_text(encoding="utf-8")
    body = body.replace("REPLACE-SLUG", args.name)
    body = body.replace("REPLACE-TITLE", args.name.replace("-", " ").title())
    if args.description:
        body = body.replace("TODO — one sentence stating the job and when to use it.", args.description)
    target.write_text(body, encoding="utf-8")
    print(f"Created draft: {target}")
    print("Edit TODO fields, review, trial, then promote to active.")


def iter_docs(root, name=None):
    if name:
        return [doc_path(root, name)]
    base = library(root)
    if not base.is_dir():
        raise PlaybookError(f"No library at {base}; run init first")
    return sorted(base.glob("*/PLAYBOOK.md"))


def list_cmd(args):
    paths = iter_docs(selected_root(args))
    if not paths:
        print("(no playbooks)")
    for path in paths:
        try:
            _, m = read_document(path)
            print(f"{path.parent.name}\t{m.get('status', '?')}\t"
                  f"{m.get('version', '?')}\t{m.get('description', '')}")
        except PlaybookError as exc:
            print(f"INVALID {path}: {exc}")
    print(f"{len(paths)} playbook(s)")


def validate_cmd(args):
    paths = iter_docs(selected_root(args), args.name)
    if not paths:
        raise PlaybookError("No playbooks to validate")
    failed = 0
    for path in paths:
        errors, warnings = validate_file(path)
        print(f"{'FAIL' if errors else 'OK'} {path}")
        for item in errors:
            print(f"  ERROR: {item}")
        for item in warnings:
            print(f"  WARNING: {item}")
        failed += bool(errors)
    if failed:
        raise PlaybookError(f"{failed} playbook(s) failed validation")


def prepare_cmd(args):
    path = doc_path(selected_root(args), args.name)
    errors, warnings = validate_file(path)
    if errors:
        raise PlaybookError("Invalid playbook: " + "; ".join(errors))
    text, meta = read_document(path)
    if meta.get("status") != "active" and not args.allow_draft:
        raise PlaybookError("Only active playbooks can run; use --allow-draft for a supervised trial")
    input_path = Path(args.inputs).expanduser()
    try:
        inputs = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PlaybookError(f"Inputs must be a readable JSON object: {exc}") from exc
    if not isinstance(inputs, dict):
        raise PlaybookError("Inputs must be a JSON object")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    recalled = []
    if getattr(args, "bank", None):
        recalled = [{"id": item["id"], "note": item["note"]}
                    for item in banklib.read_memory(args.bank, args.name)
                    if item.get("status") == "approved"]
    record = {
        "schema": "playbook-run/v1",
        "run_id": run_id,
        "state": "prepared",
        "result": None,
        "verification": "none",
        "playbook": {
            "name": args.name,
            "version": meta["version"],
            "source": str(path.resolve()),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "proof_ids": proof_ids(text),
        },
        "inputs": inputs,
        "memory_context": {"trust": "advisory_untrusted", "items": recalled},
        "proof": [],
        "created_at": now(),
        "completed_at": None,
    }
    folder = (banklib.runs_dir(args.bank, args.name) if getattr(args, "bank", None)
              else library(selected_root(args)) / ".runs")
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / (run_id + ".json")
    with output.open("x", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    print(f"Prepared run: {output}")
    print(f"Read and follow: {path}")
    print("This command did not execute the playbook or verify any evidence.")


def finish_cmd(args):
    record_path = Path(args.record).expanduser().resolve()
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
        proof = json.loads(Path(args.proof).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PlaybookError(f"Record and proof must be readable JSON: {exc}") from exc
    if record.get("schema") != "playbook-run/v1" or record.get("state") != "prepared":
        raise PlaybookError("Expected a prepared playbook-run/v1 record")
    if not isinstance(proof, dict) or not isinstance(proof.get("checks"), list):
        raise PlaybookError("Proof must be an object with a checks array")
    checks = proof["checks"]
    expected = set(record["playbook"]["proof_ids"])
    seen = set()
    for check in checks:
        if not isinstance(check, dict):
            raise PlaybookError("Every proof check must be an object")
        key = check.get("id")
        if key not in expected:
            raise PlaybookError(f"Unknown proof ID: {key!r}")
        if key in seen:
            raise PlaybookError(f"Duplicate proof ID: {key}")
        seen.add(key)
        if check.get("status") not in ("pass", "fail", "blocked"):
            raise PlaybookError(f"{key}: status must be pass, fail or blocked")
        if not isinstance(check.get("evidence"), str) or not check["evidence"].strip():
            raise PlaybookError(f"{key}: provide a non-empty evidence statement")
    if args.result == "passed":
        missing = expected - seen
        if missing:
            raise PlaybookError("Cannot report passed: missing " + ", ".join(sorted(missing)))
        if any(check["status"] != "pass" for check in checks):
            raise PlaybookError("Cannot report passed: one or more proof checks did not pass")
    if args.result == "failed" and not any(c.get("status") == "fail" for c in checks):
        raise PlaybookError("Failed result requires at least one failed proof check")
    source = Path(record["playbook"]["source"])
    if args.result == "passed":
        try:
            actual = hashlib.sha256(source.read_bytes()).hexdigest()
        except OSError as exc:
            raise PlaybookError(f"Cannot confirm pinned playbook source: {exc}") from exc
        if actual != record["playbook"]["sha256"]:
            raise PlaybookError("Playbook changed since preparation; start a new run for the new version")
    record["state"] = "completed"
    record["result"] = args.result
    record["verification"] = "self_reported_structure_checked"
    record["proof"] = checks
    record["notes"] = proof.get("notes", "")
    record["completed_at"] = now()
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {args.result}: {record_path}")
    print("Evidence is self-reported; authenticity and task success were NOT independently verified.")



def bank_cmd(args):
    if args.bank_action == "init":
        root = banklib.create_bank(args.path)
        print(f"Playbook Bank ready: {root}")
        print("Playbooks are in playbooks/; private history and memory are in .state/.")
    elif args.bank_action == "info":
        root = banklib.bank_dir(args.path)
        paths = sorted((root / "playbooks").glob("*/PLAYBOOK.md"))
        print(json.dumps({"bank": str(root), "schema": "playbook-bank/v1",
                          "playbooks": len(paths),
                          "local_state": str(root / ".state")}, indent=2))


def history_cmd(args):
    entries = banklib.load_history(args.bank, args.name, args.limit)
    if args.json:
        print(json.dumps(entries, indent=2))
    else:
        for x in entries:
            print(f"{x['run_id']}  {x['result'] or x['state']}  v{x['version']}  {x['date']}")
        if not entries:
            print("(no runs yet)")


def memory_cmd(args):
    if args.memory_action == "list":
        items = banklib.read_memory(args.bank, args.name)
        if not args.all:
            items = [x for x in items if x.get("status") == "approved"]
        print(json.dumps(items, indent=2))
    elif args.memory_action == "add":
        item = banklib.add_memory(args.bank, args.name, args.note, args.source_run)
        print(json.dumps(item, indent=2))
        print("Proposed only; explicit review required before use as approved context.")
    elif args.memory_action == "approve":
        item = banklib.approve_memory(args.bank, args.name, args.id, args.reviewer)
        print(json.dumps(item, indent=2))
        print("Reviewer identity is self-attested. This does not rewrite the playbook.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("init", help="Create a playbook directory without overwriting existing files")
    p.add_argument("--root", default=".")
    p.set_defaults(fn=init_cmd)
    p = commands.add_parser("new", help="Create a draft playbook from the bundled template")
    p.add_argument("name")
    add_source_args(p)
    p.add_argument("--description")
    p.set_defaults(fn=new_cmd)
    p = commands.add_parser("list", help="Show available playbooks")
    add_source_args(p)
    p.set_defaults(fn=list_cmd)
    p = commands.add_parser("validate", help="Structural validation, not correctness verification")
    p.add_argument("name", nargs="?")
    add_source_args(p)
    p.set_defaults(fn=validate_cmd)
    p = commands.add_parser("prepare", help="Pin a playbook and prepare a run record; no AI execution")
    p.add_argument("name")
    add_source_args(p)
    p.add_argument("--inputs", required=True)
    p.add_argument("--allow-draft", action="store_true")
    p.set_defaults(fn=prepare_cmd)
    p = commands.add_parser("bank", help="Manage a user-chosen Playbook Bank")
    sub = p.add_subparsers(dest="bank_action", required=True)
    b = sub.add_parser("init", help="Create a bank with a playbook catalog and private state")
    b.add_argument("path")
    b.set_defaults(fn=bank_cmd)
    b = sub.add_parser("info", help="Inspect an existing bank")
    b.add_argument("path")
    b.set_defaults(fn=bank_cmd)
    p = commands.add_parser("history", help="List saved execution records in a bank")
    p.add_argument("name")
    p.add_argument("--bank", required=True)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=history_cmd)
    p = commands.add_parser("memory", help="Review and curate persistent bank memory")
    sub = p.add_subparsers(dest="memory_action", required=True)
    m = sub.add_parser("list", help="Show approved entries (or --all)")
    m.add_argument("name")
    m.add_argument("--bank", required=True)
    m.add_argument("--all", action="store_true")
    m.set_defaults(fn=memory_cmd)
    m = sub.add_parser("add", help="Propose a human-readable memory entry")
    m.add_argument("name")
    m.add_argument("--bank", required=True)
    m.add_argument("--note", required=True)
    m.add_argument("--source-run", help="Optional completed run ID in the same bank")
    m.set_defaults(fn=memory_cmd)
    m = sub.add_parser("approve", help="Explicitly approve a memory entry for future context")
    m.add_argument("name")
    m.add_argument("--bank", required=True)
    m.add_argument("--id", required=True)
    m.add_argument("--reviewer", required=True)
    m.set_defaults(fn=memory_cmd)
    p = commands.add_parser("finish", help="Store self-reported proof and completion result")
    p.add_argument("record")
    p.add_argument("--proof", required=True)
    p.add_argument("--result", choices=["passed", "failed", "blocked"], required=True)
    p.set_defaults(fn=finish_cmd)
    args = parser.parse_args(argv)
    try:
        args.fn(args)
    except (PlaybookError, banklib.BankError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
