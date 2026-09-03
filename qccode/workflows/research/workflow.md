# Q-C-Code Research Workflow

## Purpose
Ground the task in the actual system by inspecting the codebase, understanding patterns, and identifying constraints.

## Steps
1. **01-read-questions.md** – Read questions.md to understand research targets and what needs to be investigated
2. **02-inspect-codebase.md** – Use Claude Code's search tools to inspect relevant files, patterns, and dependencies
3. **03-write-artifact.md** – Write research.md with findings, constraints, and facts for Structure stage

## Triggered By
Completion of questions.md with a populated `Output for next stage` section.

## Required Input
- `questions.md` — with research targets from Questions stage

## Optional Input
- Any linked files, issues, or tickets mentioned in the user request

## Output
- `research.md` — with relevant files, patterns, constraints, and `Output for next stage`

## Gates
No user gate required. Autonomous stage — pause only if blocked or findings contradict the request.

## Rules
- **Autonomous stage**: Proceed without user interaction unless blocked or findings contradict the request
- Use Claude Code's search tools: `Grep`, `Glob`, `Read` for codebase exploration
- Focus on research targets from questions.md — avoid broad repository sightseeing
- Write research.md with: relevant files, existing patterns, dependencies, constraints, risks, reuse opportunities
- Answer research targets from questions.md specifically
- Produce `Output for next stage`: constraints and facts that Design Discussion must preserve
- Do not design the solution in this stage — focus on gathering facts

## Failure Behavior
- If required files or systems cannot be found: write a blocker note in research.md and return to coordinator.
- If findings contradict the user's request: write the contradiction clearly in research.md and return to coordinator for user input.
- Do not guess at missing information — document the gap.

## Must Not
- Do not design or architect solutions in this stage.
- Do not write architecture opinions without file references.
- Do not summarize the entire codebase — only what is relevant to research targets.
- Do not use `AskUserQuestion` — surface blockers by returning to coordinator with a note in the artifact.
- Do not modify source code.