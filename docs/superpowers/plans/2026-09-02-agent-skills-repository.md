# Agent Skills Repository Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish verified `qccode` and `prism` skill packages in the public `peteralmoreno/agent-skills` GitHub repository.

**Architecture:** Keep each skill self-contained at the repository root. Preserve Q-C-Code from its authoritative Claude folder, while creating PRISM from the standalone five-view framework with its own behavioral evidence and contract tests. Use dependency-free Node tests and the bundled Codex skill validator so contributors can verify the repository locally.

**Tech Stack:** Markdown, YAML, Node.js built-in test runner, PowerShell, Git, GitHub

**Spec:** `docs/superpowers/specs/2026-09-02-agent-skills-repository-design.md`

## Global Constraints

- Publish to the public repository `peteralmoreno/agent-skills`.
- Do not modify or delete the original source folders.
- Exclude Q-C-Code backups, `.qccode` runs, chat/session history, credentials, and machine-specific state.
- Preserve Q-C-Code's Claude-specific `argument-hint`, tool names, and hierarchical workflow behavior.
- Implement PRISM as Problem, Requirements, Invariants, Solution, and Measures; do not substitute Spec Writer's six-stage model.
- Use only built-in Node modules for repository tests.
- License the published repository under MIT.

---

### Task 1: Package the authoritative Q-C-Code skill

**Files:**

- Create: `tests/qccode-package.test.mjs`
- Create: `qccode/**` by copying `~/.claude/skills/qccode/**`

**Interfaces:**

- Consumes: the authoritative live Q-C-Code tree under `~/.claude/skills/qccode`.
- Produces: a self-contained `qccode/` package whose declared references and seven workflow entrypoints resolve.

- [ ] **Step 1: Write the failing package contract test**

```js
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
  const references = [...skill.matchAll(/references\/[A-Za-z0-9._/-]+\.md/g)]
    .map((match) => match[0]);
  assert.ok(references.length >= 8);
  for (const reference of new Set(references)) {
    assert.ok(fs.existsSync(path.join(root, reference)), reference);
  }
  for (const stage of stages) {
    assert.ok(fs.existsSync(path.join(root, "workflows", stage, "workflow.md")), stage);
  }
});

test("Q-C-Code package excludes backups and run state", () => {
  assert.equal(fs.existsSync(path.resolve("qccode.backup-20260627-103648")), false);
  assert.equal(fs.existsSync(path.join(root, ".qccode")), false);
});
```

- [ ] **Step 2: Run the test and verify it fails because `qccode/SKILL.md` is absent**

Run: `node --test tests/qccode-package.test.mjs`

Expected: FAIL at `assert.ok(fs.existsSync(skillPath))`.

- [ ] **Step 3: Copy the authoritative Q-C-Code tree**

Resolve the user profile with `[Environment]::GetFolderPath('UserProfile')`, then copy only `.claude\skills\qccode` beneath it. Never copy the sibling backup directory.

- [ ] **Step 4: Run the Q-C-Code package test**

Run: `node --test tests/qccode-package.test.mjs`

Expected: both tests PASS.

- [ ] **Step 5: Commit the Q-C-Code package**

```powershell
git add qccode tests/qccode-package.test.mjs
git commit -m "feat: publish qccode skill"
```

---

### Task 2: Establish the PRISM behavioral baseline

**Files:**

- Create: `prism/tests/skill-baseline.md`

**Interfaces:**

- Consumes: realistic ambiguous specification prompts and the standalone `PRISM_Spec_Framework.md` only as evaluation criteria.
- Produces: observed baseline failures that justify the new skill's instructions.

- [ ] **Step 1: Run a fresh agent without the PRISM skill on a build scenario**

Use this scenario:

```text
Turn this into an engineering specification: "Add reliable bulk invoice export. It should be fast, secure, and retry safely." Do not ask me follow-up questions; make reasonable assumptions.
```

Record whether the baseline separates the problem, numbered requirements, invariants, solution decisions, measures, and traceability; also record any invented decisions.

- [ ] **Step 2: Run a fresh agent without the PRISM skill on a review scenario**

Use this scenario:

```text
Review this spec: "Build exports with a queue. Use Redis. It must be scalable. We will know it works when QA likes it." Identify whether it is ready for implementation.
```

Record whether the baseline distinguishes requirements from solution choices and demands objective measures.

- [ ] **Step 3: Save the verbatim outcomes and identified failure patterns**

`prism/tests/skill-baseline.md` must include the prompts, observed behavior, and a short list of gaps. It must not claim the forward test passed.

---

### Task 3: Implement the PRISM skill test-first

**Files:**

- Create: `prism/tests/skill-contract.test.mjs`
- Create: `prism/SKILL.md`
- Create: `prism/references/prism-spec-framework.md`
- Create: `prism/agents/openai.yaml`

**Interfaces:**

- Consumes: an idea or existing specification and an explicit mode: Explain, Build, or Review.
- Produces: a confirmed PRISM specification or a structured PRISM review; it never authorizes research, planning, or implementation.

- [ ] **Step 1: Write the failing PRISM contract tests**

```js
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
  for (const view of ["Problem", "Requirements", "Invariants", "Solution", "Measures"]) {
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
```

- [ ] **Step 2: Run the tests and verify they fail because the PRISM package is absent**

Run: `node --test prism/tests/skill-contract.test.mjs`

Expected: FAIL with `ENOENT` for `prism/SKILL.md`.

- [ ] **Step 3: Add the canonical five-view framework reference**

Copy the content of `..\study-card-creator\PRISM_Spec_Framework.md` to `prism/references/prism-spec-framework.md`, preserving its Problem, Requirements, Invariants, Solution, Measures, and traceability definitions.

- [ ] **Step 4: Write the minimal PRISM skill**

The skill must:

- route Explain, Build, and Review modes;
- require the reference to be read completely before Build or Review;
- ask one focused question at a time when material information is missing;
- label unconfirmed content as assumptions or open questions;
- produce numbered `R#`, `I#`, `S#`, and `M#` items;
- connect important requirements through a traceability section;
- end at an approved specification or review without starting downstream work.

- [ ] **Step 5: Add portable UI metadata**

```yaml
interface:
  display_name: "PRISM Spec Framework"
  short_description: "Turn vague engineering prompts into traceable specifications"
  default_prompt: "Use PRISM to build or review a software specification with explicit problems, requirements, invariants, solution decisions, measures, and traceability."
```

- [ ] **Step 6: Run PRISM contract tests and validator**

Run:

```powershell
node --test prism/tests/skill-contract.test.mjs
$env:PYTHONUTF8='1'
$validator = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex\skills\.system\skill-creator\scripts\quick_validate.py'
python $validator prism
```

Expected: all tests PASS and validator reports `Skill is valid!`.

- [ ] **Step 7: Commit PRISM**

```powershell
git add prism
git commit -m "feat: add prism specification skill"
```

---

### Task 4: Forward-test PRISM behavior

**Files:**

- Create: `prism/tests/skill-forward-results.md`

**Interfaces:**

- Consumes: the same two scenarios from the baseline plus `prism/SKILL.md` and its reference.
- Produces: evidence that the skill improves structure, uncertainty handling, objective measures, and traceability.

- [ ] **Step 1: Run fresh agents with the PRISM skill on both baseline scenarios**

For Build mode, verify the agent either asks for missing material decisions or marks them explicitly as assumptions/open questions. For Review mode, verify it separates the prescribed queue/Redis solution from observable requirements and replaces subjective acceptance with objective measures.

- [ ] **Step 2: Record forward outcomes**

Write the prompts, concise outcome summaries, and comparison against baseline to `prism/tests/skill-forward-results.md`.

- [ ] **Step 3: Re-run contract tests**

Run: `node --test prism/tests/skill-contract.test.mjs`

Expected: all tests PASS.

- [ ] **Step 4: Commit behavioral evidence**

```powershell
git add prism/tests/skill-forward-results.md
git commit -m "test: document prism behavior"
```

---

### Task 5: Add repository documentation, licensing, and release checks

**Files:**

- Create: `README.md`
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `tests/repository-safety.test.mjs`

**Interfaces:**

- Consumes: the finished skill packages and compatibility facts.
- Produces: installable public documentation and an automated guard against accidentally publishing local or sensitive state.

- [ ] **Step 1: Write the failing repository safety test**

The test must recursively inspect tracked publishable files and reject `.env` files, private keys, `.qccode` run directories, backup directories, and absolute local source paths. It must allow documentation that names the portable `~/.claude/skills/qccode` install path.

- [ ] **Step 2: Run the safety test and confirm it fails until root documentation exists**

Run: `node --test tests/repository-safety.test.mjs`

Expected: FAIL because `README.md`, `LICENSE`, and `.gitignore` are absent.

- [ ] **Step 3: Add README, MIT license, and ignore rules**

The README must describe both skills, clearly label Q-C-Code as Claude-specific and PRISM as portable, provide copy/install examples, and list validation commands. The ignore file must exclude `.env*`, `.qccode/`, backups, session artifacts, and common editor/system files.

- [ ] **Step 4: Run the complete verification suite**

Run:

```powershell
node --test tests/*.test.mjs prism/tests/*.test.mjs
$env:PYTHONUTF8='1'
$validator = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex\skills\.system\skill-creator\scripts\quick_validate.py'
python $validator prism
git diff --check
git status --short
```

Expected: tests PASS, PRISM validation passes, no whitespace errors, and only intended files are uncommitted.

- [ ] **Step 5: Commit repository documentation and checks**

```powershell
git add README.md LICENSE .gitignore tests
git commit -m "docs: add installation and release checks"
```

---

### Task 6: Create and publish the GitHub repository

**Files:**

- No additional repository files.

**Interfaces:**

- Consumes: verified local `main` branch and the authenticated GitHub account.
- Produces: public `https://github.com/peteralmoreno/agent-skills` with local `origin/main` tracking the uploaded commit.

- [ ] **Step 1: Verify the repository name is still available**

Open `https://github.com/peteralmoreno/agent-skills`. Continue only if it is absent or already belongs to the user and is empty/appropriate.

- [ ] **Step 2: Create the public repository without generated starter files**

Use GitHub's authenticated repository creation UI. Set owner `peteralmoreno`, name `agent-skills`, visibility Public, and do not initialize with README, license, or `.gitignore` because those exist locally.

- [ ] **Step 3: Add the remote and push**

```powershell
git remote add origin https://github.com/peteralmoreno/agent-skills.git
git push -u origin main
```

- [ ] **Step 4: Verify local and remote state**

Run:

```powershell
git status --short --branch
git ls-remote --heads origin main
git rev-parse HEAD
```

Expected: clean `main...origin/main`, and the remote `main` hash equals local `HEAD`.

- [ ] **Step 5: Verify the public repository contents**

Open `https://github.com/peteralmoreno/agent-skills` and confirm README rendering plus visible `qccode/` and `prism/` folders.
