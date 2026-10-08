# Triviality of the stated \(C(n+1)\) inhomogeneous deformation

## Conclusion

The supplied definitions do **not** determine necessary and sufficient
conditions on the \(gb_{\sigma,j,s}\), for \(n=1,2,3\) or in general. They
specify \(4n\) parameters and a proposed coboundary, but do not specify the
adjoint-valued cochain \(\gamma_{gb}\) as a function of those parameters.
In particular, the coefficients said to be obtained from the deformed
oscillator relations are not given, nor is the identification of the
\(\kappa\)-terms with elements of the adjoint module \(\mathfrak g\).
Consequently the linear system whose solvability would decide triviality
cannot be formed from the provided material.

This is a definitive limitation of the stated problem, not evidence that the
only trivial parameter is zero or that every parameter is trivial. The
zero parameter gives the undeformed bracket and hence the zero cochain, which
is a coboundary (\(f=0\)). Whether any nonzero parameter is trivial remains
undetermined until the missing cochain data and module identification are
provided. No external source was used.

## What the definitions do determine

The root/oscillator definition gives
\[
 \dim \mathfrak g_{\bar 0}=e=2n^2+n+1,\qquad
 \dim \mathfrak g_{\bar 1}=o=4n,
\]
and the inhomogeneous-deformation note lists \(4n\) odd parameters
\(gb_{\sigma,j,s}\). The coboundary note specifies an odd map
\(f:\mathfrak g\to\mathfrak g\) and, for homogeneous \(X,Y\), the formula
\[
(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]
-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y]).
\]
This formula is super-skew in \(X,Y\), as required for a 2-cochain. If
\(c_{ij}^{k}\) are the homogeneous structure constants of \(\mathfrak g\),
the formula determines a linear matrix \(D_n\) for \(f\mapsto\delta f\).
An odd \(f\) has \(2eo\) scalar coefficients.

The inhomogeneous note also writes
\([X,Y]_\gamma=[X,Y]_0+\kappa\gamma(X,Y)\) and asserts that
\(\gamma:\mathfrak g\otimes\mathfrak g\to\mathfrak g\). That assertion alone
does not give \(\gamma\)'s values. The oscillator cross-relations specify
scalar multiples of \(\kappa\), while the note does not define a map
identifying these terms (or their products with oscillator generators)
with vectors in \(\mathfrak g\). Nor does it tabulate the resulting
\(\gamma(X,Y)\) on a basis. The reference to coefficients being “derived”
describes a possible calculation, not its result or a complete rule for
performing it.

There is an additional distinction to preserve: a central scalar-valued
extension cocycle and a cocycle with coefficients in the adjoint module
\(\mathfrak g\) are different coefficient modules. Declaring
\(\kappa\mathfrak g\) to be an abelian extension “by its adjoint
representation” can describe the latter only after the action and the
identification of the \(\kappa\)-coefficient with \(\mathfrak g\) are
specified. The phrase “up to scalar” does not supply that missing
identification.

## Exact linear-algebra criterion, once the missing data exist

Fix an ordered homogeneous basis of \(\mathfrak g\) and the requested
identification of the deformation term with the adjoint module. If the
cochain depends linearly on the parameters, write its coordinate vector as
\[
 \operatorname{vec}(\gamma_{gb})=G_n b,\qquad
 b=(gb_{\sigma,j,s})\in\mathbf C^{4n}.
\]
Let \(D_n\) be the matrix of the displayed coboundary formula in the same
2-cochain coordinates. Then the necessary and sufficient condition is
\[
 \exists u:\ D_nu=G_nb
 \quad\Longleftrightarrow\quad
 \operatorname{rank}(D_n)=\operatorname{rank}[D_n\mid G_nb].
\]
Equivalently, if the rows of \(L_n\) span the left nullspace of \(D_n\),
then \(L_nG_nb=0\). These are usable tests, but \(G_n\) cannot be recovered
from the supplied documents, so they do not reduce to conditions on the
individual \(gb\)'s here. A proposed \(\gamma_{gb}\) must also be checked
to be a 2-cocycle; being a coboundary implies that property, but the
definitions do not provide a basis table to verify it for the proposed
deformation.

For scale clarity, the full space of parity-odd, super-skew bilinear maps
\(\mathfrak g\times\mathfrak g\to\mathfrak g\) has dimension
\[
 q_n=o\binom e2+e^2o+o\binom{o+1}{2}.
\]
This is only the ambient cochain space, not the 2-cocycle space. For the
three requested cases, the dimensions are:

| \(n\) | \((e,o)\) | \(gb\) parameters | odd \(f\) coefficients \(2eo\) | ambient odd 2-cochain coordinates \(q_n\) |
|---:|---:|---:|---:|---:|
| 1 | (4, 4) | 4 | 32 | 128 |
| 2 | (11, 8) | 8 | 176 | 1,696 |
| 3 | (22, 12) | 12 | 528 | 9,516 |

The JSON companion records these arithmetic checks and the missing matrix
data in a machine-readable form. It intentionally marks the structure
constants and \(G_n\) as unavailable rather than inventing them.

## Adjoint representation and “up to scalar”

With adjoint coefficients, \(\delta f\) and \(\gamma\) must be maps taking
values in the *same* \(\mathfrak g\)-module, with coordinates compared in
the same basis. Exact triviality means \(\gamma=\delta f\); it is not
equality only after discarding a scalar or central component. Thus, if
“up to scalar” means equality modulo scalar-valued terms, that is a
different quotient-module problem and needs the scalar submodule and
quotient action to be defined. The supplied definitions do not do so.

If instead “up to scalar” means \(\gamma=\lambda\delta f\) for an
unspecified scalar \(\lambda\), this does not change the nonzero
triviality test: for \(\lambda\ne0\), the image of the linear map
\(\delta\) is closed under nonzero rescaling, so it is equivalent to
\(\gamma\in\operatorname{im}\delta\). Allowing \(\lambda=0\) would
incorrectly classify the zero cochain as a scalar multiple of every
cochain. The well-defined standard condition used in the linear criterion
above is exact equality, with no extra scalar.

## What is needed to finish the parameter classification

The missing inputs are: (1) a basis-level rule identifying the
\(\kappa\)-deformation terms with \(\mathfrak g\) in the claimed adjoint
extension; (2) the resulting coefficients
\(\gamma_{gb}(Z_i,Z_j)\), or an unambiguous derivation rule that produces
them for every parameter; and (3) confirmation that the cochain is
super-skew and satisfies the 2-cocycle equations for the parameter values
under consideration. With these inputs one can construct \(D_n,G_n\) and
apply the rank criterion separately for \(n=1,2,3\). Until then, a claimed
nonzero-triviality classification would not follow from the given
definitions.
