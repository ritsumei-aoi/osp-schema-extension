# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.
All conventions below were fixed in Issue I01 and are binding for Issues I02–I08.

## 1. Algebra and oscillators

* Target algebra: $C(n+1) = \mathfrak{osp}(2|2n)$, bosonic rank $n \ge 1$.
  File names use the bosonic rank: `C_{n}_*.json` (so $C(2)=\mathfrak{osp}(2|2)$ is `C_1_*.json`).
* Oscillators (all elements of the pre-oscillator superspace $V$):

| Symbol | JSON label | Parity | Relations |
|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 | $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$ (CAR) |
| $a_1^-$ | `a_1_m` | 1 | |
| $b_k^+$ | `b_{k}_p` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$, $[b_k^\pm, b_l^\pm] = 0$ (CCR) |
| $b_k^-$ | `b_{k}_m` | 0 | |
| mixed | | | $[b_k^s, a_1^\sigma] = 0$ (undeformed) |

* Central elements of the extension $A = V \oplus \mathbf{C}K \oplus \mathbf{C}\kappa$:
  * `K` — even central element, identified with the scalar $1$ in all computations.
    It is **not** a basis element of $\mathfrak g$; it may appear as a target label `"K"`
    in deformation data (Schema 2–4) when a bracket produces a constant term.
  * `kappa` — odd central element, $\kappa^2 = 0$, $x\kappa = (-1)^{p(x)}\kappa x$.
    Also not a basis element of $\mathfrak g$; it only appears as the formal first-order
    symbol of the inhomogeneous deformation.
* Graded bracket: $[X, Y\} = XY - (-1)^{p(X)p(Y)}YX$ inside the universal enveloping algebra
  $\mathcal U(A)$. The JSON key `sign_rule: "graded"` refers to this convention.

## 2. Root system and generator labels

Roots are written with $\varepsilon$ (fermionic direction) and $\delta_1,\dots,\delta_n$ (bosonic).

| Root | Generator label | Oscillator realization | Parity |
|---|---|---|---|
| — (Cartan) | `H_1` | $a_1^+a_1^- + b_1^+b_1^-$ | 0 |
| — (Cartan) | `H_k`, $2\le k\le n$ | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ | 0 |
| — (Cartan) | `H_{n+1}` | $-b_n^+b_n^- - \tfrac12$ | 0 |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ | 0 |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ | 0 |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ | 0 |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ | 0 |
| $-\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ | 0 |
| $-\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ | 0 |
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+b_k^+$ | 1 |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+b_k^-$ | 1 |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^-b_k^+$ | 1 |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^-b_k^-$ | 1 |

Label grammar: `E_<root-part>_<signs>`, where the sign string lists the signs of the
root components **in the order the components are written in the label**
(fermionic $\varepsilon$ first, then $\delta$ with increasing index). `p` = $+$, `m` = $-$.
The Cartan generators `H_1..H_{n+1}` are the Chevalley-type generators of Frappat et al.:
$H_1 = \{E_{\varepsilon-\delta_1}, E_{\delta_1-\varepsilon}\}$,
$H_k = [E_{\delta_{k-1}-\delta_k}, E_{\delta_k-\delta_{k-1}}]$,
$H_{n+1} = [\tfrac12 E_{2\delta_n}, \tfrac12 E_{-2\delta_n}]$.
Note that with these definitions $[H_{n+1}, E_{2\delta_n}] = -2E_{2\delta_n}$ (Frappat sign
convention; the structure constants are generated mechanically from the realizations and are
therefore self-consistent).

Dimension: even $= (n+1) + 2n + 4\binom{n}{2} = 2n^2+n+1$, odd $= 4n$, total $= 2n^2+5n+1$.

### Explicit basis lists

**C(2) = osp(2|2), n = 1** (even 4, odd 4):
```
even: H_1, H_2, E_2del1_p, E_2del1_m
odd : E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm
```

**C(3) = osp(2|4), n = 2** (even 11, odd 8):
```
even: H_1, H_2, H_3,
      E_2del1_p, E_2del2_p, E_del1_del2_pp,
      E_2del1_m, E_2del2_m, E_del1_del2_mm,
      E_del1_del2_pm, E_del1_del2_mp
odd : E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm,
      E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm
```

**C(4) = osp(2|6), n = 3** (even 22, odd 12):
```
even: H_1, H_2, H_3, H_4,
      E_2del1_p, E_2del2_p, E_2del3_p,
      E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
      E_2del1_m, E_2del2_m, E_2del3_m,
      E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
      E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,
      E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp
odd : E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm,
      E_eps1_del3_pp, E_eps1_del3_pm,
      E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm,
      E_eps1_del3_mp, E_eps1_del3_mm
```

## 3. PBW ordering

Two orderings are used; they must not be confused.

### 3.1 Ordering of oscillator symbols (inside `generator_realization`)

```
kappa < a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ... < b_n_p < b_n_m
```
Every oscillator word stored in the JSON is normal-ordered with respect to this list
(`kappa` only occurs in deformation data). Reordering uses the CAR/CCR relations of §1.

### 3.2 Ordering of basis generators (PBW order of $\mathfrak g$, used for basis lists and for
listing structure constants)

```
kappa < [odd block] < [even block]      (K = 1 is excluded, as in B(0,n) v5.0)

odd block : for sigma in (p, m): for k in 1..n: for s in (p, m): E_eps1_del{k}_{sigma}{s}
even block: H_1, ..., H_{n+1},
            E_2del{k}_p (k = 1..n), E_del{i}_del{j}_pp (i<j, lexicographic),
            E_2del{k}_m (k = 1..n), E_del{i}_del{j}_mm (i<j),
            E_del{i}_del{j}_pm (i<j), E_del{i}_del{j}_mp (i<j)
```
The position of a generator in this list is its `basis index`; structure-constant records are
sorted by (index of X, index of Y).

## 4. Deformation parameters (Schema 2–4)

* `gb` matrix: $2 \times 2n$, rows indexed by the fermionic oscillator (`a_1_p`, `a_1_m`),
  columns by the bosonic oscillators (`b_1_p`, `b_1_m`, …, `b_n_p`, `b_n_m`).
  Entry label: `gb_a1{sigma}_b{k}{s}`, e.g. `gb_a1p_b2m` $= \mathrm{gb}_{a_1^+, b_2^-}$.
* Deformed oscillator relation: $[b_k^s, a_1^\sigma] = -\,\mathrm{gb}_{a_1^\sigma, b_k^s}\,\kappa$.
* The `gb` entries are treated as **commuting (scalar) parameters**; the odd parity of the
  deformation is carried entirely by $\kappa$ (see I05 Response for the discussion of the
  parity remark in `C_inhomogeneous_definition.md`).
* Deformed bracket: $[X,Y]_\gamma = [X,Y]_0 + \kappa\,\gamma(X,Y)$, $\kappa$ written on the left.
  $\gamma(X,Y)$ has parity $p(X)+p(Y)+1$ and takes values in $\mathfrak g \oplus \mathbf{C}K$.
* Odd linear map for coboundaries: $f(Z_j) = \sum_i \phi_{ij} Z_i$ with $p(Z_i) \ne p(Z_j)$;
  label `phi_<i>_<j>` uses basis indices of §3.2. The coboundary is
  $(\delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])$.

## 5. Rational numbers in JSON

All coefficients are stored as strings in lowest terms (`"1"`, `"-1/2"`, `"4"`), never as floats.
