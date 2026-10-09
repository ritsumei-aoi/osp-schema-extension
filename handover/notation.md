# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Oscillator Labels

| Symbol | JSON label | Parity | Algebra |
|---|---|---|---|
| $a_0$ | `a_0` | 1 | B(0,n): supplementary fermion, $a_0^2 = 1/2$ |
| $a_1^+$ | `a_1_p` | 1 | C(n+1): standard fermion (creation) |
| $a_1^-$ | `a_1_m` | 1 | C(n+1): standard fermion (annihilation) |
| $b_k^+$ | `b_{k}_p` | 0 | Bosonic oscillator (creation), $k=1,\ldots,n$ |
| $b_k^-$ | `b_{k}_m` | 0 | Bosonic oscillator (annihilation), $k=1,\ldots,n$ |

### 2. Generator Labels for C(n+1) = osp(2|2n)

#### Even generators (parity 0)

| Root | JSON label | Oscillator realization |
|---|---|---|
| Cartan $H_k$ ($k=1$) | `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ |
| Cartan $H_k$ ($2 \le k \le n$) | `H_{k}` | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ |
| Cartan $H_{n+1}$ | `H_{n+1}` | $-b_n^+ b_n^- - 1/2$ |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |

#### Odd generators (parity 1)

| Root | JSON label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

### 3. Even/Odd Basis Lists

**C(2) = osp(2|2), n=1**: dim = (4 | 4), total = 8

Even (4): `H_1, H_2, E_2del1_p, E_2del1_m`

Odd (4): `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

**C(3) = osp(2|4), n=2**: dim = (11 | 8), total = 19

Even (11): `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`

Odd (8): `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

**C(4) = osp(2|6), n=3**: dim = (22 | 12), total = 34

Even (22): `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`

Odd (12): `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm`

### 4. PBW Ordering

**Convention**: $\kappa$ < [odd generators] < [even generators], with $K = 1$ excluded.

This follows the B(0,n) convention for consistency.

**Two options considered**:
- **Option A** (chosen): $\kappa < \text{odd} < \text{even}$. Matches the B(0,n) convention used in the existing v5.0 schema. Keeps odd generators (which involve the fermionic oscillator) ordered first, consistent with standard PBW ordering for oscillator superalgebras.
- **Option B**: $\kappa < \text{even} < \text{odd}$. Sometimes used in physics literature where bosonic generators come first. Rejected for lack of backward compatibility with the B(0,n) schema.

**Within odd generators**: Group by $\varepsilon$-sign, then by $\delta$-index:
```
E_eps1_del{1}_pp, ..., E_eps1_del{n}_pp,   (ε + δ_k)
E_eps1_del{1}_pm, ..., E_eps1_del{n}_pm,   (ε - δ_k)
E_eps1_del{1}_mp, ..., E_eps1_del{n}_mp,   (-ε + δ_k)
E_eps1_del{1}_mm, ..., E_eps1_del{n}_mm    (-ε - δ_k)
```

**Within even generators**: Cartan first, then positive roots, then negative roots, then mixed-sign roots:
```
H_1, ..., H_{n+1},
E_2del{1}_p, ..., E_2del{n}_p,
E_del{i}_del{j}_pp (i<j),
E_2del{1}_m, ..., E_2del{n}_m,
E_del{i}_del{j}_mm (i<j),
E_del{i}_del{j}_pm (i<j),
E_del{i}_del{j}_mp (i<j)
```

### 5. Dimension Formulas

| Algebra | Even | Odd | Total |
|---|---|---|---|
| B(0,n) = osp(1\|2n) | $2n^2 + n$ | $2n$ | $2n^2 + 3n$ |
| C(n+1) = osp(2\|2n) | $2n^2 + n + 1$ | $4n$ | $2n^2 + 5n + 1$ |
