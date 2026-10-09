# Mathematical Definition of Inhomogeneous Deformation for C(n+1) (revised)

This document defines the inhomogeneous deformation for $C(n+1) = \mathfrak{osp}(2|2n)$.
It is well-known that $C(n+1)$(and other oscillator Lie superalgebras) can be obtained from skew-supersymmetric bilinear forms.
Let $V=V_{\overline{0}}\oplus V_{\overline{1}}$ be a superspace. Consider the extension $A=V\oplus \mathbf{C}K\oplus\mathbf{C}\kappa$, where $K$ and $\kappa$ are even/odd central elements respectively.
The structure of a Lie superalgebras on the extension is obtained by a skew-supersymmetric pre-oscillator form $(\cdot|\cdot):V\times V\to\mathbf{C}$ by the following:
$$
[a,b]=\begin{cases}
(a|b)K & p(a)=p(b), \\
(a|b)\kappa & p(a)\ne p(b),
\end{cases}
$$
where $p(\cdot)$ stands for the parity of homogeneous elements in $V$.
In this note, we always consider that $C(n+1)$ is realized as a subalgebra of $\mathcal{U}(A)$(universal enveloping algebra) by adjoint representation.

## 1. Deformation parameters (gb)

The inhomogeneous deformation is parametrized by a set of parity-0 (even)
parameters collected in the **gb matrix**.

The role of the fermionic sector is played by the standard pair $a_1^+, a_1^-$. The deformation is defined by the exchange relations between fermionic and bosonic oscillators:

$$ [b_j^s, a_1^\sigma] = - \mathrm{gb}_{\sigma, j, s} \cdot \kappa, \quad \sigma \in \{+,-\}, s \in \{+,-\}. $$

The $gb$ parameters are indexed by the fermionic oscillator label and the bosonic oscillator label. For $C(n+1)$, there are $2 \times 2n = 4n$ deformation parameters:
$$ \{ \mathrm{gb}_{a_1^+, b_j^+}, \mathrm{gb}_{a_1^+, b_j^-}, \mathrm{gb}_{a_1^-, b_j^+}, \mathrm{gb}_{a_1^-, b_j^-} \mid j=1, \ldots, n \}. $$

## 2. Relation to Lie Superalgebra Bracket

The deformed bracket on the Lie superalgebra $\mathfrak{g} = C(n+1)$ is given by:
$$ [X, Y]_\gamma = [X, Y]_0 + \kappa \cdot \gamma(X, Y), $$
where the oscillator gamma data may include the central identity component
$K$, so its recorded output space is $\mathfrak{g}\oplus\mathbf{C}K$.
We note that the bracket can be extend to $L:=\mathfrak{g}\oplus \kappa\mathfrak{g}$ as an abelian extension by its adjoint representation, where the central element $\kappa$ acts trivial.
The coefficients $\gamma_{abc}$ are derived by substituting the oscillator realizations of generators $X, Y$ and evaluating the bracket using the deformed oscillator relations.


**Parity Note**: The central extension element $\kappa$ is odd
($p(\kappa)=1$), and the deformation parameters $\mathrm{gb}$ are even
($p(\mathrm{gb})=0$). Thus the correction
$-\mathrm{gb}_{\sigma,j,s}\kappa$ to the bracket of an even boson and an odd
fermion has parity 1, as required.
