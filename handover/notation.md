# Notation and Terminology

This document defines the basis and oscillator-label conventions for
$C(n+1)=\mathfrak{osp}(2|2n)$ used throughout this repository.

## Root and generator labels

Use $\varepsilon$ for the $\mathfrak{so}(2)$ direction and
$\delta_1,\ldots,\delta_n$ for the $\mathfrak{sp}(2n)$ directions. The Cartan
generators are `H_1` through `H_{n+1}`. The even root generators are labelled:

| Root | Label | Oscillator realization |
|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ |
| $-\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ |
| $-\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ |

The odd root labels use `E_eps1_del{k}_{xy}`, with `x` the sign of
$\varepsilon$ and `y` the sign of $\delta_k$:

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+b_k^+$ |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+b_k^-$ |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^-b_k^+$ |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^-b_k^-$ |

Here `a_1_p` and `a_1_m` denote $a_1^+$ and $a_1^-$, and `b_k_p` and
`b_k_m` denote $b_k^+$ and $b_k^-$. The fermions are odd and obey
$\{a_1^-,a_1^+\}=1$; the bosons are even and obey
$[b_i^-,b_j^+]=\delta_{ij}$. Thus all `E_eps1_del...` generators are odd,
and the Cartan and `E_del...`/`E_2del...` generators are even.

## Basis lists

For any rank $n$, the even basis consists of `H_1` through `H_{n+1}`,
`E_2del{k}_p/m` for $1\leq k\leq n$, and all four
`E_del{i}_del{j}_{pp,pm,mp,mm}` labels for $1\leq i<j\leq n`.
The odd basis consists of all four `E_eps1_del{k}_{pp,pm,mp,mm}` labels for
$1\leq k\leq n$. Their dimensions are respectively $2n^2+n+1$ and $4n$.
Explicit lists (in PBW order) for the first three ranks are:

### C(2) = osp(2|2), n=1

- Even: `E_2del1_m, H_1, H_2, E_2del1_p`
- Odd: `E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del1_pm, E_eps1_del1_pp`
- Dimensions: 4 even, 4 odd, 8 total.

### C(3) = osp(2|4), n=2

- Even: `E_del1_del2_mp, E_del1_del2_mm, E_2del1_m, E_2del2_m, H_1, H_2, H_3, E_del1_del2_pm, E_del1_del2_pp, E_2del1_p, E_2del2_p`
- Odd: `E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del1_pm, E_eps1_del1_pp, E_eps1_del2_pm, E_eps1_del2_pp`
- Dimensions: 11 even, 8 odd, 19 total.

### C(4) = osp(2|6), n=3

- Even: `E_del1_del2_mp, E_del1_del2_mm, E_del1_del3_mp, E_del1_del3_mm, E_del2_del3_mp, E_del2_del3_mm, E_2del1_m, E_2del2_m, E_2del3_m, H_1, H_2, H_3, H_4, E_del1_del2_pm, E_del1_del2_pp, E_del1_del3_pm, E_del1_del3_pp, E_del2_del3_pm, E_del2_del3_pp, E_2del1_p, E_2del2_p, E_2del3_p`
- Odd: `E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del3_mp, E_eps1_del3_mm, E_eps1_del1_pm, E_eps1_del1_pp, E_eps1_del2_pm, E_eps1_del2_pp, E_eps1_del3_pm, E_eps1_del3_pp`
- Dimensions: 22 even, 12 odd, 34 total.

## PBW ordering

Two applicable total-order conventions were considered:

1. Put all odd root generators first, followed by Cartan and even root
   generators, mirroring the B(0,n) schema's parity-grouped convention.
2. Use triangular root order: negative roots, Cartan generators, then positive
   roots, with a fixed ordering within each group.

Use option 2. It follows the positive system with positive odd roots
$\varepsilon\pm\delta_k$ and positive even roots $\delta_i\pm\delta_j$
($i<j$) and $2\delta_k$, and makes the root-space ordering explicit for
bracket and schema generation. The full ordering used in the lists above is:

1. Negative odd roots: for increasing $k$, suffixes `mp`, then `mm`.
2. Negative even roots: for increasing $(i,j)$, suffixes `mp`, then `mm`;
   then `E_2del{k}_m` for increasing $k$.
3. Cartan: `H_1` through `H_{n+1}`.
4. Positive even roots: for increasing $(i,j)$, suffixes `pm`, then `pp`;
   then `E_2del{k}_p` for increasing $k$.
5. Positive odd roots: for increasing $k$, suffixes `pm`, then `pp`.

The identity $K=1$ is not a basis generator. Any formal extension symbol such
as $\kappa$ is recorded separately from the basis of $C(n+1)$.
