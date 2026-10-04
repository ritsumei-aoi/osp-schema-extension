# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Algebras

- $B(0,n) = \mathfrak{osp}(1|2n)$: base case, supplementary fermion $a_0$ with $a_0^2 = 1/2$.
- $C(n+1) = \mathfrak{osp}(2|2n)$: extension case, standard fermionic pair $a_1^\pm$.

### Oscillator Labels

| Symbol | JSON label | Parity | Relation |
|--------|-----------|--------|----------|
| $a_1^+$ | `a_1_p` | 1 | CAR pair |
| $a_1^-$ | `a_1_m` | 1 | CAR pair |
| $b_k^+$ | `b_{k}_p` | 0 | CCR pair |
| $b_k^-$ | `b_{k}_m` | 0 | CCR pair |

Relations: $\{a_1^-, a_1^+\} = 1$, $[b_k^-, b_l^+] = \delta_{kl}$, $[b_k^\pm, a_1^\pm] = 0$ (undeformed).

### Root Generator Labels for C(n+1)

| Root | Generator label | Oscillator realization |
|------|----------------|----------------------|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

### Cartan Generators

| Label | Realization |
|-------|------------|
| `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ |
| `H_k` ($k \geq 2$) | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ |
| `H_{n+1}` | $-b_n^+ b_n^- - 1/2$ |

### Basis Lists for C(n+1)

**C(2) = osp(2|2), n=1**: dim = (4|4), total = 8

- Even basis (4): `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- Odd basis (4): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

**C(3) = osp(2|4), n=2**: dim = (11|8), total = 19

- Even basis (11): `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
- Odd basis (8): `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`

**C(4) = osp(2|6), n=3**: dim = (22|12), total = 34

- Even basis (22): `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`, `E_del1_del3_pm`, `E_del1_del3_mp`, `E_del2_del3_pm`, `E_del2_del3_mp`
- Odd basis (12): `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del3_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del3_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del3_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`, `E_eps1_del3_mm`

### PBW Ordering Decision

**Options considered**:

1. **Option A** (odd-first): `κ < [odd: E_eps1_del{k}_{...}] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_{...}]`
   - Pros: Mirrors B(0,n) convention; odd generators come first, consistent with superalgebra PBW theory.
   - Cons: Interleaving ε-roots requires choosing an ordering among the 4n odd generators.

2. **Option B** (even-first): `[even] < [odd]`
   - Pros: Even subalgebra forms a closed sub-PBW-basis.
   - Cons: Breaks symmetry with B(0,n) convention; odd generators at the end.

**Decision**: **Option A** (odd-first), mirroring B(0,n).

Within odd generators, order by: first positive ε-sign (`a_1^+` sector) then negative (`a_1^-` sector), and within each sector order by bosonic index $k$ and then sign of $\delta_k$ (positive before negative).

Full PBW ordering (for n=1 example):
```
κ < E_eps1_del1_pp < E_eps1_del1_pm < E_eps1_del1_mp < E_eps1_del1_mm
  < H_1 < H_2 < E_2del1_p < E_2del1_m
```

### Central Elements

| Symbol | JSON label | Parity | Property |
|--------|-----------|--------|----------|
| $\kappa$ | `kappa` | 1 | Odd nilpotent: $\kappa^2 = 0$ |
| $K$ | `K` | 0 | Even central identity (identified with scalar 1) |
