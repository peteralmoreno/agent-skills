"""Unit tests for the optional RAY block shape parser."""
import sys
import json
import re
import subprocess
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lint_ray import parse_ray  # noqa: E402


class TestParseRay(unittest.TestCase):
    def test_all_grades_preserve_commitment(self):
        text = "Intent\nR — Result: Teams can retry.\nA — Angle:\n"
        for grade, label in enumerate(["Consider", "Prefer", "Strong", "Required"], 1):
            text += f"- [{grade}:{label}] Direction {grade}.\n"
        parsed = parse_ray(text + "Y — Why: Retries are slow.\n")
        self.assertTrue(parsed["valid"], parsed["errors"])
        self.assertEqual([1, 2, 3, 4], [a["grade"] for a in parsed["angles"]])

    def test_open_requires_a_word_and_cannot_mix_decisions(self):
        for angle in ["OpenSearch", "Open\n- [2:Prefer] Kafka.", ""]:
            with self.subTest(angle=angle):
                self.assertFalse(parse_ray(
                    f"Intent\nR — Result: Teams can retry.\nA — Angle: {angle}\nY — Why: Slow retries."
                )["valid"])

    def test_documented_intent_blocks(self):
        root = Path(__file__).resolve().parents[1]
        for file in root.rglob("*.md"):
            for block in re.findall(r"```text\n(.*?)```", file.read_text(encoding="utf-8"), re.S):
                if block.startswith("Intent\n"):
                    with self.subTest(file=file.name, block=block):
                        parsed = parse_ray(block)
                        self.assertTrue(parsed["valid"], parsed["errors"])

    def test_cli_json_and_invalid_exit_status(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "lint_ray.py"
        valid = "Intent\nR — Result: Teams can retry.\nA — Angle: Open\nY — Why: Slow retries."
        for text, status in [(valid, 0), ("Not an intent", 1)]:
            with self.subTest(status=status):
                run = subprocess.run([sys.executable, str(script), "--stdin", "--json"],
                                     input=text, text=True, capture_output=True)
                self.assertEqual(status, run.returncode, run.stderr)
                self.assertEqual(status == 0, json.loads(run.stdout)["valid"])

    def test_graded_block(self):
        text = """Intent
R — Result: Integrations can consume domain events.
A — Angle:
- [3:Strong] Dedicated Kafka topic, but allow alternatives.
- [4:Required] Preserve existing consumers (contract owner to confirm).
Y — Why: Today integrations require excessive coordination.
"""
        parsed = parse_ray(text)
        self.assertTrue(parsed["valid"], parsed["errors"])
        self.assertEqual([3, 4], [x["grade"] for x in parsed["angles"]])
        self.assertEqual("ray/v1", parsed["format"])
        self.assertTrue(parsed["warnings"])

    def test_open_block(self):
        text = """## Intent
R — Result: Teams can find orphaned workflows.
A — Angle: Open — no early decisions yet.
Y — Why: Ownership becomes unclear during reorgs.
"""
        parsed = parse_ray(text)
        self.assertTrue(parsed["valid"], parsed["errors"])
        self.assertEqual([], parsed["angles"])
        self.assertTrue(parsed["angle_note"].startswith("Open"))

    def test_invalid_grade(self):
        text = """Intent
R — Result: Teams can retry.
A — Angle:
- [5:Mandatory] Redis.
Y — Why: It takes too long.
"""
        parsed = parse_ray(text)
        self.assertFalse(parsed["valid"])
        self.assertTrue(any("Angle entry" in e for e in parsed["errors"]))

    def test_mismatched_label(self):
        text = """Intent
R — Request: Teams can retry.
A — Angle: Open — no early decisions yet.
Y — Why: Retries are slow.
"""
        parsed = parse_ray(text)
        self.assertFalse(parsed["valid"])
        self.assertTrue(any("expected label" in e for e in parsed["errors"]))

    def test_order(self):
        text = """Intent
Y — Why: Slowness.
R — Result: Speed.
A — Angle: Open — no early decisions yet.
"""
        self.assertFalse(parse_ray(text)["valid"])

    def test_duplicate(self):
        text = """Intent
R — Result: Fast.
R — Result: Reliable.
A — Angle: Open — no early decisions yet.
Y — Why: Slowness.
"""
        self.assertTrue(any("duplicate" in e for e in parse_ray(text)["errors"]))

    def test_missing_why(self):
        text = """Intent
R — Result: Fast.
A — Angle: Open — no early decisions yet.
"""
        self.assertFalse(parse_ray(text)["valid"])

    def test_next_heading_stops_parse(self):
        text = """Intent
R — Result: Fast.
A — Angle: Open — no early decisions yet.
Y — Why: Slowness.

## Context
Lots of extra Jira text not part of the intent.
"""
        parsed = parse_ray(text)
        self.assertTrue(parsed["valid"])
        self.assertEqual("Slowness.", parsed["why"])

    def test_no_header(self):
        text = """This is my ticket.
R — Result: Something.
A — Angle: Open — no early decisions yet.
Y — Why: Something else.
"""
        self.assertFalse(parse_ray(text)["valid"])

    def test_bad_name_in_grade(self):
        text = """Intent
R — Result: Fast.
A — Angle:
- [3:Required] Kafka.
Y — Why: Slow.
"""
        self.assertFalse(parse_ray(text)["valid"])


if __name__ == "__main__":
    unittest.main()
