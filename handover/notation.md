# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Generator Labels
- Cartans: `H_k` for $k=1, \ldots, n+1$.
- Even generators ($\Delta_{\bar{0}}$):
  - `E_2del{k}_p` for $E_{2\delta_k} = (b_k^+)^2$
  - `E_2del{k}_m` for $E_{-2\delta_k} = (b_k^-)^2$
  - `E_del{i}_del{j}_pp` for $E_{\delta_i + \delta_j} = b_i^+ b_j^+$ ($i < j$)
  - `E_del{i}_del{j}_pm` for $E_{\delta_i - \delta_j} = b_i^+ b_j^-$ ($i < j$)
  - `E_del{i}_del{j}_mp` for $E_{-\delta_i + \delta_j} = b_i^- b_j^+$ ($i < j$)
  - `E_del{i}_del{j}_mm` for $E_{-\delta_i - \delta_j} = b_i^- b_j^-$ ($i < j$)
- Odd generators ($\Delta_{\bar{1}}$):
  - `E_eps1_del{k}_pp` for $E_{\varepsilon + \delta_k} = a_1^+ b_k^+$
  - `E_eps1_del{k}_pm` for $E_{\varepsilon - \delta_k} = a_1^+ b_k^-$
  - `E_eps1_del{k}_mp` for $E_{-\varepsilon + \delta_k} = a_1^- b_k^+$
  - `E_eps1_del{k}_mm` for $E_{-\varepsilon - \delta_k} = a_1^- b_k^-$

### 2. PBW Ordering
We define the PBW ordering as: $\kappa < [\text{odd}] < [\text{even}]$.
Within the odd and even groups, we group by sign (creation/annihilation) of the first root index, then by the second, and order lexicographically by indices.

- **Odd Ordering:**
  1. `E_eps1_del{k}_pp` ($k=1 \ldots n$)
  2. `E_eps1_del{k}_pm` ($k=1 \ldots n$)
  3. `E_eps1_del{k}_mp` ($k=1 \ldots n$)
  4. `E_eps1_del{k}_mm` ($k=1 \ldots n$)
- **Even Ordering:**
  1. Cartans `H_k` ($k=1 \ldots n+1$)
  2. `E_2del{k}_p` ($k=1 \ldots n$)
  3. `E_del{i}_del{j}_pp` ($i < j$)
  4. `E_2del{k}_m` ($k=1 \ldots n$)
  5. `E_del{i}_del{j}_mm` ($i < j$)
  6. `E_del{i}_del{j}_pm` ($i < j$)
  7. `E_del{i}_del{j}_mp` ($i < j$)

### 3. Basis for C(n+1)

**For C(2) (n=1):**
- Even (4): `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- Odd (4): `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

**For C(3) (n=2):**
- Even (11): `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
- Odd (8): `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`

**For C(4) (n=3):**
- Even (22): `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del3_pm`, `E_del2_del3_pm`, `E_del1_del2_mp`, `E_del1_del3_mp`, `E_del2_del3_mp`
- Odd (12): `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del3_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del3_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del3_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`, `E_eps1_del3_mm`
