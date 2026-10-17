import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve('ray');
const read = (name) => fs.readFileSync(path.join(root, name), 'utf8');

test('RAY exposes a portable and independently installable skill', () => {
  const skill = read('SKILL.md');
  assert.match(skill, /^---\r?\nname: ray\r?\n/m);
  assert.match(skill, /description: .*intent/i);
  assert.doesNotMatch(skill, /argument-hint:|allowed-tools:/);
  assert.ok(fs.existsSync(path.join(root, 'agents', 'openai.yaml')));
  assert.ok(fs.existsSync(path.join(root, 'references', 'guide.md')));
});

test('RAY preserves exactly three fields and graded directions', () => {
  const skill = read('SKILL.md');
  for (const field of ['R — Result', 'A — Angle', 'Y — Why']) {
    assert.ok(skill.includes(field), `Missing ${field}`);
  }
  for (const grade of ['1:Consider', '2:Prefer', '3:Strong', '4:Required']) {
    assert.ok(skill.includes(grade), `Missing ${grade}`);
  }
  assert.match(skill, /grade \*\*each\*\*|grade each/i);
  assert.match(skill, /no early decisions yet/i);
});

test('RAY coaches and defers specification and implementation', () => {
  const skill = read('SKILL.md');
  assert.match(skill, /recommendations/i);
  assert.match(skill, /clarif/i);
  assert.match(skill, /not.*PRISM generator/i);
  assert.match(skill, /do \*\*not\*\* write PRISM/i);
  assert.match(skill, /never.*publish|never.*overwrite/i);
  assert.match(skill, /without separate, explicit instruction/i);
});

test('RAY has examples and a proposed parse contract but does not claim Jira integration', () => {
  assert.match(read('references/handoff-contract.md'), /proposed integration contract/i);
  assert.match(read('references/examples.md'), /Kafka/i);
  assert.match(read('README.md'), /not an existing Shipwright\/Jira integration/i);
  assert.ok(fs.existsSync(path.join(root, 'scripts', 'lint_ray.py')));
  assert.ok(fs.existsSync(path.join(root, 'tests', 'test_lint_ray.py')));
});
