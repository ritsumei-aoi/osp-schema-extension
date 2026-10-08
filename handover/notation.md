# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

Conventions were finalized in Issue I01 and are extended by I02 (schema keys),
I05 (deformation parameters), and I07 (coboundary map).

## 1. Algebra

$C(n+1) = \mathfrak{osp}(2|2n)$, bosonic rank $n \geq 1$, fermionic rank $m = 1$.

| $n$ | Cartan type | osp | even | odd | total |
|---|---|---|---|---|---|
| 1 | C(2) | osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) | osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) | osp(2\|6) | 22 | 12 | 34 |

Formulas: even $= 2n^2 + n + 1$, odd $= 4n$, total $= 2n^2 + 5n + 1$.

File naming: `C_{n}_structure.json`, `C_{n}_gamma.json`, `C_{n}_evaluated.json`,
`C_{n}_coboundary.json`, where `n` is the **bosonic rank** (C(2) is `n=1`).

## 2. Oscillators

| Label | Symbol | Parity | Relations |
|---|---|---|---|
| `a_1_p`, `a_1_m` | $a_1^+, a_1^-$ | 1 | $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$ |
| `b_k_p`, `b_k_m` ($1 \le k \le n$) | $b_k^+, b_k^-$ | 0 | $[b_k^-, b_l^+] = \delta_{kl}$, $[b_k^\pm, b_l^\pm] = 0$ |
| `kappa` | $\kappa$ | 1 | odd central, $\kappa^2 = 0$ |
| `K` | $K$ | 0 | even central, identified with the scalar $1$ |

Undeformed mixed relation: $[b_k^s, a_1^\sigma] = 0$.
Deformed mixed relation (Schema 2, I05): $[b_k^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,k,s}\,\kappa$.

Suffix convention: `_p` = $+$ (creation), `_m` = $-$ (annihilation).

**Oscillator normal order** (used for `standard_form` words):
```
kappa < a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ... < b_n_p < b_n_m
```
Every oscillator word is written in this order; reordering uses the
(anti)commutation relations above. A word never contains two `kappa`'s
($\kappa^2 = 0$) nor two equal fermionic letters ($(a_1^\pm)^2 = 0$).

## 3. Roots and generator labels

Root vectors: $\varepsilon$ (fermionic direction) and $\delta_1, \ldots, \delta_n$ (bosonic).

| Root | Label | Oscillator realization | Parity |
|---|---|---|---|
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

In the odd labels the **first** sign letter refers to $\varepsilon$ and the
**second** to $\delta_k$. The `eps1` index is fixed to 1 because $m = 1$.

Normalization: $E_{\pm 2\delta_k} = (b_k^\pm)^2$ **without** the factor $\tfrac12$
(this is the "all root generators" normalization of `Cn1_definition.md` §2 and the
B(0,n) convention). Consequently $[E_{2\delta_n}, E_{-2\delta_n}] = 4 H_{n+1}$.

### Cartan generators (Frappat distinguished simple-root form)

| Label | Realization | Simple root |
|---|---|---|
| `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ | $\alpha_1 = \varepsilon - \delta_1$ (odd) |
| `H_k` ($2 \le k \le n$) | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ | $\alpha_k = \delta_{k-1} - \delta_k$ |
| `H_{n+1}` | $-b_n^+ b_n^- - \tfrac12$ | $\alpha_{n+1} = 2\delta_n$ |

$H_k = [E_{\alpha_k}, E_{-\alpha_k}\}$ for $k = 1, \ldots, n$ and
$[E_{2\delta_n}, E_{-2\delta_n}] = 4 H_{n+1}$ (because of the normalization above).

The constant $-\tfrac12$ in $H_{n+1}$ is **required for closure**; the Cartan
subalgebra is spanned by the symmetrized number operators
$a_1^+a_1^- - \tfrac12$ and $b_k^+ b_k^- + \tfrac12$.

## 4. Basis lists and PBW ordering

**PBW ordering (decided in I01):**
```
kappa < [odd generators] < [even generators]
```
with the internal orders

- odd: `E_eps1_del{k}_pp` ($k=1..n$), `E_eps1_del{k}_pm` ($k=1..n$),
  `E_eps1_del{k}_mp` ($k=1..n$), `E_eps1_del{k}_mm` ($k=1..n$);
- even: `H_1`, ..., `H_{n+1}`,
  `E_2del{k}_p` ($k=1..n$), `E_del{i}_del{j}_pp` ($i<j$),
  `E_2del{k}_m` ($k=1..n$), `E_del{i}_del{j}_mm` ($i<j$),
  `E_del{i}_del{j}_pm` ($i<j$), `E_del{i}_del{j}_mp` ($i<j$).

$K$ is excluded from the basis and from the PBW order (it is the scalar 1).

### C(2), n = 1 (even 4, odd 4)

```
even: H_1, H_2, E_2del1_p, E_2del1_m
odd:  E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm
```

### C(3), n = 2 (even 11, odd 8)

```
even: H_1, H_2, H_3,
      E_2del1_p, E_2del2_p, E_del1_del2_pp,
      E_2del1_m, E_2del2_m, E_del1_del2_mm,
      E_del1_del2_pm, E_del1_del2_mp
odd:  E_eps1_del1_pp, E_eps1_del2_pp,
      E_eps1_del1_pm, E_eps1_del2_pm,
      E_eps1_del1_mp, E_eps1_del2_mp,
      E_eps1_del1_mm, E_eps1_del2_mm
```

### C(4), n = 3 (even 22, odd 12)

```
even: H_1, H_2, H_3, H_4,
      E_2del1_p, E_2del2_p, E_2del3_p,
      E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
      E_2del1_m, E_2del2_m, E_2del3_m,
      E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
      E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,
      E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp
odd:  E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp,
      E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm,
      E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp,
      E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm
```

The lists are generated programmatically by `src/C_generators.py`
(`even_basis(n)`, `odd_basis(n)`); the lists above are the ground truth the
code is tested against.

## 5. Brackets

$[X, Y\} = XY - (-1)^{p(X)p(Y)} YX$ (graded bracket), computed in the universal
enveloping algebra of the oscillator extension $A = V \oplus \mathbb{C}K \oplus \mathbb{C}\kappa$.
Structure constants are stored as `{"X", "Y", "Z", "coeff"}` entries meaning
$[X, Y\} = \sum_Z \mathrm{coeff}\, Z$. All coefficients are exact rationals
(strings such as `"1"`, `"-1/2"`, `"4"`).

## 6. Deformation parameters (Schema 2, see I05)

$\mathrm{gb}_{\sigma,k,s}$, $\sigma, s \in \{+,-\}$, $k = 1..n$ ($4n$ parameters) with labels
```
gb_a1{σ}_b{k}{s}      e.g.  gb_a1p_b1p, gb_a1p_b1m, gb_a1m_b1p, gb_a1m_b1m
```
arranged as the $2 \times 2n$ **gb matrix** (rows: `a_1_p`, `a_1_m`; columns:
`b_1_p, b_1_m, ..., b_n_p, b_n_m`).

Deformed bracket: $[X,Y]_\gamma = [X,Y]_0 + \kappa\,\gamma(X,Y)$;
$\gamma$ takes values in $\mathfrak{g} \oplus \mathbb{C}K$ (see I05 Response for why $K$ is needed).

## 7. Coboundary (Schema 4, see I07)

Odd linear map $f(Z_j) = \sum_i \phi_{ij} Z_i$;
$(\delta f)(X,Y) = (-1)^{p(X)}[X, f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y, f(X)] - f([X,Y])$
(exactly the formula of `docs/math/C_coboundary_definition.md`).
