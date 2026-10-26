[Step 1 of 8] Issue I01-1: C(n+1) basis and root system design

## Context & Background
C(n+1) = osp(2|2n) uses a standard fermionic pair (a_1_p, a_1_m) instead of
B(0,n)'s supplementary fermion a_0. This changes the basis structure, PBW
ordering, and oscillator relations throughout the entire schema.

The existing B(0,n) implementation is available for reference at:
https://github.com/ritsumei-aoi/osp-triviality

For C(n+1) root structure, refer to:
Frappat et al., "Dictionary on Lie Algebras and Superalgebras", arXiv:hep-th/9607161

## Requirements
1. Define even and odd basis lists for C(n+1) for n=1, 2, 3 (i.e., C(2), C(3), C(4)), following the Frappat notation.
2. Determine PBW ordering with ε-roots, proposing concrete options for human selection.
3. Design oscillator generator labels.
4. Report the finalized conventions in your reply.

## Deliverables
- A summary in your reply documenting even/odd basis, PBW ordering, and generator labels.

## Completion Criteria
- [ ] Even and odd basis lists are clearly defined for C(2), C(3), and C(4).
- [ ] PBW ordering is decided and documented.
- [ ] Notation conventions for the generators are finalized.

## Trust Boundary & Workflow Note
- **Human Approval Required**: The decision on PBW ordering must be approved by a human researcher before finalization.
- **Iterative Dialogue Expected**: Propose concrete ordering options (at least two) and halt. **CRITICAL RULE**: Do NOT modify any files until the human explicitly selects an option.
