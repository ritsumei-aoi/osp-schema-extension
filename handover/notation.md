# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

---

## Conventions

### 1. Algebra Identification

| Notation | Meaning |
|---|---|
| $B(0,n)$ | $\mathfrak{osp}(1\|2n)$: supplementary fermion $a_0$ plus $n$ bosonic pairs |
| $C(n+1)$ | $\mathfrak{osp}(2\|2n)$: standard fermionic pair $a_1^\pm$ plus $n$ bosonic pairs |

### 2. Oscillator Labels

#### C(n+1) oscillators

| Symbol | JSON label | Parity | Role |
|---|---|---|---|
| $a_1^+$ | `a1p` | 1 (odd) | Fermionic creation |
| $a_1^-$ | `a1m` | 1 (odd) | Fermionic annihilation |
| $b_k^+$ ($k=1,\ldots,n$) | `b{k}p` | 0 (even) | Bosonic creation, mode $k$ |
| $b_k^-$ ($k=1,\ldots,n$) | `b{k}m` | 0 (even) | Bosonic annihilation, mode $k$ |

#### Oscillator relations

$$\{a_1^-, a_1^+\} = K = 1, \quad (a_1^\pm)^2 = 0$$
$$[b_k^-, b_l^+] = \delta_{kl}, \quad [a_1^\pm, b_k^\pm] = 0$$

### 3. Generator Labels and Oscillator Realizations

#### Even generators (parity 0)

**Cartan generators** ($k = 1, \ldots, n+1$):

| Label | Oscillator realization |
|---|---|
| `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ |
| `H_k` ($k=2,\ldots,n$) | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ |
| `H_{n+1}` | $-b_n^+ b_n^- - \tfrac{1}{2}$ |

**sp(2n) root generators** ($1 \leq k \leq n$, $1 \leq i < j \leq n$):

| Label | Root | Oscillator realization |
|---|---|---|
| `E_2del{k}_p` | $2\delta_k$ | $(b_k^+)^2$ |
| `E_2del{k}_m` | $-2\delta_k$ | $(b_k^-)^2$ |
| `E_del{i}_del{j}_pp` | $\delta_i + \delta_j$ | $b_i^+ b_j^+$ |
| `E_del{i}_del{j}_mm` | $-\delta_i - \delta_j$ | $b_i^- b_j^-$ |
| `E_del{i}_del{j}_pm` | $\delta_i - \delta_j$ | $b_i^+ b_j^-$ |
| `E_del{i}_del{j}_mp` | $-\delta_i + \delta_j$ | $b_i^- b_j^+$ |

#### Odd generators (parity 1) ($k = 1, \ldots, n$)

| Label | Root | Oscillator realization |
|---|---|---|
| `E_eps1_del{k}_pp` | $\varepsilon + \delta_k$ | $a_1^+ b_k^+$ |
| `E_eps1_del{k}_pm` | $\varepsilon - \delta_k$ | $a_1^+ b_k^-$ |
| `E_eps1_del{k}_mp` | $-\varepsilon + \delta_k$ | $a_1^- b_k^+$ |
| `E_eps1_del{k}_mm` | $-\varepsilon - \delta_k$ | $a_1^- b_k^-$ |

### 4. Basis Lists

#### PBW Ordering Convention

The PBW ordering for the basis generators is:
$$\kappa < [\text{odd generators}] < [\text{even generators}]$$

**Rationale for ordering options considered:**

- **Option A** (chosen): $\kappa < \text{odd} < \text{even}$, following the B(0,n) pattern. Within odd: positive-$\varepsilon$ roots first (pp, pm order per k), then negative-$\varepsilon$ roots (mp, mm order per k). Within even: Cartan H_k in order, then positive sp(2n) roots, then negative, then mixed.
- **Option B** (not chosen): Oscillator-level PBW ordering ($a_1^+ < a_1^- < b_1^+ < b_1^- < \cdots$). This is natural for computation but less standard for the schema.

Option A is chosen because it parallels the B(0,n) schema convention and makes parity structure explicit.

#### C(2) = osp(2|2), n=1 (dim 4|4 = 8)

**Even basis** (dim = 4):
```
H_1, H_2, E_2del1_p, E_2del1_m
```

**Odd basis** (dim = 4):
```
E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm
```

#### C(3) = osp(2|4), n=2 (dim 11|8 = 19)

**Even basis** (dim = 11):
```
H_1, H_2, H_3,
E_2del1_p, E_2del2_p,
E_del1_del2_pp,
E_2del1_m, E_2del2_m,
E_del1_del2_mm,
E_del1_del2_pm, E_del1_del2_mp
```

**Odd basis** (dim = 8):
```
E_eps1_del1_pp, E_eps1_del2_pp,
E_eps1_del1_pm, E_eps1_del2_pm,
E_eps1_del1_mp, E_eps1_del2_mp,
E_eps1_del1_mm, E_eps1_del2_mm
```

#### C(4) = osp(2|6), n=3 (dim 22|12 = 34)

**Even basis** (dim = 22):
```
H_1, H_2, H_3, H_4,
E_2del1_p, E_2del2_p, E_2del3_p,
E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
E_2del1_m, E_2del2_m, E_2del3_m,
E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,
E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp
```

**Odd basis** (dim = 12):
```
E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp,
E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm,
E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp,
E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm
```

### 5. Deformation Parameters (gb matrix)

For C(n+1), the inhomogeneous deformation parameters are:

$$\{ \mathrm{gb}_{a_1^\sigma, b_j^s} \mid \sigma \in \{+,-\},\ j = 1,\ldots,n,\ s \in \{+,-\} \}$$

**JSON label convention**: `gb_{ferm_label}_{bos_label}`, e.g., `gb_a1p_b1p`.

| Parameter | JSON label | Parity |
|---|---|---|
| $\mathrm{gb}_{a_1^+, b_j^+}$ | `gb_a1p_b{j}p` | 1 |
| $\mathrm{gb}_{a_1^+, b_j^-}$ | `gb_a1p_b{j}m` | 1 |
| $\mathrm{gb}_{a_1^-, b_j^+}$ | `gb_a1m_b{j}p` | 1 |
| $\mathrm{gb}_{a_1^-, b_j^-}$ | `gb_a1m_b{j}m` | 1 |

Total: $4n$ parameters per algebra.

### 6. Central Elements

| Symbol | JSON label | Parity | Role |
|---|---|---|---|
| $K$ | `K` | 0 (even) | Identity ($K = 1$ in realizations) |
| $\kappa$ | `kappa` | 1 (odd) | Nilpotent central element ($\kappa^2 = 0$) |
