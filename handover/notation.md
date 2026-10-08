# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

## C(n+1) = osp(2|2n) conventions

Use `eps1` for the single orthogonal weight \(\varepsilon\) and `del{k}` for
\(\delta_k\). The Cartan basis is `H_1` through `H_{n+1}`. Even root
generators use the same labels as the B(0,n) schema:

| Root | Label |
|---|---|
| \(2\delta_k\), \(-2\delta_k\) | `E_2del{k}_p`, `E_2del{k}_m` |
| \(\delta_i+\delta_j\), \(-\delta_i-\delta_j\) | `E_del{i}_del{j}_pp`, `E_del{i}_del{j}_mm` |
| \(\delta_i-\delta_j\), \(-\delta_i+\delta_j\) | `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp` |

Here \(i<j\). Odd roots and their labels are:

| Root | Label |
|---|---|
| \(\varepsilon+\delta_k\), \(\varepsilon-\delta_k\) | `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm` |
| \(-\varepsilon+\delta_k\), \(-\varepsilon-\delta_k\) | `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm` |

The first suffix sign records the coefficient of \(\varepsilon\), and the
second the coefficient of \(\delta_k\); `p` means plus and `m` means minus.
In oscillator realizations the corresponding odd words are
`a_1_p b_k_p`, `a_1_p b_k_m`, `a_1_m b_k_p`, and `a_1_m b_k_m`.

For a given \(n\), list the even basis in this order:
`H_1, ..., H_{n+1}`, then `E_2del{k}_p` for increasing \(k\), then
`E_del{i}_del{j}_pp` in lexicographic \((i,j)\) order, then
`E_2del{k}_m`, then `E_del{i}_del{j}_mm`, `E_del{i}_del{j}_pm`, and
`E_del{i}_del{j}_mp` (each pair-group in lexicographic order).
The odd basis is ordered by increasing \(k\), with the four labels
`E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`,
`E_eps1_del{k}_mm` for each \(k\).

### Explicit basis lists

**C(2), \(n=1\)** — even:
`H_1, H_2, E_2del1_p, E_2del1_m`; odd:
`E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`.

**C(3), \(n=2\)** — even:
`H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`;
odd:
`E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm`.

**C(4), \(n=3\)** — even:
`H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`;
odd:
`E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del3_mp, E_eps1_del3_mm`.

### PBW ordering

Two compatible choices are:

1. Keep the B(0,n) parity-block convention, with \(\kappa\) first, followed
   by all odd root generators and then all even basis generators. Use the
   canonical within-parity orders above.
2. Use root-triangular order: negative-root generators, Cartan generators,
   positive-root generators, with a fixed order within each group.

This project adopts option 1 for schema ordering because it preserves the
existing B(0,n) schema convention and makes the C(n+1) extension comparable.
The PBW order is `κ < [odd basis] < [even basis]`; \(K=1\) is excluded as an
independent basis element.
