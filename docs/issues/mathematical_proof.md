# Triviality of the stated \(C(n+1)\) inhomogeneous deformation

## Conclusion

With the definitions currently supplied, there is **no well-defined necessary
and sufficient condition on the \(gb_{\sigma,j,s}\)** for triviality, and the
question whether a nonzero \(gb\) configuration is trivial has no determined
answer. This is a mathematical under-specification, not a computation that
remains to be run. In particular, the documents do not define the map
\[
  gb\longmapsto\gamma_{gb}\in C^2(\mathfrak g,\mathfrak g)
\]
whose membership in the coboundaries is to be tested.

What is determined is the general test: after fixing a homogeneous basis,
structure constants, and all coefficients of \(\gamma_{gb}\), triviality is
equivalent to a finite linear system expressing \(\gamma_{gb}\) as
\(\delta f\) for an odd \(f\). The machine-readable companion
`docs/issues/cn1_triviality_artifacts.json` records the available input,
parameter indexing, dimensions, and the missing data explicitly. It does not
fill those gaps with guessed coefficients.

## Data verified and scope

The definitions and issue prompt were read from the repository. In particular,
`docs/math/Cn1_definition.md` contains no JSON-schema information. The supplied
definition identifies \(C(n+1)\) with \(\mathfrak{osp}(2|2n)\), gives its even
and odd dimensions, lists root families and oscillator expressions, and
describes a proposed cross-oscillator relation. The coboundary document gives
an odd linear map and a formula for its differential.

The requested cases have the following dimensions and numbers of displayed
parameters:

| \(n\) | \(\dim\mathfrak g_{\bar 0}\) | \(\dim\mathfrak g_{\bar 1}\) | \(\dim\mathfrak g\) | number of \(gb\) symbols |
|---:|---:|---:|---:|---:|
| 1 | 4 | 4 | 8 | 4 |
| 2 | 11 | 8 | 19 | 8 |
| 3 | 22 | 12 | 34 | 12 |

These are dimensions and parameter counts, not bases or structure constants.
The listed oscillator expressions do not give a complete normalized
homogeneous basis with all bracket coefficients in that basis. More
importantly, the inhomogeneous definition says that coefficients
\(\gamma_{abc}\) are “derived” from oscillator relations but supplies neither
those coefficients nor a rule giving them as functions of `gb`. It also does
not fully specify the pre-oscillator form and its compatibility conditions
needed to carry out that derivation. Thus no coefficient matrix for
\(\gamma_{gb}\) can be assembled for \(n=1,2,3\) from the provided material.

## The exact adjoint-coboundary test

Fix a homogeneous basis \(Z_1,\ldots,Z_N\) of \(\mathfrak g\), with parities
\(p_i\), and write
\[
 [Z_i,Z_j]=\sum_k c_{ij}^{\,k}Z_k,\qquad
 f(Z_j)=\sum_r\phi^r_j Z_r.
\]
Oddness of \(f\) requires \(\phi^r_j=0\) unless
\(p_r=p_j+1\pmod 2\). In these coordinates the supplied definition gives
\[
 (\delta f)(Z_i,Z_j)
 =(-1)^{p_i}[Z_i,f(Z_j)]
  -(-1)^{(p_i+1)p_j}[Z_j,f(Z_i)]
  -f([Z_i,Z_j]).
\]
Consequently the coefficient of \(Z_k\) is
\[
 D(\phi)_{ij}^{\,k}
 =(-1)^{p_i}\sum_r\phi^r_j c_{ir}^{\,k}
  -(-1)^{(p_i+1)p_j}\sum_r\phi^r_i c_{jr}^{\,k}
  -\sum_\ell c_{ij}^{\,\ell}\phi^k_\ell.
\]
Once the structure constants and the coefficient functions
\(\Gamma_{ij}^{\,k}(gb)\) of \(\gamma_{gb}\) are specified, the required
conditions are exactly the solvability conditions
\[
  \Gamma_{ij}^{\,k}(gb)=D(\phi)_{ij}^{\,k}
  \quad\text{for all }i,j,k
\]
in the parity-allowed unknowns \(\phi^r_j\). Equivalently, vectorizing
cochains, \(\Gamma(gb)\) must lie in the column space of the matrix \(D\)
representing \(\delta\) on odd 1-cochains. If the map \(gb\mapsto\Gamma(gb)\)
is linear, this becomes a linear system in \(gb\) and \(\phi\); linearity
cannot be verified from the current definition alone.

For the three requested values of \(n\), an odd endomorphism \(f\) has,
respectively, \(2\dim\mathfrak g_{\bar0}\dim\mathfrak g_{\bar1}
=32,176,528\) potentially nonzero scalar entries before any further
constraints. These counts do not resolve the system: its matrix \(D\) requires
the missing structure constants, and its right-hand side requires the
missing \(\Gamma(gb)\).

## Meaning of “adjoint representation / up to scalar”

The phrase “as an adjoint representation” can be made precise only after
identifying the coefficient module. If the intended coefficient module is
the adjoint module \(\mathfrak g\), then both sides of the triviality equation
must be elements of the same cochain space
\(C^2(\mathfrak g,\mathfrak g)\), and equality means equality of every
coefficient in a fixed basis. Merely saying “in the adjoint representation”
does not permit independent rescaling of coefficients or basis vectors.

There is a related notational issue in the inhomogeneous definition: it first
places the deformation term in \(\kappa\mathfrak g\), then calls \(\gamma\)
\(\mathfrak g\)-valued. If \(\kappa\mathfrak g\) is intended as a copy of the
adjoint module, a specific module identification and the parity of the
resulting cochain must be stated. The coboundary formula for odd \(f\) produces
an odd 2-cochain, so the deformation term must be interpreted consistently
with that parity.

If “up to scalar” means one global scalar \(c\), the condition is
\(\gamma=c\,\delta f\). For \(c\ne0\), this is equivalent to exact
coboundarity, since \(\delta\) is linear and \(c\) can be absorbed into \(f\).
For \(c=0\), it only describes the zero cochain. If it instead means a
different scalar for each pair or coefficient, it is not a defined
cohomological equivalence and must not be used as a triviality criterion.
Accordingly, this report uses exact equality in the adjoint coefficient
module, as stated in the coboundary definition, and does not silently impose
an ambiguous “up to scalar” relaxation.

## Internal consistency checks

There is a parity conflict in the stated oscillator relation and its parity
note. For homogeneous \(b_j^s\) even and \(a_1^\sigma\) odd, their
superbracket has parity \(1\). The document declares both \(gb\) and
\(\kappa\) odd, so \(gb\,\kappa\) has parity \(0\), not \(1\). If the relation
is literally an equality in a superalgebra over an even ground field, its
coefficient multiplying odd \(\kappa\) must be even. This needs clarification
before the relation can define a parity-compatible deformation.

The proposed bracket \([X,Y]_\gamma=[X,Y]_0+\kappa\gamma(X,Y)\) also needs an
explicit parity convention for \(\gamma\) and a precise coefficient module.
These are not cosmetic choices: a parity-incompatible term cannot be a
Lie-superalgebra bracket, and the corresponding cochain space affects the
coboundary calculation.

Finally, the issue calls \(\gamma\) a 2-cocycle, but no Jacobi/2-cocycle
constraints on `gb` are given. Even after the coefficient map is provided,
one must verify that the resulting cochain has the claimed parity and
satisfies the 2-cocycle condition before describing it as a deformation
cocycle.

## Definitive finding and next mathematical input

The only unconditional conclusion is the linear-algebra criterion above.
Neither “only \(gb=0\) is trivial” nor “some nonzero \(gb\) is trivial” follows
from the supplied definitions: each assertion requires the unspecified
cochain map and bracket data. The zero-parameter case is trivial if the
intended construction assigns \(\gamma_{gb=0}=0\), but even that assignment
should be stated as part of the construction rather than inferred from the
phrase “defined by the parameters.”

To turn this into a decidable computation for \(n=1,2,3\), the definition must
provide (i) a full homogeneous basis and normalized structure constants,
(ii) all oscillator/pre-oscillator relations and a rule deriving every
\(\Gamma_{ij}^{\,k}(gb)\), (iii) the parity and coefficient-module
identification for the \(\kappa\)-extension, and (iv) the admissible
parameter constraints from super-skew-symmetry and the cocycle/Jacobi
identity. With those inputs, solving
\(\Gamma(gb)=D\phi\) gives the requested necessary and sufficient conditions
without relying on an ambiguous scalar convention.
