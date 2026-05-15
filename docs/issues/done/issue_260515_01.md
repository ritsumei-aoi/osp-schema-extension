# Issue I01-1: C(n+1) basis and root system design

**Date**: 2026-05-15
**Status**: closed
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
- [x] Even and odd basis lists are clearly defined for `C(1)`, `C(2)`, and `C(3)`.
- [x] PBW ordering is decided and documented.
- [x] Notation conventions for the generators are finalized.

## Trust Boundary & Workflow Note
- **Human Approval Required**: The decision on the PBW ordering must be approved by a human researcher before finalization.
- **Iterative Dialogue Expected**: The AI should first propose options for the PBW ordering and basis labels in the `### Response` section below. Stop and wait for human selection. Once the human selects an option, the AI will document it and complete the issue.

---
### Response

**AI Agent**: Below is the analysis and proposal for Issue I01-1. Please review and select your preferred options.

---

## 1. Even and Odd Basis for C(n+1) = osp(2|2n)

### Oscillator generators

Following the notation established in `handover/notation.md`:

| Label | Operator | Parity |
|-------|----------|--------|
| `a_1_p` | Fermionic creation | odd (1) |
| `a_1_m` | Fermionic annihilation | odd (1) |
| `b_i_p` | Bosonic creation (i=1..n) | even (0) |
| `b_i_m` | Bosonic annihilation (i=1..n) | even (0) |

### Odd basis (4n generators)

| Generator | Root | Oscillator | Label |
|-----------|------|------------|-------|
| `E_eps1_del{k}_pp` | ε₁ + δ_k | a_1_p b_k_p | positive odd |
| `E_eps1_del{k}_pm` | ε₁ − δ_k | a_1_p b_k_m | positive odd |
| `E_eps1_del{k}_mp` | −(ε₁ − δ_k) | a_1_m b_k_p | negative odd |
| `E_eps1_del{k}_mm` | −(ε₁ + δ_k) | a_1_m b_k_m | negative odd |

for k = 1, ..., n.

### Even basis — design question

From Frappat et al., the even subalgebra of C(n+1) = osp(2|2n) is **so(2) × sp(2n)** with dimension:
- sp(2n): n(2n+1) = 2n² + n
- so(2): 1 (Cartan only)
- **Total even**: 2n² + n + 1

The root system of the even part consists of sp(2n) roots only:
- ±2δ_k (k=1..n)
- ±(δ_i ± δ_j) (i < j)

**Question**: The current `notation.md` lists `E_eps1_p = a_1_p²` and `E_eps1_m = a_1_m²` as even roots with root ε₁ and −ε₁. However, in standard C(n+1), these ε₁ roots belong to the **odd** root system (combined with δ_k). The generators a_1_p² and a_1_m² are quadratic in fermions and have even parity, but they do **not** appear as independent even root vectors in the standard Frappat basis of osp(2|2n).

I propose two options:

- **Option B1 (Standard Frappat)**: Omit `E_eps1_p`, `E_eps1_m` from the even basis. Even generators are Cartan (n+1) + sp(2n) root vectors (2n²) = 2n² + n + 1 total.
- **Option B2 (Extended)**: Include `E_eps1_p`, `E_eps1_m` in the even basis. Even generators = 2n² + n + 3 total. This requires mathematical justification that these are within osp(2|2n).

**Proposed even basis (assuming B1 — Standard Frappat)**:

| Category | Generators | Count |
|----------|-----------|-------|
| Cartan | `H_1, ..., H_{n-1}` (differences), `H_n` (last bosonic), `H_{n+1}` (fermionic) | n+1 |
| Positive long roots | `E_2del{k}_p` (k=1..n) | n |
| Negative long roots | `E_2del{k}_m` (k=1..n) | n |
| Positive sum roots | `E_del{i}_del{j}_pp` (i<j) | n(n-1)/2 |
| Negative sum roots | `E_del{i}_del{j}_mm` (i<j) | n(n-1)/2 |
| Pos-neg diff roots | `E_del{i}_del{j}_pm` (i<j) | n(n-1)/2 |
| Neg-pos diff roots | `E_del{i}_del{j}_mp` (i<j) | n(n-1)/2 |

### Dimension check

| n | Even | Odd | Total | osp(2\|2n) |
|---|------|-----|-------|------------|
| 1 | 4    | 4   | 8     | 8 ✓ |
| 2 | 11   | 8   | 19    | 19 ✓ |
| 3 | 22   | 12  | 34    | 34 ✓ |

---

## 2. PBW Ordering — Proposed Options

The existing B(0,n) convention (`B_generators.py`, v4.1) is:
```
κ < [odd generators] < [even generators] < K
```
where within each block, positive roots precede negative roots, and Cartan comes first among evens.

For C(n+1), I propose **three options**:

### Option A (Conservative — recommended)
```
κ < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp] < K
```
Same structure as B(0,n). Within even block: Cartan first, then positive roots, then negative roots, then mixed roots.

### Option B (ε-even separated)
```
κ < [odd] < [ε-even generators (if included)] < [δ-even generators] < K
```
Subdivides even block by oscillator origin (fermionic vs bosonic). Only relevant if B2 is chosen above.

### Option C (Root-height ordering)
```
κ < [ε₁+δ_k roots] < [ε₁−δ_k roots] < [−ε₁+δ_k roots] < [−ε₁−δ_k roots] < [even generators] < K
```
Orders odd generators by root height within the odd block.

---

### Human Decision (2026-05-15)

| # | Decision | Selection | Notes |
|---|----------|-----------|-------|
| 1 | Even basis scope | **B1** — Standard Frappat | Omit ε-even roots |
| 2 | PBW ordering | **A** — Conservative | κ < [odd] < [even] < K |

These decisions are now reflected in `handover/notation.md`.
