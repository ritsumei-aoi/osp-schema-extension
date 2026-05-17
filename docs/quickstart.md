# Quick Start: Issue-Driven Research Workflow from Scratch

This guide explains how to set up a new AI-assisted research project using the
[Issue-Driven Research Workflow](https://github.com/ritsumei-aoi/ai-research-workflow-template)
from an empty state.

## Prerequisites

- Git installed and configured
- An AI assistant with direct file access (e.g., GitHub Copilot Chat in agent mode, Gemini CLI)
- A GitHub account (for public repository hosting)

## Step 1: Create a Repository from the Template

1. Go to [ai-research-workflow-template](https://github.com/ritsumei-aoi/ai-research-workflow-template)
2. Click **"Use this template" → "Create a new repository"**
3. Set the repository name (e.g., `osp-schema-extension`)
4. Set visibility to **Public**
5. Clone the repository locally:
   ```bash
   git clone https://github.com/<your-org>/<repo-name>.git
   cd <repo-name>
   ```

## Step 2: Choose Language and Copy Workflow Files

The template provides documentation in both English (`en/`) and Japanese (`ja/`).

```bash
# Example: use English documentation
cp -r en/handover/ handover/
cp en/CUSTOMIZE.md CUSTOMIZE.md
```

Or follow the instructions in `en/quickstart.md` (or `ja/quickstart.md`).

## Step 3: Configure AI Trust Policy

Edit `handover/ai_trust_policy.md` to define your project's delegation boundaries.

**What AI CAN do** (examples):
- Implement algorithms from specifications
- Generate and run test code
- Create documentation drafts
- Execute Git operations

**What AI CANNOT do** (examples):
- Make final judgments on mathematical correctness
- Decide proof strategies
- Approve schema designs
- Make submission decisions

## Step 4: Initialize Handover State

Edit `handover/handover_memo_latest.md` to record:
- Project name and goals
- Current status (empty / initial)
- Implementation roadmap (planned milestones)

## Step 5: Create Your First Issue

Create a file in `docs/issues/` following this structure:

```markdown
# Issue: <Title>

- **Created**: YYYY-MM-DD
- **Status**: open
- **Category**: <design | implementation | verification | documentation>
- **Priority**: <high | medium | low>

## Items

1. [Instruction] <What needs to be done>
2. [Question] <What needs to be clarified>
3. [Confirmation] <What needs to be verified>

## Responses

(AI fills this section during the session)
```

## Step 6: Start an AI Session (Method B)

1. Create a session branch:
   ```bash
   git checkout -b ai/<YYYY-MM-DD>-<topic>
   ```

2. Point the AI to the issue file and handover documents.

3. The AI reads context, confirms understanding, and begins work.

4. At session end:
   - Run tests (if any): `pytest tests/ -v`
   - Update `handover/handover_memo_latest.md`
   - Commit and push the branch

5. When the milestone is complete:
   ```bash
   git checkout main
   git merge --squash ai/<YYYY-MM-DD>-<topic>
   git commit -m "Squash merge: <summary of milestone>"
   git push
   ```

## Step 7: Iterate

Repeat Steps 5–6 for each issue cycle. The workflow maintains continuity
through handover documents and issue files, not through AI session memory.

## Key Principles

| Principle | What it means in practice |
|---|---|
| **Pre-planning** | Write the plan before implementing. AI proposes, human approves. |
| **Contextual Continuity** | Handover files carry context across sessions. AI has no memory. |
| **Issue-Driven** | Every task is a structured issue file, not a verbal instruction. |
| **Separation of Exploration and Verification** | AI explores and generates. Human selects and validates. |

## Differences from the Original oscillator-lie-superalgebras Workflow

This quickstart is adapted from the workflow used in the
[oscillator-lie-superalgebras](https://github.com/ritsumei-aoi/osp-triviality)
project. Key simplifications for new users:

| Aspect | Original project | This guide |
|---|---|---|
| Handover structure | 3-layer (latest, archived, next-session) | 1-layer (latest only) to start |
| Issue workflow | Integrated with review-driven workflow | Standalone issue files |
| Schema management | 4-layer JSON with v1–v5 evolution | Start with a single schema version |
| Session methods | Method A, B, C, D | Method B only |

As your project grows, you can adopt additional layers from the template.

## Metrics Collection (for Research Use)

If you are using this workflow as part of a research study, pre-define your
metrics before starting. See `STUDY_PROTOCOL.md` for the measurement protocol
used in this prospective case study.
