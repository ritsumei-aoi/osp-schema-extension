# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project and finalized in Issue I01.

## 1. Algebra and Rank Conventions

- $C(n+1) = \mathfrak{osp}(2|2n)$, with bosonic rank $n$ (so $C(2)$ has $n=1$, $C(3)$ has $n=2$, $C(4)$ has $n=3$).
- $\dim \mathfrak{g}_{\bar 0} = 2n^2+n+1$, $\dim \mathfrak{g}_{\bar 1} = 4n$, total $2n^2+5n+1$.

## 2. Oscillators

| Symbol | Meaning | Parity |
|---|---|---|
| $a_1^+$, $a_1^-$ | standard fermion pair, $\{a_1^-, a_1^+\}=1$ | 1 |
| $b_k^+$, $b_k^-$ ($k=1,\dots,n$) | bosonic oscillators, $[b_k^-, b_l^+]=\delta_{kl}$ | 0 |
| $\kappa$ | odd central element, $\kappa^2=0$ | 1 |
| $K$ | even central element, identified with the scalar 1 | 0 |

The supplementary fermion $a_0$ of B(0,n) is absent.

## 3. Root Labels

Roots are written with $\varepsilon$ (fermionic) and $\delta_k$ (bosonic):

- Odd roots: $\pm\varepsilon \pm \delta_k$, $k=1,\dots,n$ (4n roots).
- Even roots: $\pm 2\delta_k$ and $\pm(\delta_i \pm \delta_j)$ with $i<j$.
- Even Cartan: $n+1$ elements, $H_1,\dots,H_{n+1}$.

## 4. Basis Lists (Finalized)

### C(2), n=1 (dim 8: even 4, odd 4)

- Even: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- Odd: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

### C(3), n=2 (dim 19: even 11, odd 8)

- Even: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del1_m`, `E_2del2_p`, `E_2del2_m`, `E_del1_del2_pp`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
- Odd: `E_eps1_del1_{pp,pm,mp,mm}`, `E_eps1_del2_{pp,pm,mp,mm}`

### C(4), n=3 (dim 34: even 22, odd 12)

- Even: `H_1`..`H_4` (4), `E_2del{k}_{p,m}` for $k=1,2,3$ (6), `E_del{i}_del{j}_{pp,pm,mp,mm}` for $i<j$ (12)
- Odd: `E_eps1_del{k}_{pp,pm,mp,mm}` for $k=1,2,3$ (12)

## 5. Generator Label Convention

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |

Suffix rule: `p` means a raising (`+`) oscillator, `m` means a lowering (`-`) oscillator. In two-index labels the first suffix refers to the first index.

Cartan labels: `H_k` for $k=1,\dots,n+1$, with
- $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$ (the $\mathfrak{so}(2)$ direction combined with $\mathfrak{sp}$),
- $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $2\le k\le n$,
- $H_{n+1} = -b_n^+ b_n^- - \tfrac12$.

For $n=1$, $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$ and $H_2 = -b_1^+ b_1^- - \tfrac12$.

## 6. PBW Ordering (Finalized)

Ordering: $\kappa < [\text{odd}] < [\text{even}]$, with $K$ excluded (as in B(0,n)).

Within each block the order is lexicographic by (index $k$, sign pattern in the order `pp < pm < mp < mm`), with the Cartan generators first in the even block.

Options considered:
- **(A) odd-first, then even** (chosen): matches the B(0,n) convention `κ < [odd] < [even]`. Keeps Schema 1 fields (`basis.odd`, `basis.even`) structurally identical to B(0,n), which eases compatibility.
- **(B) even-first, then odd**: mathematically equivalent PBW basis, but breaks the parallel with B(0,n) and changes the position of the odd block in every JSON key.
- **(C) ε-roots interleaved with δ-roots by height**: gives a natural grading but makes the ordering depend on a height function that is not a schema-level key. Rejected for simplicity.

Reason for (A): the only ε-dependent part is the odd block, so the change from B(0,n) is confined to replacing the `E_del{k}_p/m` entries by the 4n `E_eps1_*` entries.

## 7. Terminology

- **Inhomogeneous deformation**: $[X,Y]_\gamma = [X,Y]_0 + \kappa\,\gamma(X,Y)$.
- **gb matrix**: the $2\times 2n$ array of parity-1 parameters $\mathrm{gb}_{\sigma,j,s}$ with $\sigma\in\{+,-\}$ (fermion index), $j=1,\dots,n$, $s\in\{+,-\}$ (boson sign). Total $4n$ parameters.
- **Coboundary**: $\delta f$ for an odd linear map $f$ (see `docs/math/C_coboundary_definition.md`).
