"""Regression tests for self-contained Storycraft outputs and route integrity."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import base64
import json
import tempfile
from unittest.mock import patch
import unittest

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'scripts'/'render_story.py'
spec=importlib.util.spec_from_file_location('storycraft_renderer', MOD)
renderer=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(renderer)
CHECK=ROOT/'scripts'/'check_story.py'
spec2=importlib.util.spec_from_file_location('storycraft_check', CHECK)
checker=importlib.util.module_from_spec(spec2)
assert spec2.loader
spec2.loader.exec_module(checker)


class TestStorycraft(unittest.TestCase):
    def setUp(self):
        self.story=json.loads((ROOT/'examples'/'burrito-blaster.story.json').read_text(encoding='utf-8'))

    def test_three_styles_preserve_content_and_all_links(self):
        expected_nodes={n['title'] for n in self.story['flow']['nodes']}
        expected_branches={e['label'] for e in self.story['flow']['edges']}
        for style in renderer.STYLES:
            with self.subTest(style=style):
                result=renderer.render_story(self.story,style)
                self.assertIn(f'class="style-{style}"',result)
                self.assertIn(self.story['title'],result)
                for title in expected_nodes:self.assertIn(title,result)
                for condition in expected_branches:self.assertIn(condition,result)
                self.assertIn('id="story-data"',result)
                self.assertIn('aria-live',result)
                with tempfile.TemporaryDirectory() as temp:
                    page=Path(temp)/'render.html';page.write_text(result,encoding='utf-8')
                    self.assertEqual(checker.check_file(page),[])

    def test_signature_visual_language_is_in_real_output(self):
        dark=renderer.render_story(self.story,'dark')
        morrito=renderer.render_story(self.story,'morrito')
        gilded=renderer.render_story(self.story,'gilded')
        self.assertIn('--accent:#ef5b53',dark)
        self.assertIn('.hero h1 .title-emphasis{color:#ef5b53}',dark)
        self.assertIn('morrito-star',morrito)
        self.assertIn('class="story-scene"',morrito)
        self.assertIn('pipe-connector pipe-green',morrito)
        self.assertIn('route-pipe pipe-orange',morrito)
        self.assertIn('route-pipe pipe-red',morrito)
        self.assertIn('class="section-ornament"',gilded)
        self.assertIn('class="wand-mark"',gilded)
        self.assertIn('class="riding-bird"',gilded)
        self.assertIn('#42314f',gilded)  # violet tactical controls
        for page in (dark,morrito,gilded):
            self.assertIn('Only a preview—not a real launch',page)
            self.assertIn('What if the destination is unknown?',page)

    def test_v03_question_motifs_and_pipe_collars_are_present(self):
        morrito=renderer.render_story(self.story,'morrito')
        gilded=renderer.render_story(self.story,'gilded')
        self.assertIn('class="collar collar-left"',morrito)
        self.assertIn('class="collar collar-right"',morrito)
        self.assertIn('class="morrito-question-block"',morrito)
        self.assertIn('class="bird-curiosity"',gilded)
        self.assertIn('class="bird-curiosity-question"',gilded)
        self.assertIn('class="story-callout uncertain"',gilded)
        # Neither style should add an undefined route or invent evidence.
        self.assertEqual(morrito.count('class="diversion '),len(self.story['flow']['edges'])-len(self.story['flow']['primary_path'])+1)

    def test_one_integrated_morrito_footer(self):
        morrito=renderer.render_story(self.story,'morrito')
        self.assertEqual(morrito.count('<footer'),1)
        self.assertIn('<footer class="footer morrito-footer"><div class="story-scene"',morrito)
        self.assertIn('<div class="footer-copy shell">',morrito)
        self.assertNotIn('background:linear-gradient(#89df29 0 9px',morrito)
        # Generic themes retain their original simple footer.
        for style in ('dark','gilded'):
            page=renderer.render_story(self.story,style)
            self.assertIn('<footer class="footer shell">',page)
            self.assertNotIn('morrito-footer',page)

    def test_gilded_uses_local_presenter_png_if_present(self):
        with tempfile.TemporaryDirectory() as directory:
            temp=Path(directory)
            png=temp/'gilded-bird.png'
            png.write_bytes(b'\x89PNG\r\n\x1a\n' + b'local-art')
            with patch.object(renderer,'ASSET_ROOT',temp):
                element=renderer.gilded_bird_markup()
            self.assertIn('<img class="riding-bird"',element)
            self.assertIn('data:image/png;base64,',element)

    def test_curious_mascot_reuses_exact_same_presenter_image(self):
        import base64
        # Same data URI in both components; no separate generated mascot.
        original_png=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScL/nwAAAABJRU5ErkJggg==')
        with tempfile.TemporaryDirectory() as directory:
            assets=Path(directory)
            (assets/'gilded-bird.png').write_bytes(original_png)
            (assets/'gilded-bird.svg').write_text('<svg></svg>',encoding='utf-8')
            (assets/'gilded-sword.svg').write_text('<svg></svg>',encoding='utf-8')
            with patch.object(renderer,'ASSET_ROOT',assets):
                hero=renderer.gilded_bird_markup()
                question=renderer.gilded_curiosity_markup()
            exact='data:image/png;base64,'+base64.b64encode(original_png).decode('ascii')
            self.assertIn(exact,hero)
            self.assertIn(exact,question)
            self.assertIn('bird-curiosity-question',question)

    def test_explicit_custom_bird_import_overrides_cached_bird(self):
        import os
        with tempfile.TemporaryDirectory() as directory:
            assets=Path(directory)
            canonical=assets/'gilded-bird.png'
            original=b'\x89PNG\r\n\x1a\n' + b'canonical-art'
            custom=assets/'custom-bird.png'
            alternate=b'\x89PNG\r\n\x1a\n' + b'custom-art'
            canonical.write_bytes(original)
            custom.write_bytes(alternate)
            with patch.object(renderer,'ASSET_ROOT',assets), patch.dict(os.environ,{'STORYCRAFT_PRESENTER_BIRD':str(custom)}):
                self.assertEqual(renderer.presenter_bird_path(),custom)
                self.assertIn(base64.b64encode(alternate).decode('ascii'),renderer.gilded_curiosity_markup())

    def test_morrito_pipe_tube_is_longer_with_two_end_collars(self):
        pipe=renderer.pipe_html('green')
        self.assertIn('viewBox="0 0 78 30"',pipe)
        self.assertIn('width="66"',pipe)
        self.assertIn('class="collar collar-left"',pipe)
        self.assertIn('class="collar collar-right"',pipe)

    def test_gilded_title_keeps_original_font_with_heavier_outlines(self):
        css=(ROOT/'assets'/'gilded-presenter.css').read_text(encoding='utf-8')
        self.assertIn('-webkit-text-stroke:1.6px #303629',css)
        self.assertIn('-webkit-text-stroke:1.6px #4f3a1d',css)
        self.assertIn('font-family:var(--serif)',css)

    def test_callouts_are_explicit_and_safe(self):
        self.story['callouts'][0]['kind']='success'
        with self.assertRaisesRegex(ValueError,'important or uncertain'):
            renderer.validate_story(self.story)
        self.story['callouts'][0]['kind']='important'
        self.story['callouts'][0]['text']='<img src=x onerror=alert(1)>'
        page=renderer.render_story(self.story,'morrito')
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;',page)
        self.assertNotIn('<img src=x onerror=alert(1)>',page)

    def test_invalid_edges_rejected(self):
        self.story['flow']['edges'][0]['to']='nonexistent'
        with self.assertRaisesRegex(ValueError,'nonexistent'):
            renderer.validate_story(self.story)

    def test_primary_path_cannot_invent_a_connection(self):
        self.story['flow']['primary_path'][2]='pause'
        with self.assertRaisesRegex(ValueError,'no such edge'):
            renderer.validate_story(self.story)

    def test_external_scripts_in_source_strings_cannot_break_out(self):
        self.story['flow']['nodes'][0]['detail']='\u003c/script\u003e<script>alert(1)</script>'
        result=renderer.render_story(self.story,'dark')
        self.assertNotIn('</script><script>alert(1)</script>',result)
        self.assertIn('\\u003c/script\\u003e',result)

    def test_reject_unsafe_links(self):
        self.story['sources']=[{'label':'Unsafe','url':'javascript:alert(1)'}]
        with self.assertRaisesRegex(ValueError,'explicit https'):
            renderer.validate_story(self.story)

    def test_reject_unknown_hero_symbol(self):
        self.story['hero_symbol']='remote-stock-photo'
        with self.assertRaisesRegex(ValueError,'hero_symbol'):
            renderer.validate_story(self.story)

    def test_illustration_boundary_stays_visible(self):
        for style in renderer.STYLES:
            result=renderer.render_story(self.story,style)
            self.assertIn('No real orders, coordinates, projectiles, or messages are used.',result)
            self.assertIn('Stage inspector · presentation only',result)
            self.assertNotIn('https://fonts.',result)

    def test_output_previews_are_current(self):
        for style in renderer.STYLES:
            source=ROOT/'examples'/f'burrito-blaster-{style}.html'
            self.assertTrue(source.exists(),f'missing {source}')
            self.assertEqual(source.read_text(encoding='utf-8'), renderer.render_story(self.story,style))


if __name__=='__main__':unittest.main()
