# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Algebra Family

- $B(0,n) = \mathfrak{osp}(1|2n)$: supplementary fermion $a_0$ with $a_0^2 = 1/2$.
- $C(n+1) = \mathfrak{osp}(2|2n)$: standard fermionic pair $a_1^\pm$ with $\{a_1^-, a_1^+\} = 1$.

### Oscillator Labels

| Symbol | JSON label | Parity | Description |
|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 | Fermionic creation operator |
| $a_1^-$ | `a_1_m` | 1 | Fermionic annihilation operator |
| $b_k^+$ | `b_{k}_p` | 0 | Bosonic creation, $k=1,\ldots,n$ |
| $b_k^-$ | `b_{k}_m` | 0 | Bosonic annihilation, $k=1,\ldots,n$ |
| $\kappa$ | `kappa` | 1 | Odd central element |
| $K$ | `K` | 0 | Even central element (= scalar 1 in applications) |

### Generator Labels for C(n+1)

Root generators are named by their root vector using the following scheme:

| Root | JSON label | Oscillator realization | Parity |
|---|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ | 0 |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ | 0 |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ | 0 |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ | 0 |
| $-(\delta_i-\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ | 0 |
| $-(\delta_i+\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ | 0 |
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ | 1 |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ | 1 |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ | 1 |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ | 1 |
| Cartan $H_1$ | `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ | 0 |
| Cartan $H_k$ ($k \ge 2$) | `H_{k}` | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ | 0 |
| Cartan $H_{n+1}$ | `H_{n+1}` | $-b_n^+ b_n^- - 1/2$ | 0 |

### PBW Ordering (C(n+1))

**Decision**: Use the ordering

$$\kappa < [\text{odd}] < [\text{even, Cartan}] < [\text{even, roots}]$$

within odd: $\varepsilon+\delta_k$ before $\varepsilon-\delta_k$ before $-\varepsilon+\delta_k$ before $-\varepsilon-\delta_k$, for $k=1,\ldots,n$.

Two options were considered:
1. **Option A** (chosen): $\kappa < [\text{odd: } E\_\text{eps1}\_\text{del{k}\_pp/pm/mp/mm}] < [\text{even: } H, E\_\text{roots}]$. This mirrors the B(0,n) convention (odd before even) and keeps $\kappa$ first as the nilpotent extension element.
2. **Option B**: $\kappa < [\text{even}] < [\text{odd}]$. Less natural because it separates $\kappa$ (odd) from odd generators.

**Reason for Option A**: Consistency with the B(0,n) base case and standard PBW conventions placing the nilpotent extension element first.

Full ordering for $n=1$ (C(2)):
```
κ < E_eps1_del1_pp < E_eps1_del1_pm < E_eps1_del1_mp < E_eps1_del1_mm
  < H_1 < H_2
  < E_2del1_p < E_2del1_m
```

Full ordering for $n=2$ (C(3)):
```
κ < E_eps1_del1_pp < E_eps1_del1_pm < E_eps1_del1_mp < E_eps1_del1_mm
    E_eps1_del2_pp < E_eps1_del2_pm < E_eps1_del2_mp < E_eps1_del2_mm
  < H_1 < H_2 < H_3
  < E_2del1_p < E_2del2_p
  < E_del1_del2_pp < E_2del1_m < E_2del2_m
  < E_del1_del2_mm
  < E_del1_del2_pm < E_del1_del2_mp
```

### Basis Lists for C(n+1)

#### C(2) = osp(2|2), n=1: dim = (4|4), total = 8

Even basis (4 elements):
- `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`

Odd basis (4 elements):
- `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

#### C(3) = osp(2|4), n=2: dim = (11|8), total = 19

Even basis (11 elements):
- `H_1`, `H_2`, `H_3`
- `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`
- `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`
- `E_del1_del2_pm`, `E_del1_del2_mp`

Odd basis (8 elements):
- `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`
- `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`

#### C(4) = osp(2|6), n=3: dim = (22|12), total = 34

Even basis (22 elements):
- `H_1`, `H_2`, `H_3`, `H_4`
- `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`
- `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`
- `E_del1_del2_pm`, `E_del1_del2_mp`, `E_del1_del3_pm`, `E_del1_del3_mp`, `E_del2_del3_pm`, `E_del2_del3_mp`

Odd basis (12 elements):
- `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`
- `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`
- `E_eps1_del3_pp`, `E_eps1_del3_pm`, `E_eps1_del3_mp`, `E_eps1_del3_mm`
