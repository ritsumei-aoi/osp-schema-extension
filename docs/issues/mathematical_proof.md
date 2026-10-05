# Mathematical Proof: Triviality Conditions for C(n+1) Inhomogeneous Deformations

## 1. Statement of the Theorem

**Theorem.** For the Lie superalgebra $\mathfrak{g} = C(n+1) \cong \mathfrak{osp}(2|2n)$ with $n = 1, 2, 3$, the inhomogeneous deformation $\gamma_{gb}$ is trivial — i.e., there exists an odd linear map $f: \mathfrak{g} \to \mathfrak{g}$ such that $\gamma_{gb} = \delta f$ in the adjoint representation — **if and only if** all deformation parameters vanish:

$$
\mathrm{gb}_{\sigma, j, s} = 0 \quad \text{for all } \sigma \in \{+, -\},\ j \in \{1, \ldots, n\},\ s \in \{+, -\}.
$$

Equivalently, every non-zero inhomogeneous deformation of $C(n+1)$ defines a non-trivial cohomology class in $H^2(\mathfrak{g}, \mathfrak{g})$.

---

## 2. Setup and Definitions

### 2.1 The Lie Superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$

The algebra is realized via oscillators:
- **Fermionic pair** $a_1^{\pm}$: $\{a_1^-, a_1^+\} = 1$, parity $p(a_1^{\pm}) = 1$.
- **Bosonic oscillators** $b_k^{\pm}$ ($k = 1, \ldots, n$): $[b_k^-, b_l^+] = \delta_{kl}$, parity $p(b_k^{\pm}) = 0$.

The generators are bilinears in oscillators:

| Generator | Expression | Parity |
|-----------|-----------|--------|
| $H_1$ | $a_1^+ a_1^- + b_1^+ b_1^-$ | 0 |
| $H_k$ ($2 \leq k \leq n$) | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ | 0 |
| $H_{n+1}$ | $-b_n^+ b_n^- - \tfrac{1}{2}$ | 0 |
| $E_{\pm 2\delta_k}$ | $(b_k^{\pm})^2 / 2$ | 0 |
| $E_{\delta_k - \delta_l}$ ($k \neq l$) | $b_k^+ b_l^-$ | 0 |
| $E_{\delta_k + \delta_l}$ ($k < l$) | $b_k^+ b_l^+$ | 0 |
| $E_{-\delta_k - \delta_l}$ ($k < l$) | $b_k^- b_l^-$ | 0 |
| $E_{\varepsilon + \delta_k}$ | $a_1^+ b_k^+$ | 1 |
| $E_{\varepsilon - \delta_k}$ | $a_1^+ b_k^-$ | 1 |
| $E_{-\varepsilon + \delta_k}$ | $a_1^- b_k^+$ | 1 |
| $E_{-\varepsilon - \delta_k}$ | $a_1^- b_k^-$ | 1 |

Total dimension: $\dim(\mathfrak{g}) = 2n^2 + 5n + 1$ ($= 8, 19, 34$ for $n = 1, 2, 3$).

### 2.2 The Inhomogeneous Deformation $\gamma_{gb}$

The deformation modifies the mixed oscillator relations:
$$
[b_j^s, a_1^{\sigma}] = -\mathrm{gb}_{\sigma, j, s} \cdot \kappa
$$
where $\kappa$ is an odd central element. This induces a 2-cocycle $\gamma_{gb}: \mathfrak{g} \otimes \mathfrak{g} \to \mathfrak{g}$ defined by:
$$
[X, Y]_{\gamma} = [X, Y]_0 + \kappa \cdot \gamma_{gb}(X, Y).
$$

The cocycle $\gamma_{gb}$ is computed via the **Leibniz expansion** of the bracket of bilinear generators. For generators $Z_i = x_1 x_2$ and $Z_j = y_1 y_2$:
$$
[x_1 x_2, y_1 y_2] = x_1[x_2, y_1] y_2 + (-1)^{p_2 p_3} x_1 y_1 [x_2, y_2] + (-1)^{p_2(p_3+p_4)} [x_1, y_1] y_2 x_2 + (-1)^{p_2(p_3+p_4)+p_1 p_3} y_1 [x_1, y_2] x_2
$$
The $\kappa$-linear corrections arise when one of the four contractions $[x_a, y_b]$ is the deformed $[b_j^s, a_1^{\sigma}] = -\mathrm{gb}\cdot\kappa$.

### 2.3 The Coboundary Operator $\delta f$

For an odd linear map $f: \mathfrak{g} \to \mathfrak{g}$ with $f(Z_j) = \sum_m \phi_j^m Z_m$:
$$
(\delta f)(Z_i, Z_j) = (-1)^{p_i} [Z_i, f(Z_j)] - (-1)^{(p_i+1)p_j} [Z_j, f(Z_i)] - f([Z_i, Z_j])
$$

In components:
$$
(\delta f)_{ij}^k = (-1)^{p_i} \sum_m c_{im}^k \phi_j^m - (-1)^{(p_i+1)p_j} \sum_m c_{jm}^k \phi_i^m - \sum_l c_{ij}^l \phi_l^k
$$
where $c_{ij}^k$ are the structure constants.

### 2.4 The "Adjoint Representation / Up to Scalar" Condition

Since $C(n+1)$ is realized as a subalgebra of $\mathcal{U}(A)$ via the adjoint representation, elements differing by a scalar (multiple of the identity) act identically. The triviality condition $\gamma_{gb} = \delta f$ is therefore imposed **modulo scalars**:
$$
\gamma_{gb}(X, Y) \equiv (\delta f)(X, Y) \pmod{\mathbb{C} \cdot \mathrm{Id}}
$$

**Treatment in our computation**: The structure constants $c_{ij}^k$ capture only the $\mathfrak{g}$-component of brackets (the scalar part is tracked separately but not included in the triviality equations). The $\gamma_{gb}$ cocycle is similarly decomposed into its $\mathfrak{g}$-valued part and a scalar part. Only the $\mathfrak{g}$-valued parts enter the linear system $\gamma = \delta f$. This correctly implements the "up to scalar" condition, since scalar differences are automatically absorbed.

---

## 3. Computational Method

### 3.1 Structure Constants

For each pair of generators $(Z_i, Z_j)$, we compute $[Z_i, Z_j]$ using the Leibniz expansion of bilinear products. Each bracket is decomposed into the generator basis by solving against the **design matrix** $D$, where $D_{\beta, k}$ is the coefficient of bilinear $\beta$ in generator $Z_k$. The design matrix has full rank (equal to $\dim(\mathfrak{g})$), confirming that the generators form a proper basis.

**Verification**: Zero antisymmetry violations were found in all three cases.

### 3.2 Gamma Cocycle

For each of the $4n$ basis deformation parameters $\mathrm{gb}_{\sigma, j, s}$, we compute $\gamma^{(\sigma,j,s)}(Z_i, Z_j)$ by replacing the zero undeformed commutator $[b_j^s, a_1^{\sigma}]_0 = 0$ with the deformed value $-1$ (the $\kappa$-coefficient) in the Leibniz expansion, and collecting the resulting bilinear.

### 3.3 Linear System

The triviality condition becomes a linear system:
$$
A \cdot \vec{\phi} = \vec{b}(\mathrm{gb})
$$
where:
- $A$ is the **coboundary matrix** (depends only on structure constants)
- $\vec{\phi}$ contains the parameters of $f$ (restricted to parity-changing components)
- $\vec{b}(\mathrm{gb}) = \sum_p \mathrm{gb}_p \cdot \vec{\gamma}^{(p)}$ is the gamma vector

The triviality of $\gamma_{gb}$ requires $\vec{b}(\mathrm{gb}) \in \mathrm{Col}(A)$.

---

## 4. Results

### 4.1 Dimensional Analysis

| Algebra | $\dim(\mathfrak{g})$ | $\#\text{gb params}$ | $\#\phi$ unknowns | $\mathrm{rank}(A)$ | $\mathrm{rank}([A \mid \Gamma])$ | Gap |
|---------|-----|------|------|---------|---------|-----|
| $C(2)$ | 8 | 4 | 32 | 28 | 32 | **4** |
| $C(3)$ | 19 | 8 | 176 | 168 | 176 | **8** |
| $C(4)$ | 34 | 12 | 528 | 516 | 528 | **12** |

In every case, the rank gap equals exactly $4n$, the number of deformation parameters.

### 4.2 Interpretation

The gamma cocycle matrix $\Gamma$ (whose columns are $\vec{\gamma}^{(p)}$ for each gb parameter) has all $4n$ columns linearly independent from the column space of the coboundary matrix $A$. This means:

$$
\mathrm{Col}(\Gamma) \cap \mathrm{Col}(A) = \{0\}
$$

Therefore, the **only** $\mathrm{gb}$ vector satisfying $\Gamma \cdot \mathrm{gb} \in \mathrm{Col}(A)$ is $\mathrm{gb} = 0$.

### 4.3 Explicit Constraints

The SVD analysis yields exactly $4n$ independent constraints on gb, each of the form:
$$
\mathrm{gb}_{\sigma, j, s} = 0
$$
for each individual parameter. No non-trivial linear combinations of gb parameters can produce a coboundary.

---

## 5. Proof of the Theorem

**Proof.** We proceed in two directions.

**($\Leftarrow$)** If $\mathrm{gb} = 0$, then $\gamma_{gb} = 0 = \delta(0)$, which is trivially a coboundary.

**($\Rightarrow$)** Suppose $\gamma_{gb} = \delta f$ for some odd linear map $f: \mathfrak{g} \to \mathfrak{g}$. Writing $\gamma_{gb} = \sum_{p=1}^{4n} \mathrm{gb}_p \cdot \gamma^{(p)}$, the triviality condition in component form is:
$$
\sum_p \mathrm{gb}_p \cdot \gamma^{(p)}_{ij}{}^k = (\delta f)_{ij}^k \quad \text{for all } i, j, k.
$$

This is the linear system $A \vec{\phi} = \Gamma \vec{\mathrm{gb}}$, which has a solution $\vec{\phi}$ if and only if $\Gamma \vec{\mathrm{gb}} \in \mathrm{Col}(A)$.

By direct computation (verified for $n = 1, 2, 3$):
$$
\mathrm{rank}([A \mid \Gamma]) - \mathrm{rank}(A) = 4n
$$

This means all $4n$ columns of $\Gamma$ are linearly independent modulo $\mathrm{Col}(A)$. Projecting $\Gamma$ onto the orthogonal complement of $\mathrm{Col}(A)$ via the SVD $A = U S V^T$, we obtain:
$$
\Pi_{\perp} \Gamma = U_{\perp}^T \Gamma
$$
where $U_{\perp}$ spans $\mathrm{Col}(A)^{\perp}$. This projected matrix has rank $4n$, and the condition $\Pi_{\perp} \Gamma \cdot \vec{\mathrm{gb}} = 0$ has only the trivial solution $\vec{\mathrm{gb}} = 0$.

Therefore $\gamma_{gb} = \delta f$ implies $\mathrm{gb} = 0$. $\square$

---

## 6. Cohomological Significance

The result establishes that the $4n$-dimensional space of inhomogeneous deformations injects into the second cohomology:
$$
\mathrm{span}\{\gamma^{(\sigma,j,s)}\} \hookrightarrow H^2(\mathfrak{g}, \mathfrak{g})
$$

This means $\dim H^2(\mathfrak{g}, \mathfrak{g}) \geq 4n$ for $\mathfrak{g} = C(n+1)$.

The non-triviality of all inhomogeneous deformations is consistent with the known fact that for type I basic classical Lie superalgebras (where $C(n+1)$ belongs), the Whitehead-type vanishing theorem for $H^2(\mathfrak{g}, \mathfrak{g})$ does **not** hold in general, unlike the classical Lie algebra case.

### 6.1 Role of the $\mathfrak{so}(2)$ Factor

The even subalgebra $\mathfrak{g}_{\bar{0}} = \mathfrak{so}(2) \times \mathfrak{sp}(2n)$ has a one-dimensional $\mathfrak{so}(2)$ factor generated (in the oscillator realization) by the fermion number operator. The $\mathfrak{so}(2)$ charge distinguishes the odd generators $E_{\varepsilon \pm \delta_k}$ (charge $+1$) from $E_{-\varepsilon \pm \delta_k}$ (charge $-1$). The deformation parameters $\mathrm{gb}_{\sigma, j, s}$ couple oscillators across this charge grading, and the resulting cocycles cannot be unwound by any coboundary — this reflects a genuine obstruction in the $\mathfrak{so}(2)$-graded cohomology.

---

## 7. Computational Artifacts

All computations are implemented in `compute_triviality.py` and the structured verification data is exported to `verification_artifacts.json`. The artifacts contain:

1. **Structure constants** $c_{ij}^k$ for $C(n+1)$, $n = 1, 2, 3$ (as sparse dictionaries).
2. **Gamma cocycle** $\gamma^{(p)}_{ij}{}^k$ for each gb parameter $p$ (as sparse dictionaries).
3. **Scalar parts** of both brackets and gamma (tracked separately for the "up to scalar" analysis).
4. **Triviality results**: ranks, residuals, and constraints.

### 7.1 Sample Verification Data (C(2), n=1)

Structure constants (non-zero, $i \leq j$):

```
[H_1, E_{2δ}]   = 2 E_{2δ}
[H_1, E_{-2δ}]  = -2 E_{-2δ}
[H_1, E_{ε+δ}]  = 2 E_{ε+δ}
[H_1, E_{-ε-δ}] = -2 E_{-ε-δ}
[H_2, E_{2δ}]   = -2 E_{2δ}
[H_2, E_{-2δ}]  = 2 E_{-2δ}
[H_2, E_{ε+δ}]  = -E_{ε+δ}
[H_2, E_{ε-δ}]  = E_{ε-δ}
[H_2, E_{-ε+δ}] = -E_{-ε+δ}
[H_2, E_{-ε-δ}] = E_{-ε-δ}
[E_{2δ}, E_{-2δ}]   = H_2      (+ scalar -1/2)
[E_{2δ}, E_{ε-δ}]   = -E_{ε+δ}
[E_{2δ}, E_{-ε-δ}]  = -E_{-ε+δ}
[E_{-2δ}, E_{ε+δ}]  = E_{ε-δ}
[E_{-2δ}, E_{-ε+δ}] = E_{-ε-δ}
{E_{ε+δ}, E_{-ε+δ}} = 2 E_{2δ}
{E_{ε+δ}, E_{-ε-δ}} = -H_1 - 2H_2  (+ scalar 1)
{E_{ε-δ}, E_{-ε+δ}} = H_1
{E_{ε-δ}, E_{-ε-δ}} = 2 E_{-2δ}
```

### 7.2 Reproducibility

```python
# To verify the results independently:
import json
with open('verification_artifacts.json') as f:
    data = json.load(f)

# Check C(2) triviality
assert data['C(2)']['triviality']['all_trivial'] == False
assert data['C(2)']['triviality']['rank_delta'] == 28
assert data['C(2)']['triviality']['rank_delta_plus_gamma'] == 32

# Check C(3) triviality
assert data['C(3)']['triviality']['all_trivial'] == False
assert data['C(3)']['triviality']['rank_delta'] == 168
assert data['C(3)']['triviality']['rank_delta_plus_gamma'] == 176

# Check C(4) triviality
assert data['C(4)']['triviality']['all_trivial'] == False
assert data['C(4)']['triviality']['rank_delta'] == 516
assert data['C(4)']['triviality']['rank_delta_plus_gamma'] == 528
```

---

## 8. Conclusion

For $C(n+1) = \mathfrak{osp}(2|2n)$ with $n = 1, 2, 3$:

> **The inhomogeneous deformation $\gamma_{gb}$ is trivial if and only if $\mathrm{gb} = 0$.**

All $4n$ deformation parameters contribute independent non-trivial cohomology classes. The rank gap $\mathrm{rank}([A|\Gamma]) - \mathrm{rank}(A) = 4n$ is exact and equals the number of deformation parameters, proving that no non-zero linear combination of the basis cocycles is a coboundary.

This contrasts with the classical Lie algebra setting where Whitehead's second lemma guarantees $H^2(\mathfrak{g}, \mathfrak{g}) = 0$, and demonstrates a fundamental difference in the deformation theory of Lie superalgebras.
