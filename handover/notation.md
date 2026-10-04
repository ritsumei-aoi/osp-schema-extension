# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository for the $C(n+1) = \mathfrak{osp}(2|2n)$ Lie superalgebra schema extension project.

## 1. Lie Superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$

- **Bosonic Rank**: $n \ge 1$.
- **Even Subalgebra**: $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$, dimension $\dim(\mathfrak{g}_{\bar{0}}) = 2n^2 + n + 1$.
- **Odd Subspace**: Dimension $\dim(\mathfrak{g}_{\bar{1}}) = 4n$.
- **Superdimension**: $(2n^2 + n + 1) \mid 4n$, total dimension $2n^2 + 5n + 1$.

## 2. Oscillator Generators & Relations

### Oscillators
- **Fermionic pair**: $a_1^+, a_1^-$ with parity $p(a_1^\pm) = 1$. CAR relation:
  $$\{a_1^-, a_1^+\} = 1, \quad (a_1^+)^2 = (a_1^-)^2 = 0.$$
- **Bosonic pairs**: $b_k^+, b_k^-$ ($k = 1, \ldots, n$) with parity $p(b_k^\pm) = 0$. CCR relations:
  $$[b_k^-, b_l^+] = \delta_{kl}, \quad [b_k^\pm, b_l^\pm] = 0.$$
- **Mixed commutators**: $[b_k^\pm, a_1^\sigma] = 0$ for standard algebra. (Under deformation, $[b_k^s, a_1^\sigma] = -\mathrm{gb}_{\sigma, k, s}\kappa$).

### Central Elements
- $\kappa$: Odd central element ($p(\kappa) = 1$, $\kappa^2 = 0$) representing the nilpotent deformation extension parameter.
- $K$: Even central identity scalar ($p(K) = 0$, $K = 1$).

## 3. Generator Labels and Oscillator Realizations

### Even Generators ($p=0$)
1. **Cartan Generators** ($n+1$ total):
   - $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$ (label: `H_1`)
   - $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $2 \le k \le n$ (label: `H_{k}`)
   - $H_{n+1} = -b_n^+ b_n^- - \frac{1}{2}$ (label: `H_{n+1}`)
2. **$\mathfrak{sp}(2n)$ Long Roots** ($2n$ total):
   - $E_{2\delta_k} = (b_k^+)^2$ (label: `E_2del{k}_p`)
   - $E_{-2\delta_k} = (b_k^-)^2$ (label: `E_2del{k}_m`)
3. **$\mathfrak{sp}(2n)$ Short Roots** ($2n(n-1)$ total, $1 \le i < j \le n$):
   - $E_{\delta_i + \delta_j} = b_i^+ b_j^+$ (label: `E_del{i}_del{j}_pp`)
   - $E_{\delta_i - \delta_j} = b_i^+ b_j^-$ (label: `E_del{i}_del{j}_pm`)
   - $E_{-\delta_i + \delta_j} = b_i^- b_j^+$ (label: `E_del{i}_del{j}_mp`)
   - $E_{-\delta_i - \delta_j} = b_i^- b_j^-$ (label: `E_del{i}_del{j}_mm`)

### Odd Generators ($p=1$)
Roots $\pm \varepsilon \pm \delta_k$ ($4n$ total, $1 \le k \le n$):
- $E_{\varepsilon + \delta_k} = a_1^+ b_k^+$ (label: `E_eps1_del{k}_pp`)
- $E_{\varepsilon - \delta_k} = a_1^+ b_k^-$ (label: `E_eps1_del{k}_pm`)
- $E_{-\varepsilon + \delta_k} = a_1^- b_k^+$ (label: `E_eps1_del{k}_mp`)
- $E_{-\varepsilon - \delta_k} = a_1^- b_k^-$ (label: `E_eps1_del{k}_mm`)

## 4. Basis Lists for $n=1, 2, 3$

### $n=1$ ($C(2) = \mathfrak{osp}(2|2)$)
- **Even (4)**: `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- **Odd (4)**: `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`

### $n=2$ ($C(3) = \mathfrak{osp}(2|4)$)
- **Even (11)**: `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd (8)**: `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`

### $n=3$ ($C(4) = \mathfrak{osp}(2|6)$)
- **Even (22)**: `["H_1", "H_2", "H_3", "H_4", "E_2del1_p", "E_2del2_p", "E_2del3_p", "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp", "E_2del1_m", "E_2del2_m", "E_2del3_m", "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm", "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm", "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"]`
- **Odd (12)**: `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm", "E_eps1_del3_pp", "E_eps1_del3_pm", "E_eps1_del3_mp", "E_eps1_del3_mm"]`

## 5. PBW Ordering Convention

We adopt **Option 1: Graded Block Ordering ($\kappa < \text{odd} < \text{even}$)**:
$$\text{PBW}: \kappa < [\text{odd generators}] < [\text{even generators}].$$

- **Options Considered**:
  1. **Option 1 ($\kappa < \text{odd} < \text{even}$)**: Odd generators placed first in lexicographical root index order, followed by even generators.
  2. **Option 2 ($\kappa < \text{even} < \text{odd}$)**: Even generators placed first, followed by odd generators.
  3. **Option 3 (Root-Height Canonical Ordering)**: Ordering generators by root height (negative roots < Cartan < positive roots).
- **Decision & Justification**:
  Option 1 was chosen to maintain direct compatibility with the $B(0,n)$ v5.0 JSON schema convention (`PBW: κ < [odd] < [even]`). This ensures seamless processing in downstream validation and computation tools designed for the v5.0 schema family.
