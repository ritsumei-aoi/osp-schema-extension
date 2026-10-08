# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

## C(n+1) = osp(2|2n) conventions

### Root and generator labels

Use the roots $\varepsilon,\delta_1,\ldots,\delta_n$ from
`docs/math/Cn1_definition.md`. The even roots are
$\pm2\delta_k$ and $\pm\delta_i\pm\delta_j$ for $i<j$; the odd roots are
$\pm\varepsilon\pm\delta_k$.

The generator labels encode root signs with `p` for plus and `m` for minus:

| Root | Generator label |
|---|---|
| $2\delta_k$, $-2\delta_k$ | `E_2del{k}_p`, `E_2del{k}_m` |
| $\delta_i+\delta_j$, $\delta_i-\delta_j$ | `E_del{i}_del{j}_pp`, `E_del{i}_del{j}_pm` |
| $-\delta_i+\delta_j$, $-\delta_i-\delta_j$ | `E_del{i}_del{j}_mp`, `E_del{i}_del{j}_mm` |
| $\varepsilon+\delta_k$, $\varepsilon-\delta_k$ | `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm` |
| $-\varepsilon+\delta_k$, $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm` |

The Cartan generators are `H_1` through `H_{n+1}`. The oscillator labels are
`a_1_p`, `a_1_m`, and `b_{k}_p`, `b_{k}_m` for $1\leq k\leq n$; `a_1_p`
and `a_1_m` are a standard fermionic pair, not the supplementary $a_0$.

### Basis and PBW ordering

Use the following even basis order:

1. `H_1`, ..., `H_{n+1}`;
2. `E_2del{k}_p` in increasing $k$, then `E_del{i}_del{j}_pp` and
   `E_del{i}_del{j}_pm` in lexicographic $(i,j)$ order;
3. `E_2del{k}_m` in increasing $k$, then `E_del{i}_del{j}_mm` and
   `E_del{i}_del{j}_mp` in lexicographic $(i,j)$ order.

The odd basis is ordered by increasing $k$, with
`E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`,
`E_eps1_del{k}_mm` for each $k$. The full PBW convention is
`[odd generators in this order] < [even generators in this order]`.
The central bookkeeping symbols $\kappa$ and $K$ are not basis elements.

Two possible odd-generator orders were considered: (1) group all four roots
for each $\delta_k$, as above; or (2) group all $\varepsilon$-positive roots
before all $\varepsilon$-negative roots. The per-$k$ grouping is adopted
because it keeps the four-dimensional odd sector associated with each
bosonic oscillator adjacent and makes the ordering extend mechanically as
$n$ grows. Both are valid orderings; this convention is chosen for schema
consistency, not as an additional mathematical restriction.

### Explicit basis lists

For compactness, the following lists use the ordering defined above.

**C(2) = osp(2|2), $n=1$**

- Even: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`.
- Odd: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`,
  `E_eps1_del1_mm`.

**C(3) = osp(2|4), $n=2$**

- Even: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`,
  `E_del1_del2_pp`, `E_del1_del2_pm`, `E_2del1_m`, `E_2del2_m`,
  `E_del1_del2_mm`, `E_del1_del2_mp`.
- Odd: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`,
  `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`,
  `E_eps1_del2_mp`, `E_eps1_del2_mm`.

**C(4) = osp(2|6), $n=3$**

- Even: `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`,
  `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del2_pm`,
  `E_del1_del3_pp`, `E_del1_del3_pm`, `E_del2_del3_pp`,
  `E_del2_del3_pm`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`,
  `E_del1_del2_mm`, `E_del1_del2_mp`, `E_del1_del3_mm`,
  `E_del1_del3_mp`, `E_del2_del3_mm`, `E_del2_del3_mp`.
- Odd: for each $k=1,2,3$ in increasing order,
  `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`,
  `E_eps1_del{k}_mm`.

These lists have $(2n^2+n+1)$ even and $4n$ odd generators, giving
dimensions $4|4$, $11|8$, and $22|12$ for $n=1,2,3$, respectively.
