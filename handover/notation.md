# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Oscillator Generator Labels
* **Fermions**: `a_1_p` for $a_1^+$, `a_1_m` for $a_1^-$
* **Bosons**: `b_k_p` for $b_k^+$, `b_k_m` for $b_k^-$ (where $k = 1, \dots, n$)

### 2. Root Generator Labels
* **Cartan generators**: `H_k` (for $k = 1, \dots, n+1$)
* **Even positive/negative roots**: 
  * `E_2del{k}_p` and `E_2del{k}_m` for $\pm 2\delta_k$
  * `E_del{i}_del{j}_pp`, `E_del{i}_del{j}_mm` for $\pm(\delta_i + \delta_j)$
  * `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp` for $\pm(\delta_i - \delta_j)$
* **Odd roots**: 
  * `E_eps1_del{k}_pp` for $\varepsilon + \delta_k$
  * `E_eps1_del{k}_pm` for $\varepsilon - \delta_k$
  * `E_eps1_del{k}_mp` for $-\varepsilon + \delta_k$
  * `E_eps1_del{k}_mm` for $-\varepsilon - \delta_k$

### 3. C(n+1) Basis Lists

**C(2) (n=1)**
* **Even** (4): `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
* **Odd** (4): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

**C(3) (n=2)**
* **Even** (11): `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_pp`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
* **Odd** (8): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`

**C(4) (n=3)**
* **Even** (22): `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del3_pm`, `E_del2_del3_pm`, `E_del1_del2_mp`, `E_del1_del3_mp`, `E_del2_del3_mp`
* **Odd** (12): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`, `E_eps1_del3_pp`, `E_eps1_del3_pm`, `E_eps1_del3_mp`, `E_eps1_del3_mm`

### 4. PBW Ordering
* **Selected Option**: Parity-split ordering (`[odd] < [even]`).
* **Reasoning**: This ordering maintains structural consistency with the $B(0,n)$ schema (which used `κ < [odd] < [even]`). By keeping odd generators together and even generators together, we simplify graded commutator logic and parity tracking in downstream schema processors.
