# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It was initialized during the $C(n+1)$ schema extension project (Issue I01) and is the
single source of truth for basis labels, PBW ordering, and oscillator conventions.

## Conventions

### 1. Algebra and rank

- $\mathfrak{g} = C(n+1) = \mathfrak{osp}(2|2n)$, with $n \ge 1$ the **bosonic rank**.
  Files are indexed by $n$: C(2) ↔ `n=1`, C(3) ↔ `n=2`, C(4) ↔ `n=3`.
- Superdimension $(2n^2+n+1 \mid 4n)$, total $2n^2+5n+1$.
- Parity is written $p(\cdot) \in \{0,1\}$; the graded bracket is
  $[X,Y] = XY - (-1)^{p(X)p(Y)} YX$.

### 2. Oscillators (labels used in code/JSON)

| Label | Meaning | Parity | Relation |
|---|---|---|---|
| `a_1_p`, `a_1_m` | fermionic pair $a_1^+, a_1^-$ | 1 | $\{a_1^-,a_1^+\}=1$, $(a_1^\pm)^2=0$ |
| `b_k_p`, `b_k_m` | bosonic pair $b_k^+, b_k^-$, $k=1..n$ | 0 | $[b_k^-,b_l^+]=\delta_{kl}$, $[b_k^\pm,b_l^\pm]=0$ |
| `kappa` | odd central element $\kappa$ | 1 | $\kappa^2=0$ (used only for the deformation, Layer 2+) |
| `K` | even central element, identified with the scalar 1 | 0 | not a basis element |

Undeformed: $[b_k^\pm, a_1^\pm]=0$.
Deformed (Layer 2): $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$.

**Oscillator normal order** (used for all `standard_form` words):
`a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ... < b_n_p < b_n_m`
(creation before annihilation, fermion before bosons; identical in spirit to
the B(0,n) order `a_0, b_1_p, b_1_m, ...`). $\kappa$ is always moved to the far left.

### 3. Generator labels and realizations

Suffix letters: `p` = $+$, `m` = $-$. For two-sign suffixes the first letter refers
to the first named root vector, the second to the second.

| Root | Label | Realization | Parity |
|---|---|---|---|
| Cartan | `H_1` | $a_1^+a_1^- + b_1^+b_1^-$ | 0 |
| Cartan | `H_k` ($2\le k\le n$) | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ | 0 |
| Cartan | `H_{n+1}` | $-b_n^+b_n^- - \tfrac12$ | 0 |
| $\pm 2\delta_k$ | `E_2del{k}_p` / `E_2del{k}_m` | $\tfrac12 (b_k^\pm)^2$ | 0 |
| $\pm(\delta_i+\delta_j)$, $i<j$ | `E_del{i}_del{j}_pp` / `_mm` | $b_i^\pm b_j^\pm$ | 0 |
| $\delta_i-\delta_j$, $i<j$ | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ | 0 |
| $-(\delta_i-\delta_j)$, $i<j$ | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ | 0 |
| $\sigma\varepsilon + s\delta_k$ | `E_eps1_del{k}_{σs}` ($σ,s\in\{p,m\}$) | $a_1^\sigma b_k^s$ | 1 |

Notes:
- The Cartan elements are exactly the **super-symmetrized** quadratics
  ($a_1^+a_1^- - \tfrac12 = \tfrac12[a_1^+,a_1^-]$, $b^+b^- + \tfrac12 = \tfrac12\{b^+,b^-\}$),
  so the span of all generators is closed under the bracket **without** central $K$ terms.
- $E_{\pm2\delta_k}$ carry the factor $\tfrac12$ for every $k$ (Chevalley normalization of
  the simple generator $E_{2\delta_n}$ in `Cn1_definition.md`, applied uniformly), so that
  $[E_{2\delta_n}, E_{-2\delta_n}] = H_{n+1}$.
- `E_eps1_del{k}_pm` is $a_1^+b_k^-$ (root $\varepsilon-\delta_k$) and
  `E_eps1_del{k}_mp` is $a_1^-b_k^+$ (root $-\varepsilon+\delta_k$).

### 4. PBW ordering (basis order)

$$\kappa \;<\; [\text{odd}] \;<\; [\text{even}] \qquad (K=1 \text{ excluded, as in B(0,n)})$$

- **odd block**, sign-major / index-minor, $\varepsilon$-sign first:
  `E_eps1_del{1..n}_pp`, `E_eps1_del{1..n}_pm`, `E_eps1_del{1..n}_mp`, `E_eps1_del{1..n}_mm`.
- **even block**:
  `H_1..H_{n+1}`, `E_2del{1..n}_p`, `E_del{i}_del{j}_pp` ($i<j$ lexicographic),
  `E_2del{1..n}_m`, `E_del{i}_del{j}_mm`, `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`.

### 5. Basis lists

**C(2), n=1** — even (4): `H_1, H_2, E_2del1_p, E_2del1_m`;
odd (4): `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`.

**C(3), n=2** — even (11): `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`;
odd (8): `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`.

**C(4), n=3** — even (22): `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`;
odd (12): `E_eps1_del{1,2,3}_pp, E_eps1_del{1,2,3}_pm, E_eps1_del{1,2,3}_mp, E_eps1_del{1,2,3}_mm` (in that order).

### 6. Deformation / cohomology symbols

- `gb_{σ}_{j}_{s}` (e.g. `gb_p_1_m`) = $\mathrm{gb}_{a_1^\sigma, b_j^s}$; $4n$ parameters,
  arranged as a $2\times 2n$ matrix with rows $(a_1^+, a_1^-)$ and columns
  $(b_1^+, b_1^-, \dots, b_n^+, b_n^-)$.
- $[X,Y]_\gamma = [X,Y]_0 + \kappa\,\gamma(X,Y)$, $\kappa$ written on the **left**.
- $(\delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])$, $f$ odd.
