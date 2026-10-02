# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
The conventions below describe the finite-dimensional Lie superalgebra
$C(n+1)=\mathfrak{osp}(2|2n)$ and its oscillator realization.

## Conventions

### Roots and parity

Use $\varepsilon$ for the one-dimensional orthogonal direction and
$\delta_1,\ldots,\delta_n$ for the symplectic directions. The even roots are
$\pm2\delta_i$ and $\pm\delta_i\pm\delta_j$ for $i<j$. The odd roots are
$\pm\varepsilon\pm\delta_i$. The Cartan basis is
$H_1,\ldots,H_{n+1}$, so the even dimension is $n+1+2n^2$ and the odd
dimension is $4n$.

For concise generator labels, `_p` and `_m` mean plus and minus,
respectively. The first suffix in an odd-root label is the sign of
$\varepsilon$; the second is the sign of $\delta_i$. Thus:

| Root | Generator label |
|---|---|
| $\varepsilon+\delta_i$ | `E_eps1_del{i}_pp` |
| $\varepsilon-\delta_i$ | `E_eps1_del{i}_pm` |
| $-\varepsilon+\delta_i$ | `E_eps1_del{i}_mp` |
| $-\varepsilon-\delta_i$ | `E_eps1_del{i}_mm` |

For even roots use `E_2del{i}_p/m` for $\pm2\delta_i$. For $i<j$, use
`E_del{i}_del{j}_pp`, `_pm`, `_mp`, and `_mm` for
$\delta_i+\delta_j$, $\delta_i-\delta_j$, $-\delta_i+\delta_j$, and
$-\delta_i-\delta_j$, respectively. The index convention $i<j$ prevents
duplicate labels.

The complete generator lists for the first three ranks are:

| Algebra | Even basis | Odd basis |
|---|---|---|
| $C(2)$ ($n=1$) | `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m` | `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm` |
| $C(3)$ ($n=2$) | `H_1`–`H_3`, `E_2del1_p/m`, `E_2del2_p/m`, `E_del1_del2_pp/pm/mp/mm` | `E_eps1_del1_pp/pm/mp/mm`, `E_eps1_del2_pp/pm/mp/mm` |
| $C(4)$ ($n=3$) | `H_1`–`H_4`, `E_2del{i}_p/m` ($i=1,2,3$), and `E_del{i}_del{j}_pp/pm/mp/mm` ($1\le i<j\le3$) | `E_eps1_del{i}_pp/pm/mp/mm` ($i=1,2,3$) |

These lists have dimensions $4|4$, $11|8$, and $22|12$, respectively.
`K` (the even central identity) and `κ` (the odd deformation parameter)
belong to the extension conventions, not to the basis of $\mathfrak g$.

### PBW order

Two deterministic choices are useful:

1. Put all odd generators first, then all even generators, matching the
   repository's B(0,n) schema convention. Within each block order Cartan
   generators by increasing index, then root generators by increasing
   indices and suffix order `pp`, `pm`, `mp`, `mm`; put doubled roots before
   paired-index roots. An extension symbol `κ`, when present, precedes the
   $\mathfrak g$ generators; `K=1` is not an independent basis element.
2. Order root generators by a fixed positive-root system, with negative-root
   generators first, Cartan generators next, and positive-root generators
   last; this interleaves even and odd generators.

Use choice 1 for schema basis arrays. Any total ordering of a homogeneous
basis gives a PBW monomial convention, and this choice preserves the existing
schema layout while making array order reproducible. Choice 2 is a valid
root-triangular alternative but is not used for these schema arrays.

### Oscillators and Cartan generators

Use bosonic labels `b_{i}_p` and `b_{i}_m` for $b_i^+$ and $b_i^-$, and
fermionic labels `a_1_p` and `a_1_m` for $a_1^+$ and $a_1^-$. The fermions
have parity 1 and satisfy $\{a_1^-,a_1^+\}=1$; bosons have parity 0 and
satisfy $[b_i^-,b_j^+]=\delta_{ij}$. In the undeformed oscillator algebra,
bosons commute with fermions.

The oscillator realization uses
$H_1=a_1^+a_1^-+b_1^+b_1^-$,
$H_k=b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ for $2\le k\le n$, and
$H_{n+1}=-b_n^+b_n^- - \tfrac12$. Even-root generators are quadratic
bosonic words. Odd-root generators are
$E_{\varepsilon\pm\delta_i}=a_1^+b_i^\pm$ and
$E_{-\varepsilon\pm\delta_i}=a_1^-b_i^\pm$.
