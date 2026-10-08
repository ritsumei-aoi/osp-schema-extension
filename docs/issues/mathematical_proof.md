# Triviality of the stated \(C(n+1)\) inhomogeneous deformation

## Conclusion

The materials supplied in this repository do **not** define a map from the
\(4n\) parameters \(gb_{\sigma,j,s}\) to an adjoint-valued 2-cochain
\(\gamma_{gb}\). Consequently they do not determine necessary and sufficient
conditions on those parameters for triviality, for \(n=1,2,3\) or in general.
In particular, the claim that only the zero parameter configuration is
trivial, or that some nonzero configuration is trivial, cannot be proved from
these definitions.

This is a definitive conclusion about the stated problem: it is
underdetermined (and has a parity inconsistency), rather than a theorem that
the trivial locus is zero or nonzero. A machine-readable record of the data
and the missing definitions is in
[`verification_artifacts.json`](verification_artifacts.json).

## What triviality would mean

Let \(\mathfrak g=C(n+1)\), and let \(C^q(\mathfrak g;\mathfrak g)\) denote
adjoint-valued cochains. The specified odd coboundary operator is the map
\[
D_{\mathfrak g}:C^1_{\bar 1}(\mathfrak g;\mathfrak g)\longrightarrow
C^2_{\bar 1}(\mathfrak g;\mathfrak g)
\]
whose value on an odd linear map \(f\) is
\[
(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]
-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y]).
\]
Each term has parity \(p(X)+p(Y)+1\), so this is an odd 2-cochain, as
required for a coefficient multiplying an odd \(\kappa\).

If the deformation data were made explicit, they would give a map
\[
G_n:P_n\longrightarrow C^2_{\bar 1}(\mathfrak g;\mathfrak g),
\qquad \dim P_n=4n,
\]
where \(G_n(gb)=\gamma_{gb}\). The exact necessary-and-sufficient condition
would then be
\[
gb\text{ is trivial}\quad\Longleftrightarrow\quad
G_n(gb)\in\operatorname{im}D_{\mathfrak g}.
\]
Equivalently, if \(D_n\) and \(G_n\) are matrices in specified homogeneous
bases, solve \(D_n f=G_n gb\); the trivial parameter locus is
\(G_n^{-1}(\operatorname{im}D_n)\). The oscillator realization gives a
route to derive the undeformed structure constants, but the repository does
not tabulate \(D_n\), and—decisively—does not give the coordinates of
\(G_n\). Merely naming \(\gamma_{gb}\) a 2-cocycle does not specify that
map.

## Adjoint representation and “up to scalar”

The expression \([X,Y]_0+\kappa\gamma(X,Y)\) belongs to an extension with a
\(\kappa\mathfrak g\) summand, not to \(\mathfrak g\) alone. For the comparison
with a coboundary to be meaningful, the extension must be specified as a
direct sum (or otherwise supplied with an explicit identification), and the
comparison must be made in the coefficient of that summand:
\[
\kappa\gamma(X,Y)=\kappa(\delta f)(X,Y)
\quad\Longleftrightarrow\quad
\gamma(X,Y)=(\delta f)(X,Y).
\]
This uses that the map \(u\mapsto\kappa u\) is injective in the stipulated
copy of \(\kappa\mathfrak g\). It does not identify an element of
\(\kappa\mathfrak g\) with an element of \(\mathfrak g\) without that
coefficient comparison.

If “up to scalar” means allowing a fixed **nonzero** scalar multiple, the
criterion is unchanged: \(\lambda\gamma\in\operatorname{im}D_{\mathfrak g}\)
for \(\lambda\ne0\) is equivalent to
\(\gamma\in\operatorname{im}D_{\mathfrak g}\), since the image is a linear
subspace. Allowing \(\lambda=0\) would make the condition vacuous and is not
a valid triviality criterion. The phrase cannot supply the missing
parameter-to-cochain map.

## Defects in the supplied definitions

1. **No parameter-to-cochain rule.** The inhomogeneous definition gives the
   oscillator exchange relation
   \([b_j^s,a_1^\sigma]=-gb_{\sigma,j,s}\kappa\), but supplies no formula for
   the resulting values \(\gamma_{gb}(X,Y)\) on a homogeneous basis of
   \(\mathfrak g\). In particular, it gives no \(\gamma\)-components or
   coefficient extraction rule for the quadratic oscillator generators.
2. **Parity mismatch.** Here \(p(b)=0\), \(p(a)=1\), and \(p(\kappa)=1\), so
   the left side of the exchange relation is odd. If \(gb\) has the asserted
   parity 1, then \(p(gb\cdot\kappa)=1+1=0\), which is even. With a central
   odd \(\kappa\), a homogeneous coefficient in this relation must instead
   be even. Over the ordinary base field \(\mathbb C\), there are no nonzero
   odd scalar coefficients in the first place. A coefficient superalgebra
   and a consistent parity convention would have to be stated.
3. **Extension not fixed sufficiently for the calculation.** The text calls
   \(\kappa\) central, then describes an abelian extension
   \(\mathfrak g\oplus\kappa\mathfrak g\) by the adjoint representation.
   These statements can coexist only after specifying which element is
   central (a scalar \(\kappa\), or the action on the shifted copy) and the
   extension bracket and parity conventions. Those data are not supplied.
4. **Cocycle status is asserted, not verified.** No component formula or
   Jacobi/cocycle calculation is supplied from which one could check that
   the oscillator deformation induces a 2-cocycle on \(\mathfrak g\).

The listed dimensions and oscillator realizations identify useful starting
data, but do not repair these omissions. In particular, the same
parameter-space dimension \(4n\) does not determine the map \(G_n\).

## Scope of computational evidence

For \(n=1,2,3\), the documents supply respectively dimensions \(8,19,34\)
and \(4,8,12\) deformation labels. Those counts are recorded in the JSON
artifact. The artifact records that the full structure-constant arrays are
not tabulated (although they are in principle derivable from the stated
oscillator realization), and that the actual \(G_n\) component arrays are
absent. Writing invented zero \(\gamma\)-components would falsely imply a
calculation. Thus no rank test for \(D_n\), no comparison
\(D_nf=G_ngb\), and no nonzero-parameter witness is claimed. The artifact
supports the conclusion of underdetermination by making explicit both the
given inputs and the absent map required to test triviality.

## Data needed to finish a classification

A determinate computation requires: (i) a parity-consistent coefficient
algebra and deformed oscillator relations; (ii) a fixed homogeneous basis,
normalization, and complete bracket/extension conventions; (iii) explicit
coordinates of \(\gamma_{gb}(X,Y)\) for every basis pair, derived from those
relations; and (iv) verification of the cocycle identity. With these, one
can form the coboundary matrix from the displayed \(\delta f\), solve
\(D_nf=G_ngb\) for each \(n\), and report the resulting kernel/image
conditions. No external sources or workspaces were used.
