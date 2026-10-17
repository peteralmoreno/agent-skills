import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const slurp = p => fs.readFileSync(path.join(root,p),'utf8');

for (const [name,artifact] of [['ray','intent'],['prism','spec'],['lens','plan']]) {
  test(`${name}-html is separately discoverable and honors cross-format requests`, () => {
    const dir=`${name}-html`;
    const skill=slurp(`${dir}/SKILL.md`);
    assert.match(skill,new RegExp(`^---\\nname: ${name}-html\\n`));
    assert.match(skill,/HTML/i);
    assert.match(skill,/Markdown/i);
    assert.match(skill,/input/i);
    assert.match(skill,/output|emit|produce/i);
    assert.match(skill,/standalone|independently/i);
    assert.doesNotMatch(skill,/allowed-tools:|argument-hint:/);
    for(const file of [
      `${dir}/agents/openai.yaml`,
      `${dir}/references/html-guide.md`,
      `${dir}/assets/${artifact}-template.html`,
      `${dir}/assets/${artifact}-example.html`,
      `${dir}/README.md`
    ]) assert.ok(fs.existsSync(path.join(root,file)),`${file} missing`);
    const html=slurp(`${dir}/assets/${artifact}-example.html`);
    assert.match(html,/^<!doctype html>/i);
    assert.match(html,new RegExp(`data-skill="${name}"`));
    assert.match(html,/<main\b/);
    assert.doesNotMatch(html,/<script\b|onload=|onclick=|<iframe\b/i);
  });
}

test('format selection is a preference in both directions', () => {
  const guide=slurp('docs/format-interoperability.md');
  for(const name of ['ray','prism','lens']) {
    assert.ok(guide.includes(`\`${name}\``));
    assert.ok(guide.includes(`\`${name}-html\``));
  }
  assert.match(guide,/explicit request.*wins/i);
  assert.match(guide,/Input format \*\*never forces\*\* output format/);
  assert.match(guide,/do not currently parse HTML/);
});

test('HTML layouts have meaningful stage-specific markers', () => {
  const ray=slurp('ray-html/assets/intent-example.html');
  const prism=slurp('prism-html/assets/spec-example.html');
  const lens=slurp('lens-html/assets/plan-example.html');
  for (const x of ['result','angle','why']) assert.ok(ray.includes(`data-ray-field="${x}"`));
  assert.match(ray,/data-grade="3"/);
  for(const x of ['R1','I1','S1','M1']) assert.ok(prism.includes(`data-prism-id="${x}"`));
  assert.match(prism,/data-trace="R1 I1 S1 M1"/);
  assert.match(lens,/data-requirement="R1" data-delivery="Now"/);
  assert.match(lens,/data-work-id="W1" data-depends-on="None"/);
  assert.match(lens,/data-work-id="W1" data-measures="M1"/);
});
