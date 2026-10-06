# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

Finalized in **Issue I01** (C(n+1) = osp(2|2n) basis, PBW ordering, generator labels).

## Conventions

### 1. Algebra and indices

- $C(n+1) = \mathfrak{osp}(2|2n)$, with **bosonic rank** $n$.
  File naming uses the bosonic rank $n$: C(2) → `C_1_*`, C(3) → `C_2_*`, C(4) → `C_3_*`.
- Orthogonal weight vectors: one fermionic $\varepsilon$ and $n$ bosonic $\delta_1,\dots,\delta_n$.
- Root system (Frappat–Sciarrino–Sorba):
  $$\Delta = \{\pm\delta_k\pm\delta_l,\ \pm 2\delta_k,\ \pm\varepsilon\pm\delta_k\},\quad 1\le k<l\le n.$$
  - Even roots $\Delta_{\bar 0}$: $\pm 2\delta_k$ and $\pm(\delta_i\pm\delta_j)$ ($i<j$).
  - Odd roots $\Delta_{\bar 1}$: $\pm\varepsilon\pm\delta_k$ ($4n$ total).
- Even subalgebra $\mathfrak{so}(2)\times\mathfrak{sp}(2n)$, dimension $2n^2+n+1$.
- **Superdimension**: even $=2n^2+n+1$, odd $=4n$, total $=2n^2+5n+1$.

| $C(n+1)$ | $n$ | even | odd | total |
|---|---|---|---|---|
| C(2)=osp(2\|2) | 1 | 4 | 4 | 8 |
| C(3)=osp(2\|4) | 2 | 11 | 8 | 19 |
| C(4)=osp(2\|6) | 3 | 22 | 12 | 34 |

### 2. Oscillator realization

- **Standard fermionic pair** $a_1^+,a_1^-$: CAR $\{a_1^-,a_1^+\}=1$, $(a_1^\pm)^2=0$, parity $1$.
  Replaces the supplementary fermion $a_0$ of $B(0,n)$.
- **Bosonic oscillators** $b_k^\pm$ ($k=1,\dots,n$): CCR $[b_k^-,b_l^+]=\delta_{kl}$, parity $0$.
- Bosons and fermions commute in the **undeformed** algebra: $[b_k^s,a_1^\sigma]=0$.
- Number operators: $N_a=a_1^+a_1^-$, $N_k=b_k^+b_k^-$ ($n+1$ of them, spanning the Cartan).

### 3. Generator labels (JSON schema)

All generators are degree-2 oscillator words. Label ↔ realization:

| Root | Label | Realization | Parity |
|---|---|---|---|
| Cartan $H_1$ | `H_1` | $a_1^+a_1^- + b_1^+b_1^-$ | 0 |
| Cartan $H_k$ ($2\le k\le n$) | `H_k` | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ | 0 |
| Cartan $H_{n+1}$ | `H_{n+1}` | $-b_n^+b_n^- - \tfrac12$ | 0 |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ | 0 |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ | 0 |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ | 0 |
| $-(\delta_i+\delta_j)$ | `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ | 0 |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ | 0 |
| $-(\delta_i-\delta_j)$ | `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ | 0 |
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+b_k^+$ | 1 |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+b_k^-$ | 1 |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^-b_k^+$ | 1 |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^-b_k^-$ | 1 |

Convention for the odd label `E_eps1_del{k}_{s1}{s2}`: `s1` is the sign of $\varepsilon$
(`p`=$+$, `m`=$-$), `s2` is the sign of $\delta_k$. The Cartan generators $H_1,\dots,H_{n+1}$
follow Frappat exactly; $H_{n+1}$ carries the constant $-\tfrac12$ from normal ordering.

### 4. Explicit even/odd basis lists

**C(2), $n=1$** (even 4, odd 4):
- even: `H_1, H_2, E_2del1_p, E_2del1_m`
- odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

**C(3), $n=2$** (even 11, odd 8):
- even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- odd: `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

**C(4), $n=3$** (even 22, odd 12):
- even: `H_1, H_2, H_3, H_4,`
  `E_2del1_p, E_2del2_p, E_2del3_p,`
  `E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,`
  `E_2del1_m, E_2del2_m, E_2del3_m,`
  `E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,`
  `E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,`
  `E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`
- odd: `E_eps1_del{k}_pp (k=1..3), E_eps1_del{k}_pm, E_eps1_del{k}_mp, E_eps1_del{k}_mm`

### 5. PBW ordering

Two options were considered:

- **Option A** (chosen): `κ < [odd] < [even]`, i.e.
  $$\kappa \prec \big[\text{odd: }E_{\varepsilon\pm\delta_k\ \dots}\big]\prec\big[\text{even: }H_i,\ E_{2\delta_k},\ E_{\delta_i\pm\delta_j}\big].$$
  Within even: Cartan $H_1,\dots,H_{n+1}$, then raising blocks ($2\delta_k$ `_p`, then $\delta_i+\delta_j$ `_pp`),
  then lowering blocks (`_m`, `_mm`), then mixed (`_pm`, `_mp`). Within odd: grouped by sign block
  `pp, pm, mp, mm`, each ranging over $k=1,\dots,n$.
- **Option B** (rejected): order strictly by root height / by a chosen positive-system height function,
  interleaving even and odd generators.

**Decision & justification**: Option A is adopted because it is **backward compatible** with the
existing $B(0,n)$ v5.0 schema (which uses `κ < [odd] < [even]`), so downstream Schema 2–4 tooling and
the $B(0,n)$ reference code transfer with minimal change. Grading the odd sector first also keeps the
central odd element $\kappa$ adjacent to the odd generators it pairs with in the deformation, which
simplifies the γ-structure bookkeeping (Schema 2). Option B would reorder generators relative to
$B(0,n)$ and provide no computational benefit for the structure-constant engine, which is
basis-order agnostic (it decomposes bracket results into whatever basis order is declared).

### 6. Central elements

- $\kappa$: odd ($p=1$), nilpotent $\kappa^2=0$; formal symbol of the nilpotent extension and carrier
  of the inhomogeneous deformation. Listed in the top-level `central_elements` key with
  **parity 1** (per the I02 unified rule; this is the mathematically correct odd parity, consistent
  with $C$ inhomogeneous deformation where $\kappa$ is odd).
- $K$: even central identity, identified with the scalar $1$; excluded from the PBW basis lists.
