# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project (finalized in Issue I01).

## Conventions

### 0. General

- $n \ge 1$ is the **bosonic rank**. $C(n+1) = \mathfrak{osp}(2|2n)$; files are indexed by $n$
  (C(2) = osp(2|2) ↔ `n=1`, C(3) = osp(2|4) ↔ `n=2`, C(4) = osp(2|6) ↔ `n=3`).
- Parity $p(\cdot) \in \{0, 1\}$; super-bracket $[X, Y\} = XY - (-1)^{p(X)p(Y)} YX$ (written $[X,Y]$).
- Label suffixes: `_p` = "+" (raising / creation), `_m` = "−" (lowering / annihilation).
  Two-letter suffixes (`pp`, `pm`, `mp`, `mm`) give the signs of the two constituents **in label order**.
- Rational coefficients are stored in JSON as strings (`"1"`, `"-1/2"`).

### 1. Oscillator generators (labels)

| Label | Symbol | Parity | Relations |
|---|---|---|---|
| `a_1_p`, `a_1_m` | $a_1^+, a_1^-$ | 1 | CAR: $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$ |
| `b_k_p`, `b_k_m` ($k=1..n$) | $b_k^+, b_k^-$ | 0 | CCR: $[b_k^-, b_l^+] = \delta_{kl}$, other brackets $0$ |
| `kappa` | $\kappa$ | 1 | central, $\kappa^2 = 0$ |
| `K` | $K$ | 0 | central, identified with the scalar $1$ |

Undeformed: $[b_k^\pm, a_1^\sigma] = 0$. Deformed (Schema 2): $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$.

**Oscillator ordering (normal/standard form)**: `kappa < a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < ... < b_n_m`.
Every element of $\mathcal{U}(A)$ is stored as a sum of words in this order.

### 2. Roots and generator labels

Roots: $\varepsilon$ (fermionic), $\delta_1, \dots, \delta_n$ (bosonic).

| Root | Label | Realization | Parity |
|---|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ | 0 |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ | 0 |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ | 0 |
| $-\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ | 0 |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ | 0 |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ | 0 |
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ | 1 |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ | 1 |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ | 1 |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ | 1 |

**Cartan generators** (from `docs/math/Cn1_definition.md`, distinguished simple roots
$\varepsilon - \delta_1, \delta_1 - \delta_2, \dots, \delta_{n-1} - \delta_n, 2\delta_n$):

| Label | Realization |
|---|---|
| `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ |
| `H_k` ($2 \le k \le n$) | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ |
| `H_{n+1}` | $-b_n^+ b_n^- - \tfrac12$ |

All even generators are the Weyl-(anti)symmetrized quadratics: e.g. $h_\varepsilon = a_1^+a_1^- - \tfrac12$,
$h_k = b_k^+ b_k^- + \tfrac12$, so $H_1 = h_\varepsilon + h_1$, $H_k = h_{k-1} - h_k$, $H_{n+1} = -h_n$.
With this convention the span of the generators closes under the bracket **without** producing $K$.

**Normalization convention**: root vectors use the *unnormalized* form
$E_{\pm 2\delta_k} = (b_k^\pm)^2$ for all $k$ (as in the "all root generators" formula and in the
B(0,n) label table). The Chevalley-normalized simple generator $\tfrac12 (b_n^\pm)^2$ of
`Cn1_definition.md` is $\tfrac12$ `E_2del{n}_p/m`; it is not a separate basis element.

### 3. Basis lists

Even ($2n^2 + n + 1$), in PBW order:
`H_1, …, H_{n+1}`, `E_2del{k}_p` (k=1..n), `E_del{i}_del{j}_pp` (i<j, lexicographic),
`E_2del{k}_m`, `E_del{i}_del{j}_mm`, `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`.

Odd ($4n$), in PBW order:
`E_eps1_del{k}_pp` (k=1..n), `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm`.

**C(2), n=1** (4 | 4):
- even: `H_1, H_2, E_2del1_p, E_2del1_m`
- odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

**C(3), n=2** (11 | 8):
- even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

**C(4), n=3** (22 | 12):
- even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`
- odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm`

### 4. PBW ordering

$$\kappa \;<\; [\text{odd: } \texttt{pp} < \texttt{pm} < \texttt{mp} < \texttt{mm},\ \text{each block by } k] \;<\; [\text{even, order of §3}]$$

$K$ (= 1) is excluded from basis lists and PBW ordering; it is recorded in `central_elements` only.
(Decision record: `docs/issues/I01.md`.)

### 5. Deformation and cochains

- Deformation parameters: `gb_a1{σ}_b{j}{s}` ↔ $\mathrm{gb}_{a_1^\sigma, b_j^s}$, e.g. `gb_a1p_b1m` = $\mathrm{gb}_{a_1^+, b_1^-}$.
  The gb matrix has rows `a_1_p, a_1_m` and columns `b_1_p, b_1_m, …, b_n_p, b_n_m` (2 × 2n).
- Deformed bracket: $[X, Y]_\gamma = [X, Y]_0 + \kappa\,\gamma(X, Y)$ ($\kappa$ written on the **left**).
  $\gamma$ takes values in $\mathfrak{g} \oplus \mathbb{C}K$; the $K$-component is stored with `"Z": "K"`.
- Odd 1-cochain $f$: $f(Z_j) = \sum_i \phi_{ij} Z_i\ (+\ \phi_{K,j} K)$, unknown labels `phi[Z_i,Z_j]`.
- Coboundary: $(\delta f)(X,Y) = (-1)^{p(X)}[X, f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y, f(X)] - f([X,Y])$.
