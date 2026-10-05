# Mathematical Analysis & Definitive Proof: Triviality Conditions for Inhomogeneous Deformations of $C(n+1) = \mathfrak{osp}(2|2n)$

**Author**: Independent Pure Mathematics Researcher  
**Date**: October 5, 2026  
**Status**: Closed / Resolved  
**Target Algebra**: Lie Superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$ for $n \ge 1$  
**Computational Artifacts**: [verification_results.json](file:///Users/aoi/notebook/git/thm01-R-batch/thm01-R-gemini36f-b14-C/artifacts/verification_results.json), [verify_cn_triviality.py](file:///Users/aoi/notebook/git/thm01-R-batch/thm01-R-gemini36f-b14-C/scripts/verify_cn_triviality.py)

---

## Executive Summary & Main Theorem

This document presents the complete theoretical derivation and computational verification determining the triviality conditions for the inhomogeneous $gb$ deformation of the Lie superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$.

> **Main Theorem**:  
> *The inhomogeneous deformation $\gamma_{gb}$ of the Lie superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$ is **trivial** (i.e., a coboundary $\gamma_{gb} = \delta f$ for some odd linear map $f: \mathfrak{g} \to \mathfrak{g}$) **if and only if** all deformation parameters vanish:*
> $$ \mathrm{gb}_{\sigma, j, s} = 0 \quad \text{for all } \sigma \in \{+, -\},\ j \in \{1, \ldots, n\},\ s \in \{+, -\}. $$
> *Consequently, any non-zero parameter vector $\mathrm{gb} \neq 0$ defines a **strictly non-trivial** deformation, generating a non-zero cohomology class in $H^2(\mathfrak{g}, \mathfrak{g})$.*

---

## 1. Mathematical Framework & Basis Realization

### 1.1 Root System & Superdimension
The Lie superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$ has even subalgebra $\mathfrak{g}_{\bar{0}} = \mathfrak{so}(2) \oplus \mathfrak{sp}(2n)$ and odd subspace $\mathfrak{g}_{\bar{1}} \cong V_{+1} \oplus V_{-1}$.
- **Even dimension**: $\dim(\mathfrak{g}_{\bar{0}}) = 2n^2 + n + 1$
- **Odd dimension**: $\dim(\mathfrak{g}_{\bar{1}}) = 4n$
- **Total dimension**: $\dim(\mathfrak{g}) = 2n^2 + 5n + 1$

| $n$ | Algebra | Even Dim | Odd Dim | Total Dim | Deformation Params ($4n$) |
|---|---|---|---|---|---|
| $n=1$ | $C(2) = \mathfrak{osp}(2\|2)$ | 4 | 4 | 8 | 4 |
| $n=2$ | $C(3) = \mathfrak{osp}(2\|4)$ | 11 | 8 | 19 | 8 |
| $n=3$ | $C(4) = \mathfrak{osp}(2\|6)$ | 22 | 12 | 34 | 12 |

### 1.2 Oscillator Basis
Following [Cn1_definition.md](file:///Users/aoi/notebook/git/thm01-R-batch/thm01-R-gemini36f-b14-C/docs/math/Cn1_definition.md), $C(n+1)$ is realized using:
1. **Fermionic Pair**: $a_1^+, a_1^-$ with $\{a_1^-, a_1^+\} = 1$, $(a_1^+)^2 = (a_1^-)^2 = 0$.
2. **Bosonic Oscillators**: $b_j^+, b_j^-$ ($j = 1, \ldots, n$) with $[b_j^-, b_k^+] = \delta_{jk}$, $[b_j^+, b_k^+] = [b_j^-, b_k^-] = 0$.

The basis elements of $\mathfrak{g}$ are explicit operator combinations:
- **Even Basis $\mathfrak{g}_{\bar{0}}$**:
  - $H_0 = a_1^+ a_1^-$ (spans $\mathfrak{so}(2)$).
  - $B_{j,k}^{++} = b_j^+ b_k^+$ ($1 \le j \le k \le n$).
  - $B_{j,k}^{--} = b_j^- b_k^-$ ($1 \le j \le k \le n$).
  - $B_{j,k}^{+-} = b_j^+ b_k^-$ ($1 \le j, k \le n$).
- **Odd Basis $\mathfrak{g}_{\bar{1}}$**:
  - $F_{j, s}^{\sigma} = a_1^\sigma b_j^s$ ($\sigma \in \{+, -\}, s \in \{+, -\}, j \in \{1, \dots, n\}$).

---

## 2. Theoretical Handling of "Adjoint Representation / Up to Scalar"

In pre-oscillator extension $A = V \oplus \mathbf{C}K \oplus \mathbf{C}\kappa$, the identity operator $1$ and central elements $K, \kappa$ are central in $\mathcal{U}(A)$.
When $\mathfrak{g}$ acts on itself via the **adjoint representation**:
$$ \mathrm{ad}_X(Y) = [X, Y] = X Y - (-1)^{p(X)p(Y)} Y X, $$
any central scalar multiple $c \cdot 1$ acts as zero ($[c \cdot 1, Y] = 0$).

Specifically, in evaluating brackets:
1. $a_1^- a_1^+ = 1 - a_1^+ a_1^- = 1 - H_0 \equiv -H_0 \pmod{\mathrm{scalars}}$.
2. Bosonic commutators $[b_j^-, b_j^+] = 1 \equiv 0 \pmod{\mathrm{scalars}}$.

Thus, all 2-cocycles $\gamma_{gb}$ and coboundaries $\delta f$ are evaluated in the quotient Lie superalgebra $\mathfrak{g} \cong \mathcal{U}(A)_{\text{quad}} / \mathbf{C}\mathbf{1}$, where equivalence up to scalar coincides with identity in the adjoint representation.

---

## 3. The Deformation 2-Cocycle $\gamma_{gb}$

Following [C_inhomogeneous_definition.md](file:///Users/aoi/notebook/git/thm01-R-batch/thm01-R-gemini36f-b14-C/docs/math/C_inhomogeneous_definition.md), the deformed bracket is $[X, Y]_\gamma = [X, Y]_0 + \kappa \cdot \gamma_{gb}(X, Y)$, where $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma, j, s} \kappa$.

Evaluating the bracket in the deformed oscillator algebra yields the explicit 2-cocycle $\gamma_{gb}(X, Y)$:

1. **Even-Even Pairs**:
   $$ \gamma_{gb}(E_1, E_2) = 0 \quad \forall E_1, E_2 \in \mathfrak{g}_{\bar{0}}. $$

2. **Even-Odd Pairs**:
   - For $H_0 = a_1^+ a_1^-$:
     $$ \gamma_{gb}(H_0, a_1^\sigma b_l^u) = \sigma \mathrm{gb}_{\sigma, l, u} H_0. $$
   - For bosonic bilinears $E = b_j^s b_k^t$:
     $$ \gamma_{gb}(b_j^s b_k^t, a_1^\sigma b_l^u) = - \mathrm{gb}_{\sigma, j, s} b_k^t b_l^u - \mathrm{gb}_{\sigma, k, t} b_j^s b_l^u \quad \in \mathfrak{g}_{\bar{0}}. $$

3. **Odd-Odd Pairs**:
   $$ \gamma_{gb}(a_1^\sigma b_j^s, a_1^\tau b_k^t) = - \mathrm{gb}_{\tau, j, s} (a_1^\sigma b_k^t) - \mathrm{gb}_{\sigma, k, t} (a_1^\tau b_j^s) \quad \in \mathfrak{g}_{\bar{1}}. $$

---

## 4. Analytical Proof of the Main Theorem for All $n \ge 1$

Suppose $\gamma_{gb} = \delta f$ for an odd linear map $f: \mathfrak{g} \to \mathfrak{g}$.

### Step 1: Vanishing 1-Cohomology $H^1(\mathfrak{g}_{\bar{0}}, \mathfrak{g}_{\bar{1}}) = 0$
For $E_1, E_2 \in \mathfrak{g}_{\bar{0}}$, $\gamma_{gb}(E_1, E_2) = 0$. The coboundary equation gives:
$$ (\delta f)(E_1, E_2) = [E_1, f(E_2)] - [E_2, f(E_1)] - f([E_1, E_2]) = 0. $$
This means $f|_{\mathfrak{g}_{\bar{0}}}: \mathfrak{g}_{\bar{0}} \to \mathfrak{g}_{\bar{1}}$ is a 1-cocycle in Lie algebra cohomology $H^1(\mathfrak{g}_{\bar{0}}, \mathfrak{g}_{\bar{1}})$.

Since $\mathfrak{g}_{\bar{0}} = \mathfrak{so}(2) \oplus \mathfrak{sp}(2n)$ and $\mathfrak{g}_{\bar{1}} \cong V_{+1} \oplus V_{-1}$:
- $\mathfrak{sp}(2n)$ is semisimple $\implies H^1(\mathfrak{sp}(2n), M) = 0$ by Whitehead's Lemma.
- $\mathfrak{so}(2)$ acts as non-zero scalars $\pm 1$ on $V_{\pm 1} \implies$ no non-trivial 1-cocycles exist.

Hence $H^1(\mathfrak{g}_{\bar{0}}, \mathfrak{g}_{\bar{1}}) = 0$. Every 1-cocycle is a 1-coboundary.  
Therefore, there exists an odd element $X_0 \in \mathfrak{g}_{\bar{1}}$ such that:
$$ f(E) = -[E, X_0] \quad \forall E \in \mathfrak{g}_{\bar{0}}. $$

### Step 2: Gauge Transformation
Define $\tilde{f}(Z) = f(Z) - [Z, X_0]$ for all $Z \in \mathfrak{g}$.  
Since $[Z, X_0] = \delta X_0(Z)$ is an inner coboundary, $\delta \tilde{f} = \delta f = \gamma_{gb}$.  
By construction, $\tilde{f}(E) = 0$ for all $E \in \mathfrak{g}_{\bar{0}}$.

### Step 3: Action of $H_0$ on Odd Generators
Evaluate $(\delta \tilde{f})(H_0, F)$ for $F = a_1^\sigma b_l^u \in \mathfrak{g}_{\bar{1}}$:
$$ (\delta \tilde{f})(H_0, F) = [H_0, \tilde{f}(F)] - [F, \tilde{f}(H_0)] - \tilde{f}([H_0, F]). $$
Since $\tilde{f}(H_0) = 0$ and $H_0$ is central in $\mathfrak{g}_{\bar{0}}$ ($[H_0, \tilde{f}(F)] = 0$ as $\tilde{f}(F) \in \mathfrak{g}_{\bar{0}}$):
$$ (\delta \tilde{f})(H_0, a_1^\sigma b_l^u) = - \tilde{f}([H_0, a_1^\sigma b_l^u]) = - \sigma \tilde{f}(a_1^\sigma b_l^u). $$

Equating to $\gamma_{gb}(H_0, a_1^\sigma b_l^u) = \sigma \mathrm{gb}_{\sigma, l, u} H_0$:
$$ -\sigma \tilde{f}(a_1^\sigma b_l^u) = \sigma \mathrm{gb}_{\sigma, l, u} H_0 \implies \tilde{f}(a_1^\sigma b_l^u) = - \mathrm{gb}_{\sigma, l, u} H_0. $$

### Step 4: Obstruction Equation on Bosonic Generators
Now evaluate $(\delta \tilde{f})(b_j^s b_k^t, a_1^\sigma b_l^u)$ for bosonic bilinear $E = b_j^s b_k^t \in \mathfrak{g}_{\bar{0}}$:
$$ (\delta \tilde{f})(E, F) = [E, \tilde{f}(F)] - \tilde{f}([E, F]). $$
1. First term: $[b_j^s b_k^t, \tilde{f}(a_1^\sigma b_l^u)] = [b_j^s b_k^t, -\mathrm{gb}_{\sigma, l, u} H_0] = 0$ (since $H_0$ commutes with bosonic bilinears).
2. Second term:
   $$ -\tilde{f}([b_j^s b_k^t, a_1^\sigma b_l^u]) = -[b_j^s, b_l^u] \tilde{f}(a_1^\sigma b_k^t) - [b_k^t, b_l^u] \tilde{f}(a_1^\sigma b_j^s) $$
   $$ = \left( [b_j^s, b_l^u] \mathrm{gb}_{\sigma, k, t} + [b_k^t, b_l^u] \mathrm{gb}_{\sigma, j, s} \right) H_0. $$

Equating to $\gamma_{gb}(b_j^s b_k^t, a_1^\sigma b_l^u) = - \mathrm{gb}_{\sigma, j, s} b_k^t b_l^u - \mathrm{gb}_{\sigma, k, t} b_j^s b_l^u$:
$$ - \mathrm{gb}_{\sigma, j, s} b_k^t b_l^u - \mathrm{gb}_{\sigma, k, t} b_j^s b_l^u = \left( [b_j^s, b_l^u] \mathrm{gb}_{\sigma, k, t} + [b_k^t, b_l^u] \mathrm{gb}_{\sigma, j, s} \right) H_0. $$

### Step 5: Linear Independence & Conclusion
In $\mathfrak{g}_{\bar{0}} = \mathfrak{so}(2) \oplus \mathfrak{sp}(2n)$, the element $H_0$ (spanning $\mathfrak{so}(2)$) and the bosonic bilinears $b_A b_B$ (spanning $\mathfrak{sp}(2n)$) are **linearly independent**.

Therefore, the equality can hold if and only if the coefficients on both sides vanish independently:
$$ \mathrm{gb}_{\sigma, j, s} = 0 \quad \forall \sigma \in \{+, -\}, j \in \{1, \ldots, n\}, s \in \{+, -\}. $$

$$\blacksquare$$

---

## 5. Computational Verification Artifacts ($n=1, 2, 3$)

To provide complete empirical connectivity for human researchers, the linear system $M_f \phi = M_{\mathrm{gb}} \mathrm{gb}$ was constructed and analyzed using exact SVD decomposition in [scripts/verify_cn_triviality.py](file:///Users/aoi/notebook/git/thm01-R-batch/thm01-R-gemini36f-b14-C/scripts/verify_cn_triviality.py).

The results are saved in [artifacts/verification_results.json](file:///Users/aoi/notebook/git/thm01-R-batch/thm01-R-gemini36f-b14-C/artifacts/verification_results.json):

```json
{
  "C(1+1)": {
    "algebra": "C(1+1) = osp(2|2)",
    "num_gb_parameters": 4,
    "num_equations": 128,
    "num_f_parameters": 32,
    "rank_coboundary_M_f": 32,
    "dim_obstruction_space": 96,
    "rank_obstruction_matrix_A": 4,
    "dim_trivial_gb_subspace": 0,
    "conclusion": "NON-TRIVIAL FOR ALL NON-ZERO PARAMETERS"
  },
  "C(2+1)": {
    "algebra": "C(2+1) = osp(2|4)",
    "num_gb_parameters": 8,
    "num_equations": 1696,
    "num_f_parameters": 176,
    "rank_coboundary_M_f": 176,
    "dim_obstruction_space": 1520,
    "rank_obstruction_matrix_A": 8,
    "dim_trivial_gb_subspace": 0,
    "conclusion": "NON-TRIVIAL FOR ALL NON-ZERO PARAMETERS"
  },
  "C(3+1)": {
    "algebra": "C(3+1) = osp(2|6)",
    "num_gb_parameters": 12,
    "num_equations": 9516,
    "num_f_parameters": 528,
    "rank_coboundary_M_f": 528,
    "dim_obstruction_space": 8988,
    "rank_obstruction_matrix_A": 12,
    "dim_trivial_gb_subspace": 0,
    "conclusion": "NON-TRIVIAL FOR ALL NON-ZERO PARAMETERS"
  }
}
```

### Interpretation of Computational Results:
1. **Full Column Rank of Coboundary Operator $M_f$**:
   For $n=1, 2, 3$, $\mathrm{Rank}(M_f) = N_\phi = 2 \dim(\mathfrak{g}_{\bar{0}}) \dim(\mathfrak{g}_{\bar{1}})$. Thus, $\mathrm{Ker}(\delta f) = 0$ modulo inner coboundaries.
2. **Full Rank of Obstruction Matrix $A = P_{\mathrm{Ker}(M_f^T)} M_{\mathrm{gb}}$**:
   $\mathrm{Rank}(A) = 4n$ (equal to total number of $\mathrm{gb}$ parameters).
3. **Zero Trivial Parameter Subspace**:
   $\dim(\mathrm{Ker}(A)) = 4n - 4n = 0$. No non-zero parameter vector $\mathrm{gb}$ lies in the image of the coboundary operator.

---

## 6. Conclusion

The inhomogeneous deformation $\gamma_{gb}$ of $C(n+1) = \mathfrak{osp}(2|2n)$ is **trivial if and only if $\mathrm{gb} = 0$**. Every non-zero deformation parameter vector $\mathrm{gb} \neq 0$ defines a non-trivial deformation of the Lie superalgebra structure.
