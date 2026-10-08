# Triviality of the Inhomogeneous (gb) Deformation of C(n+1) = osp(2|2n)

**Author**: Claude Fable 5.1 (run `study/thm01-R-fable51-b07-C`)
**Date**: 2026-10-09
**Status of the issue `docs/issues/issue_open.md`**: resolved (definitive conclusion below)
**Sources used**: only `docs/math/Cn1_definition.md`, `docs/math/C_inhomogeneous_definition.md`,
`docs/math/C_coboundary_definition.md`. No external files, papers or web access were used.
**Artifacts**: `verification/osp_deform.py`, `verification/run_verification.py`,
`verification/artifacts/osp2_2n_n{1,2,3}.json`, `verification/artifacts/summary.json`.

---

## 0. Statement of the result

Let $\mathfrak g = C(n+1)=\mathfrak{osp}(2|2n)$ be realized by quadratic oscillator elements as in
`Cn1_definition.md`, let $\gamma_{gb}$ be the odd 2-cochain produced by the inhomogeneous
deformation $[b_j^s,a_1^\sigma]=-\mathrm{gb}_{\sigma,j,s}\,\kappa$ of `C_inhomogeneous_definition.md`,
and let $\delta f$ be the coboundary of an odd linear map $f$ as in `C_coboundary_definition.md`,
with the triviality condition read, as that document says, *"as an adjoint representation, i.e.
$\gamma(X,Y)=(\delta f)(X,Y)$ for all $X,Y$ up to scalar"*.

> **Theorem.** For every $n\ge 1$ and for **every** choice of the $4n$ parameters
> $\mathrm{gb}_{\sigma,j,s}\in\mathbf C$ the inhomogeneous deformation $\gamma_{gb}$ is trivial:
> there is an explicit odd linear map $f_{gb}:\mathfrak g\to\hat{\mathfrak g}=\mathfrak g\oplus\mathbf C\cdot 1$,
> linear in $\mathrm{gb}$, with
> $$\gamma_{gb}(X,Y)=(\delta f_{gb})(X,Y)\qquad\text{for all }X,Y\in\mathfrak g,$$
> as an *exact* identity in $\hat{\mathfrak g}$, hence a fortiori modulo scalars (in the adjoint
> representation). Consequently the set of necessary and sufficient conditions on $\mathrm{gb}$ for
> triviality is **empty**: the admissible parameter set is all of $\mathbf C^{4n}$, and in particular
> every non-zero configuration of $\mathrm{gb}$ satisfies the triviality condition.
>
> The map $f_{gb}$ is given on oscillator monomials by (with $u^\sigma:=\sum_{j=1}^n\big(\mathrm{gb}_{\sigma,j,+}\,b_j^- - \mathrm{gb}_{\sigma,j,-}\,b_j^+\big)$)
> $$ f_{gb}(a_1^\sigma b_l^{s}) = u^\sigma b_l^{s},\qquad
>    f_{gb}(a_1^+a_1^-) = u^+a_1^- - a_1^+u^-,\qquad
>    f_{gb}(b_k^{s}b_l^{t}) = 0, $$
> and it is unique up to adding an inner odd derivation $\mathrm{ad}(Y)$, $Y\in\mathfrak g_{\bar 1}$.

The only reading of the problem under which a non-trivial condition appears is the *strict* one in
which the scalar (central) terms are **not** discarded and $f$ is forced to take values in $\mathfrak g$
rather than $\hat{\mathfrak g}$. Under that reading the condition is $\mathrm{gb}=0$ (Proposition 5.2).
Section 5 explains why this reading is not the one defined in `C_coboundary_definition.md` and is not
even internally consistent with `C_inhomogeneous_definition.md` ($\gamma_{gb}$ is not $\mathfrak g$-valued).

All statements were verified by exact rational computation for $n=1,2,3$ (Section 7); the proof in
Section 4 is uniform in $n$.

---

## 1. Setting and conventions

* $A=V\oplus\mathbf CK\oplus\mathbf C\kappa$ with $V$ spanned by the fermionic pair $a_1^\pm$
  (parity 1) and the bosonic $b_j^\pm$, $j=1,\dots,n$ (parity 0). Undeformed relations
  $\{a_1^-,a_1^+\}=K$, $[b_j^-,b_l^+]=\delta_{jl}K$, all other brackets of generators zero.
* **$K=1$.** The quadratic elements of `Cn1_definition.md` close into $\mathfrak{osp}(2|2n)$ only in
  the quotient $U(A)/(K-1)$ (e.g. $[\tfrac12(b_n^-)^2,\tfrac12(b_n^+)^2]=K\,b_n^+b_n^-+\tfrac12K^2$ must
  equal $-H_{n+1}$). We work in that quotient throughout, which is the usual Fock-type realization.
* **$\kappa$ is odd and central, hence $\kappa^2=0$** ($[\kappa,\kappa]=2\kappa^2=0$ in $U(A)$).
  Therefore every deformed bracket is *exactly* of the form $[X,Y]_0+\kappa\,\gamma(X,Y)$; no higher
  orders exist and no formal-parameter truncation is needed.
* **Parity of the gb parameters.** The deformed relation $[b_j^s,a_1^\sigma]=-\mathrm{gb}_{\sigma,j,s}\kappa$
  has an odd left-hand side ($p(b)+p(a)=1$) and $\kappa$ is odd, so the coefficients $\mathrm{gb}$ are ordinary
  **even** scalars; what is odd (parity 1) is the resulting 2-cochain $\gamma_{gb}$
  (it is the coefficient of the odd element $\kappa$, so $p(\gamma(X,Y))=p(X)+p(Y)+1$). This is how the
  "parity note" of `C_inhomogeneous_definition.md` is interpreted here. (If one insisted on
  Grassmann-odd $\mathrm{gb}$, then $t:=\mathrm{gb}\,\kappa$ would be an even nilpotent central parameter and the
  whole argument of Section 4 goes through verbatim with $\kappa u^\sigma$ replaced by $t$-linear terms;
  the conclusion is unchanged.)
* The deformed algebra $A'$ (same space, deformed form) is again a Lie superalgebra: all brackets of
  generators are central, so the super-Jacobi identity is automatic, and $U(A')$ has the PBW property.
  `C_inhomogeneous_definition.md` requires the form to be skew-supersymmetric, which is consistent:
  $[a_1^\sigma,b_j^s]=+\mathrm{gb}_{\sigma,j,s}\kappa$.
* $\mathfrak g\subset U(A)$ is the span of the $2n^2+5n+1$ elements listed in `Cn1_definition.md`
  (we use the "all root generators" normalization $E_{\pm2\delta_k}=(b_k^\pm)^2$, which is irrelevant for
  triviality). $\hat{\mathfrak g}:=\mathfrak g\oplus\mathbf C\cdot1$ is the span of *all* normal-ordered
  monomials of degree $\le2$ (there are exactly $2n^2+5n+2$ of them). $\hat{\mathfrak g}$ is a Lie
  superalgebra, $1$ is central, and $\mathfrak g=[\hat{\mathfrak g},\hat{\mathfrak g}]$ — so the
  decomposition $\hat{\mathfrak g}=\mathfrak g\oplus\mathbf C1$ is canonical (this is why the constant
  $-\tfrac12$ in $H_{n+1}$ is forced).

---

## 2. The cochain $\gamma_{gb}$ and where the scalars come from

For $X,Y\in\mathfrak g$ (quadratic), the super-commutator in $U(A')$ is computed by the super-Leibniz
rule; every term contains exactly one bracket of generators, which is either the undeformed central
value ($1$) or $-\mathrm{gb}\,\kappa$. Hence

$$[X,Y]_{\gamma}=[X,Y]_0+\kappa\,\gamma_{gb}(X,Y),\qquad \gamma_{gb}(X,Y)\in\hat{\mathfrak g},$$

with $\gamma_{gb}$ **linear** in $\mathrm{gb}$, odd, super-skew, and (because $U(A')$ is associative)
a 2-cocycle for the abelian extension $L=\mathfrak g\oplus\kappa\mathfrak g$ of
`C_inhomogeneous_definition.md`, $[X+\kappa U,\,Y+\kappa V]=[X,Y]+\kappa\big(\gamma(X,Y)+(-1)^{p(X)}[X,V]+[U,Y]\big)$.

The $\kappa$-term is a product of the two oscillators that were *not* contracted; after normal ordering
it may contain a constant. Example ($n=1$, from the artifact):
$$[E_{2\delta_1},E_{\varepsilon-\delta_1}]_\gamma=[(b^+)^2,\,a^+b^-]_\gamma
   = -2a^+b^+ \;+\;\kappa\,\mathrm{gb}_{+,1,+}\big(-2\,b^+b^-\big)
   = -2a^+b^+ + \kappa\,\mathrm{gb}_{+,1,+}\big(2H_2+1\big),$$
so $\gamma_{gb}$ has a non-zero **scalar component** $\gamma_C$. Thus, strictly, $\gamma_{gb}$ takes values
in $\hat{\mathfrak g}$, not in $\mathfrak g$. This is exactly the point addressed by the clause
*"as an adjoint representation … up to scalar"* in `C_coboundary_definition.md`: in the adjoint
representation the central element $1$ (and therefore $\kappa\cdot1$) acts by zero, so two cochains are
identified when they differ by scalars. We therefore distinguish three readings of
"$\gamma_{gb}=\delta f$":

| reading | equality holds in | $f$ takes values in | matches the docs? |
|---|---|---|---|
| **R1** | $\hat{\mathfrak g}/\mathbf C1\cong\mathfrak g$ (adjoint rep., "up to scalar") | $\mathfrak g$ | **yes** – literally `C_coboundary_definition.md` §3 |
| R2 | $\hat{\mathfrak g}$ (exact) | $\hat{\mathfrak g}=\mathfrak g\oplus\mathbf C1$ | yes (stronger than R1) |
| R3 | $\hat{\mathfrak g}$ (exact) | $\mathfrak g$ only | no (see §5) |

R2 ⟹ R1 trivially (project along $\mathbf C1$; the projection $\hat{\mathfrak g}\to\mathfrak g$ is a Lie
superalgebra homomorphism, and $(\delta f)_{\mathfrak g}=\delta(f_{\mathfrak g})$ because scalars are central).

---

## 3. Reformulation: triviality = splitting of the extension

For an odd map $f$, write $\Phi_f(X)=X+\kappa f(X)$. Using only that $\kappa$ is odd and central
($X\kappa=(-1)^{p(X)}\kappa X$, $\kappa^2=0$) one computes in $U(A)\supset \hat{\mathfrak g}\oplus\kappa\hat{\mathfrak g}$:

$$[X+\kappa f(X),\,Y+\kappa f(Y)]_0
 =[X,Y]_0+\kappa\Big((-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]\Big). \tag{3.1}$$

(Indeed $[X,\kappa f(Y)]=(-1)^{p(X)}\kappa[X,f(Y)]$ and $[\kappa f(X),Y]=\kappa[f(X),Y]
=-(-1)^{(p(X)+1)p(Y)}\kappa[Y,f(X)]$ since $p(f(X))=p(X)+1$.) Comparing with
$\Phi_f([X,Y]_\gamma)=[X,Y]_0+\kappa f([X,Y]_0)+\kappa\gamma(X,Y)$ we get

$$\Phi_f\text{ is a homomorphism }(\mathfrak g,[\,,]_\gamma)\to(\hat{\mathfrak g}\oplus\kappa\hat{\mathfrak g},[\,,]_0)
\iff \gamma=\delta f \text{ with } \delta f \text{ exactly the formula of `C\_coboundary\_definition.md`.}\tag{3.2}$$

So the sign conventions of the provided coboundary formula are precisely those for which
$\gamma=\delta f$ means "the deformation is undone by the change of basis $X\mapsto X+\kappa f(X)$".

---

## 4. Proof of the Theorem (uniform in $n$)

**Step 1 – an algebra homomorphism $\Phi:U(A')\to U(A)$.** Define on generators
$$\Phi(b_j^s)=b_j^s,\qquad \Phi(\kappa)=\kappa,\qquad
  \Phi(a_1^\sigma)=a_1^\sigma+\kappa\,u^\sigma,\qquad
  u^\sigma=\sum_{j=1}^n\big(\mathrm{gb}_{\sigma,j,+}\,b_j^- - \mathrm{gb}_{\sigma,j,-}\,b_j^+\big).$$
We check that $\Phi$ preserves every defining relation of $U(A')$ (computed in $U(A)$, i.e. with
$[b,a]=0$):

* $[b_j^s,b_l^t]$ and the centrality of $\kappa$, $\kappa^2=0$: untouched.
* $[b_j^s,\Phi(a_1^\sigma)]=\kappa[b_j^s,u^\sigma]$ ($\kappa$ commutes with the even $b$'s).
  Since $[b_j^-,b_j^+]=1$, $[b_j^+,b_j^-]=-1$:
  for $s=-$ this is $\kappa\cdot(-\mathrm{gb}_{\sigma,j,-})=-\mathrm{gb}_{\sigma,j,-}\kappa$;
  for $s=+$ it is $\kappa\cdot\mathrm{gb}_{\sigma,j,+}\cdot(-1)=-\mathrm{gb}_{\sigma,j,+}\kappa$.
  Both agree with $[b_j^s,a_1^\sigma]=-\mathrm{gb}_{\sigma,j,s}\kappa$. ✓
* $\{\Phi(a_1^-),\Phi(a_1^+)\}=\{a_1^-,a_1^+\}+\{a_1^-,\kappa u^+\}+\{\kappa u^-,a_1^+\}+\{\kappa u^-,\kappa u^+\}$.
  The last term contains $\kappa^2=0$. For the middle ones,
  $\{a_1^-,\kappa u^+\}=a_1^-\kappa u^+ + \kappa u^+a_1^-=\kappa(-a_1^-u^++u^+a_1^-)=-\kappa[a_1^-,u^+]=0$
  because $[a,b]=0$ in $U(A)$; similarly for the other. Hence $\{\Phi(a_1^-),\Phi(a_1^+)\}=1$. ✓
  The same computation gives $\{\Phi(a_1^\sigma),\Phi(a_1^\sigma)\}=0$. ✓

So $\Phi$ is a well-defined homomorphism of associative superalgebras (it preserves parity:
$\kappa u^\sigma$ is odd). (The artifacts verify these relations symbolically for $n=1,2,3$:
check `Phi_preserves_oscillator_relations`.)

**Step 2 – $\Phi$ on $\hat{\mathfrak g}$ and the map $f_{gb}$.** For a quadratic monomial $Z$,
$\Phi(Z)$ is obtained by expanding; since $\kappa^2=0$,
$$\Phi(Z)=Z+\kappa f_{gb}(Z),\qquad f_{gb}(Z)\in\hat{\mathfrak g},$$
where $f_{gb}(Z)$ is again a product of two oscillators (one $a$ replaced by a $b$). Explicitly
$$f_{gb}(a_1^\sigma b_l^s)=u^\sigma b_l^s,\qquad
  f_{gb}(a_1^+a_1^-)=(\kappa\text{-coefficient of }(a_1^++\kappa u^+)(a_1^-+\kappa u^-))=u^+a_1^--a_1^+u^-,\qquad
  f_{gb}(b_k^sb_l^t)=0 .$$
$f_{gb}$ is odd ($\mathfrak g_{\bar1}\to\hat{\mathfrak g}_{\bar0}$, $\mathfrak g_{\bar0}\to\mathfrak g_{\bar1}$),
linear in $\mathrm{gb}$, and $\Phi(\kappa W)=\kappa W$ for quadratic $W$.

**Step 3 – the identity $\gamma_{gb}=\delta f_{gb}$.** For $X,Y\in\mathfrak g$, apply the homomorphism
$\Phi$ to the identity $[X,Y]_\gamma=[X,Y]_0+\kappa\gamma_{gb}(X,Y)$ of $U(A')$:
$$[\Phi X,\Phi Y]_0=\Phi([X,Y]_\gamma)=[X,Y]_0+\kappa f_{gb}([X,Y]_0)+\kappa\,\gamma_{gb}(X,Y).$$
The left side is (3.1) with $f=f_{gb}$. Comparing $\kappa$-coefficients (the map
$W\mapsto\kappa W$ is injective on $\hat{\mathfrak g}$, since the normal-ordered monomials
$\kappa\cdot m$ are linearly independent in $U(A)$ by PBW):
$$\gamma_{gb}(X,Y)=(-1)^{p(X)}[X,f_{gb}(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f_{gb}(X)]-f_{gb}([X,Y])=(\delta f_{gb})(X,Y).$$
This is an exact identity in $\hat{\mathfrak g}$ (reading R2), for every value of $\mathrm{gb}$.
Projecting along $\mathbf C1$ gives reading R1 with the $\mathfrak g$-valued map
$(f_{gb})_{\mathfrak g}$. $\blacksquare$

**Step 4 – uniqueness of $f$.** If $\delta f=\delta f'$ then $f-f'$ is an odd 1-cocycle, i.e. an odd
derivation $\mathfrak g\to\mathfrak g$ (the scalar part of $f-f'$ is an odd functional vanishing on
$[\mathfrak g,\mathfrak g]=\mathfrak g$, hence $0$). The computation shows $\dim Z^1_{\bar1}(\mathfrak g,\mathfrak g)=4n=\dim\mathfrak g_{\bar1}$
for $n=1,2,3$, so all odd derivations are inner, $f$ is unique up to $\mathrm{ad}(Y)$, $Y\in\mathfrak g_{\bar1}$,
and the splitting $\Phi_f$ is unique up to the inner automorphism $\exp(\kappa\,\mathrm{ad}Y)=1+\kappa\,\mathrm{ad}Y$.

**Remark (why the conclusion is robust).** The proof uses only: $\kappa$ odd central (so $\kappa^2=0$),
$[b_j^-,b_j^+]$ invertible (non-degeneracy of the bosonic form), and $[a,b]=0$ in the undeformed algebra.
The odd–even cross terms $(b|a)\kappa$ of a pre-oscillator form can therefore *always* be removed by the
substitution $a\mapsto a+\kappa u$, and the induced deformation of any quadratic subalgebra is a
coboundary. For $n=1,2$ this is also implied by the stronger computed fact $H^2_{\bar1}(\mathfrak g,\mathfrak g)=0$
(Section 7), but the Theorem does not depend on it.

---

## 5. The "adjoint representation / up to scalar" condition and the strict reading R3

**5.1 Why scalars must be discarded.** As shown in §2, $\gamma_{gb}$ has a scalar component
$\gamma_C\ne0$. A $\mathfrak g$-valued cochain is obtained only after projecting $\hat{\mathfrak g}\to\hat{\mathfrak g}/\mathbf C1=\mathfrak g$,
which is what "as an adjoint representation" does ($\mathrm{ad}(1)=0$; the kernel of $\mathrm{ad}|_{\hat{\mathfrak g}}$ is
exactly $\mathbf C1$). This is reading R1, the one defined in `C_coboundary_definition.md`, and the Theorem
answers it: **no condition on gb**.

Because $\gamma_{gb}$ is linear in $\mathrm{gb}$, the alternative parsing of "up to scalar" as
"$\gamma=\lambda\,\delta f$ for some $\lambda\ne0$" changes nothing: $\gamma=\lambda\delta f\iff\gamma=\delta(\lambda f)$.
Under either parsing the admissible set is a linear subspace of $\mathbf C^{4n}$, and we have shown it is everything.

**5.2 Proposition (strict reading R3).** If one demands the exact identity $\gamma_{gb}=\delta f$ in
$\hat{\mathfrak g}$ **and** $f(\mathfrak g)\subset\mathfrak g$, then triviality holds **iff** $\mathrm{gb}=0$.

*Proof.* For $f:\mathfrak g\to\mathfrak g$, $(\delta f)(X,Y)\in\mathfrak g$ (closure of $\mathfrak g$), so the scalar part
$\gamma_C$ must vanish. By Step 3, $\gamma_{gb}=\delta f_{gb}$ with $f_{gb}=(f_{gb})_{\mathfrak g}+f_C\cdot1$, and
since $[X,\,1]=0$, $\gamma_C(X,Y)=-f_C([X,Y])$. As $[\mathfrak g,\mathfrak g]=\mathfrak g$, $\gamma_C=0\iff f_C=0$.
Reading off constants from Step 2 (normal ordering $b_l^-b_l^+=b_l^+b_l^-+1$ and the canonical scalar part
$-\tfrac12$ of $b_l^+b_l^-=H_{l+1}+\dots+H_n-H_{n+1}-\tfrac12$ in $\hat{\mathfrak g}=\mathfrak g\oplus\mathbf C1$):
$$f_C\big(E_{\sigma\varepsilon+s\delta_l}\big)=\tfrac12\,\mathrm{gb}_{\sigma,l,s},\qquad f_C(\text{even elements})=0,$$
so $f_C=0\iff\mathrm{gb}=0$. Conversely $\mathrm{gb}=0$ gives $\gamma=0=\delta 0$. $\blacksquare$
(The artifacts confirm: for R3 the admissible subspace has dimension $0$ and the rank of the scalar
conditions $\{\gamma_C(Z_a,Z_b)=0\}$ is exactly $4n$ for $n=1,2,3$; the listed forms are, e.g. for $n=1$,
$\gamma_C(H_2,E_{\varepsilon+\delta_1})=\tfrac12\mathrm{gb}_{+,1,+}$, $\gamma_C(E_{2\delta_1},E_{\varepsilon-\delta_1})=\mathrm{gb}_{+,1,+}$, …)

**5.3 Why R3 is not the intended condition.** (i) It contradicts `C_inhomogeneous_definition.md`, which
declares $\gamma$ to be $\mathfrak g$-valued and extends the bracket to $L=\mathfrak g\oplus\kappa\mathfrak g$: that
is only possible after discarding scalars. (ii) It is not invariant under the natural notion of
equivalence: the deformed algebra $(\mathfrak g,[\,,]_\gamma)$ *is* isomorphic to the undeformed one via
$\Phi_{f_{gb}}$; R3 merely refuses the isomorphism because it has a (central, hence representation-theoretically
invisible) scalar component. (iii) `C_coboundary_definition.md` §3 explicitly says "as an adjoint
representation … up to scalar". For completeness, however, R3 is reported with its full data in the artifacts.

---

## 6. Explicit data for small $n$ (illustration; full lists are in the JSON artifacts)

For $n=1$ ($\mathfrak{osp}(2|2)$, basis $H_1,H_2,E_{\pm2\delta_1},E_{\pm\varepsilon\pm\delta_1}$) the map
$f_{gb}$ reads, writing $g_{\sigma s}:=\mathrm{gb}_{\sigma,1,s}$:

| $Z$ | $f_{gb}(Z)$ (in $\hat{\mathfrak g}$) |
|---|---|
| $H_1$ | $-g_{-+}E_{\varepsilon-\delta}+g_{--}E_{\varepsilon+\delta}-g_{+-}E_{-\varepsilon+\delta}+g_{++}E_{-\varepsilon-\delta}$ |
| $H_2,\ E_{\pm2\delta}$ | $0$ |
| $E_{\varepsilon+\delta}$ | $-g_{+-}E_{2\delta}-g_{++}H_2+\tfrac12 g_{++}\cdot1$ |
| $E_{\varepsilon-\delta}$ | $g_{+-}H_2+g_{++}E_{-2\delta}+\tfrac12 g_{+-}\cdot1$ |
| $E_{-\varepsilon+\delta}$ | $-g_{--}E_{2\delta}-g_{-+}H_2+\tfrac12 g_{-+}\cdot1$ |
| $E_{-\varepsilon-\delta}$ | $g_{--}H_2+g_{-+}E_{-2\delta}+\tfrac12 g_{--}\cdot1$ |

and, e.g., $\gamma_{gb}(H_1,H_2)=-g_{+-}E_{-\varepsilon+\delta}-g_{++}E_{-\varepsilon-\delta}+g_{--}E_{\varepsilon+\delta}+g_{-+}E_{\varepsilon-\delta}$
(the deformation even modifies the bracket of two Cartan elements). One checks directly that this equals
$(\delta f_{gb})(H_1,H_2)=[H_1,f(H_2)]-[H_2,f(H_1)]-f([H_1,H_2])=-[H_2,f(H_1)]$, using $[H_2,E_{\pm\varepsilon\pm\delta}]=\mp E_{\pm\varepsilon\pm\delta}$
(sign of $\delta$). The complete tables of $c_{ab}^{\,k}$, $\gamma_{ab}^{\,k}(\mathrm{gb})$ and $f$ for $n=1,2,3$ are in the artifacts.

---

## 7. Computational verification (exact arithmetic)

`verification/osp_deform.py` implements the deformed enveloping algebra $U(A')$ (normal ordering with the
rules $a^-a^+=1-a^+a^-$, $b_j^-b_j^+=b_j^+b_j^-+1$, $b_j^sa^\sigma=a^\sigma b_j^s-\mathrm{gb}_{\sigma,j,s}\kappa$,
$x\kappa=(-1)^{p(x)}\kappa x$, $\kappa^2=0$) over the ring $\mathbf Q[\mathrm{gb}]$ with `fractions.Fraction`
coefficients. `verification/run_verification.py n` then, for each $n$:

1. computes all $(\dim\mathfrak g)^2$ brackets $[Z_a,Z_b]_\gamma$, decomposes them in the basis of
   $\hat{\mathfrak g}$ and extracts $c_{ab}^{\,k}$ and $\gamma_{ab}^{\,k}(\mathrm{gb})$ (asserting closure of
   $\mathfrak g$, linearity in $\mathrm{gb}$, oddness, super-skewness);
2. verifies the super-Jacobi identity of $L=\mathfrak g\oplus\kappa\mathfrak g$ (cocycle condition) on all
   $(\dim\mathfrak g)^3$ basis triples and for each of the $4n$ gb-directions;
3. builds $f_{gb}$ exactly as the $\kappa$-part of $\Phi$ (Step 2) and checks $\gamma_{gb}=\delta f_{gb}$
   with the coboundary formula of the docs, as an identity of polynomials in $\mathrm{gb}$, both exactly in
   $\hat{\mathfrak g}$ (R2) and modulo scalars with $f:\mathfrak g\to\mathfrak g$ (R1); it also checks that
   $\Phi$ preserves the oscillator relations;
4. **independently of Step 3** sets up the linear system $\delta f=\gamma_{gb}$ in the unknown
   coefficients $\phi_{ij}$ of $f$ and the parameters $\mathrm{gb}$, and computes
   $\operatorname{rank}A$ and $\operatorname{rank}[A\,|\,\Gamma]$ (coboundary matrix, and the same matrix
   augmented by the $4n$ columns $\gamma_{gb=e_k}$) modulo two large primes and in floating point. The
   codimension of the admissible gb-subspace is $\operatorname{rank}[A|\Gamma]-\operatorname{rank}A$;
5. computes $\dim H^2_{\bar1}(\mathfrak g,\mathfrak g)$ (odd super-skew cocycles modulo odd coboundaries, values in $\mathfrak g$) for $n=1,2$.

Results (`verification/artifacts/summary.json`):

| | $n=1$: $\mathfrak{osp}(2|2)$ | $n=2$: $\mathfrak{osp}(2|4)$ | $n=3$: $\mathfrak{osp}(2|6)$ |
|---|---|---|---|
| $\dim\mathfrak g$ (even\|odd) | 8 (4\|4) | 19 (11\|8) | 34 (22\|12) |
| number of gb parameters | 4 | 8 | 12 |
| closure, gb-linearity, oddness, skewness, cocycle | all ✓ | all ✓ | all ✓ |
| $\Phi$ preserves relations; $\gamma_{gb}=\delta f_{gb}$ exact (R2) and mod scalars (R1) | ✓ ✓ ✓ | ✓ ✓ ✓ | ✓ ✓ ✓ |
| R1: unknowns $\phi$ / equations; $\operatorname{rank}A=\operatorname{rank}[A|\Gamma]$ | 32 / 212; 28 = 28 | 176 / 2748; 168 = 168 | 528 / 13976; 516 = 516 |
| R1: dim of admissible gb subspace | 4 = all | 8 = all | 12 = all |
| R2: $\operatorname{rank}A=\operatorname{rank}[A|\Gamma]$; admissible gb | 32 = 32; all | 176 = 176; all | 528 = 528; all |
| R3: $\operatorname{rank}A$, $\operatorname{rank}[A|\Gamma]$; admissible gb | 28, 32; $\{0\}$ | 168, 176; $\{0\}$ | 516, 528; $\{0\}$ |
| rank of the scalar conditions $\gamma_C=0$ | 4 | 8 | 12 |
| $\dim Z^1_{\bar1}(\mathfrak g,\mathfrak g)$ (= freedom in $f$) | 4 = $\dim\mathfrak g_{\bar1}$ | 8 = $\dim\mathfrak g_{\bar1}$ | 12 = $\dim\mathfrak g_{\bar1}$ |
| $\dim Z^2_{\bar1}$, $\dim B^2_{\bar1}$, $\dim H^2_{\bar1}(\mathfrak g,\mathfrak g)$ | 28, 28, **0** | 168, 168, **0** | not computed (≈10⁴ unknowns; not needed) |
| wall time | 0.2 s | 7 s | 83 s |

All ranks agree between the two primes and the floating-point SVD. The modular/float ranks are cross-checks
only; the proof-level statements (items 1–3) are exact identities over $\mathbf Q[\mathrm{gb}]$.

To reproduce: `python3 verification/run_verification.py 1 2 3` (pure Python 3 + numpy; ≈ a few minutes).

**Artifact schema** (`verification/artifacts/osp2_2n_n{n}.json`): `basis` (name, parity, root, oscillator
expression), `structure_constants.entries` $=[a,b,k,c_{ab}^{\,k}]$, `gamma.entries_in_g` and
`gamma.entries_scalar` $=[a,b,k,\text{gb-name},\text{coefficient}]$ (so $\gamma(Z_a,Z_b)=\sum\text{coeff}\cdot\mathrm{gb}\cdot Z_k$),
`explicit_f.entries` $=[j,i,\text{gb-name},\text{coeff}]$ (so $f(Z_j)=\sum\text{coeff}\cdot\mathrm{gb}\cdot Z_i$, key `"1"` = scalar),
`linear_system` (ranks and dimensions for R1/R2/R3), `R3_scalar_part_conditions`, `checks`. All numbers are
exact rationals stored as strings. Parameter names are `gb[sigma][j][s]` $=\mathrm{gb}_{\sigma,j,s}=\mathrm{gb}_{a_1^\sigma,b_j^s}$.

---

## 8. Conclusion

* **Answer to the issue.** Under the triviality condition as defined in the provided documents
  (equality in the adjoint representation, i.e. up to scalars), the inhomogeneous deformation
  $\gamma_{gb}$ of $C(n+1)=\mathfrak{osp}(2|2n)$ is a coboundary for **all** values of the $4n$ parameters
  $\mathrm{gb}_{\sigma,j,s}$. There is no non-trivial inhomogeneous deformation of this type; the
  necessary-and-sufficient condition is vacuous. The trivializing odd map is explicit
  ($f_{gb}=\kappa$-part of the substitution $a_1^\sigma\mapsto a_1^\sigma+\kappa u^\sigma$) and unique up to inner odd derivations.
* **Mechanism.** The odd central element $\kappa$ squares to zero, so the cross relations
  $[b,a]=-\mathrm{gb}\,\kappa$ can be absorbed into a redefinition of the fermionic oscillators; the deformed
  and undeformed enveloping algebras are isomorphic, and the isomorphism restricts to
  $X\mapsto X+\kappa f_{gb}(X)$ on $\mathfrak g$. The only residue of the deformation is a *central*
  (scalar) term, invisible in the adjoint representation.
* **If scalars are not discarded** and $f$ is confined to $\mathfrak g$ (reading R3, not the one in the
  docs), the condition becomes $\mathrm{gb}=0$; the obstruction is precisely the scalar part
  $f_C(E_{\sigma\varepsilon+s\delta_l})=\tfrac12\mathrm{gb}_{\sigma,l,s}$.
* Verified exactly for $n=1,2,3$ by two independent computations (explicit $f$ and rank analysis);
  the proof is uniform in $n$. For $n=1,2$ even $H^2_{\bar1}(\mathfrak g,\mathfrak g)=0$.
