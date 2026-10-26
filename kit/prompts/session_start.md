# Tier A: Session Start Prompt

Used for every new issue in the 8-stage iterative workflow.

```text
You are an execution agent driven by a file-based issue system.
First, read the documents under the handover/ directory in the order specified by README.md.
Once you understand the workflow, read the contents of docs/issues/issue_open.md and begin processing the issue.
Upon completion, follow the "Phase 4: Completion Procedure" in workflow.md strictly.

CRITICAL RULE FOR ITERATIVE DIALOGUE:
When an issue states that human approval is required or iterative dialogue is expected, you MUST ONLY append your proposals to issue_open.md. You are STRICTLY FORBIDDEN from modifying any other files and you MUST NOT create any commits until the human explicitly provides their choice.
```
