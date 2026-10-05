# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Oscillator Labels

| Symbol | JSON label | Parity | Relation |
|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 | $\{a_1^-, a_1^+\} = 1$ (CAR) |
| $a_1^-$ | `a_1_m` | 1 | $\{a_1^-, a_1^+\} = 1$ (CAR) |
| $b_k^+$ | `b_{k}_p` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ (CCR) |
| $b_k^-$ | `b_{k}_m` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ (CCR) |

### 2. Generator Labels for C(n+1)

#### Even generators

| Root | JSON label | Oscillator realization |
|---|---|---|
| Cartan $H_1$ | `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ |
| Cartan $H_k$ ($2 \leq k \leq n$) | `H_{k}` | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ |
| Cartan $H_{n+1}$ | `H_{n+1}` | $-b_n^+ b_n^- - 1/2$ |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |

#### Odd generators

| Root | JSON label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

### 3. PBW Ordering

**Chosen ordering**: $\kappa$ < [odd generators] < [even generators]

Within each parity sector, generators are ordered by:
1. Positive roots before negative roots.
2. Lower index before higher index.

Explicit order:

**Odd sector** (left to right):
`E_eps1_del{1}_pp`, ..., `E_eps1_del{n}_pp`, `E_eps1_del{1}_pm`, ..., `E_eps1_del{n}_pm`, `E_eps1_del{1}_mp`, ..., `E_eps1_del{n}_mp`, `E_eps1_del{1}_mm`, ..., `E_eps1_del{n}_mm`

**Even sector** (left to right):
`H_1`, ..., `H_{n+1}`, `E_2del{1}_p`, ..., `E_2del{n}_p`, [E_del{i}_del{j}_pp for i<j], `E_2del{1}_m`, ..., `E_2del{n}_m`, [E_del{i}_del{j}_mm for i<j], [E_del{i}_del{j}_pm for i<j], [E_del{i}_del{j}_mp for i<j]

**PBW ordering options considered**:
- **Option A** (chosen): $\kappa$ < odd < even. This is consistent with the B(0,n) convention and places the central extension element first. The odd generators precede even, which simplifies graded product computations.
- **Option B**: $\kappa$ < even < odd. This reverses the parity order. Rejected because it breaks compatibility with B(0,n) conventions.

### 4. Basis Lists

#### C(2) = osp(2|2), n=1

**Even** (4 generators): `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`

**Odd** (4 generators): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

**Total**: 8 = 4|4

#### C(3) = osp(2|4), n=2

**Even** (11 generators): `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`

**Odd** (8 generators): `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`

**Total**: 19 = 11|8

#### C(4) = osp(2|6), n=3

**Even** (22 generators): `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del3_pm`, `E_del2_del3_pm`, `E_del1_del2_mp`, `E_del1_del3_mp`, `E_del2_del3_mp`

**Odd** (12 generators): `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del3_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del3_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del3_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`, `E_eps1_del3_mm`

**Total**: 34 = 22|12

### 5. Dimension Formulas

| Algebra | Even | Odd | Total |
|---|---|---|---|
| C(n+1) | $2n^2 + n + 1$ | $4n$ | $2n^2 + 5n + 1$ |
| B(0,n) | $2n^2 + n$ | $2n$ | $2n^2 + 3n$ |

### 6. Central Elements

- **$K$** (parity 0): Central identity element; identified with scalar 1 in applications. Excluded from PBW ordering and basis lists.
- **$\kappa$** (parity 1): Odd nilpotent central element ($\kappa^2 = 0$). Appears first in PBW ordering. Used as the formal parameter for the abelian extension.
