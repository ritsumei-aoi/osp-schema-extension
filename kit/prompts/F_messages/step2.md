[Step 2 of 8] Issue I02-1: Schema 1 v5.0 extension for C(n+1)

## Context & Background
The existing Schema 1 (algebra structure) was designed for B(m,n). Extending to
C(n+1) requires modifications to several fields while maintaining backward
compatibility. Step 1 has finalized the basis and PBW ordering.

## Requirements
1. Design `algebra` field for C(n+1) (family="C").
2. Design `oscillator_generators` without supplementary fermion.
3. Design `oscillator_relations` for standard fermionic pair (CAR).
4. Determine `central_elements` (kappa, K) for C(n+1).
5. Define file naming conventions (e.g., `C_1_structure.json`, `C_2_structure.json`, `C_3_structure.json`).

### Mandatory unified rules (fixed for all runs)
- **Algebra Field**: explicitly include `"m": 1` and the dimension formulas `even`: `2n^2 + n + 1`, `odd`: `4n`.
- **Oscillator Generators**: two keys, `"fermions"` (with `m=1`, labels `a_1_p, a_1_m`) and `"bosons"` (with rank `n`).
- **Central Elements**: `central_elements` is a **top-level key**, containing `kappa` (parity 1) and `K` (parity 0).
- **File Naming**: `C_{n}_structure.json`, where `n` is the bosonic rank (e.g., C(2) uses `n=1`).

## Deliverables
- Document: updated `docs/json_schema_specification.md` with C(n+1) field definitions.

## Completion Criteria
- [ ] All Schema 1 fields defined for C(n+1).
- [ ] Compatibility with B(m,n) schema documented.
- [ ] File naming convention confirmed.
- [ ] Schema specification draft created.

## Trust Boundary & Workflow Note
- **Human Approval Required**: Schema field decisions require human approval before the specification file is written.
- **Iterative Dialogue Expected**: Propose all field definitions in your reply and halt. **CRITICAL RULE**: Do NOT modify `json_schema_specification.md` until the human explicitly approves.
