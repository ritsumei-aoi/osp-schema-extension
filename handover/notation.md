# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
Initialized and finalized during the $C(n+1)$ schema extension project (Issue I01).

---

## 1. Oscillator Generators

### Fermionic oscillators (C(n+1))
| Symbol | Label | Parity | Relation |
|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 | CAR: $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$ |
| $a_1^-$ | `a_1_m` | 1 | CAR |

### Bosonic oscillators
| Symbol | Label | Parity | Relation |
|---|---|---|---|
| $b_k^+$ | `b{k}_p` | 0 | CCR: $[b_k^-, b_k^+] = 1$ |
| $b_k^-$ | `b{k}_m` | 0 | CCR |

### Central elements
| Symbol | Label | Parity | Property |
|---|---|---|---|
| $K$ | `K` | 0 | Identity ($K = 1$) |
| $\kappa$ | `kappa` | 1 | Nilpotent: $\kappa^2 = 0$ |

---

## 2. Basis Generators for C(n+1) = osp(2|2n)

**Dimension formula**: even $= 2n^2 + n + 1$, odd $= 4n$, total $= 2n^2 + 5n + 1$.

### Even generators

| Root | Label | Oscillator realization |
|---|---|---|
| (Cartan, $H_k$) | `H_{k}` | see §3 |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |

### Odd generators (new vs B(0,n))

Subscripts encode the sign of $\varepsilon$ (first) and $\delta_k$ (second):

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

---

## 3. Cartan Generators

$$
H_1 = a_1^+ a_1^- + b_1^+ b_1^-
$$
$$
H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- \quad (k = 2, \ldots, n)
$$
$$
H_{n+1} = -b_n^+ b_n^- - \tfrac{1}{2}
$$

---

## 4. PBW Ordering (Decided: Option A)

**Two options considered**:

- **Option A** (chosen): Graded by parity — odd elements before even, consistent with B(0,n) convention.
  `κ < [odd] < [even]`
- **Option B**: Triangular decomposition — positive roots < Cartan < negative roots.

**Rationale for Option A**: Directly extends the B(0,n) PBW convention; maximizes backward compatibility with existing schema tooling; the odd-before-even ordering is natural for superalgebra computations.

### PBW ordering within each sector

**Odd sector** (4n elements): Ordered by $k = 1, \ldots, n$ and then by sign combination (pp, pm, mp, mm).

$$
E_{\varepsilon+\delta_1}^{++},\ E_{\varepsilon-\delta_1}^{+-},\ E_{-\varepsilon+\delta_1}^{-+},\ E_{-\varepsilon-\delta_1}^{--},\ \ldots,\ E_{\varepsilon+\delta_n}^{++},\ \ldots,\ E_{-\varepsilon-\delta_n}^{--}
$$

**Even sector** ($2n^2+n+1$ elements): Cartan first, then positive bosonic root generators, then negative, then mixed.

$$
H_1, \ldots, H_{n+1},\ E_{2\delta_1}^+, \ldots,\ E_{\delta_i+\delta_j}^{++} (i<j),\ E_{2\delta_1}^-, \ldots,\ E_{\delta_i+\delta_j}^{--},\ E_{\delta_i-\delta_j}^{+-},\ E_{\delta_i-\delta_j}^{-+}
$$

---

## 5. Basis Lists by Case

### C(2) = osp(2|2), n=1 — total dim 8

**Even** (4): `H_1, H_2, E_2del1_p, E_2del1_m`

**Odd** (4): `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

### C(3) = osp(2|4), n=2 — total dim 19

**Even** (11): `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`

**Odd** (8): `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm`

### C(4) = osp(2|6), n=3 — total dim 34

**Even** (22): `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`

**Odd** (12): `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del3_mp, E_eps1_del3_mm`

---

## 6. Deformation Parameters (gb matrix)

For C(n+1), there are $4n$ deformation parameters (parity 1):
$$
\{ \mathrm{gb}_{a_1^+, b_j^+},\ \mathrm{gb}_{a_1^+, b_j^-},\ \mathrm{gb}_{a_1^-, b_j^+},\ \mathrm{gb}_{a_1^-, b_j^-} \mid j = 1, \ldots, n \}
$$

Labels in JSON schema: `gb_a1p_b{j}p`, `gb_a1p_b{j}m`, `gb_a1m_b{j}p`, `gb_a1m_b{j}m`.

The deformed exchange relation: $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma, j, s} \cdot \kappa$.
