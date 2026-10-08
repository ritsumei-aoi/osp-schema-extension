# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

## 1. Oscillator Generators
- **Fermionic**: `a_1_p`, `a_1_m` (Standard CAR pair)
- **Bosonic**: `b_k_p`, `b_k_m` for $k=1 \dots n$

## 2. Generator Labels
- **Cartans**: `H_k` ($k=1 \dots n+1$)
- **Even Roots**: 
  - $\pm 2\delta_k$: `E_2del{k}_p`, `E_2del{k}_m`
  - $\pm \delta_i \pm \delta_j$: `E_del{i}_del{j}_pp`, `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`, `E_del{i}_del{j}_mm` (where $i < j$)
- **Odd Roots**:
  - $\pm \varepsilon \pm \delta_k$: `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm`

## 3. PBW Ordering
Consistent with the base B(0,n) schema, we use the `[odd] < [even]` ordering convention:
`[Odd Roots] < [Cartans] < [Even Roots]`
Within each group, generators are ordered lexicographically by their index $k$ (or pairs $i, j$) and then by sign combinations (`pp` < `pm` < `mp` < `mm`, `p` < `m`).
