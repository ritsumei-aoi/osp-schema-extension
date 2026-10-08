# Prompt Pack: Start

Prompt collection for starting the next session.

## Prompt 0: Session Start

```markdown
# <YYYY-MM-DD> Handover Session

## 0. Introduction

We will now attach the necessary information in this thread. Instructions will be given in the following order:

- 1. Paper and work overview
- 2. Current status and goal setting
- 3. Workflow rules confirmation

Please follow the "Your task here" instructions in each step.
You may ask questions at any point if something is unclear.
When ready, respond with "Please proceed to the next step."
```

## Prompt 1: Paper Confirmation

<!-- CUSTOMIZE: Replace with your project's reference paper/resource -->

```markdown
## 1. Paper and Work Overview

### Reference Paper
<!-- CUSTOMIZE: Describe your reference paper or resource -->
The attached **`<reference-file>`** is the focus of this session's work.

### Project Purpose
<!-- CUSTOMIZE: Describe your project's purpose -->

### Your Task Here

Review the above materials and understand the project's key definitions and structure.

When finished, respond with "Materials reviewed. Please proceed to the next step."
```

## Prompt 2: Goal Setting

```markdown
## 2. Current Status and Goal Setting

### 2.1 Current Status

The files we are creating belong to the following GitHub repository:

<!-- CUSTOMIZE: Update with your repository information -->
- owner: `your-github-username`
- repo: `your-repo-name`

You can retrieve files from here via the MCP server. However, you cannot write files or perform Git operations.
Start with the following:
- `handover/README.md`: overview of handover information
- `handover/handover_memo_latest.md`: memo from the previous session
Retrieve these from the MCP server and review the file structure. You may also retrieve other files listed here later via the MCP server.

### Status Check
Review the above two files from the MCP server, understand the current status, and provide a summary. Goals and specific next steps for this session will be addressed in subsequent steps.
```

```markdown
### 2.2 Goal Setting

Review the previously loaded
**`handover/handover_memo_latest.md`** to understand the current implementation status and next steps:

**Items to check**:
- **Current Status**: last update date and progress summary
- **Implementation Roadmap**: completed and pending steps
- **🔄 Handover to Next Session**: specific tasks from the previous session

### Session Goals (Draft)

**Placeholder (describe specific goals below)**:
<session-goals>

**Default**: If the above is blank, proceed with the work described in the "🔄 Handover to Next Session" section of `handover_memo_latest.md`.

### Your Task Here

Based on this information, review and organize the "Session Goals (Draft)" and verify their feasibility.
Suggest modifications if needed. Ask if anything is unclear.
The actual approach will be presented after the goals are finalized.
```

## Prompt 3: Workflow Confirmation

```markdown
## 3. Workflow Rules Confirmation

### Workflow and Update Rules

Retrieve the following from the MCP server to understand the workflow and document update rules:

- `handover/workflow_common.md`
- `handover/workflow_method_a.md` (interactive) or `handover/workflow_method_b.md` (AI agent)
- `handover/session_protocol_method_a.md` (Method A details)
- `handover_memo_format.md`

**Items to check**:
- **Method A / Method B**: workflow for the method in use
- **Branch naming convention**: `ai/<YYYY-MM-DD>-<topic>`
- **Handover Memo Rules**: latest/archived split structure, update timing, template structure
- **Session End Checklist**: items to check at session end

### Your Task Here

- Read the above files and confirm the workflow rules
- Determine the temporary branch name in `ai/<YYYY-MM-DD>-<topic>` format and output the following:
  1. Branch name
  2. Branch creation command (e.g., `git checkout -b ai/2026-03-03-topic-name`)

The approach for this session will be proposed in the next step.
```
