"""Format contract checks for the three static HTML companion skills."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from importlib import import_module
validate=import_module('validate-semantic-html')

class HTMLContractTests(unittest.TestCase):
    def source(self,skill,which='example'):
        stem={'ray':'intent','prism':'spec','lens':'plan'}[skill]
        return (ROOT/f'{skill}-html'/'assets'/f'{stem}-{which}.html').read_text(encoding='utf-8')

    def test_sample_html_examples_are_valid(self):
        for stage in ('ray','prism','lens'):
            with self.subTest(stage=stage):
                result=validate.analyze(self.source(stage),stage)
                self.assertTrue(result['ok'],result['errors'])

    def test_sample_html_templates_are_valid(self):
        for stage in ('ray','prism','lens'):
            with self.subTest(stage=stage):
                result=validate.analyze(self.source(stage,'template'),stage)
                self.assertTrue(result['ok'],result['errors'])

    def test_ray_angle_grades_visible_and_valid(self):
        src=self.source('ray')
        self.assertFalse(validate.analyze(src.replace('data-grade="3"','data-grade="7"'))['ok'])
        self.assertFalse(validate.analyze(src.replace('[3:Strong]','[4:Required]'))['ok'])

    def test_prism_trace_references_exist(self):
        src=self.source('prism')
        self.assertFalse(validate.analyze(src.replace('data-trace="R1 I1 S1 M1"','data-trace="R1 I8 S1 M1"'))['ok'])
        self.assertFalse(validate.analyze(src.replace('data-decision-state="preferred"','data-decision-state="required"'))['ok'])

    def test_lens_requires_signals_and_coverage(self):
        src=self.source('lens')
        self.assertFalse(validate.analyze(src.replace('data-work-id="W1" data-measures="M1"','data-work-id="W8" data-measures="M1"'))['ok'])
        self.assertFalse(validate.analyze(src.replace('data-delivery="Now"','data-delivery="Unclear"'))['ok'])

    def test_rejects_executable_input_and_malformed_document(self):
        src=self.source('ray')
        self.assertFalse(validate.analyze(src.replace('</body>','<script>alert(1)</script></body>'))['ok'])
        self.assertFalse(validate.analyze(src.replace('data-skill="ray"','data-skill="prism"'))['ok'])

    def test_html_variants_are_standalone_and_format_flexible(self):
        for stage in ('ray','prism','lens'):
            with self.subTest(stage=stage):
                skill=(ROOT/f'{stage}-html'/'SKILL.md').read_text(encoding='utf-8')
                self.assertTrue(skill.startswith(f'---\nname: {stage}-html\n'))
                self.assertIn('Markdown',skill)
                self.assertIn('HTML',skill)
                self.assertTrue((ROOT/f'{stage}-html'/'agents'/'openai.yaml').is_file())
                self.assertTrue((ROOT/f'{stage}-html'/'references'/'html-guide.md').is_file())

    def test_cross_format_contract_is_explicit(self):
        guide=(ROOT/'docs'/'format-interoperability.md').read_text(encoding='utf-8')
        self.assertIn('Input format **never forces** output format',guide)
        self.assertIn('do not currently parse HTML',guide)
        self.assertIn('independent of the presentation format',guide)

if __name__ == '__main__': unittest.main()
