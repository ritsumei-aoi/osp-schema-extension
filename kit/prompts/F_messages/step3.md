[Step 3 of 8] Issue I03-1: C(n+1) structure constant generator

## Context & Background
With the basis, PBW ordering (step 1), and Schema 1 specification (step 2) finalized,
implement the Python generator scripts to compute structure constants and output
them as JSON for n=1, 2, 3.

## Requirements
1. Implement a Python script (e.g., `src/C_generators.py`) to build the C(n+1) basis following the PBW ordering agreed in step 1.
2. Implement the structure constant generator using the defined oscillator relations.
3. Output results as `C_1_structure.json`, `C_2_structure.json`, `C_3_structure.json` in `data/`.
4. Add unit tests for parity, generator counts, and consistency.

## Deliverables
- Code: Python generator script in `src/` and tests in `tests/`.
- Data: JSON files in `data/`.

## Completion Criteria
- [ ] Generator functions implemented and tested.
- [ ] Schema 1 JSON generated for n=1, 2, 3.
- [ ] Tests pass for all three values of n.
- [ ] Structure constants conform to `json_schema_specification.md`.

## Trust Boundary & Workflow Note
- **Human Approval Required**: Mathematical validation of the implementation logic and test results requires human judgment.
- **Iterative Dialogue Expected**: Propose the script implementation and initial test results. **CRITICAL RULE**: Do NOT finalize the code or generate the final JSON files until the human explicitly approves the implementation and test results.
