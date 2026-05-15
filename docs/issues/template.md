# Issue Template Definition

## Issue Numbering Scheme

- **Serial numbers**: `I{NN}-{n}` format (NN: 2-digit issue number, n: sub-issue number)
  - Example: `I08-1`, `I08-2`, `I09-1`
- **Theme separation**: Different themes have different issue numbers
  - Example: I08-1, I08-2 are one theme → next theme is I09-1
- **Multiple themes in one file**: Separate with `---` (horizontal rule). The AI processes each theme sequentially, completing Phase 4 for each before moving to the next
- **Template**: `template_issue_open.md` contains `{NN}` placeholder. Replace with the actual number when copying

### Multi-Issue Operating Rules

1. Read `issue_open.md` and confirm the number of issues
2. Work on each issue (theme) sequentially (complete Phase 4 to finalize each independently)
3. If an error occurs during work: leave completed issues as-is, do not enter the next issue, and terminate

## Issue File Schema

### Structure

```markdown
# Issue {ID}: {Title}

**Date**: YYYY-MM-DD
**Status**: open | needs_clarification | done
**Category**: [category]
**Theme Working Branch**: [branch]
```

### Background
[Motivation and context for this issue]

### Requirements
[Specific work to be done]

### Supplementary Information

#### Deliverable Format
{document / schema / code / decision / script}

#### Related Folders/Files
- {relative path from repository root}

#### Related Issues
{e.g., I07-3, or "none"}

### Completion Criteria
- [ ] Criterion 1 (aim for 3–5 items)
- [ ] Criterion 2
```

Minimal structure (Background, Requirements, Completion Criteria may be omitted):

```markdown
## I01-1. Title

Body
```

### Multiple Themes

Separate different themes with `---` (horizontal rule) and increment the issue number:

```markdown
## I08-1. Theme A

...

---

## I09-1. Theme B

...
```

The AI processes each theme sequentially, completing Phase 4 for each before moving to the next.

### Response Section (Added by AI after completion)

```markdown
### Response

[Response content]
```

### Cross-cutting Supplementary Section (Optional)

For notes that apply across multiple items, add after the last item:

```markdown
## Supplementary

[Notes applicable to multiple items]
```

## Issue Design Guidelines

- **One theme per issue**: Consider splitting if sub-issues exceed 3
- **Completion criteria**: Aim for 3–5 items. Include **only work items**, not Phase 4 procedures (archiving, close_issue.sh execution, etc.)
- **Explicit deliverable format**: State the expected form (document / schema / code / decision / script)
- **Declare dependencies**: Specify prerequisite issues in "Related Issues"

## Category Labels

| Category | Scope |
|----------|-------|
| `verification` | Verification of computation results and logic |
| `research` | Investigation and direction proposals |
| `proposal` | Policy and design proposals |
| `implementation` | Code implementation and fixes |
| `paper` | Paper content and structure |
| `docs` | Documentation in general |
| `workflow` | Workflow and operational methods |

<!-- CUSTOMIZE: Add or modify categories according to your project -->

## Completed File Naming Convention

```
done/issue_YYMMDD_NN.md
```

- `YYMMDD`: creation date (6 digits)
- `NN`: sequential number within the same day (2-digit zero-padded)

## Phase 4 (Completion Process)

1. Update completion criteria checkboxes to `[x]` and add `### Response` section per item
2. Copy to `docs/issues/done/issue_YYMMDD_NN.md`
3. Reset `issue_open.md` by copying `template_issue_open.md` (replace `{NN}` with the next number)
4. Add a record to `docs/issues/issue_history.md`
5. Add deliverables to `docs/issues/artifact_index.md`
6. Update `handover/handover_memo_latest.md`
7. Git completion: commit → push → squash merge to main → sync branch

> **Script**: Automate with `handover/scripts/close_issue.sh`
> **Note**: Completion criteria should contain only work items. Do not include Phase 4 procedure steps (items 1–7 above)

Post-completion branch state:
- **main**: squash commit
- **ai/workflow_issue**: synced with main via `git reset --hard main && git push --force-with-lease`
- **issue_open.md**: template state on both branches
