# Notation and Terminology

This document defines the mathematical notation, basis conventions, PBW ordering, and oscillator realizations for $C(n+1) = \mathfrak{osp}(2|2n)$.

---

## 1. Algebra Overview and Dimensions

- **Algebra Family**: $C(n+1) = \mathfrak{osp}(2|2n)$, with bosonic rank $n \ge 1$ and fermionic rank $m = 1$.
- **Even Subalgebra**: $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$, dimension $= 2n^2 + n + 1$.
- **Odd Subspace**: Dimension $= 4n$.
- **Total Dimension**: $(2n^2 + n + 1) + 4n = 2n^2 + 5n + 1$.

| $n$ | Algebra | Even Dim ($2n^2+n+1$) | Odd Dim ($4n$) | Total Dim ($2n^2+5n+1$) |
|---|---|---|---|---|
| $n=1$ | $C(2) = \mathfrak{osp}(2\|2)$ | 4 | 4 | 8 |
| $n=2$ | $C(3) = \mathfrak{osp}(2\|4)$ | 11 | 8 | 19 |
| $n=3$ | $C(4) = \mathfrak{osp}(2\|6)$ | 22 | 12 | 34 |

---

## 2. Oscillator Realization

### 2.1 Oscillators
- **Fermionic Oscillators** ($m=1$): $a_1^+, a_1^-$ with parity $p(a_1^\pm) = 1$.
  - Canonical Anticommutation Relations (CAR):
    $$\{a_1^-, a_1^+\} = a_1^- a_1^+ + a_1^+ a_1^- = 1, \quad \{a_1^+, a_1^+\} = 2(a_1^+)^2 = 0, \quad \{a_1^-, a_1^-\} = 2(a_1^-)^2 = 0.$$
- **Bosonic Oscillators** ($n$ pairs): $b_j^+, b_j^-$ for $j = 1, \ldots, n$ with parity $p(b_j^\pm) = 0$.
  - Canonical Commutation Relations (CCR):
    $$[b_j^-, b_k^+] = b_j^- b_k^+ - b_k^+ b_j^- = \delta_{jk}, \quad [b_j^\pm, b_k^\pm] = 0.$$
- **Cross-Relations**:
  $$[b_j^\pm, a_1^\sigma] = 0 \quad (\sigma \in \{+,-\}, j = 1, \dots, n).$$

### 2.2 Central Elements
- $\kappa$: Odd central element ($p(\kappa) = 1$, $\kappa^2 = 0$) governing the inhomogeneous deformation.
- $K$: Even central identity scalar ($p(K) = 0$, $K = 1$).

---

## 3. Generator Naming and Realization

### 3.1 Cartan Generators ($n+1$ total, parity 0)
- $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$
- $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $2 \le k \le n$
- $H_{n+1} = -b_n^+ b_n^- - \tfrac{1}{2}$

### 3.2 Even Root Generators ($2n^2$ total, parity 0)
- **Long roots** ($2n$ total):
  - $E_{2\delta_k}$: `E_2del{k}_p` $= (b_k^+)^2$
  - $E_{-2\delta_k}$: `E_2del{k}_m` $= (b_k^-)^2$
- **Short even roots** ($2n(n-1)$ total, for $1 \le i < j \le n$):
  - $E_{\delta_i + \delta_j}$: `E_del{i}_del{j}_pp` $= b_i^+ b_j^+$
  - $E_{-\delta_i - \delta_j}$: `E_del{i}_del{j}_mm` $= b_i^- b_j^-$
  - $E_{\delta_i - \delta_j}$: `E_del{i}_del{j}_pm` $= b_i^+ b_j^-$
  - $E_{-\delta_i + \delta_j}$: `E_del{i}_del{j}_mp` $= b_i^- b_j^+$

### 3.3 Odd Root Generators ($4n$ total, parity 1)
For $k = 1, \ldots, n$:
- $E_{\varepsilon + \delta_k}$: `E_eps1_del{k}_pp` $= a_1^+ b_k^+$
- $E_{\varepsilon - \delta_k}$: `E_eps1_del{k}_pm` $= a_1^+ b_k^-$
- $E_{-\varepsilon + \delta_k}$: `E_eps1_del{k}_mp` $= a_1^- b_k^+$
- $E_{-\varepsilon - \delta_k}$: `E_eps1_del{k}_mm` $= a_1^- b_k^-$

---

## 4. PBW Ordering

We considered two candidate PBW orderings:

1. **Option A (Polarity-First ordering, Selected)**:
   $$\kappa < [\text{Odd } (++ \text{ then } +- \text{ then } -+ \text{ then } --)] < [\text{Even Cartans}] < [\text{Even Positive Roots}] < [\text{Even Negative Roots}] < [\text{Even Mixed Roots}]$$
   - Odd generators are ordered by oscillator sign polarities:
     1. `E_eps1_del{k}_pp` ($k=1..n$)
     2. `E_eps1_del{k}_pm` ($k=1..n$)
     3. `E_eps1_del{k}_mp` ($k=1..n$)
     4. `E_eps1_del{k}_mm` ($k=1..n$)
   - Even generators:
     1. Cartans: `H_1, ..., H_{n+1}`
     2. Positive roots: `E_2del{k}_p` ($k=1..n$), `E_del{i}_del{j}_pp` ($i<j$)
     3. Negative roots: `E_2del{k}_m` ($k=1..n$), `E_del{i}_del{j}_mm` ($i<j$)
     4. Mixed roots: `E_del{i}_del{j}_pm` ($i<j$), `E_del{i}_del{j}_mp` ($i<j$)
   - **Rationale**: Option A directly generalizes the $B(0,n)$ v5.0 convention (where all positive root generators precede all negative root generators), keeping the positive fermionic sector ($a_1^+$) grouped together and separated from the negative fermionic sector ($a_1^-$).

2. **Option B (Mode/Multiplet-First ordering)**:
   - For each mode $k=1..n$, list all 4 odd generators together: `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm`.
   - While mode-local, Option B breaks the polarity grading structure and is inconsistent with the $B(0,n)$ convention.

Therefore, **Option A** is adopted.

---

## 5. Basis Lists for $n=1, 2, 3$

### 5.1 $n=1$ ($C(2) = \mathfrak{osp}(2|2)$)
- **Even (4)**:
  `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- **Odd (4)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`

### 5.2 $n=2$ ($C(3) = \mathfrak{osp}(2|4)$)
- **Even (11)**:
  `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd (8)**:
  `["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del1_mm", "E_eps1_del2_mm"]`

### 5.3 $n=3$ ($C(4) = \mathfrak{osp}(2|6)$)
- **Even (22)**:
  `["H_1", "H_2", "H_3", "H_4", "E_2del1_p", "E_2del2_p", "E_2del3_p", "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp", "E_2del1_m", "E_2del2_m", "E_2del3_m", "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm", "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm", "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"]`
- **Odd (12)**:
  `["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp", "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm", "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp", "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"]`
