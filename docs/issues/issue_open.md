# Issue I01-1: C(n+1) basis and root system design

**Date**: 2026-05-15
**Status**: needs_clarification
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

Assumption: n = 1,2,3 → C(2), C(3), C(4). Proceeding autonomously because the user is not available; human approval is required for PBW ordering (see Trust Policy).

Proposals

1) Even and odd basis (root-generator form)

- C(2) (n=1)
  - Oscillators: a_1_p, a_1_m; b_1_p, b_1_m
  - Even generators: E_{\pm\epsilon_1}, E_{\pm 2\delta_1}
  - Odd generators: E_{\epsilon_1\pm\delta_1} and their negatives

- C(3) (n=2)
  - Oscillators: a_1_p, a_1_m; b_{1,2}_p, b_{1,2}_m
  - Even generators: E_{\pm\epsilon_1}, E_{\pm 2\delta_1}, E_{\pm 2\delta_2}, E_{\delta_1\pm\delta_2}
  - Odd generators: E_{\epsilon_1\pm\delta_1}, E_{\epsilon_1\pm\delta_2} and their negatives

- C(4) (n=3)
  - Oscillators: a_1_p, a_1_m; b_{1..3}_p, b_{1..3}_m
  - Even generators: E_{\pm\epsilon_1}, E_{\pm 2\delta_i} (i=1..3), E_{\delta_i\pm\delta_j} (i<j)
  - Odd generators: E_{\epsilon_1\pm\delta_i} (i=1..3) and their negatives

2) PBW ordering — three options (human must choose)

- Option A (recommended): Fermionic-first (continuity with B(0,n))
  - Example sample ordering: κ < [fermionic oscillators a_1_p,a_1_m] < [odd root generators (lexicographic)] < [even positive root generators (lexicographic)] < [Cartan generators] < K
  - Pros: maximal continuity with existing B(0,n) schema; simpler migration and schema reuse.
  - Cons: some literature prefers root-height or bosonic-first order.

- Option B: Bosonic-first
  - Pros: groups all even generators together; may simplify some PBW constructions.
  - Cons: breaks continuity with B(0,n) schema.

- Option C: Root-height (graded) ordering
  - Pros: algorithmically natural; orders by root degree/height.
  - Cons: more invasive change; less compatible with current schema tooling.

3) Generator label conventions

- Keep existing naming: a_1_p, a_1_m; b_i_p, b_i_m; E_eps1_p/m, E_2del{i}_p/m, E_eps1_del{i}_pp/pm/mp/mm, etc. Map labels to oscillator realizations as in handover/notation.md.

Next steps

- Please reply with a choice: Option A, B, or C. After human selection the AI will finalize handover/notation.md and commit the finalized notation.

Execution note

- Draft proposals appended here and a small "Proposed (pending approval)" section was added to handover/notation.md in this commit.

## Trust Boundary Remand

This issue reached the project's trust boundary: PBW ordering decisions are explicitly not delegable to the AI (see ai_trust_policy.md). The AI has proposed three options (A: Fermionic-first — recommended; B: Bosonic-first; C: Root-height/graded) and recommends Option A for continuity with the existing B(0,n) schema. Human approval is required before finalizing the PBW ordering and completing the issue.

To proceed, reply in this issue with a selection (A, B, or C). Once a choice is provided, the AI will finalize handover/notation.md, update completion criteria, and complete Phase 4 procedures.

