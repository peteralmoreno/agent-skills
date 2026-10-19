"""Focused regressions for YAML integrity and authoritative graph selection."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
import map_format as fmt
spec = importlib.util.spec_from_file_location('core_format_test', SKILL / 'scripts/driftmaps.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

GRAPH = '## Flowchart\n\n```mermaid\nflowchart TD\nsetup -->|ready| work\nwork -->|done| complete\n```\n'


class FormatTests(unittest.TestCase):
    def test_normal_yaml_conveniences_and_duplicate_rejection(self):
        self.assertEqual(fmt.read_yaml('requires: [approval] # comment\nproduces: []'),
                         {'requires': ['approval'], 'produces': []})
        for text in ['requires: []\nrequires: [approval]', 'value: [unterminated',
                     'value: hello: world', 'value: [!unknown x]',
                     'value:\n  nested: 1\n  nested: 2']:
            with self.subTest(text=text), self.assertRaises(fmt.MapError):
                fmt.read_yaml(text)

    def test_null_and_malformed_node_headers_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'work.md'
            for header in ['requires:\nproduces:', 'requires:\n  - "approval\nproduces: []',
                           'requires: [false]\nproduces: []']:
                path.write_text('---\n' + header + '\n---\nInstructions\n')
                with self.subTest(header=header), self.assertRaises(fmt.MapError):
                    fmt.node_frontmatter(path)

    def test_graph_does_not_escape_section_or_ignore_routes(self):
        cases = [GRAPH.replace('work -->|done| complete', 'style work fill:#fff; work -->|done| complete'),
                 GRAPH.replace('## Flowchart', '## Flowchart\n\n## Unrelated example'),
                 GRAPH + '\n' + GRAPH,
                 '```markdown\n' + GRAPH + '\n```',
                 GRAPH.replace('work -->|done| complete', 'style work fill:#fff --> complete')]
        for body in cases:
            with self.subTest(body=body), self.assertRaises(fmt.MapError):
                fmt.graph(body)

    def test_basic_styles_and_trailing_semicolons_preserve_routes(self):
        body = GRAPH.replace('setup -->|ready| work', 'setup -->|ready| work;').replace(
            'work -->|done| complete', 'work -->|done| complete\nstyle work fill:#fff')
        self.assertEqual(fmt.graph(body)[1], fmt.graph(GRAPH)[1])

    def test_start_round_trips_nested_yaml_and_false(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inp = root / 'input.yaml'
            inp.write_text('order:\n  note: "hello: world"\n  items: [rice, beans]\nisMember: false\n')
            args = types.SimpleNamespace(map=str(SKILL / 'examples/burrito-cannon/MAP.md'),
                                         root=str(root), input_file=str(inp), allow_draft=False)
            core.start(args)
            trail = next(root.glob('.driftmaps/runs/*/trail.yaml'))
            data = fmt.read_yaml(trail.read_text())
            self.assertEqual(data['context'], fmt.read_yaml(inp.read_text()))
            self.assertEqual(data['current'], {'status': 'running', 'node': 'setup'})

    def test_bundled_parser_and_examples_stay_identical(self):
        other = SKILL.parent / 'driftmap-presenter'
        if not other.exists():
            self.skipTest('Other independently installable Skill is not present')
        self.assertEqual((SKILL / 'scripts/map_format.py').read_bytes(),
                         (other / 'scripts/map_format.py').read_bytes())
        example = SKILL / 'examples/burrito-cannon'
        for file in [example / 'MAP.md', *sorted((example / 'nodes').glob('*.md'))]:
            self.assertEqual(file.read_bytes(), (other / 'examples/burrito-cannon' / file.relative_to(example)).read_bytes())
        core.require_valid(other / 'examples/burrito-cannon/MAP.md')


if __name__ == '__main__':
    unittest.main()
