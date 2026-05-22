# Triviality of the \(C(n+1)\) Inhomogeneous Deformation

## Statement

Let \(\mathfrak g=C(n+1)\cong \mathfrak{osp}(2|2n)\), with odd generators
\[
Q_{\sigma,j,s}:=a_1^\sigma b_j^s
\quad
(\sigma\in\{+,-\},\ j=1,\dots,n,\ s\in\{+,-\}),
\]
and even bosonic quadratic generators
\[
S_{(j,s),(k,t)}:=b_j^s b_k^t.
\]
Let
\[
J:=\sum_{r=1}^{n+1}H_r=a_1^+a_1^- - \tfrac12,
\]
the \(\mathfrak{so}(2)\) Cartan element in the oscillator realization.

The inhomogeneous deformation is given by
\[
[b_j^s,a_1^\sigma]_\gamma=-\,gb_{\sigma,j,s}\,\kappa,
\]
equivalently
\[
[X,Y]_\gamma=[X,Y]_0+\kappa\,\gamma_{gb}(X,Y).
\]

**Theorem.**
For every \(n\ge 1\) and every choice of the \(4n\) parameters \(gb_{\sigma,j,s}\), the corresponding inhomogeneous deformation is trivial in the sense of `docs/math/C_coboundary_definition.md`.

Equivalently, the necessary and sufficient triviality condition is:

\[
\boxed{\text{no restriction at all on the } gb_{\sigma,j,s}.}
\]

So there are **no nontrivial inhomogeneous deformation classes** of this type: every \(gb\)-configuration is a coboundary.

## 1. First-order gauge transformation on oscillators

Work to first order in the odd central parameter \(\kappa\), exactly as in the deformation ansatz
\[
[X,Y]_\gamma=[X,Y]_0+\kappa\,\gamma(X,Y).
\]

Define new oscillator variables by
\[
\widetilde a_1^\pm:=a_1^\pm,
\qquad
\widetilde b_j^s:=b_j^s-\kappa\bigl(gb_{+,j,s}\,a_1^-+gb_{-,j,s}\,a_1^+\bigr).
\]

Using the undeformed CAR relation
\[
[a_1^-,a_1^+]_0=\{a_1^-,a_1^+\}=1,
\]
and \([a_1^\pm,a_1^\pm]_0=0\), one gets
\[
[\widetilde b_j^s,\widetilde a_1^\sigma]_0
=
[\widetilde b_j^s,a_1^\sigma]_0
=
-\,gb_{\sigma,j,s}\,\kappa.
\]

Thus the deformed oscillator relation is obtained from the undeformed one by the even first-order change of variables
\[
T=\mathrm{id}+\kappa f.
\]
Therefore the deformation is gauge-equivalent to the original oscillator presentation.

## 2. Induced odd map \(f\) on \(\mathfrak g\)

Passing from oscillators to quadratic generators gives the induced odd linear map \(f:\mathfrak g\to\mathfrak g\) (up to scalar, explained below).

### 2.1 Bosonic quadratic generators

For \(S_{(j,s),(k,t)}=b_j^s b_k^t\),
\[
\widetilde S_{(j,s),(k,t)}
=
\widetilde b_j^s\widetilde b_k^t
=
S_{(j,s),(k,t)}+\kappa f\!\left(S_{(j,s),(k,t)}\right),
\]
with
\[
f\!\left(S_{(j,s),(k,t)}\right)
=
-\,gb_{+,j,s}\,Q_{-,k,t}
-\,gb_{-,j,s}\,Q_{+,k,t}
-\,gb_{+,k,t}\,Q_{-,j,s}
-\,gb_{-,k,t}\,Q_{+,j,s}.
\]

This indeed sends even generators to odd generators.

### 2.2 Odd generators

For \(Q_{+,j,s}=a_1^+b_j^s\),
\[
\widetilde Q_{+,j,s}
=
a_1^+\widetilde b_j^s
=
Q_{+,j,s}
-\kappa\,gb_{+,j,s}\,a_1^+a_1^-.
\]
Since \(a_1^+a_1^-=J+\tfrac12\), this becomes
\[
\widetilde Q_{+,j,s}
=
Q_{+,j,s}
\;+\;
\kappa\bigl(-gb_{+,j,s}J\bigr)
\;+\;
\text{(scalar)}\cdot\kappa.
\]

Likewise, for \(Q_{-,j,s}=a_1^-b_j^s\),
\[
\widetilde Q_{-,j,s}
=
a_1^-\widetilde b_j^s
=
Q_{-,j,s}
-\kappa\,gb_{-,j,s}\,a_1^-a_1^+.
\]
Using \(a_1^-a_1^+=1-a_1^+a_1^-=\tfrac12-J\), we get
\[
\widetilde Q_{-,j,s}
=
Q_{-,j,s}
\;+\;
\kappa\bigl(+gb_{-,j,s}J\bigr)
\;+\;
\text{(scalar)}\cdot\kappa.
\]

So in the adjoint representation,
\[
f(Q_{+,j,s})=-gb_{+,j,s}J,
\qquad
f(Q_{-,j,s})=+gb_{-,j,s}J,
\qquad
f(J)=0.
\]

This sends odd generators to even generators, so \(f\) is genuinely parity reversing.

## 3. Why “adjoint representation / up to scalar” is the right interpretation

The only place where scalar terms appear is in the odd-generator computation above:
\[
a_1^+a_1^- = J+\tfrac12,
\qquad
a_1^-a_1^+ = \tfrac12-J.
\]
Hence the transformed odd generators differ from \(Q_{\pm,j,s}+\kappa f(Q_{\pm,j,s})\) by a scalar multiple of \(\kappa\cdot 1\).

That scalar is irrelevant here for two independent reasons:

1. The deformation problem in `docs/math/C_coboundary_definition.md` is stated **in the adjoint representation**.
2. The same document explicitly allows equality **“up to scalar.”**

Because \(\operatorname{ad}_{\lambda 1}=0\), scalar multiples of the identity vanish in the adjoint action. Therefore the induced \(f\) is \(g\)-valued modulo scalars exactly in the sense required by the problem statement.

This removes the apparent closure issue: after passing to the adjoint representation, the transformed generators live in \(\mathfrak g\oplus \kappa\mathfrak g\), with no extra effective directions.

## 4. Coboundary identity

Since \(T=\mathrm{id}+\kappa f\) is an even first-order change of variables, the standard gauge-transformation computation gives
\[
T^{-1}[T(X),T(Y)]_0
=
[X,Y]_0+\kappa\,(\delta f)(X,Y)
\quad (\mathrm{mod}\ \kappa^2),
\]
where \(\delta f\) is exactly the coboundary operator from `docs/math/C_coboundary_definition.md`:
\[
(\delta f)(X,Y)
=
(-1)^{p(X)}[X,f(Y)]
-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]
-f([X,Y]).
\]

But the transformed oscillators were chosen precisely so that their undeformed bracket reproduces the \(gb\)-deformed oscillator bracket. Therefore the cocycle extracted from the inhomogeneous deformation is
\[
\gamma_{gb}=\delta f.
\]

Hence every \(\gamma_{gb}\) is a coboundary.

## 5. Consequences for \(n=1,2,3\) and for general \(n\)

The argument never uses any accidental low-rank identity. It depends only on:

1. the existence of one fermionic pair \(a_1^\pm\),
2. the linear bosonic labels \((j,s)\),
3. the quadratic realization of \(\mathfrak g\),
4. the fact that \(J=a_1^+a_1^- - \tfrac12\) belongs to the \(\mathfrak{so}(2)\) factor.

Therefore the proof is uniform in \(n\). In particular, for the requested cases \(n=1,2,3\), the same \(f\) works without modification.

So the computational checks for \(n=1,2,3\) are not special exceptions; they are finite-dimensional samples of a general theorem.

## 6. Final conclusion

The open issue asks whether any nonzero \(gb\)-configuration can be trivial.

The answer is:

\[
\boxed{\text{Yes. In fact every } gb\text{-configuration is trivial.}}
\]

Equivalently:

\[
\boxed{\gamma_{gb}\text{ is trivial for all } gb_{\sigma,j,s}.}
\]

There is no additional vanishing condition such as \(gb=0\). The entire \(4n\)-parameter family is gauge-removable by the explicit odd coboundary \(f\) above.

## 7. Artifact linkage

The structured artifact file

`docs/issues/verification_artifacts.json`

records:

- startup file verification,
- the explicit gauge transformation,
- the induced \(f\)-map,
- the basis/dimension data for \(n=1,2,3\),
- reusable symbolic templates for future computational checks.

Those artifacts are sufficient for a researcher to reconstruct the same coboundary calculation in a CAS or a custom symbolic script.
