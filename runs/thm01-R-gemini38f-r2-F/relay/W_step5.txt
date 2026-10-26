[Step 5 of 8] Issue I05-1: Schema 2 (gamma structure) for C(n+1)

## Context & Background
With the structure constants verified (step 4), extend the schema to include
the inhomogeneous deformation (gamma structure, Schema 2).

For C(n+1), the inhomogeneous deformation is defined by the interaction between
the standard fermionic pair (a1+, a1-) and the bosonic oscillators. Refer to
`docs/math/C_inhomogeneous_definition.md` for the formal mathematical grounding.

## Requirements
1. Define the `gb_matrix` for C(n+1) (size 2 x 2n) based on the oscillator pairs.
2. Compute gamma coefficients $\gamma_{abc}$ for C(n+1) inhomogeneous deformation.
3. Design the `inhomogeneous_deformation` field in accordance with Schema 2 standards.
4. Generate Schema 2 JSON for n=1, 2, 3.
5. Verify consistency with Schema 1.

## Deliverables
- Code: gamma computation script.
- Data: Schema 2 JSON files.

## Completion Criteria
- [ ] Gamma computation implemented.
- [ ] Schema 2 JSON generated for n=1, 2, 3.
- [ ] Consistency check passes.

## Trust Boundary & Workflow Note
- **Human Approval Required**: Gram matrix sign conventions require human approval.
- **Iterative Dialogue Expected**: Propose the gamma computation method and sign convention options. **CRITICAL RULE**: Do NOT write Schema 2 JSON until the human approves.
