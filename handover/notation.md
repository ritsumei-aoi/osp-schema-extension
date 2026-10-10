# Notation and Terminology

This document records the conventions for the $C(n+1)=\mathfrak{osp}(2|2n)$
schema extension.

## Root and oscillator notation

Write the roots using $\varepsilon,\delta_1,\ldots,\delta_n$. The even roots
are $\pm2\delta_k$ and $\pm\delta_i\pm\delta_j$ for $i<j$; the odd roots are
$\pm\varepsilon\pm\delta_k$. The Cartan basis is
$H_1,\ldots,H_{n+1}$. Thus
$\dim\mathfrak{g}_{\bar 0}=2n^2+n+1$ and
$\dim\mathfrak{g}_{\bar 1}=4n$.

The oscillator labels use `p` for $+$ and `m` for $-$:

- Fermions: `a_1_p`, `a_1_m`, with
  $\{a_{1,m},a_{1,p}\}=1$ and
  $\{a_{1,p},a_{1,p}\}=\{a_{1,m},a_{1,m}\}=0$.
- Bosons: `b_k_p`, `b_k_m` for $1\le k\le n$, with
  $[b_{i,m},b_{j,p}]=\delta_{ij}$ and like-sign bosonic commutators zero.
  Bosons commute with the fermions.

For `i < j`, the even-root generator labels retain the existing B(0,n)
convention:

| Label | Root |
|---|---|
| `E_2del{k}_p` / `E_2del{k}_m` | $\pm2\delta_k$ |
| `E_del{i}_del{j}_pp` | $\delta_i+\delta_j$ |
| `E_del{i}_del{j}_pm` | $\delta_i-\delta_j$ |
| `E_del{i}_del{j}_mp` | $-\delta_i+\delta_j$ |
| `E_del{i}_del{j}_mm` | $-\delta_i-\delta_j$ |

Odd-root labels are `E_eps1_del{k}_XY`, where `X` is the
$\varepsilon$ sign and `Y` is the $\delta_k$ sign:

| Label suffix | Root | Oscillator realization |
|---|---|---|
| `pp` | $\varepsilon+\delta_k$ | `a_1_p b_k_p` |
| `pm` | $\varepsilon-\delta_k$ | `a_1_p b_k_m` |
| `mp` | $-\varepsilon+\delta_k$ | `a_1_m b_k_p` |
| `mm` | $-\varepsilon-\delta_k$ | `a_1_m b_k_m` |

The uniform all-root oscillator expressions for the even root generators are
$E_{\pm2\delta_k}=(b_k^\pm)^2$ and
$E_{\pm\delta_i\pm\delta_j}=b_i^\pm b_j^\pm$, with signs interpreted
independently. Cartan oscillator expressions are
$H_1=a_{1,p}a_{1,m}+b_{1,p}b_{1,m}$,
$H_k=b_{k-1,p}b_{k-1,m}-b_{k,p}b_{k,m}$ for $2\le k\le n$, and
$H_{n+1}=-b_{n,p}b_{n,m}-\tfrac12$.
Simple-generator expressions may use normalization factors as specified in
`docs/math/Cn1_definition.md`; these do not change the root-to-label mapping.

## Basis lists

For general $n$, the even basis is `H_1` through `H_{n+1}`, followed by
`E_2del{k}_p/m` for $1\le k\le n$ and the four pair-root labels
`E_del{i}_del{j}_pp/pm/mp/mm` for each $1\le i<j\le n`. The odd basis has
`E_eps1_del{k}_pp/pm/mp/mm` for each $1\le k\le n`.

| Algebra | Even basis | Odd basis |
|---|---|---|
| C(2), $n=1$ | `H_1, H_2, E_2del1_p, E_2del1_m` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm` |
| C(3), $n=2$ | `H_1, H_2, H_3, E_2del1_p, E_2del1_m, E_2del2_p, E_2del2_m, E_del1_del2_pp, E_del1_del2_pm, E_del1_del2_mp, E_del1_del2_mm` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm` |
| C(4), $n=3$ | `H_1, H_2, H_3, H_4, E_2del1_p, E_2del1_m, E_2del2_p, E_2del2_m, E_2del3_p, E_2del3_m, E_del1_del2_pp, E_del1_del2_pm, E_del1_del2_mp, E_del1_del2_mm, E_del1_del3_pp, E_del1_del3_pm, E_del1_del3_mp, E_del1_del3_mm, E_del2_del3_pp, E_del2_del3_pm, E_del2_del3_mp, E_del2_del3_mm` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del3_mp, E_eps1_del3_mm` |

The corresponding even/odd dimensions are $4|4$, $11|8$, and $22|12$.

## PBW ordering — approved Option A

Use the positive roots $2\delta_k$, $\delta_i+\delta_j$,
$\delta_i-\delta_j$, $\varepsilon+\delta_k$, and $\varepsilon-\delta_k$;
the negatives of these are the negative roots. Sort $k$ increasingly and
pairs $(i,j)$ lexicographically. Within a family, use the suffix ordering
shown below. The PBW sequence is:

1. `κ`, if represented; omit `K = 1` from the basis.
2. Odd positive roots: for increasing $k$, `E_eps1_del{k}_pp`, then
   `E_eps1_del{k}_pm`.
3. Odd negative roots: for increasing $k$, `E_eps1_del{k}_mp`, then
   `E_eps1_del{k}_mm`.
4. Cartan generators `H_1, ..., H_{n+1}`.
5. Positive even roots, in family order: `E_2del{k}_p` by increasing $k$;
   `E_del{i}_del{j}_pp` by lexicographic $(i,j)$; then
   `E_del{i}_del{j}_pm` by lexicographic $(i,j)$.
6. Negative even roots, in family order: `E_2del{k}_m` by increasing $k$;
   `E_del{i}_del{j}_mm` by lexicographic $(i,j)$; then
   `E_del{i}_del{j}_mp` by lexicographic $(i,j)$.

This parity-block ordering retains the B(0,n) schema's organization: central
extension symbol (when present), odd generators, then even generators. `K`
denotes the scalar identity and is not an independent PBW basis element.
