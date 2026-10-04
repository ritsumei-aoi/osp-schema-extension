# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Generator Labels

1. **Cartan Generators**: `H_{k}` for $k=1, \ldots, n+1$.
2. **Even Root Generators**: 
   - `E_2del{k}_p` and `E_2del{k}_m` for $\pm 2\delta_k$.
   - `E_del{i}_del{j}_pp`, `E_del{i}_del{j}_mm`, `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp` for $\pm\delta_i \pm\delta_j$ ($i < j$).
3. **Odd Root Generators**:
   - `E_eps1_del{k}_pp` for $\varepsilon + \delta_k$.
   - `E_eps1_del{k}_pm` for $\varepsilon - \delta_k$.
   - `E_eps1_del{k}_mp` for $-\varepsilon + \delta_k$.
   - `E_eps1_del{k}_mm` for $-\varepsilon - \delta_k$.
4. **Oscillators**:
   - Fermions: `a_1_p`, `a_1_m`.
   - Bosons: `b_{k}_p`, `b_{k}_m` for $k=1, \ldots, n$.

### PBW Ordering

To maintain consistency with the existing B(0,n) schema, we group by parity:
`κ < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]`
Within the odd and even blocks, we order lexicographically by the generator labels.
