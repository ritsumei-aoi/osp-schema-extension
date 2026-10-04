# Notation and Terminology

This document defines the mathematical notation and terminology used in this
repository for the $C(n+1)=\mathfrak{osp}(2|2n)$ schema extension.

## Root and oscillator labels

- $\varepsilon$ denotes the orthogonal direction for the $\mathfrak{so}(2)$
  factor; $\delta_1,\ldots,\delta_n$ denote the directions for
  $\mathfrak{sp}(2n)$.
- The standard fermion labels are `a_1_p` and `a_1_m`, representing
  $a_1^+$ and $a_1^-$, with parity 1 and
  $\{a_1^-,a_1^+\}=1$. Bosons `b_k_p` and `b_k_m` represent $b_k^+$ and
  $b_k^-$.
- Even Cartan generators are `H_1` through `H_{n+1}`. The remaining even
  root generators are `E_2del{k}_p/m` for $\pm2\delta_k$ and
  `E_del{i}_del{j}_pp/pm/mp/mm` for the four roots
  $\pm\delta_i\pm\delta_j$ with $i<j$. In the latter label, the first sign
  is the coefficient of $\delta_i$ and the second is that of $\delta_j`;
  `p` means plus and `m` means minus.
- The odd root generators are `E_eps1_del{k}_pp/pm/mp/mm`. The first
  suffix is the coefficient sign of $\varepsilon$, the second that of
  $\delta_k`; the four labels represent respectively
  $\varepsilon+\delta_k$, $\varepsilon-\delta_k$,
  $-\varepsilon+\delta_k$, and $-\varepsilon-\delta_k$.
- With $1\leq i<j\leq n$, the even basis is
  $H_1,\ldots,H_{n+1}$ together with the $2n$ generators for
  $\pm2\delta_k$ and the $4\binom n2$ generators for
  $\pm\delta_i\pm\delta_j$. Its dimension is $2n^2+n+1$.
  The odd basis consists of the four $\varepsilon,\delta_k$ combinations
  for each $k$, and has dimension $4n$.

## Explicit bases

The following lists use the labels above; `i<j` indicates all such pairs.

| Algebra | Even basis | Odd basis |
|---|---|---|
| $C(2)$, $n=1$ | `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m` | `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm` |
| $C(3)$, $n=2$ | `H_1`, `H_2`, `H_3`; `E_2del1_p/m`, `E_2del2_p/m`; `E_del1_del2_pp`, `E_del1_del2_pm`, `E_del1_del2_mp`, `E_del1_del2_mm` | For each `k=1,2`: `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm` |
| $C(4)$, $n=3$ | `H_1`, `H_2`, `H_3`, `H_4`; `E_2del{k}_p/m` for `k=1,2,3`; `E_del{i}_del{j}_pp/pm/mp/mm` for `(i,j)=(1,2),(1,3),(2,3)` | For each `k=1,2,3`: `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm` |

These lists have respectively even/odd dimensions $4|4$, $11|8$, and
$22|12$.

## PBW ordering

Two deterministic total-order choices are:

1. A parity-block order, `κ < [all odd root generators] < [all even
   generators]`, following the organization of the B(0,n) schema.
2. A root-triangular order, `κ < [negative-root generators] < [Cartan
   generators] < [positive-root generators]`.

Use option 2. Take the positive odd roots to be
$\varepsilon\pm\delta_k$ and the positive even roots to be $2\delta_k$ and
$\delta_i\pm\delta_j$ ($i<j$). Within each negative- or positive-root block,
order the even roots first (increasing index, then `2del` before
`del_i_del_j`, and suffix order `pp`, `pm`, `mp`, `mm`), followed by odd
roots in increasing $k$ and suffix order `pp`, `pm`, `mp`, `mm`. Order the
Cartan generators as `H_1` through `H_{n+1}`. Thus the odd negative block
uses the `mp`, `mm` labels and the odd positive block uses `pp`, `pm`.
This is an ordering convention for PBW monomials, not an assertion that
generators within a block commute.

The even central symbol `K` is identified with the scalar identity and is not
an independent basis element. The odd central symbol `κ` is recorded
separately and precedes the algebra generators in the PBW convention.
