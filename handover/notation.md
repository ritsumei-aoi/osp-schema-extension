# Notation and Terminology

This document defines the mathematical notation and terminology used in this
repository for the $C(n+1)=\mathfrak{osp}(2|2n)$ schema extension.

## Roots and generator labels

Use $\varepsilon$ for the orthogonal direction of the $\mathfrak{so}(2)$
factor and $\delta_1,\ldots,\delta_n$ for the symplectic directions. The even
roots are $\pm2\delta_i$ and $\pm\delta_i\pm\delta_j$ ($i<j$); the odd roots
are $\pm\varepsilon\pm\delta_k$.

The Cartan generators are `H_1` through `H_{n+1}`. Even root generators use:

| Root | Label | Oscillator realization |
|---|---|---|
| $2\delta_i$ | `E_2del{i}_p` | `(b_i_p)^2` |
| $-2\delta_i$ | `E_2del{i}_m` | `(b_i_m)^2` |
| $\delta_i+\delta_j$, $i<j$ | `E_del{i}_del{j}_pp` | `b_i_p b_j_p` |
| $\delta_i-\delta_j$, $i<j$ | `E_del{i}_del{j}_pm` | `b_i_p b_j_m` |
| $-\delta_i+\delta_j$, $i<j$ | `E_del{i}_del{j}_mp` | `b_i_m b_j_p` |
| $-\delta_i-\delta_j$, $i<j$ | `E_del{i}_del{j}_mm` | `b_i_m b_j_m` |

For odd generators, the first sign specifies the coefficient of $\varepsilon$
and the second the coefficient of $\delta_k$:

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | `a_1_p b_k_p` |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | `a_1_p b_k_m` |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | `a_1_m b_k_p` |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | `a_1_m b_k_m` |

The fermionic generators `a_1_p` and `a_1_m` are a standard CAR pair,
$\{a_1_m,a_1_p\}=1$; `b_i_p` and `b_i_m` are bosonic creation and annihilation
generators with $[b_i_m,b_j_p]=\delta_{ij}$. The odd root generators have
parity 1; Cartan and even-root generators have parity 0.

## Basis lists and PBW ordering

For every positive integer $n$, the even basis consists of
`H_1,...,H_{n+1}`, `E_2del{i}_p/m` for $1<=i<=n`, and
`E_del{i}_del{j}_{pp,pm,mp,mm}` for every $1<=i<j<=n$. The odd basis consists
of `E_eps1_del{k}_{pp,pm,mp,mm}` for every $1<=k<=n`. Thus the dimensions are
$2n^2+n+1$ even and $4n$ odd.

The explicit bases are:

| Algebra | Even basis | Odd basis |
|---|---|---|
| $C(2)$ ($n=1$) | `H_1, H_2, E_2del1_p, E_2del1_m` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm` |
| $C(3)$ ($n=2$) | `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_del1_del2_pm, E_del1_del2_mp, E_del1_del2_mm, E_2del1_m, E_2del2_m` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm` |
| $C(4)$ ($n=3$) | `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del2_pm, E_del1_del2_mp, E_del1_del2_mm, E_del1_del3_pp, E_del1_del3_pm, E_del1_del3_mp, E_del1_del3_mm, E_del2_del3_pp, E_del2_del3_pm, E_del2_del3_mp, E_del2_del3_mm, E_2del1_m, E_2del2_m, E_2del3_m` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del3_mp, E_eps1_del3_mm` |

Two consistent PBW choices are (1) put the complete even basis before the odd
basis, or (2) put the complete odd basis before the complete even basis.
Choose option 2: `κ < [odd generators] < [even generators]`, with $K=1$
excluded from the basis. Within the odd block order by increasing $k$, then
`pp, pm, mp, mm`. Within the even block order the Cartan generators first,
then positive roots (`2δ_i`, followed by `δ_i+δ_j` and `δ_i-δ_j` for increasing
indices), then negative roots (`-2δ_i`, followed by `-δ_i-δ_j` and
`-δ_i+δ_j` for increasing indices). This keeps the odd/even PBW blocks
explicit and the root labels in a deterministic order.
