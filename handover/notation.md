# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It was initialized during the $C(n+1)$ schema extension project and finalized in Issue I01.

Mathematical background: `docs/math/Cn1_definition.md` (root system, oscillator realization),
`docs/math/B0n_definition.md` and `docs/math/B0n_schema_v5.md` (base case and base schema).

---

## 1. Algebra and rank

* $C(n+1) = \mathfrak{osp}(2|2n)$, $n \ge 1$. Throughout, **$n$ is the bosonic rank**
  (number of bosonic oscillator pairs). The fermionic rank is $m = 1$.
* File names and JSON keys use the bosonic rank: `C_1_*.json` is $C(2)=\mathfrak{osp}(2|2)$,
  `C_2_*.json` is $C(3)=\mathfrak{osp}(2|4)$, `C_3_*.json` is $C(4)=\mathfrak{osp}(2|6)$.
* Dimensions: $\dim\mathfrak{g}_{\bar0} = 2n^2+n+1$, $\dim\mathfrak{g}_{\bar1} = 4n$,
  total $2n^2+5n+1$ (8, 19, 34 for $n = 1, 2, 3$).

## 2. Oscillators

| Symbol (math) | JSON label | Parity | Relations |
|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 | $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$ |
| $a_1^-$ | `a_1_m` | 1 | (standard CAR pair) |
| $b_k^+$ | `b_{k}_p` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$, $[b_k^\pm, b_l^\pm] = 0$ |
| $b_k^-$ | `b_{k}_m` | 0 | ($k = 1, \dots, n$, standard CCR) |

Mixed relations (undeformed algebra): $[b_k^\pm, a_1^\pm] = 0$.

**Oscillator ordering (normal ordering / PBW ordering of oscillator words)**:
```
kappa < a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ... < b_n_p < b_n_m
```
Every oscillator word in the JSON files is written in this order ("standard form").
The constant $1$ (empty word) is identified with the even central element $K$.

**Central elements** (see `docs/math/C_inhomogeneous_definition.md`):

| Symbol | JSON label | Parity | Relations / role |
|---|---|---|---|
| $K$ | `K` | 0 | even central element, identified with the scalar $1$; excluded from basis lists |
| $\kappa$ | `kappa` | 1 | odd central element of the inhomogeneous extension, $\kappa^2 = 0$; excluded from Schema 1 basis lists, first in PBW order |

## 3. Weights and generator labels

Root vectors: $\varepsilon$ (fermionic direction, weight of $a_1^+$) and
$\delta_k$ (weight of $b_k^+$). The oscillator $a_1^-$ has weight $-\varepsilon$, $b_k^-$ has weight $-\delta_k$.

Label grammar: `E_<root>_<signs>` where `<root>` names the absolute root
(`eps1`, `del{k}`, `2del{k}`, `del{i}_del{j}` with $i<j$) and `<signs>` is a string of `p`/`m`
giving the sign of **each factor in order** (`p` $= +$, `m` $= -$).

### 3.1 Even generators (so(2) ⊕ sp(2n) part), $2n^2+n+1$ in total

| Root | Label | Oscillator realization |
|---|---|---|
| Cartan ($n+1$) | `H_1`, …, `H_{n+1}` | see §3.3 |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $-\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |

These labels coincide with the $B(0,n)$ v5.0 labels for the common $\mathfrak{sp}(2n)$ part.

### 3.2 Odd generators ($4n$ in total)

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

The first sign letter is the sign of $\varepsilon$ (fermionic factor), the second is the sign
of $\delta_k$ (bosonic factor). These replace $B(0,n)$'s `E_del{k}_p/m`.

### 3.3 Cartan generators (Frappat distinguished basis, `Cn1_definition.md` §2)

$$
H_1 = a_1^+a_1^- + b_1^+b_1^-,\qquad
H_k = b_{k-1}^+b_{k-1}^- - b_k^+b_k^- \ (2\le k\le n),\qquad
H_{n+1} = -b_n^+b_n^- - \tfrac12 .
$$

Equivalent description via symmetrized number operators
$N_0^{s} = a_1^+a_1^- - \tfrac12$, $N_k^{s} = b_k^+b_k^- + \tfrac12$ (these span the
Cartan subalgebra of the symmetrized-quadratic realization and carry no $K$ component):
$H_1 = N_0^s + N_1^s$, $H_k = N_{k-1}^s - N_k^s$, $H_{n+1} = -N_n^s$.
Inverse: $N_n^s = -H_{n+1}$, $N_k^s = H_{k+1}+\dots+H_n - H_{n+1}$ ($1\le k<n$), $N_0^s = H_1 - N_1^s$.

Convention note (recorded ambiguity): `Cn1_definition.md` §2 lists the simple generator
$E_{2\delta_n} = \tfrac12 (b_n^+)^2$ but the "all root generators" table lists
$E_{\pm2\delta_k} = (b_k^\pm)^2$. We adopt **$(b_k^\pm)^2$ without the factor $\tfrac12$**
for `E_2del{k}_p/m`, matching the $B(0,n)$ v5.0 schema labels, so that the $\mathfrak{sp}(2n)$
part of the two schemas is identical.

## 4. Basis lists

### 4.1 $n=1$: $C(2)=\mathfrak{osp}(2|2)$, dim $4|4$

* even: `H_1, H_2, E_2del1_p, E_2del1_m`
* odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

### 4.2 $n=2$: $C(3)=\mathfrak{osp}(2|4)$, dim $11|8$

* even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
* odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

### 4.3 $n=3$: $C(4)=\mathfrak{osp}(2|6)$, dim $22|12$

* even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`
* odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm`

General rule (any $n$), produced by `src/C_generators.py`:

```
even = [H_1..H_{n+1}]
     + [E_2del{k}_p, k=1..n] + [E_del{i}_del{j}_pp, i<j]
     + [E_2del{k}_m, k=1..n] + [E_del{i}_del{j}_mm, i<j]
     + [E_del{i}_del{j}_pm, i<j] + [E_del{i}_del{j}_mp, i<j]
odd  = [E_eps1_del{k}_pp, k=1..n] + [E_eps1_del{k}_pm, k=1..n]
     + [E_eps1_del{k}_mp, k=1..n] + [E_eps1_del{k}_mm, k=1..n]
```
(pairs $i<j$ in lexicographic order.)

## 5. PBW ordering of the basis (decision)

Adopted ordering (**Option A**):
```
kappa < [odd: E_eps1_del{k}_pp (k=1..n), E_eps1_del{k}_pm, E_eps1_del{k}_mp, E_eps1_del{k}_mm]
      < [even: H_1..H_{n+1}, E_2del{k}_p, E_del{i}_del{j}_pp, E_2del{k}_m, E_del{i}_del{j}_mm,
               E_del{i}_del{j}_pm, E_del{i}_del{j}_mp]
```
$K = 1$ is excluded. The odd block is sorted first by the sign of $\varepsilon$
(`p*` before `m*`), then by the bosonic sign, then by $k$.

Options considered:

* **Option A (adopted)**: `kappa < [odd] < [even]`, odd block grouped by $\varepsilon$-sign.
  Mirrors the $B(0,n)$ v5.0 convention exactly (same position of $\kappa$, same even block
  order), so $B(0,n)$ tooling and documentation transfer unchanged. The grouping by
  $\varepsilon$-sign is natural because odd generators with the same $\varepsilon$-sign
  anticommute among themselves ($\{a_1^+b_k^\pm, a_1^+b_l^\pm\} = 0$ since $(a_1^+)^2 = 0$),
  so each $\varepsilon$-block is an abelian odd subalgebra and the $\mathfrak{so}(2)$
  grading ($\varepsilon$-charge $+1, -1$) is visible in the ordering.
* **Option B**: `kappa < [even] < [odd]`. Rejected: breaks compatibility with the $B(0,n)$
  convention for no mathematical gain.
* **Option C**: ordering by root height (all positive roots, then Cartan, then negative
  roots, odd and even interleaved). Rejected: mixes parities, which complicates the
  $\kappa$-sign bookkeeping in Schema 2–4 where $\kappa$ must be moved past odd factors only.

## 6. Structure constants and brackets

* $[X, Y\} = XY - (-1)^{p(X)p(Y)} YX$ (graded commutator in the oscillator algebra).
* Schema 1 stores **all ordered pairs** $(X,Y)$ with non-zero bracket:
  entries `{"X","Y","Z","coeff"}` mean $[X,Y\} = \sum_Z \text{coeff}\,Z$. Coefficients are
  exact rationals written as strings (`"1"`, `"-1/2"`).
* Deformed bracket (Schema 2): $[X,Y]_\gamma = [X,Y]_0 + \kappa\,\gamma(X,Y)$, with
  deformation parameters named `gb_a1{σ}_b{j}{s}` (e.g. `gb_a1p_b1m` $= \mathrm{gb}_{a_1^+, b_1^-}$),
  from $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$.
* Coboundary (Schema 4): $f(Z_j) = \sum_i \phi_{ij} Z_i$; unknowns named `phi[<Z_i>][<Z_j>]`.
