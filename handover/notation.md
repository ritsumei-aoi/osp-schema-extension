# Notation and Terminology

This document defines the mathematical notation, oscillator realizations, basis ordering, and terminology used throughout the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension project.

---

## 1. Algebra Definition and Superdimension

The Lie superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$ has:
- **Fermionic rank**: $m = 1$ (associated with the $\varepsilon$ root vector and fermionic oscillator pair $a_1^\pm$).
- **Bosonic rank**: $n$ (associated with orthogonal root vectors $\delta_1, \ldots, \delta_n$ and bosonic oscillator pairs $b_1^\pm, \ldots, b_n^\pm$).
- **Even subalgebra**: $\mathfrak{g}_{\bar{0}} = \mathfrak{so}(2) \oplus \mathfrak{sp}(2n)$, dimension $\dim(\mathfrak{g}_{\bar{0}}) = 2n^2 + n + 1$.
- **Odd subspace**: $\mathfrak{g}_{\bar{1}}$, dimension $\dim(\mathfrak{g}_{\bar{1}}) = 4n$.
- **Total dimension**: $\dim(\mathfrak{g}) = 2n^2 + 5n + 1$.

### Dimension Table

| $n$ | Algebra | Even dim ($2n^2+n+1$) | Odd dim ($4n$) | Total dim ($2n^2+5n+1$) |
|---|---|---|---|---|
| $n=1$ | $C(2) = \mathfrak{osp}(2\|2)$ | 4 | 4 | 8 |
| $n=2$ | $C(3) = \mathfrak{osp}(2\|4)$ | 11 | 8 | 19 |
| $n=3$ | $C(4) = \mathfrak{osp}(2\|6)$ | 22 | 12 | 34 |

---

## 2. Oscillator Realization and Relations

### 2.1 Generators
- **Fermionic oscillators**: $a_1^+, a_1^-$ (labels: `a_1_p`, `a_1_m`), parity 1.
- **Bosonic oscillators**: $b_k^+, b_k^-$ (labels: `b_k_p`, `b_k_m`, $k=1, \ldots, n$), parity 0.
- **Central elements**:
  - $\kappa$ (`kappa`): parity 1, central, nilpotent ($\kappa^2 = 0$). Formal deformation parameter carrier.
  - $K$ (`K`): parity 0, central identity element ($K = 1$).

### 2.2 Canonical Relations
- **CAR (Fermions)**:
  $$\{a_1^-, a_1^+\} = a_1^- a_1^+ + a_1^+ a_1^- = 1, \quad (a_1^+)^2 = 0, \quad (a_1^-)^2 = 0$$
- **CCR (Bosons)**:
  $$[b_j^-, b_k^+] = b_j^- b_k^+ - b_k^+ b_j^- = \delta_{jk}, \quad [b_j^\pm, b_k^\pm] = 0$$
- **Cross relations**:
  $$[a_1^\pm, b_k^\pm] = 0 \quad (\text{undeformed})$$
- **Inhomogeneous deformation**:
  $$[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma, j, s} \cdot \kappa \quad (\sigma \in \{+,-\}, s \in \{+,-\})$$

---

## 3. Basis Elements and Oscillator Realizations

### 3.1 Cartan Subalgebra ($n+1$ generators, even)
- $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$
- $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $2 \leq k \leq n$
- $H_{n+1} = -b_n^+ b_n^- - \frac{1}{2}$

*(Note: The Cartan generators span the Cartan subalgebra of $\mathfrak{so}(2) \oplus \mathfrak{sp}(2n)$).*

### 3.2 Even Root Generators ($2n^2$ generators, even)
- **Long roots** ($2n$ generators):
  - $E_{2\delta_k} \to$ `E_2del{k}_p` $= (b_k^+)^2$
  - $E_{-2\delta_k} \to$ `E_2del{k}_m` $= (b_k^-)^2$
- **Short/mixed bosonic roots** ($2n(n-1)$ generators for $n \geq 2$, $1 \leq i < j \leq n$):
  - $E_{\delta_i + \delta_j} \to$ `E_del{i}_del{j}_pp` $= b_i^+ b_j^+$
  - $E_{-\delta_i - \delta_j} \to$ `E_del{i}_del{j}_mm` $= b_i^- b_j^-$
  - $E_{\delta_i - \delta_j} \to$ `E_del{i}_del{j}_pm` $= b_i^+ b_j^-$
  - $E_{-\delta_i + \delta_j} \to$ `E_del{i}_del{j}_mp` $= b_i^- b_j^+$

### 3.3 Odd Root Generators ($4n$ generators, odd)
For each $k \in \{1, \ldots, n\}$:
- $E_{\varepsilon + \delta_k} \to$ `E_eps1_del{k}_pp` $= a_1^+ b_k^+$
- $E_{\varepsilon - \delta_k} \to$ `E_eps1_del{k}_pm` $= a_1^+ b_k^-$
- $E_{-\varepsilon + \delta_k} \to$ `E_eps1_del{k}_mp` $= a_1^- b_k^+$
- $E_{-\varepsilon - \delta_k} \to$ `E_eps1_del{k}_mm` $= a_1^- b_k^-$

---

## 4. Basis Enumeration for $n=1, 2, 3$

### 4.1 $C(2) = \mathfrak{osp}(2|2)$ ($n=1$, Even: 4, Odd: 4, Total: 8)
- **Even basis (4)**:
  `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- **Odd basis (4)**:
  `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

### 4.2 $C(3) = \mathfrak{osp}(2|4)$ ($n=2$, Even: 11, Odd: 8, Total: 19)
- **Even basis (11)**:
  `H_1`, `H_2`, `H_3`,
  `E_2del1_p`, `E_2del2_p`,
  `E_2del1_m`, `E_2del2_m`,
  `E_del1_del2_pp`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
- **Odd basis (8)**:
  `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`,
  `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`

### 4.3 $C(4) = \mathfrak{osp}(2|6)$ ($n=3$, Even: 22, Odd: 12, Total: 34)
- **Even basis (22)**:
  `H_1`, `H_2`, `H_3`, `H_4`,
  `E_2del1_p`, `E_2del2_p`, `E_2del3_p`,
  `E_2del1_m`, `E_2del2_m`, `E_2del3_m`,
  `E_del1_del2_pp`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`,
  `E_del1_del3_pp`, `E_del1_del3_mm`, `E_del1_del3_pm`, `E_del1_del3_mp`,
  `E_del2_del3_pp`, `E_del2_del3_mm`, `E_del2_del3_pm`, `E_del2_del3_mp`
- **Odd basis (12)**:
  `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`,
  `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`,
  `E_eps1_del3_pp`, `E_eps1_del3_pm`, `E_eps1_del3_mp`, `E_eps1_del3_mm`

---

## 5. PBW Ordering Convention

The standard PBW ordering convention adopted for $C(n+1)$ is:

$$\kappa < [\text{Odd Generators}] < [\text{Even Generators}]$$

Specifically:
1. Odd generators are ordered lexicographically by bosonic index $k \in \{1, \ldots, n\}$, then by sign pair $(\mathrm{pp}, \mathrm{pm}, \mathrm{mp}, \mathrm{mm})$.
2. Even generators are ordered as:
   - Cartan generators $H_1, \ldots, H_{n+1}$,
   - Positive long root generators $E_{2\delta_k}^+$,
   - Negative long root generators $E_{2\delta_k}^-$,
   - Mixed root generators ordered by $(i,j)$ with $1 \leq i < j \leq n$ in order $(\mathrm{pp}, \mathrm{mm}, \mathrm{pm}, \mathrm{mp})$.
