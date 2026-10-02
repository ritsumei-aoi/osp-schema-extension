# Triviality of the stated inhomogeneous deformation of \(C(n+1)\)

## Conclusion

The supplied definitions do **not** determine a necessary-and-sufficient
condition on the \(4n\) parameters for triviality as an adjoint-valued
2-cocycle. In particular, they do not define a well-typed map
\(\gamma_{gb}:\mathfrak g\otimes\mathfrak g\to\mathfrak g\) from the
oscillator relations. They describe its correction as a multiple of an odd
element \(\kappa\), whereas the stated coboundary \(\delta f\) takes values in
\(\mathfrak g\). The phrase “as an adjoint representation” / “up to scalar”
does not give an identification between these target spaces.

There is nevertheless a definitive result for the literal direct-sum
interpretation in the definitions: if \(\gamma_{gb}\) is regarded as
\(\mathbb C\kappa\)-valued and \(\delta f\) as \(\mathfrak g\)-valued, equality
in \(\mathfrak g\oplus\mathbb C\kappa\) implies that both sides are zero.
Consequently, triviality in that literal sense is equivalent to
\(\gamma_{gb}=0\) (and \(\delta f=0\) for the chosen witness). This does not,
without an explicit formula for the induced \(\gamma_{gb}\), yield a
necessary-and-sufficient condition on all of the \(gb_{\sigma,j,s}\).
At the level of the displayed oscillator exchange relations themselves, all
those relations are undeformed exactly when every \(gb_{\sigma,j,s}=0\),
assuming \(\kappa\ne0\) and the parameters are independent.

If “up to scalar” is meant to identify \(\mathbb C\kappa\) with
\(\mathfrak g\), the identification (or the actual map into the adjoint
module) is missing. Thus no stronger conclusion about nonzero parameter
configurations follows from the supplied data. In particular, it would be
unsupported to claim that every nonzero \(gb\) is nontrivial or that some
nonzero \(gb\) is a coboundary for the intended adjoint-valued problem.

## What the definitions say

Let \(\mathfrak g=C(n+1)=\mathfrak{osp}(2|2n)\). The algebra definition gives
\[
\dim\mathfrak g_{\bar 0}=2n^2+n+1,\qquad
\dim\mathfrak g_{\bar 1}=4n.
\]
The inhomogeneous-deformation definition gives the \(4n\) exchange
coefficients in
\[
[b_j^s,a_1^\sigma]=-gb_{\sigma,j,s}\,\kappa,
\quad \sigma,s\in\{+,-\},\quad 1\le j\le n,
\]
and identifies \(\kappa\) as odd and central in its oscillator extension.
The coboundary definition instead specifies an odd map
\(f:\mathfrak g\to\mathfrak g\) and the formula
\[
(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]
-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y]).
\]
Every term on the right belongs to \(\mathfrak g\). Therefore
\(\delta f\in\operatorname{Hom}(\mathfrak g\otimes\mathfrak g,\mathfrak g)\),
while the displayed oscillator correction belongs to
\(\operatorname{Hom}(\cdots,\mathbb C\kappa)\), not to that cochain space.
The direct sum has zero intersection between these two summands. If equality
is asserted in that direct sum, its two components must separately vanish.

The inhomogeneous definition also describes
\(L=\mathfrak g\oplus\kappa\mathfrak g\) as an abelian extension by the
adjoint representation. This is not the same target as the central line
\(\mathbb C\kappa\): the adjoint module \(\kappa\mathfrak g\) is generally
not central, since the adjoint action of \(\mathfrak g\) on it is nonzero.
The document does not specify a map taking the oscillator correction into
\(\kappa\mathfrak g\), nor how that is to be compared to the
\(\mathfrak g\)-valued \(\delta f\).

## Grading inconsistency

The oscillator parities in the algebra definition are
\(p(b_j^s)=0\) and \(p(a_1^\sigma)=1\), so the bracket
\([b_j^s,a_1^\sigma]\) has parity \(1\). The inhomogeneous definition assigns
\(p(\kappa)=1\), but also declares each \(gb_{\sigma,j,s}\) to have parity
\(1\). The right side then has parity
\[
p(gb_{\sigma,j,s}\kappa)=1+1=0\pmod 2,
\]
which disagrees with the left side. With \(\kappa\) odd, a homogeneous
coefficient in this relation must be even. If the \(gb\)'s are meant to be
ordinary complex scalars, they are even and the parity equation is consistent
only after removing the document's assertion that they are odd parameters.
This must be resolved before the relations can define a Lie-superalgebra
deformation.

## Meaning of “up to scalar”

There are distinct possible interpretations, and the supplied text does not
choose one:

1. **Equality in the stated direct sum.** Here
   \(\gamma_{gb}\in\mathbb C\kappa\) and \(\delta f\in\mathfrak g\). Their
   equality forces both to be zero. At the oscillator-relation level this
   forces every \(gb_{\sigma,j,s}=0\), provided \(\kappa\ne0\) and the
   coefficients are independent. This is a target-space observation, not a
   computation of the induced \(\mathfrak g\)-valued cocycle.
2. **An unspecified identification with the adjoint module.** If the
   correction is meant to land in \(\kappa\mathfrak g\), its coefficients
   must specify the vector in \(\mathfrak g\) multiplying \(\kappa\), as well
   as the action and parity conventions. No such data are provided, so the
   equation \(\gamma_{gb}=\delta f\) cannot be formed.
3. **Equality modulo a scalar or after projection.** A projection, quotient,
   scalar normalization, or module map must be stated. Different choices can
   change the kernel and hence the triviality conditions. A scalar factor
   alone does not repair a mismatch of target spaces.

No result for the intended adjoint-module reading should be inferred by
silently choosing one of these identifications.

## General computational test once the missing data are fixed

For a homogeneous basis \(e_i\) of \(\mathfrak g\), write
\([e_i,e_j]=\sum_k c_{ij}^{k}e_k\), and write an odd map as
\(f(e_j)=\sum_l F^l_j e_l\), with \(F^l_j=0\) unless
\(p(e_l)=p(e_j)+1\). The coefficient of \(e_k\) in the specified
coboundary is
\[
(\delta f)_{ij}^{k}
=(-1)^{p(e_i)}\sum_l F^l_j c_{i l}^{k}
-(-1)^{(p(e_i)+1)p(e_j)}\sum_l F^l_i c_{j l}^{k}
-\sum_l c_{ij}^{l}F^k_l.
\]
Thus, once actual structure constants and a well-typed coefficient tensor
\(\gamma_{gb,ij}^{k}\) are supplied, triviality is exactly solvability of the
linear system
\[
D F=\gamma_{gb}.
\]
To test all \(n=1,2,3\) cases, one must build that system for each algebra and
substitute the explicit parameter-to-cochain map. The supplied documents give
neither the full structure-constant table in a fixed basis nor this map.
Accordingly, the computations below verify the dimension counts and expose
the grading/target-space obstructions; they do not purport to solve an
undefined linear system.

## Checks for \(n=1,2,3\)

| \(n\) | \(\dim\mathfrak g_{\bar0}\) | \(\dim\mathfrak g_{\bar1}\) | \(gb\) parameters | Result from supplied definitions |
|---:|---:|---:|---:|---|
| 1 | 4 | 4 | 4 | Same target-space and parity obstructions |
| 2 | 11 | 8 | 8 | Same target-space and parity obstructions |
| 3 | 22 | 12 | 12 | Same target-space and parity obstructions |

The dimension and parameter counts agree with the formulas in the algebra
and deformation definitions. The grading contradiction and the distinct
coboundary/deformation codomains are independent of \(n\), so all three
cases fail the same consistency checks. No \(n\)-specific structure constants
can remove these type-level contradictions.

## Requirements for a definitive adjoint-valued criterion

To determine whether any nonzero parameter configuration is a coboundary,
the mathematical specification must first provide:

* a consistent parity for \(gb\), \(\kappa\), and the deformed bracket;
* the exact coefficient module and whether \(\kappa\) is central or denotes
  the parity-shifted adjoint module \(\kappa\mathfrak g\);
* the explicit map from every deformed oscillator relation to
  \(\gamma_{gb}(X,Y)\), for a stated basis of \(\mathfrak g\);
* the meaning of “up to scalar,” including the map or quotient defining that
  comparison; and
* the structure constants and signs in that same basis.

After those choices are made, the displayed linear system gives a finite,
reproducible necessary-and-sufficient test. The machine-readable companion
`cn1_triviality_artifacts.json` records all values derivable now, and
`verify_cn1_artifacts.py` checks them without external dependencies.

## Scope and provenance

This report uses only the three mathematical definitions and issue text in
this repository. No external source, external repository, or other local
workspace was accessed. No unprovided structure constants, oscillator
normal-ordering rules, or parameter-to-cocycle coefficients have been
invented.
