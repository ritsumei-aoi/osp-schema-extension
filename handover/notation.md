# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Algebras

- $B(0,n) = \mathfrak{osp}(1|2n)$: base case, supplementary fermion $a_0$.
- $C(n+1) = \mathfrak{osp}(2|2n)$: extension, standard fermionic pair $a_1^\pm$.

### Oscillators

| Symbol | Label | Parity | Relation |
|---|---|---|---|
| $a_1^+$ | `a1p` | 1 (odd) | $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$ |
| $a_1^-$ | `a1m` | 1 (odd) | same |
| $b_k^+$ | `bkp` | 0 (even) | $[b_k^-, b_l^+] = \delta_{kl}$ |
| $b_k^-$ | `bkm` | 0 (even) | same |

Normal-ordering convention: $a_1^+ < a_1^- < b_1^+ < b_1^- < b_2^+ < b_2^- < \cdots < b_n^+ < b_n^-$ (creation-type precedes annihilation-type within each mode).

### Generator Labels for $C(n+1)$

#### Even generators

| Root / description | Label | Oscillator realization |
|---|---|---|
| Cartan $H_k$ ($k=1,\ldots,n$) | `H_{k}` | see below |
| Cartan $H_{n+1}$ | `H_{n+1}` | $-b_n^+ b_n^- - \tfrac{1}{2}$ |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i < j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i < j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\delta_i - \delta_j$ ($i < j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i < j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |

Cartan realizations:
- $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$
- $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $k = 2, \ldots, n$
- $H_{n+1} = -b_n^+ b_n^- - \tfrac{1}{2}$

#### Odd generators

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

### PBW Ordering

**Decision**: Option A (parity-first, matching B(0,n) schema convention).

Two options were considered:
- **Option A** (chosen): $\kappa < [\text{odd generators}] < [\text{even generators}]$, where within each parity block generators are ordered by their root labels lexicographically. This matches the B(0,n) PBW convention and preserves backward compatibility.
- **Option B**: $\kappa < a_1^+ < a_1^- < b_1^+ < b_1^- < \cdots$ (oscillator ordering). This is more natural for the enveloping algebra but differs from the schema convention.

**Justification for Option A**: the B(0,n) schema uses parity-first PBW ordering; maintaining this convention ensures the schema format remains consistent and the JSON structure-constant entries can be compared directly across algebra families.

Full PBW order:
$$\kappa \ < \ [\text{odd: } E\_\text{eps1\_del\{k\}\_\{ss\}}] \ < \ [K,\ H_k,\ E\_\text{2del\{k\}\_p/m},\ E\_\text{del\{i\}\_del\{j\}\_pp/mm/pm/mp}]$$

### Central Elements

- $K$: even ($p=0$), central identity element. Identified with scalar 1 in all representations. Excluded from the PBW basis list but may appear in structure constants.
- $\kappa$: odd ($p=1$), nilpotent central element of the inhomogeneous extension. $\kappa^2 = 0$.

### Basis Sizes for $C(n+1)$

Dimension formula: even $= 2n^2 + n + 1$, odd $= 4n$.

| $n$ | Algebra | even | odd | total |
|---|---|---|---|---|
| 1 | $C(2) = \mathfrak{osp}(2\|2)$ | 4 | 4 | 8 |
| 2 | $C(3) = \mathfrak{osp}(2\|4)$ | 11 | 8 | 19 |
| 3 | $C(4) = \mathfrak{osp}(2\|6)$ | 22 | 12 | 34 |

#### $C(2)$, $n=1$

Even basis (4): `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`

Odd basis (4): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

#### $C(3)$, $n=2$

Even basis (11): `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`

Odd basis (8): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`

#### $C(4)$, $n=3$

Even basis (22): `H_1`, `H_2`, `H_3`, `H_4`; `E_2del1_p`, `E_2del2_p`, `E_2del3_p`; `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`; `E_2del1_m`, `E_2del2_m`, `E_2del3_m`; `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`; `E_del1_del2_pm`, `E_del1_del2_mp`, `E_del1_del3_pm`, `E_del1_del3_mp`, `E_del2_del3_pm`, `E_del2_del3_mp`

Odd basis (12): `E_eps1_del{k}_{pp,pm,mp,mm}` for $k = 1, 2, 3$.

### File Naming

Schema files use `C_{n}_{layer}.json` where `n` is the bosonic rank and `layer` is `structure`, `gamma`, `evaluated`, or `coboundary`.

Examples: `C_1_structure.json` (for $C(2)=\mathfrak{osp}(2|2)$), `C_2_structure.json`, `C_3_structure.json`.
