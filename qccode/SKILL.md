---
name: qccode
description: "Use Q-C-Code for coding tasks with structured Questions, Research, Design Discussion, Structure, Plan, Worktree, and Implement stages. Opens with a simple menu: new, continue, or about. Supports resumable scratch artifacts, sequential subagent handoff, and controlled parallel implementation when file ownership is safe."
argument-hint: [new|continue|about|list|execute|guide <task>]
allowed-tools: [Read, Write, Edit, Bash, PowerShell, Glob, Grep, Agent, AskUserQuestion, TodoWrite]
---

# Q-C-Code

Use this skill to either explain Q-C-Code/QRSPI or guide a developer through a coding task using Claude Code's hierarchical sub-agent capabilities. Q-C-Code uses the seven-stage QRSPI flow adapted for Claude Code with dedicated subagents for each stage:

```text
Questions -> Research -> Design Discussion -> Structure Outline -> Plan -> Worktree -> Implement
```

## Hierarchical Sub-Agent Architecture

Q-C-Code implements a hierarchical sub-agent pattern where:
- Main Q-C-Code coordinator manages overall workflow and model selection
- Each QRSPI stage is executed by a dedicated subagent with its own workflow
- Subagents operate independently with clear boundaries and communication through artifacts
- **Subagents execute sequentially** - each stage must complete before the next begins
- Results flow through artifact chain with minimal context transfer between stages
- Subagents are used for context control and keeping things clean, not for parallel execution
- User interaction is owned by the coordinator. Stage agents may identify questions, options, or approval gates, but the coordinator asks the user with `AskUserQuestion` and records the answer in the artifact before continuing.

```
Main Q-C-Code Coordinator
├── Model Selection (user choice)
├── Questions Subagent (workflow: ~/.claude/skills/qccode/workflows/questions/)
├── Research Subagent (workflow: ~/.claude/skills/qccode/workflows/research/)
├── Design Discussion Subagent (workflow: ~/.claude/skills/qccode/workflows/design-discussion/)
├── Structure Subagent (workflow: ~/.claude/skills/qccode/workflows/structure/)
├── Plan Subagent (workflow: ~/.claude/skills/qccode/workflows/plan/)
├── Worktree Subagent (workflow: ~/.claude/skills/qccode/workflows/worktree/)
└── Implement Subagent (workflow: ~/.claude/skills/qccode/workflows/implement/)
```

Treat QC-Code as a temporary context-management method, not a documentation project. Create scratch artifacts only when they help keep context small, reviewable, and resumable.

## Scratch Path

Use this scratch path for all Q-C-Code run artifacts:

```text
.qccode
```

Active runs:

```text
.qccode/active/<run-id>/
```

Archived runs:

```text
.qccode/archive/<run-id>/
```

Do not use `.devin/qccode` or `~/.claude/qccode`.

## Reference Policies

Use these references when executing or maintaining the skill:

- `references/step-template.md`
- `references/workflow-template.md`
- `references/artifact-schemas.md`
- `references/run-state.md`
- `references/tool-fallbacks.md`
- `references/parallel-implementation-policy.md`
- `references/validation-levels.md`
- `references/secret-handling.md`

## Recognition / Fallback

This machine stores Q-C-Code at `~/.claude/skills/qccode/SKILL.md`. If an agent does not list `qccode` among its active skills but the user invokes `/qccode`, `/ccode`, `$qccode`, `$ccode`, `qccode`, `ccode`, `q-c-code`, or `Q-C-Code`, it should read `~/.claude/skills/qccode/SKILL.md` and treat that file as the authoritative skill contract for the turn.

If a repo also contains a shim at another location, use the shim only to locate this canonical file. Do not maintain two independent Q-C-Code contracts.

## Model Selection Strategy

Before starting QC-Code execution, ask the user about their preferred model strategy for subagent execution using `AskUserQuestion`:

```text
Use AskUserQuestion to present:
Question: "QC-Code can execute each QRSPI stage using different model strategies. This affects cost, speed, and reasoning quality. Choose your model strategy:"
Options:
- Local model only: Use your current local model for all stages (fastest, no additional cost)
- Adaptive selection: Use better models for complex stages (Research, Design, Structure) and local model for simpler stages
- Premium quality: Use best available models for all stages (highest quality, higher cost)
- Custom strategy: Specify model preferences per stage
```

Include in the question description: "Your choice affects how subagents will be configured. Stage complexity: Research/Design/Structure = high, Questions/Plan = medium, Worktree/Implement = variable."

Record the user's model choice in the main coordinator context and configure subagent calls accordingly. For adaptive selection, use better models for Research, Design Discussion, and Structure Outline stages; use local model for Questions, Plan, Worktree, and Implement stages.

## Initial Flow Menu

When Q-C-Code is invoked (with or without initial task data), immediately present the menu using `AskUserQuestion`:

```text
Use AskUserQuestion to present:
Question: "What would you like to do with Q-C-Code?"
Options:
- New: Start a new Q-C-Code flow
- Continue: Resume an existing Q-C-Code flow  
- About: Learn about Q-C-Code/QRSPI
```

Present this menu clearly at the start using clickable buttons. Wait for the user to respond with their selection or provide their request directly via the "Other" option.

### Option 1: New
When the user chooses New, gather the feature idea using `AskUserQuestion`:
- Ask: "What would you like to implement? Please describe your feature idea, bug fix, or coding task."
- Gather the core request and any context they provide
- Ask follow-up questions only if the request is unclear
- Then proceed to the Questions stage with the gathered information

This is the primary entry point for new Q-C-Code flows when users invoke the skill without providing a task upfront.

### Option 2: Continue
When the user chooses Continue, follow the Continue / Resume Pattern below.

### Option 3: About
When the user chooses About, provide the New User Explanation below.

## Choose A Mode

The initial menu (new, continue, about) handles the most common cases. For specific commands, you can also choose modes directly:

- `explain` or `about`: Explain Q-C-Code/QRSPI to a new user in plain language, highlighting Claude Code-specific adaptations and hierarchical sub-agent architecture.
- `intake`: Prepare to receive feature ideas after the user explicitly preloads the skill without yet giving a task.
- `continue`: List or resume an existing Q-C-Code run from `.qccode/active/`, especially when the user starts a new chat and needs to recover context.
- `list`: Show all active Q-C-Code flows (available as direct command).
- `clear`: Clear active Q-C-Code run folders from `.qccode/active/` after an explicit confirmation (available as direct command).
- `guide`: Walk the user through Q-C-Code stages using subagents without editing code. Use this for planning, architecture discussion, or unclear work.
- `execute`: Apply Q-C-Code to a concrete code task using hierarchical subagents, then implement once the relevant questions, research, design, structure, plan, and execution policy are clear enough.

Do not force every stage when the task is tiny. Collapse stages deliberately, but preserve the intent: expose ambiguity, ground in the codebase, define shape, plan small slices, then implement.

## Preload / Intake Pattern

If the user invokes the skill without a concrete feature idea, immediately present the Initial Flow Menu using `AskUserQuestion`. Do not wait for task input - let the menu drive the interaction.

The menu system handles all cases:
- **New**: Will prompt for the feature idea as part of the New flow
- **Continue**: Will show active flows for resumption
- **About**: Will explain Q-C-Code/QRSPI

This allows users to operate entirely through the menu system without needing to provide initial data when invoking the skill.

## Continue / Resume Pattern

If the user says `qccode continue`, `ccode continue`, `continue qccode`, `continue ccode`, asks to resume a Q-C-Code flow, or starts a new chat with only a resume request, enter continue mode.

Do not create a new run folder yet. First inspect `.qccode/active/` in the current project. If the directory does not exist or has no run folders, say no active Q-C-Code flows were found and ask for the feature idea or a path to a run folder.

If the user includes a search string, such as `qccode continue joke` or `ccode continue joke`, use it to quickly find the intended active flow:

- Match case-insensitively against run folder names, slug words, and cheap text from stage artifacts such as headings, `feature intent`, `user or customer goal`, and `Output for next stage`.
- Prefer exact slug or title matches over partial text matches.
- If there is one clear match, show the matched flow and ask for confirmation before resuming.
- If there are multiple plausible matches, show the best 3 matches using the normal numbered resume list.
- If there are no matches, say no active flow matched the search string, then show the most recent 3 active flows.

When active runs exist:

1. Sort run folders by most recent filesystem modification time, newest first.
2. Show only the most recent 3 active flows unless the user asks for more. If fewer than 3 exist, show only those flows.
3. For each flow, infer a concise label from the folder slug and current stage from the furthest completed stage artifact in QRSPI order: `questions.md`, `research.md`, `design-discussion.md`, `structure.md`, `plan.md`, `worktree.md`, `implementation-notes.md`.
4. Include the run path, last modified time, current stage, and any short `Output for next stage` summary that can be read cheaply from the latest artifact.
5. Use `AskUserQuestion` to present the flows as clickable options.

Use this response shape with `AskUserQuestion`:

```text
First display: "I found these active Q-C-Code flows:"
[Show table with flow details]

Then use AskUserQuestion:
Question: "Which one should I continue?"
Options:
- Continue flow 1: <slug label> - <stage> - <local time>
- Continue flow 2: <slug label> - <stage> - <local time>
- Continue flow 3: <slug label> - <stage> - <local time>
- Show more active flows
- Other: provide a run path
```

After the user chooses a flow:

- Read only the furthest completed stage artifact plus the immediately necessary prior artifact.
- Determine the next stage from the artifact handoff chain.
- If the latest artifact contains a pending `User-facing checkpoint`, show that checkpoint when resuming unless the user's latest message already answers it.
- If the latest artifact has unresolved `Open questions` that affect the next stage, ask those questions before continuing.
- If the latest artifact is missing required `Output for next stage`, repair that artifact from adjacent artifacts before continuing.
- Continue in `guide` or `execute` mode according to the recovered plan and the user's latest instruction.
- Record in the next artifact that the flow was resumed from a new chat, including the resume path and any assumptions.

This pattern is the single-agent replacement for sub-agent handoff. The run folder is the shared memory surface; do not assume another chat pane has hidden context.

## Clear Active Flows

If the user says `qccode clear`, `ccode clear`, `clear qccode`, `clear ccode`, asks to clear active flows, or asks to clean up `.qccode/active/`, enter clear mode.

Clearing active flows is destructive. Never delete run folders without an explicit confirmation in the same chat turn after showing what will be removed.

First inspect `.qccode/active/`:

- If it does not exist or has no run folders, say there are no active Q-C-Code flows to clear.
- If the user provides a search string, such as `qccode clear joke` or `ccode clear joke`, match it using the same search rules as continue mode.
- If the user says `qccode clear all` or `ccode clear all`, prepare to clear all active flows, but still require confirmation.
- Otherwise, show the most recent active flows and ask what to clear.

Use this response shape before deletion with `AskUserQuestion`:

```text
First display: "These Q-C-Code active flows are selected for clearing:"
[Show table with flow details]

Then use AskUserQuestion:
Question: "This will delete the selected scratch folders. Confirm clear or choose a different option:"
Options:
- Confirm clear: Delete the selected flows
- Show more active flows
- Cancel
- Other: provide a run path or search string
```

After explicit confirmation:

- Delete only selected directories under the resolved `.qccode/active/` directory.
- Verify each resolved path is inside `.qccode/active/` before deleting.
- Do not delete `.qccode/active/` itself unless the user explicitly asks and it is empty.
- Do not delete worktrees, branches, source files, docs, or artifacts outside `.qccode/active/`.
- Report the cleared flow paths and any paths skipped.

## Deterministic Command Behavior

Support these deterministic commands for run state management:

### `qccode list`

List active runs from `.qccode/active/`. For each run, show:
- run id
- status
- current stage
- short user request
- next stage

### `qccode continue`

Resume the only active run if exactly one exists. If multiple exist, ask the user to choose.

### `qccode continue <keyword>`

Search active run IDs and `run.md` content. Resume only if exactly one match exists. Match case-insensitively against run folder names, slug words, and cheap text from stage artifacts.

### `qccode archive <run-id>`

Move active run from `.qccode/active/<run-id>/` to `.qccode/archive/<run-id>/`. Prefer archive over delete.

### `qccode clear <run-id>`

Use `AskUserQuestion` to ask for confirmation before deleting the specified run from `.qccode/active/`.

### `qccode clear all`

Use `AskUserQuestion` to ask for confirmation before deleting all active runs from `.qccode/active/`.

Never guess between multiple active runs. Always ask the user to choose when multiple matches exist.

## Temporary Workspace

For `guide` and `execute`, create a temporary task folder before deep work:

```text
.qccode/
  active/
    <timestamp>-<short-task-slug>/
      run.md
      coordinator-log.md
      questions.md
      research.md
      design-discussion.md
      structure.md
      plan.md
      worktree.md
      implementation-todos.md
      parallelization.md
      implementation-notes.md
```

Use local time for the timestamp when available, formatted like `2026-05-12-1630`. Keep the slug lowercase and short. If the project already has a documented scratch/planning convention, use that convention instead and record the path.

Rules:

- Start a new timestamped folder for each new QC-Code run.
- Reuse an existing folder only when the user explicitly resumes that run or the task clearly continues the same feature.
- Never overwrite another run's artifacts.
- Create only the files needed for the current task.
- Keep each file concise; prefer bullets and file references over prose.
- Treat these artifacts as scratch context, not final documentation.
- Load only the current stage artifact plus the immediately necessary prior artifact.
- At the end, ask whether to delete, leave, or archive the temporary folder if cleanup matters.
- `coordinator-log.md` tracks subagent launches, model choices, and stage handoffs for debugging and resumption.

## Parallel Implementation

During implementation, check whether planned work can be split into independent file-owned slices.

Parallel subagents may be used only when:

- Each slice has exclusive file ownership
- Required interfaces are already defined
- Slices do not depend on unfinished sibling slices
- Final integration is performed serially by the coordinator

No two parallel subagents may modify the same file.

If there is any doubt, use serial implementation.

See `references/parallel-implementation-policy.md` for detailed policy.

## Secret Handling

Never copy `.env`, `.env.local`, credentials, tokens, API keys, SSH keys, or ignored secret-bearing files automatically.

Ask before copying any ignored local config file.

Prefer documenting required variables in `.env.example`.

See `references/secret-handling.md` for detailed policy.

## Run Manifest Policy

Every run must have a `run.md` file that serves as the source of truth for:

- User request
- Current stage
- Completed stages
- Next stage
- Status (active, blocked, complete, archived)

The `run.md` file follows this schema:

```md
# Q-C-Code Run

## Run ID
`<run-id>`

## User Request
<original user request>

## Current Stage
questions | research | design-discussion | structure | plan | worktree | implement | complete | blocked | archived

## Completed Stages
- questions
- research

## Next Stage
<next stage name>

## Status
active | blocked | complete | archived

## Last Updated
<timestamp if available, otherwise omit>

## Notes
<short operational notes>
```

See `references/run-state.md` for detailed run state management.

## Tool Fallbacks

The skill may run in environments with different tools. Do not hard-lock the skill to one agent platform.

### User Questions
If a native structured question tool exists, use it. The skill uses `AskUserQuestion` for all user interactions:
- Menus and navigation
- Model selection
- Flow selection and resumption
- Confirmation dialogs
- Stage gates and approvals

If no structured question tool exists, ask in normal chat with numbered options.

### Todo Tracking
If a native todo tool exists, use it. The skill uses `TodoWrite` for task tracking during implementation.

If no todo tool exists, maintain `.qccode/active/<run-id>/implementation-todos.md`.

### Subagents
If native subagent execution exists, use it for hierarchical stage execution. The skill uses `Agent` calls and their returned results for sequential stage execution.

If subagents are unavailable, execute stages directly while preserving artifact boundaries.

### Parallel Subagents
If parallel subagents are unavailable, use serial execution. Do not fake parallel execution.

See `references/tool-fallbacks.md` for detailed fallback behavior.

## Validation Levels

Q-C-Code uses five graduated validation levels (0–4) to balance speed and correctness:

- **Level 0**: Not run — commands unavailable or explicitly skipped
- **Level 1**: Static inspection — manual file and logic review, no automated commands
- **Level 2**: Targeted validation — test, lint, or build command scoped to changed area
- **Level 3**: Full project validation — full test suite, build, or lint pass
- **Level 4**: Manual runtime verification — exercised in a running app or service

Choose validation level based on change risk, time constraints, available test infrastructure, and production impact.

See `references/validation-levels.md` for detailed policy and reporting format.

## Project Portability

Before Research or Worktree decisions, inspect the current project instead of assuming this repo's conventions.

Detect:

- language, framework, package manager, and test commands
- where source, tests, docs, scripts, and config live
- how the project represents workflows, routes, jobs, modules, or services
- whether the repo uses GitLab, GitHub, another forge, or local-only Git
- branch naming and review conventions if documented
- existing temporary planning or agent scratch directories

Defaults:

- Use `.qccode/active/<timestamp>-<slug>/` for scratch artifacts when no project convention exists.
- Use the project's existing test and formatting commands.
- Use GitLab merge-request language for GitLab projects, GitHub pull-request language for GitHub projects, and generic review language when the host is unknown.
- Do not add project-specific assumptions to the skill. Record them in the task artifact.

## Portable Skill Files

For cross-agent portability:

- Treat `SKILL.md` as the authoritative behavior contract.
- Keep detailed explanations in `references/` so agents load them only when needed.
- When porting to another agent or IDE, preserve `SKILL.md` first.

## Artifact Handoff Contract

Reduce dependency on shared agent context. Each stage must produce the primary input for the next stage.

Use this chain:

```text
user request -> questions.md
questions.md -> research.md
research.md -> design-discussion.md
design-discussion.md -> structure.md
structure.md -> plan.md
plan.md -> worktree.md
worktree.md -> implementation-notes.md
```

Before starting a stage:

- Read the previous stage artifact instead of relying on remembered conversation context.
- Copy forward only the decisions, constraints, and unresolved questions needed by the next stage.
- Record important assumptions explicitly in the current artifact.
- If the previous artifact is missing or too vague, repair that artifact or ask a focused question before continuing.

Each artifact should include:

- `Inputs`: files, prior artifacts, user request, or explicit assumptions used.
- `User-facing checkpoint`: the exact pause or review-gate message shown to the user when the stage is waiting on a reply.
- `User checkpoint response`: the user's answer or decision once the checkpoint has been resolved.
- `Output for next stage`: the short handoff the next stage must read.
- `Open questions`: only questions that still affect the next stage.

Anti-patterns:

- Relying on "as discussed above" instead of writing the decision down.
- Letting later stages depend on hidden chat history.
- Copying every prior artifact into every later artifact.
- Treating scratch artifacts as polished documentation.

## Interaction Gates

Use explicit interaction gates to keep the workflow collaborative without flooding the user.

Gate types:

- `pause gate`: stop and ask for user input before continuing.
- `review gate`: present a concise recommendation and ask for approval only when there are real choices or meaningful risk.
- `autonomous stage`: proceed without user input unless blocked or surprised.

Important:

- A gate is user-facing unless this skill explicitly says it may be collapsed.
- Before or immediately after showing a pause or review gate, save the exact user-facing gate text in the current stage artifact under `User-facing checkpoint`.
- When the user answers a saved checkpoint, record the answer under `User checkpoint response` before moving to the next stage.
- Do not satisfy a pause or review gate only by writing an artifact. The user must see the decision point in chat.
- If a gate is collapsed, say so briefly in chat and record the reason in the artifact.
- If the user later notices a skipped gate, stop, treat any implementation as a draft, and ask whether to keep, revise, or remove that draft before continuing.

Whenever asking the user to choose, use `AskUserQuestion` to present clickable button options. Include a short "other" option when appropriate for custom input.

For review gates, prefer compact markdown tables to present plans, options, tradeoffs, file changes, or validation expectations. After the table, use `AskUserQuestion` to ask whether the user wants to proceed with clear approval/rejection options.

Default gates:

| Stage | Gate | User interaction |
|---|---|---|
| Questions | pause gate | Ask 2-5 meaningful clarifying questions for loose feature ideas. |
| Research | autonomous stage | Investigate the repo; ask only if blocked or if research contradicts the request. |
| Design Discussion | review gate | Present current state, desired end state, tradeoffs, and recommendation when choices matter. |
| Structure Outline | review gate | Ask only if boundaries, ownership, modules, or validation strategy are non-obvious or risky. |
| Plan | review gate | Present the planned slices and ask for approval before Worktree unless the user pre-approved implementation or the change is truly tiny and mechanical. |
| Worktree / Execution Context | pause gate | Ask before branch, worktree, push, or merge-request changes; offer concrete options. |
| Implement | autonomous stage | Execute the approved slice; pause only for new scope, risk, failing assumptions, or plan changes. |

When pausing, keep the message short. Do not show full artifacts unless the user asks. Summarize the decision needed and give concrete options.

For resume consistency, the paused chat message and the saved `User-facing checkpoint` should match closely enough that another agent can re-post it without inventing new wording or options.

## Stage Workflow with Subagent Execution

QC-Code uses hierarchical sub-agent execution for each QRSPI stage. The main coordinator launches subagents sequentially, passing artifacts between stages while maintaining minimal context transfer.

### Subagent Launch Pattern

For each stage, the coordinator:

1. **Reads the previous stage artifact** to get inputs and handoff data
2. **Chooses the appropriate profile** based on model selection strategy
3. **Launches a subagent** using `Agent` with:
   - `prompt`: Specific stage task with workflow path and artifact locations
   - `description`: Stage-specific title for tracking
4. **Waits for completion** by reading the returned `Agent` result
5. **Reads the stage artifact** produced by the subagent
6. **Records the handoff** in `coordinator-log.md`
7. **Proceeds to next stage** or handles user interaction gates

### Subagent Task Structure

Each subagent task follows this pattern:

```text
Execute the Q-C-Code {stage} workflow located at ~/.claude/skills/qccode/workflows/{stage}/workflow.md
- Read the workflow.md manifest for execution steps and rules
- Execute workflow steps in order (sequential)
- Use the provided input artifact: {previous-stage-artifact-path}
- Write your output artifact to: {current-stage-artifact-path}
- Follow the workflow rules and output specifications
- Apply the model strategy: {model-choice}
- Return completion status when workflow is finished
```

### Model Selection Implementation

Based on user's model strategy choice:

- **Local model only**: All subagents use default model configuration
- **Adaptive selection**: Research, Design Discussion, Structure use premium models; Questions, Plan, Worktree, Implement use local model
- **Premium quality**: All subagents use best available models
- **Custom strategy**: User-specified model per stage

The coordinator records model choices in `coordinator-log.md` for transparency and debugging.

### Sequential Stage Execution

**Important**: All Q-C-Code stages execute sequentially. Each subagent must complete successfully before the next stage begins. This sequential execution ensures proper context control and artifact handoff.

Before moving from one stage to the next, run this quick check:

1. Did the current stage subagent complete successfully?
2. Is the stage artifact present and valid?
3. Did the current stage have a pause or review gate that was resolved?
4. Is the next stage's `Output for next stage` present and specific?
5. Are there any unresolved open questions that block the next stage?

If any answer is no, pause and address the issue before proceeding.

### 1. Questions Stage (Subagent)

**Subagent Task**: Launch a subagent to execute the Questions workflow.

**Coordinator Action**:
```text
Launch a Claude Code `Agent` with:
Task: "Execute the Q-C-Code Questions workflow located at ~/.claude/skills/qccode/workflows/questions/workflow.md
- Read the workflow.md manifest for execution steps and rules
- Execute workflow steps in order (sequential)
- Use the user request: {user-request}
- Write your output artifact to: {questions-artifact-path}
- Follow the workflow rules and output specifications
- Apply the model strategy: {model-choice-for-questions}
- Return completion status when workflow is finished"
```

**Subagent Workflow**: The Questions subagent runs its own workflow (`~/.claude/skills/qccode/workflows/questions/workflow.md`) which:

1. Analyzes the user request for ambiguity
2. Decides whether user alignment is needed
3. Writes 2-5 meaningful questions and suggested options into `questions.md` if user input is needed
4. After coordinator/user input is recorded, writes `questions.md` with feature intent, success criteria, research targets
5. Produces `Output for next stage` for the Research subagent

**Gate Handling**: The Questions subagent prepares the pause gate; the coordinator asks the user with `AskUserQuestion`, records the answer in `questions.md`, and then continues.

**Artifact Handoff**: After completion, coordinator reads `questions.md` and passes the research targets to the Research subagent.

**Anti-patterns**:
- Coordinator trying to handle Questions stage directly instead of using subagent
- Subagent asking too many questions or irrelevant ones
- Skipping user alignment when feature intent is unclear

### 2. Research Stage (Subagent)

**Subagent Task**: Launch a subagent to execute the Research workflow.

**Coordinator Action**:
```text
Launch a Claude Code `Agent` with:
Task: "Execute the Q-C-Code Research workflow located at ~/.claude/skills/qccode/workflows/research/workflow.md
- Read the workflow.md manifest for execution steps and rules
- Execute workflow steps in order (sequential)
- Use the input artifact: {questions-artifact-path}
- Write your output artifact to: {research-artifact-path}
- Follow the workflow rules and output specifications
- Apply the model strategy: {model-choice-for-research}
- Return completion status when workflow is finished"
```

**Subagent Workflow**: The Research subagent runs its own workflow (`~/.claude/skills/qccode/workflows/research/workflow.md`) which:

1. Reads `questions.md` for research targets
2. Inspects the codebase using Claude Code's search tools (grep, Glob, read)
3. Writes `research.md` with relevant files, patterns, constraints
4. Produces `Output for next stage` for the Design Discussion subagent
5. Pauses only if blocked or findings contradict the request

**Gate Handling**: Autonomous stage - subagent proceeds without user interaction unless blocked.

**Artifact Handoff**: After completion, coordinator reads `research.md` and passes constraints to the Design Discussion subagent.

**Anti-patterns**:
- Coordinator doing research directly instead of delegating to subagent
- Subagent designing solutions instead of gathering facts
- Subagent writing architecture opinions without file references

### 3. Design Discussion Stage (Subagent)

**Subagent Task**: Launch a subagent to execute the Design Discussion workflow.

**Coordinator Action**:
```text
Launch a Claude Code `Agent` with:
Task: "Execute the Q-C-Code Design Discussion workflow located at ~/.claude/skills/qccode/workflows/design-discussion/workflow.md
- Read the workflow.md manifest for execution steps and rules
- Execute workflow steps in order (sequential)
- Use the input artifact: {research-artifact-path}
- Write your output artifact to: {design-discussion-artifact-path}
- Follow the workflow rules and output specifications
- Apply the model strategy: {model-choice-for-design}
- Return completion status when workflow is finished"
```

**Subagent Workflow**: The Design Discussion subagent runs its own workflow (`~/.claude/skills/qccode/workflows/design-discussion/workflow.md`) which:

1. Reads `research.md` for facts and constraints
2. Forms engineering opinions based on research findings
3. Writes `design-discussion.md` with current state, desired end state, tradeoffs
4. Writes review-gate options when design alternatives exist
5. Produces `Output for next stage` for the Structure subagent

**Gate Handling**: Review gate - subagent prepares alternatives; the coordinator presents them with `AskUserQuestion` and records the decision.

**Artifact Handoff**: After completion, coordinator reads `design-discussion.md` and passes design constraints to the Structure subagent.

**Anti-patterns**:
- Coordinator making design decisions instead of delegating to subagent
- Subagent debating designs before Research is complete
- Subagent hiding tradeoffs or skipping review gates

### 4. Structure Outline Stage (Subagent)

**Subagent Task**: Launch a subagent to execute the Structure Outline workflow.

**Coordinator Action**:
```text
Launch a Claude Code `Agent` with:
Task: "Execute the Q-C-Code Structure Outline workflow located at ~/.claude/skills/qccode/workflows/structure/workflow.md
- Read the workflow.md manifest for execution steps and rules
- Execute workflow steps in order (sequential)
- Use the input artifact: {design-discussion-artifact-path}
- Write your output artifact to: {structure-artifact-path}
- Follow the workflow rules and output specifications
- Apply the model strategy: {model-choice-for-structure}
- Return completion status when workflow is finished"
```

**Subagent Workflow**: The Structure subagent runs its own workflow (`~/.claude/skills/qccode/workflows/structure/workflow.md`) which:

1. Reads `design-discussion.md` for design constraints
2. Defines execution shape, module boundaries, data flow
3. Writes `structure.md` with phases, dependencies, validation approach
4. Writes review-gate options when boundaries change significantly
5. Produces `Output for next stage` for the Plan subagent

**Gate Handling**: Review gate - subagent prepares structure options; the coordinator presents them with `AskUserQuestion` when changes are non-obvious or risky.

**Artifact Handoff**: After completion, coordinator reads `structure.md` and passes structure definition to the Plan subagent.

**Anti-patterns**:
- Coordinator defining structure instead of delegating to subagent
- Subagent creating unnecessary abstractions
- Subagent sneaking implementation details into structure phase

### 5. Plan Stage (Subagent)

**Subagent Task**: Launch a subagent to execute the Plan workflow.

**Coordinator Action**:
```text
Launch a Claude Code `Agent` with:
Task: "Execute the Q-C-Code Plan workflow located at ~/.claude/skills/qccode/workflows/plan/workflow.md
- Read the workflow.md manifest for execution steps and rules
- Execute workflow steps in order (sequential)
- Use the input artifact: {structure-artifact-path}
- Write your output artifact to: {plan-artifact-path}
- Follow the workflow rules and output specifications
- Apply the model strategy: {model-choice-for-plan}
- Return completion status when workflow is finished"
```

**Subagent Workflow**: The Plan subagent runs its own workflow (`~/.claude/skills/qccode/workflows/plan/workflow.md`) which:

1. Reads `structure.md` for structure definition
2. Converts structure into small implementation slices
3. Writes `plan.md` with ordered tasks, dependencies, validation expectations
4. Writes review-gate summary and numbered options
5. Produces `Output for next stage` for the Worktree subagent

**Gate Handling**: Review gate - subagent prepares the plan summary; the coordinator presents it with `AskUserQuestion` and gets approval before proceeding.

**Artifact Handoff**: After completion, coordinator reads `plan.md` and passes plan details to the Worktree subagent.

**Anti-patterns**:
- Coordinator creating plans instead of delegating to subagent
- Subagent producing giant plans with hidden surprises
- Subagent combining unrelated concerns into single tasks

### 6. Worktree / Execution Context Stage (Subagent)

**Subagent Task**: Launch a subagent to execute the Worktree workflow.

**Coordinator Action**:
```text
Launch a Claude Code `Agent` with:
Task: "Execute the Q-C-Code Worktree workflow located at ~/.claude/skills/qccode/workflows/worktree/workflow.md
- Read the workflow.md manifest for execution steps and rules
- Execute workflow steps in order (sequential)
- Use the input artifact: {plan-artifact-path}
- Write your output artifact to: {worktree-artifact-path}
- Follow the workflow rules and output specifications
- Apply the model strategy: {model-choice-for-worktree}
- Return completion status when workflow is finished"
```

**Subagent Workflow**: The Worktree subagent runs its own workflow (`~/.claude/skills/qccode/workflows/worktree/workflow.md`) which:

1. Reads `plan.md` for implementation tasks
2. Checks current git status and project conventions
3. Identifies execution policy (same workspace, branch, worktree, test-only)
4. Writes pause-gate options for branch/worktree policy
5. Sets up execution environment (branches, worktrees, setup commands)
6. Writes `worktree.md` with execution context and environment state
7. Produces `Output for next stage` for the Implement subagent

**Gate Handling**: Pause gate - subagent prepares options; the coordinator asks with `AskUserQuestion` before creating branches, worktrees, pushing, or merging.

**Artifact Handoff**: After completion, coordinator reads `worktree.md` and passes execution context to the Implement subagent.

**Anti-patterns**:
- Coordinator manipulating git state instead of delegating to subagent
- Subagent creating branches/worktrees without user approval
- Subagent starting implementation in dirty workspace

### 7. Implement Stage (Subagent)

**Subagent Task**: Launch a subagent to execute the Implement workflow.

**Coordinator Action**:
```text
Launch a Claude Code `Agent` with:
Task: "Execute the Q-C-Code Implement workflow located at ~/.claude/skills/qccode/workflows/implement/workflow.md
- Read the workflow.md manifest for execution steps and rules
- Execute workflow steps in order (sequential)
- Use the input artifacts: {worktree-artifact-path} and {plan-artifact-path}
- Write your output artifact to: {implementation-notes-artifact-path}
- Follow the workflow rules and output specifications
- Apply the model strategy: {model-choice-for-implement}
- Return completion status when workflow is finished"
```

**Subagent Workflow**: The Implement subagent runs its own workflow (`~/.claude/skills/qccode/workflows/implement/workflow.md`) which:

1. Reads `worktree.md` for execution context and `plan.md` for current slice
2. Uses Claude Code's tools (read, edit, exec, grep, Glob, TodoWrite)
3. Executes the approved implementation slice with smallest useful diff
4. Uses `TodoWrite` for task tracking during implementation
5. Pauses only for new scope, risk, failing assumptions, or plan changes
6. Writes `implementation-notes.md` when needed for context preservation
7. Produces completion status and any follow-up work needed

**Gate Handling**: Autonomous stage - subagent proceeds without user interaction unless blocked.

**Artifact Handoff**: After completion, coordinator reads `implementation-notes.md` and presents final results to user.

**Anti-patterns**:
- Coordinator doing implementation directly instead of delegating to subagent
- Subagent redesigning architecture during implementation
- Subagent expanding scope without user approval

## Optional Follow-Up

After Implement, optionally produce verification notes or a reconciliation summary if the user needs them. These are useful, but they are not part of the original seven-stage QRSPI sequence.

Summarize in chat, or write `verification.md` / `pr-summary.md` only when useful:

- what changed
- why it changed
- validation performed
- risks or follow-ups
- unresolved uncertainty
- reviewer focus areas

Anti-patterns:

- Repeating every prior artifact.
- Hiding risk to make the work look cleaner.
- Writing marketing copy instead of review guidance.
- Omitting failed, skipped, or unavailable validation.
- Claiming the scratch folder is long-term documentation.

## New User Explanation

When explaining Q-C-Code/QRSPI to someone new, keep it short:

- RPI says: research, plan, implement.
- Q-C-Code/QRSPI splits that thinking into smaller checkpoints.
- Questions prevents silent assumptions.
- Research grounds the work in the real code.
- Design Discussion decides the current state, desired end state, and guiding patterns.
- Structure Outline defines phase order and validation shape.
- Plan creates actionable steps from that structure.
- Worktree prepares a clean execution environment.
- Implement executes the change in a focused session.

Highlight Q-C-Code advantages:
- Hierarchical sub-agent architecture for focused stage execution
- Model selection strategy for cost-quality optimization
- Native tool integration for seamless code editing and navigation
- Built-in todo management for tracking implementation progress
- Interactive decision support via AskUserQuestion
- Persistent shell sessions for running tests and builds
- Context-aware file operations that understand project structure

## Author

Q-C-Code was created by Peter A. Moreno on May 28, 2026 as a Claude Code-specific adaptation of the QRSPI methodology.

## Claude Code-Specific Adaptations

Q-C-Code includes several adaptations for Claude Code's capabilities:

1. **Hierarchical Sub-Agent Architecture**: Each QRSPI stage runs as a dedicated Claude Code `Agent` with its own workflow.

2. **Model Selection Strategy**: User can choose between local-only, adaptive, premium, or custom model strategies for cost-quality optimization.

3. **Tool Integration**: References to Claude Code's specific tools (Read, Edit, Bash, PowerShell, Grep, Glob, TodoWrite, AskUserQuestion) instead of generic tool descriptions.

4. **Workspace Management**: Uses `.qccode/` for scratch artifacts, following Claude Code's configuration conventions.

5. **Interactive Decision Making**: The coordinator consistently uses `AskUserQuestion` with clickable buttons for all user interaction points, including menus, confirmations, and stage gates.

6. **Task Tracking**: Uses `TodoWrite` for managing implementation tasks and progress visibility.

7. **Shell Sessions**: Takes advantage of Claude Code's persistent shell sessions for running tests, builds, and setup commands.

8. **Context Awareness**: Leverages Claude Code's understanding of project structure and file relationships for more accurate navigation and editing.

9. **Security Integration**: Respects Claude Code's permission system and security rules for file operations and command execution.

These adaptations make Q-C-Code feel native to Claude Code while preserving the core QRSPI methodology's benefits of structured thinking and explicit checkpoints.
