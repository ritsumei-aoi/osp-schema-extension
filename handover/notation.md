# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Algebra Family

| Symbol | Algebra | Oscillator setup |
|---|---|---|
| $B(0,n)$ | $\mathfrak{osp}(1\|2n)$ | Supplementary fermion $a_0$, $a_0^2 = 1/2$ |
| $C(n+1)$ | $\mathfrak{osp}(2\|2n)$ | Standard fermionic pair $a_1^\pm$, $\{a_1^-, a_1^+\} = 1$ |

### Oscillator Labels (JSON)

| Oscillator | JSON label | Parity |
|---|---|---|
| $a_0$ (B(0,n) only) | `a_0` | 1 |
| $a_1^+$ (C(n+1) only) | `a_1_p` | 1 |
| $a_1^-$ (C(n+1) only) | `a_1_m` | 1 |
| $b_k^+$ | `b_{k}_p` | 0 |
| $b_k^-$ | `b_{k}_m` | 0 |

### Generator Labels (JSON) — Even Sector

| Root | Label | Oscillator realization |
|---|---|---|
| Cartan $H_k$ | `H_{k}` | see below |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |

### Generator Labels (JSON) — Odd Sector

**B(0,n):**

| Root | Label | Oscillator realization |
|---|---|---|
| $\delta_k$ | `E_del{k}_p` | $a_0 b_k^+$ |
| $-\delta_k$ | `E_del{k}_m` | $a_0 b_k^-$ |

**C(n+1):**

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

### Cartan Generators for C(n+1)

| Generator | Oscillator realization | Note |
|---|---|---|
| $H_1$ | $a_1^+ a_1^- + b_1^+ b_1^-$ | Mixed fermionic–bosonic |
| $H_k$ ($2 \leq k \leq n$) | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ | Purely bosonic |
| $H_{n+1}$ | $-b_n^+ b_n^- - 1/2$ | Terminal Cartan |

### PBW Ordering for C(n+1)

**Decision**: We adopt the ordering

$$
\kappa \;<\; [\text{odd generators}] \;<\; [\text{even generators}]
$$

with sub-ordering:
- **Odd sector**: grouped by bosonic index $k = 1, \ldots, n$; within each $k$: `pp, pm, mp, mm`.
- **Even sector**: Cartan $H_1, \ldots, H_{n+1}$, then positive roots (E_2del{k}_p, E_del{i}_del{j}_pp), then negative roots (E_2del{k}_m, E_del{i}_del{j}_mm), then mixed-sign roots (E_del{i}_del{j}_pm, E_del{i}_del{j}_mp).

**Options considered**:
1. *Option A*: Split odd sector by $\varepsilon$-sign ($\varepsilon+$ before $-\varepsilon$). More natural for weight-space decomposition.
2. *Option B* (chosen): Group odd sector by bosonic index $k$. More consistent with B(0,n) convention (where odd generators are `E_del{k}_p, E_del{k}_m`), and keeps the four generators for each $\delta_k$ together.

**Justification**: Option B preserves structural parallelism with the existing B(0,n) schema and simplifies code that iterates over bosonic indices.

### Concrete Basis Lists

**C(2) = osp(2|2), n=1** — dim = (4|4) = 8

Even (4):
```
H_1, H_2, E_2del1_p, E_2del1_m
```

Odd (4):
```
E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm
```

**C(3) = osp(2|4), n=2** — dim = (11|8) = 19

Even (11):
```
H_1, H_2, H_3,
E_2del1_p, E_2del2_p, E_del1_del2_pp,
E_2del1_m, E_2del2_m, E_del1_del2_mm,
E_del1_del2_pm, E_del1_del2_mp
```

Odd (8):
```
E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm,
E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm
```

**C(4) = osp(2|6), n=3** — dim = (22|12) = 34

Even (22):
```
H_1, H_2, H_3, H_4,
E_2del1_p, E_2del2_p, E_2del3_p,
E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
E_2del1_m, E_2del2_m, E_2del3_m,
E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
E_del1_del2_pm, E_del1_del2_mp,
E_del1_del3_pm, E_del1_del3_mp,
E_del2_del3_pm, E_del2_del3_mp
```

Odd (12):
```
E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm,
E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm,
E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del3_mp, E_eps1_del3_mm
```

### Central Elements

| Element | JSON key | Parity | Role |
|---|---|---|---|
| $K$ | `K` | 0 | Identity (scalar 1), excluded from PBW basis |
| $\kappa$ | `kappa` | 1 | Nilpotent central element ($\kappa^2 = 0$), included in PBW ordering |

### Dimension Formulas

| Algebra | Even | Odd | Total |
|---|---|---|---|
| $B(0,n)$ | $2n^2 + n$ | $2n$ | $2n^2 + 3n$ |
| $C(n+1)$ | $2n^2 + n + 1$ | $4n$ | $2n^2 + 5n + 1$ |
