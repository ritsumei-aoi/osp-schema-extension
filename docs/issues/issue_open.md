# Issue I01-1: C(n+1) basis and root system design

**Date**: 2026-05-15
**Status**: open
**Category**: proposal
**Theme Working Branch**: `ai/t1-schema-extension`
*(Note: For this case study, `ai/t1-schema-extension` serves as the primary working branch for the T1 theme. Please branch off and perform operations against this branch, rather than the repository's `main` branch.)*

## Context & Background
This issue is the first step in Phase 1 of extending the 4-layer JSON schema from `B(0,n) = osp(1|2n)` to `C(n+1) = osp(2|2n)` for `n = 1, 2, 3`. 

Unlike `B(0,n)` which relies on a supplementary fermion `a_0`, `C(n+1)` uses a standard fermionic pair `(a_1_p, a_1_m)`. This fundamental change impacts the basis structure, the PBW (Poincaré-Birkhoff-Witt) ordering, and the oscillator relations. The schema extension must be consistent with the existing `B(0,n)` schema available at: https://github.com/ritsumei-aoi/osp-triviality

**Primary Reference for C(n+1)**:
- Frappat et al., "Dictionary on Lie superalgebras", arXiv:hep-th/9607161 (https://arxiv.org/abs/hep-th/9607161)

## Requirements
1. Define the even and odd basis for `C(n+1)` following the standard Frappat notation.
2. Determine the PBW ordering taking into account the new $\epsilon$-roots.
3. Design the labels for the oscillator generators without the supplementary fermion `a_0`.
4. Update `handover/notation.md` with these final conventions.

## Deliverables
- A document update: specifically, modifying `handover/notation.md` to reflect the new basis and ordering.

## Completion Criteria
- [ ] Even and odd basis lists are clearly defined for `C(1)`, `C(2)`, and `C(3)`.
- [ ] PBW ordering is decided and documented.
- [ ] Notation conventions for the generators are finalized.

## Trust Boundary & Workflow Note
- **Human Approval Required**: The decision on the PBW ordering must be approved by a human researcher before finalization.
- **Iterative Dialogue Expected**: The AI should first propose options for the PBW ordering and basis labels in the `### Response` section below. Stop and wait for human selection. Once the human selects an option, the AI will document it and complete the issue.

---
### Response

*(AI Agent: Please append your proposals, analysis, and execution logs here.)*
