# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Oscillator Generators and Relations (C(n+1) = osp(2|2n))

**Fermionic oscillators** (standard CAR pair):
- $a_1^\pm$: standard fermionic pair with $\{a_1^-, a_1^+\} = 1$ (anticommutator)
- Labels: `a_1_p` for $a_1^+$, `a_1_m` for $a_1^-$

**Bosonic oscillators**:
- $b_k^\pm$ for $k = 1, \ldots, n$: bosonic oscillators with CCR $[b_k^-, b_l^+] = \delta_{kl}$
- Labels: `b_k_p` for $b_k^+$, `b_k_m` for $b_k^-$

---

## C(n+1) Basis Structure

### Algebra Dimensions
Formula: even = $2n^2 + n + 1$, odd = $4n$, total = $2n^2 + 5n + 1$.

| $n$ | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

### C(2) = osp(2|2) (n=1) Basis

**Even basis** (4 elements):
```
Cartan: H_1 = a_1^+ a_1^- + b_1^+ b_1^-
Cartan: H_2 = -b_1^+ b_1^- - 1/2
Positive: E_2del1_p = (b_1^+)^2
Negative: E_2del1_m = (b_1^-)^2
```

**Odd basis** (4 elements):
```
E_eps_del1_pp = a_1^+ b_1^+
E_eps_del1_pm = a_1^+ b_1^-
E_eps_del1_mp = a_1^- b_1^+
E_eps_del1_mm = a_1^- b_1^-
```

### C(3) = osp(2|4) (n=2) Basis

**Even basis** (11 elements):
```
Cartan: H_1 = a_1^+ a_1^- + b_1^+ b_1^- - b_2^+ b_2^-
Cartan: H_2 = b_1^+ b_1^- - b_2^+ b_2^-
Cartan: H_3 = -b_2^+ b_2^- - 1/2
Positive roots (6): E_2del1_p, E_2del2_p, E_del1_del2_pp, E_del1_del2_pm
Negative roots (4): E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_mp
```

**Odd basis** (8 elements):
```
E_eps_del1_pp, E_eps_del1_pm, E_eps_del1_mp, E_eps_del1_mm
E_eps_del2_pp, E_eps_del2_pm, E_eps_del2_mp, E_eps_del2_mm
```

### C(4) = osp(2|6) (n=3) Basis

**Even basis** (22 elements):
```
Cartan (4): H_1, H_2, H_3, H_4
Positive roots (9):
  E_2del{k}_p for k=1,2,3 (3 elements)
  E_del{i}_del{j}_pp, E_del{i}_del{j}_pm for 1≤i<j≤3 (6 elements)
Negative roots (9):
  E_2del{k}_m for k=1,2,3 (3 elements)
  E_del{i}_del{j}_mm, E_del{i}_del{j}_mp for 1≤i<j≤3 (6 elements)
```

**Odd basis** (12 elements):
```
For each k ∈ {1,2,3}:
  E_eps_del{k}_pp, E_eps_del{k}_pm, E_eps_del{k}_mp, E_eps_del{k}_mm
```

---

## PBW Ordering Convention (Standard Superalgebra)

**Selection Rationale**: Fermionic roots come before bosonic roots in the positive root hierarchy. This follows standard superalgebra conventions (Frappat et al., Kac, Scheunert) where odd generators are treated as "higher weight" than even generators.

**Ordering**:
```
κ < [odd: E_eps_del{k}_{pp,pm,mp,mm}] < [even: H_j, E_{bosonic}]
```

Within odd roots: descending by $k$, then pp > pm > mp > mm.
Within even roots: Cartan elements first, then positive roots (descending order), then negative roots (ascending order).

---

## Generator Label Convention

### Even roots (oscillator realization):
- $2\delta_k$: `E_2del{k}_p` (realized as $(b_k^+)^2$)
- $-2\delta_k$: `E_2del{k}_m` (realized as $(b_k^-)^2$)
- $\delta_i + \delta_j$ ($i<j$): `E_del{i}_del{j}_pp` (realized as $b_i^+ b_j^+$)
- $\delta_i - \delta_j$ ($i<j$): `E_del{i}_del{j}_pm` (realized as $b_i^+ b_j^-$)
- $-(\delta_i - \delta_j)$ ($i<j$): `E_del{i}_del{j}_mp` (realized as $b_i^- b_j^+$)
- $-(\delta_i + \delta_j)$ ($i<j$): `E_del{i}_del{j}_mm` (realized as $b_i^- b_j^-$)

### Odd roots (oscillator realization):
- $\varepsilon + \delta_k$: `E_eps_del{k}_pp` (realized as $a_1^+ b_k^+$)
- $\varepsilon - \delta_k$: `E_eps_del{k}_pm` (realized as $a_1^+ b_k^-$)
- $-\varepsilon + \delta_k$: `E_eps_del{k}_mp` (realized as $a_1^- b_k^+$)
- $-\varepsilon - \delta_k$: `E_eps_del{k}_mm` (realized as $a_1^- b_k^-$)

**Suffix encoding**: For odd roots `E_eps_del{k}_{XY}`, where X,Y ∈ {p,m}:
- X refers to the sign of the fermionic factor: p = $a_1^+$, m = $a_1^-$
- Y refers to the sign of the bosonic factor: p = $b_k^+$, m = $b_k^-$
