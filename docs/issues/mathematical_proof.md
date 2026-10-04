# Mathematical Proof: Unconditional Triviality of Inhomogeneous Deformations for $C(n+1) = \mathfrak{osp}(2|2n)$

**Author**: Antigravity Autonomous Research Agent  
**Date**: 2026-10-04  
**Status**: Closed / Complete  
**Artifacts**: [`data/verification_artifacts_cn1.json`](file:///Users/aoi/notebook/git/thm01-R-batch/thm01-R-gemini38f-b05-C/data/verification_artifacts_cn1.json), [`scripts/verify_shift.py`](file:///Users/aoi/notebook/git/thm01-R-batch/thm01-R-gemini38f-b05-C/scripts/verify_shift.py)

---

## 1. Executive Summary and Main Theorem

We analyze the triviality problem for the inhomogeneous deformation of the Lie superalgebra $\mathfrak{g} = C(n+1) \cong \mathfrak{osp}(2|2n)$ parametrized by the $4n$-dimensional collection of parity-1 parameters $\mathrm{gb}_{\sigma, j, s}$ ($\sigma \in \{+, -\}, j \in \{1, \ldots, n\}, s \in \{+, -\}$).

### Main Theorem (Unconditional Triviality)
> **Theorem 1.** *For any positive integer $n \geq 1$ and for all choices of deformation parameters $\mathrm{gb}_{\sigma, j, s} \in \mathbf{C}$, the inhomogeneous deformation 2-cocycle $\gamma_{\mathrm{gb}} \in Z^2(\mathfrak{g}; \mathfrak{g})_{\bar{1}}$ is identically a coboundary.*
>
> *Specifically, there exists an odd linear map $f \in C^1(\mathfrak{g}; \mathfrak{g})_{\bar{1}}$ such that:*
> $$ \gamma_{\mathrm{gb}} = \delta(-f) = -\delta f $$
> *Consequently, the necessary and sufficient condition on the deformation parameters $\mathrm{gb}_{\sigma, j, s}$ for triviality is **vacuous / trivially satisfied**: every inhomogeneous deformation of $C(n+1)$ is trivial.*

This theorem is established both through an exact general algebraic proof valid for all $n \ge 1$ and through comprehensive, computer-algebraic symbolic verification for $n = 1, 2, 3$ covering all bracket pairs with zero mismatches.

---

## 2. Algebraic Framework and Definitions

### 2.1 The Lie Superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$
Following `docs/math/Cn1_definition.md` (Frappat, Sciarrino, Sorba 2000), $C(n+1)$ is defined with root system:
$$ \Delta = \left\{ \pm \delta_k \pm \delta_l,\ \pm 2\delta_k,\ \pm \varepsilon \pm \delta_k \right\} \quad (1 \leq k < l \leq n) $$
The decomposition by parity is:
- Even roots $\Delta_{\bar{0}} = \{\pm 2\delta_k\} \cup \{\pm(\delta_i \pm \delta_j) \mid 1 \leq i < j \leq n\}$
- Odd roots $\Delta_{\bar{1}} = \{\pm \varepsilon \pm \delta_k \mid k = 1, \ldots, n\}$

The even subalgebra is $\mathfrak{g}_{\bar{0}} \cong \mathfrak{so}(2) \oplus \mathfrak{sp}(2n)$, with dimension $2n^2 + n + 1$.  
The odd subspace $\mathfrak{g}_{\bar{1}}$ has dimension $4n$.  
Total superdimension: $\dim(\mathfrak{g}) = (2n^2 + n + 1) \mid 4n$, total dimension $2n^2 + 5n + 1$.

| $n$ | Even Dim | Odd Dim | Total Dim | Algebra |
|---|---|---|---|---|
| $n=1$ | 4 | 4 | 8 | $C(2) \cong \mathfrak{osp}(2\|2)$ |
| $n=2$ | 11 | 8 | 19 | $C(3) \cong \mathfrak{osp}(2\|4)$ |
| $n=3$ | 22 | 12 | 34 | $C(4) \cong \mathfrak{osp}(2\|6)$ |

### 2.2 Oscillator Realization
The algebra is realized via:
- One standard fermionic oscillator pair $a_1^\pm$ with CAR: $\{a_1^-, a_1^+\} = K$ (or 1), $(a_1^\pm)^2 = 0$, $p(a_1^\pm) = 1$.
- $n$ bosonic oscillator pairs $b_k^\pm$ ($k=1, \ldots, n$) with CCR: $[b_j^-, b_k^+] = \delta_{jk} K$ (or $\delta_{jk}$), $[b_j^\pm, b_k^\pm] = 0$, $p(b_k^\pm) = 0$.

The generators of $\mathfrak{g}$ are represented as quadratic polynomials in the oscillators:
1. **Cartan Subalgebra** ($\dim = n+1$):
   $$ H_1 = a_1^+ a_1^- + b_1^+ b_1^- $$
   $$ H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- \quad (2 \leq k \leq n) $$
   $$ H_{n+1} = -b_n^+ b_n^- - \tfrac{1}{2} $$
2. **Bosonic Root Generators** ($\dim = 2n^2$):
   $$ E_{\delta_k - \delta_l} = b_k^+ b_l^- \quad (k \neq l) $$
   $$ E_{\delta_k + \delta_l} = b_k^+ b_l^+ \quad (k < l), \qquad E_{-\delta_k - \delta_l} = b_k^- b_l^- \quad (k < l) $$
   $$ E_{2\delta_k} = \tfrac{1}{2} (b_k^+)^2, \qquad E_{-2\delta_k} = \tfrac{1}{2} (b_k^-)^2 \quad (1 \leq k \leq n) $$
3. **Odd Root Generators** ($\dim = 4n$):
   $$ E_{\varepsilon + \delta_l} = a_1^+ b_l^+, \qquad E_{\varepsilon - \delta_l} = a_1^+ b_l^- $$
   $$ E_{-\varepsilon + \delta_l} = a_1^- b_l^+, \qquad E_{-\varepsilon - \delta_l} = a_1^- b_l^- \quad (1 \leq l \leq n) $$

### 2.3 The Inhomogeneous Deformation $\gamma_{\mathrm{gb}}$
Following `docs/math/C_inhomogeneous_definition.md`, the extended oscillator algebra $A = V \oplus \mathbf{C}K \oplus \mathbf{C}\kappa$ includes an odd central element $\kappa$ ($p(\kappa) = 1$) with deformed cross-exchange relations:
$$ [b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma, j, s} \cdot \kappa \quad \iff \quad [a_1^\sigma, b_j^s] = \mathrm{gb}_{\sigma, j, s} \cdot \kappa $$
where $\sigma \in \{+, -\}$, $s \in \{+, -\}$, and $j \in \{1, \ldots, n\}$.

In the universal enveloping algebra $\mathcal{U}(A)$, evaluating the supercommutator of quadratic generators $X, Y \in \mathfrak{g}$ yields:
$$ [X, Y]_\gamma = [X, Y]_0 + \kappa \cdot \gamma_{\mathrm{gb}}(X, Y) $$
where $\gamma_{\mathrm{gb}}: \mathfrak{g} \otimes \mathfrak{g} \to \mathfrak{g}$ is the deformation 2-cocycle with parity $p(\gamma(X, Y)) = p(X) + p(Y) + 1 \pmod 2$.

### 2.4 The Coboundary Operator $\delta f$
Following `docs/math/C_coboundary_definition.md`, for an odd linear map $f: \mathfrak{g} \to \mathfrak{g}$ (reversing parity, $p(f(X)) = p(X) + 1 \pmod 2$), the coboundary $\delta f: \mathfrak{g} \otimes \mathfrak{g} \to \mathfrak{g}$ is:
$$ (\delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)]_0 - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]_0 - f([X, Y]_0) $$
The deformation $\gamma$ is trivial if there exists an odd linear map $f$ such that $\gamma = \delta f$ (or up to scalar).

---

## 3. Theoretical Handling of the "Adjoint Representation / Up to Scalar" Condition

The problem context specifies that the algebra $C(n+1)$ is realized as a subalgebra of $\mathcal{U}(A)$ "by adjoint representation" and triviality is considered "up to scalar". We elucidate the precise algebraic role of this condition:

1. **Central Elements and the Adjoint Action**:
   In $\mathcal{U}(A)$, central scalars commute with all elements: $[\mathbf{C}\cdot K, X] = 0$. In the adjoint representation $\mathrm{ad}: \mathcal{U}(A) \to \mathrm{End}(\mathcal{U}(A))$, any central scalar acts as the zero operator:
   $$ \mathrm{ad}(c K)(X) = [c K, X] = 0 $$
   Therefore, two elements $X, X' \in \mathcal{U}(A)$ differing by central scalars ($X' - X \in \mathbf{C}K \oplus \mathbf{C}\kappa$) define identical adjoint operators on $\mathfrak{g}$.

2. **Oscillator Normal Ordering and Commutation**:
   When commuting quadratic monomials in $\mathcal{U}(A)$, exchanging two oscillators produces a central term:
   $$ v u = (-1)^{p(u)p(v)} u v + [v, u]_A \equiv (-1)^{p(u)p(v)} u v \pmod{\mathbf{C}K \oplus \mathbf{C}\kappa} $$
   Since any term in $\gamma_{\mathrm{gb}}(X, Y)$ is already at first order in $\kappa$, any additional central commutator in $\mathcal{U}(A)$ contributes terms in $\kappa K$ (pure scalar) or $\kappa^2 = 0$. Under the adjoint action on $\mathfrak{g}$, these scalar terms have zero adjoint action.

3. **Strict Algebraic Equality**:
   Remarkably, as demonstrated in our explicit construction below, we do not even need to discard any non-zero scalar component: when the generators of $\mathfrak{g}$ are taken in standard basis, the coboundary identity holds **strictly and identically within $\mathfrak{g}$**:
   $$ \gamma_{\mathrm{gb}}(X, Y) = \delta(-f)(X, Y) \quad \text{for all } X, Y \in \mathfrak{g} $$
   with no scalar obstruction.

---

## 4. General Mathematical Proof of Triviality

### Lemma 1 (Canonical Oscillator Shift)
> Let $A = V \oplus \mathbf{C}K \oplus \mathbf{C}\kappa$ be the deformed oscillator superalgebra. Define the shifted oscillators:
> $$ \tilde{b}_j^s = b_j^s \quad (j = 1, \ldots, n;\ s \in \{+, -\}) $$
> $$ \tilde{a}_1^\sigma = a_1^\sigma + \kappa \cdot v^\sigma \quad (\sigma \in \{+, -\}) $$
> where $v^\sigma \in V_{\bar{0}}$ is the linear combination of bosonic oscillators:
> $$ v^\sigma = \sum_{j=1}^n \left( \mathrm{gb}_{\sigma, j, -} b_j^+ - \mathrm{gb}_{\sigma, j, +} b_j^- \right) \in V_{\bar{0}} $$
> Then the shifted oscillators $\tilde{a}_1^\sigma, \tilde{b}_j^s$ satisfy the **exact, undeformed commutation relations** in $\mathcal{U}(A)$:
> 1. $[\tilde{b}_j^-, \tilde{b}_k^+] = \delta_{jk} K$, $[\tilde{b}_j^\pm, \tilde{b}_k^\pm] = 0$.
> 2. $\{\tilde{a}_1^-, \tilde{a}_1^+\} = K$, $(\tilde{a}_1^\pm)^2 = 0$.
> 3. $[\tilde{b}_j^s, \tilde{a}_1^\sigma] = 0$ for all $\sigma, j, s$.

*Proof.*  
1. Since $\tilde{b} = b$, the bosonic CCR are identically preserved.
2. For the fermionic CAR, since $p(\kappa)=1$ and $p(v^\sigma)=0$, $\kappa v^\sigma$ has parity 1. Thus:
   $$ \{\tilde{a}_1^\sigma, \tilde{a}_1^{\sigma'}\} = \{a_1^\sigma, a_1^{\sigma'}\} + \kappa [v^\sigma, a_1^{\sigma'}] + \kappa [a_1^\sigma, v^{\sigma'}] + \kappa^2 \{v^\sigma, v^{\sigma'}\} $$
   Since $[v, a] \propto \kappa$ in $A$, $\kappa [v, a] \propto \kappa^2 = 0$, and $\kappa^2 = 0$ identically. Hence $\{\tilde{a}_1^\sigma, \tilde{a}_1^{\sigma'}\} = \{a_1^\sigma, a_1^{\sigma'}\} = \delta_{\sigma, -\sigma'} K$.
3. For the cross-commutator:
   $$ [\tilde{b}_j^s, \tilde{a}_1^\sigma] = [b_j^s, a_1^\sigma + \kappa v^\sigma] = [b_j^s, a_1^\sigma] + [b_j^s, \kappa v^\sigma] $$
   Since $b_j^s$ is even and $\kappa$ is central, $[b_j^s, \kappa v^\sigma] = \kappa [b_j^s, v^\sigma]_0$.
   Using the CCR $[b_j^-, b_k^+] = \delta_{jk}$ and $[b_j^+, b_k^-] = -\delta_{jk}$:
   - For $s = +$:
     $$ [b_j^+, v^\sigma]_0 = [b_j^+, -\mathrm{gb}_{\sigma, j, +} b_j^-]_0 = -\mathrm{gb}_{\sigma, j, +} (-1) = \mathrm{gb}_{\sigma, j, +} $$
   - For $s = -$:
     $$ [b_j^-, v^\sigma]_0 = [b_j^-, \mathrm{gb}_{\sigma, j, -} b_j^+]_0 = \mathrm{gb}_{\sigma, j, -} (1) = \mathrm{gb}_{\sigma, j, -} $$
   In both cases, $[b_j^s, v^\sigma]_0 = \mathrm{gb}_{\sigma, j, s}$.
   Substituting into the commutator:
   $$ [\tilde{b}_j^s, \tilde{a}_1^\sigma] = -\mathrm{gb}_{\sigma, j, s} \kappa + \kappa \cdot \mathrm{gb}_{\sigma, j, s} = 0 $$
   The cross-commutator vanishes identically. $\square$

---

### Lemma 2 (Induced 1-Cochain $f$)
> Let $Z_k$ be any basis element of $C(n+1)$, expressed as a quadratic polynomial in oscillators: $Z_k = \sum c_{uv} u v$.
> Evaluating $Z_k$ on the shifted oscillators gives:
> $$ \tilde{Z}_k = Z_k(\tilde{a}, \tilde{b}) = Z_k(a, b) + \kappa \cdot f(Z_k) $$
> where $f: \mathfrak{g} \to \mathfrak{g}$ is an odd linear map ($p(f(Z_k)) = p(Z_k) + 1 \pmod 2$) given explicitly by:
> 1. For purely bosonic generators $X \in \mathfrak{sp}(2n) \subset \mathfrak{g}_{\bar{0}}$ (all $E_{\pm \delta_k \pm \delta_l}$, $E_{\pm 2\delta_k}$, and $H_k$ for $k \ge 2$):
>    $$ f(X) = 0 $$
> 2. For the Cartan element $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$:
>    $$ f(H_1) = v^+ a_1^- - a_1^+ v^- \in \mathfrak{g}_{\bar{1}} $$
> 3. For any odd generator $E_{\sigma \varepsilon + s \delta_l} = a_1^\sigma b_l^s \in \mathfrak{g}_{\bar{1}}$:
>    $$ f(E_{\sigma \varepsilon + s \delta_l}) = v^\sigma b_l^s \in \mathfrak{g}_{\bar{0}} $$

*Proof.*  
Since $\tilde{b} = b$, any generator involving only bosonic oscillators is completely invariant under the shift, so $\tilde{X} = X$, which implies $f(X) = 0$.  
For $H_1$: $\tilde{a}_1^+ \tilde{a}_1^- = (a_1^+ + \kappa v^+)(a_1^- + \kappa v^-) = a_1^+ a_1^- + a_1^+ \kappa v^- + \kappa v^+ a_1^- + O(\kappa^2)$. Moving $\kappa$ to the left: $a_1^+ \kappa = -\kappa a_1^+$. Thus $\tilde{a}_1^+ \tilde{a}_1^- = a_1^+ a_1^- + \kappa(v^+ a_1^- - a_1^+ v^-)$.  
For the odd generators: $\tilde{a}_1^\sigma \tilde{b}_l^s = (a_1^\sigma + \kappa v^\sigma) b_l^s = a_1^\sigma b_l^s + \kappa v^\sigma b_l^s$.  
Since $v^\sigma \in V_{\bar{0}}$, $v^\sigma a_1^\pm$ and $a_1^\pm v^\sigma$ are linear combinations of fermion-boson pairs, which lie in $\mathfrak{g}_{\bar{1}}$. Similarly, $v^\sigma b_l^s$ is a linear combination of boson-boson pairs, which lie in $\mathfrak{sp}(2n) \subset \mathfrak{g}_{\bar{0}}$. Thus $f$ maps $\mathfrak{g}_{\bar{0}} \to \mathfrak{g}_{\bar{1}}$ and $\mathfrak{g}_{\bar{1}} \to \mathfrak{g}_{\bar{0}}$, so $f$ is an odd linear map on $\mathfrak{g}$. $\square$

---

### Theorem 2 (Proof of Main Theorem)
> Under the map $f$ constructed in Lemma 2:
> $$ \gamma_{\mathrm{gb}} = -\delta f = \delta(-f) $$
> identically on $\mathfrak{g} \otimes \mathfrak{g}$. Therefore, $\gamma_{\mathrm{gb}}$ is a coboundary, and the deformation is trivial for all $\mathrm{gb}$.

*Proof.*  
Let $X, Y \in \mathfrak{g}$ be homogeneous generators.  
By Lemma 1, the shifted generators $\tilde{X} = X + \kappa f(X)$ and $\tilde{Y} = Y + \kappa f(Y)$ satisfy the undeformed commutation relations:
$$ [\tilde{X}, \tilde{Y}] = \widetilde{[X, Y]_0} = [X, Y]_0 + \kappa f([X, Y]_0) $$
On the other hand, we compute the supercommutator of $\tilde{X}$ and $\tilde{Y}$ in $\mathcal{U}(A)$ using the deformed bracket:
$$ [\tilde{X}, \tilde{Y}] = [X + \kappa f(X), Y + \kappa f(Y)] $$
Expanding to first order in $\kappa$ (using $[\kappa, \cdot] = 0$ and $p(\kappa)=1$):
$$ [X, \kappa f(Y)] = (-1)^{p(X) p(\kappa)} \kappa [X, f(Y)]_0 = (-1)^{p(X)} \kappa [X, f(Y)]_0 $$
and
$$ [\kappa f(X), Y] = - (-1)^{p(\kappa f(X)) p(Y)} [Y, \kappa f(X)] = - (-1)^{(p(X)+1)p(Y)} \kappa [Y, f(X)]_0 $$
Together with the deformed bracket $[X, Y]_\gamma = [X, Y]_0 + \kappa \gamma_{\mathrm{gb}}(X, Y)$, we obtain:
$$ [\tilde{X}, \tilde{Y}] = [X, Y]_0 + \kappa \left( \gamma_{\mathrm{gb}}(X, Y) + (-1)^{p(X)} [X, f(Y)]_0 - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]_0 \right) $$
Equating the two expressions for $[\tilde{X}, \tilde{Y}]$:
$$ [X, Y]_0 + \kappa f([X, Y]_0) = [X, Y]_0 + \kappa \left( \gamma_{\mathrm{gb}}(X, Y) + (-1)^{p(X)} [X, f(Y)]_0 - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]_0 \right) $$
Subtracting $[X, Y]_0$ and equating the coefficients of $\kappa$:
$$ f([X, Y]_0) = \gamma_{\mathrm{gb}}(X, Y) + (-1)^{p(X)} [X, f(Y)]_0 - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]_0 $$
Rearranging for $\gamma_{\mathrm{gb}}(X, Y)$:
$$ \gamma_{\mathrm{gb}}(X, Y) = - \left( (-1)^{p(X)} [X, f(Y)]_0 - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]_0 - f([X, Y]_0) \right) $$
By the definition of the coboundary operator $\delta$:
$$ \gamma_{\mathrm{gb}}(X, Y) = - (\delta f)(X, Y) = \delta(-f)(X, Y) $$
This completes the proof. $\square$

---

## 5. Computational Artifacts and Empirical Verification

To ensure reproducibility and connectivity for future mathematical research, we implemented the complete symbolic algebra in Python using SymPy.

### 5.1 Verification Scripts and Data Files
The following files were created in the repository:
1. [`scripts/verify_shift.py`](file:///Users/aoi/notebook/git/thm01-R-batch/thm01-R-gemini38f-b05-C/scripts/verify_shift.py):  
   Executes exact symbolic bracket calculations and verifies $\gamma_{\mathrm{gb}} = \delta(-f)$ for $n=1, 2, 3$.
2. [`scripts/export_artifacts.py`](file:///Users/aoi/notebook/git/thm01-R-batch/thm01-R-gemini38f-b05-C/scripts/export_artifacts.py):  
   Generates comprehensive JSON artifacts documenting all structure constants, generator gradings, map $f$ coefficients, and proof certificates.
3. [`data/verification_artifacts_cn1.json`](file:///Users/aoi/notebook/git/thm01-R-batch/thm01-R-gemini38f-b05-C/data/verification_artifacts_cn1.json):  
   The primary structured artifact (13 KB JSON) recording complete verification results.

### 5.2 Verification Results Summary

| Metric | $n=1$ ($C(2)$) | $n=2$ ($C(3)$) | $n=3$ ($C(4)$) |
|---|---|---|---|
| Total Superdimension $\dim(\mathfrak{g})$ | $4 \mid 4$ ($8$) | $11 \mid 8$ ($19$) | $22 \mid 12$ ($34$) |
| Deformation parameters ($4n$) | 4 | 8 | 12 |
| Non-zero undeformed structure constants | 62 | 277 | 780 |
| Total bracket pairs $(X, Y)$ evaluated | 64 | 361 | 1156 |
| Super Jacobi identity verified on all triples | **Yes** (Identical 0) | **Yes** (Identical 0) | **Yes** (Identical 0) |
| Identity $\gamma_{\mathrm{gb}} = -\delta f = \delta(-f)$ verified | **64 / 64 pairs** | **361 / 361 pairs** | **1156 / 1156 pairs** |
| Discrepancies / Mismatches | **0** | **0** | **0** |
| Remaining obstruction equations on $\mathrm{gb}$ | **None (0)** | **None (0)** | **None (0)** |

Every single bracket pair for $n=1, 2, 3$ satisfies $\gamma_{\mathrm{gb}} = \delta(-f)$ with zero discrepancy.

---

## 6. Definitive Conclusion

For the Lie superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$:
1. The inhomogeneous deformation $\gamma_{\mathrm{gb}}$ defined via oscillator exchange relations is **unconditionally trivial** for all $n \geq 1$.
2. The triviality condition on the parameters $\mathrm{gb}_{\sigma, j, s}$ is **unconstrained**: no non-trivial equations are imposed on the parameters, and every configuration of $\mathrm{gb}$ defines a coboundary.
3. The coboundary 1-cochain $-f$ is explicitly given by the canonical oscillator shift $v^\sigma = \sum_{j=1}^n (\mathrm{gb}_{\sigma, j, -} b_j^+ - \mathrm{gb}_{\sigma, j, +} b_j^-)$ which simultaneously absorbs all deformed exchange relations while preserving all canonical CCR and CAR relations.
