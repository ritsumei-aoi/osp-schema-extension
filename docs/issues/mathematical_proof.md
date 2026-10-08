# Triviality of the Inhomogeneous (gb) Deformation of $C(n+1)=\mathfrak{osp}(2|2n)$

**Status**: resolved (definitive conclusion reached)
**Run**: study/thm01-R-fable51-b05-C
**Inputs used**: `docs/math/Cn1_definition.md`, `docs/math/C_inhomogeneous_definition.md`,
`docs/math/C_coboundary_definition.md`, `docs/issues/issue_open.md` only (no external sources).
**Artifacts**: `scripts/cn1_deformation.py`, `scripts/cn1_cohomology.py`,
`artifacts/Cn1_n{1,2,3}_verification.json`, `artifacts/Cn1_n{1,2,3}_cohomology.json`.

---

## 0. Statement of the result

**Main Theorem.** Let $n\ge 1$ and let $\mathrm{gb}=(\mathrm{gb}_{\sigma,j,s})\in\mathbb{C}^{4n}$ be an arbitrary
collection of inhomogeneous deformation parameters. Let $\gamma_{\mathrm{gb}}$ be the induced
2-cochain on $\mathfrak{g}=C(n+1)$ (defined in §1). Then there is an explicit odd linear map
$f_{\mathrm{gb}}:\mathfrak{g}\to\mathfrak{g}$, linear in $\mathrm{gb}$, such that

$$\gamma_{\mathrm{gb}}(X,Y)\;=\;(\delta f_{\mathrm{gb}})(X,Y)\qquad\text{for all }X,Y\in\mathfrak{g},$$

**as elements of the adjoint representation, i.e. up to scalar (central) terms**, exactly in
the sense of `docs/math/C_coboundary_definition.md` §3.
Consequently:

> **The necessary and sufficient condition on $\mathrm{gb}$ for $\gamma_{\mathrm{gb}}$ to be trivial is
> empty: every inhomogeneous deformation of $C(n+1)$ is trivial, for every $n\ge1$ and every
> value of the $4n$ parameters.** The space of admissible $f$ is the affine space
> $f_{\mathrm{gb}}+\{\operatorname{ad}Z : Z\in\mathfrak{g}_{\bar1}\}$ of dimension $4n$.

Two supplementary facts sharpen the picture and explain the role of the
"adjoint representation / up to scalar" clause:

1. **(Scalar terms: where they come from and why they are harmless.)** Computed literally in the
   enveloping algebra, $\gamma_{\mathrm{gb}}$ takes values in $U_{\le 2}=\mathfrak{g}\oplus\mathbb{C}\cdot 1$, and its scalar
   component depends on which representative of the odd generators one uses in $U(A')$: the
   document's word $a^\sigma b_l^s$, the normal-ordered word $b_l^s a^\sigma$ and the super-symmetrised
   $\tfrac12(a^\sigma b_l^s+b_l^s a^\sigma)$ differ from each other by the *central* element
   $\mathrm{gb}_{\sigma,l,s}\kappa$ (up to a factor). Changing representatives $Z\mapsto Z+\kappa s(Z)$,
   $s:\mathfrak{g}\to\mathbb{C}$, leaves all brackets unchanged but changes $\gamma$ by the coboundary $\delta s$ of a
   scalar map. With the document's or the normal-ordered words the scalar component
   $\gamma^{\rm sc}_{\mathrm{gb}}$ is non-zero for every $\mathrm{gb}\neq0$ (the map $\mathrm{gb}\mapsto\gamma^{\rm sc}_{\mathrm{gb}}$ is
   injective), so for those representatives the *literal* identity $\gamma_{\mathrm{gb}}=\delta f$ with
   $f:\mathfrak{g}\to\mathfrak{g}$ holds only for $\mathrm{gb}=0$; but $\gamma^{\rm sc}_{\mathrm{gb}}=\delta c_{\mathrm{gb}}$ for an explicit scalar
   odd map $c_{\mathrm{gb}}$, and **with the super-symmetrised representatives the scalar component
   vanishes identically and $\gamma_{\mathrm{gb}}=\delta f_{\mathrm{gb}}$ holds literally** (verified directly for
   $n=1,2,3$). The clause "as an adjoint representation / up to scalar" is thus exactly the
   statement that the answer must not depend on this choice of section; it is not a loophole.
2. **(Structural reason.)** $H^{k}(\mathfrak{g},\mathfrak{g})_{\bar1}=0$ and $H^{k}(\mathfrak{g},\mathbb{C})_{\bar1}=0$ for
   all $k$ (Theorem 5): on $C(n+1)$ the parity of a homogeneous element equals its
   $\mathfrak{so}(2)$-charge mod 2, so *no non-zero odd cochain can have weight zero*. Hence
   **every** odd 2-cocycle with values in $\mathfrak{g}$ or in $\mathbb{C}$ is a coboundary. This gives a second,
   independent proof of the Main Theorem valid for all $n$.

The computational artifacts verify, with exact rational arithmetic, every step for
$n=1,2,3$ (dimensions $8,19,34$), and additionally verify the cohomological statements by
independent rank computations that never use the explicit $f$.

---

## 1. Setting and conventions

### 1.1 The deformed oscillator superalgebra

$V=V_{\bar0}\oplus V_{\bar1}$ with $V_{\bar0}=\operatorname{span}\{b_j^{\pm}\}_{j=1}^n$,
$V_{\bar1}=\operatorname{span}\{a^{+},a^{-}\}$ (we write $a^\pm$ for $a_1^\pm$). The extension
$A'=V\oplus\mathbb{C}K\oplus\mathbb{C}\kappa$ carries the bracket of `C_inhomogeneous_definition.md`,
with $K$ even central, $\kappa$ odd central. We work in $U(A')/(K-1)$ and keep writing $U(A')$.
The relations are

$$\{a^-,a^+\}=1,\qquad [b_j^-,b_k^+]=\delta_{jk},\qquad
[b_j^{s},a^{\sigma}]=-\,\mathrm{gb}_{\sigma,j,s}\,\kappa\quad(\sigma,s\in\{+,-\}),$$

all other brackets of generators being $0$, together with the consequences of $\kappa$ being
**odd and central** in the super sense: $\kappa$ commutes with even elements, anticommutes with
odd ones, and

$$\kappa^2=\tfrac12[\kappa,\kappa]=0 .$$

Because $[b,a]$ is odd and $\kappa$ is odd, the parameters $\mathrm{gb}_{\sigma,j,s}$ are ordinary
(even) complex numbers; the "parity 1" remark of the definition document refers to the
*deformation cochain* $\gamma$ and to $f$, which are odd (parity-reversing) maps. (All results are
$\mathbb{C}$-linear in $\mathrm{gb}$; they remain valid verbatim over any commutative even coefficient ring.)

$\mathrm{gb}=0$ gives the undeformed algebra $A$. Nothing is lost by the normalisation
$E_{\pm2\delta_k}=(b_k^\pm)^2$ versus $\tfrac12(b_k^\pm)^2$; we use the "All root generators"
table of `Cn1_definition.md` §2.

### 1.2 $C(n+1)$ inside $U(A)$ and the canonical splitting $U_{\le2}=\mathfrak{g}\oplus\mathbb{C}1$

$\mathfrak{g}=C(n+1)$ is the span of the $2n^2+5n+1$ elements of `Cn1_definition.md` §2:
$H_1,\dots,H_{n+1}$, $E_{\pm\delta_k\pm\delta_l}$, $E_{\pm2\delta_k}$, $E_{\pm\varepsilon\pm\delta_l}$.
Writing $A:=a^+a^--\tfrac12=\tfrac12[a^+,a^-]$ and $N_k:=b_k^+b_k^-+\tfrac12=\tfrac12\{b_k^+,b_k^-\}$ one has
$H_1=A+N_1$, $H_k=N_{k-1}-N_k$ $(2\le k\le n)$, $H_{n+1}=-N_n$, so

$$\mathfrak{g}=\operatorname{span}\{\text{super-symmetrised quadratic monomials in }a^\pm,b_j^\pm\}
=\mathfrak{so}(2)\oplus\mathfrak{sp}(2n)\oplus\mathfrak{g}_{\bar1},$$

the standard oscillator realisation of $\mathfrak{osp}(2|2n)$. The script checks that $\mathfrak{g}$ is closed under
the supercommutator **without any constant terms** and reproduces the distinguished Cartan matrix
(simple roots $\varepsilon-\delta_1,\ \delta_{k-1}-\delta_k,\ 2\delta_n$; e.g. for $n=3$:
$\bigl(\begin{smallmatrix}0&1&0&0\\-1&2&-1&0\\0&-1&2&-2\\0&0&1&-2\end{smallmatrix}\bigr)$, the
first simple root being odd isotropic).

The space of elements of degree $\le2$ in the oscillators is $U_{\le2}=\mathfrak{g}\oplus\mathbb{C}\cdot1$.
Under the adjoint action of $\mathfrak{g}$ this is a direct sum of $\mathfrak{g}$-modules,
$\mathfrak{g}_{\rm ad}\oplus\mathbb{C}_{\rm triv}$, and since $\mathfrak{g}$ is simple,
$\operatorname{Hom}_{\mathfrak g}(\mathfrak{g},\mathbb{C})=\operatorname{Hom}_{\mathfrak g}(\mathbb{C},\mathfrak{g})=0$;
hence **the projection $\pi_{\rm ad}:U_{\le2}\to\mathfrak{g}$ along $\mathbb{C}1$ is canonical**.
Equivalently, $\pi_{\rm ad}(u)$ is determined by the adjoint action $\operatorname{ad}u$ on $U(A')$,
because $\ker(\operatorname{ad}|_{U_{\le2}})=\mathbb{C}1$. This is precisely the content of the phrases
"realized as a subalgebra of $U(A)$ by adjoint representation" and "equal … as an adjoint
representation, … up to scalar" in the definition documents.

**Sections.** Inside $U(A')$ the odd generators have several natural representatives, which differ
by central elements and therefore have identical brackets with everything:
$$a^\sigma b_l^s\ (\text{document})\;=\;b_l^s a^\sigma\ (\text{normal order})+\mathrm{gb}_{\sigma,l,s}\kappa,\qquad
\tfrac12\bigl(a^\sigma b_l^s+b_l^s a^\sigma\bigr)\ (\text{symmetrised})\;=\;b_l^s a^\sigma+\tfrac12\mathrm{gb}_{\sigma,l,s}\kappa .$$
A choice of representatives is a section $\mathfrak{g}\to U(A')$ of the deformed algebra, unique up to
$Z\mapsto Z+\kappa s(Z)$ with $s:\mathfrak{g}\to\mathbb{C}$ (odd, since $\kappa$ is odd). The structure constants
$C_{ij}^k$ and $\gamma^{\rm ad}$ are independent of the section; only $\gamma^{\rm sc}$ moves, by
$\gamma\mapsto\gamma+\delta s$ with $(\delta s)(X,Y)=-s([X,Y])$ (see §1.4). The scripts use the
normal-ordered words as the primary section and the symmetrised one as a cross-check.

### 1.3 The deformation cochain $\gamma_{\mathrm{gb}}$

For homogeneous $X,Y\in\mathfrak{g}$ (as words in $a,b$) the supercommutator in $U(A')$ is

$$[X,Y]_{U(A')}=[X,Y]_0+\kappa\,\gamma_{\mathrm{gb}}(X,Y),\qquad
\gamma_{\mathrm{gb}}(X,Y)=\gamma^{\rm ad}_{\mathrm{gb}}(X,Y)+\gamma^{\rm sc}_{\mathrm{gb}}(X,Y)\cdot 1,$$

with $\gamma^{\rm ad}\in\mathfrak{g}$, $\gamma^{\rm sc}\in\mathbb{C}$, both linear in $\mathrm{gb}$ and of parity
$p(X)+p(Y)+1$ (so $\gamma$ is an odd cochain; $\gamma^{\rm sc}$ is supported on even–odd pairs).
Example ($n$ arbitrary, $k$ fixed; a direct computation, reproduced by `scripts/example_bracket.py`):

$$[\,b_k^+b_k^-,\ b_k^+a^\sigma\,]_{U(A')}=b_k^+a^\sigma-\kappa\Bigl(\mathrm{gb}_{\sigma,k,+}\,b_k^+b_k^-+\mathrm{gb}_{\sigma,k,-}\,(b_k^+)^2\Bigr).$$

Re-expressed in the three sections of §1.2 (recall $N_k=b_k^+b_k^-+\tfrac12$):
$$\gamma(N_k,E_{\sigma\varepsilon+\delta_k})=-\mathrm{gb}_{\sigma,k,+}N_k-\mathrm{gb}_{\sigma,k,-}E_{2\delta_k}+
\begin{cases}+\tfrac12\mathrm{gb}_{\sigma,k,+}\cdot1&\text{normal-ordered section},\\
-\tfrac12\mathrm{gb}_{\sigma,k,+}\cdot1&\text{document section},\\
0&\text{symmetrised section}.\end{cases}$$

The adjoint part is the same in all three; the scalar is the prototype of the terms discussed in item 1 of §0.

Super-skew-symmetry $\gamma(X,Y)=-(-1)^{p(X)p(Y)}\gamma(Y,X)$ is inherited from $U(A')$ (checked).

### 1.4 Coboundary and the abelian extension $L=\mathfrak{g}\oplus\kappa\mathfrak{g}$

For an odd linear map $f$ the definition document sets

$$(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y]).\tag{1.1}$$

If $f$ is allowed to take values in $\mathfrak{g}\oplus\mathbb{C}1$, the brackets in (1.1) only see the
$\mathfrak{g}$-component of $f$, while $f([X,Y])$ sees both; for a purely scalar $c:\mathfrak{g}\to\mathbb{C}$ one gets
$(\delta c)(X,Y)=-c([X,Y])$.

**Lemma 1 (sign rules for $\kappa$).** For homogeneous $X,Y\in U(A')$, modulo $\kappa^2=0$:
$$[X,\kappa Y]=(-1)^{p(X)}\kappa[X,Y],\qquad [\kappa X,Y]=\kappa[X,Y].$$
*Proof.* $p(\kappa Y)=p(Y)+1$. Then
$[X,\kappa Y]=X\kappa Y-(-1)^{p(X)(p(Y)+1)}\kappa YX
=(-1)^{p(X)}\kappa\bigl(XY-(-1)^{p(X)p(Y)}YX\bigr)$, and
$[\kappa X,Y]=\kappa XY-(-1)^{(p(X)+1)p(Y)}Y\kappa X=\kappa\bigl(XY-(-1)^{p(X)p(Y)}YX\bigr)$. $\square$

These are the brackets of the abelian extension $L=\mathfrak{g}\oplus\kappa\mathfrak{g}$ of the definition document
($\kappa$ acts trivially, $[\kappa X,\kappa Y]=0$). The script verifies Lemma 1 on all pairs of basis vectors.

**Lemma 2 (the doc's $\delta$ is the first-order change of basis).** Let $f:\mathfrak{g}\to\mathfrak{g}\oplus\mathbb{C}1$ be odd
and $\Phi_f(X):=X+\kappa f(X)$. Then in $U(A')$, modulo $\kappa^2$,
$$[\Phi_f(X),\Phi_f(Y)]=[X,Y]_0+\kappa\bigl(\gamma_{\mathrm{gb}}(X,Y)+(\delta f)(X,Y)+f([X,Y]_0)\bigr).$$
Consequently $\Phi_f$ is a homomorphism from $(\mathfrak{g},[\ ,\ ]_0)$ onto the deformed algebra, i.e.
$[\Phi_f(X),\Phi_f(Y)]=\Phi_f([X,Y]_0)$, **iff** $\gamma_{\mathrm{gb}}=-\delta f=\delta(-f)$.
*Proof.* Expand: $[X+\kappa f(X),Y+\kappa f(Y)]=[X,Y]_{U(A')}+[X,\kappa f(Y)]+[\kappa f(X),Y]$ (the
$\kappa\kappa$ term vanishes). By Lemma 1 this is
$[X,Y]_0+\kappa\gamma(X,Y)+(-1)^{p(X)}\kappa[X,f(Y)]+\kappa[f(X),Y]$, and
$[f(X),Y]=-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]$ because $p(f(X))=p(X)+1$. Comparing with (1.1) gives the formula.
$\square$

So the triviality notion of the definition document (with $f\mapsto -f$, and with any overall
scalar factor absorbed into $f$) is the standard one: *$\gamma_{\mathrm{gb}}$ is trivial iff the deformed
algebra is isomorphic to the undeformed one via an isomorphism of the form $\mathrm{id}+\kappa f$.*
This is the sense in which "up to scalar" (reading B: $\gamma=\lambda\,\delta f$) is harmless, and
"as an adjoint representation / up to scalar" (reading A: equality in $U_{\le2}/\mathbb{C}1\cong\mathfrak{g}$) is
the substantive one. We prove the theorem in reading A and also in the stronger form
where $f$ may take values in $\mathfrak{g}\oplus\mathbb{C}1$.

---

## 2. The untwisting isomorphism (constructive proof)

**Proposition 3.** Put, for $\sigma\in\{+,-\}$,
$$m^{\sigma}:=\sum_{j=1}^{n}\bigl(\mathrm{gb}_{\sigma,j,-}\,b_j^{+}-\mathrm{gb}_{\sigma,j,+}\,b_j^{-}\bigr)\in V_{\bar0},
\qquad \tilde a^{\sigma}:=a^{\sigma}+\kappa\,m^{\sigma}.$$
Then $\tilde a^\pm,\ b_j^\pm,\ 1,\ \kappa$ satisfy the **undeformed** relations in $U(A')$:
$\{\tilde a^-,\tilde a^+\}=1$, $\{\tilde a^\sigma,\tilde a^\sigma\}=0$, $[b_j^-,b_k^+]=\delta_{jk}$,
$[b_j^s,\tilde a^\sigma]=0$, $\kappa$ odd central. Hence
$$\Phi:U(A)\longrightarrow U(A'),\qquad a^\sigma\mapsto\tilde a^\sigma,\quad b_j^s\mapsto b_j^s,\quad \kappa\mapsto\kappa$$
is a well-defined isomorphism of associative superalgebras (inverse: $a^\sigma=\tilde a^\sigma-\kappa m^\sigma$).

*Proof.* $[b_j^s,\tilde a^\sigma]=[b_j^s,a^\sigma]+\kappa[b_j^s,m^\sigma]$ ($b$ even, so $\kappa$ passes through).
Using $[b_j^+,b_j^-]=-1$, $[b_j^-,b_j^+]=1$:
$[b_j^+,m^\sigma]=\mathrm{gb}_{\sigma,j,+}$ and $[b_j^-,m^\sigma]=\mathrm{gb}_{\sigma,j,-}$, so
$[b_j^s,\tilde a^\sigma]=-\mathrm{gb}_{\sigma,j,s}\kappa+\mathrm{gb}_{\sigma,j,s}\kappa=0$.
Next, $\{a^\sigma,\kappa m^\tau\}=a^\sigma\kappa m^\tau+\kappa m^\tau a^\sigma=\kappa(m^\tau a^\sigma-a^\sigma m^\tau)=\kappa[m^\tau,a^\sigma]$,
and $[m^\tau,a^\sigma]\in\mathbb{C}\kappa$, so this is $0$ by $\kappa^2=0$; also
$\{\kappa m^\sigma,\kappa m^\tau\}=\kappa^2(\cdots)=0$. Hence $\{\tilde a^\sigma,\tilde a^\tau\}=\{a^\sigma,a^\tau\}$.
Finally $[\kappa,\tilde a^\sigma]=\kappa a^\sigma+a^\sigma\kappa+\kappa^2m^\sigma+\kappa m^\sigma\kappa=0$. $\square$

**Definition of $f_{\mathrm{gb}}$.** For $X\in\mathfrak{g}\subset U(A)$ write $\Phi(X)=X+\kappa\,\Phi_1(X)$ with
$\Phi_1(X)\in U_{\le2}=\mathfrak{g}\oplus\mathbb{C}1$ ($\Phi_1$ is odd, linear in $\mathrm{gb}$). Set
$$F_{\mathrm{gb}}:=-\Phi_1=f_{\mathrm{gb}}+c_{\mathrm{gb}},\qquad f_{\mathrm{gb}}:=\pi_{\rm ad}F_{\mathrm{gb}}:\mathfrak{g}\to\mathfrak{g},\quad c_{\mathrm{gb}}:=\pi_{\rm sc}F_{\mathrm{gb}}:\mathfrak{g}\to\mathbb{C}.$$

Explicitly (normal-ordered representatives; "$\equiv$" means modulo $\mathbb{C}1$):

| basis element $X$ | $f_{\mathrm{gb}}(X)$ | $c_{\mathrm{gb}}(X)$ |
|---|---|---|
| any purely bosonic $X$ ($E_{\pm\delta_k\pm\delta_l},E_{\pm2\delta_k},H_2,\dots,H_{n+1}$) | $0$ | $0$ |
| $H_1$ | $a^+m^- - a^-m^+ =\sum_j\bigl(\mathrm{gb}_{-,j,-}E_{\varepsilon+\delta_j}-\mathrm{gb}_{-,j,+}E_{\varepsilon-\delta_j}-\mathrm{gb}_{+,j,-}E_{-\varepsilon+\delta_j}+\mathrm{gb}_{+,j,+}E_{-\varepsilon-\delta_j}\bigr)$ | $0$ |
| $E_{\sigma\varepsilon+s\delta_l}=b_l^{s}a^{\sigma}$ | $-\,b_l^{s}m^{\sigma}\ \bmod\ \mathbb{C}1\;=\;\sum_j\bigl(\mathrm{gb}_{\sigma,j,+}\,b_l^{s}b_j^{-}-\mathrm{gb}_{\sigma,j,-}\,b_l^{s}b_j^{+}\bigr)\bmod \mathbb{C}1$ | $-\tfrac12\,\mathrm{gb}_{\sigma,l,s}$ |

(The $\mathfrak{sp}(2n)$ products $b_l^sb_j^{\pm}$ are the even root vectors or $N_j\mp\tfrac12$; the dropped
$\mp\tfrac12$ is the scalar column.) For instance, for $n=2$ and the single parameter $\mathrm{gb}_{+,1,+}$:
$f(H_1)=E_{-\varepsilon-\delta_1}$, $f(E_{\varepsilon+\delta_1})=N_1=H_2-H_3$, $f(E_{\varepsilon-\delta_1})=E_{-2\delta_1}$,
$f(E_{\varepsilon+\delta_2})=E_{\delta_2-\delta_1}$, $f(E_{\varepsilon-\delta_2})=E_{-\delta_1-\delta_2}$, $c(E_{\varepsilon+\delta_1})=-\tfrac12$,
all other values $0$ (this is the entry `f_phi_per_gb["gb[a+,b1+]"]` of `Cn1_n2_verification.json`).

**Theorem 4 (Main Theorem, constructive form).** For all $n\ge1$ and all $\mathrm{gb}\in\mathbb{C}^{4n}$:
$$\gamma^{\rm ad}_{\mathrm{gb}}=\delta f_{\mathrm{gb}}\quad\text{in }\mathfrak{g},\qquad
\gamma^{\rm sc}_{\mathrm{gb}}=\delta c_{\mathrm{gb}}\quad\text{in }\mathbb{C},\qquad\text{i.e.}\quad
\gamma_{\mathrm{gb}}=\delta F_{\mathrm{gb}}\ \text{ in }\mathfrak{g}\oplus\mathbb{C}1 .$$
In particular $\gamma_{\mathrm{gb}}$ is trivial in the sense of `C_coboundary_definition.md` §3 for every $\mathrm{gb}$.

*Proof.* $\Phi$ is an algebra isomorphism (Prop. 3), hence for $X,Y\in\mathfrak{g}$,
$[\Phi(X),\Phi(Y)]_{U(A')}=\Phi([X,Y]_{U(A)})=\Phi([X,Y]_0)=[X,Y]_0+\kappa\Phi_1([X,Y]_0)$, i.e.
$\Phi=\Phi_{\Phi_1}$ is a homomorphism $(\mathfrak{g},[\,,]_0)\to U(A')$. By Lemma 2 (with $f=\Phi_1$,
values in $\mathfrak{g}\oplus\mathbb{C}1$) this is equivalent to $\gamma_{\mathrm{gb}}=\delta(-\Phi_1)=\delta F_{\mathrm{gb}}$ in
$\mathfrak{g}\oplus\mathbb{C}1$. Since $\mathfrak{g}\oplus\mathbb{C}1=\mathfrak{g}_{\rm ad}\oplus\mathbb{C}_{\rm triv}$ as $\mathfrak{g}$-modules and $\delta$
respects the decomposition, projecting gives the two displayed identities. $\square$

**Corollary 4.1 (the scalar terms, and why "as adjoint representation / up to scalar" is the right
notion).** In the normal-ordered section, $\gamma^{\rm sc}_{\mathrm{gb}}(N_l,\,b_l^{s}a^{\sigma})=\tfrac{s}{2}\mathrm{gb}_{\sigma,l,s}$;
hence $\mathrm{gb}\mapsto\gamma^{\rm sc}_{\mathrm{gb}}$ is injective and $\gamma^{\rm sc}_{\mathrm{gb}}\neq0$ whenever $\mathrm{gb}\ne0$ (the same
holds in the document's section, with the opposite sign). Since $\delta f$ has no scalar component for
$f:\mathfrak{g}\to\mathfrak{g}$, in these two sections the *literal* equation $\gamma_{\mathrm{gb}}=\delta f$ in $U_{\le2}$ with
$f:\mathfrak{g}\to\mathfrak{g}$ is solvable **iff $\mathrm{gb}=0$**. However:
(i) the obstruction lives entirely in the trivial summand $\mathbb{C}1$, which is invisible in the adjoint
representation ($\operatorname{ad}1=0$);
(ii) it is exact, $\gamma^{\rm sc}=\delta c_{\mathrm{gb}}$, $c_{\mathrm{gb}}(E_{\sigma\varepsilon+s\delta_l})=-\tfrac12\mathrm{gb}_{\sigma,l,s}$;
(iii) it is an artefact of the section: passing to the super-symmetrised representatives
$Z\mapsto Z+\kappa s(Z)$ with $s=-c_{\mathrm{gb}}$ (i.e. $s(E_{\sigma\varepsilon+s\delta_l})=+\tfrac12\mathrm{gb}_{\sigma,l,s}$)
changes $\gamma$ by $\delta s=-\gamma^{\rm sc}$, so that **in the symmetrised section
$\gamma^{\rm sc}_{\mathrm{gb}}\equiv0$ and $\gamma_{\mathrm{gb}}=\delta f_{\mathrm{gb}}$ holds literally, with
$f_{\mathrm{gb}}:\mathfrak{g}\to\mathfrak{g}$ the map of the table above.** (Verified by direct recomputation of all
brackets with the symmetrised elements for $n=1,2,3$: `checks.symmetrized_section` in the artifacts.)
Under the definition adopted in the documents (equality as adjoint representation / up to scalar),
which is precisely the section-independent formulation, there is no obstruction for any $\mathrm{gb}$.

**Corollary 4.2 (uniqueness).** $f$ is unique up to $Z^1(\mathfrak{g},\mathfrak{g})_{\bar1}$ = odd derivations
$=\{\operatorname{ad}Z: Z\in\mathfrak{g}_{\bar1}\}$ (Theorem 5 gives $H^1_{\bar1}=0$; $\operatorname{ad}$ is injective
since $\mathfrak{g}$ is simple), an affine space of dimension $4n$. (Verified: $\dim Z^1_{\bar1}=4,8,12$ for $n=1,2,3$.)

---

## 3. Structural proof: odd cohomology of $C(n+1)$ vanishes

**Lemma (parity = $\mathfrak{so}(2)$-charge).** Let $A=\tfrac12[a^+,a^-]=H_1-H_2-\dots-H_n+H_{n+1}$ be the
generator of $\mathfrak{so}(2)\subset\mathfrak{g}_{\bar0}$. $\operatorname{ad}A$ is diagonal in the root basis with eigenvalue
$0$ on $\mathfrak{g}_{\bar0}$ and $\pm1$ on $\mathfrak{g}_{\bar1}$ (the $\varepsilon$-coefficient of the root). Hence for every
homogeneous $X\in\mathfrak{g}$: $\ \mathrm{charge}(X)\equiv p(X)\pmod 2$. The same holds on the modules
$\mathbb{C}$ (charge $0$, even) and $\mathfrak{g}\oplus\mathbb{C}1$.

**Theorem 5.** For $M\in\{\mathfrak{g},\ \mathbb{C},\ \mathfrak{g}\oplus\mathbb{C}1\}$ and all $k\ge0$: $H^k(\mathfrak{g},M)_{\bar1}=0$.
In particular every odd 2-cocycle (= first-order odd deformation of the bracket, equivalently a
Lie superalgebra structure on $L=\mathfrak{g}\oplus\kappa\mathfrak{g}$ extending $[\,,]_0$) is a coboundary, and every odd
derivation of $\mathfrak{g}$ is inner.

*Proof.* The Chevalley–Eilenberg complex $C^\bullet(\mathfrak{g},M)$ splits under $\operatorname{ad}A$ (which acts
semisimply and commutes with $d$) into weight subcomplexes $C^\bullet_\lambda$. Cartan's formula
$L_A=d\,i_A+i_A\,d$ (valid for even $A$ in the super setting) shows $L_A=\lambda$ is null-homotopic on
$C^\bullet_\lambda$, so $H(C^\bullet_\lambda)=0$ for $\lambda\neq0$ and $H^\bullet(\mathfrak{g},M)=H(C^\bullet_0)$.
Now let $\varphi$ be an odd $k$-cochain and consider a component mapping
$X_1\otimes\dots\otimes X_k\mapsto m$ with all $X_i,m$ homogeneous. Its weight is
$\lambda=\sum_i\mathrm{charge}(X_i)-\mathrm{charge}(m)\equiv\sum_i p(X_i)+p(m)\equiv p(\varphi)=1\pmod2$ by the Lemma.
Thus $\lambda\ne0$ for every non-zero component: $C^k_0\cap C^k_{\bar1}=0$, and $H^k(\mathfrak{g},M)_{\bar1}=0$. $\square$

(The computation confirms this literally: the weight-zero odd subcomplex has $0$ unknowns for
$n=1,2,3$, while the full complexes give $\dim Z^2_{\bar1}=\dim B^2_{\bar1}=28,168,516$.)

**Second proof of the Main Theorem.** The deformed bracket is the supercommutator of $U(A')$, so it
satisfies the super-Jacobi identity; its order-$\kappa$ part says that $\gamma_{\mathrm{gb}}$ is an odd
2-cocycle with values in $\mathfrak{g}\oplus\mathbb{C}1$. By Theorem 5 it is a coboundary $\delta F$,
$F:\mathfrak{g}\to\mathfrak{g}\oplus\mathbb{C}1$ odd, and projecting to the adjoint summand, $\gamma^{\rm ad}_{\mathrm{gb}}=\delta(\pi_{\rm ad}F)$. $\square$

This proof shows more: **any** odd first-order deformation of the pre-oscillator form (not only the
"inhomogeneous" $gb$-type one), and indeed any odd 2-cocycle of $C(n+1)$ whatsoever, is trivial.
The $gb$-deformation is thus trivial for a reason intrinsic to $C(n+1)$ — the $\mathfrak{so}(2)$ factor of
$\mathfrak{g}_{\bar0}$ grades parity — in addition to the explicit untwisting of Proposition 3, which is
specific to deformations coming from the oscillator form and does not even need simplicity of $\mathfrak{g}$.

---

## 4. Answer to the questions of `issue_open.md`

* **Consistency between the two deformation structures ($n=1,2,3$).** Both $\gamma_{\mathrm{gb}}$ and $\delta f$
  are odd super-skew cochains; $\gamma_{\mathrm{gb}}$ takes values in $\mathfrak{g}\oplus\mathbb{C}1$, $\delta f$ (for
  $f:\mathfrak{g}\to\mathfrak{g}$) in $\mathfrak{g}$. They are compared in the adjoint module $\mathfrak{g}=U_{\le2}/\mathbb{C}1$. With the doc's
  sign conventions (1.1), the identity $\gamma=\delta f$ is exactly the statement that $X\mapsto X-\kappa f(X)$
  is an isomorphism from the undeformed to the deformed algebra (Lemma 2).
* **Can a non-zero $\mathrm{gb}$ satisfy $\gamma_{\mathrm{gb}}=\delta f$?** Yes — **every** $\mathrm{gb}\in\mathbb{C}^{4n}$ does,
  with $f=f_{\mathrm{gb}}$ of §2 (modulo scalars / in the adjoint representation). Taken literally with
  scalars included and $f$ restricted to $\mathfrak{g}$-values, no non-zero $\mathrm{gb}$ does, and the failure is
  exactly the exact scalar cocycle $\gamma^{\rm sc}=\delta c$ (Cor. 4.1).
* **Necessary and sufficient condition:** none (the condition is $\mathrm{gb}\in\mathbb{C}^{4n}$). Equivalently, the
  image of $\mathrm{gb}\mapsto[\gamma^{\rm ad}_{\mathrm{gb}}]\in H^2(\mathfrak{g},\mathfrak{g})_{\bar1}$ is $0$ because the target is $0$.

---

## 5. Computational artifacts and what they verify

All code is in `scripts/` and is self-contained (Python 3, standard library only; exact `Fraction`
arithmetic in `cn1_deformation.py`, exact arithmetic in $\mathrm{GF}(p)$, $p=2^{31}-1$, in
`cn1_cohomology.py`). Re-run with

```
python3 scripts/cn1_deformation.py 1 2 3
python3 scripts/cn1_cohomology.py 1 2 3 --full
```

### 5.1 `scripts/cn1_deformation.py` → `artifacts/Cn1_n{n}_verification.json`

Implements $U(A')$ with normal ordering ($\kappa<b^+<b^-<a^+<a^-$), coefficients being linear forms
$c_0+\sum c_{\sigma,j,s}\,\mathrm{gb}_{\sigma,j,s}$ (no $\mathrm{gb}^2$ can occur since $\kappa^2=0$, and this is asserted).
For each $n$ it:

1. builds the basis of `Cn1_definition.md` (names, parities, weights, oscillator words);
2. computes all $[Z_i,Z_j]$ in $U(A')$ and decomposes them as $C_{ij}^k Z_k+\kappa\bigl(\gamma^{{\rm ad},k}_{ij}Z_k+\gamma^{\rm sc}_{ij}\cdot1\bigr)$,
   asserting closure of $\mathfrak{g}$ **without constants**, absence of $\mathrm{gb}$ in the $\kappa^0$ part, and super-skew-symmetry;
3. verifies Lemma 1 (both $\kappa$ sign rules) on all pairs;
4. verifies Proposition 3: the untwisted generators satisfy the undeformed relations, and
   $[\Phi(Z_i),\Phi(Z_j)]=\Phi([Z_i,Z_j]_0)$ **exactly** in $U(A')$ for all $i,j$;
5. extracts $F=-\Phi_1=(\,\phi,\ c\,)$ and verifies, per unit parameter, $\gamma^{\rm ad}=\delta\phi$ and
   $\gamma^{\rm sc}=\delta c$ with the doc's formula (1.1) evaluated on the structure constants;
6. verifies $\gamma^{\rm sc}\ne0$ for each unit parameter and $\operatorname{rank}(\mathrm{gb}\mapsto\gamma^{\rm sc})=4n$
   (normal-ordered section);
7. recomputes every bracket directly with the super-symmetrised odd generators and verifies that in
   that section $\gamma^{\rm sc}\equiv0$ while $\gamma^{\rm ad}$ is unchanged, and that the section shift $s$
   equals $-c_{\mathrm{gb}}$ (`checks.symmetrized_section`).

JSON keys (all values are exact rationals as strings; tensors are given **per unit gb parameter**,
and the general case is the linear combination):
`basis`, `structure_constants_C[i][j][k]`, `gamma_ad_per_gb`, `gamma_scalar_per_gb`,
`untwisting_map.f_phi_per_gb` ($f(Z_j)=\sum_i\phi_{ij}Z_i$, stored as `{Z_j: {Z_i: phi_ij}}`),
`untwisting_map.f_scalar_per_gb`, `cartan_matrix_*`, `checks`.

### 5.2 `scripts/cn1_cohomology.py` → `artifacts/Cn1_n{n}_cohomology.json`

Uses only `structure_constants`, `gamma_ad_per_gb`, `gamma_scalar_per_gb` (never the explicit $f$):

1. builds the matrix of $\delta$ on odd 1-cochains $\phi$ (and optionally scalar unknowns $c$) and
   decides solvability of $\gamma^{\rm ad}=\delta\phi$ for each unit parameter and for a random $\mathrm{gb}$ by rank
   comparison; computes $\dim Z^1_{\bar1}$ and $H^1_{\bar1}$;
2. decides the literal equation $\gamma=\delta\phi$ in $\mathfrak{g}\oplus\mathbb{C}1$ with $\phi:\mathfrak{g}\to\mathfrak{g}$ (expected: unsolvable)
   and with $\phi:\mathfrak{g}\to\mathfrak{g}\oplus\mathbb{C}1$ (expected: solvable);
3. sets up the odd 2-cocycle condition as the order-$\kappa$ part of super-Jacobi on $L=\mathfrak{g}\oplus\kappa\mathfrak{g}$
   (Lemma 1 sign rules), checks that every $\gamma^{\rm ad}_{\mathrm{gb}}$ and a random $\delta\phi$ satisfy it, and
   computes $\dim Z^2_{\bar1}$, $\dim B^2_{\bar1}$, $H^2_{\bar1}$ on the weight-zero subcomplex and on the full complex.

### 5.3 Results table

| $n$ | $\dim\mathfrak{g}$ | $\#\mathrm{gb}$ | $\gamma^{\rm ad}=\delta f$ (exact, per gb) | $\gamma^{\rm sc}=\delta c$ | rank$(\mathrm{gb}\mapsto\gamma^{\rm sc})$ (normal-ordered section) | $\gamma^{\rm sc}\equiv0$ in symmetrised section | $\gamma^{\rm ad}=\delta\phi$ solvable (rank test) | literal $\gamma=\delta\phi$, $\phi:\mathfrak{g}\to\mathfrak{g}$, normal-ordered section | $\dim Z^1_{\bar1}$ / inner | $H^1_{\bar1}$ | odd 2-cochains / $Z^2_{\bar1}$ / $B^2_{\bar1}$ | $H^2_{\bar1}$ | weight-0 odd cochains |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 8 = 4\|4 | 4 | ✓ | ✓ | 4 | ✓ | ✓ (all, random) | ✗ for every unit gb | 4 / 4 | 0 | 128 / 28 / 28 | 0 | 0 |
| 2 | 19 = 11\|8 | 8 | ✓ | ✓ | 8 | ✓ | ✓ (all, random) | ✗ for every unit gb | 8 / 8 | 0 | 1696 / 168 / 168 | 0 | 0 |
| 3 | 34 = 22\|12 | 12 | ✓ | ✓ | 12 | ✓ | ✓ (all, random) | ✗ for every unit gb | 12 / 12 | 0 | 9516 / 516 / 516 | 0 | 0 |

(Full-complex Jacobi systems: 340, 10108, 98850 equations respectively.)

### 5.4 How the artifacts support the theorem

* The *existence* statements of Theorem 4 are backed by exact rational identities (5.1, items 4–5),
  independently re-derived by rank computations that do not know $f$ (5.2, item 1).
* The *non-existence* statement of Corollary 4.1 (literal reading, normal-ordered or document section) is
  backed by 5.1 item 6 and 5.2 item 2; its section-dependence (literal identity true in the symmetrised
  section) by 5.1 item 7.
* Theorem 5 is backed by 5.2 item 3 ($Z^2_{\bar1}=B^2_{\bar1}$ and empty weight-zero odd complex), and
  the $\mathrm{GF}(p)$ ranks are consistent with $\dim B^2=\dim C^1_{\bar1}-\dim Z^1_{\bar1}$ ($528-12=516$ for $n=3$).
* The hand proofs (Lemma 1, Lemma 2, Prop. 3) are uniform in $n$; the artifacts instantiate every
  step for $n=1,2,3$ as required, and the structure constants/gamma tables allow any third party to
  re-check the claims with their own code.

---

## 6. Summary

For $C(n+1)=\mathfrak{osp}(2|2n)$ the inhomogeneous deformation $\gamma_{\mathrm{gb}}$ is **always trivial**:
$\gamma^{\rm ad}_{\mathrm{gb}}=\delta f_{\mathrm{gb}}$ with the explicit odd map of §2 obtained from the
untwisting $a^\sigma\mapsto a^\sigma+\kappa\,m^\sigma$ of the oscillators. The only part of $\gamma_{\mathrm{gb}}$ that
is not of the form $\delta f$ with $f:\mathfrak{g}\to\mathfrak{g}$ is its scalar (central) component; with the document's
(or the normal-ordered) representatives of the odd generators it is non-zero for every $\mathrm{gb}\neq0$,
but it is annihilated by the adjoint representation, it is itself $\delta c$ for a scalar-valued $c$,
and it disappears altogether when the odd generators are represented by their super-symmetrised
products. This is precisely what the "as an adjoint representation / up to scalar" clause of the
definition accounts for. Independently, $H^2(\mathfrak{g},\mathfrak{g})_{\bar1}=H^2(\mathfrak{g},\mathbb{C})_{\bar1}=0$ because parity on
$C(n+1)$ is the $\mathfrak{so}(2)$-charge mod 2, so no odd deformation of $C(n+1)$ can ever be non-trivial.
