# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## 1. Oscillator Realization for $C(n+1) = \mathfrak{osp}(2|2n)$

### Oscillators
- **Fermionic**: $a_1^+, a_1^-$ with $\{a_1^-, a_1^+\} = 1$. Labelled as `a_1_p`, `a_1_m`.
- **Bosonic**: $b_k^+, b_k^-$ with $[b_k^-, b_l^+] = \delta_{kl}$ for $k=1 \dots n$. Labelled as `b_k_p`, `b_k_m`.

### Cartan Generators ($H_k$)
- $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$ (Label: `H_1`)
- $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $k=2 \dots n$ (Label: `H_k`)
- $H_{n+1} = -b_n^+ b_n^- - 1/2$ (Label: `H_{n+1}`)

### Root Generators
- **Even Roots**:
  - $E_{2\delta_k} = (b_k^+)^2$ (Label: `E_2delk_p`)
  - $E_{-2\delta_k} = (b_k^-)^2$ (Label: `E_2delk_m`)
  - $E_{\delta_i + \delta_j} = b_i^+ b_j^+$ (Label: `E_del{i}_del{j}_pp`)
  - $E_{-\delta_i - \delta_j} = b_i^- b_j^-$ (Label: `E_del{i}_del{j}_mm`)
  - $E_{\delta_i - \delta_j} = b_i^+ b_j^-$ (Label: `E_del{i}_del{j}_pm`)
  - $E_{-\delta_i + \delta_j} = b_i^- b_j^+$ (Label: `E_del{i}_del{j}_mp`)
- **Odd Roots**:
  - $E_{\varepsilon + \delta_k} = a_1^+ b_k^+$ (Label: `E_eps1_delk_pp`)
  - $E_{\varepsilon - \delta_k} = a_1^+ b_k^-$ (Label: `E_eps1_delk_pm`)
  - $E_{-\varepsilon + \delta_k} = a_1^- b_k^+$ (Label: `E_eps1_delk_mp`)
  - $E_{-\varepsilon - \delta_k} = a_1^- b_k^-$ (Label: `E_eps1_delk_mm`)

## 2. PBW Ordering (Option A: Parity-based)

The ordering follows:
$$\kappa < [\text{Odd Roots}] < [\text{Even Cartan}] < [\text{Even Roots}]$$

**Internal Sort Rules**:
1. **Odd Roots**: Sorted by $\varepsilon$-index sign ($+ > -$), then by $\delta$-index sign ($+ > -$), then by $\delta$ index $k$ ($1 < 2 < \dots < n$).
   - Sequence: $E_{\varepsilon+\delta_1}, \dots, E_{\varepsilon+\delta_n}, E_{\varepsilon-\delta_1}, \dots, E_{\varepsilon-\delta_n}, E_{-\varepsilon+\delta_1}, \dots, E_{-\varepsilon+\delta_n}, E_{-\varepsilon-\delta_1}, \dots, E_{-\varepsilon-\delta_n}$.
2. **Even Cartan**: $H_1, H_2, \dots, H_{n+1}$.
3. **Even Roots**: Positive roots $\to$ Negative roots $\to$ Mixed roots, sorted lexicographically by labels.

## 3. Basis Lists for $n=1, 2, 3$

### $C(2)$ ($n=1$)
- **Even**: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- **Odd**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

### $C(3)$ ($n=2$)
- **Even**: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
- **Odd**: `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`

### $C(4)$ ($n=3$)
- **Even**: `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del3_pm`, `E_del2_del3_pm`, `E_del1_del2_mp`, `E_del1_del3_mp`, `E_del2_del3_mp`
- **Odd**: `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del3_pp`, `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del3_pm`, `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del3_mp`, `E_eps1_del1_mm`, `E_eps1_del2_mm`, `E_eps1_del3_mm`
