[Step 6 of 8] Issue I06-1: Layer 3: Evaluated structure for C(n+1)

## Context & Background
With the symbolic gamma structure (Layer 2) completed in step 5, proceed to
construct the Evaluated Structure (Layer 3). This involves substituting
concrete signs into the $gb$ matrix parameters.

## Requirements
1. Define a representative assignment for the 4n deformation parameters $gb$ (e.g., all set to +1 or representative sign profiles).
2. Implement a substitution script to generate `C_{n}_evaluated.json` for n=1, 2, 3.
3. Ensure the output JSON adheres to the Schema 3 (Evaluated Structure) format.

## Deliverables
- Code: Substitution/evaluation script.
- Data: Schema 3 JSON files in `data/`.

## Completion Criteria
- [ ] Evaluation script implemented.
- [ ] Schema 3 JSON generated for n=1, 2, 3.
- [ ] Data consistency with Schema 2 verified.

## Trust Boundary & Workflow Note
- **Human Approval Required**: The choice of representative $gb$ sign profiles requires human approval.
- **Iterative Dialogue Expected**: Propose your assignment plan and halt. **CRITICAL RULE**: Do NOT generate JSON until the human approves the sign profile.
