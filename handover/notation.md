# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
Finalized during Issue I01 for the C(n+1) = osp(2|2n) schema extension project.

## Conventions

### 1. Algebra family

| Symbol | Algebra | Oscillators |
|---|---|---|
| B(0,n) = osp(1\|2n) | Supplementary fermion a_0, bosons b_k^± | reference case |
| C(n+1) = osp(2\|2n) | Standard fermionic pair a_1^±, bosons b_k^± | new extension |

### 2. Oscillator labels and PBW order

PBW order for C(n+1): `a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ... < b_n_p < b_n_m`

| Oscillator | Label | Parity | Relation |
|---|---|---|---|
| a_1^+ | `a_1_p` | 1 | CAR: {a_1^-, a_1^+} = 1, (a_1^±)^2 = 0 |
| a_1^- | `a_1_m` | 1 | CAR |
| b_k^+ | `b_k_p` | 0 | CCR: [b_k^-, b_l^+] = δ_{kl} |
| b_k^- | `b_k_m` | 0 | CCR |

Cross relation: a_1^± and b_k^± commute (different sectors).

### 3. Generator label convention for C(n+1)

**Cartan generators** (n+1 total):

| Generator | Oscillator realization | Label |
|---|---|---|
| H_1 | a_1^+ a_1^- + b_1^+ b_1^- | `H_1` |
| H_k (k=2,...,n) | b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- | `H_k` |
| H_{n+1} | -b_n^+ b_n^- - 1/2 | `H_{n+1}` |

**Even non-Cartan generators** (2n^2 total):

| Root | Generator label | Oscillator form | PBW monomial |
|---|---|---|---|
| 2δ_k | `E_2del{k}_p` | (b_k^+)^2 | (b_k_p, b_k_p) |
| -2δ_k | `E_2del{k}_m` | (b_k^-)^2 | (b_k_m, b_k_m) |
| δ_i + δ_j (i<j) | `E_del{i}_del{j}_pp` | b_i^+ b_j^+ | (b_i_p, b_j_p) |
| -(δ_i + δ_j) (i<j) | `E_del{i}_del{j}_mm` | b_i^- b_j^- | (b_i_m, b_j_m) |
| δ_i - δ_j (i<j) | `E_del{i}_del{j}_pm` | b_i^+ b_j^- | (b_i_p, b_j_m) |
| -(δ_i - δ_j) (i<j) | `E_del{i}_del{j}_mp` | b_i^- b_j^+ | (b_i_m, b_j_p) |

**Odd generators** (4n total):

| Root | Generator label | Oscillator form | PBW monomial |
|---|---|---|---|
| ε + δ_k | `E_eps1_del{k}_pp` | a_1^+ b_k^+ | (a_1_p, b_k_p) |
| ε - δ_k | `E_eps1_del{k}_pm` | a_1^+ b_k^- | (a_1_p, b_k_m) |
| -ε + δ_k | `E_eps1_del{k}_mp` | a_1^- b_k^+ | (a_1_m, b_k_p) |
| -ε - δ_k | `E_eps1_del{k}_mm` | a_1^- b_k^- | (a_1_m, b_k_m) |

### 4. Basis lists by n

**PBW ordering convention**: κ < [odd generators] < [even generators]
Within odd: (pp, pm, mp, mm) × (k=1,...,n)
Within even Cartan: H_1, ..., H_{n+1}
Within even non-Cartan: positive (pp,p) → negative (mm,m) → mixed (pm, mp)

**C(2) = osp(2|2), n=1** — total dim = 8 (even=4, odd=4):

Even basis (4): `H_1, H_2, E_2del1_p, E_2del1_m`
Odd basis (4): `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

**C(3) = osp(2|4), n=2** — total dim = 19 (even=11, odd=8):

Even basis (11): `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
Odd basis (8): `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

**C(4) = osp(2|6), n=3** — total dim = 34 (even=22, odd=12):

Even basis (22): `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del2_mp, E_del1_del3_pm, E_del1_del3_mp, E_del2_del3_pm, E_del2_del3_mp`
Odd basis (12): `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm`

### 5. Dimension formulas

For C(n+1) = osp(2|2n):
- even dim: 2n^2 + n + 1
- odd dim: 4n
- total dim: 2n^2 + 5n + 1

### 6. File naming

Schema files use `C_{n}_{layer}.json` where n is the bosonic rank:
- C(2) → n=1: `C_1_structure.json`, `C_1_gamma.json`, etc.
- C(3) → n=2: `C_2_structure.json`, etc.
- C(4) → n=3: `C_3_structure.json`, etc.

### 7. Central elements

| Element | Label | Parity | Property |
|---|---|---|---|
| κ | `kappa` | 1 (odd) | κ^2 = 0 |
| K | `K` | 0 (even) | central identity (= scalar 1 in practice) |

κ is the formal symbol for the nilpotent central extension used in the inhomogeneous deformation.
K = 1 is excluded from basis lists (not an independent element in applications).

### 8. Deformation parameters

For C(n+1), the gb parameters are indexed by (fermionic label, bosonic label):
`gb_{sigma}_{j}_{s}` where sigma ∈ {p, m} (for a_1^±) and s ∈ {p, m} (for b_j^±).

Total count: 4n parameters (2 fermion labels × n boson indices × 2 boson signs).
