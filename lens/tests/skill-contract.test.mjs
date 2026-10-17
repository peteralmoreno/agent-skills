import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve('lens');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

test('LENS is a portable, standalone skill', () => {
  const skill = read('SKILL.md');
  assert.match(skill, /^---\r?\nname: lens\r?\n/);
  assert.match(skill, /description: Use when/);
  assert.doesNotMatch(skill, /argument-hint:|allowed-tools:/);
  assert.ok(fs.existsSync(path.join(root, 'agents/openai.yaml')));
  assert.ok(fs.existsSync(path.join(root, 'assets/plan-template.md')));
  assert.ok(fs.existsSync(path.join(root, 'references/guide.md')));
});

test('LENS defines all four sections and a single referenced artifact', () => {
  const s = read('SKILL.md');
  for (const x of ['L — Limits','E — Execution plan','N — Needs','S — Signals','source_spec','Requirement coverage']) {
    assert.ok(s.includes(x), `Missing ${x}`);
  }
  assert.match(s, /one standalone, implementation-ready LENS document/i);
  assert.match(s, /No(?:thing)? .*authoriz|not permission|does not authorize/i);
});

test('LENS does not turn into an implementation or review workflow', () => {
  const s = read('SKILL.md');
  assert.match(s, /Do not edit application code/);
  assert.match(s, /open PRs/);
  assert.match(s, /not.*code/i);
  assert.match(s, /source PRISM/);
  assert.match(s, /user approv/i);
});

test('LENS includes a PRISM mapping, worked examples, rubric, and mechanical checks', () => {
  assert.match(read('references/prism-mapping.md'), /R# → I# → S# → M#/);
  assert.match(read('references/examples.md'), /Kafka/);
  assert.match(read('references/review-rubric.md'), /Ready for handoff/);
  assert.ok(fs.existsSync(path.join(root,'scripts/validate-plan.mjs')));
});
