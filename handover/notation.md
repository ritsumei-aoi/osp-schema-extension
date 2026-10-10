# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.
Finalized in Issue I01.

## 1. Algebra and Oscillators

- $C(n+1) = \mathfrak{osp}(2|2n)$, bosonic rank $n$. File names use the bosonic
  rank: C(2) = osp(2|2) is `C_1_*.json`, C(3) = osp(2|4) is `C_2_*.json`, etc.
- **Standard fermionic pair** $a_1^\pm$ (labels `a_1_p`, `a_1_m`), parity 1, CAR:
  $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$.
- **Bosonic oscillators** $b_k^\pm$ (labels `b_{k}_p`, `b_{k}_m`, $k = 1,\dots,n$),
  parity 0, CCR: $[b_k^-, b_l^+] = \delta_{kl}$.
- Mixed relations (undeformed): $[b_k^\pm, a_1^\pm] = 0$.
- Central elements: $K$ (even, identified with the scalar 1; recorded for schema
  completeness only, excluded from the basis) and $\kappa$ (odd, $\kappa^2 = 0$,
  carrier of the inhomogeneous deformation).

## 2. Root System

Roots are written with $\varepsilon$ (fermionic direction) and $\delta_1,\dots,\delta_n$:
- Even roots: $\pm 2\delta_k$, $\pm(\delta_i \pm \delta_j)$ ($i<j$). Even subalgebra
  $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$, dimension $2n^2+n+1$.
- Odd roots: $\pm\varepsilon \pm \delta_k$, $4n$ in total.

## 3. Generator Labels and Oscillator Realization

Sign suffixes `p`/`m` stand for $+$/$-$. For odd generators the **first** sign
refers to $\varepsilon$ and the **second** to $\delta_k$.

| Generator label | Root | Oscillator realization | Parity |
|---|---|---|---|
| `H_eps` | — (Cartan, so(2)) | $a_1^+ a_1^- - \tfrac12$ | 0 |
| `H_{k}` ($k=1..n$) | — (Cartan, sp(2n)) | $b_k^+ b_k^- + \tfrac12$ | 0 |
| `E_2del{k}_p` | $2\delta_k$ | $(b_k^+)^2$ | 0 |
| `E_2del{k}_m` | $-2\delta_k$ | $(b_k^-)^2$ | 0 |
| `E_del{i}_del{j}_pp` ($i<j$) | $\delta_i+\delta_j$ | $b_i^+ b_j^+$ | 0 |
| `E_del{i}_del{j}_mm` ($i<j$) | $-\delta_i-\delta_j$ | $b_i^- b_j^-$ | 0 |
| `E_del{i}_del{j}_pm` ($i<j$) | $\delta_i-\delta_j$ | $b_i^+ b_j^-$ | 0 |
| `E_del{i}_del{j}_mp` ($i<j$) | $-\delta_i+\delta_j$ | $b_i^- b_j^+$ | 0 |
| `E_eps_del{k}_pp` | $\varepsilon+\delta_k$ | $a_1^+ b_k^+$ | 1 |
| `E_eps_del{k}_pm` | $\varepsilon-\delta_k$ | $a_1^+ b_k^-$ | 1 |
| `E_eps_del{k}_mp` | $-\varepsilon+\delta_k$ | $a_1^- b_k^+$ | 1 |
| `E_eps_del{k}_mm` | $-\varepsilon-\delta_k$ | $a_1^- b_k^-$ | 1 |

**Constant shifts in the Cartan generators.** $H_{k} = b_k^+ b_k^- + \tfrac12$ and
$H_{eps} = a_1^+ a_1^- - \tfrac12$ are chosen so that the algebra closes without an
identity element, e.g.
$[E_{-2\delta_k}, E_{2\delta_k}] = 4H_k$ and
$\{E_{\varepsilon+\delta_k}, E_{-\varepsilon-\delta_k}\} = H_k - H_{eps}$,
$\{E_{\varepsilon-\delta_k}, E_{-\varepsilon+\delta_k}\} = H_k + H_{eps}$.

## 4. Basis Lists and PBW Ordering

**PBW ordering (decided in I01)**: $\kappa <$ [odd] $<$ [even], matching the
B(0,n) v5.0 convention. ($K = 1$ is excluded.)

Odd basis (order: $a_1^+$ block then $a_1^-$ block, each with $\delta$-sign $+$ then $-$, $k$ ascending):
```
E_eps_del1_pp, ..., E_eps_del{n}_pp,
E_eps_del1_pm, ..., E_eps_del{n}_pm,
E_eps_del1_mp, ..., E_eps_del{n}_mp,
E_eps_del1_mm, ..., E_eps_del{n}_mm
```

Even basis (order: Cartan, raising, lowering, mixed — matching B(0,n)):
```
H_eps, H_1, ..., H_n,
E_2del1_p, ..., E_2del{n}_p,
E_del{i}_del{j}_pp (i<j, lexicographic),
E_2del1_m, ..., E_2del{n}_m,
E_del{i}_del{j}_mm (i<j),
E_del{i}_del{j}_pm (i<j),
E_del{i}_del{j}_mp (i<j)
```

Oscillator word ordering inside realizations: `a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m`.

### Concrete basis lists

**C(2) = osp(2|2), n=1** — even (4): `H_eps, H_1, E_2del1_p, E_2del1_m`;
odd (4): `E_eps_del1_pp, E_eps_del1_pm, E_eps_del1_mp, E_eps_del1_mm`. Total 8.

**C(3) = osp(2|4), n=2** — even (11): `H_eps, H_1, H_2, E_2del1_p, E_2del2_p,
E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`;
odd (8): `E_eps_del1_pp, E_eps_del2_pp, E_eps_del1_pm, E_eps_del2_pm,
E_eps_del1_mp, E_eps_del2_mp, E_eps_del1_mm, E_eps_del2_mm`. Total 19.

**C(4) = osp(2|6), n=3** — even (22): `H_eps, H_1, H_2, H_3, E_2del1_p, E_2del2_p,
E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m,
E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm,
E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`;
odd (12): `E_eps_del1_pp, E_eps_del2_pp, E_eps_del3_pp, E_eps_del1_pm,
E_eps_del2_pm, E_eps_del3_pm, E_eps_del1_mp, E_eps_del2_mp, E_eps_del3_mp,
E_eps_del1_mm, E_eps_del2_mm, E_eps_del3_mm`. Total 34.

## 5. Deformation Parameters (gb)

The inhomogeneous deformation is parametrized by $4n$ parity-1 parameters
$\mathrm{gb}_{\sigma, j, s}$, $\sigma, s \in \{+,-\}$, $j = 1..n$, via
$[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$.
JSON label: `gb_{σ}_{j}_{s}` with σ/s rendered as `p`/`m`
(e.g. `gb_p_1_m` $= \mathrm{gb}_{a_1^+, b_1^-}$).

In computations the gb symbols are treated as formal central scalar coefficients
attached to $\kappa$ (first order in $\kappa$, $\kappa^2 = 0$); see I05 response
for the bookkeeping convention.
