# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Oscillators

| Symbol | Type | Parity | Relation |
|---|---|---|---|
| $a_1^\pm$ | Standard fermionic pair | 1 | $\{a_1^-, a_1^+\} = 1$ |
| $b_k^\pm$ ($k=1,\ldots,n$) | Bosonic oscillators | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ |
| $\kappa$ | Odd central element | 1 | $\kappa^2 = 0$ |
| $K$ | Even central identity | 0 | identified with scalar 1 |

### Root Vectors

$C(n+1) = \mathfrak{osp}(2|2n)$ uses orthogonal vectors $\varepsilon$ (fermionic) and $\delta_1,\ldots,\delta_n$ (bosonic).

### Generator Label Convention (JSON schema)

**Even generators (parity 0):**

| Root | Generator label | Oscillator realization |
|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| Cartan $k$ | `H_{k}` | see oscillator realization |

**Odd generators (parity 1):**

| Root | Generator label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps_del{k}_mm` | $a_1^- b_k^-$ |

### Cartan Generators (oscillator realization)

From `Cn1_definition.md` (simple generators):

$$
H_1 = a_1^+ a_1^- + b_1^+ b_1^-
$$
$$
H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-, \quad 2 \leq k \leq n
$$
$$
H_{n+1} = -b_n^+ b_n^- - \tfrac{1}{2}
$$

### Basis Lists

**C(2) = osp(2|2), $n=1$**, dim $(4|4) = 8$:
- Even: `H_1, H_2, E_2del1_p, E_2del1_m`
- Odd: `E_eps_del1_pp, E_eps_del1_pm, E_eps_del1_mp, E_eps_del1_mm`

**C(3) = osp(2|4), $n=2$**, dim $(11|8) = 19$:
- Even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- Odd: `E_eps_del1_pp, E_eps_del1_pm, E_eps_del1_mp, E_eps_del1_mm, E_eps_del2_pp, E_eps_del2_pm, E_eps_del2_mp, E_eps_del2_mm`

**C(4) = osp(2|6), $n=3$**, dim $(22|12) = 34$:
- Even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del2_mp, E_del1_del3_pm, E_del1_del3_mp, E_del2_del3_pm, E_del2_del3_mp`
- Odd: `E_eps_del1_pp, E_eps_del1_pm, E_eps_del1_mp, E_eps_del1_mm, E_eps_del2_pp, E_eps_del2_pm, E_eps_del2_mp, E_eps_del2_mm, E_eps_del3_pp, E_eps_del3_pm, E_eps_del3_mp, E_eps_del3_mm`

### PBW Ordering

**Decision**: Option A — consistent with the B(0,n) convention.

PBW ordering (C(n+1)):
```
κ < [odd: E_eps_del{k}_{pp/pm/mp/mm}] < [even: H_k, E_2del{k}_p, E_del{i}_del{j}_pp, E_2del{k}_m, E_del{i}_del{j}_mm, E_del{i}_del{j}_pm, E_del{i}_del{j}_mp]
```

Rationale: Option A keeps κ leftmost (as a nilpotent central element), groups all fermionic (ε-type) generators before even generators, and orders even generators by root type (Cartan, then positive, then negative, then mixed). This mirrors B(0,n) convention and simplifies PBW normal-form algorithms.

Option B (κ < [bosonic positive] < [fermionic] < [bosonic negative]) was considered but rejected because it mixes parity classes and breaks the standard superalgebra PBW convention.

### Deformation Parameters (gb matrix)

For C(n+1), there are $4n$ deformation parameters indexed by:
$$
\mathrm{gb}_{\sigma, j, s}, \quad \sigma \in \{+,-\},\ j=1,\ldots,n,\ s \in \{+,-\}.
$$

Labels: `gb_a1p_bkp`, `gb_a1p_bkm`, `gb_a1m_bkp`, `gb_a1m_bkm` for $k=1,\ldots,n$.

The deformed commutator is:
$$
[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s} \cdot \kappa.
$$
