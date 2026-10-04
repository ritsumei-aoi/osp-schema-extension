# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository for the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension project.

## 1. Oscillator Generators and Central Elements

- **Standard Fermionic Pair**: $a_1^+, a_1^-$ with Canonical Anticommutation Relations (CAR):
  $$\{a_1^-, a_1^+\} = 1, \quad \{a_1^+, a_1^+\} = 0, \quad \{a_1^-, a_1^-\} = 0$$
  Parity: $p(a_1^\pm) = 1$. In JSON schema: labels `"a_1_p"`, `"a_1_m"`.
- **Bosonic Oscillators**: $b_k^+, b_k^-$ ($k = 1, \ldots, n$) with Canonical Commutation Relations (CCR):
  $$[b_k^-, b_l^+] = \delta_{kl}, \quad [b_k^+, b_l^+] = 0, \quad [b_k^-, b_l^-] = 0$$
  Parity: $p(b_k^\pm) = 0$. In JSON schema: labels `"b_k_p"`, `"b_k_m"`.
- **Central Elements**:
  - $\kappa$: Odd central element ($p(\kappa) = 1$, $\kappa^2 = 0$) parametrizing the nilpotent extension.
  - $K$: Even central element ($p(K) = 0$), acting as identity $1$.

---

## 2. Generator Label Conventions

### Even Generators ($p=0$, dimension $2n^2 + n + 1$)
- **Cartan Generators** ($n+1$ elements):
  - `H_0`: $\mathfrak{so}(2)$ Cartan element, $a_1^+ a_1^- - 1/2$.
  - `H_k` ($k = 1, \ldots, n$): $\mathfrak{sp}(2n)$ Cartan elements, $b_k^+ b_k^- + 1/2$.
- **$\mathfrak{sp}(2n)$ Root Generators**:
  - `E_2del{k}_p`: $2\delta_k$ root generator, $(b_k^+)^2$.
  - `E_2del{k}_m`: $-2\delta_k$ root generator, $(b_k^-)^2$.
  - `E_del{i}_del{j}_pp` ($i < j$): $\delta_i + \delta_j$ root generator, $b_i^+ b_j^+$.
  - `E_del{i}_del{j}_mm` ($i < j$): $-(\delta_i + \delta_j)$ root generator, $b_i^- b_j^-$.
  - `E_del{i}_del{j}_pm` ($i < j$): $\delta_i - \delta_j$ root generator, $b_i^+ b_j^-$.
  - `E_del{i}_del{j}_mp` ($i < j$): $-(\delta_i - \delta_j)$ root generator, $b_i^- b_j^+$.

### Odd Generators ($p=1$, dimension $4n$)
- `E_eps1_del{k}_pp`: $\varepsilon + \delta_k$ root generator, $a_1^+ b_k^+$.
- `E_eps1_del{k}_pm`: $\varepsilon - \delta_k$ root generator, $a_1^+ b_k^-$.
- `E_eps1_del{k}_mp`: $-\varepsilon + \delta_k$ root generator, $a_1^- b_k^+$.
- `E_eps1_del{k}_mm`: $-\varepsilon - \delta_k$ root generator, $a_1^- b_k^-$.

---

## 3. Basis Lists for $C(2)$, $C(3)$, and $C(4)$

### $C(2) = \mathfrak{osp}(2|2)$ ($n=1$, total dim 8: 4 even, 4 odd)
- **Even Basis** (4): `["H_0", "H_1", "E_2del1_p", "E_2del1_m"]`
- **Odd Basis** (4): `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`

### $C(3) = \mathfrak{osp}(2|4)$ ($n=2$, total dim 19: 11 even, 8 odd)
- **Even Basis** (11):
  `["H_0", "H_1", "H_2", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd Basis** (8):
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`

### $C(4) = \mathfrak{osp}(2|6)$ ($n=3$, total dim 34: 22 even, 12 odd)
- **Even Basis** (22):
  Cartans: `["H_0", "H_1", "H_2", "H_3"]`
  Positive roots: `["E_2del1_p", "E_2del2_p", "E_2del3_p", "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp"]`
  Negative roots: `["E_2del1_m", "E_2del2_m", "E_2del3_m", "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm"]`
  Mixed roots: `["E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm", "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"]`
- **Odd Basis** (12):
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm", "E_eps1_del3_pp", "E_eps1_del3_pm", "E_eps1_del3_mp", "E_eps1_del3_mm"]`

---

## 4. PBW Ordering Decision and Justification

### Options Considered
1. **Option 1 (Parity Block Ordering)**:
   $$\kappa < [\text{odd basis}] < [\text{even basis}]$$
   Ordering within odd basis: sorted by rank $k$ then sign combination (`pp`, `pm`, `mp`, `mm`).
   Ordering within even basis: Cartans ($H_0, H_1, \dots, H_n$), then positive roots, negative roots, mixed roots.
2. **Option 2 (Lexicographical Root Weight Ordering)**:
   Generators ordered by weight vector $(\pm\varepsilon, \pm\delta_1, \dots, \pm\delta_n)$ in lexicographical order.

### Decision and Justification
**Selected Option**: **Option 1 (Parity Block Ordering)**.

**Justification**:
1. **Schema Backward Compatibility**: B(0,n) schema v5.0 employs `κ < [odd] < [even]`. Keeping this structure ensures algorithms processing graded commutators, Jacobi identity, and deformation matrices can use uniform indexing logic.
2. **Graded Algebra Separation**: Isolating odd generators before even generators simplifies matrix representations for the coboundary operator $\delta f$ and inhomogeneous deformation matrix $gb$.
