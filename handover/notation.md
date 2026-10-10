# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Generator Labels for C(n+1)
Following the Frappat et al. notation, the generators for $C(n+1) = \mathfrak{osp}(2|2n)$ are labeled as follows in our schema:

**Even Generators:**
- Cartan subalgebra: `H_k` for $k = 1, \dots, n+1$.
- Roots $\pm 2\delta_k$: `E_2del{k}_p` and `E_2del{k}_m`.
- Roots $\pm(\delta_i \pm \delta_j)$ ($i < j$): `E_del{i}_del{j}_pp`, `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`, `E_del{i}_del{j}_mm`.

**Odd Generators ($\varepsilon$-roots):**
- Roots $\pm\varepsilon \pm \delta_k$: `E_eps_del{k}_pp` ($+\varepsilon+\delta_k$), `E_eps_del{k}_pm` ($+\varepsilon-\delta_k$), `E_eps_del{k}_mp` ($-\varepsilon+\delta_k$), `E_eps_del{k}_mm` ($-\varepsilon-\delta_k$).

### 2. PBW Ordering
For $C(n+1)$, we maintain the convention established in $B(0,n)$:
**PBW Ordering**: `κ < [odd] < [even]`

Within the `[odd]` sector, generators are ordered lexicographically by the $\delta$ index and then by sign pattern (pp, pm, mp, mm):
`E_eps_del1_pp, E_eps_del1_pm, E_eps_del1_mp, E_eps_del1_mm, E_eps_del2_pp, ...`

Within the `[even]` sector, generators are ordered as:
Cartan (`H_k`), then pure $\delta_k$ roots (`E_2del{k}_p`, `E_2del{k}_m`), then mixed $\delta$ roots (`E_del{i}_del{j}_...`).

### 3. Even and Odd Basis Lists

**C(2) / n=1**:
- **Odd**: `E_eps_del1_pp`, `E_eps_del1_pm`, `E_eps_del1_mp`, `E_eps_del1_mm`
- **Even**: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`

**C(3) / n=2**:
- **Odd**: `E_eps_del1_pp`, `E_eps_del1_pm`, `E_eps_del1_mp`, `E_eps_del1_mm`, `E_eps_del2_pp`, `E_eps_del2_pm`, `E_eps_del2_mp`, `E_eps_del2_mm`
- **Even**: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_pp`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`

**C(4) / n=3**:
- **Odd**: `E_eps_del1_pp`..`E_eps_del1_mm`, `E_eps_del2_pp`..`E_eps_del2_mm`, `E_eps_del3_pp`..`E_eps_del3_mm`
- **Even**: `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del3_pm`, `E_del2_del3_pm`, `E_del1_del2_mp`, `E_del1_del3_mp`, `E_del2_del3_mp`
