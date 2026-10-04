# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository for the $C(n+1) = \mathfrak{osp}(2|2n)$ Lie superalgebra schema extension project.

---

## 1. Lie Superalgebra Parameters & Superdimension

For the $C(n+1) = \mathfrak{osp}(2|2n)$ family:
- $m = 1$ (fermionic rank)
- $n \in \{1, 2, 3, \ldots\}$ (bosonic rank)
- Superdimension:
  $$\dim(\mathfrak{g}) = (2n^2 + n + 1) \mid 4n$$
  $$\dim_{\text{total}} = 2n^2 + 5n + 1$$
- Even subalgebra: $\mathfrak{g}_{\bar{0}} \cong \mathfrak{so}(2) \oplus \mathfrak{sp}(2n)$ of dimension $2n^2 + n + 1$.
- Odd subspace: $\mathfrak{g}_{\bar{1}}$ of dimension $4n$.

| $n$ | Cartan Type | Algebra | Even Dim ($2n^2+n+1$) | Odd Dim ($4n$) | Total Dim ($2n^2+5n+1$) |
|---|---|---|---|---|---|
| 1 | $C(2)$ | $\mathfrak{osp}(2\|2)$ | 4 | 4 | 8 |
| 2 | $C(3)$ | $\mathfrak{osp}(2\|4)$ | 11 | 8 | 19 |
| 3 | $C(4)$ | $\mathfrak{osp}(2\|6)$ | 22 | 12 | 34 |

---

## 2. Oscillator Generators and Relations

### 2.1 Generators
- **Standard Fermionic Pair**: $a_1^+, a_1^-$
  - Parity: $p(a_1^+) = 1$, $p(a_1^-) = 1$
  - Labels in schema: `a_1_p`, `a_1_m`
- **Bosonic Oscillators**: $b_k^+, b_k^-$ for $k = 1, \ldots, n$
  - Parity: $p(b_k^+) = 0$, $p(b_k^-) = 0$
  - Labels in schema: `b_k_p`, `b_k_m`

### 2.2 Canonical (Anti-)Commutation Relations
- Canonical Anticommutation Relations (CAR) for fermions:
  $$\{a_1^-, a_1^+\} = a_1^- a_1^+ + a_1^+ a_1^- = 1, \quad \{a_1^+, a_1^+\} = 2(a_1^+)^2 = 0, \quad \{a_1^-, a_1^-\} = 2(a_1^-)^2 = 0$$
- Canonical Commutation Relations (CCR) for bosons:
  $$[b_j^-, b_k^+] = b_j^- b_k^+ - b_k^+ b_j^- = \delta_{jk}, \quad [b_j^+, b_k^+] = 0, \quad [b_j^-, b_k^-] = 0$$
- Mixed Commutators (undeformed):
  $$[b_k^\pm, a_1^\pm] = 0$$

### 2.3 Central Elements
- $\kappa$: Odd central element ($p(\kappa) = 1$, $\kappa^2 = 0$) used for the formal nilpotent deformation.
- $K$: Even central identity ($p(K) = 0$, $K = 1$).

---

## 3. PBW Ordering Conventions

We considered two candidate PBW ordering strategies:

1. **Option A (Graded Block Ordering - Adopted)**:
   $$\kappa < [\text{odd generators}] < [\text{even generators}]$$
   Specifically:
   $$\kappa < E_{\varepsilon \pm \delta_k} < E_{-\varepsilon \pm \delta_k} < H_1 \ldots H_{n+1} < E_{\text{even roots}}$$
   - **Rationale**: Preserves exact compatibility with the $B(0,n)$ v5.0 schema convention (`κ < [odd] < [even]`), cleanly separates odd and even subspaces in matrix and tensor indexing, and simplifies verification of graded skew-symmetry and Jacobi identities.

2. **Option B (Triangular / Root-Height Ordering - Alternative)**:
   $$\kappa < [\text{negative roots}] < [\text{Cartan generators}] < [\text{positive roots}]$$
   - **Rationale**: Natural in representation theory (Verma modules, triangular decomposition $\mathfrak{n}^- \oplus \mathfrak{h} \oplus \mathfrak{n}^+$), but mixes parity within blocks, increasing complexity of parity-graded tensor data serialization.

**Decision**: Adopt **Option A**.

---

## 4. Generator Labels and Oscillator Realizations

### 4.1 Even Generators ($\mathfrak{g}_{\bar{0}}$)
- **Cartan Subalgebra** ($n+1$ generators):
  - $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$ (`H_1`)
  - $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ (`H_k` for $2 \leq k \leq n$)
  - $H_{n+1} = -b_n^+ b_n^- - \tfrac{1}{2}$ (`H_{n+1}`)
- **Long Root Vectors** ($2n$ generators):
  - $E_{2\delta_k} = (b_k^+)^2$ (`E_2del{k}_p`)
  - $E_{-2\delta_k} = (b_k^-)^2$ (`E_2del{k}_m`)
- **Short Even Root Vectors** ($2n(n-1)$ generators, for $1 \leq i < j \leq n$):
  - $E_{\delta_i + \delta_j} = b_i^+ b_j^+$ (`E_del{i}_del{j}_pp`)
  - $E_{-\delta_i - \delta_j} = b_i^- b_j^-$ (`E_del{i}_del{j}_mm`)
  - $E_{\delta_i - \delta_j} = b_i^+ b_j^-$ (`E_del{i}_del{j}_pm`)
  - $E_{-\delta_i + \delta_j} = b_i^- b_j^+$ (`E_del{i}_del{j}_mp`)

### 4.2 Odd Generators ($\mathfrak{g}_{\bar{1}}$, $4n$ generators)
For $k = 1, \ldots, n$:
- $E_{\varepsilon + \delta_k} = a_1^+ b_k^+$ (`E_eps1_del{k}_pp`)
- $E_{\varepsilon - \delta_k} = a_1^+ b_k^-$ (`E_eps1_del{k}_pm`)
- $E_{-\varepsilon + \delta_k} = a_1^- b_k^+$ (`E_eps1_del{k}_mp`)
- $E_{-\varepsilon - \delta_k} = a_1^- b_k^-$ (`E_eps1_del{k}_mm`)

---

## 5. Basis Lists for $n=1, 2, 3$

### 5.1 $C(2) = \mathfrak{osp}(2|2)$ ($n=1$)
- **Even Basis** (4):
  `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- **Odd Basis** (4):
  `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`
- **Total Dimension**: $4 + 4 = 8$.

### 5.2 $C(3) = \mathfrak{osp}(2|4)$ ($n=2$)
- **Even Basis** (11):
  `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd Basis** (8):
  `["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del1_mm", "E_eps1_del2_mm"]`
- **Total Dimension**: $11 + 8 = 19$.

### 5.3 $C(4) = \mathfrak{osp}(2|6)$ ($n=3$)
- **Even Basis** (22):
  `["H_1", "H_2", "H_3", "H_4", "E_2del1_p", "E_2del2_p", "E_2del3_p", "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp", "E_2del1_m", "E_2del2_m", "E_2del3_m", "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm", "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm", "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"]`
- **Odd Basis** (12):
  `["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp", "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm", "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp", "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"]`
- **Total Dimension**: $22 + 12 = 34$.

---

## 6. Inhomogeneous Deformation Parameters ($gb$)

The deformation of the oscillator algebra by $\kappa$ introduces $4n$ parity-1 parameters:
$$\{ \mathrm{gb}_{a_1^+, b_k^+}, \mathrm{gb}_{a_1^+, b_k^-}, \mathrm{gb}_{a_1^-, b_k^+}, \mathrm{gb}_{a_1^-, b_k^-} \mid k = 1, \ldots, n \}$$
Represented in the $2 \times 2n$ $gb$-matrix:
$$\mathrm{gb} = \begin{pmatrix} \mathrm{gb}_{a_1^+, b_1^+} & \mathrm{gb}_{a_1^+, b_1^-} & \cdots & \mathrm{gb}_{a_1^+, b_n^+} & \mathrm{gb}_{a_1^+, b_n^-} \\ \mathrm{gb}_{a_1^-, b_1^+} & \mathrm{gb}_{a_1^-, b_1^-} & \cdots & \mathrm{gb}_{a_1^-, b_n^+} & \mathrm{gb}_{a_1^-, b_n^-} \end{pmatrix}$$
