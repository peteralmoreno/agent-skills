"""Offline unit tests for portable DriftMaps authoring utilities."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "driftmaps.py"
SAMPLE = SKILL / "examples" / "burrito-cannon"

spec = importlib.util.spec_from_file_location("driftmaps_core", SCRIPT)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


class DriftMapsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.map_dir = self.root / "maps" / "burrito-cannon"
        shutil.copytree(SAMPLE, self.map_dir)
        self.source = self.map_dir / "MAP.md"

    def test_example_graph_and_contracts(self):
        model = core.require_valid(self.source)
        self.assertEqual(model["name"], "burrito-cannon")
        self.assertEqual(len(model["edges"]), 10)
        self.assertEqual(len(model["nodes"]), 8)  # five real + three controls
        self.assertEqual(model["max_transitions"], 12)
        meta, _ = core.frontmatter(self.map_dir / "nodes" / "locate.md")
        self.assertIn("isMember", meta["produces"])

    def test_cannot_invent_a_missing_node(self):
        (self.map_dir / "nodes" / "blast.md").unlink()
        model = core.analyze(self.source)
        self.assertTrue(any("missing node file" in issue for issue in model["errors"]))
        with self.assertRaises(core.MapError):
            core.require_valid(self.source)

    def test_unregistered_node_is_not_allowed(self):
        path = self.map_dir / "nodes" / "imagined.md"
        path.write_text("---\nrequires: []\nproduces: []\n---\n# Invented\n")
        self.assertTrue(any("unregistered node" in x for x in
                            core.analyze(self.source)["errors"]))

    def test_rejects_ambiguous_mermaid_branch_labels(self):
        source = self.source.read_text()
        source = source.replace("|missing order|", "|ready|")
        self.source.write_text(source)
        self.assertTrue(any("unique, nonempty branch labels" in x for x in
                            core.analyze(self.source)["errors"]))

    def test_rejects_advanced_unknown_graph_syntax(self):
        source = self.source.read_text()
        source = source.replace(
            'setup["Setup"] -->|ready| prepare["Prepare"]',
            "setup --> prepare --> locate"
        )
        self.source.write_text(source)
        with self.assertRaisesRegex(core.MapError, "One -->"):
            core.analyze(self.source)

    def test_new_scaffold_is_valid_and_will_not_overwrite(self):
        fresh = self.root / "fresh"
        core.init(type("Args", (), {"root": str(fresh)})())
        core.create(type("Args", (), {"root": str(fresh), "name": "my-map"})())
        created = fresh / "maps" / "my-map" / "MAP.md"
        model = core.require_valid(created)
        self.assertEqual(model["status"], "draft")
        self.assertTrue((fresh / ".driftmaps" / ".gitignore").is_file())
        with self.assertRaises(core.MapError):
            core.create(type("Args", (), {"root": str(fresh), "name": "my-map"})())

    def test_start_prepares_trail_but_does_not_execute_nodes(self):
        inp = self.root / "input.yaml"
        inp.write_text("order_ref: ORD-42\nisMember: false\n", encoding="utf-8")
        core.start(type("Args", (), {
            "map": str(self.source), "root": str(self.root),
            "input_file": str(inp), "allow_draft": False
        })())
        runs = list((self.root / ".driftmaps" / "runs").iterdir())
        self.assertEqual(len(runs), 1)
        content = (runs[0] / "trail.yaml").read_text()
        self.assertIn("node: setup", content)
        self.assertIn("isMember: false", content)
        self.assertIn("source_sha256:", content)
        self.assertIn("history: []", content)
        self.assertFalse((runs[0] / "handover.yaml").exists())

    def test_draft_must_opt_in_to_trial(self):
        text = self.source.read_text().replace("status: example", "status: draft")
        self.source.write_text(text)
        with self.assertRaisesRegex(core.MapError, "Draft maps"):
            core.start(type("Args", (), {
                "map": str(self.source), "root": str(self.root),
                "input_file": None, "allow_draft": False
            })())

    def test_input_validation_occurs_before_folder_creation(self):
        inp = self.root / "bad-input.yaml"
        inp.write_text("nested:\n  key: value\n", encoding="utf-8")
        with self.assertRaisesRegex(core.MapError, "flat key"):
            core.start(type("Args", (), {
                "map": str(self.source), "root": str(self.root),
                "input_file": str(inp), "allow_draft": False
            })())
        self.assertFalse((self.root / ".driftmaps" / "runs").exists())

    def test_missing_limits_is_rejected(self):
        source = self.source.read_text()
        source = source.replace("limits:\n  max_transitions: 12\n", "")
        self.source.write_text(source)
        self.assertTrue(any("max_transitions" in x for x in
                            core.analyze(self.source)["errors"]))


if __name__ == "__main__":
    unittest.main()
