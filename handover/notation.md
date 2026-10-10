# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### C(n+1) Generator Labels

- **Even Generators**:
  - Cartans: `H_{k}` for $k = 1, \dots, n+1$.
  - Long roots: `E_2del{k}_p` and `E_2del{k}_m` for $2\delta_k$ and $-2\delta_k$.
  - Short roots ($i < j$): `E_del{i}_del{j}_pp`, `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`, `E_del{i}_del{j}_mm` for $\pm\delta_i \pm\delta_j$.
- **Odd Generators**:
  - `E_eps1_del{k}_pp` for $\varepsilon + \delta_k$.
  - `E_eps1_del{k}_pm` for $\varepsilon - \delta_k$.
  - `E_eps1_del{k}_mp` for $-\varepsilon + \delta_k$.
  - `E_eps1_del{k}_mm` for $-\varepsilon - \delta_k$.

### Basis lists for n=1, 2, 3
- **n=1 (C(2))**:
  - Even (4): `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`.
  - Odd (4): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`.
- **n=2 (C(3))**:
  - Even (11): `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`.
  - Odd (8): `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`.
- **n=3 (C(4))**:
  - Even (22): `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del3_pm`, `E_del2_del3_pm`, `E_del1_del2_mp`, `E_del1_del3_mp`, `E_del2_del3_mp`.
  - Odd (12): `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del3_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del3_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del3_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`, `E_eps1_del3_mm`.

### PBW Ordering
- **Ordering Strategy**: Consistent with B(0,n) conventions, we use `κ < [odd] < [even]`.
- **Reasoning**: This ordering places the nilpotent element first and odd elements before even ones, maintaining compatibility with the pre-existing structure constant evaluators used for B(0,n) which anticipate this general graded sequence.
- **Detailed Ordering**:
  `κ < E_eps1_del{k}_{signs} (ordered by signs: pp, pm, mp, mm, then by k) < H_k < E_2del{k}_p < E_del{i}_del{j}_pp < E_2del{k}_m < E_del{i}_del{j}_mm < E_del{i}_del{j}_pm < E_del{i}_del{j}_mp`
