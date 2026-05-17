# Execution Workflow

You are an AI agent driven by a file-based issue system. Follow this loop strictly:

## 1. The Core Loop (Priority Order)

1. **Check for Corrections (Highest Priority)**:
   If `docs/issues/issue_correction.md` exists, your ONLY task is to fix the reported issues. Once fixed, run `handover/scripts/submit_correction.sh` and end the session.

2. **Execute Open Issue**:
   Read `docs/issues/issue_open.md`. If a task is present:
   - **Analyze & Execute**: Perform the requested code, math, or doc updates.
   - **Check for "Human Approval Required"**:
     - If this label exists in the issue: Append your proposal to the `### Response` section of `issue_open.md` and **STOP**. Do NOT modify other files or create commits.
     - If NO approval is required and the task is fully complete: Proceed to **Phase 4**.

## 2. Phase 4: Completion Procedure

Only perform this if the task is finished and no human approval is pending:
1. Update checkboxes `[x]` and ensure the `### Response` section is filled in `issue_open.md`.
2. Move the completed issue content to `docs/issues/done/issue_YYMMDD_NN.md`.
3. Reset `issue_open.md` to its template state.
4. Update `docs/issues/issue_history.md` and `handover/handover_memo_latest.md`.
5. **Commit and Push** your changes to the current branch.
6. Run `handover/scripts/close_issue.sh` and end the session.
