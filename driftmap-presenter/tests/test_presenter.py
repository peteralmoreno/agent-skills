"""Offline contract tests for the optional Drift Map Presenter."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "render_map.py"
EXAMPLE = SKILL / "examples" / "burrito-cannon"

spec = importlib.util.spec_from_file_location("driftmap_render", SCRIPT)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class PresenterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name) / "burrito-cannon"
        shutil.copytree(EXAMPLE, self.folder)
        self.source = self.folder / "MAP.md"

    def test_extracts_graph_and_node_metadata(self):
        model = renderer.load_map(self.source)
        self.assertEqual(model["name"], "burrito-cannon")
        self.assertEqual(len(model["edges"]), 9)
        ids = {n["id"] for n in model["nodes"]}
        self.assertEqual(ids, {"setup", "prepare", "locate", "blast",
                                "notify", "pause", "stop", "complete"})
        self.assertIn("isMember", next(n for n in model["nodes"]
                                       if n["id"] == "locate")["produces"])
        self.assertEqual(next(n for n in model["nodes"]
                              if n["id"] == "pause")["file"], "")

    def test_generates_standalone_html_without_mutating_source(self):
        files = sorted(self.folder.rglob("*.md"))
        before = {str(p): p.read_bytes() for p in files}
        output = self.folder / "overview.html"
        path, model = renderer.create(self.source, output)
        self.assertEqual(path, output)
        text = output.read_text(encoding="utf-8")
        self.assertIn('<svg id="graph"', text)
        self.assertIn("Route explorer", text)
        self.assertIn("nodes/locate.md", text)
        self.assertIn("isMember", text)
        self.assertNotIn("__MAP_DATA__", text)
        self.assertNotIn('<script src=', text)
        self.assertNotIn('fetch(', text)
        self.assertEqual(before, {str(p): p.read_bytes() for p in files})
        self.assertEqual(len(model["edges"]), 9)

    def test_refuses_overwriting_until_explicit(self):
        output = self.folder / "overview.html"
        renderer.create(self.source, output)
        with self.assertRaises(renderer.MapError):
            renderer.create(self.source, output)
        renderer.create(self.source, output, force=True)

    def test_missing_node_fails_instead_of_inventing_one(self):
        (self.folder / "nodes" / "blast.md").unlink()
        with self.assertRaisesRegex(renderer.MapError, "Missing node"):
            renderer.load_map(self.source)

    def test_unsupported_mermaid_does_not_silently_drop_routes(self):
        source = self.source.read_text()
        source = source.replace("setup[\"Setup\"] -->|ready| prepare[\"Prepare Burrito\"]",
                                "setup --> prepare --> locate")
        self.source.write_text(source)
        with self.assertRaisesRegex(renderer.MapError, "one directed Mermaid edge"):
            renderer.load_map(self.source)

    def test_untrusted_source_markup_cannot_execute_in_html(self):
        node_path = self.folder / "nodes" / "locate.md"
        node_path.write_text(node_path.read_text() +
                             "\n<script>alert('unsafe')</script>\n", encoding="utf-8")
        output = self.folder / "overview.html"
        renderer.create(self.source, output)
        html = output.read_text(encoding="utf-8")
        self.assertNotIn("<script>alert(", html)
        self.assertNotIn("</script><script>", html)
        # Content is escaped once for HTML and again when embedded in JS.
        self.assertIn("\\u0026lt;script", html)


if __name__ == "__main__":
    unittest.main()
