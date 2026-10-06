# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It was finalized in Issue I01 for the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension project.

## Conventions

### Indexing
- $n$ = bosonic rank. $C(n+1)=\mathfrak{osp}(2|2n)$; so $C(2)$: $n=1$, $C(3)$: $n=2$, $C(4)$: $n=3$.
- Files use $n$: `C_{n}_structure.json`.
- Graded bracket: $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$. Parity $p\in\{0,1\}$.

### Oscillators (letters used in JSON "words")
| Symbol | Label | Parity | Relation |
|---|---|---|---|
| $a_1^{\pm}$ | `a_1_p`, `a_1_m` | 1 | $\{a_1^-,a_1^+\}=1$, $(a_1^\pm)^2=0$ |
| $b_k^{\pm}$ ($1\le k\le n$) | `b_k_p`, `b_k_m` | 0 | $[b_k^-,b_l^+]=\delta_{kl}$, others commute |
| $\kappa$ | `K` (in code only; JSON key `kappa`) | 1 | $\kappa^2=0$, graded central |
| $K$ | scalar `1` | 0 | even central, identified with 1 (not a basis element) |

Oscillator-word ordering (normal form): `a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`
(κ, if present, is leftmost). Deformation: $[b_j^s,a_1^\sigma]=-\mathrm{gb}_{\sigma,j,s}\,\kappa$.

### Roots
$\Delta_{\bar0}=\{\pm2\delta_k,\ \pm\delta_i\pm\delta_j\ (i<j)\}$, $\Delta_{\bar1}=\{\pm\varepsilon\pm\delta_k\}$.

### Generator labels
Sign letters: `p` = +, `m` = −. For `E_eps1_del{k}_{e}{d}`, `e` is the sign of $\varepsilon$ and `d` the sign of $\delta_k$.

| Root | Label | Realization | Parity |
|---|---|---|---|
| Cartan, $k=1$ | `H_1` | $a_1^+a_1^-+b_1^+b_1^-$ | 0 |
| Cartan, $2\le k\le n$ | `H_k` | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ | 0 |
| Cartan, last | `H_{n+1}` | $-b_n^+b_n^- - \tfrac12$ | 0 |
| $2\delta_k$ / $-2\delta_k$ | `E_2del{k}_p` / `_m` | $(b_k^\pm)^2$ | 0 |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ | 0 |
| $-\delta_i-\delta_j$ | `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ | 0 |
| $\delta_i-\delta_j$ | `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ | 0 |
| $-\delta_i+\delta_j$ | `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ | 0 |
| $\pm\varepsilon\pm\delta_k$ | `E_eps1_del{k}_{pp,pm,mp,mm}` | $a_1^{\pm}b_k^{\pm}$ | 1 |

Note: $H_1$ carries the $\mathfrak{so}(2)$ part ($a_1^+a_1^-$); $H_2,\dots,H_{n+1}$ are $\mathfrak{sp}(2n)$ Cartan elements.

### Even / odd bases (PBW order, left to right)

Odd order: by sign of $\varepsilon$ (p before m), then sign of $\delta$ (p before m), then $k$.
Even order: $H_1..H_{n+1}$; `E_2del{k}_p`; `E_del{i}_del{j}_pp`; `E_2del{k}_m`; `E_del{i}_del{j}_mm`; `..._pm`; `..._mp` (pairs $i<j$ lexicographic).

**C(2), n=1** (4|4): odd `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`; even `H_1, H_2, E_2del1_p, E_2del1_m`.

**C(3), n=2** (11|8): odd `E_eps1_del{1,2}_pp`, `E_eps1_del{1,2}_pm`, `E_eps1_del{1,2}_mp`, `E_eps1_del{1,2}_mm` (in that order);
even `H_1,H_2,H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`.

**C(4), n=3** (22|12): odd as above with $k=1,2,3$; even
`H_1..H_4, E_2del{1,2,3}_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del{1,2,3}_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, (pm: 12,13,23), (mp: 12,13,23)`.

Counts: even $2n^2+n+1$, odd $4n$, total $2n^2+5n+1$.

### PBW ordering
$\kappa < [\text{odd}] < [\text{even}]$ with the within-block orders above ($K=1$ excluded).
Rationale and alternatives: see `docs/issues/I01.md` Response.

### Normalization
$E_{\pm2\delta_k}=(b_k^\pm)^2$ for all $k$ (no factor $\tfrac12$); see I01 Response, ambiguity A1.
