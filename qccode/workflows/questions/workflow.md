# Q-C-Code Questions Workflow

## Purpose
Expose ambiguity before research or implementation by asking meaningful clarifying questions and defining the feature intent.

## Steps
1. **01-analyze-request.md** – Analyze the user request for ambiguity and decide whether user alignment is needed
2. **02-ask-questions.md** – Ask 2-5 meaningful questions using structured decision gathering (if needed)
3. **03-write-artifact.md** – Write questions.md with feature intent, success criteria, and research targets

## Triggered By
Coordinator launching the Questions stage with the user request (new run) or an existing questions.md artifact with a `User checkpoint response` section (resume after user answered questions).

## Required Input
- User request (provided by coordinator)

## Optional Input
- Linked issue, ticket, or notes if provided
- Existing questions.md if resuming with user-recorded answers

## Output
- `questions.md` – with feature intent, success criteria, research targets, and `Output for next stage`

## Gates
Pause gate: Step 02 writes a `User-facing checkpoint` to the artifact and returns. The coordinator asks the user with `AskUserQuestion` and records the answer under `User checkpoint response`. The coordinator then relaunches the Questions subagent to complete step 03.

## Rules
- **Pause gate**: Prepare 2-5 meaningful clarifying questions and options for the coordinator to ask with `AskUserQuestion`
- Skip the pause only when the request already gives enough intent, success criteria, state expectations, and constraints
- For feature ideas that imply code changes, default to asking at least one user-facing question
- Group questions around decisions that would change the implementation (user experience, smallest version, state persistence, API shape, success criteria, constraints)
- If some assumptions are safe, state them briefly and ask only for parts that affect direction
- Write questions.md with: feature intent, user goal, success criteria, non-goals, smallest useful version, open questions, risky assumptions, research targets
- Keep the artifact brief; do not paste the whole user conversation
- If user doesn't answer every question, record remaining open questions and continue only when next step is still useful and low-risk
- Produce `Output for next stage`: the exact research targets to investigate

## Failure Behavior
- If the user request is too vague to even formulate questions: write a single broad question asking for the feature description, then return to coordinator.
- If resuming and `User checkpoint response` is present but incomplete: carry unanswered questions as open questions in questions.md and continue.

## Must Not
- Do not use `AskUserQuestion` directly — the coordinator does this.
- Do not design the solution during the Questions stage.
- Do not ask more than 5 questions — focus on decisions that would change implementation.
- Do not silently assume business behavior that should be confirmed.
- Do not paste the entire user conversation into the artifact.
