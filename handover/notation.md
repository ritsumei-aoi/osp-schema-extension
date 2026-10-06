# Notation and Terminology

This document defines the mathematical notation and terminology used in this
repository for the C(n+1) = osp(2|2n) schema extension project.

## 1. Algebra family and ranks

- Target family: C(n+1) = osp(2|2n), with m = 1 (number of fermionic standard pairs)
  and bosonic rank n.
- The three case studies are n = 1, 2, 3, i.e. C(2) = osp(2|2), C(3) = osp(2|4),
  C(4) = osp(2|6).
- Cartan rank = n + 1.
- Dimensions (even | odd | total):
  - n=1: 4 | 4 | 8
  - n=2: 11 | 8 | 19
  - n=3: 22 | 12 | 34
- Dimension formulas: even = 2n^2 + n + 1, odd = 4n, total = 2n^2 + 5n + 1.

## 2. Root system

Root vectors live in the span of orthogonal symbols
ε (fermionic), δ_1, …, δ_n (bosonic).

- Even roots: {±2δ_k | 1≤k≤n} ∪ {±(δ_i ± δ_j) | 1≤i<j≤n}.
- Odd roots: {±ε ± δ_k | 1≤k≤n} (four sign combinations per k).

## 3. Oscillator generators

- Standard fermionic pair a_1^+ , a_1^- with CAR {a_1^-, a_1^+} = 1 and
  (a_1^±)^2 = 0, parity 1.
- Bosonic oscillators b_k^+, b_k^- (k = 1,…,n) with CCR [b_k^-, b_l^+] = δ_{kl},
  parity 0.
- Mixed brackets vanish in the undeformed algebra: [b_k^s, a_1^σ] = 0.
- Central elements κ (odd, κ^2 = 0) and K (even, identified with scalar 1).

Oscillator label strings (used verbatim in JSON):
`a_1_p`, `a_1_m`, `b_k_p`, `b_k_m` (k = 1,…,n).

## 4. Generator label convention

| Root            | Label (JSON key)           | Oscillator word |
|-----------------|---------------------------|-----------------|
| Cartan #j (j=1..n+1) | `H_j`                 | polynomial in b^+b^- and a_1^+a_1^- |
| 2δ_k            | `E_2del{k}_p`             | (b_k^+)^2       |
| -2δ_k           | `E_2del{k}_m`             | (b_k^-)^2       |
| δ_i + δ_j (i<j) | `E_del{i}_del{j}_pp`      | b_i^+ b_j^+     |
| -(δ_i + δ_j)    | `E_del{i}_del{j}_mm`      | b_i^- b_j^-     |
| δ_i - δ_j (i<j) | `E_del{i}_del{j}_pm`      | b_i^+ b_j^-     |
| -(δ_i - δ_j)    | `E_del{i}_del{j}_mp`      | b_i^- b_j^+     |
| ε + δ_k         | `E_eps1_del{k}_pp`        | a_1^+ b_k^+     |
| ε - δ_k         | `E_eps1_del{k}_pm`        | a_1^+ b_k^-     |
| -ε + δ_k        | `E_eps1_del{k}_mp`        | a_1^- b_k^+     |
| -ε - δ_k        | `E_eps1_del{k}_mm`        | a_1^- b_k^-     |

Suffix convention: the first sign is the sign of ε (resp. δ_i); the second is
the sign of δ_k (resp. δ_j).

## 5. Cartan generators

Following the Frappat–Sciarrino–Sorba realization (see
`docs/math/Cn1_definition.md`), we take:

- H_1 = a_1^+ a_1^- + b_1^+ b_1^-
- H_k = b_{k-1}^+ b_{k-1}^- − b_k^+ b_k^-  (2 ≤ k ≤ n)
- H_{n+1} = − b_n^+ b_n^- − 1/2

These are the simple-root Cartan generators.

## 6. Even and odd basis lists

For C(n+1) the lists are, in PBW order (see §7):

### n = 1 (C(2), total 8)
- Even (4): `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`.
- Odd (4):  `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`.

### n = 2 (C(3), total 19)
- Even (11): `H_1`, `H_2`, `H_3`,
  `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`,
  `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`,
  `E_del1_del2_pm`, `E_del1_del2_mp`.
- Odd (8): for k = 1, 2: `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`,
  `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm`.

### n = 3 (C(4), total 34)
- Even (22): `H_1`, …, `H_4`;
  `E_2del{k}_p` and `E_2del{k}_m` for k = 1,2,3;
  `E_del{i}_del{j}_pp`, `E_del{i}_del{j}_mm`, `E_del{i}_del{j}_pm`,
  `E_del{i}_del{j}_mp` for (i,j) in {(1,2),(1,3),(2,3)}.
- Odd (12): `E_eps1_del{k}_{pp,pm,mp,mm}` for k = 1, 2, 3.

## 7. PBW ordering

Two options were considered:

**Option A (chosen)** — "κ < odd < even", grouping odd generators by k and the
four sign slots `(pp, pm, mp, mm)`, then even generators in the order
`H_j, E_2del{k}_p, E_del{i}_del{j}_pp, E_2del{k}_m, E_del{i}_del{j}_mm,
E_del{i}_del{j}_pm, E_del{i}_del{j}_mp`.

**Option B (rejected)** — Strict root-height ordering with ε and δ treated on
equal footing; this gives a lex-order over (height, signs of ε, signs of δ).

Rationale for A: parity-first ordering keeps consistency with the B(0,n) v5.0
schema (which uses "κ < odd < even"), minimises the diff between B(0,n) and
C(n+1) JSON files, and keeps the natural blocks visible — raising, lowering,
mixed. Option B gives a nicer graded Lie-theoretic reading but breaks parallel
schema layout and makes the odd/even separation less obvious in diffs.

Within the odd block, generators are ordered by k ascending; within fixed k by
sign slot `pp, pm, mp, mm`.
K (= 1) is excluded from the basis; κ is listed only in `central_elements`.

## 8. File naming

JSON files use the bosonic rank n:
- `C_1_structure.json`, `C_2_structure.json`, `C_3_structure.json`
- `C_1_gamma.json`, …
- `C_1_evaluated.json`, …
- `C_1_coboundary.json`, …

So C(n+1) uses file index n.
