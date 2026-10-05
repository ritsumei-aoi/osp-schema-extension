# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Root Vectors
- $\varepsilon$: fermionic root vector (one copy, since $m=1$ for C(n+1))
- $\delta_1, \ldots, \delta_n$: bosonic root vectors

### Oscillator Labels
| Oscillator | Label | Parity |
|---|---|---|
| $a_1^+$ | `a_1_p` | 1 |
| $a_1^-$ | `a_1_m` | 1 |
| $b_k^+$ | `b_k_p` | 0 |
| $b_k^-$ | `b_k_m` | 0 |

Relations:
- Fermionic CAR: $\{a_1^-, a_1^+\} = 1$
- Bosonic CCR: $[b_i^-, b_j^+] = \delta_{ij}$

### Even Generator Labels (Cartan + root generators)
| Root | Label | Oscillator realization |
|---|---|---|
| Cartan $H_k$ ($k=1$) | `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ |
| Cartan $H_k$ ($2 \le k \le n$) | `H_k` | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ |
| Cartan $H_{n+1}$ | `H_{n+1}` | $-b_n^+ b_n^- - 1/2$ |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |

### Odd Generator Labels
| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

### PBW Ordering Convention
$$\kappa < [\text{odd generators}] < [\text{even generators}]$$

Within the odd sector: positive $\varepsilon$ before negative $\varepsilon$, then ascending $k$, then $+\delta$ before $-\delta$:
```
E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm, ...,
E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm, ...
```

Within the even sector: Cartan first (ascending $k$), then positive root generators, then negative, then mixed:
```
H_1, ..., H_{n+1},
E_2del1_p, ..., E_2del{n}_p, E_del{i}_del{j}_pp, ...,
E_2del1_m, ..., E_2del{n}_m, E_del{i}_del{j}_mm, ...,
E_del{i}_del{j}_pm, ..., E_del{i}_del{j}_mp, ...
```

### Central Elements
- $K$: even central element (parity 0), identified with scalar 1
- $\kappa$: odd central element (parity 1), $\kappa^2 = 0$

### Dimension Formulas for C(n+1)
- Even: $2n^2 + n + 1$
- Odd: $4n$
- Total: $2n^2 + 5n + 1$

### Basis Lists

**C(2) = osp(2|2), n=1** — even: 4, odd: 4, total: 8
- Even: `H_1, H_2, E_2del1_p, E_2del1_m`
- Odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

**C(3) = osp(2|4), n=2** — even: 11, odd: 8, total: 19
- Even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- Odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm`

**C(4) = osp(2|6), n=3** — even: 22, odd: 12, total: 34
- Even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del2_mp, E_del1_del3_pm, E_del1_del3_mp, E_del2_del3_pm, E_del2_del3_mp`
- Odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del3_mp, E_eps1_del3_mm`
