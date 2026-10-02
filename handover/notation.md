# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

## C(n+1) = osp(2|2n) conventions

### Cartan and root labels

Use the Cartan generators `H_1, ..., H_{n+1}`. The even root generators keep
the B(0,n) labels:

| Root | Generator label |
|---|---|
| $2\delta_k$ | `E_2del{k}_p` |
| $-2\delta_k$ | `E_2del{k}_m` |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` |
| $-(\delta_i-\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` |
| $-(\delta_i+\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` |

The four odd root labels encode the signs of $\varepsilon$ first and
$\delta_k$ second:

| Root | Generator label | Oscillator realization |
|---|---|---|
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | `a_1_p b_{k}_p` |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | `a_1_p b_{k}_m` |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | `a_1_m b_{k}_p` |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | `a_1_m b_{k}_m` |

`a_1_p` and `a_1_m` are the standard fermionic pair, and `b_k_p` and
`b_k_m` are bosonic oscillators. The even root generators use the
oscillator realizations specified in `docs/math/Cn1_definition.md`.

### Basis and dimensions

For every $n\geq1$, the even basis is ordered as:

1. `H_1, ..., H_{n+1}`;
2. `E_2del{k}_p` for increasing $k$, followed by `E_del{i}_del{j}_pp` and
   `E_del{i}_del{j}_pm` for lexicographically increasing pairs $i<j$;
3. `E_2del{k}_m` for increasing $k$, followed by `E_del{i}_del{j}_mm` and
   `E_del{i}_del{j}_mp` for lexicographically increasing pairs $i<j$.

The odd basis is ordered as all `E_eps1_del{k}_pp`, then all
`E_eps1_del{k}_pm`, then all `E_eps1_del{k}_mp`, then all
`E_eps1_del{k}_mm`, with increasing $k$ within each group.
The resulting dimensions are even $2n^2+n+1$ and odd $4n$.

| Algebra | Even basis | Odd basis |
|---|---|---|
| C(2), $n=1$ | `H_1, H_2, E_2del1_p, E_2del1_m` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm` |
| C(3), $n=2$ | `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_del1_del2_pm, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_mp` | `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm` |
| C(4), $n=3$ | `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp` | `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm` |

### PBW ordering

The selected total order is `κ < [all odd root generators in the order above]
< [all even generators in the order above]`. The central identity `K` is the
scalar $1$, not an independent basis element, and is omitted. This keeps the
project's established B(0,n) parity-block PBW convention and changes only the
odd-root block when passing to C(n+1).

An alternative is root-height order: positive roots, Cartan generators, then
negative roots, with a fixed order within each height and parity. That is a
valid PBW order too, but it would reorganize the inherited B(0,n) basis and
complicate comparisons across the two schemas; therefore the parity-block
order above is preferred.
