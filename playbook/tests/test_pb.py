"""Offline tests for the standalone playbook utility."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pb.py"


class PlaybookCLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def call(self, *args, ok=True):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--root", str(self.root)],
            text=True, capture_output=True,
        )
        if ok and r.returncode != 0:
            self.fail(f"CLI error: {r.stderr}\nstdout: {r.stdout}")
        return r

    def setup_draft(self):
        self.call("init")
        self.call("new", "incident-triage", "--description", "Investigate a failing API")
        return self.root / "playbooks" / "incident-triage" / "PLAYBOOK.md"

    def activate(self):
        doc = self.setup_draft()
        content = doc.read_text(encoding="utf-8")
        content = content.replace("status: draft", "status: active")
        content = content.replace("TODO", "To be confirmed")
        doc.write_text(content, encoding="utf-8")
        return doc

    def test_init_is_idempotent(self):
        self.call("init")
        note = self.root / "playbooks" / "README.md"
        note.write_text("Existing owner notes\n", encoding="utf-8")
        self.call("init")
        self.assertEqual(note.read_text(encoding="utf-8"), "Existing owner notes\n")
        self.assertEqual((self.root / "playbooks" / ".gitignore").read_text(), ".runs/\n")

    def test_new_list_validate_and_refuse_overwrite(self):
        self.setup_draft()
        self.assertIn("incident-triage", self.call("list").stdout)
        result = self.call("validate")
        self.assertIn("WARNING", result.stdout)
        duplicate = self.call("new", "incident-triage", ok=False)
        self.assertNotEqual(duplicate.returncode, 0)

    def test_draft_requires_opt_in_before_prepare(self):
        self.setup_draft()
        inp = self.root / "input.json"
        inp.write_text('{"service":"api"}', encoding="utf-8")
        result = self.call("prepare", "incident-triage", "--inputs", str(inp), ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Only active", result.stderr)
        self.call("prepare", "incident-triage", "--inputs", str(inp), "--allow-draft")

    def test_prepare_and_finish_validate_reported_proof(self):
        self.activate()
        self.call("validate")
        inp = self.root / "input.json"
        inp.write_text('{"service":"api"}', encoding="utf-8")
        self.call("prepare", "incident-triage", "--inputs", str(inp))
        record_path = next((self.root / "playbooks" / ".runs").glob("*.json"))
        record = json.loads(record_path.read_text())
        self.assertEqual(record["playbook"]["proof_ids"], ["P1", "P2"])
        proof_path = self.root / "proof.json"
        proof_path.write_text(json.dumps({
            "checks": [{"id":"P1", "status":"pass", "evidence":"report with timestamps"}]
        }))
        missing = subprocess.run(
            [sys.executable, str(SCRIPT), "finish", str(record_path), "--proof",
             str(proof_path), "--result", "passed"],
            text=True, capture_output=True,
        )
        self.assertNotEqual(missing.returncode, 0)
        proof_path.write_text(json.dumps({
            "checks": [
                {"id":"P1", "status":"pass", "evidence":"report with timestamps"},
                {"id":"P2", "status":"pass", "evidence":"manual review recorded"},
            ]
        }), encoding="utf-8")
        success = subprocess.run(
            [sys.executable, str(SCRIPT), "finish", str(record_path), "--proof",
             str(proof_path), "--result", "passed"],
            text=True, capture_output=True,
        )
        self.assertEqual(success.returncode, 0, success.stderr)
        final = json.loads(record_path.read_text())
        self.assertEqual(final["result"], "passed")
        self.assertEqual(final["verification"], "self_reported_structure_checked")

    def test_changed_source_blocks_passed_run(self):
        doc = self.activate()
        inp = self.root / "input.json"
        inp.write_text("{}", encoding="utf-8")
        self.call("prepare", "incident-triage", "--inputs", str(inp))
        record_path = next((self.root / "playbooks" / ".runs").glob("*.json"))
        doc.write_text(doc.read_text() + "\nChanged after run preparation.\n")
        proof_path = self.root / "proof.json"
        proof_path.write_text(json.dumps({
            "checks":[{"id": key, "status":"pass", "evidence":"checked"}
                      for key in ("P1", "P2")]
        }))
        failed = subprocess.run(
            [sys.executable, str(SCRIPT), "finish", str(record_path), "--proof",
             str(proof_path), "--result", "passed"],
            text=True, capture_output=True,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("Playbook changed", failed.stderr)


if __name__ == "__main__":
    unittest.main()
