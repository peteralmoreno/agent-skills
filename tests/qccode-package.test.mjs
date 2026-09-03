import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve("qccode");
const stages = [
  "questions",
  "research",
  "design-discussion",
  "structure",
  "plan",
  "worktree",
  "implement",
];

test("Q-C-Code contains its entrypoint, references, and seven workflows", () => {
  const skillPath = path.join(root, "SKILL.md");
  assert.ok(fs.existsSync(skillPath));
  const skill = fs.readFileSync(skillPath, "utf8");
  const references = [...skill.matchAll(/references\/[A-Za-z0-9._/-]+\.md/g)].map(
    (match) => match[0],
  );
  assert.ok(references.length >= 8);
  for (const reference of new Set(references)) {
    assert.ok(fs.existsSync(path.join(root, reference)), reference);
  }
  for (const stage of stages) {
    assert.ok(
      fs.existsSync(path.join(root, "workflows", stage, "workflow.md")),
      stage,
    );
  }
});

test("Q-C-Code package excludes backups and run state", () => {
  assert.equal(
    fs.existsSync(path.resolve("qccode.backup-20260627-103648")),
    false,
  );
  assert.equal(fs.existsSync(path.join(root, ".qccode")), false);
});
