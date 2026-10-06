# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

*(Finalized in Issue I01; used by all later issues.)*

### 1. Algebra and rank

- $C(n+1) = \mathfrak{osp}(2|2n)$, $n \geq 1$ is the **bosonic rank** (number of boson pairs).
  File names use $n$: C(2) → `C_1_*`, C(3) → `C_2_*`, C(4) → `C_3_*`.
- $\varepsilon$ (written `eps1` in labels, since $m=1$) is the fermionic weight; $\delta_1,\dots,\delta_n$ are the bosonic weights.
- Superdimension: even $= 2n^2+n+1$, odd $= 4n$, total $= 2n^2+5n+1$.

### 2. Oscillator labels

| Symbol | Label | Parity | Relations |
|---|---|---|---|
| $a_1^+$, $a_1^-$ | `a_1_p`, `a_1_m` | 1 | CAR: $\{a_1^-,a_1^+\}=1$, $(a_1^\pm)^2=0$ |
| $b_k^+$, $b_k^-$ | `b_k_p`, `b_k_m` | 0 | CCR: $[b_k^-,b_l^+]=\delta_{kl}$, all other brackets 0 |
| $\kappa$ | `kappa` | 1 | odd central, $\kappa^2=0$ (deformation symbol, Schema 2+) |
| $K$ | `K` | 0 | even central, identified with the scalar 1 |

Undeformed: $[b_k^\pm, a_1^\pm]=0$. Deformed (Schema 2): $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$.

**Oscillator word order** (used for the standard / normal-ordered form of every word):
$$\kappa < a_1^+ < a_1^- < b_1^+ < b_1^- < b_2^+ < b_2^- < \dots < b_n^+ < b_n^-.$$
Every generator realization is stored as a sum of words already in this order.

### 3. Generator labels and realizations

| Root | Label | Realization (standard form) | Parity |
|---|---|---|---|
| Cartan | `H_1` | $a_1^+a_1^- + b_1^+b_1^-$ | 0 |
| Cartan | `H_k` ($2\le k\le n$) | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ | 0 |
| Cartan | `H_{n+1}` | $-b_n^+b_n^- - \tfrac12$ | 0 |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ | 0 |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ | 0 |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ | 0 |
| $-\delta_i-\delta_j$ | `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ | 0 |
| $\delta_i-\delta_j$ | `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ | 0 |
| $-\delta_i+\delta_j$ | `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ | 0 |
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+b_k^+$ | 1 |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+b_k^-$ | 1 |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^-b_k^+$ | 1 |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^-b_k^-$ | 1 |

Suffix rule: the first letter of the suffix is the sign of the first oscillator, the second letter the sign of the second oscillator (same as B(0,n)).

**Normalization decisions**
- $E_{\pm2\delta_k} = (b_k^\pm)^2$ for *all* $k$ (the uniform "all root generators" formula of `Cn1_definition.md`).
  The Chevalley-normalized simple generator $\tfrac12(b_n^\pm)^2$ of the same document differs only by the factor $\tfrac12$;
  we do not use it, so that the labels and coefficients match the B(0,n) table.
- Odd generators are written with the fermion first ($a_1^\sigma b_k^s$). The simple-root form $E_{\delta_1-\varepsilon}=b_1^+a_1^-$
  equals $a_1^-b_1^+$ in the undeformed algebra; in the deformed algebra the two differ by a central $\kappa$-term,
  so the fermion-first form is the *definition*.
- The Cartan elements are exactly the ones in `Cn1_definition.md`. They are super-symmetrized quadratics
  ($H_1 = (a_1^+a_1^- - \tfrac12) + (b_1^+b_1^- + \tfrac12)$, $H_{n+1} = -(b_n^+b_n^- + \tfrac12)$), which is why the
  span of the basis is closed under the bracket without producing $K$.

### 4. Basis and PBW ordering

**Chosen PBW ordering (Option A, B(0,n)-compatible)**:
$$\kappa < [\text{odd}] < [\text{even}]$$
- odd block: `E_eps1_del{k}_pp` ($k=1..n$), `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm`
  (positive odd roots $\varepsilon\pm\delta_k$ first, then negative ones, mirroring B(0,n)'s "all `_p` then all `_m`");
- even block: `H_1..H_{n+1}`, `E_2del{k}_p`, `E_del{i}_del{j}_pp`, `E_2del{k}_m`, `E_del{i}_del{j}_mm`,
  `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp` (exactly the B(0,n) even order, with one extra Cartan).
- $K$ ($=1$) is excluded from the basis and PBW ordering, as for B(0,n).

Options considered (I01): (A) above; (B) odd generators interleaved per $k$ (`pp, pm, mp, mm` for $k=1$, then $k=2$, …);
(C) triangular ordering $\mathfrak n^- < \mathfrak h < \mathfrak n^+$. A was chosen because it changes the B(0,n) convention
in the minimal way (κ < odd < even, positive before negative inside the odd block), keeps all B(0,n)-type even labels
in identical positions, and the ordering has no effect on the structure constants themselves.

**Basis lists**

C(2) = osp(2|2), $n=1$ (4|4):
- even: `H_1, H_2, E_2del1_p, E_2del1_m`
- odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

C(3) = osp(2|4), $n=2$ (11|8):
- even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

C(4) = osp(2|6), $n=3$ (22|12):
- even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`
- odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm`

### 5. Brackets and signs

- Graded bracket: $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$, computed in the oscillator algebra and re-expanded in the basis.
- $\kappa$ is supercentral: $\kappa x = (-1)^{p(x)} x\kappa$; it is always moved to the far left.
- Deformed bracket: $[X,Y]_\gamma = [X,Y]_0 + \kappa\,\gamma(X,Y)$.
- Coefficients are exact rationals written as strings (`"1"`, `"-1/2"`); symbolic coefficients use `gb_{σ}_{j}_{s}` for $\mathrm{gb}_{a_1^\sigma,b_j^s}$, e.g. `gb_p_1_m` (Schema 2), and `phi_{i}_{j}` for $\phi_{ij}$ (Schema 4).
