# Triviality of the stated \(C(n+1)\) inhomogeneous deformation

## Conclusion

The supplied definitions do **not** determine necessary and sufficient
conditions on the individual \(gb_{\sigma,j,s}\). In particular, they do not
define a map from those parameters to the adjoint-valued cocycle
\(\gamma_{gb}:\mathfrak g\otimes\mathfrak g\to\mathfrak g\) that appears in the
triviality equation. Consequently, neither a nonzero trivial parameter choice
nor the assertion that only \(gb=0\) is trivial follows from these documents.

The exact criterion, once the missing map is supplied, is
\[
  gb\text{ is trivial}
  \quad\Longleftrightarrow\quad
  \gamma_{gb}\in\operatorname{im}(\delta:
  C^1_{\bar 1}(\mathfrak g;\mathfrak g)\to
  C^2_{\bar 1}(\mathfrak g;\mathfrak g)).
\]
Equivalently, if \(G\) denotes the still-unspecified linear map taking the
parameter vector to cocycle coordinates and \(D\) is the matrix of the
specified coboundary operator, the condition is
\[
  [G\,gb]=0\quad\text{in }\operatorname{coker}D.
\]
This is necessary and sufficient but cannot be reduced to equations in the
\(gb\)'s without \(G\) and the bracket table defining \(D\).

## What is determined by the definitions

The stated dimensions and parameter indexing give the following counts:

| \(n\) | \(\dim\mathfrak g_{\bar 0}\) | \(\dim\mathfrak g_{\bar 1}\) | \(\dim\mathfrak g\) | number of \(gb\)'s | dimension of odd \(\operatorname{Hom}(\mathfrak g,\mathfrak g)\) |
|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 4 | 8 | 4 | 32 |
| 2 | 11 | 8 | 19 | 8 | 176 |
| 3 | 22 | 12 | 34 | 12 | 528 |

Here an odd map has independent blocks
\(\mathfrak g_{\bar 0}\to\mathfrak g_{\bar 1}\) and
\(\mathfrak g_{\bar 1}\to\mathfrak g_{\bar 0}\), so its dimension is
\(2\dim\mathfrak g_{\bar 0}\dim\mathfrak g_{\bar 1}\). This counts possible
unknowns in \(f\); it does not determine the rank or image of \(\delta\).
The structured companion file
[`cn1_inhomogeneous_artifacts.json`](cn1_inhomogeneous_artifacts.json)
records these counts and the missing maps explicitly.

The oscillator relations specify \(4n\) cross-commutator coefficients
\([b_j^s,a_1^\sigma]=-gb_{\sigma,j,s}\kappa\). They do not give the
coefficients of \(\gamma_{gb}(X,Y)\) in a basis of \(\mathfrak g\), nor the
linear map that converts those scalar central terms into
\(\kappa\mathfrak g\). The inhomogeneous-definition document asserts such a
map and an adjoint-valued cocycle but does not define that conversion or give
its coefficients. Thus the parameter count alone cannot decide whether a
nonzero parameter vector has zero image, lies in \(\operatorname{im}\delta\),
or fails to be a cocycle.

## Adjoint representation and “up to scalar”

There are two different targets in the supplied descriptions:

1. The oscillator relation takes values in the one-dimensional central
   direction \(\mathbf C\kappa\).
2. The coboundary formula takes values in \(\mathfrak g\), with the adjoint
   \(\mathfrak g\)-module structure.

The inhomogeneous definition also writes the correction as
\(\kappa\gamma(X,Y)\in\kappa\mathfrak g\), which is a third, adjoint-module
target if \(\kappa\mathfrak g\) is understood as a copy of \(\mathfrak g\).
A scalar central term is not by itself an element of that copy. An explicit
identification or coefficient-extraction rule is required before the
oscillator deformation can be compared with \(\delta f\). Merely calling the
realization an adjoint representation does not supply such a rule.

If “up to scalar” means equality of adjoint-valued cochains with one fixed
nonzero scalar \(\lambda\),
\(\gamma_{gb}=\lambda\,\delta f\), it does not change the coboundary test:
replace \(f\) by \(\lambda f\), since \(\delta\) is linear. It must not mean
independent scalars for different inputs or coordinates; that would be a
different condition. If equality is instead tested only after applying
\(\operatorname{ad}\), the conclusion is equality modulo the center unless
faithfulness of the adjoint representation is also specified. None of these
interpretations repairs the missing map from \(gb\) to \(\gamma_{gb}\).

Under a literal comparison of a central scalar output with an adjoint-valued
output inside a direct sum, the two summands intersect only in zero, so the
only equal correction is zero. This observation is **not** a proof that
\(gb=0\): the definitions do not establish that the map from \(gb\) to the
correction is injective. It also is not a valid substitute for the missing
identification if the intended comparison is between coefficient cochains.

## Internal parity check

The parity declarations also conflict as written. Since \(b_j^s\) is even
and \(a_1^\sigma\) is odd, their bracket is odd. The right-hand side
\(gb_{\sigma,j,s}\kappa\) has parity
\(p(gb_{\sigma,j,s})+1\). For an ordinary homogeneous scalar coefficient
and an odd \(\kappa\), parity compatibility therefore requires
\(p(gb_{\sigma,j,s})=0\), whereas the inhomogeneous-definition document
declares every \(gb\) odd. If \(gb\) is intended as an external odd
parameter, the coefficient-ring and total-parity convention must be stated
and the relation adjusted or explained. As written, this is another reason
the deformation cannot be treated as a well-defined parity-homogeneous
cocycle.

## What a complete parameter-level theorem requires

To decide the question computationally for \(n=1,2,3\), one must supply:

1. A homogeneous basis of \(\mathfrak g\) and its normalized structure
   constants.
2. A precise rule deriving every coordinate
   \(\gamma_{gb}(Z_i,Z_j)\) from the \(gb\)'s, including how a central
   oscillator term becomes an adjoint-valued coefficient.
3. The coefficient-ring/parity convention and the meaning of “up to scalar.”

Then form \(D\), the matrix obtained by applying the provided \(\delta f\)
formula to a basis of odd maps, and \(G\), the matrix of the parameter-to-
cocycle map. The sought set is exactly
\(\{u\in\mathbf C^{4n}:Gu\in\operatorname{im}D\}\), or
\(\ker(QG)\) for any matrix \(Q\) whose kernel is \(\operatorname{im}D\).
This procedure tests the stated necessary-and-sufficient condition without
assuming in advance that the only solution is zero.

## Verification status and scope

For \(n=1,2,3\), the dimension identities, root-count identities, parameter
counts, odd-map dimensions, parity mismatch, and separation of central from
adjoint targets are directly checkable from the supplied documents; the
companion JSON records these claims as structured data. No structure-constant
or gamma-coordinate table is claimed, because neither is provided by the
in-scope files. No external source or workspace was used. The definitive
finding is therefore that the requested parameter-level triviality
classification is **underdetermined by the stated data**, not that a
particular nonzero or zero-only classification has been established.
