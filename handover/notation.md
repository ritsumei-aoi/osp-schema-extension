# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository for $C(n+1) = \mathfrak{osp}(2|2n)$.

## 1. Oscillator Realization and Labels

- **Bosonic oscillators**: $b_j^+$, $b_j^-$ for $j = 1, \dots, n$.
  - JSON labels: `b_j_p`, `b_j_m`.
  - Parity: $p(b_j^\pm) = 0$.
  - Canonical commutation relations (CCR): $[b_j^-, b_k^+] = \delta_{jk}$, $[b_j^\pm, b_k^\pm] = 0$.
- **Fermionic oscillators**: Standard CAR pair $a_1^+$, $a_1^-$.
  - JSON labels: `a_1_p`, `a_1_m`.
  - Parity: $p(a_1^\pm) = 1$.
  - Canonical anticommutation relations (CAR): $\{a_1^-, a_1^+\} = 1$, $\{a_1^\pm, a_1^\pm\} = 0$.
- **Mixed relations**: $[b_j^\pm, a_1^\pm] = 0$ in the undeformed algebra.
- **Central elements**:
  - $\kappa$: odd central parameter ($p(\kappa) = 1$, $\kappa^2 = 0$).
  - $K$: even central identity ($p(K) = 0$).

## 2. Generator Definitions and Parity

### Even Generators ($p=0$, dimension $2n^2 + n + 1$)
- **Cartan generators**: $H_1, \dots, H_{n+1}$
  - $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$
  - $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $2 \leq k \leq n$
  - $H_{n+1} = b_n^+ b_n^- + \frac{1}{2}$
- **Long roots**:
  - $E_{2\delta_k}$: `E_2del{k}_p` = $(b_k^+)^2$
  - $E_{-2\delta_k}$: `E_2del{k}_m` = $(b_k^-)^2$
- **Short roots ($1 \leq i < j \leq n$)**:
  - $E_{\delta_i + \delta_j}$: `E_del{i}_del{j}_pp` = $b_i^+ b_j^+$
  - $E_{-(\delta_i + \delta_j)}$: `E_del{i}_del{j}_mm` = $b_i^- b_j^-$
  - $E_{\delta_i - \delta_j}$: `E_del{i}_del{j}_pm` = $b_i^+ b_j^-$
  - $E_{-(\delta_i - \delta_j)}$: `E_del{i}_del{j}_mp` = $b_i^- b_j^+$

### Odd Generators ($p=1$, dimension $4n$)
For $k = 1, \dots, n$:
- $E_{\varepsilon + \delta_k}$: `E_eps1_del{k}_pp` = $a_1^+ b_k^+$
- $E_{\varepsilon - \delta_k}$: `E_eps1_del{k}_pm` = $a_1^+ b_k^-$
- $E_{-\varepsilon + \delta_k}$: `E_eps1_del{k}_mp` = $a_1^- b_k^+$
- $E_{-\varepsilon - \delta_k}$: `E_eps1_del{k}_mm` = $a_1^- b_k^-$

## 3. PBW Ordering Convention

We adopt the graded PBW ordering convention extending the $B(0,n)$ schema:
$$ \kappa < [\text{Odd Generators}] < [\text{Even Generators}] $$

- **Odd sector ordering**:
  Grouped by $k = 1, \dots, n$, with internal sub-ordering `pp` < `pm` < `mp` < `mm`:
  `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, ..., `E_eps1_del{n}_mm`.
- **Even sector ordering**:
  `H_1`, ..., `H_{n+1}`, followed by positive long roots, positive short roots, negative long roots, negative short roots, mixed short roots:
  `H_1, ..., H_{n+1}`, `E_2del1_p, ..., E_2del{n}_p`, `E_del{i}_del{j}_pp`, `E_2del1_m, ..., E_2del{n}_m`, `E_del{i}_del{j}_mm`, `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`.

## 4. Concrete Basis Lists for C(2), C(3), C(4)

### C(2) = osp(2|2) ($n=1$)
- **Even Basis (4)**: `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- **Odd Basis (4)**: `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`
- **Total Dimension**: 8

### C(3) = osp(2|4) ($n=2$)
- **Even Basis (11)**: `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd Basis (8)**: `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`
- **Total Dimension**: 19

### C(4) = osp(2|6) ($n=3$)
- **Even Basis (22)**:
  `["H_1", "H_2", "H_3", "H_4", "E_2del1_p", "E_2del2_p", "E_2del3_p", "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp", "E_2del1_m", "E_2del2_m", "E_2del3_m", "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm", "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm", "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"]`
- **Odd Basis (12)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm", "E_eps1_del3_pp", "E_eps1_del3_pm", "E_eps1_del3_mp", "E_eps1_del3_mm"]`
- **Total Dimension**: 34
