# Notation and Terminology

This document defines the mathematical notation and generator-label conventions
used for the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension.

## Oscillator labels

- `a_1_p` and `a_1_m` denote the standard fermionic oscillators $a_1^+$ and
  $a_1^-$, with parity 1 and $\{a_1^-,a_1^+\}=1$.
- `b_k_p` and `b_k_m` denote bosonic oscillators $b_k^+$ and $b_k^-$, with
  $[b_k^-,b_l^+]=\delta_{kl}$.

## Cartan and root-generator labels

Use `H_1, ..., H_{n+1}` for the Cartan generators. Even root labels retain the
B(0,n) schema convention:

| Label | Root |
|---|---|
| `E_2del{k}_p` | $2\delta_k$ |
| `E_2del{k}_m` | $-2\delta_k$ |
| `E_del{i}_del{j}_pp` (`i<j`) | $\delta_i+\delta_j$ |
| `E_del{i}_del{j}_pm` (`i<j`) | $\delta_i-\delta_j$ |
| `E_del{i}_del{j}_mp` (`i<j`) | $-\delta_i+\delta_j$ |
| `E_del{i}_del{j}_mm` (`i<j`) | $-\delta_i-\delta_j$ |

Odd root labels are `E_eps1_del{k}_{xy}`. The first suffix character gives the
sign of $\varepsilon$ (`p` for $+$, `m` for $-$); the second gives the sign of
$\delta_k$ (`p` for $+$, `m` for $-$):

| Label | Root |
|---|---|
| `E_eps1_del{k}_pp` | $\varepsilon+\delta_k$ |
| `E_eps1_del{k}_pm` | $\varepsilon-\delta_k$ |
| `E_eps1_del{k}_mp` | $-\varepsilon+\delta_k$ |
| `E_eps1_del{k}_mm` | $-\varepsilon-\delta_k$ |

The Cartan generators and even root generators have parity 0; the odd-root
generators have parity 1. The even and odd basis dimensions are
$2n^2+n+1$ and $4n$, respectively.

## Basis lists for C(2), C(3), and C(4)

The lists below use the PBW ordering finalized for this project.

| Algebra | Even basis | Odd basis |
|---|---|---|
| C(2), `n=1` | `H_1, H_2, E_2del1_p, E_2del1_m` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm` |
| C(3), `n=2` | `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_del1_del2_pm, E_2del1_m, E_2del2_m, E_del1_del2_mp, E_del1_del2_mm` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm` |
| C(4), `n=3` | `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del2_pm, E_del1_del3_pp, E_del1_del3_pm, E_del2_del3_pp, E_del2_del3_pm, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mp, E_del1_del2_mm, E_del1_del3_mp, E_del1_del3_mm, E_del2_del3_mp, E_del2_del3_mm` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del3_mp, E_eps1_del3_mm` |

`K` (the scalar identity) and the extension symbol `κ` are not members of
these finite-dimensional Lie-superalgebra basis lists.

## PBW ordering

The approved PBW ordering places the odd block before the even block:

1. All odd generators, ordered by increasing `k`; for each `k`, use suffix
   order `pp`, `pm`, `mp`, `mm`.
2. The even block: `H_1, ..., H_{n+1}`; then `E_2del{k}_p` in increasing `k`;
   then the positive pair-root generators `E_del{i}_del{j}_pp` and
   `E_del{i}_del{j}_pm` in lexicographic `(i,j)` order; then `E_2del{k}_m` in
   increasing `k`; finally the negative pair-root generators
   `E_del{i}_del{j}_mp` and `E_del{i}_del{j}_mm` in lexicographic `(i,j)` order.

Thus the block order is `[odd] < [even]`. Neither `K` nor `κ` is included in
this ordering.
