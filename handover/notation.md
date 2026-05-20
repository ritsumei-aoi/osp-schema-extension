# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

**Last updated**: Issue I01-1 (2026-05-20)

---

## 1. Algebra Family

The target algebra is $C(n+1) = \mathfrak{osp}(2|2n)$.

- JSON schema key: `"family": "C"`, `"m": 1`
- File naming: `C_{n}_structure.json` (e.g., C(2) = `C_1_structure.json`)
- Reference: Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000); arXiv:hep-th/9607161

---

## 2. Oscillator Generators

| Symbol | Label | Parity | Relation |
|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 (odd) | CAR: $\{a_1^-, a_1^+\} = 1$ |
| $a_1^-$ | `a_1_m` | 1 (odd) | CAR: $\{a_1^-, a_1^+\} = 1$ |
| $b_k^+$ ($k=1,\ldots,n$) | `b_{k}_p` | 0 (even) | CCR: $[b_k^-, b_l^+] = \delta_{kl}$ |
| $b_k^-$ ($k=1,\ldots,n$) | `b_{k}_m` | 0 (even) | CCR: $[b_k^-, b_l^+] = \delta_{kl}$ |

> **Key difference from B(0,n)**: C(n+1) uses a standard fermionic pair $(a_1^+, a_1^-)$ with CAR,
> instead of B(0,n)'s supplementary fermion $a_0$ satisfying $a_0^2 = \tfrac{1}{2}$.

---

## 3. Generator Labels and Oscillator Realizations

### Even generators

| Root | Label | Oscillator realization | Parity |
|---|---|---|---|
| Cartan ($k=1$) | `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ | 0 |
| Cartan ($k=2,\ldots,n$) | `H_{k}` | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ | 0 |
| Cartan ($k=n+1$) | `H_{n+1}` | $-b_n^+ b_n^- - \tfrac{1}{2}$ | 0 |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ | 0 |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ | 0 |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ | 0 |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ | 0 |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ | 0 |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ | 0 |

### Odd generators ($k = 1, \ldots, n$)

| Root | Label | Oscillator realization | Parity |
|---|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ | 1 |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ | 1 |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ | 1 |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ | 1 |

---

## 4. PBW Ordering Convention — Option A (Fermionic-first)

**Decision**: Option A approved in Issue I01-1 (2026-05-20).

```
κ  <  [odd generators]  <  [even generators]
```

### Odd block order (κ < this block):
```
E_eps1_del{k}_pp  (k = 1…n),
E_eps1_del{k}_pm  (k = 1…n),
E_eps1_del{k}_mp  (k = 1…n),
E_eps1_del{k}_mm  (k = 1…n)
```

### Even block order (odd block < this block):
```
H_1, H_2, …, H_{n+1},
E_2del{k}_p  (k = 1…n),   E_del{i}_del{j}_pp  (i < j, lex order),
E_2del{k}_m  (k = 1…n),   E_del{i}_del{j}_mm  (i < j, lex order),
E_del{i}_del{j}_pm  (i < j, lex order),
E_del{i}_del{j}_mp  (i < j, lex order)
```

---

## 5. Basis Lists by Algebra

### C(2) = osp(2|2), n = 1 — dim (4|4), total 8

**Even** (4): `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`

**Odd** (4): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

**PBW order**:
```
κ,
E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm,
H_1, H_2, E_2del1_p, E_2del1_m
```

---

### C(3) = osp(2|4), n = 2 — dim (11|8), total 19

**Even** (11): `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`

**Odd** (8): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`

**PBW order**:
```
κ,
E_eps1_del1_pp, E_eps1_del2_pp,
E_eps1_del1_pm, E_eps1_del2_pm,
E_eps1_del1_mp, E_eps1_del2_mp,
E_eps1_del1_mm, E_eps1_del2_mm,
H_1, H_2, H_3,
E_2del1_p, E_2del2_p, E_del1_del2_pp,
E_2del1_m, E_2del2_m, E_del1_del2_mm,
E_del1_del2_pm, E_del1_del2_mp
```

---

### C(4) = osp(2|6), n = 3 — dim (22|12), total 34

**Even** (22): `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`, `E_del1_del3_pm`, `E_del1_del3_mp`, `E_del2_del3_pm`, `E_del2_del3_mp`

**Odd** (12): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`, `E_eps1_del3_pp`, `E_eps1_del3_pm`, `E_eps1_del3_mp`, `E_eps1_del3_mm`

**PBW order**:
```
κ,
E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp,
E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm,
E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp,
E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm,
H_1, H_2, H_3, H_4,
E_2del1_p, E_2del2_p, E_2del3_p,
E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
E_2del1_m, E_2del2_m, E_2del3_m,
E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
E_del1_del2_pm, E_del1_del2_mp,
E_del1_del3_pm, E_del1_del3_mp,
E_del2_del3_pm, E_del2_del3_mp
```

---

## 6. Note on κ and K

- **κ** (kappa): Odd central element ($p(\kappa)=1$, $\kappa^2=0$) introduced by the Bakalov–Sullivan central extension. It appears first in the PBW ordering and in the `central_elements` JSON key.
- **K**: Even central element identified with the scalar identity ($K=1$) in all current applications. It does **not** appear as an independent basis element in PBW ordering or basis lists.
