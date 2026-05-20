# Mathematical Definition of Inhomogeneous Deformation for C(n+1)

This document defines the inhomogeneous deformation (gamma structure) for
$C(n+1) = \mathfrak{osp}(2|2n)$, extending the framework used for $B(0,n)$.

## 1. Deformation parameters (gb)

The inhomogeneous deformation is parametrized by a set of parity-1 parameters
collectively referred to as the **gb matrix**.

In $B(0,n)$, the deformation was defined via the supplementary fermion $a_0$:
$$ a_0^2 \longmapsto \frac{1}{2} + \kappa \sum_{j, s} \mathrm{gb}_{a_0, b_j^s} \cdot b_j^s. $$

In $C(n+1) \cong C(1,n)$, the role of the fermionic sector is played by the
standard pair $a_1^+, a_1^-$. The deformation is defined by the exchange
relations between fermionic and bosonic oscillators:

$$ [b_j^s, a_1^\sigma] = - \mathrm{gb}_{\sigma, j, s} \cdot \kappa, \quad \sigma \in \{+,-\}, s \in \{+,-\}. $$

The $gb$ parameters are indexed by the fermionic oscillator label and the bosonic
oscillator label. For $C(n+1)$, there are $2 \times 2n = 4n$ deformation parameters:
$$ \{ \mathrm{gb}_{a_1^+, b_j^+}, \mathrm{gb}_{a_1^+, b_j^-}, \mathrm{gb}_{a_1^-, b_j^+}, \mathrm{gb}_{a_1^-, b_j^-} \mid j=1, \ldots, n \}. $$

## 2. Relation to Lie Superalgebra Bracket

The deformed bracket on the Lie superalgebra $\mathfrak{g} = C(n+1)$ is given by:
$$ [X, Y]_\gamma = [X, Y]_0 + \kappa \cdot \gamma(X, Y), $$
where $\gamma: \mathfrak{g} \otimes \mathfrak{g} \to \mathfrak{g}$ is a 2-cocycle.

The coefficients $\gamma_{abc}$ are derived by substituting the oscillator
realizations of generators $X, Y$ and evaluating the bracket using the deformed
oscillator relations.

### Mapping from B(0,n)
- The term $a_0^2$ in $B(0,n)$'s Cartan generator $H_n$ corresponds to the
  product $a_1^+ a_1^-$ in $C(n+1)$'s $H_1$.
- The deformation enters the algebra whenever an odd generator (linear in $a_1^\pm$)
  is commuted with an even generator (quadratic in $b_j^\pm$) or vice-versa.

## 3. Schema 2 (Gamma Structure) JSON Requirements

The `inhomogeneous_deformation` field in the JSON schema must record:
1.  `exchange_relation`: $[b_j, a_i] = -gb_{ij} \cdot \kappa$.
2.  `gb_matrix`: A $2 \times 2n$ matrix of parameter labels.
3.  `gamma_matrix`: The resulting $\gamma_{abc}$ coefficients for non-zero cases.

**Parity Note**: Since $\kappa$ is odd ($p(\kappa)=1$) and the bracket preserves
total parity, the deformation parameters $\mathrm{gb}$ must have parity 1.
