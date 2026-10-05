# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Generator Labels for C(n+1) = osp(2|2n)
The generators for C(n+1) are labeled to align with the schema specifications:

**Cartan Generators**:
- `H_k` for $k = 1, \dots, n+1$.

**Even Root Generators**:
- `E_2del{k}_p` = $(b_k^+)^2$ for $2\delta_k$
- `E_2del{k}_m` = $(b_k^-)^2$ for $-2\delta_k$
- `E_del{i}_del{j}_pp` = $b_i^+ b_j^+$ for $\delta_i + \delta_j$ ($i < j$)
- `E_del{i}_del{j}_pm` = $b_i^+ b_j^-$ for $\delta_i - \delta_j$ ($i < j$)
- `E_del{i}_del{j}_mp` = $b_i^- b_j^+$ for $-\delta_i + \delta_j$ ($i < j$)
- `E_del{i}_del{j}_mm` = $b_i^- b_j^-$ for $-\delta_i - \delta_j$ ($i < j$)

**Odd Root Generators**:
- `E_eps1_del{k}_pp` = $a_1^+ b_k^+$ for $\varepsilon + \delta_k$
- `E_eps1_del{k}_pm` = $a_1^+ b_k^-$ for $\varepsilon - \delta_k$
- `E_eps1_del{k}_mp` = $a_1^- b_k^+$ for $-\varepsilon + \delta_k$
- `E_eps1_del{k}_mm` = $a_1^- b_k^-$ for $-\varepsilon - \delta_k$

### 2. PBW Ordering
For the basis of C(n+1), the chosen PBW ordering convention is:
**Option A: Graded Lexicographical Order ($\varepsilon$ precedes $\delta$)**
$\varepsilon \succ \delta_1 \succ \dots \succ \delta_n$

This places the odd generators associated with $\varepsilon$ before the bosonic ones. This aligns with standard $osp(2|2n)$ supermatrix conventions where the $(1|0)$ fermionic block appears first. The ordering in the schema will be:
`κ < [odd generators] < [even generators]`

### 3. Even and Odd Basis Lists

#### C(2) = osp(2|2) [n=1]
**Even Basis (4)**: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
**Odd Basis (4)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

#### C(3) = osp(2|4) [n=2]
**Even Basis (11)**: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
**Odd Basis (8)**: `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`

#### C(4) = osp(2|6) [n=3]
**Even Basis (22)**: `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del3_pm`, `E_del2_del3_pm`, `E_del1_del2_mp`, `E_del1_del3_mp`, `E_del2_del3_mp`
**Odd Basis (12)**: `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del3_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del3_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del3_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`, `E_eps1_del3_mm`
