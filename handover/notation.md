# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

Finalized in Issue I01 (C(n+1) basis and root system design).

### 1. Algebra and rank

- $C(n+1) = \mathfrak{osp}(2|2n)$, $n \ge 1$. The integer `n` used in code and file
  names is the **bosonic rank** (number of boson pairs $b_k^\pm$). Hence
  C(2) ↔ `n=1`, C(3) ↔ `n=2`, C(4) ↔ `n=3`.
- Root vectors: $\varepsilon$ (one fermionic direction, written `eps1` in labels),
  $\delta_1,\dots,\delta_n$ (bosonic directions, written `del{k}`).
- Superdimension: $(2n^2+n+1)\,|\,4n$; total $2n^2+5n+1$.

### 2. Oscillators

| Label | Math | Parity | Relations |
|---|---|---|---|
| `a_1_p`, `a_1_m` | $a_1^+, a_1^-$ | 1 | CAR: $\{a_1^-,a_1^+\}=1$, $(a_1^\pm)^2=0$ |
| `b_k_p`, `b_k_m` | $b_k^+, b_k^-$ | 0 | CCR: $[b_k^-,b_l^+]=\delta_{kl}$, $[b_k^\pm,b_l^\pm]=0$ |
| `kappa` | $\kappa$ | 1 | odd central, $\kappa^2=0$ |
| `K` | $K$ | 0 | even central, identified with the scalar $1$ |

Undeformed mixed relation: $[b_k^s, a_1^\sigma]=0$.
Deformed (Schema 2): $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$.

**Oscillator normal ordering** (used for all `standard_form` words):
`a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ... < b_n_p < b_n_m`.
The odd central $\kappa$ is always moved to the far left.

### 3. Generator labels

Sign suffixes: `p` = $+$, `m` = $-$. For two-index labels the first suffix letter refers to
the first index, the second letter to the second index.

| Root | Label | Realization | Parity |
|---|---|---|---|
| Cartan | `H_1` | $a_1^+a_1^- + b_1^+b_1^-$ | 0 |
| Cartan ($2\le k\le n$) | `H_k` | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ | 0 |
| Cartan | `H_{n+1}` | $-b_n^+b_n^- - \tfrac12$ | 0 |
| $\pm 2\delta_k$ | `E_2del{k}_p` / `E_2del{k}_m` | $(b_k^\pm)^2$ | 0 |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ | 0 |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ | 0 |
| $-\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ | 0 |
| $-\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ | 0 |
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+b_k^+$ | 1 |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+b_k^-$ | 1 |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^-b_k^+$ | 1 |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^-b_k^-$ | 1 |

Notes:
- The Cartan generators follow `docs/math/Cn1_definition.md` (Frappat distinguished basis).
  Their span equals the span of $a_1^+a_1^- - \tfrac12$ and $b_k^+b_k^- + \tfrac12$, so the
  linear span of all generators is closed under the bracket **without** a $K$ term.
- $E_{\pm2\delta_k}=(b_k^\pm)^2$ follows the "all root generators" list of
  `Cn1_definition.md` and the B(0,n) label table (no factor $\tfrac12$). The Chevalley-normalised
  $\tfrac12(b_n^\pm)^2$ appearing in the simple-generator table differs only by rescaling.
- The odd label `E_eps1_del{k}_{σs}` always has its oscillator word already in normal order.

### 4. Basis lists and PBW ordering

**PBW ordering (adopted)**: $\kappa$ < [odd] < [even], with $K$ excluded (as in B(0,n) v5.0).

- odd block, grouped by sign pattern then by $k$:
  `E_eps1_del{1..n}_pp`, `E_eps1_del{1..n}_pm`, `E_eps1_del{1..n}_mp`, `E_eps1_del{1..n}_mm`
- even block (B(0,n) order with the extra Cartan): `H_1..H_{n+1}`, `E_2del{1..n}_p`,
  `E_del{i}_del{j}_pp` ($i<j$, lexicographic), `E_2del{1..n}_m`, `E_del{i}_del{j}_mm`,
  `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`.

The JSON `basis.even` / `basis.odd` lists are written in exactly this order; the global
basis index used by Schemas 2–4 is `odd + even` (odd first).

#### C(2) = osp(2|2), n = 1 (4 | 4)
- even: `H_1, H_2, E_2del1_p, E_2del1_m`
- odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

#### C(3) = osp(2|4), n = 2 (11 | 8)
- even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m,
  E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm,
  E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

#### C(4) = osp(2|6), n = 3 (22 | 12)
- even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp,
  E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm,
  E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp,
  E_del1_del3_mp, E_del2_del3_mp`
- odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm,
  E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm,
  E_eps1_del2_mm, E_eps1_del3_mm`

### 5. Brackets and deformation conventions

- Graded bracket: $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$.
- Deformed bracket: $[X,Y]_\gamma = [X,Y]_0 + \kappa\,\gamma(X,Y)$ with $\kappa$ written on the
  **left**. $\gamma$ is an odd 2-cochain: $p(\gamma(X,Y)) = p(X)+p(Y)+1$.
- Deformation parameters: `gb_a1{σ}_b{j}{s}` (e.g. `gb_a1p_b2m` = $\mathrm{gb}_{a_1^+,b_2^-}$),
  $4n$ in total, stored as a $2\times 2n$ matrix (rows `a_1_p, a_1_m`; columns
  `b_1_p, b_1_m, ..., b_n_p, b_n_m`). They are ordinary scalars; "parity 1" in the math docs
  refers to the odd parity of the deformation term $\kappa\,\gamma$ (see I05 Response).
- Coboundary: odd map $f(Z_j)=\sum_i \phi_{ij} Z_i$ (only $p(Z_i)\ne p(Z_j)$), parameter name
  `phi_{i}_{j}` with the global basis indices; $(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)] -
  (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])$.
- Fractions are serialized as strings (`"1"`, `"-1/2"`).
