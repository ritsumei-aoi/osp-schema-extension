# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository for $C(n+1) = \mathfrak{osp}(2|2n)$.
It is initialized and populated during the $C(n+1)$ schema extension project.

## 1. Algebra Definition

$C(n+1) = \mathfrak{osp}(2|2n)$ is a Lie superalgebra of bosonic rank $n$ (total rank $n+1$).
- **Even subalgebra**: $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$, dimension $2n^2 + n + 1$.
- **Odd subspace**: dimension $4n$.
- **Total dimension**: $2n^2 + 5n + 1$.

## 2. Oscillator Realization

- **Fermionic oscillators**: Standard pair $a_1^+, a_1^-$ satisfying CAR $\{a_1^-, a_1^+\} = 1$ (labels: `a_1_p`, `a_1_m`).
- **Bosonic oscillators**: $b_k^+, b_k^-$ ($k = 1, \ldots, n$) satisfying CCR $[b_k^-, b_l^+] = \delta_{kl}$ (labels: `b_k_p`, `b_k_m`).
- **Central element**: $\kappa$ (parity 1, nilpotent $\kappa^2=0$, label: `kappa`).

## 3. Basis and Root Generators

### Even Generators ($2n^2 + n + 1$ total)
1. **Cartan generators** ($n+1$ total):
   - $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$ (label: `H_1`)
   - $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $2 \leq k \leq n$ (labels: `H_2`, ..., `H_n`)
   - $H_{n+1} = -b_n^+ b_n^- - \frac{1}{2}$ (label: `H_{n+1}`)
2. **Roots of $\mathfrak{sp}(2n)$** ($2n^2$ total):
   - $2\delta_k$: `E_2del{k}_p` = $(b_k^+)^2$
   - $-2\delta_k$: `E_2del{k}_m` = $(b_k^-)^2$
   - $\delta_i + \delta_j$ ($i < j$): `E_del{i}_del{j}_pp` = $b_i^+ b_j^+$
   - $-\delta_i - \delta_j$ ($i < j$): `E_del{i}_del{j}_mm` = $b_i^- b_j^-$
   - $\delta_i - \delta_j$ ($i < j$): `E_del{i}_del{j}_pm` = $b_i^+ b_j^-$
   - $-\delta_i + \delta_j$ ($i < j$): `E_del{i}_del{j}_mp` = $b_i^- b_j^+$

### Odd Generators ($4n$ total)
- $\varepsilon + \delta_k$: `E_eps1_del{k}_pp` = $a_1^+ b_k^+$
- $\varepsilon - \delta_k$: `E_eps1_del{k}_pm` = $a_1^+ b_k^-$
- $-\varepsilon + \delta_k$: `E_eps1_del{k}_mp` = $a_1^- b_k^+$
- $-\varepsilon - \delta_k$: `E_eps1_del{k}_mm` = $a_1^- b_k^-$

## 4. PBW Ordering Convention

The canonical PBW ordering for $C(n+1)$ is:
$$\kappa < [\text{odd generators}] < [\text{even generators}]$$

- **Odd sub-ordering**: Grouped by $k=1, \dots, n$, with internal order `pp` < `pm` < `mp` < `mm`.
- **Even sub-ordering**: Cartans $H_1, \dots, H_{n+1}$, followed by positive $2\delta_k$ roots, positive $\delta_i+\delta_j$ roots, negative $2\delta_k$ roots, negative $\delta_i+\delta_j$ roots, and $\delta_i-\delta_j$ / $-\delta_i+\delta_j$ roots.

## 5. Basis Lists for $n=1, 2, 3$

### C(2) = osp(2|2) ($n=1$)
- **Even (4)**: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- **Odd (4)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

### C(3) = osp(2|4) ($n=2$)
- **Even (11)**: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
- **Odd (8)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`

### C(4) = osp(2|6) ($n=3$)
- **Even (22)**: `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`, `E_del1_del3_pm`, `E_del1_del3_mp`, `E_del2_del3_pm`, `E_del2_del3_mp`
- **Odd (12)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`, `E_eps1_del3_pp`, `E_eps1_del3_pm`, `E_eps1_del3_mp`, `E_eps1_del3_mm`
