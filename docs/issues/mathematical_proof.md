# Triviality of the stated \(C(n+1)\) inhomogeneous deformation

## Conclusion

The documents in this repository do **not** determine necessary and sufficient
conditions on the \(4n\) parameters \(gb_{\sigma,j,s}\), nor do they determine
whether a nonzero parameter configuration is trivial. This is an
underdetermination result, not a claim that nonzero deformations are
nontrivial (or that they are all trivial).

The exact criterion available from the definitions is the finite-dimensional
linear condition
\[
  \operatorname{vec}(\gamma_{gb}) \in \operatorname{im}(D_n),
\]
where \(D_n\) is the matrix of the stated coboundary operator on odd linear
maps. Equivalently,
\[
  \operatorname{rank}[D_n\mid\operatorname{vec}(\gamma_{gb})]
  =\operatorname{rank}(D_n).
\]
This is necessary and sufficient once the bracket table of
\(\mathfrak g=C(n+1)\) and the actual coefficient table for \(\gamma_{gb}\)
are specified. Neither table is present in the supplied documents, so this
criterion cannot be reduced there to explicit equations in \(gb\).

In particular, the data given do not justify either proposed definitive
parameter answer \(gb=0\) only, or arbitrary \(gb\). The zero configuration
is trivial if, as the stated deformation construction implies, setting all
deformation parameters to zero gives \(\gamma_0=0\); it is the only
configuration whose triviality follows without further bracket data.

There is also a parity obstruction in the stated oscillator relation itself.
With the parities specified in `Cn1_definition.md` and
`C_inhomogeneous_definition.md`, \(p(b_j^s)=0\), \(p(a_1^\sigma)=1\), and
\(p(\kappa)=1\). Hence the left side of
\[
  [b_j^s,a_1^\sigma]=-gb_{\sigma,j,s}\,\kappa
\]
has parity \(1\), while its right side has parity \(1+1=0\), because the
document declares \(gb_{\sigma,j,s}\) odd. In a homogeneous superalgebra,
an odd element cannot equal an even element except when both are zero.
Thus, read literally, the relation permits only \(gb_{\sigma,j,s}\kappa=0\)
for every index; the documents do not specify a parameter algebra or an
annihilator condition from which this could be turned into \(gb=0\).
Making \(gb\) even would repair this particular relation, but would change
the stated parity declaration. No such repair is assumed here. This
inconsistency independently prevents treating the displayed \(gb\)-family
as a well-defined nonzero homogeneous deformation.

## What is specified and what is missing

The definitions specify the dimensions
\[
  \dim \mathfrak g_{\bar 0}=2n^2+n+1,\qquad
  \dim \mathfrak g_{\bar 1}=4n,
\]
the \(4n\) names \(gb_{\sigma,j,s}\), and a formula for \(\delta f\) for an
odd map \(f:\mathfrak g\to\mathfrak g\). They do not specify:

1. a homogeneous basis of \(\mathfrak g\) together with its complete bracket
   constants in that basis;
2. the full oscillator algebra and its sign conventions (including the
   action/brackets involving \(K\) and \(\kappa\));
3. the resulting coefficient map \(gb\mapsto\gamma_{gb}(X,Y)\) on pairs of
   basis elements; or
4. a parameter coefficient superalgebra resolving the parity mismatch above;
   or
5. verification that this coefficient map is a 2-cocycle with the stated
   module and parity conventions.

The root list and generator expressions in `Cn1_definition.md` do not fill
these gaps: they do not provide a complete, normalized bracket table for a
basis of the finite-dimensional superalgebra, and the inhomogeneous
definition only says that the \(\gamma\) coefficients are to be derived.
That instruction is not itself a definition of those coefficients. A
rank computation for \(n=1,2,3\) would therefore require inventing missing
mathematical input and could not constitute verification of the requested
deformation.

## Linear-algebra criterion

Fix a homogeneous basis \(Z_1,\dots,Z_m\), let \(p_i\in\{0,1\}\) denote its
parities, and write
\[
 [Z_a,Z_b]=\sum_k c_{ab}^{k}Z_k,\qquad
 \gamma_{gb}(Z_a,Z_b)=\sum_k q_{ab}^{k}(gb)Z_k.
\]
An odd \(f\) has coefficients \(F_{ij}\) only when \(p_i\ne p_j\), since
\(f(Z_j)=\sum_{i:p_i\ne p_j}F_{ij}Z_i\). Substitution into the coboundary
definition gives
\[
 (\delta f)(Z_a,Z_b)=
 (-1)^{p_a}\sum_i F_{ib}[Z_a,Z_i]
 -(-1)^{(p_a+1)p_b}\sum_i F_{ia}[Z_b,Z_i]
 -\sum_\ell c_{ab}^{\ell} f(Z_\ell).
\]
This expression is linear in the allowed \(F_{ij}\); its coefficient matrix
is \(D_n\). Thus triviality is exactly solvability of \(D_nF=q(gb)\).
If \(q(gb)\) is linear in the parameters, this is a linear system in the
parameters after eliminating \(F\), but the elimination equations depend on
the missing \(c_{ab}^k\) and \(q_{ab}^k\).

The reusable exact-rational checker is
`docs/issues/verify_coboundary.py`. Its input format and limitations are
recorded in `docs/issues/mathematical_proof_artifacts.json`. It checks the
stated coboundary equality for supplied tables; it does not manufacture the
missing tables or certify the 2-cocycle identity.

## “Adjoint representation / up to scalar”

The phrase in `C_coboundary_definition.md` is handled as follows. “Adjoint
representation” identifies the coefficient module: the output of the
cochain takes values in \(\mathfrak g\) with its adjoint action. It does not
change the equality of bilinear maps and does not supply an additional
freedom to conjugate their values.

The definition first states the exact equality \(\gamma=\delta f\), then
adds “up to scalar.” If this means equality up to one global scalar
\(\lambda\), it does not change the triviality criterion: for
\(\lambda\ne0\), \(\lambda\delta f=\delta(\lambda f)\), and for
\(\lambda=0\) the resulting zero cochain is already \(\delta 0\).
Accordingly the checker tests exact equality. A component-dependent scalar,
or equivalence under an unspecified representation isomorphism, is not a
defined coboundary condition and cannot be inferred from that phrase.

There is also a parity convention to keep explicit. An odd \(f\) has an odd
coboundary under the given formula. Since the central symbol \(\kappa\) is
declared odd, the coefficient \(\gamma\) in a term \(\kappa\gamma\) must
have parity \(p(X)+p(Y)+1\) for that term to have the same parity as a
bracket. The checker enforces the output parity of the stated odd
coboundary; the input \(\gamma\) table must use that convention. The
checker uses rational coefficients and so cannot represent the declared
odd \(gb\) parameters or resolve their parity conflict.

## Computational status for \(n=1,2,3\)

The artifact records the documented dimensions and parameter labels for
each of these ranks, and distinguishes them from data that are not supplied.
No structure constants or evaluated \(\gamma\) entries have been fabricated.
Consequently there is no valid numerical rank/nullspace result for any of
the three ranks. Running the checker on complete, independently validated
tables will return whether a *particular rational-valued evaluated*
\(\gamma\) is a
coboundary and, when it is, one odd map \(f\) witnessing that fact. To
derive parameter conditions, the same computation must be done with
symbolic parameter entries or repeated over a sufficient set of parameter
values together with a justified linearity argument, after first specifying
a parity-consistent parameter algebra.

No external sources or workspaces were used. This conclusion is restricted
to the contents of this repository and does not assert a general rigidity or
cohomology theorem for \(\mathfrak{osp}(2|2n)\).
