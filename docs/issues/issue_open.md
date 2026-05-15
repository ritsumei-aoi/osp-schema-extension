# Issue I03-1: C(n+1) structure constant generator

**Date**: 2026-05-15
**Status**: open
**Category**: implementation
**Theme Working Branch**: ai/t1-schema-extension

## Context & Background
Now that the basis, PBW ordering (I01-1), and Schema 1 specification (I02-1) have been finalized for C(n+1) = osp(2|2n), we need to implement the Python generator scripts to compute and output the structural constants in the defined JSON format for n=1, 2, 3.

## Requirements
1. Implement a Python script (e.g., `src/C_generators.py`) to build the C(n+1) basis following the PBW ordering defined in `handover/notation.md`.
2. Implement the structure constant generator using the defined oscillator relations.
3. Output the results as `C_1_structure.json`, `C_2_structure.json`, and `C_3_structure.json` in the `data/` folder.
4. Add basic unit tests for parity, generator counts, and consistency.

## Deliverables
- Code (Python generator script in `src/` and tests in `tests/`)
- Data (JSON files in `data/`)

## Completion Criteria
- [ ] Generator functions implemented and tested.
- [ ] Schema 1 JSON generated for n=1, 2, 3.
- [ ] Tests pass for all three values of n.
- [ ] Structure constants conform to the `json_schema_specification.md` design.

## Trust Boundary & Workflow Note
- **Human Approval Required**: You must present the script logic and the output of the tests to the human for mathematical validation.
- **Iterative Dialogue Expected**: Please propose the script implementation in the response section. **CRITICAL RULE**: Do NOT commit the code or generate the final JSON files, and do NOT proceed to Phase 4 until the human explicitly approves your implementation.

---
### Response

*(AI Agent: Please append your proposals, analysis, and execution logs here.)*
