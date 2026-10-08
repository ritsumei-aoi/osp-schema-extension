# Triviality of the Inhomogeneous ($gb$) Deformation of $C(n+1)=\mathfrak{osp}(2|2n)$

**Status**: resolved (theorem proved for all $n\ge 1$; exact computer verification for $n=1,2,3$)
**Author**: Claude Fable 5.1 (session `study/thm01-R-fable51-b09-C`), 2026-10-09
**Sources used**: only `docs/math/Cn1_definition.md`, `docs/math/C_inhomogeneous_definition.md`,
`docs/math/C_coboundary_definition.md`, `docs/issues/issue_open.md`. No external files or web access.
**Artifacts**: `scripts/osp_deform.py`, `scripts/summarize.py`, `artifacts/*.json`.

---

## 0. Main result

> **Theorem.** Let $\mathfrak g = C(n+1)=\mathfrak{osp}(2|2n)$ with the oscillator realization of
> `Cn1_definition.md`, and let $\gamma_{gb}$ be the inhomogeneous deformation of
> `C_inhomogeneous_definition.md` with parameters $gb_{\sigma,j,s}\in\mathbf C$ ($\sigma,s\in\{+,-\}$,
> $1\le j\le n$). Then **for every value of the $4n$ parameters** there is an odd linear map
> $f_{gb}:\mathfrak g\to\mathfrak g$ with
> $$\gamma_{gb}=\delta f_{gb}$$
> in the sense of `C_coboundary_definition.md`. Two explicit formulas for $f_{gb}$ are given
> (§3 and §4). Consequently the necessary and sufficient condition on $gb$ for triviality is
> **vacuous**: every configuration, zero or non-zero, is trivial. The deformation is nevertheless
> non-zero as a cochain whenever $gb\neq 0$ (§5), so it is a *non-trivial-looking coboundary*, not the zero cochain.
>
> More generally (§4, Corollary): **every odd cocycle of $\mathfrak g$ with values in the adjoint
> module is a coboundary**, $H^k(\mathfrak g,\mathfrak g)_{\bar 1}=0$ for all $k\ge 1$ and all $n$.

The "adjoint representation / up to scalar" clause of the triviality condition is made precise in §2 and §6:
the only scalars that ever appear are multiples of the unit $1\in\mathcal U(A)$ produced by normal ordering,
and the theorem holds *both* modulo these scalars (with $f:\mathfrak g\to\mathfrak g$) *and* on the nose
(with $f:\mathfrak g\to\mathfrak g\oplus\mathbf C1$).

---

## 1. Setting and conventions

### 1.1 The oscillator superalgebra and its deformation

$V=V_{\bar 0}\oplus V_{\bar 1}$ with $V_{\bar 1}=\langle a^+,a^-\rangle$ and
$V_{\bar 0}=\langle b_k^+,b_k^-\rangle_{k=1..n}$. $A_\theta=V\oplus\mathbf CK\oplus\mathbf C\kappa$,
$K$ even central (set $K=1$ in $\mathcal U$), $\kappa$ **odd** central. The brackets are
$$[a^-,a^+]=1,\qquad [b_k^-,b_l^+]=\delta_{kl},\qquad [b_j^s,a^\sigma]=-\,gb_{\sigma,j,s}\,\kappa ,$$
all other brackets of generators zero. Here $[\cdot,\cdot]$ is the supercommutator
$[x,y]=xy-(-1)^{p(x)p(y)}yx$, so $[a^-,a^+]$ is an anticommutator and $[b^-,b^+]$ a commutator.
Write
$$[x,y]=\omega(x,y)\,1+\kappa\,\theta(x,y)\qquad(x,y\in V),$$
where $\omega$ is the undeformed (even, non-degenerate, skew-supersymmetric) pre-oscillator form and
$$\theta(b_j^s,a^\sigma)=-gb_{\sigma,j,s},\qquad \theta(a^\sigma,b_j^s)=+gb_{\sigma,j,s},\qquad
\theta(V_{\bar0},V_{\bar0})=\theta(V_{\bar1},V_{\bar1})=0 .$$
$\theta$ is antisymmetric on mixed pairs: this is exactly what skew-supersymmetry
$(a|b)=-(-1)^{p(a)p(b)}(b|a)$ demands when $p(a)p(b)=0$.

**Facts about $\kappa$ used throughout.** Since $\kappa$ is odd and central in the super sense,
$$x\kappa=(-1)^{p(x)}\kappa x,\qquad \kappa^2=\tfrac12[\kappa,\kappa]=0,\qquad
[\kappa u,y]=\kappa[u,y],\qquad [x,\kappa v]=(-1)^{p(x)}\kappa[x,v]. \tag{1.1}$$
Hence $\mathcal U(A_\theta)$ is a module over $R=\mathbf C[\kappa]/(\kappa^2)$ and every
computation is *linear* in $\kappa$ and therefore linear in $gb$.

**Parity bookkeeping.** We take $gb_{\sigma,j,s}\in\mathbf C$; the odd parity of the deformation is
carried by $\kappa$. The resulting 2-cochain $\gamma$ ($[X,Y]_\gamma=[X,Y]_0+\kappa\gamma(X,Y)$) has
parity $p(\gamma(X,Y))=p(X)+p(Y)+1$, i.e. $\gamma$ is an **odd cochain**, which is why the
coboundary document uses an **odd** $f$. (If one prefers to regard the $gb$'s as Grassmann-odd
parameters, the formulas below are unchanged except for $\alpha$-dependent signs when a $gb_\alpha$ is
moved past odd elements; since $\gamma_{gb}=\sum_\alpha gb_\alpha\gamma_\alpha$ and we prove
$\gamma_\alpha=\delta f_\alpha$ for *each* $\alpha$ separately, the conclusion is identical.)

### 1.2 The basis of $\mathfrak g$

We use literally the generators of `Cn1_definition.md`:
$H_1=a^+a^-+b_1^+b_1^-$, $H_k=b_{k-1}^+b_{k-1}^--b_k^+b_k^-$ ($2\le k\le n$),
$H_{n+1}=-b_n^+b_n^--\tfrac12$,
$E_{\pm\delta_k\pm\delta_l}=b_k^\pm b_l^\pm$ ($k<l$), $E_{\pm2\delta_k}=(b_k^\pm)^2$,
$E_{\varepsilon\pm\delta_l}=a^+b_l^\pm$, $E_{-\varepsilon\pm\delta_l}=a^-b_l^\pm$.
That is $n+1+n(2n-1)+2n+4n=2n^2+5n+1$ elements, of dimension $(2n^2+n+1\,|\,4n)$. Each is a weight vector
for the weight coordinates $(\varepsilon,\delta_1,\dots,\delta_n)$.

**Lemma 1.1 (super-symmetrised quadratics).** In the undeformed algebra, $\mathfrak g$ equals the span of
the super-symmetrised quadratics $\mathrm{sym}(xy)=\tfrac12\big(xy+(-1)^{p(x)p(y)}yx\big)$, $x,y\in V$.

*Proof.* $\mathrm{sym}(a^+a^-)=a^+a^--\tfrac12$, $\mathrm{sym}(b_k^+b_k^-)=b_k^+b_k^-+\tfrac12$, and all other
monomials in the list are already symmetric. The Cartan elements of the list span
$\{a^+a^--\tfrac12,\ b_k^+b_k^-+\tfrac12\}$ (indeed $M_n:=b_n^+b_n^-+\tfrac12=-H_{n+1}$,
$M_{k}=H_{k+1}+M_{k+1}$, $a^+a^--\tfrac12=H_1-M_1$). Counting: $\dim\mathrm{sym}^2V=\binom{2n+1}{2}+1+4n=2n^2+5n+1$. $\square$

In the engine the elements are stored as normal-ordered words; the decomposition of any quadratic
element in the basis $\{Z_i\}\cup\{1\}$ is unique and is computed exactly (the $(2n^2+5n+2)$-square
change-of-basis matrix is inverted over $\mathbf Q$).

---

## 2. The cochain $\gamma_{gb}$, its scalar part, and the cocycle property

Evaluate the generator expressions $Z_i$ in $\mathcal U(A_\theta)$ and compute the supercommutators by
normal ordering. Because every bracket of letters is central and $\kappa^2=0$, the result is
$$[Z_i,Z_j]_\theta=\sum_k c_{ij}^k Z_k\;+\;\kappa\Big(\sum_k\gamma^k_{ij}Z_k+s_{ij}\,1\Big),\tag{2.1}$$
with $c_{ij}^k$ the structure constants of $C(n+1)$, $\gamma^k_{ij}$ and $s_{ij}$ **linear in $gb$**:
$\gamma_{gb}=\sum_\alpha gb_\alpha\gamma_\alpha$, $s=\sum_\alpha gb_\alpha s_\alpha$, $\alpha=(\sigma,j,s)$.

* The $\kappa^0$ part closes in $\mathfrak g$ with no scalar (checked: closure and super-Jacobi, 0 violations).
* The **scalar part $s_{ij}\,\kappa\,1$** is the origin of the phrase *"up to scalar"* in
  `C_coboundary_definition.md`: it appears because the listed generators are *normal-ordered* monomials,
  and in $\mathcal U(A_\theta)$ a normal-ordered mixed monomial differs from its super-symmetrisation by
  a $\kappa$-multiple of $1$: $a^\sigma b_j^s=\mathrm{sym}(a^\sigma b_j^s)+\tfrac12 gb_{\sigma,j,s}\kappa$.
  Example ($n=1$, $\alpha=gb_{+,1,+}$): $[H_1,E_{\varepsilon+\delta_1}]_\theta$ contains $-\,gb\,\kappa\,1$.
  Since $\kappa 1$ is central in $\mathfrak g\oplus\kappa(\mathfrak g\oplus\mathbf C1)$, projecting it away
  gives a Lie superalgebra structure on $L=\mathfrak g\oplus\kappa\mathfrak g$; this is the abelian
  extension by the (parity-shifted) adjoint representation mentioned in the inhomogeneous document.
* $\gamma_{gb}$ is super-skew, $\gamma(Y,X)=-(-1)^{p(X)p(Y)}\gamma(X,Y)$ (checked).
* **$\gamma_{gb}$ (with or without the scalar part) is a 2-cocycle**: the Jacobi identity holds in the
  associative algebra $\mathcal U(A_\theta)$; its $\kappa$-linear part reads, with $c$ the undeformed bracket
  extended by $c(\cdot,1)=0$,
  $$J(\gamma)(X,Y,Z):=\gamma(c(X,Y),Z)+c(\gamma(X,Y),Z)-\gamma(X,c(Y,Z))-(-1)^{p(X)}c(X,\gamma(Y,Z))
  +(-1)^{p(X)p(Y)}\big[\gamma(Y,c(X,Z))+(-1)^{p(Y)}c(Y,\gamma(X,Z))\big]=0. \tag{2.2}$$
  (Derived from $[[X,Y],Z]=[X,[Y,Z]]-(-1)^{p(X)p(Y)}[Y,[X,Z]]$ using (1.1).) Checked on all
  $(\dim\mathfrak g)^3$ triples for every $\alpha$: 0 violations.

### 2.1 The coboundary operator and what "$\gamma=\delta f$" means

With the document's formula
$(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y])$ and
$[f(X),Y]=-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]$ one has the equivalent form
$$(\delta f)(X,Y)=[f(X),Y]+(-1)^{p(X)}[X,f(Y)]-f([X,Y]). \tag{2.3}$$
**Interpretation (Lemma 2.1).** For an odd $f:\mathfrak g\to\mathfrak g$, $\Phi=\mathrm{id}+\kappa f$ is an
$R$-linear bijection of $L=\mathfrak g\oplus\kappa\mathfrak g$, and by (1.1)
$$\Phi([X,Y]_\gamma)-[\Phi X,\Phi Y]_0=\kappa\big(\gamma(X,Y)-(\delta f)(X,Y)\big).$$
So $\gamma=\delta f$ **exactly** says that $\mathrm{id}+\kappa f$ is an isomorphism from the deformed
bracket to the undeformed one, i.e. the deformation is trivial. The derivation also fixes the sign
conventions: the document's $\delta$ corresponds to $\Phi=\mathrm{id}+\kappa f$ mapping *deformed → undeformed*.

---

## 3. First proof: the deformation is a change of oscillator basis

**Proposition 3.1.** Let $h\in\mathrm{End}(V)$ be **odd** and $\Phi(x)=x+\kappa h(x)$ on $V$. Then
$$[\Phi x,\Phi y]_0=\omega(x,y)+\kappa\,(Dh)(x,y),\qquad (Dh)(x,y):=\omega(hx,y)+(-1)^{p(x)}\omega(x,hy).$$
*Proof.* Expand with (1.1); the $[\kappa hx,\kappa hy]$ term is a multiple of $\kappa^2=0$. $\square$

**Proposition 3.2 (surjectivity).** Put $\beta(x,y):=\omega(hx,y)$. Then $Dh(x,y)=\beta(x,y)-\beta(y,x)$ for all $x,y$.
Hence $D:\mathrm{End}(V)_{\bar1}\to\{\text{mixed antisymmetric forms}\}$ is **surjective**, with kernel the
symmetric mixed forms $\cong\mathfrak{osp}(V)_{\bar 1}$ (dimension $4n$).

*Proof.* If $p(x)=p(y)$ both sides vanish ($h$ flips parity, $\omega$ pairs equal parities).
If $x$ even, $y$ odd: $\omega(x,hy)=-\omega(hy,x)=-\beta(y,x)$ by skewness on $V_{\bar0}$.
If $x$ odd, $y$ even: $(-1)^{p(x)}\omega(x,hy)=-\omega(x,hy)=-\omega(hy,x)=-\beta(y,x)$ by symmetry on $V_{\bar1}$.
The map $h\mapsto\beta$ is a bijection $\mathrm{End}(V)_{\bar1}\to\{\text{mixed forms}\}$ ($\omega$ non-degenerate),
and $\beta\mapsto\beta-\beta^{t}$ is onto antisymmetric mixed forms. $\square$

Since $\theta$ is a mixed antisymmetric form, choose $\beta=\theta/2$, i.e. **$h$ defined by $\omega(hx,y)=\tfrac12\theta(x,y)$**. Explicitly
$$h(b_j^s)=-\tfrac12\big(gb_{-,j,s}\,a^+ + gb_{+,j,s}\,a^-\big),\qquad
h(a^\sigma)=\tfrac12\sum_{l=1}^n\big(gb_{\sigma,l,+}\,b_l^- - gb_{\sigma,l,-}\,b_l^+\big). \tag{3.1}$$
Then $[\Phi x,\Phi y]_0=[x,y]_\theta$ for all $x,y\in V$, so $\Phi$ extends to an $R$-algebra homomorphism
$\mathcal U(A_\theta)\to\mathcal U(A_0)$, which is the identity mod $\kappa$ and hence an isomorphism.

**Proposition 3.3 (the coboundary).** On a quadratic monomial, $\Phi(xy)=xy+\kappa\tilde f(xy)$ with
$$\tilde f(xy)=(hx)\,y+(-1)^{p(x)}x\,(hy), \tag{3.2}$$
(products in the undeformed algebra). $\tilde f$ maps the generator expressions $Z_i$ into
$\mathfrak g\oplus\mathbf C1$; write $\tilde f=f_A+e$ with $f_A:\mathfrak g\to\mathfrak g$ odd and $e:\mathfrak g\to\mathbf C$.
Applying $\Phi$ to (2.1) and using $\Phi(Z_i^\theta)=Z_i^0+\kappa\tilde f(Z_i)$:
$$\gamma_{gb}(X,Y)+s(X,Y)\,1=[\tilde fX,Y]+(-1)^{p(X)}[X,\tilde fY]-\tilde f([X,Y])=(\delta\tilde f)(X,Y).$$
Projecting to $\mathfrak g$ and to $\mathbf C1$:
$$\boxed{\ \gamma_{gb}=\delta f_A\ }\qquad\text{and}\qquad s_{ij}=-\sum_k c^k_{ij}\,e_k .$$
This proves the Theorem, and shows that the scalar terms are themselves "coboundaries" of the scalar part $e$ of $\tilde f$ — the precise content of *"up to scalar"*. $\square$

*$n=1$, $\alpha=gb_{+,1,+}$:* $f_A(H_2)=\tfrac12E_{-\varepsilon-\delta_1}$, $f_A(E_{2\delta_1})=-E_{-\varepsilon+\delta_1}$,
$f_A(E_{\varepsilon+\delta_1})=\tfrac12H_1$ (with $e=\tfrac12$), $f_A(E_{\varepsilon-\delta_1})=\tfrac12E_{-2\delta_1}$, all others $0$.

---

## 4. Second proof: the $\mathbf Z$-grading of a type-I superalgebra kills odd cohomology

Let $N:=a^+a^--\tfrac12=\mathrm{sym}(a^+a^-)\in\mathfrak g_{\bar0}$ (in the basis:
$N=H_1-H_2-\dots-H_n+H_{n+1}$; for $n=1$, $N=H_1+H_2$). Then $\mathrm{ad}N$ acts by the
$\varepsilon$-coordinate of the weight: $+1$ on $a^+b^\pm$, $-1$ on $a^-b^\pm$, $0$ on $\mathfrak g_{\bar0}$.
Thus $\mathfrak g=\mathfrak g_{-1}\oplus\mathfrak g_0\oplus\mathfrak g_1$ is $\mathbf Z$-graded by $\mathrm{ad}N$ and
**the parity is the degree mod 2** ($C(n+1)$ is of type I).

**Lemma 4.1 (weights of $\gamma_\alpha$).** Give $\kappa$ the weight $\sigma\varepsilon+s\delta_j$ in the
relation $[b_j^s,a^\sigma]=-gb_{\sigma,j,s}\kappa$; then $\mathcal U(A_\theta)$ is weight-graded and every
component of $\gamma_\alpha$ and $s_\alpha$ has the weight
$$\lambda_\alpha=-(\sigma\varepsilon+s\delta_j),\qquad\lambda_\alpha(N)=-\sigma\in\{\pm1\}\neq0 .$$
(Verified: each $\gamma_\alpha$ has exactly one weight, the listed one.)

**Lemma 4.2 (Cartan homotopy, $k=2$).** Let $\tilde\gamma$ be any cocycle (2.2) with values in
$\mathfrak g\oplus\mathbf C1$, homogeneous of $\mathrm{ad}N$-weight $\lambda\neq0$. Then
$$\tilde\gamma=\delta\!\left(\frac{\iota_N\tilde\gamma}{\lambda}\right),\qquad(\iota_N\tilde\gamma)(Y):=\tilde\gamma(N,Y).$$
*Proof.* Put $X=N$ in (2.2). With $c(N,Y)=d_Y\,Y$ ($d_Y$ the degree) and
$c(N,\tilde\gamma(Y,Z))=(d_Y+d_Z+\lambda)\tilde\gamma(Y,Z)$:
$$0=d_Y\tilde\gamma(Y,Z)+c(\iota_N\tilde\gamma(Y),Z)-\iota_N\tilde\gamma(c(Y,Z))-(d_Y+d_Z+\lambda)\tilde\gamma(Y,Z)
+d_Z\tilde\gamma(Y,Z)+(-1)^{p(Y)}c(Y,\iota_N\tilde\gamma(Z)),$$
i.e. $\lambda\tilde\gamma(Y,Z)=(\delta\,\iota_N\tilde\gamma)(Y,Z)$ by (2.3). $\square$

**Proof of the Theorem (second version).** $\gamma_{gb}=\gamma^{(+)}+\gamma^{(-)}$ with
$\gamma^{(\sigma)}=\sum_{j,s}gb_{\sigma,j,s}\gamma_{\sigma,j,s}$ of $\mathrm{ad}N$-weight $-\sigma$. By Lemma 4.2
$$\boxed{\ f_B(Y)=-\gamma^{(+)}(N,Y)+\gamma^{(-)}(N,Y),\qquad \gamma_{gb}=\delta f_B\ }$$
and the same formula applied to $\gamma+s$ reproduces the scalar terms as well. $\square$

**Corollary 4.3 ($H^\bullet(\mathfrak g,\mathfrak g)_{\bar1}=0$).** An odd $k$-cochain $\varphi$ satisfies
$\deg\varphi(X_1,\dots,X_k)\equiv\sum\deg X_i+1\pmod 2$, so all its $\mathrm{ad}N$-weight components have
**odd**, hence non-zero, weight; by the Cartan homotopy formula $L_N=\delta\iota_N+\iota_N\delta$
(Lemma 4.2 for $k=2$) every odd cocycle is a coboundary. In particular there is **no** odd
(inhomogeneous) deformation of $C(n+1)$ with a non-trivial class — not just the $gb$ family.
Numerically: the space of weight-zero odd 2-cochains is $0$ for $n=1,2,3$ (table in §7), so
$H^2(\mathfrak g,\mathfrak g)_{\bar 1}=0$ independently of the argument above.

---

## 5. Non-degeneracy and uniqueness

* **$\gamma_{gb}\ne0$ for $gb\neq0$.** The $4n$ cochains $\gamma_\alpha$ have pairwise distinct weights
  and are each non-zero (e.g. $\gamma_{+,j,+}(E_{\varepsilon+\delta_j},E_{\varepsilon+\delta_j})=2E_{\varepsilon+\delta_j}$,
  from $(a^+b_j^+)^2=gb\,\kappa\,a^+b_j^+$); hence they are linearly independent (rank $=4n$ verified).
  So the triviality is *not* because the deformation vanishes.
* **Uniqueness of $f$.** $f$ is determined modulo $\ker\delta^1=$ odd derivations of $\mathfrak g$.
  For $n=1,2,3$ the computed $\dim\ker\delta^1_{\bar1}=4n=\dim\mathfrak g_{\bar1}$, i.e. all odd derivations
  are inner ($\mathrm{ad}Y$, $Y\in\mathfrak g_{\bar1}$). The two explicit solutions differ by such a derivation
  ($\delta(f_A-f_B)=0$ verified).

---

## 6. How "adjoint representation / up to scalar" was handled

1. *Adjoint representation.* $\gamma$ and $\delta f$ are compared as maps $\mathfrak g\otimes\mathfrak g\to\mathfrak g$
   where $\mathfrak g\subset\mathcal U(A)$ acts on itself by $\mathrm{ad}$; the deformed structure is the
   abelian extension $L=\mathfrak g\oplus\kappa\mathfrak g$ by the parity-shifted adjoint module
   ($[X,\kappa Y]=(-1)^{p(X)}\kappa[X,Y]$, $[\kappa\mathfrak g,\kappa\mathfrak g]=0$); Lemma 2.1 identifies the
   document's $\delta f$ with the condition "$\mathrm{id}+\kappa f$ is an isomorphism of extensions".
2. *Up to scalar.* The only scalar ambiguity is the central term $s_{ij}\kappa 1$ of (2.1), caused by
   normal ordering. We showed (Prop. 3.3, Lemma 4.2) that it is **also** a coboundary, of the scalar part
   $e$ of $\tilde f$. Hence $\gamma_{gb}=\delta f$ holds *modulo scalars* with $f:\mathfrak g\to\mathfrak g$ and
   *exactly* with $\tilde f:\mathfrak g\to\mathfrak g\oplus\mathbf C1$. The alternative reading "up to a
   non-zero scalar multiple $\gamma=c\,\delta f$" is covered trivially by rescaling $f$.
3. *Basis normalisation.* The result is basis-independent (rescaling $E_{\pm2\delta_k}$ by $\tfrac12$ as in
   the simple-generator list changes nothing); the artifacts record the exact basis used.

---

## 7. Computational verification (exact rational arithmetic)

`scripts/osp_deform.py --n N --cohomology` implements, from scratch and with `fractions.Fraction` only:

1. a normal-ordering engine for words in $\{\kappa,a^\pm,b_k^\pm\}$ with the deformed relations
   (rules (1.1), $(a^\pm)^2=0$, $\kappa^2=0$, polynomial coefficients in the $gb$'s);
2. the basis $Z_i$, parities, weights; the exact decomposition of quadratics in $\{Z_i\}\cup\{1\}$;
3. the brackets (2.1): $c^k_{ij}$, $\gamma^k_{\alpha,ij}$, $s_{\alpha,ij}$ for every parameter $\alpha$;
4. checks: super-Jacobi of $c$, super-skewness and cocycle condition (2.2) of each $\gamma_\alpha$ on all triples, single weight of $\gamma_\alpha$;
5. the explicit $f_A$ (3.1)–(3.2) and $f_B$ (§4), and the **exact equalities** $\delta f_A=\gamma_\alpha$, $\delta f_B=\gamma_\alpha$ via the document's formula, plus the scalar identities $s=-e\circ c$ for both;
6. negative controls ($f=0$ and $f=-f_A$ fail), rank of $\{\gamma_\alpha\}$, $\dim\ker\delta^1_{\bar1}$,
   and $\dim$ of weight-zero odd 2-cochains/cocycles ($=\dim H^2(\mathfrak g,\mathfrak g)_{\bar1}$ by the Cartan argument).

| $n$ | $\mathfrak g$ | $\dim$ | #$gb$ | rank$\{\gamma_\alpha\}$ | cocycle viol. | $\delta f_A=\gamma$ | $\delta f_B=\gamma$ | scalars matched | odd derivations | wt-0 odd 2-cochains | $H^2_{\bar1}$ | runtime |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | $\mathfrak{osp}(2\|2)$ | (4\|4) | 4 | 4 | 0 | ✓ (4/4) | ✓ (4/4) | ✓ | 4 = dim $\mathfrak g_{\bar1}$ | 0 | 0 | 0.1 s |
| 2 | $\mathfrak{osp}(2\|4)$ | (11\|8) | 8 | 8 | 0 | ✓ (8/8) | ✓ (8/8) | ✓ | 8 = dim $\mathfrak g_{\bar1}$ | 0 | 0 | 0.8 s |
| 3 | $\mathfrak{osp}(2\|6)$ | (22\|12) | 12 | 12 | 0 | ✓ (12/12) | ✓ (12/12) | ✓ | 12 = dim $\mathfrak g_{\bar1}$ | 0 | 0 | 6 s |

Artifacts (`artifacts/`): `C2_deformation_n1.json`, `C3_deformation_n2.json`, `C4_deformation_n3.json`
each contain the basis (oscillator expressions, parity, weight), all structure constants
`[Z_i, Z_j, Z_k, c]`, the full cocycle $\gamma_\alpha$ and scalar terms $s_\alpha$ per parameter, the two
solutions $f_A$, $f_B$ (with their scalar parts), and every check flag; `verification_summary.json`
aggregates them. All numbers are exact rationals stored as strings.

Reproduce:
```bash
python3 scripts/osp_deform.py --n 1 --cohomology
python3 scripts/osp_deform.py --n 2 --cohomology
python3 scripts/osp_deform.py --n 3 --cohomology
python3 scripts/summarize.py
```

---

## 8. Conclusion

* **Necessary and sufficient condition for triviality of $\gamma_{gb}$: none.** For all
  $gb\in\mathbf C^{4n}$, $\gamma_{gb}=\delta f_{gb}$ with the explicit odd map
  $f_{gb}=f_A$ (3.1)–(3.2) or $f_B(Y)=-\gamma^{(+)}(N,Y)+\gamma^{(-)}(N,Y)$.
* Conceptually, the inhomogeneous deformation is an **infinitesimal change of the oscillator basis**
  $x\mapsto x+\kappa h(x)$ (Prop. 3.2: every mixed antisymmetric perturbation of the pre-oscillator form is
  induced by an odd endomorphism), and independently it is forced to be trivial by the $\mathbf Z$-grading
  of the type-I superalgebra $C(n+1)$ (Cor. 4.3: all odd adjoint cohomology vanishes).
* The question "can any non-zero configuration of $gb$ satisfy $\gamma_{gb}=\delta f$?" has the answer:
  **every** configuration does, and the corresponding cochains are non-zero, so the $gb$ family consists
  of non-zero coboundaries; it does not produce a genuine (non-equivalent) deformation of $C(n+1)$.
