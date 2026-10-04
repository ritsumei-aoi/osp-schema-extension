# Triviality of the stated \(C(n+1)\) inhomogeneous deformation

## Conclusion

The supplied definitions do **not** determine necessary and sufficient conditions on the \(gb_{\sigma,j,s}\), and they do not determine whether any nonzero \(gb\)-configuration is trivial. In particular, they do not define an explicit map
\[
\Gamma_n:\mathbb C^{4n}\longrightarrow C^2_{\bar 1}(\mathfrak g,\mathfrak g),
\qquad gb\longmapsto\gamma_{gb},
\]
whose image could be compared with the coboundaries. This is a genuine missing mathematical input, not a computational gap. The data and dimensions that are specified, along with the missing inputs, are recorded in `docs/issues/c_n1_triviality_audit.json`.

The exact conditional answer is as follows. Once a homogeneous basis, structure constants, and the map \(\Gamma_n\) are specified, let \(D_n\) be the matrix of the stated coboundary operator on odd endomorphisms. Then
\[
\gamma_{gb}\text{ is trivial}\quad\Longleftrightarrow\quad
D_n x=G_n\,gb\text{ is consistent},
\]
where \(G_n\) is the matrix of \(\Gamma_n\) and \(x\) is the coordinate vector of an odd linear map \(f\). Equivalently,
\[
\operatorname{rank}(D_n)=\operatorname{rank}\bigl[D_n\mid G_n\,gb\bigr].
\]
If \(L_n\) has rows forming a basis of the left nullspace of \(D_n\), this is precisely \(L_nG_n\,gb=0\). These equations are necessary and sufficient, but the present documents do not provide \(D_n\) or \(G_n\) in coordinates, so they cannot be reduced to conditions on the individual \(gb\)'s.

## What is specified

The definition identifies \(\mathfrak g=C(n+1)=\mathfrak{osp}(2|2n)\), gives its even and odd dimensions
\[
m=\dim\mathfrak g_{\bar 0}=2n^2+n+1,\qquad
q=\dim\mathfrak g_{\bar 1}=4n,
\]
and lists \(4n\) parity-1 parameters \(gb_{\sigma,j,s}\). The oscillator exchange relation supplied is
\[
[b_j^s,a_1^\sigma]=-gb_{\sigma,j,s}\,\kappa.
\]
The coboundary document specifies an odd map \(f:\mathfrak g\to\mathfrak g\) and, for homogeneous \(X,Y\), the formula
\[
(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]
-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y]).
\]
Thus, if \(f\) is odd, its only possible matrix blocks are
\(\mathfrak g_{\bar0}\to\mathfrak g_{\bar1}\) and
\(\mathfrak g_{\bar1}\to\mathfrak g_{\bar0}\). Its parameter space has dimension \(2mq\): respectively \(32,176,528\) for \(n=1,2,3\).

For reference, the space of all odd, super-skew bilinear maps
\(\mathfrak g\otimes\mathfrak g\to\mathfrak g\) has dimension
\[
q\left(\binom m2+\binom{q+1}2\right)+m^2q.
\]
The three terms count even-even inputs, odd-odd inputs, and mixed inputs, with output parity opposite to the input parity. Its dimensions for \(n=1,2,3\) are \(128,1696,9516\), respectively. These are ambient cochain-space dimensions, not claims about the cocycle subspace or the dimension of the image of \(\delta\).

## Why the stated data do not define \(\Gamma_n\)

1. The inhomogeneous definition gives a relation with value in the one-dimensional central direction \(\mathbb C\kappa\), but then asserts a \(\mathfrak g\)-valued cocycle and an extension involving \(\kappa\mathfrak g\). It gives no identification, projection, or coefficient rule converting the central oscillator terms into elements of \(\mathfrak g\). A central scalar multiple and a vector in the adjoint module are different targets until such a rule is specified.
2. It says that coefficients \(\gamma_{abc}\) are obtained by substituting oscillator generators and evaluating brackets, but gives neither those coefficients nor a rule for which pairs of \(\mathfrak g\)-generators are to be evaluated and how the result is expressed in a fixed basis. Consequently the \(4n\) oscillator relations do not specify the \(4n\) cochain columns of \(G_n\).
3. No structure-constant table in a basis of \(\mathfrak g\) is supplied to construct the matrix of \(\delta\). The root and oscillator descriptions give dimensions and generators, but not a complete, consistently normalized coordinate table for this calculation. In particular, the displayed simple-root formula for \(E_{2\delta_n}\) has a factor \(1/2\), whereas the later all-root formula gives \(E_{\pm2\delta_k}=(b_k^\pm)^2\). A normalization convention must be fixed before using these as coordinate structure constants.
4. Calling \(\gamma\) a 2-cocycle does not specify which cocycle is associated to a given parameter vector, nor whether the oscillator construction yields a cocycle for every vector. Cocycle status alone cannot replace the missing map \(gb\mapsto\gamma_{gb}\).

These omissions prevent testing the requested cases \(n=1,2,3\) beyond the dimension and indexing checks above. It would be unjustified to report either “only \(gb=0\)” or “some nonzero \(gb\) is trivial.”

## Adjoint representation and “up to scalar”

The coboundary definition says equality as an adjoint-representation cochain, while also saying “up to scalar”; it does not define the scalar convention. The mathematically coherent interpretations are:

- **Exact equality in \(\mathfrak g\).** Compare \(\gamma_{gb}(X,Y)\) with \((\delta f)(X,Y)\) as vectors. This is the equality used in the matrix criterion above.
- **Equality after applying the adjoint representation.** Compare \(\operatorname{ad}(\gamma_{gb}(X,Y))\) and \(\operatorname{ad}((\delta f)(X,Y))\). This implies vector equality when the adjoint representation is faithful (equivalently, the center is zero). If it is not faithful, it only gives equality modulo the center. The supplied text does not state the faithfulness convention, though the exact-vector interpretation avoids needing it.
- **One fixed nonzero scalar for the entire cochain.** If \(\gamma_{gb}=\lambda\,\delta f\) for a single \(\lambda\ne0\), this does not change triviality: replace \(f\) by \(\lambda f\), since \(\delta\) is linear. This is the only ordinary “up to scalar” reading that can be absorbed without changing the question.

A scalar chosen separately for each input pair is not equality of cochains up to a scalar and does not define the stated coboundary condition. Allowing the scalar to be zero would make the condition vacuous. Therefore the report uses exact vector equality (or, equivalently, one fixed nonzero overall scalar).

There is an additional parity consistency check: since \(\kappa\) is declared odd, the term \(\kappa\gamma(X,Y)\) has the parity of a bracket only if \(\gamma\) is odd as a cochain. This agrees with the specified odd \(f\) and odd \(\delta f\), but does not determine the missing coefficients of \(\gamma\).

## Computational verification path

The accompanying JSON artifact is a machine-readable record of the data actually fixed in the definitions: dimensions, parameter labels, cochain-coordinate counts, the formal coboundary equation, and explicit `null` entries wherever required matrices are not specified. It deliberately does not fabricate structure constants or gamma coefficients.

To complete the requested computation, supply a single consistent ordered homogeneous basis and its structure constants, resolve the oscillator normalization, and give the explicit coefficient rule for every \(\gamma_{gb}(Z_i,Z_j)\). One can then build \(D_n\) directly from the displayed \(\delta f\) formula, build \(G_n\) by evaluating the coefficient rule on each parameter basis vector, and compute \(L_nG_n\). The rows of that matrix give the desired necessary and sufficient linear conditions on \(gb\), and its kernel determines whether any nonzero configurations are trivial.

No external sources or files outside this repository were consulted.
