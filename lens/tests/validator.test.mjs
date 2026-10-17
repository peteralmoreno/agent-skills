import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { validatePlan } from '../scripts/validate-plan.mjs';

const fixtures = path.resolve('lens/tests/fixtures');
const lens = fs.readFileSync(path.join(fixtures,'event-notifications-lens.md'),'utf8');
const prism = fs.readFileSync(path.join(fixtures,'event-notifications-prism.md'),'utf8');
const check = (text, src=prism) => validatePlan(text,{prismText:src});

test('valid approved LENS plan passes mechanical checks', () => {
  const result = check(lens);
  assert.deepEqual(result.errors, []);
  assert.equal(result.ok,true);
  assert.equal(result.counts.requirements,2);
  assert.equal(result.counts.work_units,2);
});

test('detects an uncovered requirement from source PRISM', () => {
  const edited = lens.replace('| R2 | Later | Future consumer-migration increment |\n','');
  assert.match(check(edited).errors.join(' '), /R2 is not classified/);
});

test('detects a Now requirement without a work unit', () => {
  const edited = lens.replace('| R2 | Later | Future consumer-migration increment |','| R2 | Now | Include in this increment |');
  assert.match(check(edited).errors.join(' '), /R2: Now requirement has no work-unit link/);
});

test('detects cycles and unknown dependencies', () => {
  const c = lens.replace('| W1 | Add agreed event publication path | None |','| W1 | Add agreed event publication path | W2 |');
  assert.match(check(c).errors.join(' '), /cyclic dependencies/);
  const u = lens.replace('| W1 | Add agreed event publication path | None |','| W1 | Add agreed event publication path | W9 |');
  assert.match(check(u).errors.join(' '), /unknown dependency W9/);
});

test('every work unit needs a Signal row', () => {
  const edited = lens.replace('| W2 | M1, M2 | Record publication and backward-compatibility test results |\n','');
  assert.match(check(edited).errors.join(' '), /W2: no planned verification/);
});

test('unknown spec measure is rejected', () => {
  const edited = lens.replace('| W2 | M1, M2 |','| W2 | M1, M99 |');
  assert.match(check(edited).errors.join(' '), /unknown PRISM measure M99/);
});

test('approved status cannot contain an unresolved Blocker', () => {
  const edited = lens.replace('| N1 | Question |','| N1 | Blocker |');
  assert.match(check(edited).errors.join(' '), /approved plan cannot contain unresolved Blocker/);
});

test('unapproved PRISM does not qualify for approved handoff', () => {
  const edited = lens.replace('source_status: approved','source_status: draft');
  assert.match(check(edited).errors.join(' '), /requires source_status: approved/);
});

test('section order must be canonical', () => {
  const edited = lens.replace('## L — Limits','## X — Former limits');
  assert.match(check(edited).errors.join(' '), /Missing required heading/);
});

test('missing source can still be checked structurally with warning', () => {
  const result = validatePlan(lens);
  assert.equal(result.ok,true);
  assert.match(result.warnings.join(' '), /PRISM source not supplied/);
});
