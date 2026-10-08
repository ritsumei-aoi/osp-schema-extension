# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project and finalized in Issue I01.

## 1. Algebra and oscillators

| Symbol | Meaning |
|---|---|
| $C(n+1) = \mathfrak{osp}(2\|2n)$ | Target Lie superalgebra; $n \ge 1$ is the **bosonic rank**. $C(2)=\mathfrak{osp}(2\|2)$, $C(3)=\mathfrak{osp}(2\|4)$, $C(4)=\mathfrak{osp}(2\|6)$. |
| $a_1^\pm$ (`a_1_p`, `a_1_m`) | Standard fermionic pair, parity 1, CAR $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$. Replaces the supplementary fermion $a_0$ of $B(0,n)$. |
| $b_k^\pm$ (`b_k_p`, `b_k_m`), $k=1,\dots,n$ | Bosonic oscillators, parity 0, CCR $[b_k^-, b_l^+] = \delta_{kl}$. |
| $K$ (`K`) | Even central identity of the pre-oscillator extension $A = V \oplus \mathbb{C}K \oplus \mathbb{C}\kappa$; identified with the scalar $1$. Never a basis element. |
| $\kappa$ (`kappa`) | Odd, super-central ($[\kappa, X\} = 0$), nilpotent ($\kappa^2 = 0$) symbol of the inhomogeneous deformation. Never a basis element of $C(n+1)$. |
| $\mathfrak{g}$ | $C(n+1)$ itself (dimension $2n^2+5n+1$). |
| $\tilde{\mathfrak{g}} = \mathfrak{g} \oplus \mathbb{C}K$ | $C(n+1)$ extended by the central identity; the natural target of the deformation cocycle $\gamma$ (see I05). |
| $N_a = a_1^+ a_1^-$, $N_k = b_k^+ b_k^-$ | Number operators (used only in derivations, not as basis labels). |

Graded bracket: $[X, Y\} = XY - (-1)^{p(X)p(Y)} YX$ computed in the universal enveloping
algebra of the oscillators. Dimensions: even $= 2n^2+n+1$, odd $= 4n$, total $= 2n^2+5n+1$.

## 2. Root system and generator labels

Roots are written in the orthogonal basis $(\varepsilon, \delta_1, \dots, \delta_n)$:
$\Delta_{\bar 0} = \{\pm 2\delta_k,\ \pm\delta_i \pm \delta_j\ (i<j)\}$,
$\Delta_{\bar 1} = \{\pm\varepsilon \pm \delta_k\}$.
Simple roots (Frappat): $\varepsilon - \delta_1,\ \delta_1 - \delta_2,\ \dots,\ \delta_{n-1} - \delta_n,\ 2\delta_n$.

Label rule: `p` = sign $+$, `m` = sign $-$; in a two-letter suffix the first letter refers to
the first oscillator in the word, the second letter to the second. Every root vector is a
single oscillator word with coefficient $1$.

| Root | Label | Realization | Parity |
|---|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ | 1 |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ | 1 |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ | 1 |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ | 1 |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ | 0 |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ | 0 |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ | 0 |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ | 0 |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ | 0 |
| $-\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ | 0 |

Cartan subalgebra ($n+1$ elements, labels `H_1`, ..., `H_{n+1}`), following `Cn1_definition.md`:

$$
H_1 = a_1^+ a_1^- + b_1^+ b_1^-,\qquad
H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-\ (2 \le k \le n),\qquad
H_{n+1} = -b_n^+ b_n^- - \tfrac12 .
$$

The constant $-\tfrac12$ in $H_{n+1}$ is part of the generator (it is forced by
$[E_{2\delta_n}, E_{-2\delta_n}] = 4 H_{n+1}$). The Cartan span equals
$\mathrm{span}\{N_a - \tfrac12,\ N_k + \tfrac12\}$, so the scalar $1$ (i.e. $K$) is **not**
in $\mathfrak{g}$; $N_a - \tfrac12 = H_1 - H_2 - \cdots - H_n + H_{n+1}$ generates the $\mathfrak{so}(2)$ factor.

**Normalization decision.** `Cn1_definition.md` lists $E_{2\delta_n} = \tfrac12 (b_n^+)^2$ among the
simple generators but $E_{\pm 2\delta_k} = (b_k^\pm)^2$ among "all root generators". We adopt
coefficient $1$ for all root vectors (consistent with the $B(0,n)$ JSON convention
`E_2del{k}_p` $= (b_k^+)^2$); the factor $\tfrac12$ only rescales structure constants.

## 3. Basis lists (even / odd) for $C(2)$, $C(3)$, $C(4)$

Ordering inside each list is the PBW order of Section 4.

**$C(2)$, $n=1$ (even 4, odd 4, total 8)**
- even: `H_1, H_2, E_2del1_p, E_2del1_m`
- odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

**$C(3)$, $n=2$ (even 11, odd 8, total 19)**
- even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

**$C(4)$, $n=3$ (even 22, odd 12, total 34)**
- even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`
- odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm`

General rule (implemented in `src/C_generators.py`):
- even $=$ `H_1..H_{n+1}` ; `E_2del{k}_p` ($k\uparrow$) ; `E_del{i}_del{j}_pp` (lexicographic $i<j$) ; `E_2del{k}_m` ; `E_del{i}_del{j}_mm` ; `E_del{i}_del{j}_pm` ; `E_del{i}_del{j}_mp`
- odd $=$ `E_eps1_del{k}_pp` ($k\uparrow$) ; `..._pm` ; `..._mp` ; `..._mm`

## 4. PBW ordering

**Generator level**: $\kappa\ <\ [\text{odd}]\ <\ [\text{even}]$, with the inner orders of Section 3.
$K = 1$ is excluded.

**Oscillator level** (used for normal-ordered "standard forms"):
`kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m`
(creation before annihilation inside each pair; fermions before bosons).

Options considered (I01):
1. **(adopted)** $\kappa <$ odd $<$ even, odd roots grouped by sign pattern `pp, pm, mp, mm` then by $k$. Mirrors the $B(0,n)$ convention `κ < [odd] < [even]` exactly, keeps the odd nilpotent symbol adjacent to the odd generators, and reduces to the $B(0,n)$ layout when the fermion pair is collapsed.
2. $\kappa <$ even $<$ odd (Cartan first). Rejected: breaks compatibility with the $B(0,n)$ schema and the existing B tooling that assumes odd-first lists.
3. Root-height ordering (Cartan, then positive roots by height, then negatives, mixed parity). Rejected: natural for Chevalley bases but the odd/even split is what the 4-layer schema and the coboundary parameterization (odd map $f$) need; height order would scatter the odd generators.

## 5. Deformation parameters (preview of I05)

$\mathrm{gb}_{a_1^\sigma, b_j^s}$ is labelled `gb_a1{σ}_b{j}{s}` (e.g. `gb_a1p_b1m` $= \mathrm{gb}_{a_1^+, b_1^-}$);
there are $4n$ of them, arranged as a $2 \times 2n$ matrix (rows `a_1_p, a_1_m`; columns `b_1_p, b_1_m, ..., b_n_p, b_n_m`).
Deformed relation: $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma, j, s}\,\kappa$. The gb's are treated as
scalar parameters (see I05 for the parity discussion).

## 6. File naming

`data/C_{n}_structure.json`, `C_{n}_gamma.json`, `C_{n}_evaluated.json`, `C_{n}_coboundary.json`
with $n$ the bosonic rank ($C(2) \to$ `C_1_...`).
