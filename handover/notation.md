# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
Populated during Issue I01 for the C(n+1) = osp(2|2n) schema extension project.

## Conventions

### Oscillator Labels

| Symbol | JSON label | Parity | Description |
|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 | Fermionic creation operator |
| $a_1^-$ | `a_1_m` | 1 | Fermionic annihilation operator |
| $b_k^+$ | `b_{k}_p` | 0 | Bosonic creation operator ($k=1,\ldots,n$) |
| $b_k^-$ | `b_{k}_m` | 0 | Bosonic annihilation operator ($k=1,\ldots,n$) |

### Generator Labels (C(n+1))

Even generators:

| Root | JSON label | Oscillator realization |
|---|---|---|
| (Cartan $H_k$, $k=1,\ldots,n+1$) | `H_{k}` | see Cn1_definition.md |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $-(\delta_i+\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i-\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |

Odd generators ($k=1,\ldots,n$):

| Root | JSON label | Oscillator realization |
|---|---|---|
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

### Basis Lists

#### C(2) = osp(2|2), n=1: dim = (4|4), total = 8

**Even** (4 elements):
`H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`

**Odd** (4 elements):
`E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

#### C(3) = osp(2|4), n=2: dim = (11|8), total = 19

**Even** (11 elements):
`H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`,
`E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`

**Odd** (8 elements):
`E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`,
`E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`

#### C(4) = osp(2|6), n=3: dim = (22|12), total = 34

**Even** (22 elements):
`H_1`, `H_2`, `H_3`, `H_4`,
`E_2del1_p`, `E_2del2_p`, `E_2del3_p`,
`E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`,
`E_2del1_m`, `E_2del2_m`, `E_2del3_m`,
`E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`,
`E_del1_del2_pm`, `E_del1_del2_mp`, `E_del1_del3_pm`, `E_del1_del3_mp`,
`E_del2_del3_pm`, `E_del2_del3_mp`

**Odd** (12 elements):
`E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`,
`E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`,
`E_eps1_del3_pp`, `E_eps1_del3_pm`, `E_eps1_del3_mp`, `E_eps1_del3_mm`

### PBW Ordering

**Chosen ordering** (Option A):
```
κ < [odd generators, grouped by sign type then by k] < [even generators]
```

Odd ordering within the odd sector:
- All `E_eps1_del{k}_pp` for k=1..n
- Then `E_eps1_del{k}_pm` for k=1..n
- Then `E_eps1_del{k}_mp` for k=1..n
- Then `E_eps1_del{k}_mm` for k=1..n

Even ordering within the even sector:
- Cartan generators: `H_1,...,H_{n+1}`
- Positive bosonic: `E_2del{k}_p` (k=1..n), `E_del{i}_del{j}_pp` (i<j)
- Negative bosonic: `E_2del{k}_m` (k=1..n), `E_del{i}_del{j}_mm` (i<j)
- Mixed: `E_del{i}_del{j}_pm` (i<j), `E_del{i}_del{j}_mp` (i<j)

**Justification**: Option A follows the B(0,n) convention (κ < odd < even) for
consistency and backward compatibility. Grouping odd generators by root sign-type
(pp, pm, mp, mm) reflects the ε-structure naturally. The alternative Option B
([even] < [odd] < κ) was rejected because it breaks the pattern established by the
B(0,n) base case and would require separate PBW conventions for each algebra family.

### Deformation Parameters (gb matrix)

For C(n+1), the gb matrix has dimensions 2 × 2n (indexed by fermionic oscillator × bosonic oscillator):

$$\mathrm{gb}_{\sigma, k, s} \quad \sigma \in \{+,-\},\ k=1,\ldots,n,\ s \in \{+,-\}$$

JSON labels: `gb_a1p_bkp`, `gb_a1p_bkm`, `gb_a1m_bkp`, `gb_a1m_bkm` for $k=1,\ldots,n$.
Total: 4n parameters, all parity 1.

### Central Elements

- $K$: even central element (parity 0), identified with scalar 1 in all applications.
- $\kappa$: odd central element (parity 1), $\kappa^2 = 0$; formal symbol of nilpotent extension.
