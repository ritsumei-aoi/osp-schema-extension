# Mathematical Definition of Inhomogeneous Deformation for C(n+1)

This document defines the inhomogeneous deformation for $C(n+1) = \mathfrak{osp}(2|2n)$.

## 1. Deformation parameters (gb)

The inhomogeneous deformation is parametrized by a set of parity-1 parameters collections referred to as the **gb matrix**.

The role of the fermionic sector is played by the standard pair $a_1^+, a_1^-$. The deformation is defined by the exchange relations between fermionic and bosonic oscillators:

$$ [b_j^s, a_1^\sigma] = - \mathrm{gb}_{\sigma, j, s} \cdot \kappa, \quad \sigma \in \{+,-\}, s \in \{+,-\}. $$

The $gb$ parameters are indexed by the fermionic oscillator label and the bosonic oscillator label. For $C(n+1)$, there are $2 \times 2n = 4n$ deformation parameters:
$$ \{ \mathrm{gb}_{a_1^+, b_j^+}, \mathrm{gb}_{a_1^+, b_j^-}, \mathrm{gb}_{a_1^-, b_j^+}, \mathrm{gb}_{a_1^-, b_j^-} \mid j=1, \ldots, n \}. $$

## 2. Relation to Lie Superalgebra Bracket

The deformed bracket on the Lie superalgebra $\mathfrak{g} = C(n+1)$ is given by:
$$ [X, Y]_\gamma = [X, Y]_0 + \kappa \cdot \gamma(X, Y), $$
where $\gamma: \mathfrak{g} \otimes \mathfrak{g} \to \mathfrak{g}$ is a 2-cocycle.

The coefficients $\gamma_{abc}$ are derived by substituting the oscillator realizations of generators $X, Y$ and evaluating the bracket using the deformed oscillator relations.

**Parity Note**: Since $\kappa$ is odd ($p(\kappa)=1$) and the bracket preserves total parity, the deformation parameters $\mathrm{gb}$ must have parity 1.
