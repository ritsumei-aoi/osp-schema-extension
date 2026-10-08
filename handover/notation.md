# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Even and Odd Basis for C(n+1)

The C(n+1) = osp(2|2n) superalgebra consists of even and odd generators. The basis elements for $n=1, 2, 3$ are defined as follows.

**C(2) (n=1)**
- **Even (4 elements)**: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- **Odd (4 elements)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

**C(3) (n=2)**
- **Even (11 elements)**: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_del1_del2_pm`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mp`, `E_del1_del2_mm`
- **Odd (8 elements)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`

**C(4) (n=3)**
- **Even (22 elements)**: `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_del1_del2_pm`, `E_del1_del3_pm`, `E_del2_del3_pm`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mp`, `E_del1_del3_mp`, `E_del2_del3_mp`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`
- **Odd (12 elements)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del3_pp`, `E_eps1_del3_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`, `E_eps1_del3_mp`, `E_eps1_del3_mm`

### 2. PBW Ordering

When ordering elements for the PBW basis, we must choose a consistent ordering between parity blocks and within them.

**Options considered:**
- **Option A**: `κ < [even] < [odd]` - Natural algebraic order starting with Cartan and even roots.
- **Option B**: `κ < [odd] < [even]` - Parity-based ordering that matches the legacy B(0,n) schema convention.

**Selected Ordering**: **Option B (`κ < [odd] < [even]`)**.
**Justification**: Choosing Option B maintains strict compatibility with the B(0,n) v5.0 JSON schema structure, reducing the amount of friction when adapting downstream tooling that expects odd elements to precede even elements in block matrix forms.

### 3. Generator Labels

The standard generator labels in JSON schemas follow this mapping to roots:

| Root | Generator label |
|---|---|
| $2\delta_k$ | `E_2del{k}_p` |
| $-2\delta_k$ | `E_2del{k}_m` |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` |
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` |
| Cartan $H_k$ | `H_{k}` |
