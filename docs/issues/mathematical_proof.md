# Triviality of the Inhomogeneous ($gb$) Deformation of $C(n+1)=\mathfrak{osp}(2|2n)$

**Status**: closed / resolved
**Scope**: `docs/issues/issue_open.md`
**Sources used**: `docs/math/Cn1_definition.md`, `docs/math/C_inhomogeneous_definition.md`,
`docs/math/C_coboundary_definition.md` only. No external literature was consulted
(the provided documents are self-contained), hence no web-access approval was requested.

---

## 0. Statement of the result

> **Theorem (Main).** Let $n\ge 1$, $\mathfrak g = C(n+1)=\mathfrak{osp}(2|2n)$, and let
> $\gamma_{gb}\in C^2(\mathfrak g;\mathfrak g)_{\bar 1}$ be the inhomogeneous deformation
> cocycle determined by the $4n$ parameters $gb_{\sigma,j,s}$
> ($\sigma,s\in\{+,-\}$, $1\le j\le n$) of `C_inhomogeneous_definition.md`.
> Then $\gamma_{gb}$ is **trivial for every** $gb$: there is an explicit odd linear map
> $f_{gb}:\mathfrak g\to\mathfrak g$ with
> $$\gamma_{gb} \;=\; -\,\delta f_{gb}\qquad\text{identically in the } gb .$$
> Equivalently, the triviality condition is **vacuous**: the whole $4n$-dimensional
> family $\{\gamma_{gb}\}$ lies in $B^2(\mathfrak g;\mathfrak g)_{\bar 1}$ and its image in
> $H^2(\mathfrak g;\mathfrak g)_{\bar1}$ is $\{0\}$.

> **Corollary (answer to Requirement 3 of the issue).** *Every* non-zero configuration
> of $gb$ satisfies the triviality condition. There is no non-trivial inhomogeneous
> deformation of $C(n+1)$, even though $\gamma_{gb}\ne 0$ as a cochain whenever $gb\ne0$.

> **Theorem (Rigidity of the trivialiser).** $f_{gb}$ is unique modulo the inner odd
> derivations: the solution set of $\delta f=-\gamma_{gb}$ is an affine space of
> dimension exactly $4n=\dim\mathfrak g_{\bar1}$, a torsor under
> $\{\operatorname{ad}u : u\in\mathfrak g_{\bar 1}\}$.

The companion statement that handles the *"adjoint representation / up to scalar"*
clause is Theorem 5.1 below; it is the only place where a non-vacuous condition on
$gb$ can appear, and §5 shows precisely why it does not survive a consistent choice
of conventions.

---

## 1. Conventions and the ambient algebra

Following `C_inhomogeneous_definition.md`, put
$A=V\oplus\mathbf C K\oplus\mathbf C\kappa$ with
$V_{\bar 0}=\operatorname{span}\{b_j^{\pm}\}_{j=1}^{n}$,
$V_{\bar1}=\operatorname{span}\{a_1^{+},a_1^{-}\}$ (written $a^\pm$ below),
$K$ even central, $\kappa$ **odd** central, and the skew-supersymmetric pre-oscillator
form
$$[v,w]=\begin{cases}(v|w)\,K,& p(v)=p(w),\\ (v|w)\,\kappa,& p(v)\ne p(w).\end{cases}$$

Write $\omega_{ij}=(v_i|v_j)$ on the parity-preserving part and $\mu_{ij}=(v_i|v_j)$ on
the parity-reversing part. Skew-supersymmetry forces $\omega$ to be antisymmetric on
$V_{\bar 0}$, symmetric on $V_{\bar1}$, and $\mu$ to be antisymmetric. Normalising as
in `Cn1_definition.md`,
$$\omega(b_j^-,b_k^+)=\delta_{jk}=-\omega(b_j^+,b_k^-),\qquad
\omega(a^+,a^-)=\omega(a^-,a^+)=1,$$
and the deformation of `C_inhomogeneous_definition.md`,
$[b_j^s,a^\sigma]=-gb_{\sigma,j,s}\kappa$, is
$$\boxed{\;\mu(b_j^s,a^\sigma)=-gb_{\sigma,j,s}=-\mu(a^\sigma,b_j^s).\;}\tag{1.1}$$

Jacobi holds for any such form because $K,\kappa$ are central; so $A$ is a Lie
superalgebra for **all** values of $gb$. We work in $\mathcal U(A)/(K-1)$, the
deformed Weyl–Clifford algebra $\mathcal W_\kappa$, whose defining relations are
$$v_iv_j-(-1)^{p_ip_j}v_jv_i=\omega_{ij}+\mu_{ij}\kappa. \tag{1.2}$$

**Lemma 1.1 ($\kappa^2=0$).** $\kappa$ is odd and central, so $[\kappa,\kappa]=0$;
but for an odd element $[\kappa,\kappa]=2\kappa^2$. Hence $\kappa^2=0$ *exactly*, not
merely to first order. $\square$

Lemma 1.1 is what makes the whole problem finite and exact: every coefficient
occurring below is an **affine-linear** polynomial in the $gb$, and the extension
$L=\mathfrak g\oplus\kappa\mathfrak g$ of `C_inhomogeneous_definition.md` is honestly
abelian. It is also the reason no truncation or "first-order" caveat is needed
anywhere in this report.

> **Remark 1.2 (a parity slip in the source document).** The closing *Parity Note* of
> `C_inhomogeneous_definition.md` asserts that the $gb$ "must have parity 1". This is
> inconsistent with the displayed relation: $b_j^s$ is even and $a^\sigma$ is odd, so
> $[b_j^s,a^\sigma]$ is **odd**, and since $\kappa$ is already odd the coefficient
> $gb_{\sigma,j,s}$ must be **even** (an ordinary scalar) for (1.1) to be
> parity-homogeneous. We therefore take $gb\in\mathbf C$. This choice is harmless for
> the result: $\gamma_{gb}$ is linear in $gb$ and the trivialiser $f_{gb}$ below is
> linear in $gb$ as well, so if one insists on reading the $gb$ as odd elements of an
> auxiliary Grassmann algebra, every identity proved here holds verbatim over that
> ring. The conclusion is unaffected either way.

## 2. The algebra $\mathfrak g$ as super-symmetrised quadratics

For $i\le j$ set
$$Z_{ij}\;=\;v_i\circ v_j\;:=\;\tfrac12\bigl(v_iv_j+(-1)^{p_ip_j}v_jv_i\bigr)\in\mathcal W_\kappa,
\tag{2.1}$$
omitting $i=j$ with $p_i=1$ (indeed $(a^\pm)^2=\tfrac12\omega(a^\pm,a^\pm)=0$).
Counting: $n(2n+1)$ purely bosonic, $1$ purely fermionic ($a^+\circ a^-$), $4n$ mixed,
i.e.
$$\dim = (2n^2+n+1)\,|\,4n,\qquad \text{total } 2n^2+5n+1,$$
which is exactly the superdimension table of `Cn1_definition.md`. So the span of
(2.1) **is** $C(n+1)$, and the oscillator generators listed there
($H_1=a^+a^-+b_1^+b_1^-$, $E_{\varepsilon-\delta_1}=a^+b_1^-$,
$E_{2\delta_n}=\tfrac12 (b_n^+)^2$, …) are recovered as combinations of the $Z_{ij}$ up
to the usual normal-ordering constants.

It is essential that (2.1) is the super-symmetrisation computed **inside the deformed
algebra**; this is the canonical copy of $\mathfrak g$ and, by Theorem 5.1, the *only*
choice for which the framework of `C_inhomogeneous_definition.md` is consistent.
Computationally (`check_basic.py`, `analyze_triviality.py` step [1]):

* the structure constants of $\{Z_a\}$ are **independent of $gb$** — the deformation
  lives entirely in the $\kappa$-part;
* $[Z_a,Z_b]$ has **no** scalar term and **no** $\kappa\cdot$scalar term, so
  $$[Z_a,Z_b]=\sum_c C_{ab}^{\,c}Z_c+\kappa\sum_c \gamma_{ab}^{\,c}Z_c \tag{2.2}$$
  closes on $L=\mathfrak g\oplus\kappa\mathfrak g$ as postulated;
* $[Z_a,\kappa Z_b]=(-1)^{p_a}\kappa\,[Z_a,Z_b]_0$ and $[\kappa\mathfrak g,\kappa\mathfrak g]=0$,
  i.e. $L$ is the abelian extension of $\mathfrak g$ by the **adjoint** module, with
  $\kappa$ acting trivially — precisely the structure asserted in the definition document.

Since the bracket of an associative algebra automatically obeys the graded Jacobi
identity, (2.2) together with the closure statements *proves* that $\gamma$ is a
genuine odd $2$-cocycle, $\;\mathrm d\gamma=0$, with no appeal to any sign convention
for $\mathrm d$. (This is how the cocycle property is verified in the code: by closure
of $L$, not by a hand-chosen formula.)

## 3. The twist: proof of the Main Theorem

**Definition 3.1.** Let $T:V\to V$ be the odd map
$$T(b_j^{s})=0,\qquad
T(a^{\sigma})=\sum_{j=1}^{n}\Bigl(gb_{\sigma,j,-}\;b_j^{+}\;-\;gb_{\sigma,j,+}\;b_j^{-}\Bigr),
\tag{3.1}$$
and set $\tilde v_i:=v_i+\kappa\,T(v_i)$. Note $p(\kappa T v_i)=p(\kappa)+p(Tv_i)=1+(p_i+1)=p_i$,
so $\tilde v_i$ is homogeneous of the same parity as $v_i$.

**Lemma 3.2 (the twist kills the deformation).** For all $i,j$,
$$[\tilde v_i,\tilde v_j]=\omega_{ij}\qquad\text{(the \emph{undeformed} relations).}$$

*Proof.* Using $\kappa$ odd central, $[x,\kappa y]=(-1)^{p(x)}\kappa[x,y]$, and
$\kappa^2=0$ (Lemma 1.1), which annihilates every $\mu$-term multiplied by $\kappa$:

* $[\tilde b,\tilde b']=[b,b']=\omega(b,b')$, since $T(b)=T(b')=0$.
* $[\tilde a^\sigma,\tilde a^\tau]=\{a^\sigma,a^\tau\}
  +(-1)^{1}\kappa[a^\sigma,Ta^\tau]+\dots$ and $[a^\sigma,Ta^\tau]\in\mathbf C\kappa$
  (mixed parity), so those terms carry $\kappa^2=0$. Hence $=\omega(a^\sigma,a^\tau)$.
* The only non-trivial case is mixed. Since $T(b_j^s)=0$,
  $$[\tilde b_j^{s},\tilde a^{\sigma}]
  =\underbrace{[b_j^s,a^\sigma]}_{=\;-gb_{\sigma,j,s}\kappa}
  +(-1)^{p(b)}\kappa\,[b_j^s,T a^\sigma]
  =-gb_{\sigma,j,s}\kappa+\kappa\,\omega\!\left(b_j^s,Ta^\sigma\right).$$
  By (3.1), $\omega(b_j^+,Ta^\sigma)=\omega(b_j^+,b_j^-)\cdot(-gb_{\sigma,j,+})=+gb_{\sigma,j,+}$
  and $\omega(b_j^-,Ta^\sigma)=\omega(b_j^-,b_j^+)\cdot gb_{\sigma,j,-}=+gb_{\sigma,j,-}$.
  Both cases cancel the first term exactly. $\square$

(Verified symbolically for $n=1,2,3$ in `check_basic.py`, final block.)

**Theorem 3.3.** The assignment $v_i\mapsto\tilde v_i$ extends to an injective
homomorphism $\Phi$ of the **undeformed** Weyl–Clifford algebra into $\mathcal W_\kappa$.
Consequently
$$\tilde Z_{ij}:=\Phi(Z_{ij})=\tilde v_i\circ\tilde v_j
= Z_{ij}+\kappa\, f(Z_{ij}),\qquad
\boxed{\,f(v_i\circ v_j)=T(v_i)\circ v_j+(-1)^{p_i}\,v_i\circ T(v_j)\,}
\tag{3.2}$$
with $f:\mathfrak g\to\mathfrak g$ an **odd** linear map, and
$$[\tilde Z_a,\tilde Z_b]=\sum_c C^{\,c}_{ab}\,\tilde Z_c
\qquad\text{(undeformed structure constants).}\tag{3.3}$$

*Proof.* Lemma 3.2 says the $\tilde v_i$ satisfy the defining relations of the
undeformed algebra, giving $\Phi$. Expanding
$\tilde v_i\tilde v_j=v_iv_j+\kappa\bigl(Tv_i\,v_j+(-1)^{p_i}v_i\,Tv_j\bigr)$
(the $\kappa^2$ term vanishes) and super-symmetrising yields (3.2); since
$T$ is odd and $\kappa$ absorbs one parity unit, $f$ is parity-reversing and lands in
the span of quadratics, which is $\mathfrak g$ by §2. (3.3) is $\Phi$ applied to the
undeformed bracket. $\square$

**Corollary 3.4 (Main Theorem).** Substituting $\tilde Z=Z+\kappa f(Z)$ into (3.3) and
using (2.2), $[Z_a,\kappa X]=(-1)^{p_a}\kappa[Z_a,X]_0$, $\kappa^2=0$:
$$\kappa\gamma(X,Y)+(-1)^{p(X)}\kappa[X,fY]-(-1)^{p(X)p(Y)+p(Y)}\kappa[Y,fX]
=\kappa f([X,Y]),$$
that is
$$\gamma(X,Y)=-\Bigl((-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y])\Bigr)
=-(\delta f)(X,Y),$$
with $\delta$ **exactly** the operator of `C_coboundary_definition.md` §2. $\square$

So the triviality condition holds identically, for all $gb$ and all $n$. Note the
construction is uniform in $n$; the computations of §6 confirm it for $n=1,2,3$ as
required by the issue, but the proof above is general.

### 3.5 Explicit trivialiser, $n=1$

With $\mathfrak g=C(2)=\mathfrak{osp}(2|2)$ and the basis
$\{b^+\!\circ b^+, b^+\!\circ b^-, b^-\!\circ b^-, a^+\!\circ a^-\}$ (even),
$\{b^{s}\!\circ a^{\sigma}\}$ (odd), formula (3.2) gives $f=0$ on
$b^{s}\circ b^{t}$ and
$$
\begin{aligned}
f(b^{+}\!\circ a^{\sigma}) &= gb_{\sigma,1,-}\,b^+\!\circ b^+ - gb_{\sigma,1,+}\,b^+\!\circ b^-,\\
f(b^{-}\!\circ a^{\sigma}) &= gb_{\sigma,1,-}\,b^+\!\circ b^- - gb_{\sigma,1,+}\,b^-\!\circ b^-,\\
f(a^{+}\!\circ a^{-}) &= gb_{+,1,-}\,b^+\!\circ a^- - gb_{+,1,+}\,b^-\!\circ a^-
 - gb_{-,1,-}\,b^+\!\circ a^+ + gb_{-,1,+}\,b^-\!\circ a^+ .
\end{aligned}
$$
This is the content of `artifacts/Cn1_structure_n1.json → trivialiser_phi`, and the
analogous tables for $n=2,3$ are in the corresponding files.

That $\gamma_{gb}\neq0$ while being a coboundary is worth recording explicitly; e.g.
for $n=1$,
$$\gamma\bigl(b^+\!\circ b^+,\;b^+\!\circ a^+\bigr)=-2\,gb_{+,1,+}\;\,b^+\!\circ b^+ .$$
The computations confirm that $\gamma_{gb}$ depends non-trivially on **all** $4n$
parameters, so the deformation is genuinely visible — it is simply never a new
algebra.

## 4. Uniqueness of $f$

$\delta f=-\gamma_{gb}$ is an inhomogeneous linear system in the
$2\dim\mathfrak g_{\bar0}\dim\mathfrak g_{\bar1}$ unknowns $\phi_{ij}$. Solving it numerically
with exact rational data and random $gb\ne0$ (`analyze_triviality.py` step [8]):

| $n$ | $\dim\mathfrak g$ | unknowns | equations | $\operatorname{rank}A$ | $\operatorname{rank}[A|b]$ | solvable | $\dim$ solution set |
|---|---|---|---|---|---|---|---|
| 1 | 8  | 32  | 512   | 28  | 28  | yes | 4  |
| 2 | 19 | 176 | 6859  | 168 | 168 | yes | 8  |
| 3 | 34 | 528 | 39304 | 516 | 516 | yes | 12 |

The system is consistent in every case (residuals $\le4\times10^{-15}$), an independent
confirmation of Corollary 3.4. The rank deficiency is $4n=\dim\mathfrak g_{\bar1}$ in
each case, and `check_kernel.py` identifies the kernel exactly: $\delta(\operatorname{ad}u)=0$
for every $u\in\mathfrak g_{\bar1}$ and these $4n$ maps are linearly independent. So

$$\ker\delta|_{C^1_{\bar1}}=\{\operatorname{ad}u: u\in\mathfrak g_{\bar1}\}
\quad\Longleftrightarrow\quad H^1(\mathfrak g;\mathfrak g)_{\bar1}=0,$$

as expected for the simple Lie superalgebra $C(n+1)$: all derivations are inner. The
trivialiser is therefore unique up to an inner odd derivation, and the twist (3.1) —
which carries $8n$ free parameters subject to $4n$ conditions — reproduces exactly
this $4n$-dimensional freedom. The two counts agreeing is a non-trivial consistency
check on the whole construction.

## 5. The "adjoint representation / up to scalar" condition

This is the delicate point of the problem, and it is where a *spurious* non-triviality
can appear. The triviality condition of `C_coboundary_definition.md` §3 reads
"$\gamma(X,Y)=(\delta f)(X,Y)$ **as an adjoint representation** … **up to scalar**".
Two readings must be separated.

### 5.1 Reading A — "up to an overall scalar multiple"

If "up to scalar" means $\gamma=c\,\delta f$ for some $c\in\mathbf C$, the clause is
vacuous whenever $c\neq0$, since $\gamma=c\,\delta f=\delta(cf)$ and $cf$ is again an
odd map $\mathfrak g\to\mathfrak g$. The only substantive case would be $c=0$, i.e.
$\gamma_{gb}=0$, which by §3.5 happens iff $gb=0$. Under Reading A the answer is
therefore the Main Theorem: triviality for all $gb$, with the normalisation $c=-1$
realised by (3.2).

### 5.2 Reading B — "up to a central scalar term", and why it is the operative one

The substantive reading is that equality is required only **modulo $\mathbf C\kappa$**,
i.e. modulo the non-adjoint, scalar-valued part. That this clause is needed at all is a
genuine feature of the oscillator realisation, and it is section-dependent:

**Theorem 5.1.** Let $Z^{0}_{ij}:=v_iv_j-\tfrac12\omega_{ij}$ be the *naive* (undeformed
normal-ordering) section of $\mathfrak g$ in $\mathcal W_\kappa$, as opposed to the
super-symmetrised section (2.1), to which it is related by
$$Z^{0}_{ij}=Z_{ij}+\tfrac12\mu_{ij}\,\kappa .$$
Then the bracket in the $Z^0$-section acquires an extra **scalar** term,
$$[Z^0_a,Z^0_b]=\sum_c C^{\,c}_{ab}Z^0_c+\kappa\sum_c\gamma^{\,c}_{ab}Z^0_c
+\kappa\,\sigma(Z^0_a,Z^0_b),\qquad \sigma(X,Y)=\varphi([X,Y]),$$
where $\varphi:\mathfrak g\to\mathbf C$ is the odd linear functional supported on
$\mathfrak g_{\bar1}$ determined by
$$\boxed{\;\varphi\bigl(b_j^{s}\circ a^{\sigma}\bigr)=\tfrac12\,gb_{\sigma,j,s},
\qquad \varphi|_{\mathfrak g_{\bar0}}=0 .\;}\tag{5.1}$$
In the super-symmetrised section (2.1) one has $\sigma\equiv0$ identically.

*Verification.* `analyze_scalar_obstruction.py` solves $\sigma_{ab}=\sum_c C^{\,c}_{ab}\varphi_c$
exactly over $\mathbf Q$, switching on one $gb$ parameter at a time, for $n=1,2,3$; the
unique solution is (5.1) in all $4n$ cases, and $\sigma\equiv0$ for the SYM section is
confirmed entrywise. $\square$

Three consequences, which together constitute our handling of the clause:

1. **$\varphi$ is rigid.** By (5.1) $\varphi$ is determined by $gb$ alone — it does not
   depend on which trivialiser $f$ one chooses, nor on the $4n$-fold freedom of §4. In
   particular $\varphi=0\iff gb=0$. So the scalar term is not an artefact of a bad
   choice of $f$; it is intrinsic to the *section*.

2. **It is a parity phenomenon, and $\kappa$ is exactly what resolves it.** $\varphi$ is
   an odd $1$-cochain with values in the *trivial* module $\mathbf C$, so
   $(\delta\varphi)(X,Y)=-\varphi([X,Y])=-\sigma(X,Y)$: the anomaly is a coboundary in
   the graded complex. Removing it means re-choosing the section by
   $$Z\;\longmapsto\;Z+\kappa\,\varphi(Z),$$
   which is legitimate precisely because $\kappa$ is **odd**: adding $\kappa\varphi(Z)$
   to an odd $Z$ preserves parity, whereas the parity-preserving shift
   $Z\mapsto Z+\varphi(Z)$ by a bare even scalar would not. Carrying this out is
   literally the passage $Z^0\rightsquigarrow Z$ of Theorem 5.1, since
   $\tfrac12\mu(b_j^s,a^\sigma)=-\tfrac12 gb_{\sigma,j,s}=-\varphi(b_j^s\circ a^\sigma)$.
   This is what "up to scalar" licenses, and it is the *only* available route:
   $\mathbf C\kappa$ is an odd central line, not part of the adjoint module
   $\kappa\mathfrak g$.

3. **The framework itself selects the super-symmetrised section.**
   `C_inhomogeneous_definition.md` postulates $\gamma:\mathfrak g\otimes\mathfrak g\to\mathfrak g$
   and $L=\mathfrak g\oplus\kappa\mathfrak g$ an abelian extension *by the adjoint
   representation*. With the naive section this is false for $gb\neq0$: the bracket
   leaves $\mathfrak g\oplus\kappa\mathfrak g$ and one is forced into
   $\hat L=\mathfrak g\oplus\kappa\mathfrak g\oplus\mathbf C\kappa$, whose module is
   $\mathfrak g\oplus\mathbf C$, **not** the adjoint one. With the super-symmetrised
   section the postulate holds on the nose ($\sigma\equiv0$, verified for $n=1,2,3$).
   Hence the definition document's own hypotheses pin down section (2.1), and in that
   section the "up to scalar" allowance is never exercised: Corollary 3.4 is an exact
   equality of $\mathfrak g$-valued cochains.

**The sharp dichotomy.** For completeness, the one way to obtain a non-vacuous
condition on $gb$ is to insist simultaneously on (i) the naive section $Z^0$ *and*
(ii) a strictly $\mathfrak g$-valued $f$ with the scalar term **not** discarded. Then
$\gamma^{0}_{gb}=\delta f$ forces $\varphi=0$, i.e.
$$\gamma^{0}_{gb}\ \text{trivial}\iff gb_{\sigma,j,s}=0\ \ \forall\,\sigma,j,s,$$
by (5.1) — the all-or-nothing answer. We record this because it is the statement one
would reach by a direct basis computation that overlooks the normal-ordering shift;
but it is an artefact of a section in which the problem's own structural hypothesis
(abelian extension by the adjoint module) fails. Dropping either (i) or (ii) — and
"up to scalar" drops (ii) explicitly — returns the Main Theorem. **The definitive
conclusion is the Main Theorem: $\gamma_{gb}$ is trivial for every $gb$.**

## 6. Computational artifacts

All code is in `scripts/`, all data in `artifacts/`. Coefficients are exact rationals
and affine-linear in the $gb$ symbols throughout (legitimate by Lemma 1.1); no
floating point enters any step of the *proof* (floats appear only in the auxiliary
rank computation of §4).

| file | role |
|---|---|
| `scripts/osp_algebra.py` | deformed Weyl–Clifford algebra $\mathcal W_\kappa$: normal ordering, $\kappa^2=0$, affine-linear $gb$ arithmetic |
| `scripts/osp_deformation.py` | basis (2.1) of $C(n+1)$, decomposition (2.2), the twist (3.1), the operator $\delta$ of `C_coboundary_definition.md` |
| `scripts/check_basic.py` | superdimensions, closure of the undeformed algebra, Lemma 3.2 |
| `scripts/analyze_triviality.py` | Jacobi, $\gamma$ for both sections, closure/adjointness of $L$, Theorem 3.3, Corollary 3.4, rank table of §4 |
| `scripts/analyze_scalar_obstruction.py` | Theorem 5.1 and the functional $\varphi$ of (5.1) |
| `scripts/check_kernel.py` | $\ker\delta=\{\operatorname{ad}u\}_{u\in\mathfrak g_{\bar1}}$ |
| `scripts/export_artifacts.py` | writes the JSON below |
| `scripts/verify_artifacts.py` | **standalone** re-verification from the JSON alone |

Data files `artifacts/Cn1_structure_n{1,2,3}.json` each contain: `basis` (labels and
parities), `structure_constants` $C_{ab}^{\,c}$, `gamma` $\gamma_{ab}^{\,c}$ as
affine-linear forms in the $gb$, `trivialiser_phi` ($\phi_{ij}$, the matrix of $f$),
`twist_T`, and a `conventions` block stating every normalisation used. Linear forms
are encoded as `{"gb[+,1,-]": "1", ...}` with `"1"` reserved for the constant term;
all values are exact rational strings. Additional summaries:
`artifacts/analysis_summary.json`, `artifacts/scalar_obstruction.json`.

To reproduce everything:

```sh
cd scripts && ./run_all.sh          # full derivation + checks
cd scripts && python3 verify_artifacts.py   # independent check from JSON only
```

`verify_artifacts.py` imports nothing from the derivation engine. It re-checks, from
the JSON alone: the graded Jacobi identity for $C$; graded antisymmetry of $C$ and
$\gamma$; that $\gamma$ is linear in $gb$ with no constant term and depends on all
$4n$ parameters; that $f$ is parity-reversing; and that
$\gamma+\delta f=0$ identically in the $gb$. Current status: **ALL ARTIFACT CHECKS
PASSED** for $n=1,2,3$.

## 7. Conclusion

For $\mathfrak g=C(n+1)=\mathfrak{osp}(2|2n)$ the inhomogeneous $gb$-deformation is a
non-zero odd $2$-cocycle for every $gb\ne0$, yet it is always a coboundary:
$$\gamma_{gb}=-\delta f_{gb},\qquad
f_{gb}(v_i\circ v_j)=T(v_i)\circ v_j+(-1)^{p_i}v_i\circ T(v_j),$$
with $T$ given by (3.1). The triviality condition on the parameters is therefore
**empty**: all $4n$-dimensional configurations, zero or not, are trivial, and the
deformation defines no new Lie superalgebra — the twisted generators
$\tilde v=v+\kappa Tv$ exhibit an explicit isomorphism back to the undeformed
$C(n+1)$. The only invariant trace the deformation leaves is the rigid odd scalar
functional $\varphi=\tfrac12 gb$ of (5.1), which is not adjoint-valued and which the
"up to scalar" clause of `C_coboundary_definition.md` exists precisely to discard.

Structurally, the mechanism is that $V_{\bar1}$ for $C(n+1)$ is the *standard* pair
$a^\pm$ with the non-degenerate symmetric form $\omega(a^+,a^-)=1$. Non-degeneracy of
$\omega$ on both $V_{\bar0}$ and $V_{\bar1}$ is exactly what makes the linear system
of Lemma 3.2 solvable — $8n$ parameters in $T$ against $4n$ conditions — so the
mixed-parity part $\mu$ of the pre-oscillator form can always be gauged away. We note
that the same argument applies verbatim to $B(0,n)=\mathfrak{osp}(1|2n)$ as described in
`Cn1_definition.md` §3 ($\dim V_{\bar1}=1$, $a_0^2=\tfrac12$, giving $2n$ conditions on
$4n$ parameters); verifying that case was outside the scope of this issue and has not
been computed here.
