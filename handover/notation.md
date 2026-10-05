# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
Finalized during Issue I01-1 for the $C(n+1)$ schema extension project.

**Reference**: Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000);
arXiv:hep-th/9607161.

---

## 1. Algebra Family

| Symbol | Meaning |
|---|---|
| $C(n+1)$ | $\mathfrak{osp}(2\|2n)$, with even subalgebra $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$ |
| $B(0,n)$ | $\mathfrak{osp}(1\|2n)$, reference case |
| $\varepsilon$ | Fermionic orthogonal vector (one, for $C(n+1)$) |
| $\delta_k$ | Bosonic orthogonal vectors, $k = 1, \ldots, n$ |

---

## 2. Oscillator Generators

### C(n+1) oscillators

| Symbol | Label | Parity | Relation |
|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 | $\{a_1^-, a_1^+\} = 1$ (CAR) |
| $a_1^-$ | `a_1_m` | 1 | $\{a_1^-, a_1^+\} = 1$ (CAR) |
| $b_k^+$ | `b_{k}_p` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ (CCR) |
| $b_k^-$ | `b_{k}_m` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ (CCR) |

### B(0,n) oscillators (reference)

| Symbol | Label | Parity | Relation |
|---|---|---|---|
| $a_0$ | `a_0` | 1 | $a_0^2 = 1/2$ (supplementary fermion) |
| $b_k^\pm$ | `b_{k}_p/m` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ |

---

## 3. Generator Labels

### Even generators (same for B(0,n) and C(n+1))

| Root | Label | Oscillator realization |
|---|---|---|
| (Cartan) | `H_{k}`, $k=1,\ldots,n+1$ | see definition files |
| $2\delta_k$ | `E_2del{k}_p` | $\tfrac{1}{2}(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $\tfrac{1}{2}(b_k^-)^2$ |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $-(\delta_i+\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i-\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |

### Odd generators — B(0,n)

| Root | Label | Oscillator realization |
|---|---|---|
| $\delta_k$ | `E_del{k}_p` | $a_0 b_k^+$ |
| $-\delta_k$ | `E_del{k}_m` | $a_0 b_k^-$ |

### Odd generators — C(n+1)

The fermionic direction is denoted `eps1` in labels (ε = first fermionic direction).

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

Label suffix convention: the two signs `_{s1}{s2}` encode the signs of (ε-component, δ-component),
where `p` = positive (+) and `m` = negative (−).

---

## 4. PBW Ordering — C(n+1) (Approved: Option A, Parity-First)

**Decision (2026-10-05)**: Option A selected for structural continuity with B(0,n).

**Convention**: All odd generators precede all even generators in PBW order.

```
[odd] < [even]
```

Within **odd** (ordered by k, then by ε-sign):
```
E_eps1_del{1}_pp, E_eps1_del{1}_pm, ..., E_eps1_del{n}_pp, E_eps1_del{n}_pm,
E_eps1_del{1}_mp, E_eps1_del{1}_mm, ..., E_eps1_del{n}_mp, E_eps1_del{n}_mm
```

Within **even** (Cartans first, then positive even roots by height, then negative):
```
H_1, ..., H_{n+1},
E_2del{1}_p, ..., E_2del{n}_p, E_del{i}_del{j}_pp (i<j),
E_2del{1}_m, ..., E_2del{n}_m, E_del{i}_del{j}_mm (i<j),
E_del{i}_del{j}_pm (i<j), E_del{i}_del{j}_mp (i<j)
```

### Reference ordering for B(0,n)

```
κ < [odd: E_del{k}_p/m] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]
```

---

## 5. Basis Lists by Algebra

### C(2) = osp(2|2), n=1: dim = (4|4) = 8

**Even** (4): `H_1, H_2, E_2del1_p, E_2del1_m`

**Odd** (4): `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

---

### C(3) = osp(2|4), n=2: dim = (11|8) = 19

**Even** (11):
```
H_1, H_2, H_3,
E_2del1_p, E_2del2_p, E_del1_del2_pp,
E_2del1_m, E_2del2_m, E_del1_del2_mm,
E_del1_del2_pm, E_del1_del2_mp
```

**Odd** (8):
```
E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm,
E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm
```

---

### C(4) = osp(2|6), n=3: dim = (22|12) = 34

**Even** (22):
```
H_1, H_2, H_3, H_4,
E_2del1_p, E_2del2_p, E_2del3_p,
E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
E_2del1_m, E_2del2_m, E_2del3_m,
E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,
E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp
```

**Odd** (12):
```
E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm,
E_eps1_del3_pp, E_eps1_del3_pm,
E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm,
E_eps1_del3_mp, E_eps1_del3_mm
```

---

## 6. Dimension Formulas

| Algebra | even | odd | total |
|---|---|---|---|
| $B(0,n) = \mathfrak{osp}(1\|2n)$ | $2n^2+n$ | $2n$ | $2n^2+3n$ |
| $C(n+1) = \mathfrak{osp}(2\|2n)$ | $2n^2+n+1$ | $4n$ | $2n^2+5n+1$ |
