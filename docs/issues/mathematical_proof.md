# Triviality of the stated \(C(n+1)\) inhomogeneous deformation

## Conclusion

With the parity assignments in the supplied definitions taken literally, the only
admissible parameter choice is
\[
  \mathrm{gb}_{\sigma,j,s}=0
  \qquad (1\leq j\leq n,\ \sigma,s\in\{+,-\}).
\]
It gives \(\gamma_{gb}=0=\delta 0\), so it is trivial. No nonzero configuration
is a deformation in the stated Lie-superalgebra sense, and hence none can be
classified as a nonzero trivial deformation under those definitions. This
conclusion applies for \(n=1,2,3\), and the parity obstruction is independent of
\(n\).

This is a consistency conclusion, not a computation of
\(H^2(C(n+1),C(n+1))\). The provided documents do not define enough data for
such a cohomology computation or for a structure-constant-by-structure-constant
test of \(\gamma_{gb}=\delta f\). In particular, they do not supply a complete
homogeneous basis and bracket table for \(\mathfrak g\), nor a precise map from
the displayed oscillator relations to all values
\(\gamma_{gb}(X,Y)\in\mathfrak g\). A stronger nonzero-parameter triviality
theorem would require those items and a correction or clarification of the
parity issue below.

## Startup file verification

All six requested files were present and read: `docs/math/Cn1_definition.md`,
`docs/math/C_inhomogeneous_definition.md`,
`docs/math/C_coboundary_definition.md`, `docs/issues/issue_open.md`,
`final_reflection_template.md`, and `supplementary_metrics_template.md`.
`docs/math/Cn1_definition.md` contains no JSON schema information. No external
sources were accessed.

## Parity obstruction

The inhomogeneous-definition document assigns
\[
p(b_j^s)=0,\qquad p(a_1^\sigma)=1,\qquad p(\kappa)=1,\qquad
p(\mathrm{gb}_{\sigma,j,s})=1
\]
and imposes
\[
[b_j^s,a_1^\sigma]=-\mathrm{gb}_{\sigma,j,s}\,\kappa.
\]
A Lie-superalgebra bracket is homogeneous of degree zero, so the left-hand side
must have parity \(0+1=1\). The right-hand side has parity
\(1+1=0\). The two sides therefore have different parity. In a parity-graded
algebra, equality of homogeneous elements of distinct degrees forces both
components to vanish. Since \(\kappa\) is specified as a nonzero central
generator of the extension, and the parameters are independent, the relation
can hold homogeneously only when every \(\mathrm{gb}_{\sigma,j,s}=0\).

This argument uses the usual free coefficient interpretation for the
independent parameters and the stated nonzero extension generator. If the
parameters were intended to be even instead, the displayed oscillator
relation would have the expected odd parity, but that would change the supplied
parity declaration. It would not, by itself, repair the missing definition of
the full cochain \(\gamma_{gb}\).

The dimensions and numbers of parameters involved are:

| \(n\) | \(\dim \mathfrak g_{\bar 0}\) | \(\dim \mathfrak g_{\bar 1}\) | number of \(gb\) parameters |
|---:|---:|---:|---:|
| 1 | 4 | 4 | 4 |
| 2 | 11 | 8 | 8 |
| 3 | 22 | 12 | 12 |

The obstruction is identical for each of the \(4n\) relations; no exceptional
case arises for these values of \(n\).

## Meaning of “adjoint representation / up to scalar”

The inhomogeneous definition writes a bracket deformation in the form
\([X,Y]_\gamma=[X,Y]_0+\kappa\,\gamma(X,Y)\) and describes the extension as
\(\mathfrak g\oplus\kappa\mathfrak g\). In that formulation, \(\gamma\) is the
coefficient of the \(\kappa\mathfrak g\) component and should be compared with
\(\delta f\) as an element of
\(\operatorname{Hom}(\Lambda^2\mathfrak g,\mathfrak g)\), pair by pair.
“Up to scalar” cannot mean equality only up to an arbitrary scalar while also
being the stated triviality condition: a scalar multiple is a different
cochain unless the normalization of the deformation or of \(f\) is explicitly
changed. The exact condition is \(\gamma(X,Y)=(\delta f)(X,Y)\) for every
homogeneous pair, with the same coefficient convention on both sides.

There is also a target-space gap in the supplied construction. The displayed
oscillator relation has scalar-\(\kappa\) output, whereas an adjoint
2-cochain in the stated extension must have \(\kappa\mathfrak g\)-valued
output. A specified oscillator-to-adjoint identification is needed to infer
all \(\gamma(X,Y)\) from those relations. The machine-readable artifact records
the relations that are actually provided and does not invent unprovided
structure constants.

The coboundary formula in `C_coboundary_definition.md` is well defined once
the bracket table and the odd linear map \(f\) are fixed. At the only
parity-admissible parameter point found here, \(\gamma=0\), take \(f=0\);
the formula gives \(\delta f=0\) identically. This proves sufficiency as well
as necessity under the stated homogeneous bracket requirement.

## Reproducible verification artifact

`docs/issues/cn1_inhomogeneous_verification.json` records, for \(n=1,2,3\),
the dimensions from the supplied \(C(n+1)\) definition, the \(4n\)
parameter labels, the parity of each side of the oscillator relation, and
the resulting zero-parameter condition. It also records the generic
coboundary formula and the scope limitation: the provided definitions do not
specify a full structure-constant tensor or a full \(\gamma_{gb}\) table. The
artifact therefore supports the parity theorem and enables an independent
check of the input counts without presenting fabricated cochain data as a
computation.

## What would be needed for a nonzero-parameter classification

To determine whether nonzero parameters are coboundaries in a corrected
version of the problem, the definitions must specify at least:

1. A consistent parity for the parameters and central generator (and the
   coefficient superalgebra, if parameters are odd).
2. A fixed homogeneous basis of \(\mathfrak g\) with all normalized structure
   constants.
3. The explicit map assigning every pair \((X,Y)\) its
   \(\mathfrak g\)-valued coefficient \(\gamma_{gb}(X,Y)\).
4. Whether “up to scalar” is intended to alter the equality relation or only
   describe extraction of the \(\kappa\)-coefficient.

Once provided, triviality is a finite linear system in the coefficients of
the odd map \(f\), with one equation for every basis pair and output
coordinate. The present documents do not determine that system.
