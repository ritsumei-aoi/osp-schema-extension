# Notation and Terminology

This document defines the mathematical notation, oscillator realizations, generator labeling conventions, and PBW ordering conventions used in this repository for the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension.

---

## 1. Oscillator Generators

The Lie superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$ is realized via an oscillator algebra over $V = V_{\bar{0}} \oplus V_{\bar{1}}$:

1. **Standard Fermionic Oscillator Pair** ($p = 1$):
   - Creation operator: $a_1^+$ (JSON label: `a_1_p`)
   - Annihilation operator: $a_1^-$ (JSON label: `a_1_m`)
   - Canonical Anticommutation Relation (CAR):
     $$\{a_1^-, a_1^+\} = a_1^- a_1^+ + a_1^+ a_1^- = 1, \quad (a_1^\pm)^2 = 0$$

2. **Bosonic Oscillators** ($p = 0$, $k = 1, \ldots, n$):
   - Creation operators: $b_k^+$ (JSON label: `b_k_p`)
   - Annihilation operators: $b_k^-$ (JSON label: `b_k_m`)
   - Canonical Commutation Relations (CCR):
     $$[b_k^-, b_l^+] = b_k^- b_l^+ - b_l^+ b_k^- = \delta_{kl}, \quad [b_k^\pm, b_l^\pm] = 0$$

3. **Central Elements**:
   - $\kappa$: Odd central element ($p(\kappa) = 1, \kappa^2 = 0$) parametrizing the inhomogeneous deformation.
   - $K$: Even central element ($p(K) = 0$, identity scalar $K = 1$).

---

## 2. Generator Labels and Oscillator Realizations

### 2.1 Even Subalgebra ($\mathfrak{g}_{\bar{0}}$, dimension $2n^2 + n + 1$)

The even subalgebra is $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$ of rank $n+1$.

- **Cartan Subalgebra** ($n+1$ generators):
  - $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$ (`H_1`)
  - $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ (`H_k`, for $2 \le k \le n$)
  - $H_{n+1} = -b_n^+ b_n^- - \frac{1}{2}$ (`H_{n+1}`)

- **Long Root Generators** ($\pm 2\delta_k$, $2n$ generators):
  - $E_{2\delta_k} = (b_k^+)^2$ (`E_2del{k}_p`, $k = 1, \ldots, n$)
  - $E_{-2\delta_k} = (b_k^-)^2$ (`E_2del{k}_m`, $k = 1, \ldots, n$)

- **Short Root Generators** ($\pm \delta_i \pm \delta_j$, $1 \le i < j \le n$, $2n(n-1)$ generators):
  - $E_{\delta_i + \delta_j} = b_i^+ b_j^+$ (`E_del{i}_del{j}_pp`)
  - $E_{-\delta_i - \delta_j} = b_i^- b_j^-$ (`E_del{i}_del{j}_mm`)
  - $E_{\delta_i - \delta_j} = b_i^+ b_j^-$ (`E_del{i}_del{j}_pm`)
  - $E_{-\delta_i + \delta_j} = b_i^- b_j^+$ (`E_del{i}_del{j}_mp`)

### 2.2 Odd Subspace ($\mathfrak{g}_{\bar{1}}$, dimension $4n$)

Odd roots are $\pm \varepsilon \pm \delta_k$ ($k = 1, \ldots, n$):
- $E_{\varepsilon + \delta_k} = a_1^+ b_k^+$ (`E_eps1_del{k}_pp`)
- $E_{\varepsilon - \delta_k} = a_1^+ b_k^-$ (`E_eps1_del{k}_pm`)
- $E_{-\varepsilon + \delta_k} = a_1^- b_k^+$ (`E_eps1_del{k}_mp`)
- $E_{-\varepsilon - \delta_k} = a_1^- b_k^-$ (`E_eps1_del{k}_mm`)

---

## 3. PBW Ordering Convention (Approved Option 1: Polarity-Ordered)

The PBW ordering follows the graded hierarchy:
$$\kappa < [\text{Odd Generators}] < [\text{Even Generators}]$$

### 3.1 Odd Sector Ordering
The $4n$ odd generators are ordered by root polarity (positive roots $\Delta_{\bar{1}}^+$ preceding negative roots $\Delta_{\bar{1}}^-$), preserving consistency with the $B(0,n)$ v5.0 schema convention:
1. Positive roots with $+\delta_k$: `E_eps1_del{k}_pp` ($k = 1, \ldots, n$)
2. Positive roots with $-\delta_k$: `E_eps1_del{k}_pm` ($k = 1, \ldots, n$)
3. Negative roots with $+\delta_k$: `E_eps1_del{k}_mp` ($k = 1, \ldots, n$)
4. Negative roots with $-\delta_k$: `E_eps1_del{k}_mm` ($k = 1, \ldots, n$)

### 3.2 Even Sector Ordering
The $2n^2 + n + 1$ even generators are ordered as follows:
1. Cartan generators: `H_1, ..., H_{n+1}`
2. Long positive roots: `E_2del{k}_p` ($k = 1, \ldots, n$)
3. Short positive roots ($++$): `E_del{i}_del{j}_pp` ($1 \le i < j \le n$, lexicographic on $(i,j)$)
4. Long negative roots: `E_2del{k}_m` ($k = 1, \ldots, n$)
5. Short negative roots ($--$): `E_del{i}_del{j}_mm` ($1 \le i < j \le n$, lexicographic on $(i,j)$)
6. Mixed short roots ($+-$): `E_del{i}_del{j}_pm` ($1 \le i < j \le n$, lexicographic on $(i,j)$)
7. Mixed short roots ($-+$): `E_del{i}_del{j}_mp` ($1 \le i < j \le n$, lexicographic on $(i,j)$)

---

## 4. Concrete Basis Lists for $n = 1, 2, 3$

### 4.1 $n = 1$: $C(2) = \mathfrak{osp}(2|2)$
- **Superdimension**: $4 \mid 4$, total 8
- **Even Basis (4)**:
  ```json
  [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m"
  ]
  ```
- **Odd Basis (4)**:
  ```json
  [
    "E_eps1_del1_pp",
    "E_eps1_del1_pm",
    "E_eps1_del1_mp",
    "E_eps1_del1_mm"
  ]
  ```

### 4.2 $n = 2$: $C(3) = \mathfrak{osp}(2|4)$
- **Superdimension**: $11 \mid 8$, total 19
- **Even Basis (11)**:
  ```json
  [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm",
    "E_del1_del2_pm",
    "E_del1_del2_mp"
  ]
  ```
- **Odd Basis (8)**:
  ```json
  [
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ]
  ```

### 4.3 $n = 3$: $C(4) = \mathfrak{osp}(2|6)$
- **Superdimension**: $22 \mid 12$, total 34
- **Even Basis (22)**:
  ```json
  [
    "H_1", "H_2", "H_3", "H_4",
    "E_2del1_p", "E_2del2_p", "E_2del3_p",
    "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp",
    "E_2del1_m", "E_2del2_m", "E_2del3_m",
    "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm",
    "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm",
    "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"
  ]
  ```
- **Odd Basis (12)**:
  ```json
  [
    "E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"
  ]
  ```
