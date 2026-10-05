# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Algebra Identification

| Symbol | Algebra | Bosonic rank | Fermionic rank |
|---|---|---|---|
| $B(0,n)$ | $\mathfrak{osp}(1\|2n)$ | $n$ | $0$ |
| $C(n+1)$ | $\mathfrak{osp}(2\|2n)$ | $n$ | $1$ |

### Oscillator Labels

| Oscillator | Label | Parity | Relation |
|---|---|---|---|
| $a_0$ (B(0,n) only) | `a_0` | 1 | $a_0^2 = 1/2$ |
| $a_1^+$ (C(n+1)) | `a_1_p` | 1 | $\{a_1^-, a_1^+\} = 1$ |
| $a_1^-$ (C(n+1)) | `a_1_m` | 1 | $\{a_1^-, a_1^+\} = 1$ |
| $b_k^+$ | `b_{k}_p` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ |
| $b_k^-$ | `b_{k}_m` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ |

### Root Vectors

- $\varepsilon$: fermionic root vector (C(n+1) only)
- $\delta_k$ ($k=1,\ldots,n$): bosonic root vectors

### Even Generators (C(n+1))

| Root | Label | Oscillator Realization |
|---|---|---|
| Cartan $H_k$ ($k=1,\ldots,n+1$) | `H_{k}` | see below |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |

Cartan elements:
- $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$
- $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $k=2,\ldots,n$
- $H_{n+1} = -b_n^+ b_n^- - 1/2$

### Odd Generators (C(n+1))

| Root | Label | Oscillator Realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps_del{k}_mm` | $a_1^- b_k^-$ |

### PBW Ordering (C(n+1))

$$
\kappa < [\text{odd generators}] < [\text{even generators}]
$$

Within each parity sector:

**Odd** (4n generators):
$$
E\_eps\_del1\_pp, \ldots, E\_eps\_deln\_pp,\;
E\_eps\_del1\_pm, \ldots, E\_eps\_deln\_pm,\;
E\_eps\_del1\_mp, \ldots, E\_eps\_deln\_mp,\;
E\_eps\_del1\_mm, \ldots, E\_eps\_deln\_mm
$$

**Even** ($2n^2+n+1$ generators):
$$
H_1, \ldots, H_{n+1},\;
E\_2del1\_p, \ldots, E\_2deln\_p,\;
E\_del{i}\_del{j}\_pp\;(i<j),\;
E\_2del1\_m, \ldots, E\_2deln\_m,\;
E\_del{i}\_del{j}\_mm\;(i<j),\;
E\_del{i}\_del{j}\_pm\;(i<j),\;
E\_del{i}\_del{j}\_mp\;(i<j)
$$

### Dimension Formulas

| | B(0,n) | C(n+1) |
|---|---|---|
| Even | $2n^2+n$ | $2n^2+n+1$ |
| Odd | $2n$ | $4n$ |
| Total | $2n^2+3n$ | $2n^2+5n+1$ |

### Explicit Basis Lists

**C(2) = osp(2|2), n=1**: even=4, odd=4, total=8
- Even: `H_1, H_2, E_2del1_p, E_2del1_m`
- Odd: `E_eps_del1_pp, E_eps_del1_pm, E_eps_del1_mp, E_eps_del1_mm`

**C(3) = osp(2|4), n=2**: even=11, odd=8, total=19
- Even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- Odd: `E_eps_del1_pp, E_eps_del2_pp, E_eps_del1_pm, E_eps_del2_pm, E_eps_del1_mp, E_eps_del2_mp, E_eps_del1_mm, E_eps_del2_mm`

**C(4) = osp(2|6), n=3**: even=22, odd=12, total=34
- Even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`
- Odd: `E_eps_del1_pp, E_eps_del2_pp, E_eps_del3_pp, E_eps_del1_pm, E_eps_del2_pm, E_eps_del3_pm, E_eps_del1_mp, E_eps_del2_mp, E_eps_del3_mp, E_eps_del1_mm, E_eps_del2_mm, E_eps_del3_mm`

### Central Elements

| Symbol | Label | Parity | Role |
|---|---|---|---|
| $K$ | `K` | 0 | Central identity (= 1 in all applications) |
| $\kappa$ | `kappa` | 1 | Nilpotent odd central element ($\kappa^2=0$) |
