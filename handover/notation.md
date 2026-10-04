# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project (Issue I01).

## 1. Superalgebra Identification

- **Algebra Family**: $C(n+1) = \mathfrak{osp}(2|2n)$.
- **Fermionic Rank**: $m = 1$.
- **Bosonic Rank**: $n \in \{1, 2, 3\}$ (corresponding to $C(2)$, $C(3)$, $C(4)$).
- **Dimension Formula**:
  - Even dimension: $\dim(\mathfrak{g}_{\bar{0}}) = 2n^2 + n + 1$ (subalgebra $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$).
  - Odd dimension: $\dim(\mathfrak{g}_{\bar{1}}) = 4n$.
  - Total dimension: $\dim(\mathfrak{g}) = 2n^2 + 5n + 1$.

| $n$ | Algebra | Even dim | Odd dim | Total dim |
|---|---|---|---|---|
| 1 | $C(2) = \mathfrak{osp}(2\|2)$ | 4 | 4 | 8 |
| 2 | $C(3) = \mathfrak{osp}(2\|4)$ | 11 | 8 | 19 |
| 3 | $C(4) = \mathfrak{osp}(2\|6)$ | 22 | 12 | 34 |

---

## 2. Oscillator Generators and Central Elements

### Oscillators
- **Standard Fermionic Pair** ($m=1$):
  - `a_1_p` ($a_1^+$): creation operator, parity $p(a_1^+) = 1$.
  - `a_1_m` ($a_1^-$): annihilation operator, parity $p(a_1^-) = 1$.
  - Canonical Anticommutation Relations (CAR):
    $$\{a_1^-, a_1^+\} = 1, \quad \{a_1^+, a_1^+\} = 0, \quad \{a_1^-, a_1^-\} = 0.$$
- **Bosonic Oscillators** ($k = 1, \ldots, n$):
  - `b_k_p` ($b_k^+$): creation operator, parity $p(b_k^+) = 0$.
  - `b_k_m` ($b_k^-$): annihilation operator, parity $p(b_k^-) = 0$.
  - Canonical Commutation Relations (CCR):
    $$[b_j^-, b_k^+] = \delta_{jk}, \quad [b_j^\pm, b_k^\pm] = 0.$$
- **Mixed Relations (Undeformed)**:
  $$[b_k^\pm, a_1^\pm] = 0.$$

### Central Elements
- `K`: Identity / central scaling element, parity $p(K) = 0$. Excluded from Lie algebra basis ($K = 1$).
- `kappa` ($\kappa$): Nilpotent odd central parameter, parity $p(\kappa) = 1$, $\kappa^2 = 0$. Parametrizes the inhomogeneous deformation.

---

## 3. Lie Superalgebra Basis and Generator Labels

### Even Generators ($\mathfrak{g}_{\bar{0}}$, Parity 0)
- **Cartan Generators**: $n+1$ generators:
  - `H_1`: $a_1^+ a_1^- + b_1^+ b_1^-$
  - `H_k` ($2 \le k \le n$): $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$
  - `H_{n+1}`: $-b_n^+ b_n^- - \frac{1}{2}$
- **Long Root Generators**:
  - `E_2del{k}_p` ($+2\delta_k$): $(b_k^+)^2$
  - `E_2del{k}_m` ($-2\delta_k$): $(b_k^-)^2$
- **Cross Root Generators** ($1 \le i < j \le n$):
  - `E_del{i}_del{j}_pp` ($+\delta_i + \delta_j$): $b_i^+ b_j^+$
  - `E_del{i}_del{j}_mm` ($-\delta_i - \delta_j$): $b_i^- b_j^-$
  - `E_del{i}_del{j}_pm` ($+\delta_i - \delta_j$): $b_i^+ b_j^-$
  - `E_del{i}_del{j}_mp` ($-\delta_i + \delta_j$): $b_i^- b_j^+$

### Odd Generators ($\mathfrak{g}_{\bar{1}}$, Parity 1)
For each $k \in \{1, \ldots, n\}$, four fermionic-bosonic bilinear generators:
- `E_eps1_del{k}_pp` ($+\varepsilon + \delta_k$): $a_1^+ b_k^+$
- `E_eps1_del{k}_pm` ($+\varepsilon - \delta_k$): $a_1^+ b_k^-$
- `E_eps1_del{k}_mp` ($-\varepsilon + \delta_k$): $a_1^- b_k^+$
- `E_eps1_del{k}_mm` ($-\varepsilon - \delta_k$): $a_1^- b_k^-$

---

## 4. PBW Ordering Conventions

### Ordering Rule
We adopt the **Parity-Split PBW Convention** (Odd-then-Even), consistent with the $B(0,n)$ base schema:
$$\kappa < [\mathfrak{g}_{\bar{1}} \text{ (odd)}] < [\mathfrak{g}_{\bar{0}} \text{ (even)}].$$

Within the odd and even sectors, the order is fixed as follows:
1. **Odd sector**: Ordered by bosonic index $k = 1, \ldots, n$, and within each $k$ by the sign profile `pp < pm < mp < mm`:
   $$\mathtt{E\_eps1\_del\{k\}\_pp} < \mathtt{E\_eps1\_del\{k\}\_pm} < \mathtt{E\_eps1\_del\{k\}\_mp} < \mathtt{E\_eps1\_del\{k\}\_mm}.$$
2. **Even sector**:
   - Cartan generators: $H_1 < H_2 < \cdots < H_{n+1}$.
   - Positive long roots: $\mathtt{E\_2del1\_p} < \cdots < \mathtt{E\_2deln\_p}$.
   - Positive cross roots (ordered lexicographically by $(i,j)$): $\mathtt{E\_del\{i\}\_del\{j\}\_pp}$.
   - Negative long roots: $\mathtt{E\_2del1\_m} < \cdots < \mathtt{E\_2deln\_m}$.
   - Negative cross roots (ordered lexicographically by $(i,j)$): $\mathtt{E\_del\{i\}\_del\{j\}\_mm}$.
   - Mixed cross roots (ordered lexicographically by $(i,j)$, with `pm` before `mp`): $\mathtt{E\_del\{i\}\_del\{j\}\_pm} < \mathtt{E\_del\{i\}\_del\{j\}\_mp}$.

### Rationale and Alternative Considered
- **Alternative Considered (Option 2: Triangular Root-Height Ordering)**:
  $E^- < H < E^+$. While standard in Lie algebra representation theory, this mixes even and odd generators throughout the list, breaking backward compatibility with the $B(0,n)$ schema architecture which explicitly separates `basis.even` and `basis.odd`.
- **Selected Rationale (Option 1)**:
  Preserves structural compatibility with the v5.0 JSON schema, provides natural stratification between the nilpotent Grassmann sector and the polynomial symmetric sector, and facilitates unambiguous indexing in matrix representations.

---

## 5. Concrete Basis Lists for $C(2)$, $C(3)$, $C(4)$

### $C(2)$ ($n=1$, Total dim = 8)
- **Even basis (4)**:
  `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- **Odd basis (4)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`

### $C(3)$ ($n=2$, Total dim = 19)
- **Even basis (11)**:
  `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd basis (8)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`

### $C(4)$ ($n=3$, Total dim = 34)
- **Even basis (22)**:
  `["H_1", "H_2", "H_3", "H_4", "E_2del1_p", "E_2del2_p", "E_2del3_p", "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp", "E_2del1_m", "E_2del2_m", "E_2del3_m", "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm", "E_del1_del2_pm", "E_del1_del2_mp", "E_del1_del3_pm", "E_del1_del3_mp", "E_del2_del3_pm", "E_del2_del3_mp"]`
- **Odd basis (12)**:
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm", "E_eps1_del3_pp", "E_eps1_del3_pm", "E_eps1_del3_mp", "E_eps1_del3_mm"]`
