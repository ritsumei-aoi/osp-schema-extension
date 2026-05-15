# Issue I02-1: Schema 1 v5.0 extension for C(n+1)

**Date**: 2026-05-15
**Status**: open
**Category**: proposal
**Theme Working Branch**: ai/t1-schema-extension
*(Note: For this case study, the Theme Working Branch serves as the primary working branch. Please perform operations and merge against this branch, rather than the repository's `main` branch.)*

## Context & Background
The existing Schema 1 (algebra structure) was designed for B(m,n).
Extending to C(n+1) requires modifications to several fields while maintaining backward compatibility with the schema specification. Issue I01-1 has finalized the basis and PBW ordering.

## Requirements
1. Design `algebra` field for C(n+1) (family="C")
2. Design `oscillator_generators` without supplementary fermion
3. Design `oscillator_relations` for standard fermionic pair
4. Determine `central_elements` (kappa, K) for C(n+1)
5. Define file naming conventions (e.g., `C_1_structure.json`, `C_2_structure.json`, `C_3_structure.json`)

## Deliverables
- Document (schema specification update, proposing how to extend `docs/json_schema_specification.md`)

## Completion Criteria
- [ ] All Schema 1 fields defined for C(n+1)
- [ ] Compatibility with B(m,n) schema documented
- [ ] File naming convention confirmed
- [ ] Schema specification draft created

## Trust Boundary & Workflow Note
- **Human Approval Required**: Schema field decisions and backward compatibility mapping require human approval.
- **Iterative Dialogue Expected**: Please propose the updated schema fields in the response section. **CRITICAL RULE**: Do NOT modify `json_schema_specification.md`, do NOT make any commits, and do NOT proceed to Phase 4 until the human explicitly approves your proposal.

---
### Response

*(AI Agent: Please append your proposals, analysis, and execution logs here.)*
