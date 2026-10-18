"""CLI regression tests for optional Playbook Bank source, history, and memory."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pb.py"


class BankCLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        self.bank = self.work / "bank"

    def cli(self, *args, expected=0):
        r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                           text=True, capture_output=True)
        if expected == 0:
            self.assertEqual(r.returncode, 0, f"{args}: {r.stderr}\n{r.stdout}")
        else:
            self.assertNotEqual(r.returncode, 0, f"{args}: unexpected success")
        return r

    def create_active(self, slug="triage"):
        self.cli("bank", "init", self.bank)
        self.cli("new", slug, "--bank", self.bank,
                 "--description", "Investigate a reproducible failure")
        path = self.bank / "playbooks" / slug / "PLAYBOOK.md"
        path.write_text(path.read_text(encoding="utf-8")
                        .replace("status: draft", "status: active")
                        .replace("TODO", "Confirmed"), encoding="utf-8")
        self.cli("validate", "--bank", self.bank)
        return path

    def prepare(self, slug="triage"):
        inp = self.work / "inputs.json"
        inp.write_text('{"service":"gateway"}', encoding="utf-8")
        self.cli("prepare", slug, "--bank", self.bank, "--inputs", inp)
        return sorted((self.bank / ".state" / "runs" / slug).glob("*.json"))[-1]

    def finish(self, record):
        proof = self.work / "proof.json"
        proof.write_text(json.dumps({"checks": [
            {"id": "P1", "status": "pass", "evidence": "Validated report"},
            {"id": "P2", "status": "pass", "evidence": "No unauthorized writes observed"},
        ]}), encoding="utf-8")
        self.cli("finish", record, "--proof", proof, "--result", "passed")

    def test_bank_creation_and_no_implicit_fallback(self):
        self.cli("bank", "init", self.bank)
        self.cli("bank", "init", self.bank)  # safe repeat
        self.assertTrue((self.bank / "bank.json").exists())
        self.assertEqual((self.bank / ".gitignore").read_text(), ".state/\n")
        self.assertTrue((self.bank / ".state" / "memory").is_dir())
        self.cli("list", "--bank", self.bank)
        self.cli("list", "--bank", self.work / "missing", expected=1)
        stranger = self.work / "unrelated"
        stranger.mkdir()
        (stranger / "important.txt").write_text("preserve")
        self.cli("bank", "init", stranger, expected=1)
        self.assertFalse((stranger / "bank.json").exists())
        self.assertEqual((stranger / "important.txt").read_text(), "preserve")

    def test_scaffolding_memory_review_and_run_history(self):
        self.create_active()
        one = self.prepare()
        run_id = json.loads(one.read_text())["run_id"]
        # A source run must be complete before attaching it to a note.
        self.cli("memory", "add", "triage", "--bank", self.bank,
                 "--source-run", run_id, "--note", "Check database pool limits.",
                 expected=1)
        self.finish(one)
        output = self.cli("memory", "add", "triage", "--bank", self.bank,
                          "--source-run", run_id,
                          "--note", "Check database pool limits.").stdout
        proposed = json.loads(output.split("\nProposed only;")[0])
        self.assertEqual(proposed["status"], "proposed")
        second = self.prepare()
        state = json.loads(second.read_text())
        self.assertEqual(state["memory_context"]["items"], [])
        self.cli("memory", "approve", "triage", "--bank", self.bank,
                 "--id", proposed["id"], "--reviewer", "a human")
        third = self.prepare()
        state = json.loads(third.read_text())
        self.assertEqual(state["memory_context"]["trust"], "advisory_untrusted")
        self.assertEqual(len(state["memory_context"]["items"]), 1)
        self.assertEqual(state["memory_context"]["items"][0]["note"],
                         "Check database pool limits.")
        history = json.loads(self.cli("history", "triage", "--bank", self.bank,
                                     "--json").stdout)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["state"], "prepared")
        self.assertEqual(history[-1]["result"], "passed")
        approved = json.loads(self.cli("memory", "list", "triage",
                                      "--bank", self.bank).stdout)
        self.assertEqual(len(approved), 1)

    def test_bank_and_project_modes_are_separate(self):
        self.create_active()
        project = self.work / "project"
        self.cli("init", "--root", project)
        self.cli("list", "--root", project)
        self.assertIn("(no playbooks)", self.cli("list", "--root", project).stdout)
        self.assertIn("triage", self.cli("list", "--bank", self.bank).stdout)
        self.cli("list", "--bank", self.bank, "--root", project, expected=1)

    def test_reject_invalid_memory_or_source_changes(self):
        path = self.create_active()
        run = self.prepare()
        self.cli("memory", "add", "triage", "--bank", self.bank,
                 "--source-run", "../../foo", "--note", "bad", expected=1)
        path.write_text(path.read_text() + "\nChanged during execution.\n")
        proof = self.work / "proof.json"
        proof.write_text(json.dumps({"checks": [
            {"id": key, "status": "pass", "evidence": "observed"}
            for key in ("P1", "P2")
        ]}))
        response = self.cli("finish", run, "--proof", proof,
                            "--result", "passed", expected=1)
        self.assertIn("Playbook changed", response.stderr)


if __name__ == "__main__":
    unittest.main()
