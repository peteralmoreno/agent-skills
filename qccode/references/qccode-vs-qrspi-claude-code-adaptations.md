# Q-C-Code / QRSPI - Claude Code-Adapted Implementation

## From Generic QRSPI → Claude Code-Native QC-Code

The original QRSPI methodology (Questions → Research → Design Discussion → Structure → Plan → Worktree → Implement) provides a robust cognitive framework for AI-assisted engineering. QC-Code adapts this methodology specifically for Claude Code's capabilities and workflow.

## Claude Code-Specific Adaptations

### Tool Integration

Claude Code's native tool set is deeply integrated into each QC-Code stage:

| Stage | Claude Code Tools Used |
|---|---|
| Questions | `AskUserQuestion` for structured decision gathering |
| Research | `Grep`, `Glob`, `Read` for codebase exploration |
| Design Discussion | `Read` for inspecting patterns, `AskUserQuestion` for tradeoff decisions |
| Structure | `Read` for understanding module boundaries |
| Plan | `TodoWrite` for task breakdown and dependency mapping |
| Worktree | `Bash` / `PowerShell` for git operations and environment setup |
| Implement | `Edit`, `Bash` / `PowerShell`, `TodoWrite` for focused implementation |

### Workspace Management

**Generic QRSPI**: Uses `.qcode/active/` for scratch artifacts

**QC-Code**: Uses `.qccode/active/` for scratch artifacts, providing tool-agnostic artifact storage that works across different AI tools and IDEs.

### Interactive Decision Making

Claude Code's `AskUserQuestion` tool provides structured, multi-option decision points that enhance the QRSPI gate system:

- **Pause Gates**: Present clear numbered options for user decisions
- **Review Gates**: Show compact tables with tradeoffs and recommendations
- **Autonomous Stages**: Proceed without interruption when appropriate

### Task Tracking

The `TodoWrite` tool provides real-time progress visibility:

- Automatic task state management (pending → in_progress → completed)
- Clear progress indication for both user and agent
- Natural fit for QRSPI's slice-based implementation approach

### Shell Session Management

Claude Code's persistent shell sessions enhance several stages:

- **Research**: Run commands to understand runtime behavior
- **Worktree**: Execute git operations, setup scripts, environment initialization
- **Implement**: Run tests, builds, and validation in consistent environments
- **Follow-up**: Execute verification and reconciliation commands

### Context-Aware Operations

Claude Code's understanding of project structure improves navigation and editing:

- Intelligent file suggestions during Research
- Context-aware edit operations that respect project patterns
- Automatic detection of project conventions (package managers, test frameworks, etc.)

## Enhanced Artifact Structure

QC-Code maintains the QRSPI artifact chain with Claude Code-specific enhancements:

```text
questions.md        → Enhanced with AskUserQuestion integration
research.md         → Leverages Claude Code's search tools for precise file references
design-discussion.md → Uses structured decision presentation
structure.md        → Includes Claude Code-specific module boundary detection
plan.md             → Integrates with TodoWrite for task management
worktree.md         → Enhanced with shell session management
implementation-notes.md → Tracks tool usage and command execution patterns
```

## Security and Permission Integration

QC-Code respects Claude Code's security model:

- File operations follow Claude Code's permission rules
- Destructive operations require explicit confirmation
- Workspace boundaries are enforced
- Secret and credential handling follows Claude Code's security guidelines

## Workflow Advantages

### Compared to Generic QRSPI

| Aspect | Generic QRSPI | QC-Code |
|---|---|---|
| Tool Integration | Abstract tool references | Specific Claude Code tool calls |
| Decision Making | Text-based prompts | Structured multi-option questions |
| Task Tracking | Manual or external | Native TodoWrite integration |
| Shell Operations | One-off commands | Persistent sessions with state |
| File Operations | Generic read/write | Context-aware operations |
| Security | Generic guidelines | Claude Code-specific permission model |
| Workspace | Custom paths | Claude Code configuration conventions |

### Practical Benefits

1. **Faster Execution**: Native tool integration reduces overhead
2. **Better Progress Visibility**: TodoWrite provides real-time status
3. **Improved Decision Quality**: Structured questions lead to clearer choices
4. **Consistent Environments**: Persistent shell sessions ensure reproducibility
5. **Security Compliance**: Built-in permission and security rule adherence
6. **Context Preservation**: Claude Code's context management reduces information loss

## The Core Philosophy Remains

Despite these adaptations, QC-Code preserves the fundamental QRSPI insight:

> AI reliability improves more from reducing cognitive jump size than from increasing model intelligence.

The Claude Code adaptations simply make this philosophy more practical and powerful within Claude Code's specific environment.

## Usage Example

When you invoke QC-Code for a feature:

1. **Questions**: Claude Code uses `AskUserQuestion` to gather 2-5 key decisions
2. **Research**: Claude Code uses `Grep`, `Glob`, `Read` to explore the codebase
3. **Design Discussion**: Claude Code presents tradeoffs using structured tables and recommendations
4. **Structure**: Claude Code outlines phases using context-aware module understanding
5. **Plan**: Claude Code creates tasks with `TodoWrite` for clear progress tracking
6. **Worktree**: Claude Code sets up execution environment using persistent shell sessions
7. **Implement**: Claude Code executes changes using `Edit`, `Bash` / `PowerShell`, and `TodoWrite` with real-time progress

Each stage leverages Claude Code's specific strengths while maintaining the cognitive discipline of QRSPI.