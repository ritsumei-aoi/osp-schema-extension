# Notation and Terminology for C(n+1) = osp(2|2n)

This document defines the mathematical notation, generator labels, basis structures, and PBW ordering conventions for the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension.

---

## 1. Oscillator Generators and Parity

The algebra $C(n+1) = \mathfrak{osp}(2|2n)$ is realized via:
- **Standard fermionic oscillator pair** ($m=1$):
  - $a_1^+, a_1^-$ represented as `a_1_p`, `a_1_m`
  - Parity: $p(a_1^\pm) = 1$ (odd)
  - Canonical Anticommutation Relations (CAR):
    $$\{a_1^-, a_1^+\} = 1, \quad (a_1^+)^2 = 0, \quad (a_1^-)^2 = 0$$
- **Bosonic oscillators** ($n$ pairs, $k = 1, \ldots, n$):
  - $b_k^+, b_k^-$ represented as `b_k_p`, `b_k_m`
  - Parity: $p(b_k^\pm) = 0$ (even)
  - Canonical Commutation Relations (CCR):
    $$[b_j^-, b_k^+] = \delta_{jk}, \quad [b_j^\pm, b_k^\pm] = 0$$
- **Cross relations**:
  - $[b_k^\pm, a_1^\sigma] = 0$ in the unperturbed algebra.
- **Central elements**:
  - `kappa` ($\kappa$): odd central element ($p(\kappa) = 1$, $\kappa^2 = 0$) parametrizing deformations.
  - `K`: even central element ($p(K) = 0$), identified with scalar 1.

---

## 2. Generator Realizations and Notation Conventions

### 2.1 Cartan Generators ($n+1$ generators, parity 0)
- $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$ (`H_1`)
- $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ (`H_k` for $2 \leq k \leq n$)
- $H_{n+1} = -b_n^+ b_n^- - \frac{1}{2}$ (`H_{n+1}`)

### 2.2 Even Root Generators ($2n^2$ generators, parity 0)
- $E_{2\delta_k} = (b_k^+)^2$ (`E_2del{k}_p`)
- $E_{-2\delta_k} = (b_k^-)^2$ (`E_2del{k}_m`)
- For $1 \leq i < j \leq n$:
  - $E_{\delta_i + \delta_j} = b_i^+ b_j^+$ (`E_del{i}_del{j}_pp`)
  - $E_{\delta_i - \delta_j} = b_i^+ b_j^-$ (`E_del{i}_del{j}_pm`)
  - $E_{-\delta_i + \delta_j} = b_i^- b_j^+$ (`E_del{i}_del{j}_mp`)
  - $E_{-\delta_i - \delta_j} = b_i^- b_j^-$ (`E_del{i}_del{j}_mm`)

### 2.3 Odd Root Generators ($4n$ generators, parity 1)
- For $k = 1, \ldots, n$:
  - $E_{\varepsilon + \delta_k} = a_1^+ b_k^+$ (`E_eps1_del{k}_pp`)
  - $E_{\varepsilon - \delta_k} = a_1^+ b_k^-$ (`E_eps1_del{k}_pm`)
  - $E_{-\varepsilon + \delta_k} = a_1^- b_k^+$ (`E_eps1_del{k}_mp`)
  - $E_{-\varepsilon - \delta_k} = a_1^- b_k^-$ (`E_eps1_del{k}_mm`)

---

## 3. PBW Ordering

We considered two candidate ordering conventions:
1. **Option A (Odd-first PBW convention)**:
   $$\kappa < [\text{odd generators}] < [\text{even Cartan generators}] < [\text{even root generators}]$$
   - Odd generators ordered by bosonic index $k=1,\ldots,n$, then signs `pp, pm, mp, mm`.
   - Cartan generators $H_1, \ldots, H_{n+1}$.
   - Even root generators ordered by $2\delta_k$ then $\delta_i \pm \delta_j$.
2. **Option B (Even-first PBW convention)**:
   $$\kappa < [\text{Cartan}] < [\text{even roots}] < [\text{odd generators}]$$

### Selection & Justification:
We adopt **Option A**. This choice directly mirrors the established $B(0,n)$ schema convention (`κ < [odd] < [even]`), ensuring maximal architectural consistency across superalgebra families in this repository and simplifying downstream serialization and test suites.

---

## 4. Basis Lists for $n=1, 2, 3$

### 4.1 $C(2) = \mathfrak{osp}(2|2)$ ($n=1$)
- **Superdimension**: $4 \mid 4$ (total: 8)
- **Even Basis (4)**:
  `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- **Odd Basis (4)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`

### 4.2 $C(3) = \mathfrak{osp}(2|4)$ ($n=2$)
- **Superdimension**: $11 \mid 8$ (total: 19)
- **Even Basis (11)**:
  `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd Basis (8)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`

### 4.3 $C(4) = \mathfrak{osp}(2|6)$ ($n=3$)
- **Superdimension**: $22 \mid 12$ (total: 34)
- **Even Basis (22)**:
  `["H_1", "H_2", "H_3", "H_4", "E_2del1_p", "E_2del2_p", "E_2del3_p", "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp", "E_2del1_m", "E_2del2_m", "E_2del3_m", "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm", "E_del1_del2_pm", "E_del1_del2_mp", "E_del1_del3_pm", "E_del1_del3_mp", "E_del2_del3_pm", "E_del2_del3_mp"]`
- **Odd Basis (12)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm", "E_eps1_del3_pp", "E_eps1_del3_pm", "E_eps1_del3_mp", "E_eps1_del3_mm"]`
