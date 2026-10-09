# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project and was finalized in Issue I01.

Throughout, $n \ge 1$ is the **bosonic rank**; the algebra is
$C(n+1) = \mathfrak{osp}(2|2n)$ (so $C(2)=\mathfrak{osp}(2|2)$ has $n=1$).
Files are named by the bosonic rank: `C_1_*.json`, `C_2_*.json`, `C_3_*.json`.

## 1. Oscillators

| Symbol (math) | JSON label | Parity | Relations |
|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 | $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$ |
| $a_1^-$ | `a_1_m` | 1 | (standard CAR pair, $m = 1$) |
| $b_k^+$ | `b_{k}_p` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$, $[b_k^\pm, b_l^\pm] = 0$ |
| $b_k^-$ | `b_{k}_m` | 0 | ($k = 1, \ldots, n$) |
| $\kappa$ | `kappa` | 1 | odd central: $\kappa x = (-1)^{p(x)} x\kappa$, $\kappa^2 = 0$ |
| $K$ | `K` | 0 | even central identity, $K = 1$ |

Mixed relations (undeformed): $[b_k^\pm, a_1^\pm] = 0$.

**Oscillator ordering (normal form)**: every element of the oscillator (Weyl–Clifford)
algebra is written in the normally ordered form with factors sorted by

```
kappa < a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ... < b_n_p < b_n_m
```

(`kappa` only appears in deformed/extended computations). Reordering uses the relations
above; fermionic squares vanish. The symbol $N_a := a_1^+ a_1^-$ and $N_k := b_k^+ b_k^-$
denote number operators; their symmetrized forms are $J := a_1^+a_1^- - \tfrac12$ and
$\tilde N_k := b_k^+ b_k^- + \tfrac12$.

## 2. Root system

Roots are written with the orthogonal vectors $\varepsilon$ (fermionic, one copy since $m=1$)
and $\delta_1, \ldots, \delta_n$ (bosonic):

$$\Delta_{\bar 0} = \{\pm 2\delta_k\} \cup \{\pm(\delta_i \pm \delta_j) \mid i<j\},
\qquad
\Delta_{\bar 1} = \{\pm\varepsilon \pm \delta_k\}.$$

Cartan generators follow Frappat–Sciarrino–Sorba (`docs/math/Cn1_definition.md`):

$$H_1 = a_1^+ a_1^- + b_1^+ b_1^-,\qquad
H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- \ (2 \le k \le n),\qquad
H_{n+1} = -b_n^+ b_n^- - \tfrac12 .$$

(The constant in $H_{n+1}$ is required for closure: $[(b_n^+)^2, (b_n^-)^2] = -4(b_n^+b_n^- + \tfrac12)$.)
In terms of the symmetrized number operators: $H_1 = J + \tilde N_1$, $H_k = \tilde N_{k-1} - \tilde N_k$,
$H_{n+1} = -\tilde N_n$; the $\mathfrak{so}(2)$ generator is
$J = H_1 - H_2 - \cdots - H_n + H_{n+1}$.

## 3. Generator labels (JSON)

| Root | Generator label | Oscillator realization | Parity |
|---|---|---|---|
| (Cartan) | `H_{k}`, $k=1,\ldots,n+1$ | see §2 | 0 |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ | 0 |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ | 0 |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ | 0 |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ | 0 |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ | 0 |
| $-\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ | 0 |
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ | 1 |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ | 1 |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ | 1 |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ | 1 |

Rule for the two-letter suffix of odd generators: **first letter = sign of $\varepsilon$
(i.e. of $a_1^\pm$), second letter = sign of $\delta_k$ (i.e. of $b_k^\pm$)**.
Unlike $B(0,n)$ ($E_{\pm\delta_k} = \tfrac{1}{\sqrt2} b_k^\pm$) no $\tfrac1{\sqrt2}$ factors occur; all
coefficients are rational. Note that the simple-root normalisation $E_{\pm 2\delta_n} = \tfrac12 (b_n^\pm)^2$
in `Cn1_definition.md` §2 is **not** used for the basis; the basis uses $(b_k^\pm)^2$ uniformly
(as in the $B(0,n)$ schema), which only rescales structure constants.

Dimensions: even $= (n+1) + 2n + 4\binom n2 = 2n^2 + n + 1$, odd $= 4n$, total $= 2n^2 + 5n + 1$.

## 4. Basis lists and PBW ordering

**PBW ordering (decided in I01)**:

```
kappa < [odd generators] < [even generators]          (K = 1 excluded, as in B(0,n))
```

with the following internal orders.

Odd block (sign-major, index-minor; the $\varepsilon$-sign is the outer key, then the $\delta$-sign,
then $k$):

```
E_eps1_del1_pp, ..., E_eps1_deln_pp,
E_eps1_del1_pm, ..., E_eps1_deln_pm,
E_eps1_del1_mp, ..., E_eps1_deln_mp,
E_eps1_del1_mm, ..., E_eps1_deln_mm
```

Even block (same layout as the $B(0,n)$ v5.0 schema, with $n+1$ Cartan elements):

```
H_1, ..., H_{n+1},
E_2del1_p, ..., E_2deln_p,           E_del{i}_del{j}_pp (i<j, lexicographic),
E_2del1_m, ..., E_2deln_m,           E_del{i}_del{j}_mm (i<j),
E_del{i}_del{j}_pm (i<j),            E_del{i}_del{j}_mp (i<j)
```

### C(2) = osp(2|2), n = 1 (even 4, odd 4)

```
even: H_1, H_2, E_2del1_p, E_2del1_m
odd : E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm
```

### C(3) = osp(2|4), n = 2 (even 11, odd 8)

```
even: H_1, H_2, H_3,
      E_2del1_p, E_2del2_p, E_del1_del2_pp,
      E_2del1_m, E_2del2_m, E_del1_del2_mm,
      E_del1_del2_pm, E_del1_del2_mp
odd : E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm,
      E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm
```

### C(4) = osp(2|6), n = 3 (even 22, odd 12)

```
even: H_1, H_2, H_3, H_4,
      E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
      E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
      E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,
      E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp
odd : E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp,
      E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm,
      E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp,
      E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm
```

## 5. Brackets, deformation, coboundary

* Graded bracket: $[X, Y\} = XY - (-1)^{p(X)p(Y)} YX$, computed in the oscillator algebra.
  Structure constants are stored for **all ordered pairs** $(X, Y)$ with non-zero bracket
  (`sign_rule: "graded"`); graded antisymmetry $[Y,X\} = -(-1)^{p(X)p(Y)}[X,Y\}$ is therefore
  a checkable redundancy, not an assumption.
* Deformation parameters: `gb_a1{σ}_b{k}{s}` $= \mathrm{gb}_{a_1^\sigma, b_k^s}$ ($4n$ of them),
  entering through $[b_k^s, a_1^\sigma] = -\mathrm{gb}_{a_1^\sigma, b_k^s}\,\kappa$.
  The deformed bracket is $[X,Y]_\gamma = [X,Y]_0 + \kappa\,\gamma(X,Y)$ with
  $p(\gamma(X,Y)) = p(X) + p(Y) + 1$; $\gamma(X, Y)$ takes values in $\mathfrak g \oplus \mathbb{C}K$
  (the $K$-component is stored with `"Z": "K"`).
* Odd linear map $f(Z_j) = \sum_i \phi_{ij} Z_i$ and coboundary
  $(\delta f)(X,Y) = (-1)^{p(X)}[X, f(Y)\} - (-1)^{(p(X)+1)p(Y)}[Y, f(X)\} - f([X,Y\})$.
