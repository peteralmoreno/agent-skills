import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const repositoryRoot = path.resolve(".");
const requiredRootFiles = ["README.md", "LICENSE", ".gitignore"];

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    if (entry.name === ".git") return [];
    const fullPath = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(fullPath) : [fullPath];
  });
}

test("repository includes public documentation and license files", () => {
  for (const relativePath of requiredRootFiles) {
    assert.ok(fs.existsSync(path.join(repositoryRoot, relativePath)), relativePath);
  }
});

test("publishable paths exclude local state, backups, and environment files", () => {
  for (const filePath of walk(repositoryRoot)) {
    const relativePath = path.relative(repositoryRoot, filePath).replaceAll("\\", "/");
    assert.doesNotMatch(relativePath, /(^|\/)\.qccode(\/|$)/i);
    assert.doesNotMatch(relativePath, /(^|\/)[^/]*backup[^/]*(\/|$)/i);
    assert.doesNotMatch(relativePath, /(^|\/)(sessions?|history)(\/|$)/i);
    assert.doesNotMatch(path.basename(relativePath), /^\.env(?:\..*)?$/i);
  }
});

test("text files contain no credential values or machine-specific paths", () => {
  const textExtensions = new Set([".md", ".yaml", ".yml", ".json", ".mjs", ".js", ".txt"]);
  const forbidden = [
    /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,
    /\bghp_[A-Za-z0-9]{30,}\b/,
    /\bgithub_pat_[A-Za-z0-9_]{30,}\b/,
    /\bsk-[A-Za-z0-9]{30,}\b/,
    /\b[A-Za-z]:\\(?:Users|source)\\/i,
  ];

  for (const filePath of walk(repositoryRoot)) {
    if (!textExtensions.has(path.extname(filePath).toLowerCase())) continue;
    const content = fs.readFileSync(filePath, "utf8");
    for (const pattern of forbidden) {
      assert.doesNotMatch(content, pattern, `${path.relative(repositoryRoot, filePath)}: ${pattern}`);
    }
  }
});
