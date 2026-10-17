# Notation and Terminology

This document defines the mathematical notation, generator labels, basis structures, and PBW ordering conventions used in this repository for the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension study.

---

## 1. Algebraic Setting & Oscillators

### 1.1 Oscillators
- **Bosonic oscillators**: $b_k^+, b_k^-$ for $k = 1, \ldots, n$.
  - Parity: $p(b_k^\pm) = 0$.
  - Canonical Commutation Relations (CCR):
    $$[b_j^-, b_k^+] = \delta_{jk}, \quad [b_j^\pm, b_k^\pm] = 0.$$
  - Labels in schema: `"b_{k}_p"`, `"b_{k}_m"`.
- **Standard fermionic pair**: $a_1^+, a_1^-$.
  - Parity: $p(a_1^\pm) = 1$.
  - Canonical Anticommutation Relations (CAR):
    $$\{a_1^-, a_1^+\} = 1, \quad (a_1^\pm)^2 = 0.$$
  - Labels in schema: `"a_1_p"`, `"a_1_m"`.
  - Replaces the supplementary fermion $a_0$ ($a_0^2 = 1/2$) used in $B(0,n)$.

### 1.2 Central Elements
- **$K$**: Even central identity element ($p(K) = 0$), identified with scalar 1. Excluded from PBW monomial basis.
- **$\kappa$**: Odd central nilpotent element ($p(\kappa) = 1, \kappa^2 = 0$), carrier of the inhomogeneous deformation.
  - PBW position: lowest non-trivial degree ($\kappa < [\text{odd}] < [\text{even}]$).

### 1.3 Deformation Parameters ($gb$)
- The inhomogeneous deformation modifies the mixed bracket:
  $$[b_j^s, a_1^\sigma] = - \mathrm{gb}_{\sigma, j, s} \cdot \kappa, \quad \sigma \in \{+, -\}, s \in \{+, -\}, j \in \{1, \ldots, n\}.$$
- There are $4n$ parity-1 parameters:
  $$\{\mathrm{gb}_{a_1^+, b_j^+}, \mathrm{gb}_{a_1^+, b_j^-}, \mathrm{gb}_{a_1^-, b_j^+}, \mathrm{gb}_{a_1^-, b_j^-} \mid j=1, \ldots, n\}.$$

---

## 2. Root System & Generator Labels

### 2.1 Superdimension
- Even subalgebra: $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$, $\dim \mathfrak{g}_{\bar{0}} = 2n^2 + n + 1$.
- Odd subspace: $\dim \mathfrak{g}_{\bar{1}} = 4n$.
- Total superdimension: $(2n^2 + n + 1) \mid 4n$, total dimension $= 2n^2 + 5n + 1$.

| $n$ | Algebra | even ($\mathfrak{g}_{\bar{0}}$) | odd ($\mathfrak{g}_{\bar{1}}$) | total |
|---|---|---|---|---|
| 1 | $C(2) = \mathfrak{osp}(2\|2)$ | 4 | 4 | 8 |
| 2 | $C(3) = \mathfrak{osp}(2\|4)$ | 11 | 8 | 19 |
| 3 | $C(4) = \mathfrak{osp}(2\|6)$ | 22 | 12 | 34 |

### 2.2 Cartan Generators ($n+1$ elements)
Coroots corresponding to the simple roots $\alpha_1 = \varepsilon - \delta_1$, $\alpha_k = \delta_{k-1} - \delta_k$ ($2 \le k \le n$), and $\alpha_{n+1} = 2\delta_n$:
- `H_1` $= a_1^+ a_1^- + b_1^+ b_1^-$
- `H_k` $= b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ ($2 \le k \le n$)
- `H_{n+1}` $= -b_n^+ b_n^- - \tfrac{1}{2}$

### 2.3 Even Root Generators ($\mathfrak{sp}(2n)$ Sector, $2n^2$ elements)
- **Long roots** $\pm 2\delta_k$ ($1 \le k \le n$):
  - `E_2del{k}_p` $\to (b_k^+)^2$ ($+2\delta_k$)
  - `E_2del{k}_m` $\to (b_k^-)^2$ ($-2\delta_k$)
- **Cross roots** $\pm \delta_i \pm \delta_j$ ($1 \le i < j \le n$):
  - `E_del{i}_del{j}_pp` $\to b_i^+ b_j^+$ ($+\delta_i + \delta_j$)
  - `E_del{i}_del{j}_pm` $\to b_i^+ b_j^-$ ($+\delta_i - \delta_j$)
  - `E_del{i}_del{j}_mp` $\to b_i^- b_j^+$ ($-\delta_i + \delta_j$)
  - `E_del{i}_del{j}_mm` $\to b_i^- b_j^-$ ($-\delta_i - \delta_j$)

### 2.4 Odd Root Generators ($4n$ elements)
Following the specification in `docs/math/B0n_schema_v5.md` with explicit `eps1` label:
- Roots $\pm \varepsilon \pm \delta_k$ ($1 \le k \le n$):
  - `E_eps1_del{k}_pp` $\to a_1^+ b_k^+$ ($+\varepsilon + \delta_k$)
  - `E_eps1_del{k}_pm` $\to a_1^+ b_k^-$ ($+\varepsilon - \delta_k$)
  - `E_eps1_del{k}_mp` $\to a_1^- b_k^+$ ($-\varepsilon + \delta_k$)
  - `E_eps1_del{k}_mm` $\to a_1^- b_k^-$ ($-\varepsilon - \delta_k$)

---

## 3. PBW Ordering Convention

The global PBW monomial ordering follows the charge-stratified convention (Option 1, extending $B(0,n)$):

$$\kappa < [\text{odd}] < [\text{even}]$$

### 3.1 Odd Stratum Ordering
Odd generators are ordered by $(\varepsilon, \delta)$ charge blocks ($++, +-, -+, --$), and by index $k = 1, \ldots, n$ within each block:
```
[E_eps1_del1_pp, ..., E_eps1_deln_pp]
< [E_eps1_del1_pm, ..., E_eps1_deln_pm]
< [E_eps1_del1_mp, ..., E_eps1_deln_mp]
< [E_eps1_del1_mm, ..., E_eps1_deln_mm]
```

### 3.2 Even Stratum Ordering
Even generators are ordered by Cartans, positive long roots, positive cross roots, negative long roots, negative cross roots, and mixed cross roots:
```
[H_1, ..., H_{n+1}]
< [E_2del1_p, ..., E_2deln_p]
< [E_del{i}_del{j}_pp (1 <= i < j <= n)]
< [E_2del1_m, ..., E_2deln_m]
< [E_del{i}_del{j}_mm (1 <= i < j <= n)]
< [E_del{i}_del{j}_pm, E_del{i}_del{j}_mp (1 <= i < j <= n)]
```

---

## 4. Concrete Basis Lists ($n=1, 2, 3$)

### 4.1 $C(2) = \mathfrak{osp}(2|2)$ ($n=1$)
- **Even basis (dim 4)**:
  ```json
  [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m"
  ]
  ```
- **Odd basis (dim 4)**:
  ```json
  [
    "E_eps1_del1_pp",
    "E_eps1_del1_pm",
    "E_eps1_del1_mp",
    "E_eps1_del1_mm"
  ]
  ```

### 4.2 $C(3) = \mathfrak{osp}(2|4)$ ($n=2$)
- **Even basis (dim 11)**:
  ```json
  [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ]
  ```
- **Odd basis (dim 8)**:
  ```json
  [
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ]
  ```

### 4.3 $C(4) = \mathfrak{osp}(2|6)$ ($n=3$)
- **Even basis (dim 22)**:
  ```json
  [
    "H_1", "H_2", "H_3", "H_4",
    "E_2del1_p", "E_2del2_p", "E_2del3_p",
    "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp",
    "E_2del1_m", "E_2del2_m", "E_2del3_m",
    "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm",
    "E_del1_del2_pm", "E_del1_del2_mp",
    "E_del1_del3_pm", "E_del1_del3_mp",
    "E_del2_del3_pm", "E_del2_del3_mp"
  ]
  ```
- **Odd basis (dim 12)**:
  ```json
  [
    "E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"
  ]
  ```
