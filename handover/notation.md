# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project and finalized in Issue I01.

## 1. Algebra

- $C(n+1) = \mathfrak{osp}(2|2n)$, bosonic rank $n$. Examples: $C(2)$ ($n=1$), $C(3)$ ($n=2$), $C(4)$ ($n=3$).
- Even part $\mathfrak{g}_{\bar 0} \cong \mathfrak{so}(2)\oplus\mathfrak{sp}(2n)$, $\dim = 2n^2+n+1$.
- Odd part $\mathfrak{g}_{\bar 1}$, $\dim = 4n$.
- Total $\dim = 2n^2+5n+1$.

| $n$ | algebra | even | odd | total |
|---|---|---|---|---|
| 1 | $C(2)$ | 4 | 4 | 8 |
| 2 | $C(3)$ | 11 | 8 | 19 |
| 3 | $C(4)$ | 22 | 12 | 34 |

## 2. Oscillators and labels

| Object | Label in JSON | Realization |
|---|---|---|
| Standard fermion, creation | `a_1_p` | $a_1^+$ (parity 1) |
| Standard fermion, annihilation | `a_1_m` | $a_1^-$ (parity 1) |
| Boson, creation, $k=1..n$ | `b_k_p` | $b_k^+$ (parity 0) |
| Boson, annihilation, $k=1..n$ | `b_k_m` | $b_k^-$ (parity 0) |

Relations: CAR $\{a_1^-,a_1^+\}=1$, $(a_1^\pm)^2=0$; CCR $[b_k^-,b_l^+]=\delta_{kl}$, $[b_k^\pm,b_l^\pm]=0$; $[b_k^\pm,a_1^\pm]=0$ in the undeformed algebra.

The sign suffix `_p` / `_m` always means $+$ / $-$. For roots, the first sign is the $\varepsilon$ sign and the second is the $\delta_k$ sign.

## 3. Root generators (final, fixed by I01)

Normalization: all root vectors are given by the "All root generators" formulas of `docs/math/Cn1_definition.md` with coefficient 1. In particular $E_{\pm 2\delta_k} = (b_k^\pm)^2$ (no $\tfrac12$), matching the B(0,n) schema.

| Root | Label | Realization |
|---|---|---|
| $\pm 2\delta_k$ | `E_2del{k}_p` / `E_2del{k}_m` | $(b_k^\pm)^2$ |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

Cartan generators (no $\varepsilon$-dependence beyond $H_1$):

$$
H_1 = a_1^+a_1^- + b_1^+b_1^-,\qquad
H_k = b_{k-1}^+b_{k-1}^- - b_k^+b_k^-\ (2\le k\le n),\qquad
H_{n+1} = -b_n^+b_n^- - \tfrac12 .
$$

$H_{n+1}$ is the only generator with a constant term. The constant $1$ is the identity; it is identified with $K$ and is not a basis element.

## 4. Basis and PBW ordering (decision for I01)

### Options considered

- **(A) odd-first**: $\kappa < [\text{odd}] < [\text{even}]$, the same block structure as the B(0,n) schema. Chosen.
- **(B) even-first**: $[\text{even}] < [\text{odd}]$. Rejected: it breaks comparability with the B(0,n) schema, and the odd block is the part that carries the deformation parameters.
- **(C) $\varepsilon$-sign blocked**: $[\varepsilon\text{-positive odd}] < [\text{even}] < [\varepsilon\text{-negative odd}]$. This follows the $\varepsilon$-grading (triangular decomposition). It is the most natural choice for a Borel-type PBW theorem, but it splits the odd block and makes the parallel with B(0,n) less direct. Rejected for this schema, to be revisited only if a triangular decomposition is needed.

### Chosen ordering

Odd block, ordered by (ε-sign, δ-sign, k) with $+$ before $-$:

$$
E_{\text{eps1,del}1\_pp},\ldots,E_{\text{eps1,del}n\_pp},\ E_{\ldots\_pm},\ E_{\ldots\_mp},\ E_{\ldots\_mm}.
$$

Even block: $H_1,\ldots,H_{n+1}$; $E_{2\delta_k}$ for $k=1..n$; $E_{-2\delta_k}$ for $k=1..n$; then $E_{\delta_i+\delta_j}$, $E_{\delta_i-\delta_j}$, $E_{-\delta_i+\delta_j}$, $E_{-\delta_i-\delta_j}$, each over $i<j$ in lexicographic order.

Justification: the choice only fixes the index convention and the order of listing. It does not change the structure constants up to a permutation of indices. The computation uses Weyl-type normal ordering in the oscillator algebra, which is a separate object from the PBW basis of $U(\mathfrak g)$.

## 5. Generator labels

- Odd: `E_eps1_del{k}_{st}` with $s,t \in\{p,m\}$, where $s$ is the sign of $\varepsilon$ and $t$ is the sign of $\delta_k$. Example: `E_eps1_del2_mp` $= a_1^- b_2^+$ $= E_{-\varepsilon+\delta_2}$.
- Even root: `E_2del{k}_{p|m}`, `E_del{i}_del{j}_{pp|pm|mp|mm}`.
- Cartan: `H_1` ... `H_{n+1}`.
- Parity: $0$ for even, $1$ for odd.

## 6. Deformation notation

- $\kappa$: odd central element, $p(\kappa)=1$, $\kappa^2=0$.
- $K$: even central element, identified with the scalar $1$.
- Deformed bracket: $[X,Y]_\gamma = [X,Y]_0 + \kappa\,\gamma(X,Y)$.
- gb parameters: $\mathrm{gb}_{\sigma,k,s}$ for $\sigma\in\{+,-\}$ (fermion $a_1^\sigma$), $k=1..n$, $s\in\{+,-\}$ (boson $b_k^s$), with
  $[b_k^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,k,s}\,\kappa$. There are $4n$ of them.
  Label in JSON: `gb_a1{sigma}_b{k}{s}`, e.g. `gb_a1p_b1m`.

## 7. Coboundary notation

- Odd linear map $f:\mathfrak g\to\mathfrak g$ with $p(f(X))=p(X)+1$.
- $(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y])$ (as in `docs/math/C_coboundary_definition.md`).
- Triviality: $\gamma = \delta f$ for some odd $f$. "Up to scalar" is absorbed by rescaling $f$, so the condition is linear in $\gamma$ and $f$.
