# Q-C-Code Design Discussion Workflow

## Purpose
Make the highest-leverage design choices explicit before outlining phases by documenting current state, desired end state, patterns, and tradeoffs.

## Steps
1. **01-read-research.md** – Read research.md to understand constraints and facts about the current system
2. **02-formulate-design.md** – Formulate design options based on research findings and desired end state
3. **03-present-options.md** – Prepare design options for coordinator approval with `AskUserQuestion` (if alternatives exist)
4. **04-write-artifact.md** – Write design-discussion.md with current state, desired end state, and recommended design

## Triggered By
Completion of research.md with a populated `Output for next stage` section.

## Required Input
- `research.md` — with constraints and facts from Research stage

## Optional Input
- `questions.md` — for original user intent when design needs clarification

## Output
- `design-discussion.md` — with current state, desired end state, design decisions, and `Output for next stage`

## Gates
Review gate: If real design alternatives exist, step 03 writes a `User-facing checkpoint` to the artifact and returns. The coordinator presents the options with `AskUserQuestion` and records the decision under `User checkpoint response`. The coordinator then relaunches Design Discussion to complete step 04.

If design is obvious and low-risk, step 03 is skipped and step 04 proceeds without user interaction.

## Rules
- **Review gate**: If there are real design alternatives, summarize options and recommend one before continuing
- If the design is obvious and low-risk, record the recommendation and continue without user interaction
- Form engineering opinions only from facts gathered in Research stage
- Write design-discussion.md with: current state, desired end state, patterns, options considered, tradeoffs, recommended design
- Produce `Output for next stage`: design constraints that Structure Outline must preserve

## Failure Behavior
- If research.md is missing or too vague to form any design opinion: return to Research stage.
- If design alternatives exist but cannot be evaluated without user input: write the User-facing checkpoint and return to coordinator.
- Do not guess at missing constraints — document the gap.

## Must Not
- Do not use `AskUserQuestion` directly — the coordinator does this.
- Do not debate design before Research is complete.
- Do not hide tradeoffs or risks.
- Do not propose patterns that don't exist in the codebase.
- Do not modify source code.
