import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve("prism");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");

test("PRISM exposes valid portable skill metadata", () => {
  const skill = read("SKILL.md");
  assert.match(skill, /^---\r?\nname: prism\r?\n/m);
  assert.match(skill, /description: Use when/i);
  assert.doesNotMatch(skill, /argument-hint:|allowed-tools:/);
  assert.ok(fs.existsSync(path.join(root, "agents", "openai.yaml")));
});

test("PRISM defines all five views and three operating modes", () => {
  const skill = read("SKILL.md");
  for (const view of [
    "Problem",
    "Requirements",
    "Invariants",
    "Solution",
    "Measures",
  ]) {
    assert.match(skill, new RegExp(`\\b${view}\\b`, "i"));
  }
  for (const mode of ["Explain", "Build", "Review"]) {
    assert.match(skill, new RegExp(`\\b${mode}\\b`, "i"));
  }
  assert.match(skill, /traceability/i);
});

test("PRISM preserves uncertainty and stops before implementation", () => {
  const skill = read("SKILL.md");
  assert.match(skill, /do not invent|never invent/i);
  assert.match(skill, /does not authorize|do not (?:research|plan|implement)/i);
  assert.match(skill, /references\/prism-spec-framework\.md/);
});
