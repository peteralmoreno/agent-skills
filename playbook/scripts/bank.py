"""Optional persistent bank for independently maintained playbooks.

Playbooks may be tracked in Git; raw executions and notes are private local state.
No network access and no automatic extraction of memories from run outputs.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import uuid

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RUN_ID = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{8}$")
MEMORY_ID = re.compile(r"^m-[0-9a-f]{12}$")


class BankError(Exception):
    pass


def iso_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def safe_name(name):
    if not SLUG.fullmatch(name):
        raise BankError("Playbook name must be a lowercase slug")
    return name


def bank_dir(path):
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise BankError(f"Playbook bank does not exist: {root}; run 'bank init' first")
    marker = root / "bank.json"
    try:
        metadata = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BankError(f"Not a valid Playbook Bank (missing or invalid bank.json): {root}") from exc
    if not isinstance(metadata, dict) or metadata.get("schema") != "playbook-bank/v1":
        raise BankError(f"Unsupported Playbook Bank marker: {marker}")
    return root


def create_bank(path):
    root = Path(path).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise BankError(f"Cannot create bank inside a file: {root}")
    root.mkdir(parents=True, exist_ok=True)
    marker = root / "bank.json"
    if marker.exists():
        bank_dir(root)
    else:
        # Refuse to quietly take ownership of a pre-existing, non-bank folder.
        if any(root.iterdir()):
            raise BankError(f"Directory is nonempty and has no bank.json: {root}")
        metadata = {"schema": "playbook-bank/v1", "name": root.name,
                    "created_at": iso_now()}
        marker.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    catalog = root / "playbooks"
    catalog.mkdir(exist_ok=True)
    guide = catalog / "README.md"
    if not guide.exists():
        guide.write_text("# Playbook Bank\n\nEach subfolder contains a standalone PLAYBOOK.md.\n"
                         "Run records and curated memories are stored under private .state/.\n", encoding="utf-8")
    ignore = root / ".gitignore"
    if not ignore.exists():
        ignore.write_text(".state/\n", encoding="utf-8")
    elif ".state/" not in ignore.read_text(encoding="utf-8").splitlines():
        # Don't silently rewrite a user's existing ignores.
        print("WARNING: add .state/ to your bank .gitignore before committing", file=__import__('sys').stderr)
    (root / ".state" / "runs").mkdir(parents=True, exist_ok=True)
    (root / ".state" / "memory").mkdir(parents=True, exist_ok=True)
    return root


def runs_dir(root, slug):
    return bank_dir(root) / ".state" / "runs" / safe_name(slug)


def load_history(root, slug, limit=20):
    if limit < 1 or limit > 500:
        raise BankError("History limit must be from 1 to 500")
    folder = runs_dir(root, slug)
    records = []
    for file in sorted(folder.glob("*.json"), reverse=True)[:limit]:
        try:
            record = json.loads(file.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if record.get("schema") == "playbook-run/v1" and record.get("playbook", {}).get("name") == slug:
            records.append({"run_id": record.get("run_id"),
                            "date": record.get("created_at"),
                            "state": record.get("state"), "result": record.get("result"),
                            "version": record.get("playbook", {}).get("version"),
                            "file": str(file)})
    return records


def memory_file(root, slug):
    return bank_dir(root) / ".state" / "memory" / (safe_name(slug) + ".json")


def read_memory(root, slug):
    file = memory_file(root, slug)
    if not file.exists():
        return []
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BankError(f"Invalid memory file: {file}") from exc
    if not isinstance(data, dict) or data.get("schema") != "playbook-memory/v1" or not isinstance(data.get("items"), list):
        raise BankError(f"Unsupported memory record: {file}")
    return data["items"]


def save_memory(root, slug, items):
    file = memory_file(root, slug)
    file.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps({"schema": "playbook-memory/v1", "playbook": slug, "items": items}, indent=2) + "\n"
    # Avoid partially written memory if the process crashes.
    temporary = file.with_name(file.name + "." + uuid.uuid4().hex[:8] + ".tmp")
    try:
        temporary.write_text(data, encoding="utf-8")
        os.replace(temporary, file)
    finally:
        if temporary.exists():
            temporary.unlink()
    return file


def add_memory(root, slug, note, run_id=None):
    safe_name(slug)
    if not isinstance(note, str) or not note.strip() or len(note) > 2000:
        raise BankError("Memory note must be 1-2000 characters")
    if not (bank_dir(root) / "playbooks" / slug / "PLAYBOOK.md").is_file():
        raise BankError("Memory requires a playbook that exists in this bank")
    if run_id:
        if not RUN_ID.fullmatch(run_id):
            raise BankError("Invalid source run ID")
        file = runs_dir(root, slug) / (run_id + ".json")
        try:
            record = json.loads(file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise BankError(f"Source run not found: {run_id}") from exc
        if (record.get("run_id") != run_id or record.get("state") != "completed"
                or record.get("playbook", {}).get("name") != slug):
            raise BankError("Source run must be a completed run for this playbook")
    items = read_memory(root, slug)
    item = {"id": "m-" + uuid.uuid4().hex[:12], "status": "proposed",
            "note": note.strip(), "source_run": run_id, "created_at": iso_now(),
            "reviewed_at": None, "reviewer": None}
    items.append(item)
    save_memory(root, slug, items)
    return item


def approve_memory(root, slug, item_id, reviewer):
    if not MEMORY_ID.fullmatch(item_id):
        raise BankError("Invalid memory ID")
    if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 120:
        raise BankError("Name a reviewer; recorded reviewer is self-attested")
    items = read_memory(root, slug)
    found = next((item for item in items if item.get("id") == item_id), None)
    if not found:
        raise BankError(f"Unknown memory ID for {slug}: {item_id}")
    if found.get("status") != "proposed":
        raise BankError(f"Memory already has status: {found.get('status')}")
    found.update(status="approved", reviewer=reviewer.strip(), reviewed_at=iso_now())
    save_memory(root, slug, items)
    return found
