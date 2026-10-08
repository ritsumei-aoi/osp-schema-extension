# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
Finalized during Issue I01-1 (2026-10-08) for the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension.

**Reference**: Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000);
arXiv:hep-th/9607161.

---

## 1. Algebras

| Symbol | Lie superalgebra | Oscillator content |
|---|---|---|
| $B(0,n)$ | $\mathfrak{osp}(1\|2n)$ | Supplementary fermion $a_0$ + bosons $b_1^\pm, \ldots, b_n^\pm$ |
| $C(n+1)$ | $\mathfrak{osp}(2\|2n)$ | Standard fermionic pair $a_1^\pm$ + bosons $b_1^\pm, \ldots, b_n^\pm$ |

---

## 2. Oscillator Generators

### C(n+1) oscillators

| Symbol | JSON label | Parity | Relation |
|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 | $\{a_1^-, a_1^+\} = 1$ |
| $a_1^-$ | `a_1_m` | 1 | $\{a_1^-, a_1^+\} = 1$ |
| $b_k^+$ | `b_k_p` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ |
| $b_k^-$ | `b_k_m` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ |

The PBW oscillator word ordering is:
```
a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ... < b_n_p < b_n_m
```

---

## 3. Root Generators and JSON Labels

### Even generators (same for all n)

| Root | JSON label | Oscillator |
|---|---|---|
| Cartan $H_k$ ($k=1,\ldots,n+1$) | `H_{k}` | See §4 |
| $2\delta_k$ | `E_2del{k}_p` | $\tfrac{1}{2}(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $\tfrac{1}{2}(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i < j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i < j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-\delta_i + \delta_j$ ($i < j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-\delta_i - \delta_j$ ($i < j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |

### Odd generators

| Root | JSON label | Oscillator |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps_del{k}_pm` | $a_1^+ b_k^-` |
| $-\varepsilon + \delta_k$ | `E_eps_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps_del{k}_mm` | $a_1^- b_k^-$ |

The label suffix encodes signs: first character = sign of $\varepsilon$, second = sign of $\delta_k$
(`p` = $+$, `m` = $-$).

---

## 4. Cartan Elements

$$
H_1 = a_1^+ a_1^- + b_1^+ b_1^-, \quad
H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- \;(2 \le k \le n), \quad
H_{n+1} = -b_n^+ b_n^- - \tfrac{1}{2}.
$$

---

## 5. PBW Ordering (ε-first, Option A — approved 2026-10-08)

The canonical PBW ordering for $C(n+1)$ basis elements is:

```
[odd, ε+δ group]: E_eps_del1_pp, ..., E_eps_deln_pp
< [odd, ε-δ group]: E_eps_del1_pm, ..., E_eps_deln_pm
< [odd, -ε+δ group]: E_eps_del1_mp, ..., E_eps_deln_mp
< [odd, -ε-δ group]: E_eps_del1_mm, ..., E_eps_deln_mm
< [even, Cartan]: H_1, ..., H_{n+1}
< [even, positive Sp]: E_2del1_p, ..., E_2deln_p, E_del{i}_del{j}_pp (i<j)
< [even, negative Sp]: E_2del1_m, ..., E_2deln_m, E_del{i}_del{j}_mm (i<j)
< [even, mixed Sp]: E_del{i}_del{j}_pm (i<j), E_del{i}_del{j}_mp (i<j)
```

**Rationale**: The odd generator groups are ordered by the sign of $\varepsilon$ first (positive before
negative), then by the sign of $\delta_k$ (positive before negative), consistent with the oscillator
word PBW order `a_1_p < a_1_m`. Within each group, generators are sorted by ascending $k$.

---

## 6. Basis Lists by Case

### C(2) = osp(2|2), n=1 — dim (4|4)

**Even** (dim 4): `H_1, H_2, E_2del1_p, E_2del1_m`

**Odd** (dim 4), PBW order:
`E_eps_del1_pp, E_eps_del1_pm, E_eps_del1_mp, E_eps_del1_mm`

### C(3) = osp(2|4), n=2 — dim (11|8)

**Even** (dim 11):
`H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_del1_del2_pm, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_mp`

**Odd** (dim 8), PBW order:
`E_eps_del1_pp, E_eps_del2_pp, E_eps_del1_pm, E_eps_del2_pm, E_eps_del1_mp, E_eps_del2_mp, E_eps_del1_mm, E_eps_del2_mm`

### C(4) = osp(2|6), n=3 — dim (22|12)

**Even** (dim 22):
`H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`

**Odd** (dim 12), PBW order:
`E_eps_del1_pp, E_eps_del2_pp, E_eps_del3_pp, E_eps_del1_pm, E_eps_del2_pm, E_eps_del3_pm, E_eps_del1_mp, E_eps_del2_mp, E_eps_del3_mp, E_eps_del1_mm, E_eps_del2_mm, E_eps_del3_mm`

---

## 7. Dimension Formulas

| Algebra | even | odd | total |
|---|---|---|---|
| $B(0,n) = \mathfrak{osp}(1\|2n)$ | $2n^2+n$ | $2n$ | $2n^2+3n$ |
| $C(n+1) = \mathfrak{osp}(2\|2n)$ | $2n^2+n+1$ | $4n$ | $2n^2+5n+1$ |
