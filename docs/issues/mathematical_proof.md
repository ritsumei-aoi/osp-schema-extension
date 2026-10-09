# Mathematical Proof: Triviality of Inhomogeneous Deformations of C(n+1)

**Date**: 2026-10-10
**Status**: Resolved

## Theorem

For all $n \geq 1$, every inhomogeneous deformation $\gamma_{gb}$ of $C(n+1) = \mathfrak{osp}(2|2n)$ is trivial. No constraints on the $gb$ parameters are required.

Equivalently: the relevant component of $H^2(C(n+1), C(n+1))$ classifying inhomogeneous deformations vanishes.

## Setup

We work with the oscillator realization of $C(n+1)$. The generators are:
- **Fermionic**: $a_1^+, a_1^-$ satisfying $\{a_1^+, a_1^-\} = 1$ (CAR).
- **Bosonic**: $b_j^+, b_j^-$ for $j = 1, \ldots, n$ satisfying $[b_j^-, b_j^+] = 1$ (CCR).
- **Odd central element**: $\kappa$ with $\kappa^2 = 0$.

The Lie superalgebra $\mathfrak{g} = C(n+1)$ is realized as the space of quadratic expressions in these oscillators, acting via the adjoint representation (where scalar multiples of the identity act as zero).

### Inhomogeneous Deformation

The deformation modifies the mixed bosonic-fermionic commutator:
$$[b_j^s, a_1^\sigma]_{\text{def}} = -\text{gb}_{\sigma, j, s} \cdot \kappa$$
where $\text{gb}_{\sigma, j, s} \in \mathbb{C}$ are the deformation parameters ($\sigma, s \in \{+, -\}$, $j = 1, \ldots, n$).

All other oscillator relations are unchanged: $\{a^+, a^-\} = 1$, $[b_j^-, b_j^+] = 1$, $[b, b'] = 0$ for $j \neq j'$.

### Induced Lie Algebra Deformation

The deformed oscillator relations induce a deformed Lie bracket on $\mathfrak{g}$:
$$[X, Y]_{\text{def}} = [X, Y]_0 + \kappa \cdot \gamma_{gb}(X, Y)$$

The 2-cochain $\gamma_{gb}: \mathfrak{g} \otimes \mathfrak{g} \to \mathfrak{g}$ encodes all bracket corrections at order $\kappa$.

## Proof of Triviality

### Part 1: Oscillator-Level Gauge Transformation

**Claim.** Define the corrected fermionic generators:
$$a'^\sigma = a^\sigma + \sum_{j=1}^n \left( \text{gb}_{\sigma, j, -} \cdot b_j^+ - \text{gb}_{\sigma, j, +} \cdot b_j^- \right) \kappa$$

Then $[b_j^s, a'^\sigma]_{\text{def}} = 0$ for all $j, s, \sigma$.

**Proof.** Fix $j, s, \sigma$. The correction term is $\text{corr}_\sigma = \sum_k (\text{gb}_{\sigma,k,-} b_k^+ - \text{gb}_{\sigma,k,+} b_k^-) \kappa$.

In the deformed extended algebra:
$$[b_j^s, a'^\sigma]_{\text{def}} = [b_j^s, a^\sigma]_{\text{def}} + [b_j^s, \text{corr}_\sigma]$$

The first term gives $-\text{gb}_{\sigma,j,s} \cdot \kappa$ by the deformation definition.

For the second term, since $\kappa^2 = 0$, only the $k = j$ terms contribute (cross-terms with $k \neq j$ commute):
$$[b_j^s, \text{corr}_\sigma] = \text{gb}_{\sigma,j,-} [b_j^s, b_j^+] \kappa - \text{gb}_{\sigma,j,+} [b_j^s, b_j^-] \kappa$$

- If $s = +$: $[b^+, b^+] = 0$ and $[b^+, b^-] = -1$, giving $+\text{gb}_{\sigma,j,+} \kappa$.
  But the first term gives $-\text{gb}_{\sigma,j,+} \kappa$. Total: $0$. $\checkmark$
- If $s = -$: $[b^-, b^+] = 1$ and $[b^-, b^-] = 0$, giving $+\text{gb}_{\sigma,j,-} \kappa$.
  But the first term gives $-\text{gb}_{\sigma,j,-} \kappa$. Total: $0$. $\checkmark$

Moreover:
- $\{a'^\sigma, a'^\tau\} = \{a^\sigma, a^\tau\}$ (correction terms contribute at order $\kappa^2 = 0$).
- $[b, b']$ is unchanged since $b$ is not modified.

Therefore, the map $\Phi: a^\sigma \mapsto a'^\sigma$, $b_j^s \mapsto b_j^s$, $\kappa \mapsto \kappa$ defines an automorphism of the extended oscillator algebra that removes the deformation entirely. The primed generators $\{a'^\sigma, b_j^s\}$ satisfy the **undeformed** relations in the **deformed** algebra.

**This holds for all $n \geq 1$ and all values of the $\text{gb}$ parameters, with no constraints.** $\square$

### Part 2: Lie Algebra Level Verification (n = 1)

For $C(2) = \mathfrak{osp}(2|2)$, we verify triviality at the Lie algebra level by solving the gauge equivalence equation $\gamma_{gb} = \delta_{\text{gauge}}(g)$ as a linear system.

**Basis of $C(2)$:**
- Even: $e_1 = H_1 = N_a + N_b$, $e_2 = H_2 = -N_b - \tfrac{1}{2}$, $e_3 = E_{2\delta} = \tfrac{1}{2}(b^+)^2$, $e_4 = E_{-2\delta} = \tfrac{1}{2}(b^-)^2$.
- Odd: $o_1 = a^+b^+$, $o_2 = a^+b^-$, $o_3 = a^-b^+$, $o_4 = a^-b^-$.

**Gauge equivalence formula.** For the change of basis $\Phi(X) = X + g(X)\kappa$ in the extended algebra (with $\kappa$ odd, $g$ an odd linear map), the triviality condition is:
$$\gamma(X, Y) = -[X, g(Y)] + (-1)^{|X||Y|} [Y, g(X)] + g([X, Y])$$

This formula is derived from the condition $[\Phi(X), \Phi(Y)]_{\text{def}} = \Phi([X, Y]_0)$ at first order in $\kappa$, using the bracket structure of the $\kappa$-extended algebra where $\kappa$ is odd and central.

**Remark on the sign convention.** The standard Chevalley--Eilenberg coboundary operator $(\delta f)(X, Y) = (-1)^{|X|}[X, f(Y)] - (-1)^{(|X|+1)|Y|}[Y, f(X)] - f([X, Y])$ coincides with the gauge formula only when both arguments are even. For mixed or odd-odd pairs, the two formulas differ because the CE differential is defined with respect to the Lie bracket on $\mathfrak{g}$, while the gauge formula accounts for the sign structure of the $\kappa$-extended algebra. In the context of deformations by an odd central parameter $\kappa$, the gauge formula is the correct triviality criterion.

**Computation.** We parametrize $g$ by 32 unknowns: $g(e_i) = \sum_k \phi_{ki} o_k$ (16 params, even $\to$ odd) and $g(o_k) = \sum_i \psi_{ik} e_i$ (16 params, odd $\to$ even).

The gamma values $\gamma(X, Y)$ for all basis pairs are computed from the deformed oscillator algebra using normal-ordered operator monomials (implemented in `verification/operator_algebra.py`).

Substituting into the gauge formula yields a linear system of 102 equations in 32 unknowns over $\mathbb{Q}$.

**Result:** The system has rank 28 and is **consistent**. A particular solution exists (with 4 free parameters), confirming triviality at the Lie algebra level. For $\text{gb} = (1, 2, 3, 4)$, one solution is:

| $g(e_1)$ | $-3o_2 - 2o_3 - o_4$ |
|-----------|----------------------|
| $g(e_2)$ | $2o_1 + 3o_2 + o_4$ |
| $g(e_3)$ | $-3o_1 - o_3$ |
| $g(e_4)$ | $-2o_2$ |
| $g(o_1)$ | $-e_1 - e_2 + 4e_3$ |
| $g(o_2)$ | $-2e_2$ |
| $g(o_3)$ | $3e_1 + 3e_2 + 4e_3$ |
| $g(o_4)$ | $2e_1$ |

## The "Up to Scalar" Condition

In the oscillator realization, the Lie algebra acts via the adjoint representation. Scalar multiples of the identity commute with all elements, hence $\text{ad}(c \cdot \mathbf{1}) = 0$. This means:

- $b_j^- b_j^+ = N_{b_j} + 1$ is identified with $N_{b_j}$ in the adjoint representation.
- $a^- a^+ = 1 - N_a$ is identified with $-N_a$.

When expressing operator products in the Lie algebra basis, we systematically drop the scalar part (the $(0,0,0,0)$-monomial in the normal-ordered expansion). This identification is implemented in `operator_algebra.py:express_in_basis()` and is consistent across all computations.

## Summary

| Verification | Method | Result |
|---|---|---|
| $n = 1$ (oscillator) | Gauge transformation | PASSED |
| $n = 2$ (oscillator) | Gauge transformation | PASSED |
| $n = 3$ (oscillator) | Gauge transformation | PASSED |
| $n = 1$ (Lie algebra) | 102x32 linear system | CONSISTENT (rank 28) |

**Conclusion.** The inhomogeneous deformation $\gamma_{gb}$ of $C(n+1) = \mathfrak{osp}(2|2n)$ is trivial for **all** $n \geq 1$ and **all** values of the deformation parameters $\text{gb}_{\sigma, j, s}$. No constraints are required. The triviality is established by the explicit gauge transformation $a'^\sigma = a^\sigma + \sum_j (\text{gb}_{\sigma,j,-} b_j^+ - \text{gb}_{\sigma,j,+} b_j^-)\kappa$, which removes the deformation entirely.

## Computational Artifacts

All verification code and structured data are in the `verification/` directory:
- `verify_triviality.py`: Main verification script (Parts 1--3).
- `operator_algebra.py`: Symbolic operator algebra for computing $\gamma$ from the deformed oscillator relations.
- `artifacts.json`: JSON artifact with theorem statement, solutions, and gamma data.
