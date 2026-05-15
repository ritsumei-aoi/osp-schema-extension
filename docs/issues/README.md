# docs/issues — Issue Management

## Overview

This directory records issue reports and responses for research deliverables.
It functions as the core component of Method B (Issue-Driven Agent Workflow).

## Operational Flow

```
1. User directly edits issue_open.md to add items
2. AI checks issue_open.md content → begins handling if items exist
3. Completed → copy to done/issue_YYMMDD_NN.md
4. Overwrite issue_open.md with template_issue_open.md (reset to template state)
5. Returned → create issue_needs_clarification.md
```

### Determination by File State

| File | Meaning |
|------|---------|
| `issue_open.md` (has items) | Unhandled issues exist → AI begins handling |
| `issue_open.md` (template state) | No issues to handle |
| `issue_needs_clarification.md` | Returned issues exist → awaiting additional instructions from user (top priority) |

> Template state determination: if the title of `## I{N}.` remains `{Title}`, it is in template state.

## File Structure

```
docs/issues/
├── issue_open.md                 # Issue file (always present)
├── issue_needs_clarification.md  # Returned issues (present only when needed)
├── template.md                    # Schema definition
├── template_issue_open.md        # Blank template for issue_open.md
├── issue_history.md              # Full issue response history
├── README.md                      # This file
└── done/                          # Completed issues
    └── issue_YYMMDD_NN.md        # Completed files
```

## Category Labels

<!-- CUSTOMIZE: Add or modify categories according to your project -->

| Category | Scope |
|----------|-------|
| `verification` | Verification of computation results and logic |
| `research` | Investigation and direction proposals |
| `proposal` | Policy and design proposals |
| `implementation` | Code implementation and fixes |
| `paper` | Paper content and structure |
| `docs` | Documentation in general |
| `workflow` | Workflow and operational methods |

## Completed Issues List

| File | Category | Response Commit |
|------|----------|----------------|
| <!-- entries will be added here --> | | |

## Related Files

- [`template.md`](template.md): schema definition
- [`template_issue_open.md`](template_issue_open.md): blank template for `issue_open.md`
- [`issue_history.md`](issue_history.md): response history (summary of all issues)
- [`../../handover/workflow_method_b.md`](../../handover/workflow_method_b.md): Method B workflow definition
- [`../../../samples/docs/issues/done/`](../../../samples/docs/issues/done/): sample completed issues
