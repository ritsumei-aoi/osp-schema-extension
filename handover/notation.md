# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

*(Finalized in Issue I01; see `docs/issues/I01.md` for the options considered.)*

### 0. Index conventions

- $n \geq 1$ is the **bosonic rank**. $C(n+1) = \mathfrak{osp}(2|2n)$; file names use $n$
  (C(2) $\leftrightarrow$ `C_1_*`, C(3) $\leftrightarrow$ `C_2_*`, C(4) $\leftrightarrow$ `C_3_*`).
- $k, l \in \{1,\dots,n\}$ index bosonic oscillators / the vectors $\delta_k$; pairs are written $i<j$.
- $\varepsilon$ is the single fermionic weight vector. In labels it is written `eps1`
  (the `1` is the index of the unique fermionic pair $a_1^\pm$, i.e. $m=1$).
- Sign suffixes: `p` = $+$, `m` = $-$. In a two-letter suffix the first letter refers to the
  first weight in the label and the second letter to the second weight.
- Rational coefficients in JSON are strings: `"1"`, `"-1/2"`.

### 1. Oscillators and central elements

| Label | Symbol | Parity | Relations |
|---|---|---|---|
| `a_1_p`, `a_1_m` | $a_1^+, a_1^-$ | 1 | $\{a_1^-, a_1^+\} = K$, $(a_1^\pm)^2 = 0$ (CAR) |
| `b_k_p`, `b_k_m` | $b_k^+, b_k^-$ | 0 | $[b_k^-, b_l^+] = \delta_{kl}K$, $[b_k^\pm, b_l^\pm] = 0$ (CCR) |
| `kappa` | $\kappa$ | 1 | central, $\kappa^2 = 0$ |
| `K` | $K$ | 0 | central, identified with the scalar $1$ |

Undeformed mixed relations: $[b_k^s, a_1^\sigma] = 0$.
Deformed mixed relations (Issue I05): $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$.

**Normal (oscillator) ordering** of words:
$$\kappa < a_1^+ < a_1^- < b_1^+ < b_1^- < b_2^+ < b_2^- < \dots < b_n^+ < b_n^-,$$
i.e. JSON `"ordering": "kappa, a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m"`.
$K$ never appears in words (it is replaced by $1$).

### 2. Generator labels and oscillator realization

Following Frappat–Sciarrino–Sorba (all-root-generator normalization, which coincides with the
B(0,n) v5.0 convention for the bosonic part):

| Root | Label | Realization | Parity |
|---|---|---|---|
| Cartan | `H_1` | $a_1^+a_1^- + b_1^+b_1^-$ | 0 |
| Cartan, $2 \le k \le n$ | `H_k` | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ | 0 |
| Cartan | `H_{n+1}` | $-b_n^+b_n^- - \tfrac12$ | 0 |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ | 0 |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ | 0 |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ | 0 |
| $-(\delta_i+\delta_j)$ | `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ | 0 |
| $\delta_i-\delta_j$ | `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ | 0 |
| $-(\delta_i-\delta_j)$ | `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ | 0 |
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+b_k^+$ | 1 |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+b_k^-$ | 1 |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^-b_k^+$ | 1 |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^-b_k^-$ | 1 |

Remarks.
- The Cartan subalgebra is spanned by $a_1^+a_1^- - \tfrac12$ (the $\mathfrak{so}(2)$ factor) and
  $b_k^+b_k^- + \tfrac12$ ($k=1..n$). `H_1`, `H_k`, `H_{n+1}` are combinations of these with no
  leftover constant, so all undeformed brackets close in $\mathfrak g$ without a $K$-term.
- $E_{\pm 2\delta_k}$ is $(b_k^\pm)^2$ (no factor $\tfrac12$). The Frappat simple-generator list
  writes $E_{\pm2\delta_n} = \tfrac12 (b_n^\pm)^2$; this is only a rescaling of a basis vector and
  we use the unnormalized form uniformly for all $k$ (as in B(0,n) v5.0).
- `E_eps1_del{k}_mp` $= a_1^- b_k^+$ is the root $-\varepsilon+\delta_k$, i.e. Frappat's
  $E_{\delta_k-\varepsilon}$ (for $k=1$: $b_1^+a_1^- = a_1^-b_1^+$ in the undeformed algebra).

### 3. Basis and PBW ordering

**PBW ordering (chosen option A, B(0,n)-compatible):**
$$\kappa \;<\; [\text{odd}] \;<\; [\text{even}] \qquad (K = 1 \text{ excluded}).$$

- odd block, $\varepsilon$-sign major, then $\delta$-sign, then $k$ ascending:
  `E_eps1_del{k}_pp` ($k=1..n$), `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm`.
- even block (identical pattern to B(0,n) v5.0, with $n+1$ Cartans):
  `H_1..H_{n+1}`, `E_2del{k}_p`, `E_del{i}_del{j}_pp`, `E_2del{k}_m`, `E_del{i}_del{j}_mm`,
  `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp` (pairs $i<j$ in lexicographic order).

The global basis index used in all JSON layers is: odd block first, then even block.
(The JSON `basis` key lists `even` and `odd` separately, as in v5.0.)

Dimensions: even $=2n^2+n+1$, odd $=4n$, total $=2n^2+5n+1$.

#### C(2) = osp(2|2), n = 1  (4 | 4)
- even: `H_1, H_2, E_2del1_p, E_2del1_m`
- odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

#### C(3) = osp(2|4), n = 2  (11 | 8)
- even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m,
  E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm,
  E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

#### C(4) = osp(2|6), n = 3  (22 | 12)
- even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p,
  E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m,
  E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,
  E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`
- odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm,
  E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm,
  E_eps1_del2_mm, E_eps1_del3_mm`

### 4. Brackets, deformation and cochains

- $[X,Y] = XY - (-1)^{p(X)p(Y)}YX$ (graded commutator) on homogeneous elements.
- Deformed bracket: $[X,Y]_\gamma = [X,Y]_0 + \kappa\,\gamma(X,Y)$ with $\kappa$ written on the **left**.
  $\gamma(X,Y) \in \mathfrak g \oplus \mathbb C K$; the $K$-component is called the *central part*.
- Deformation parameters: `gb_{σ}_{j}_{s}` $= \mathrm{gb}_{a_1^\sigma, b_j^s}$, e.g. `gb_p_1_m`
  $=\mathrm{gb}_{a_1^+, b_1^-}$. The **gb matrix** is $2 \times 2n$: rows `a_1_p, a_1_m`,
  columns `b_1_p, b_1_m, ..., b_n_p, b_n_m`.
- Odd linear map $f(Z_j) = \sum_i \phi_{ij} Z_i$ with $\phi_{ij} \neq 0$ only if
  $p(Z_i) \neq p(Z_j)$; unknown labels `phi__{Z_i}__{Z_j}`.
- $(\delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])$.
