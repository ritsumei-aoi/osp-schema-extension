# AI Workflow — Method B (AI Agent with Direct Execution)

Method B is the default workflow for this project. The AI agent has direct access
to the local filesystem and shell (e.g., GitHub Copilot Chat in agent mode,
Gemini CLI).

Common rules (branching, handover, file governance, checklists) are defined in
[workflow_common.md](workflow_common.md).

## Required Reading Order (Session Start)

1. [workflow_common.md](workflow_common.md) (common rules)
2. [workflow_method_b.md](workflow_method_b.md) (this file)
3. [handover_memo_latest.md](handover_memo_latest.md) (current project state)
4. [notation.md](notation.md) (notation rules)
5. [../ai_trust_policy.md](../ai_trust_policy.md) (delegation boundaries)

## Execution Modes

### Default Mode (Execute)

The AI agent reads, writes, and executes directly. The following operations
**require user confirmation before execution**:

- Destructive or hard-to-reverse operations: `git reset --hard`, `git push --force`,
  deleting untracked files, dropping data, etc.
- In these cases: present a plan and wait for explicit user approval.

### Verification-Only Mode

Activated when the user says "analysis only", "do not implement", etc.

- AI performs read-only operations: code search, file reads, test runs.
- No file writes, no git state changes.
- Stays active until the user explicitly returns to default mode.

## Core Execution Cycle

**Research → Strategy → Execute**

1. **Research**: Map the codebase and validate assumptions before making changes.
2. **Strategy**: Present a concise implementation plan before execution.
3. **Execute — Plan → Act → Validate**:
   - Plan: define implementation and test strategy per sub-task.
   - Act: apply surgical changes. Prefer editing existing files over creating new ones.
   - Validate: run tests and linters. Validation is mandatory before session closure.

## Git Workflow

1. **Branch**: Create `ai/<YYYY-MM-DD>-<topic>` at session start.
2. **Commit**: Commit at natural milestones.
3. **Push**: AI executes `git push`. If a credential prompt appears, control
   passes to the user.
4. **Squash merge**: See workflow_common.md Branching Policy.

## Session End

Before finishing, the agent must:

1. Update `handover_memo_latest.md`.
2. Verify all tests pass.
3. Update `metrics/session_log.csv` with session data.
4. Prepare squash merge if a milestone is complete.

See [workflow_common.md](workflow_common.md) for the full checklist.
