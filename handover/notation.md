# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project and finalized in Issue I01.

## 1. Algebra and oscillators

* $\mathfrak{g} = C(n+1) = \mathfrak{osp}(2|2n)$, $n \ge 1$ is the **bosonic rank**.
  File names use the bosonic rank: `C_{n}_*.json` (so $C(2)=\mathfrak{osp}(2|2)$ is `C_1_*.json`).
* **Fermionic pair** $a_1^\pm$ (labels `a_1_p`, `a_1_m`), parity 1, CAR:
  $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$.
* **Bosonic oscillators** $b_k^\pm$, $k = 1,\dots,n$ (labels `b_{k}_p`, `b_{k}_m`), parity 0, CCR:
  $[b_k^-, b_l^+] = \delta_{kl}$, $[b_k^\pm, b_l^\pm] = 0$.
* Undeformed mixed relations: $[b_k^\pm, a_1^\pm] = 0$.
* **Central elements**: $K$ (even, $K = 1$ in all realizations) and $\kappa$ (odd, $\kappa^2 = 0$,
  super-central: $\kappa b = b\kappa$, $\kappa a = -a\kappa$). Labels `K`, `kappa`.
* $\mathfrak{g}$ is the span of the *symmetrized* quadratic oscillator elements inside $\mathcal{U}(A)$.
  $\mathfrak{g}$ closes under the super-commutator without constants; constants that arise when
  writing $a_1^+a_1^-$ or $b_k^+b_k^-$ in terms of $\mathfrak{g}$ are recorded as multiples of $K$.

Generator suffix convention (inherited from B(0,n)): `p` $= +$, `m` $= -$. In a multi-letter
suffix the letters follow the order of the oscillators in the word (fermion first, then boson,
or $b_i$ then $b_j$ with $i<j$).

## 2. Root system and generator labels

Roots are written with $\varepsilon$ (fermionic, label `eps1`) and $\delta_k$ (bosonic, label `del{k}`).

| Root | Label | Oscillator word | Parity |
|---|---|---|---|
| (Cartan, simple root $k$) | `H_{k}`, $k=1,\dots,n+1$ | see below | 0 |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ | 0 |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ | 0 |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ | 0 |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ | 0 |
| $-\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ | 0 |
| $-\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ | 0 |
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ | 1 |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ | 1 |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ | 1 |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ | 1 |

Cartan generators (simple-root convention of `docs/math/Cn1_definition.md`):
$$
H_1 = a_1^+a_1^- + b_1^+b_1^-,\qquad
H_k = b_{k-1}^+b_{k-1}^- - b_k^+b_k^- \ (2 \le k \le n),\qquad
H_{n+1} = -b_n^+b_n^- - \tfrac12 .
$$
Equivalently, with the symmetrized number operators $N_a = a_1^+a_1^- - \tfrac12$,
$N_k = b_k^+b_k^- + \tfrac12$: $H_1 = N_a + N_1$, $H_k = N_{k-1} - N_k$, $H_{n+1} = -N_n$, and
conversely $N_k = \sum_{l=k+1}^{n} H_l - H_{n+1}$ ($1 \le k \le n$),
$N_a = H_1 - \sum_{k=2}^{n} H_k + H_{n+1}$. Hence
$a_1^+a_1^- = N_a + \tfrac12 K$ and $b_k^+b_k^- = N_k - \tfrac12 K$ (checked by
`tests/test_C_generators.py::test_cartan_change_of_basis`).

Normalization: $E_{\pm 2\delta_k} = (b_k^\pm)^2$ (no factor $\tfrac12$), as in the B(0,n) schema and
the "all root generators" list of `Cn1_definition.md`.

## 3. Basis lists

**Even basis** ($2n^2+n+1$ elements), in PBW order:
`H_1 … H_{n+1}`, `E_2del{k}_p` ($k=1..n$), `E_del{i}_del{j}_pp` ($i<j$),
`E_2del{k}_m`, `E_del{i}_del{j}_mm`, `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`.

**Odd basis** ($4n$ elements), in PBW order:
`E_eps1_del{k}_pp`, `E_eps1_del{k}_pm` ($k=1..n$), then `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm` ($k=1..n$).

### C(2), n=1 (dim 4|4)
* even: `H_1, H_2, E_2del1_p, E_2del1_m`
* odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

### C(3), n=2 (dim 11|8)
* even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
* odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm`

### C(4), n=3 (dim 22|12)
* even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`
* odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del3_mp, E_eps1_del3_mm`

## 4. PBW ordering

Chosen convention (same shape as B(0,n)):
$$\kappa \;<\; [\text{odd}: E_{\varepsilon\pm\delta_k},\ \text{then}\ E_{-\varepsilon\pm\delta_k}] \;<\; [\text{even}: H_k,\ E_{2\delta},\ E_{\delta+\delta},\ E_{-2\delta},\ E_{-\delta-\delta},\ E_{\delta-\delta},\ E_{-\delta+\delta}].$$
$K = 1$ is excluded from the basis and the ordering. Within the odd block the $\varepsilon$-sign is the
primary key, then $k$, then the $\delta$-sign; this groups the $a_1^+$ words before the $a_1^-$ words,
matching the oscillator normal order below.

Oscillator (normal) ordering used for `standard_form` words:
`kappa, a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m, …` (creation before annihilation).

## 5. Deformation parameters

$\mathrm{gb}_{\sigma,j,s}$, $\sigma,s\in\{+,-\}$, $j=1..n$ ($4n$ parameters), label `gb_a1{σ}_b{j}{s}`
(e.g. `gb_a1p_b1m` $= \mathrm{gb}_{a_1^+, b_1^-}$), arranged as the $2\times 2n$ **gb matrix**
(rows `a_1_p`, `a_1_m`; columns `b_1_p, b_1_m, …, b_n_p, b_n_m`). Deformed relation:
$[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$. The gb are scalar coefficients of the
odd (boson–fermion) block of the pre-oscillator form; "parity 1" in the math notes refers to that block.

## 6. Brackets and coefficients

* $[X,Y\}$ is the super-commutator; `structure_constants` entries `{X, Y, Z, coeff}` mean
  $[X,Y\} = \sum_Z \text{coeff}\cdot Z$. All ordered pairs with a non-zero bracket are stored.
* Coefficients are exact rationals written as strings (`"1/2"`, `"-4"`); polynomial coefficients in
  gb are written as strings such as `"gb_a1p_b1m - 2*gb_a1m_b1p"` with a parallel `coeff_terms` map.
