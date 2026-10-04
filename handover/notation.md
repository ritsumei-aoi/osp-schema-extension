# Notation and Terminology for $C(n+1) = \mathfrak{osp}(2|2n)$

This document defines the mathematical notation, generator labeling conventions, basis lists, and PBW ordering used throughout the $C(n+1)$ schema extension.

---

## 1. Oscillator Realization & Central Elements

### 1.1 Oscillators
- **Fermionic Oscillators**: Canonical Anticommutation Relations (CAR), parity $p(a_1^\pm) = 1$:
  $$\{a_1^-, a_1^+\} = a_1^- a_1^+ + a_1^+ a_1^- = 1, \quad (a_1^+)^2 = 0, \quad (a_1^-)^2 = 0$$
  - Schema labels: `a_1_p` ($a_1^+$), `a_1_m` ($a_1^-$).
- **Bosonic Oscillators**: Canonical Commutation Relations (CCR), parity $p(b_k^\pm) = 0$ ($k = 1, \ldots, n$):
  $$[b_k^-, b_l^+] = b_k^- b_l^+ - b_l^+ b_k^- = \delta_{kl}, \quad [b_k^\pm, b_l^\pm] = 0$$
  - Schema labels: `b_{k}_p` ($b_k^+$), `b_{k}_m` ($b_k^-$) for $k \in \{1, \ldots, n\}$.
- **Mixed Relations (Undeformed)**:
  $$[b_k^\pm, a_1^\pm] = 0$$

### 1.2 Central Elements
- $K$: Even central element ($p(K) = 0$), identified with scalar 1.
- $\kappa$: Odd central parameter ($p(\kappa) = 1$) with $\kappa^2 = 0$, governing the nilpotent extension $\tilde{\mathfrak{g}} = \mathfrak{g} \oplus \mathbb{C}\kappa$.

---

## 2. Generator Definitions and Labels

### 2.1 Cartan Generators ($n+1$ total, parity 0)
- $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$
- $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $2 \leq k \leq n$
- $H_{n+1} = -b_n^+ b_n^- - \frac{1}{2}$
- Schema labels: `H_1`, `H_2`, ..., `H_{n+1}`.

### 2.2 Even Root Generators ($2n^2$ total, parity 0)
- **Long roots ($\pm 2\delta_k$, $2n$ generators)**:
  - $E_{2\delta_k} = (b_k^+)^2 \implies$ `E_2del{k}_p`
  - $E_{-2\delta_k} = (b_k^-)^2 \implies$ `E_2del{k}_m`
- **Cross roots ($\pm \delta_i \pm \delta_j$ with $1 \leq i < j \leq n$, $2n(n-1)$ generators)**:
  - $E_{\delta_i + \delta_j} = b_i^+ b_j^+ \implies$ `E_del{i}_del{j}_pp`
  - $E_{-\delta_i - \delta_j} = b_i^- b_j^- \implies$ `E_del{i}_del{j}_mm`
  - $E_{\delta_i - \delta_j} = b_i^+ b_j^- \implies$ `E_del{i}_del{j}_pm`
  - $E_{-\delta_i + \delta_j} = b_i^- b_j^+ \implies$ `E_del{i}_del{j}_mp`

Total even dimension: $\dim(\mathfrak{g}_{\bar{0}}) = (n+1) + 2n + 2n(n-1) = 2n^2 + n + 1$.

### 2.3 Odd Root Generators ($4n$ total, parity 1)
- **Fermionic roots ($\pm \varepsilon \pm \delta_k$ with $1 \leq k \leq n$)**:
  - $E_{\varepsilon + \delta_k} = a_1^+ b_k^+ \implies$ `E_eps1_del{k}_pp`
  - $E_{\varepsilon - \delta_k} = a_1^+ b_k^- \implies$ `E_eps1_del{k}_pm`
  - $E_{-\varepsilon + \delta_k} = a_1^- b_k^+ \implies$ `E_eps1_del{k}_mp`
  - $E_{-\varepsilon - \delta_k} = a_1^- b_k^- \implies$ `E_eps1_del{k}_mm`

Total odd dimension: $\dim(\mathfrak{g}_{\bar{1}}) = 4n$.

---

## 3. Explicit Basis Lists for $n=1, 2, 3$

### 3.1 $C(2) = \mathfrak{osp}(2|2)$ ($n=1$)
- **Even Basis (4 elements)**:
  `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- **Odd Basis (4 elements)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`
- **Total Dimension**: 8 ($4 \mid 4$).

### 3.2 $C(3) = \mathfrak{osp}(2|4)$ ($n=2$)
- **Even Basis (11 elements)**:
  `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd Basis (8 elements)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`
- **Total Dimension**: 19 ($11 \mid 8$).

### 3.3 $C(4) = \mathfrak{osp}(2|6)$ ($n=3$)
- **Even Basis (22 elements)**:
  `["H_1", "H_2", "H_3", "H_4", "E_2del1_p", "E_2del2_p", "E_2del3_p", "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp", "E_2del1_m", "E_2del2_m", "E_2del3_m", "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm", "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm", "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"]`
- **Odd Basis (12 elements)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm", "E_eps1_del3_pp", "E_eps1_del3_pm", "E_eps1_del3_mp", "E_eps1_del3_mm"]`
- **Total Dimension**: 34 ($22 \mid 12$).

---

## 4. PBW Ordering

### 4.1 Options Considered
1. **Option A (Parity-Grouped: $\kappa < [\text{Odd}] < [\text{Even}])$**:
   - Order: $\kappa < \text{Odd Basis} < \text{Even Basis}$.
   - Odd sector: ordered by index $k$ ($k=1,\ldots,n$) with sub-order `(pp, pm, mp, mm)`.
   - Even sector: Cartans $H_1, \ldots, H_{n+1}$, followed by positive long roots, positive cross roots, negative long roots, negative cross roots, and mixed cross roots `(pm, mp)`.
2. **Option B (Root-Height / Triangular Graded Ordering)**:
   - Order: $\kappa < \text{Cartan} < \text{Positive Roots (Even + Odd)} < \text{Negative Roots (Even + Odd)}$.
3. **Option C (Parity-Grouped: $\kappa < [\text{Even}] < [\text{Odd}])$**:
   - Order: $\kappa < \text{Even Basis} < \text{Odd Basis}$.

### 4.2 Decision & Justification
**Option A** is adopted.
- **Justification**:
  1. Direct structural consistency with the $B(0,n)$ v5.0 schema convention (`PBW: κ < [odd] < [even]`), ensuring compatibility across the schema layers.
  2. Clear stratification between odd fermionic deformation space and even Lie algebraic generators.
  3. Clean separation during coboundary map $\delta f$ matrix representation.

---

## 5. Inhomogeneous Deformation Parameters (gb Matrix)

Deformation parameters $\mathrm{gb}_{\sigma, j, s}$ index the deformed brackets $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma, j, s} \cdot \kappa$:
- `gb_a1p_b{j}p` : $\mathrm{gb}_{a_1^+, b_j^+}$
- `gb_a1p_b{j}m` : $\mathrm{gb}_{a_1^+, b_j^-}$
- `gb_a1m_b{j}p` : $\mathrm{gb}_{a_1^-, b_j^+}$
- `gb_a1m_b{j}m` : $\mathrm{gb}_{a_1^-, b_j^-}$
Total deformation parameters for $C(n+1)$: $4n$.
