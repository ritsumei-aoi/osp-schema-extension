# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the C(n+1) schema extension project.

## Conventions

### 1. Root System and Generator Labels for C(n+1)

**Even Generators (Bosonic):**
- Cartan generators: `H_k` (for $k = 1 \dots n+1$)
- Positive roots $2\delta_k$: `E_2del{k}_p`
- Negative roots $-2\delta_k$: `E_2del{k}_m`
- Positive roots $\delta_i + \delta_j$ ($i<j$): `E_del{i}_del{j}_pp`
- Positive roots $\delta_i - \delta_j$ ($i<j$): `E_del{i}_del{j}_pm`
- Negative roots $-\delta_i + \delta_j$ ($i<j$): `E_del{i}_del{j}_mp`
- Negative roots $-\delta_i - \delta_j$ ($i<j$): `E_del{i}_del{j}_mm`

**Odd Generators (Fermionic - $\varepsilon$-roots):**
- Roots $\varepsilon + \delta_k$: `E_eps_del{k}_pp`
- Roots $\varepsilon - \delta_k$: `E_eps_del{k}_pm`
- Roots $-\varepsilon + \delta_k$: `E_eps_del{k}_mp`
- Roots $-\varepsilon - \delta_k$: `E_eps_del{k}_mm`

### 2. PBW Ordering

The chosen PBW ordering convention for C(n+1) follows a parity-separated structure compatible with the B(0,n) schema:
`κ < [odd] < [even]`
- The odd generators (`E_eps_del{k}_...`) are grouped together and ordered lexicographically by their labels.
- The even generators are grouped together: first Cartans (`H_k`), then the remaining even roots ordered lexicographically by their labels.

This maintains backward compatibility with the v5.0 JSON schema logic while accommodating the new $\varepsilon$-roots.

### 3. Even and Odd Basis Lists (n=1, 2, 3)

**C(2) / n=1:**
- Even (4): `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- Odd (4): `E_eps_del1_pp`, `E_eps_del1_pm`, `E_eps_del1_mp`, `E_eps_del1_mm`

**C(3) / n=2:**
- Even (11): `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del1_m`, `E_2del2_p`, `E_2del2_m`, `E_del1_del2_pp`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
- Odd (8): `E_eps_del1_pp`, `E_eps_del1_pm`, `E_eps_del1_mp`, `E_eps_del1_mm`, `E_eps_del2_pp`, `E_eps_del2_pm`, `E_eps_del2_mp`, `E_eps_del2_mm`

**C(4) / n=3:**
- Even (22): `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del1_m`, `E_2del2_p`, `E_2del2_m`, `E_2del3_p`, `E_2del3_m`, `E_del1_del2_pp`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`, `E_del1_del3_pp`, `E_del1_del3_mm`, `E_del1_del3_pm`, `E_del1_del3_mp`, `E_del2_del3_pp`, `E_del2_del3_mm`, `E_del2_del3_pm`, `E_del2_del3_mp`
- Odd (12): `E_eps_del1_pp`, `E_eps_del1_pm`, `E_eps_del1_mp`, `E_eps_del1_mm`, `E_eps_del2_pp`, `E_eps_del2_pm`, `E_eps_del2_mp`, `E_eps_del2_mm`, `E_eps_del3_pp`, `E_eps_del3_pm`, `E_eps_del3_mp`, `E_eps_del3_mm`
