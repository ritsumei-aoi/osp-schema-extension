# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension project.

## 1. Oscillator Generators and Parity

- **Standard Fermionic Pair**: $a_1^+, a_1^-$ (labels: `a_1_p`, `a_1_m`), parity $p(a_1^\pm) = 1$. CAR relation: $\{a_1^-, a_1^+\} = 1$.
- **Bosonic Oscillators**: $b_k^+, b_k^-$ ($k = 1, \ldots, n$, labels: `b_k_p`, `b_k_m`), parity $p(b_k^\pm) = 0$. CCR relation: $[b_j^-, b_k^+] = \delta_{jk}$.
- **Central Elements**: 
  - $\kappa$ (label: `kappa`): odd central element ($p(\kappa) = 1$, $\kappa^2 = 0$).
  - $K$ (label: `K`): even central element ($p(K) = 0$, central scalar unit).

## 2. Generator Label Conventions and Realizations

### Even Generators ($\dim \mathfrak{g}_{\bar{0}} = 2n^2 + n + 1$)
- **Cartan Generators** ($n+1$ elements): `H_1`, `H_2`, ..., `H_{n+1}`
  - $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$
  - $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ ($2 \le k \le n$)
  - $H_{n+1} = -b_n^+ b_n^- - \frac{1}{2}$
- **Bosonic Root Vectors** ($2n^2$ elements):
  - $2\delta_k$ ($1 \le k \le n$): `E_2del{k}_p` = $(b_k^+)^2$
  - $-2\delta_k$ ($1 \le k \le n$): `E_2del{k}_m` = $(b_k^-)^2$
  - $\delta_i + \delta_j$ ($1 \le i < j \le n$): `E_del{i}_del{j}_pp` = $b_i^+ b_j^+$
  - $-\delta_i - \delta_j$ ($1 \le i < j \le n$): `E_del{i}_del{j}_mm` = $b_i^- b_j^-$
  - $\delta_i - \delta_j$ ($1 \le i < j \le n$): `E_del{i}_del{j}_pm` = $b_i^+ b_j^-$
  - $-\delta_i + \delta_j$ ($1 \le i < j \le n$): `E_del{i}_del{j}_mp` = $b_i^- b_j^+$

### Odd Generators ($\dim \mathfrak{g}_{\bar{1}} = 4n$)
- $+\varepsilon + \delta_k$ ($1 \le k \le n$): `E_eps1_del{k}_pp` = $a_1^+ b_k^+$
- $+\varepsilon - \delta_k$ ($1 \le k \le n$): `E_eps1_del{k}_pm` = $a_1^+ b_k^-$
- $-\varepsilon + \delta_k$ ($1 \le k \le n$): `E_eps1_del{k}_mp` = $a_1^- b_k^+$
- $-\varepsilon - \delta_k$ ($1 \le k \le n$): `E_eps1_del{k}_mm` = $a_1^- b_k^-$

## 3. PBW Ordering Convention

The overall PBW ordering convention is:
$$\kappa < [\text{odd generators}] < [\text{even generators}]$$

### Consideration of Ordering Options:
- **Option A (Lexicographical Sorting)**: Sorting generator labels alphabetically. While simple, it splits Cartan elements from root vectors and destroys the mathematical structure of the root system.
- **Option B (Root-based / Extension of $B(0,n)$ v5.0)**: Grouping generators mathematically:
  - `odd`: Ordered by index $k=1,\ldots,n$, then by signs `pp`, `pm`, `mp`, `mm`.
  - `even`: Cartan generators (`H_1` ... `H_{n+1}`), followed by positive $2\delta$ roots, positive mixed $\delta$ roots, negative $2\delta$ roots, negative mixed $\delta$ roots, and mixed-sign $\delta$ roots.

**Decision**: Option B is selected as it directly extends the $B(0,n)$ v5.0 schema convention while preserving root system properties.

## 4. Basis Lists for $n=1, 2, 3$

### $n=1$ ($C(2) = \mathfrak{osp}(2|2)$, Even: 4, Odd: 4, Total: 8)
- `even`: `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- `odd`: `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`

### $n=2$ ($C(3) = \mathfrak{osp}(2|4)$, Even: 11, Odd: 8, Total: 19)
- `even`: `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- `odd`: `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`

### $n=3$ ($C(4) = \mathfrak{osp}(2|6)$, Even: 22, Odd: 12, Total: 34)
- `even`: `["H_1", "H_2", "H_3", "H_4", "E_2del1_p", "E_2del2_p", "E_2del3_p", "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp", "E_2del1_m", "E_2del2_m", "E_2del3_m", "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm", "E_del1_del2_pm", "E_del1_del2_mp", "E_del1_del3_pm", "E_del1_del3_mp", "E_del2_del3_pm", "E_del2_del3_mp"]`
- `odd`: `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm", "E_eps1_del3_pp", "E_eps1_del3_pm", "E_eps1_del3_mp", "E_eps1_del3_mm"]`
