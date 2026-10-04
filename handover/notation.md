# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Lie Superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$
- Rank: Bosonic rank $n$, fermionic rank $m=1$. Total rank $n+1$.
- Dimension formula: Even $\dim(\mathfrak{g}_{\bar{0}}) = 2n^2 + n + 1$, Odd $\dim(\mathfrak{g}_{\bar{1}}) = 4n$, Total dimension $= 2n^2 + 5n + 1$.
  - For $n=1$ ($C(2) = \mathfrak{osp}(2|2)$): Even = 4, Odd = 4, Total = 8.
  - For $n=2$ ($C(3) = \mathfrak{osp}(2|4)$): Even = 11, Odd = 8, Total = 19.
  - For $n=3$ ($C(4) = \mathfrak{osp}(2|6)$): Even = 22, Odd = 12, Total = 34.

### 2. Oscillator Realization
- **Fermionic oscillators**: Standard CAR pair $a_1^+, a_1^-$ with parity $p=1$.
  - Anticommutators: $\{a_1^-, a_1^+\} = 1$, $\{a_1^+, a_1^+\} = 0$, $\{a_1^-, a_1^-\} = 0$.
  - JSON labels: `"a_1_p"`, `"a_1_m"`.
- **Bosonic oscillators**: $b_k^+, b_k^-$ ($k = 1, \ldots, n$) with parity $p=0$.
  - Commutators: $[b_j^-, b_k^+] = \delta_{jk}$, $[b_j^\pm, b_k^\pm] = 0$.
  - JSON labels: `"b_{k}_p"`, `"b_{k}_m"`.
- **Central elements**:
  - `kappa` ($\kappa$): Nilpotent odd central element, $p(\kappa)=1$, $\kappa^2 = 0$.
  - `K`: Even central element, $p(K)=0$, identified with scalar 1.

### 3. Generator Labels and Realizations
#### Cartan Generators ($H_1, \ldots, H_{n+1}$, parity 0)
- $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$
- $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $2 \leq k \leq n$
- $H_{n+1} = -b_n^+ b_n^- - \frac{1}{2}$

#### Even Root Generators (parity 0)
- Long roots ($k = 1, \ldots, n$):
  - `E_2del{k}_p` $= (b_k^+)^2$ ($+2\delta_k$)
  - `E_2del{k}_m` $= (b_k^-)^2$ ($-2\delta_k$)
- Cross roots ($1 \leq i < j \leq n$):
  - `E_del{i}_del{j}_pp` $= b_i^+ b_j^+$ ($\delta_i + \delta_j$)
  - `E_del{i}_del{j}_mm` $= b_i^- b_j^-$ ($-\delta_i - \delta_j$)
  - `E_del{i}_del{j}_pm` $= b_i^+ b_j^-$ ($\delta_i - \delta_j$)
  - `E_del{i}_del{j}_mp` $= b_i^- b_j^+$ ($-\delta_i + \delta_j$)

#### Odd Root Generators (parity 1, $k = 1, \ldots, n$)
- `E_eps1_del{k}_pp` $= a_1^+ b_k^+$ ($\varepsilon + \delta_k$)
- `E_eps1_del{k}_pm` $= a_1^+ b_k^-$ ($\varepsilon - \delta_k$)
- `E_eps1_del{k}_mp` $= a_1^- b_k^+$ ($-\varepsilon + \delta_k$)
- `E_eps1_del{k}_mm` $= a_1^- b_k^-$ ($-\varepsilon - \delta_k$)

### 4. PBW Ordering Convention
The PBW ordering is chosen according to **Option 1 (Root-Type Block Ordering)**, extending the $B(0,n)$ convention:
$$\kappa < [\text{odd}] < [\text{even}]$$
where:
1. Odd generators are partitioned into sign-type blocks:
   - `pp` block: `E_eps1_del1_pp, ..., E_eps1_deln_pp`
   - `pm` block: `E_eps1_del1_pm, ..., E_eps1_deln_pm`
   - `mp` block: `E_eps1_del1_mp, ..., E_eps1_deln_mp`
   - `mm` block: `E_eps1_del1_mm, ..., E_eps1_deln_mm`
2. Even generators are ordered as:
   - Cartan block: `H_1, ..., H_{n+1}`
   - Positive long roots: `E_2del1_p, ..., E_2deln_p`
   - Positive cross roots: `E_del{i}_del{j}_pp` ($1 \leq i < j \leq n$)
   - Negative long roots: `E_2del1_m, ..., E_2deln_m`
   - Negative cross roots: `E_del{i}_del{j}_mm` ($1 \leq i < j \leq n$)
   - Mixed cross roots: `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp` ($1 \leq i < j \leq n$)

### 5. Explicit Basis Lists for $n = 1, 2, 3$

#### $n = 1$ ($C(2) = \mathfrak{osp}(2|2)$)
- **Even (4)**:
  `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- **Odd (4)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`

#### $n = 2$ ($C(3) = \mathfrak{osp}(2|4)$)
- **Even (11)**:
  `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd (8)**:
  `["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del1_mm", "E_eps1_del2_mm"]`

#### $n = 3$ ($C(4) = \mathfrak{osp}(2|6)$)
- **Even (22)**:
  `["H_1", "H_2", "H_3", "H_4", "E_2del1_p", "E_2del2_p", "E_2del3_p", "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp", "E_2del1_m", "E_2del2_m", "E_2del3_m", "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm", "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm", "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"]`
- **Odd (12)**:
  `["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp", "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm", "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp", "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"]`
