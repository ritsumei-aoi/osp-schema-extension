# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.
Finalized in Issue I01 (branch `study/thm01-R-fable51-b06-G`).

## 1. Algebra and oscillators

* $C(n+1) = \mathfrak{osp}(2|2n)$, $n \ge 1$ is the **bosonic rank**. File names use $n$
  (e.g. $C(2)=\mathfrak{osp}(2|2)$ is `C_1_*.json`).
* **Fermionic pair** (standard CAR): $a_1^\pm$, $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$,
  parity $p(a_1^\pm)=1$. JSON labels: `a_1_p`, `a_1_m`.
* **Bosonic oscillators** (CCR): $b_k^\pm$, $[b_k^-, b_l^+] = \delta_{kl}$, $k=1,\dots,n$,
  parity 0. JSON labels: `b_k_p`, `b_k_m`.
* Undeformed mixed relation: $[b_k^s, a_1^\sigma] = 0$.
* **Central elements**: $K$ (even, identified with the scalar $1$) and $\kappa$ (odd, $\kappa^2=0$).
  $\kappa$ is *super*central: $\kappa x = (-1)^{p(x)} x \kappa$. JSON labels: `K`, `kappa`.
* **Oscillator word ordering** (normal form used for all realizations):
  `a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ... < b_n_p < b_n_m`,
  with `kappa` always moved to the far left of a word.
  Every element of the oscillator algebra is written as a sum of normally ordered words
  with rational coefficients (`coeff` strings such as `"1"`, `"-1/2"`).

## 2. Root system

Roots are expressed with one fermionic vector $\varepsilon$ ($=\varepsilon_1$) and
bosonic vectors $\delta_1,\dots,\delta_n$:

| Root | Parity | Count | Generator label | Realization |
|---|---|---|---|---|
| $\pm 2\delta_k$ | 0 | $2n$ | `E_2del{k}_p`, `E_2del{k}_m` | $(b_k^\pm)^2$ |
| $\delta_i+\delta_j$, $i<j$ | 0 | $n(n-1)/2$ | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $-\delta_i-\delta_j$, $i<j$ | 0 | $n(n-1)/2$ | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\delta_i-\delta_j$, $i<j$ | 0 | $n(n-1)/2$ | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-\delta_i+\delta_j$, $i<j$ | 0 | $n(n-1)/2$ | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $\varepsilon+\delta_k$ | 1 | $n$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon-\delta_k$ | 1 | $n$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon+\delta_k$ | 1 | $n$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon-\delta_k$ | 1 | $n$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

Label rule for odd generators: `E_eps1_del{k}_{σ}{s}` where the **first** sign letter
$\sigma$ is the sign of $\varepsilon$ (= superscript of $a_1^\sigma$) and the **second**
sign letter $s$ is the sign of $\delta_k$ (= superscript of $b_k^s$). `p` = $+$, `m` = $-$.
This mirrors the B(0,n) rule `E_del{i}_del{j}_{s_i}{s_j}`.

**Cartan generators** (Frappat simple-root convention, $n+1$ of them), labels `H_1 ... H_{n+1}`:

$$
H_1 = a_1^+ a_1^- + b_1^+ b_1^-,\qquad
H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- \ (2\le k\le n),\qquad
H_{n+1} = -b_n^+ b_n^- - \tfrac12 .
$$

The constant $-\tfrac12$ in $H_{n+1}$ is kept: with it, $\mathrm{span}\{H_i\}$ equals the span of the
super-symmetrised quadratics $a_1^+a_1^- - \tfrac12$, $b_k^+b_k^- + \tfrac12$, which is exactly the
Cartan subalgebra of $\mathfrak{so}(2)\oplus\mathfrak{sp}(2n)$ inside the oscillator algebra, and all
brackets of basis elements close in the span of the basis **without** stray constants.

**Simple roots**: $\alpha_1=\varepsilon-\delta_1$, $\alpha_k=\delta_{k-1}-\delta_k$ ($2\le k\le n$),
$\alpha_{n+1}=2\delta_n$ (distinguished Dynkin diagram of $C(n+1)$).

## 3. Basis lists (even / odd)

**Dimension**: even $=2n^2+n+1$, odd $=4n$, total $=2n^2+5n+1$.

### Even basis ordering (all $n$)

```
H_1, ..., H_{n+1},
E_2del1_p, ..., E_2deln_p,
E_del{i}_del{j}_pp  (i<j, lexicographic),
E_2del1_m, ..., E_2deln_m,
E_del{i}_del{j}_mm  (i<j, lexicographic),
E_del{i}_del{j}_pm  (i<j, lexicographic),
E_del{i}_del{j}_mp  (i<j, lexicographic)
```

### Odd basis ordering (all $n$) — sign-major

```
E_eps1_del1_pp, ..., E_eps1_deln_pp,
E_eps1_del1_pm, ..., E_eps1_deln_pm,
E_eps1_del1_mp, ..., E_eps1_deln_mp,
E_eps1_del1_mm, ..., E_eps1_deln_mm
```

### C(2) = osp(2|2), n = 1  (even 4, odd 4, total 8)

* even: `H_1, H_2, E_2del1_p, E_2del1_m`
* odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

### C(3) = osp(2|4), n = 2  (even 11, odd 8, total 19)

* even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
* odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

### C(4) = osp(2|6), n = 3  (even 22, odd 12, total 34)

* even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`
* odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm`

## 4. PBW ordering

```
kappa < [odd, in the sign-major order of §3] < [even, in the order of §3]      (K = 1 excluded)
```

The full ordered basis used by all scripts is `basis.odd + basis.even` in the lists above,
with `kappa` in front when the extension $\mathfrak{g}\oplus\kappa\mathfrak{g}$ is considered.

## 5. Brackets, deformation and coboundary conventions

* Graded bracket: $[X,Y\} = XY - (-1)^{p(X)p(Y)} YX$, computed in the oscillator algebra and
  decomposed in the basis. Structure constants are stored for **all ordered pairs** $(X,Y)$ with a
  non-zero bracket.
* **Deformation parameters** (`gb`): $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$.
  There are $4n$ of them. They are **scalars** (ordinary commuting numbers); the "parity 1" of
  the deformation is carried by $\kappa$ (see I05 Response for the discussion of this point).
  JSON label: `gb_a_1_{σ}_b_{j}_{s}` (e.g. `gb_a_1_p_b_2_m` $=\mathrm{gb}_{+,2,-}$).
  The **gb matrix** is $2\times 2n$: rows `a_1_p`, `a_1_m`; columns `b_1_p, b_1_m, ..., b_n_p, b_n_m`.
* **γ-structure**: $[X,Y\}_\gamma = [X,Y\}_0 + \kappa\,\gamma(X,Y)$, with $\kappa$ written on the left.
  $\gamma(X,Y)\in\mathfrak{g}$ has parity $p(X)+p(Y)+1$; constant ($K$) terms are dropped
  (adjoint-representation convention).
* **Coboundary** of an odd linear map $f$:
  $(\delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)\} - (-1)^{(p(X)+1)p(Y)}[Y,f(X)\} - f([X,Y\})$.
* Coefficient strings: exact rationals (`"-1/2"`). Symbolic coefficients (Schema 2 and 4) are
  stored as **linear forms** `{"gb_...": "rational", ...}` plus a readable `expr` string.
