# Execution Workflow

You are an AI agent driven by a file-based issue system. Follow this loop strictly:

## 1. The Core Loop (Priority Order)

1. **Check for Corrections (Highest Priority)**:
   If `docs/issues/issue_correction.md` exists, your ONLY task is to fix the reported issues. Once fixed, run the following script and end the session:
   `./handover/scripts/submit_correction.sh`

2. **Execute Open Issue**:
   Read `docs/issues/issue_open.md`. If a task is present:
   - **Analyze & Execute**: Perform the requested code, math, or doc updates.
   - **Check for "Human Approval Required"**:
     - If this label exists in the issue: Append your proposal to the `### Response` section of `issue_open.md` and **STOP**. Do NOT modify other files or create commits.
     - If NO approval is required and the task is fully complete: Proceed to **Phase 4**.

## 2. Phase 4: Completion Procedure

Only perform this if the task is finished and no human approval is pending:
1. Update checkboxes `[x]` and ensure the `### Response` section is filled in `issue_open.md`.
2. Determine these 4 values:
   - `YYMMDD`: Today's date (e.g., 260517)
   - `NN`: Current issue number (e.g., 01)
   - `LABEL`: A short commit message (e.g., "I01-1: Define C(n+1) basis")
   - `NEXT`: The next issue number (e.g., 02)
3. Run the completion script with these values:
   `./handover/scripts/close_issue.sh <YYMMDD> <NN> "<LABEL>" <NEXT>`
   
   **NOTE**: This script will automatically:
   - Archive the issue to `docs/issues/done/`
   - Reset `issue_open.md`
   - Stage, commit, and push all your changes to the current branch.
   - Create a completion marker.
4. End the session.
