# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
Initialized during the $C(n+1)$ schema extension project (Issue I01).

---

## 1. Algebra and Root System

### Algebra family
- **B(0,n) = osp(1|2n)**: supplementary fermion $a_0$ with $a_0^2 = 1/2$.
- **C(n+1) = osp(2|2n)**: standard fermionic pair $a_1^\pm$ with $\{a_1^-, a_1^+\} = 1$.

### Vectors
- $\varepsilon$: the single fermionic direction for C(n+1).
- $\delta_k$ ($k=1,\ldots,n$): bosonic directions.

### Roots of C(n+1)
| Type | Roots | Count | Parity |
|---|---|---|---|
| Even | $\pm 2\delta_k$, $\pm(\delta_i \pm \delta_j)$ ($i<j$) | $2n^2+n$ | $\bar{0}$ |
| Even (Cartan) | $n+1$ Cartan generators $H_1,\ldots,H_{n+1}$ | $n+1$ | $\bar{0}$ |
| Odd | $\pm\varepsilon \pm \delta_k$ ($k=1,\ldots,n$) | $4n$ | $\bar{1}$ |

**Dimension**: even $= 2n^2+n+1$, odd $= 4n$, total $= 2n^2+5n+1$.

| $n$ | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

---

## 2. Oscillator Generator Labels

### Bosonic oscillators
- `b_{k}_p` → $b_k^+$, `b_{k}_m` → $b_k^-$ for $k=1,\ldots,n$.
- Relations: $[b_k^-, b_l^+] = \delta_{kl}$, all other commutators zero.

### Fermionic oscillators (C(n+1) specific)
- `a_1_p` → $a_1^+$, `a_1_m` → $a_1^-$.
- Relation: $\{a_1^-, a_1^+\} = 1$, $\{a_1^\pm, a_1^\pm\} = 0$.

### Central elements
- `kappa` → $\kappa$ (odd, $p(\kappa)=1$, $\kappa^2=0$): nilpotent extension element.
- `K` → $K$ (even, $p(K)=0$): central identity, identified with scalar 1 in all applications.

---

## 3. Generator Label Conventions for C(n+1)

### Even generators (Cartan)
| Generator | Label | Oscillator realization |
|---|---|---|
| $H_1$ | `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ |
| $H_k$ ($k=2,\ldots,n$) | `H_{k}` | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ |
| $H_{n+1}$ | `H_{n+1}` | $-b_n^+ b_n^- - 1/2$ |

### Even generators (root vectors)
| Root | Label | Oscillator realization |
|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |

### Odd generators (ε-roots)
| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

---

## 4. Basis Lists

### C(2) = osp(2|2), n=1

**Even basis** (4 generators):
```
H_1, H_2, E_2del1_p, E_2del1_m
```

**Odd basis** (4 generators):
```
E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm
```

### C(3) = osp(2|4), n=2

**Even basis** (11 generators):
```
H_1, H_2, H_3,
E_2del1_p, E_2del2_p, E_del1_del2_pp,
E_2del1_m, E_2del2_m, E_del1_del2_mm,
E_del1_del2_pm, E_del1_del2_mp
```

**Odd basis** (8 generators):
```
E_eps1_del1_pp, E_eps1_del2_pp,
E_eps1_del1_pm, E_eps1_del2_pm,
E_eps1_del1_mp, E_eps1_del2_mp,
E_eps1_del1_mm, E_eps1_del2_mm
```

### C(4) = osp(2|6), n=3

**Even basis** (22 generators):
```
H_1, H_2, H_3, H_4,
E_2del1_p, E_2del2_p, E_2del3_p,
E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
E_2del1_m, E_2del2_m, E_2del3_m,
E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,
E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp
```

**Odd basis** (12 generators):
```
E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp,
E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm,
E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp,
E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm
```

---

## 5. PBW Ordering

**Decision**: PBW ordering follows the same convention as B(0,n):

```
κ  <  [odd generators]  <  [even generators]
```

**Within odd generators**: ordered by subscript type (pp < pm < mp < mm), then by bosonic index $k$ ascending.

**Within even generators**: Cartan ($H_1 < \cdots < H_{n+1}$), then positive even ($E_{2\delta_k}$, then $E_{\delta_i+\delta_j}$), then negative even ($E_{-2\delta_k}$, then $E_{-(\delta_i+\delta_j)}$), then mixed ($E_{\delta_i-\delta_j}$, $E_{-(\delta_i-\delta_j)}$).

### Rationale for this ordering

**Option A (chosen)**: κ < [odd] < [even]
- Consistent with B(0,n) schema v5.0 PBW ordering, enabling direct comparison.
- Fermionic sector (κ and odd generators) precedes bosonic in PBW product.
- Facilitates uniform structure constant sign rules across B and C families.

**Option B (rejected)**: κ < [even Cartan] < [odd] < [even root vectors]
- Separating Cartan from root vectors breaks the clean even/odd partition.
- Would require different sign conventions from B(0,n), complicating cross-family verification.

---

## 6. Deformation Parameters (gb matrix) for C(n+1)

The inhomogeneous deformation is parametrized by $4n$ odd parameters (parity 1):

$$\mathrm{gb}_{\sigma,j,s}, \quad \sigma \in \{+,-\},\ j=1,\ldots,n,\ s \in \{+,-\}$$

Label convention: `gb_{sigma}_{j}_{s}` where sigma ∈ {p, m}, s ∈ {p, m}.

For C(2) (n=1): `gb_p_1_p`, `gb_p_1_m`, `gb_m_1_p`, `gb_m_1_m`.
