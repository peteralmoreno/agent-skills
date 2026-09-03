# PRISM Spec Framework

> **One messy prompt in. Five clear engineering views out.**

PRISM is a lightweight spec framework for turning a vague or overloaded prompt into a clear, buildable, and verifiable specification.

```text
Messy Prompt
     |
     v
   PRISM
  / | | | \
 P  R I S  M
```

A prompt often mixes together the problem, expected behavior, constraints, solution ideas, and proof. PRISM separates those concerns before implementation begins.

## P — Problem

Describe why the work exists and where it applies.

Include:

- the current problem or opportunity;
- who or what is affected;
- the desired outcome;
- what is in scope;
- what is explicitly out of scope.

**Core question:** What are we solving, and where are the boundaries?

## R — Requirements

Define the observable behavior the solution must provide.

Use numbered references:

```text
R1. The system must...
R2. When the user...
R3. If the operation fails...
```

Requirements describe the promise made by the system, not the implementation used to fulfill it.

**Core question:** What must the system do?

## I — Invariants

Record the rules and guarantees that must remain true.

Examples include:

- security and tenant isolation;
- compatibility;
- performance limits;
- reliability and recovery;
- regulatory or business rules;
- architectural constraints.

```text
I1. Existing clients must remain compatible.
I2. Retrying a request must not duplicate completed work.
```

**Core question:** What must never be broken while solving the problem?

## S — Solution

Describe the selected solution shape and the consequential decisions behind it.

Include:

- the chosen approach;
- component responsibilities;
- data and state ownership;
- lifecycle or workflow;
- important alternatives;
- rationale and tradeoffs.

```text
S1. Persist progress under a stable operation ID.
S2. Use one coordinated processing lifecycle.
```

This is not a complete implementation plan. It captures the decisions needed to align implementation.

**Core question:** How have we chosen to satisfy the requirements?

## M — Measures

Define the evidence that will prove the solution works.

Measures may include:

- unit and integration tests;
- acceptance scenarios;
- benchmarks;
- commands and build results;
- demonstrations or screenshots;
- logs, traces, and production metrics.

```text
M1. Simulate a transient failure and verify recovery.
M2. Repeat an operation ID and verify no duplicate output.
```

**Core question:** What evidence will demonstrate success?

## Traceability

PRISM sections should connect:

```text
R3 — Retrying must not duplicate work.
I2 — Completed work must remain idempotent.
S1 — Use a stable operation ID.
M2 — Retry the same operation and verify one output.
```

A useful shorthand is:

> **R3 is protected by I2, implemented through S1, and verified by M2.**

## The Pitch

> **Don’t code the prompt. Pass it through PRISM.**

PRISM turns an ambiguous request into five explicit engineering views:

**Problem · Requirements · Invariants · Solution · Measures**

It is a scaffold, not a waterfall. Each section can evolve as the team learns, but implementation should always remain connected to an explicit problem, numbered requirements, protected invariants, deliberate solution choices, and measurable proof.
