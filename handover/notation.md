# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## 1. Lie Superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$

### 1.1 Superdimension and Parity
- **Family**: $C(n+1) = \mathfrak{osp}(2|2n)$ with $m=1$ and bosonic rank $n \ge 1$.
- **Even subalgebra**: $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$ of dimension $2n^2 + n + 1$.
- **Odd subspace**: Superdimension $4n$.
- **Total dimension**: $(2n^2 + n + 1) \mid 4n$, total $2n^2 + 5n + 1$.

| Rank | Algebra | Even Dim | Odd Dim | Total Dim |
|---|---|---|---|---|
| $n=1$ | $C(2) = \mathfrak{osp}(2|2)$ | 4 | 4 | 8 |
| $n=2$ | $C(3) = \mathfrak{osp}(2|4)$ | 11 | 8 | 19 |
| $n=3$ | $C(4) = \mathfrak{osp}(2|6)$ | 22 | 12 | 34 |

---

## 2. Oscillator Realization and Labels

### 2.1 Oscillator Generators
- **Fermionic pair**: $a_1^+, a_1^-$ (labels: `a_1_p`, `a_1_m`), parity $p=1$.
  - CAR: $\{a_1^-, a_1^+\} = 1$, $\{a_1^+, a_1^+\} = 0$, $\{a_1^-, a_1^-\} = 0$.
- **Bosonic oscillators**: $b_k^+, b_k^-$ ($k = 1, \dots, n$, labels: `b_k_p`, `b_k_m`), parity $p=0$.
  - CCR: $[b_j^-, b_k^+] = \delta_{jk}$, $[b_j^\pm, b_k^\pm] = 0$.
- **Central elements**:
  - $K$: Even central element, normalized to $K=1$ as scalar identity.
  - $\kappa$: Odd nilpotent central extension parameter, $p(\kappa)=1$, $\kappa^2 = 0$.

### 2.2 Generator Naming Convention

#### Cartan Generators ($n+1$ elements, even, parity 0)
- $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$
- $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $2 \le k \le n$
- $H_{n+1} = -b_n^+ b_n^- - \tfrac{1}{2}$

#### Even Root Generators ($2n^2$ elements, parity 0)
- Long roots $\pm 2\delta_k$ ($2n$ elements):
  - `E_2del{k}_p` = $(b_k^+)^2$
  - `E_2del{k}_m` = $(b_k^-)^2$
- Short even roots $\pm \delta_i \pm \delta_j$ with $1 \le i < j \le n$ ($2n(n-1)$ elements):
  - `E_del{i}_del{j}_pp` = $b_i^+ b_j^+$
  - `E_del{i}_del{j}_mm` = $b_i^- b_j^-$
  - `E_del{i}_del{j}_pm` = $b_i^+ b_j^-$
  - `E_del{i}_del{j}_mp` = $b_i^- b_j^+$

#### Odd Root Generators ($4n$ elements, parity 1)
- For each $k \in \{1, \dots, n\}$:
  - `E_eps1_del{k}_pp` = $a_1^+ b_k^+$ (root $\varepsilon + \delta_k$)
  - `E_eps1_del{k}_pm` = $a_1^+ b_k^-$ (root $\varepsilon - \delta_k$)
  - `E_eps1_del{k}_mp` = $a_1^- b_k^+$ (root $-\varepsilon + \delta_k$)
  - `E_eps1_del{k}_mm` = $a_1^- b_k^-$ (root $-\varepsilon - \delta_k$)

---

## 3. PBW Ordering Convention

We adopt the canonical PBW ordering separating the nilpotent central parameter, odd basis, and even basis:
$$
\kappa < [\text{odd basis}] < [\text{even basis}]
$$
where $K=1$ is treated as the scalar identity and excluded from the basis.

### Sub-ordering:
1. **Nilpotent parameter**: $\kappa$
2. **Odd elements** (sorted lexicographically by bosonic index $k$, then sign pattern `pp < pm < mp < mm`):
   $$
   E_{\varepsilon+\delta_1}, E_{\varepsilon-\delta_1}, E_{-\varepsilon+\delta_1}, E_{-\varepsilon-\delta_1}, \dots, E_{\varepsilon+\delta_n}, E_{\varepsilon-\delta_n}, E_{-\varepsilon+\delta_n}, E_{-\varepsilon-\delta_n}
   $$
3. **Even elements**:
   - Cartan elements first: $H_1, \dots, H_{n+1}$
   - Followed by $2\delta_k$ roots: $E_{2\delta_1\_p}, \dots, E_{2\delta_n\_p}, E_{2\delta_1\_m}, \dots, E_{2\delta_n\_m}$
   - Followed by cross-pair roots $\delta_i \pm \delta_j$ ($i < j$): `pp`, `mm`, `pm`, `mp`.

---

## 4. Basis Lists for $C(2)$, $C(3)$, and $C(4)$

### 4.1 $C(2) = \mathfrak{osp}(2|2)$ ($n=1$, dim $4 \mid 4$)
- **Even basis (4)**:
  `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- **Odd basis (4)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`

### 4.2 $C(3) = \mathfrak{osp}(2|4)$ ($n=2$, dim $11 \mid 8$)
- **Even basis (11)**:
  `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_2del1_m", "E_2del2_m", "E_del1_del2_pp", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd basis (8)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`

### 4.3 $C(4) = \mathfrak{osp}(2|6)$ ($n=3$, dim $22 \mid 12$)
- **Even basis (22)**:
  - Cartans (4): `["H_1", "H_2", "H_3", "H_4"]`
  - $2\delta$ roots (6): `["E_2del1_p", "E_2del2_p", "E_2del3_p", "E_2del1_m", "E_2del2_m", "E_2del3_m"]`
  - $\delta_i \pm \delta_j$ roots (12):
    - $i=1, j=2$: `["E_del1_del2_pp", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
    - $i=1, j=3$: `["E_del1_del3_pp", "E_del1_del3_mm", "E_del1_del3_pm", "E_del1_del3_mp"]`
    - $i=2, j=3$: `["E_del2_del3_pp", "E_del2_del3_mm", "E_del2_del3_pm", "E_del2_del3_mp"]`
- **Odd basis (12)**:
  - $k=1$: `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`
  - $k=2$: `["E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`
  - $k=3$: `["E_eps1_del3_pp", "E_eps1_del3_pm", "E_eps1_del3_mp", "E_eps1_del3_mm"]`

