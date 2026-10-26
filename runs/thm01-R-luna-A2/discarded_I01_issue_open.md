# Issue I01-1: C(n+1) basis and root system design

**Date**: 
**Status**: open
**Model**: GPT-6 Luna
**Category**: proposal
**Theme Working Branch**: study/thm01-R-luna-A2

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
3. Design oscillator generator labels consistent with `handover/notation.md`.
4. Update `handover/notation.md` with the finalized conventions.

## Deliverables
- Updated `handover/notation.md` documenting even/odd basis, PBW ordering, and generator labels.

## Completion Criteria
- [ ] Even and odd basis lists are clearly defined for C(2), C(3), and C(4).
- [ ] PBW ordering is decided and documented.
- [ ] Notation conventions for the generators are finalized.

## Trust Boundary & Workflow Note
- **Human Approval Required**: The decision on PBW ordering must be approved by a human researcher before finalization.
- **Iterative Dialogue Expected**: Propose concrete ordering options (at least two) and halt. **CRITICAL RULE**: Do NOT modify any files other than `issue_open.md` (append your proposals there), and do NOT create any commits until the human explicitly selects an option.

---
### Response

*(AI Agent: Please append your proposals, analysis, and execution logs here.)*

### AI Proposal: C(n+1) basis and PBW options

The following is a proposal only; no conventions are finalized pending the
researcher's selection of a PBW option.

#### Basis contents and proposed labels

Use Cartan labels `H_1` through `H_{n+1}`. Retain the B(0,n) even-root label
pattern for the `sp(2n)` roots:

- `E_2del{i}_p/m` denotes the root `±2δ_i`.
- For `i < j`, `E_del{i}_del{j}_pp`, `_pm`, `_mp`, and `_mm` denote,
  respectively, `δ_i+δ_j`, `δ_i-δ_j`, `-δ_i+δ_j`, and `-δ_i-δ_j`.
- `E_eps1_del{i}_xy` denotes the odd root with signs `x ε + y δ_i`;
  the first suffix sign is the ε sign and the second is the δ sign:
  `p` means `+`, and `m` means `-`. Thus `pp`, `pm`, `mp`, `mm` denote
  `ε+δ_i`, `ε-δ_i`, `-ε+δ_i`, `-ε-δ_i`.

The even basis is the Cartan generators, the positive `sp(2n)` roots
(`E_2del{i}_p` and pair labels `_pp`, `_pm`), then their negatives
(`E_2del{i}_m` and pair labels `_mm`, `_mp`). The odd basis is, for each
increasing `i`, `E_eps1_del{i}_pp`, `_pm`, `_mp`, `_mm`. The proposed
oscillator labels are consistent with the stated realization: the first
odd-root sign selects `a_1_p` or `a_1_m`, and the second selects `b_i_p`
or `b_i_m`; for example, `E_eps1_del{i}_pm` is realized by
`a_1_p b_i_m`.

Explicit lists in the proposed even-basis order:

- **C(2), n=1** — even: `H_1, H_2, E_2del1_p, E_2del1_m` (4);
  odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm` (4).
- **C(3), n=2** — even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p,
  E_del1_del2_pp, E_del1_del2_pm, E_2del1_m, E_2del2_m,
  E_del1_del2_mm, E_del1_del2_mp` (11);
  odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm,
  E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm` (8).
- **C(4), n=3** — even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p,
  E_2del3_p, E_del1_del2_pp, E_del1_del2_pm, E_del1_del3_pp,
  E_del1_del3_pm, E_del2_del3_pp, E_del2_del3_pm, E_2del1_m,
  E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del2_mp,
  E_del1_del3_mm, E_del1_del3_mp, E_del2_del3_mm, E_del2_del3_mp` (22);
  odd: for each `i=1,2,3` in increasing order,
  `E_eps1_del{i}_pp, E_eps1_del{i}_pm, E_eps1_del{i}_mp,
  E_eps1_del{i}_mm` (12).

The counts agree with the specified dimensions: even `2n²+n+1`, odd `4n`.
The scalar identity `K` is not counted as a basis vector. The deformation
symbol `κ`, if included in a later extension schema, is separate from the
undeformed C(n+1) basis.

#### PBW ordering options for researcher selection

1. **Parity-block / B(0,n)-compatible:** `odd < even`. Within the odd block,
   order by increasing `i`, then `pp, pm, mp, mm`; within the even block use
   the explicit even-basis order above. If the extended-schema symbol `κ`
   is part of the ordering, place it before both blocks, as in the B(0,n)
   convention.
2. **Root-triangular:** `Cartan < positive roots < negative roots`. Choose
   the positive odd roots to be `ε±δ_i` and the positive even roots to be
   `2δ_i` and `δ_i±δ_j` for `i<j`; order within each block by increasing
   `i` (and lexicographic `(i,j)` for paired roots), with the positive even
   roots before positive odd roots, and negative odd roots before negative
   even roots. If present in an extended schema, place `κ` first.

Both options give the same basis and dimensions; they differ only in the
PBW sequence. **Human decision required:** select option 1 or 2 (or request
a specific adjustment). Until that selection, `handover/notation.md` and
the completion checkboxes remain unchanged.
