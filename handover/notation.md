# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Generator Labels for C(n+1)
- **Cartan generators**: `H_1, ..., H_{n+1}`
- **Even root generators (±2δ_k)**: `E_2del{k}_p` and `E_2del{k}_m`
- **Even root generators (±δ_k ± δ_l, k < l)**: `E_del{k}_del{l}_pp`, `E_del{k}_del{l}_pm`, `E_del{k}_del{l}_mp`, `E_del{k}_del{l}_mm`
- **Odd root generators (±ε ± δ_k)**: `E_eps_del{k}_pp`, `E_eps_del{k}_pm`, `E_eps_del{k}_mp`, `E_eps_del{k}_mm`

### 2. Basis Lists

#### C(2) (n=1)
- **Even (4)**: `H_1, H_2, E_2del1_p, E_2del1_m`
- **Odd (4)**: `E_eps_del1_pp, E_eps_del1_pm, E_eps_del1_mp, E_eps_del1_mm`

#### C(3) (n=2)
- **Even (11)**: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- **Odd (8)**: `E_eps_del1_pp, E_eps_del1_pm, E_eps_del1_mp, E_eps_del1_mm, E_eps_del2_pp, E_eps_del2_pm, E_eps_del2_mp, E_eps_del2_mm`

#### C(4) (n=3)
- **Even (22)**: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`
- **Odd (12)**: `E_eps_del1_pp, E_eps_del1_pm, E_eps_del1_mp, E_eps_del1_mm, E_eps_del2_pp, E_eps_del2_pm, E_eps_del2_mp, E_eps_del2_mm, E_eps_del3_pp, E_eps_del3_pm, E_eps_del3_mp, E_eps_del3_mm`

### 3. PBW Ordering
For C(n+1), we maintain the B(0,n) macro-ordering to preserve schema continuity.
- **Order**: `κ < [odd] < [even]`
- **Odd block internal order**: Ordered by index $k$ (1 to n), then by sign signatures (`pp, pm, mp, mm`).
- **Even block internal order**: Cartans `H_k`, then positive roots (2δ_k, then δ_k+δ_l), then negative roots (-2δ_k, then -δ_k-δ_l), then mixed roots (δ_k-δ_l, -δ_k+δ_l).
