[Step 4 of 8] Issue I04-1: Super Jacobi identity verification

## Context & Background
With structure constants generated in JSON format (step 3), verify that they
satisfy the Super Jacobi identity and anti-symmetry properties before
proceeding to Schema 2.

## Requirements
1. Implement a verification script (e.g., `src/verify_C_structure.py`) loading `C_1_structure.json`, `C_2_structure.json`, and `C_3_structure.json`.
2. Check anti-symmetry for all generator pairs.
3. Check the Super Jacobi identity for all generator triples.
4. Provide a summary report (pass/fail). If failures exist, provide root cause analysis.

## Deliverables
- Code: Python verification script in `src/`.
- Report: verification results given in your reply.

## Completion Criteria
- [ ] Verification script implemented.
- [ ] All generator triples checked for n=1, 2, 3.
- [ ] All checks pass, OR failures documented with root cause.

## Trust Boundary & Workflow Note
- **Human Approval Required**: Interpretation of verification failures and mathematical validity require human judgment. If the script fails, halt and work with the human to identify the root cause before proceeding.
- **Iterative Dialogue Expected**: Present verification results in your reply and halt for human review. **CRITICAL RULE**: Do NOT proceed until the human explicitly approves the verification results.
