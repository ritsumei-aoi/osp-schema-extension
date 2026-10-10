# Triviality of the Inhomogeneous (gb) Deformations of C(n+1) = osp(2|2n)

**Status**: resolved — definitive conclusion reached and machine-verified.
**Inputs**: `docs/math/Cn1_definition.md`, `docs/math/C_inhomogeneous_definition.md`,
`docs/math/C_coboundary_definition.md`, `docs/issues/issue_open.md`.
**Verification artifacts**: `scripts/verify_triviality.py`,
`artifacts/structure_constants_n{1,2,3}.json`,
`artifacts/gamma_components_n{1,2,3}.json`,
`artifacts/triviality_certificate_n{1,2,3}.json`.

---

## 0. Main result

> **Theorem (triviality condition).**
> Let $\mathfrak g = C(n+1) = \mathfrak{osp}(2|2n)$, $n \ge 1$, realized by the
> oscillators of `Cn1_definition.md`, and let $\gamma_{gb}$ be the inhomogeneous
> deformation 2-cocycle determined by the parameters
> $gb_{\sigma,j,s}$ ($\sigma,s\in\{+,-\}$, $1\le j\le n$) of
> `C_inhomogeneous_definition.md`. Then $\gamma_{gb}$ is **trivial for every
> value of the parameters**: there is an explicit odd linear map
> $f_{gb}:\mathfrak g\to\mathfrak g$ (given in closed form in §4) with
> $$\gamma_{gb} = \delta f_{gb}\qquad\text{(in the adjoint representation, up to scalar).}$$
> The necessary and sufficient condition on $gb$ for triviality is therefore
> **vacuous — it is satisfied by all $gb \in \mathbb{C}^{4n}$** (and, in the
> Grassmann-parameter reading of the definitions, by all odd parameter values;
> see §2.3). Equivalently, the linear map
> $gb \mapsto [\gamma_{gb}] \in H^2(\mathfrak g;\Pi\mathfrak g)$ is identically zero.

In particular there is **no non-zero obstruction configuration**: the answer to
Requirement 3 of the issue ("investigate whether any non-zero configuration of
$gb$ parameters can satisfy the triviality condition") is that **every**
configuration, zero or not, satisfies it. The deformation is nevertheless *not*
removable at the level of the underlying pre-oscillator extension
$A = V\oplus\mathbb{C}K\oplus\mathbb{C}\kappa$ (§6); triviality is a statement
about the quadratic (adjoint) realization of $C(n+1)$, which is exactly the
setting prescribed by the source documents. The conceptual reason for
triviality is a grading argument: the $\mathfrak{so}(2)$ charge gives
$C(n+1)$ a consistent $\mathbb Z$-grading in which every component of
$\gamma_{gb}$ has non-zero degree, and non-zero-degree cocycles are always
coboundaries (Cartan homotopy, §3).

---

## 1. Setup and conventions

### 1.1 Oscillator realization

Per `Cn1_definition.md`, $\mathfrak g$ is spanned, inside the universal
enveloping algebra of the extension
$A=V\oplus\mathbb{C}K\oplus\mathbb{C}\kappa$ (with $K$ realized as $1$), by the
quadratics in one fermionic pair $a^\pm := a_1^\pm$
($\{a^-,a^+\}=1$, $(a^\pm)^2=0$) and $n$ bosonic pairs $b_k^\pm$
($[b_k^-,b_l^+]=\delta_{kl}$). We use the basis

| name | element | parity | $\varepsilon$-degree |
|---|---|---|---|
| $N$ | $a^+a^-$ | even | $0$ |
| $P_{kl}=b_k^+b_l^+\ (k\le l)$, $Q_{kl}=b_k^+b_l^-$, $M_{kl}=b_k^-b_l^-\ (k\le l)$ | $\mathfrak{sp}(2n)$ | even | $0$ |
| $F_{\sigma,j,s}=a^\sigma b_j^s$ | odd root vectors $e_{\sigma\varepsilon+s\delta_j}$ | odd | $\sigma$ |

Dimensions: $(2n^2+n+1\,|\,4n)$, verified by the script for $n=1,2,3$
($(4|4)$, $(11|8)$, $(22|12)$). $N$ spans the $\mathfrak{so}(2)$ factor and its
adjoint action gives the **consistent $\mathbb Z$-grading**
$$\mathfrak g=\mathfrak g_{-1}\oplus\mathfrak g_0\oplus\mathfrak g_{+1},\qquad
\mathfrak g_{\pm1}=\operatorname{span}\{a^{\pm}b_j^s\},\quad
\mathfrak g_0=\mathfrak{sp}(2n)\oplus\mathbb{C}N,$$
i.e. $[N,X]=\deg(X)\,X$ ($C(n+1)$ is a type-I superalgebra; the grading is the
$\varepsilon$-charge).

### 1.2 The inhomogeneous deformation

Per `C_inhomogeneous_definition.md`, the deformation replaces the trivial
boson–fermion exchange relation by
$$[b_j^s,\,a^\sigma]\;=\;-\,gb_{\sigma,j,s}\,\kappa,\qquad
\kappa\ \text{odd, central},\ \kappa^2=0 .$$
All other oscillator relations are unchanged. Substituting the quadratic
generators and re-normal-ordering yields the deformed bracket on $\mathfrak g$,
$$[X,Y]_\gamma=[X,Y]_0+\kappa\,\gamma(X,Y),\qquad
\gamma=\sum_{\alpha}gb_\alpha\,C_\alpha,\quad \alpha=(\sigma,j,s),$$
where each $C_\alpha:\mathfrak g\otimes\mathfrak g\to\mathfrak g$ is an **odd
(parity-reversing)** bilinear map with values in $\mathfrak g$ *modulo scalars*
(see §2). The full list of the non-zero entries of every $C_\alpha$ is exported
in `artifacts/gamma_components_n{1,2,3}.json`; representative closed forms (all
machine-verified) are, writing $\bar\sigma=-\sigma$ and
$\partial_{j}^{s} := \partial/\partial b_j^s$ (formal derivative on the
commuting $b$'s):

* $C_\alpha(N,B)=\sigma\,(\partial_j^s B)\,a^{\bar\sigma}$ for
  $B\in\mathfrak{sp}(2n)$, and $C_\alpha(N,F_\beta)=-\delta_{\alpha\beta}\,a^{\sigma}a^{\bar\sigma}$;
* $C_\alpha(B,F_{\sigma,m,u})=-(\partial_j^s B)\,b_m^u$ (zero unless the
  fermion index of $F$ equals $\sigma$);
* $C_\alpha(F,F')$ = contraction of $a^\sigma$ in one argument with $b_j^s$
  in the other, the two surviving oscillators recombined (e.g. for $n=1$,
  $\alpha=(+,1,+)$: $C(F_{+,1,-},F_{-,1,+})=F_{-,1,-}$);
* $C_\alpha(B,B')=0$ and $C_\alpha(N,N)=0$.

### 1.3 The coboundary operator

Per `C_coboundary_definition.md`, for an odd linear map
$f:\mathfrak g\to\mathfrak g$,
$$(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y]).$$
Using the super-antisymmetry $[Y,f(X)]=-(-1)^{p(Y)(p(X)+1)}[f(X),Y]$ this is
equivalently the **simple form** used throughout the proof:
$$(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]+[f(X),Y]-f([X,Y]).\tag{1}$$
Triviality of $\gamma$ means $\gamma=\delta f$ for some odd $f$, as maps into
the adjoint module, **up to scalar** (§2).

$\delta f$ is precisely the first-order effect of the change of embedding
$X\mapsto X-\kappa f(X)$ inside $\mathcal U(A)$: expanding
$[X-\kappa f(X),\,Y-\kappa f(Y)]$ with $\kappa$ odd central and $\kappa^2=0$
gives $[X,Y]_0+\kappa(\delta f)(X,Y)$ modulo the relabeling of the image basis.
Hence "$\gamma$ trivial" $\iff$ the deformed algebra
$L_\gamma=\mathfrak g\oplus\kappa\mathfrak g$ is isomorphic to the undeformed
abelian extension $L_0$ by an isomorphism of the form $\mathrm{id}+\kappa f$ —
the correct deformation-theoretic notion of equivalence.

---

## 2. Theoretical handling of the "adjoint representation / up to scalar" condition

This is the subtle point of the problem statement and it is handled as follows.

### 2.1 Why a quotient is needed at all

The oscillator realization does **not** produce $C(n+1)$ on the nose: the span
$W$ of the quadratics is closed under the superbracket only *up to additive
multiples of* $1$ (the image of the central element $K$). For example
$\{a^+b^+,\,a^-b^-\}= -N + Q_{11}+\textstyle\frac{\dots}{\dots}$-type
expressions contain the constants produced by $a^-a^+=1-a^+a^-$ and
$b^-b^+=b^+b^-+1$. Thus $W\oplus\mathbb{C}1$ is a one-dimensional **central
extension** of $\mathfrak{osp}(2|2n)$, and
$$\mathfrak g \;=\; (W\oplus\mathbb{C}1)\,/\,\mathbb{C}1 \;\cong\; C(n+1).$$
"Realized … by adjoint representation" in `C_inhomogeneous_definition.md`
means exactly that one works in this quotient: in the adjoint action the
central elements $1$ (and $\kappa$, $\kappa\cdot 1$) act trivially, so the
quotient is canonical. Concretely this is also why the standard Cartan
generator is listed as $H_{n+1}=-b_n^+b_n^--\tfrac12$ in
`Cn1_definition.md`: scalar shifts of basis elements are invisible in
$\mathfrak g$.

Accordingly:

* the structure constants $c_{ij}{}^{k}$ are read off from the quadratic part
  of the brackets, and the scalar parts are stored **separately** as the
  extension 2-cocycle $s_{ij}$ (artifact field `central_scalar`);
* $\gamma$ and $\delta f$ are compared as maps
  $\mathfrak g\otimes\mathfrak g\to\mathfrak g$, i.e. after projecting out
  $\mathbb{C}1$ — this is the precise meaning we assign to
  "$\gamma(X,Y)=(\delta f)(X,Y)$ … as an adjoint representation … up to
  scalar";
* the module of the cohomology theory is $\kappa\mathfrak g\cong\Pi\mathfrak g$
  (the parity-reversed adjoint module), exactly the abelian extension
  $L=\mathfrak g\oplus\kappa\mathfrak g$ described in
  `C_inhomogeneous_definition.md`, in which $\kappa$ acts trivially.

This quotient is not a loss of information for the deformation problem: every
identity we use (the Jacobi identity of the deformed bracket, the derivation
identity (2) below) holds in $\mathcal U(A_{\rm def})$ on the nose and
*descends* to the quotient because the discarded terms are central — a central
summand inside an argument of a further bracket contributes $0$, and
$\gamma(X,\,c\!\cdot\!1)=0$ since the deformation does not alter brackets with
scalars.

### 2.2 The alternative "projective" reading

If "up to scalar" is instead read projectively — $\gamma = \lambda\,\delta f$
for some $\lambda\in\mathbb{C}^\times$ — nothing changes: $\delta$ is linear,
so $\gamma=\lambda\,\delta f \iff \gamma=\delta(\lambda f)$. Both readings
yield the same triviality locus. Our result is stated with $\lambda=1$ (exact
equality mod $\mathbb{C}1$), which implies the projective statement.

### 2.3 Parity of the parameters (the "Parity Note")

`C_inhomogeneous_definition.md` asserts $p(gb)=1$. Parity bookkeeping of the
defining relation forces the opposite:
$p([b_j^s,a^\sigma])=1$ while $p(gb\,\kappa)=p(gb)+1$, so homogeneity requires
$p(gb)=0$; likewise homogeneity of $[X,Y]_\gamma$ requires
$p(\gamma(X,Y))=p(X)+p(Y)+1$, which holds with even $gb$ (each $C_\alpha$ is
parity-reversing) and would fail with odd $gb$. We therefore work with
$gb\in\mathbb{C}^{4n}$ (even scalars), which is the internally consistent
reading, and treat $\widehat g_\alpha:=gb_\alpha\kappa$ as an *odd, central,
nilpotent* tag ($\widehat g_\alpha\widehat g_\beta=0$ because $\kappa^2=0$).
If one insists on Grassmann-odd $gb$ (reading the Parity Note literally, over
a Grassmann envelope $\Lambda$), the products $gb_\alpha\kappa$ become even
nilpotent central parameters and the *identical* $\mathbb C$-linear systems
$C_\alpha=\delta f_\alpha$ govern triviality, with
$f_{gb}=\sum_\alpha gb_\alpha f_\alpha$ now an odd map over $\Lambda$. **The
conclusion — triviality for all parameter values — is independent of this
convention choice**, precisely because the deformation and the coboundary
equation are linear in $gb$ and the certificates $f_\alpha$ are
parameter-independent.

### 2.4 Beyond "up to scalar": the central parts are also exact

As a strengthening (computed, not required by the problem): the scalar parts of
$\gamma$ (e.g. $\gamma$-entries like
$C_{(+,1,+)}(Q_{11},F_{+,1,+})=-Q_{11}-1$) can **also** be matched. Allowing
$f$ a scalar component on odd elements (permitted by parity: $f$(odd) is even
and may contain $1$), the full system
$\gamma=\delta f$ *including scalars* — where $\delta f$ now also receives the
extension cocycle $s_{ij}$ through $[X,f(Y)]$ — is solvable for every
$\alpha$ (verified by exact Gaussian elimination for $n=1,2$; artifact field
`central_extension_check`). So the deformation of the centrally extended
algebra $W\oplus\mathbb{C}1$ is trivial as well; the "up to scalar" clause is a
safe normalization, not the hiding place of an obstruction.

---

## 3. Proof of the Theorem

The proof has three steps; every step is also verified independently by the
computational artifacts (§5).

### Lemma 1 (grading of the cocycle)

*Each component $C_\alpha$, $\alpha=(\sigma,j,s)$, is homogeneous of
$\varepsilon$-degree $-\sigma$ with respect to the grading of §1.1:*
$$C_\alpha(\mathfrak g_p,\mathfrak g_q)\subseteq\mathfrak g_{\,p+q-\sigma}.$$

**Proof.** The undeformed bracket preserves the $\varepsilon$-charge
(it is $\operatorname{ad}N$-equivariant). Every first-order correction term
arises from one application of the deformed exchange rule, which deletes one
factor $a^\sigma$ (charge $\sigma$) and one factor $b_j^s$ (charge $0$) from a
normal-ordering computation and inserts the chargeless tag
$gb_\alpha\kappa$. Hence each monomial of $C_\alpha(X,Y)$ carries charge
$\deg X+\deg Y-\sigma$. $\square$

(Machine check (V3): asserted entry-by-entry for all $\alpha$, $n=1,2,3$.)

### Lemma 2 (Cartan homotopy for the grading element)

*Let $C$ be the first-order cocycle of the deformation (any $C_\alpha$, or any
$gb$-combination), homogeneous of degree $d$. Then for all homogeneous
$Y,Z\in\mathfrak g$:*
$$d\cdot C(Y,Z)\;=\;(-1)^{p(Y)}[Y,\,u(Z)]+[u(Y),\,Z]-u([Y,Z])\;=\;(\delta u)(Y,Z),
\qquad u:=C(N,\cdot).\tag{2}$$

**Proof.** Work in $\mathcal U(A_{\rm def})$, where all brackets are honest
superbrackets of associative elements, so for the *even* element $N$ the
derivation identity holds identically:
$$[N,[Y,Z]_*]_* \;=\; [[N,Y]_*,Z]_* \;+\; [Y,[N,Z]_*]_* .$$
Expand each deformed bracket as $[\cdot,\cdot]_*=[\cdot,\cdot]_0+\kappa
C(\cdot,\cdot)$ and keep the terms linear in $\kappa$ (the $\kappa^2$ terms
vanish identically). Using centrality of $\kappa$: $[N,\kappa W]=\kappa[N,W]$,
$[\kappa W,Z]=\kappa[W,Z]$, and $[Y,\kappa W]=(-1)^{p(Y)}\kappa[Y,W]$. The
zeroth-order terms cancel by the undeformed Jacobi identity, leaving
$$C(N,[Y,Z])+[N,C(Y,Z)]
=C([N,Y],Z)+[C(N,Y),Z]+C(Y,[N,Z])+(-1)^{p(Y)}[Y,C(N,Z)].$$
Now take $Y\in\mathfrak g_p$, $Z\in\mathfrak g_q$ homogeneous and use
$[N,Y]=pY$, $[N,Z]=qZ$, and $[N,C(Y,Z)]=(p+q+d)\,C(Y,Z)$ (Lemma 1). The terms
$p\,C(Y,Z)+q\,C(Y,Z)$ cancel and the identity collapses to (2); the right-hand
side is exactly the simple form (1) of the document's coboundary operator
applied to the odd map $u=C(N,\cdot)$. All discarded terms along the way were
central, so (2) holds in $\mathfrak g$ = quadratics mod $\mathbb{C}1$, which is
the required "up to scalar" sense. $\square$

### Conclusion of the proof

By Lemma 1, each $C_\alpha$ has degree $d_\alpha=-\sigma\in\{\pm1\}$, in
particular $d_\alpha\neq0$. By Lemma 2,
$$C_\alpha=\delta f_\alpha,\qquad
f_\alpha:=\frac{1}{d_\alpha}\,C_\alpha(N,\cdot)
       =-\frac{1}{\sigma}\,C_\alpha(N,\cdot),$$
an odd (parity-reversing) linear map since $C_\alpha$ is parity-reversing and
$N$ is even. By linearity of $\delta$,
$$\gamma_{gb}=\sum_\alpha gb_\alpha C_\alpha
=\delta\Big(\underbrace{\textstyle\sum_\alpha gb_\alpha f_\alpha}_{=:f_{gb}}\Big)
\qquad\text{for every } gb .$$
$\blacksquare$

**Remark (why no condition on $gb$ can appear).** The triviality locus is the
kernel of the linear map $gb\mapsto[\gamma_{gb}]\in H^2$. The grading argument
shows each class $[C_\alpha]$ vanishes individually, so the kernel is
everything. A non-trivial condition could only have arisen from a degree-$0$
component of $\gamma$; the inhomogeneous deformation of $C(n+1)$ has none,
because its odd roots $\pm\varepsilon\pm\delta_k$ all carry $\varepsilon$-charge
$\pm1$. (This is a genuine structural feature of $C(n+1)$ as opposed to
$B(0,n)=\mathfrak{osp}(1|2n)$, whose odd roots $\pm\delta_k$ are chargeless —
there, no analogous grading element is available and the same mechanism does
not apply.)

---

## 4. The explicit trivializing map $f_{gb}$ (closed form)

For $\alpha=(\sigma,j,s)$, with $\bar\sigma=-\sigma$ and
$\partial_j^s=\partial/\partial b_j^s$:

$$\boxed{\;
f_\alpha(N)=0,\qquad
f_\alpha(B)=-\,(\partial_j^s B)\,a^{\bar\sigma}\ \ (B\in\mathfrak{sp}(2n)),\qquad
f_\alpha(F_\beta)=\delta_{\alpha\beta}\,\sigma\,N \ (\text{mod }\mathbb C 1),
\;}$$

and $f_{gb}=\sum_{\sigma,j,s} gb_{\sigma,j,s}\,f_{(\sigma,j,s)}$ satisfies
$\gamma_{gb}=\delta f_{gb}$. For example, for $n=1$ and $\alpha=(+,1,+)$:
$$f(b^+b^+)=-2\,a^-b^+,\quad f(b^+b^-)=-\,a^-b^-,\quad f(a^+b^+)=N,\quad
f(\text{all other basis elements})=0 .$$
The map is **not inner**: $f_\alpha\neq\operatorname{ad}T$ for any odd
$T\in\mathfrak g$, since $f_\alpha(N)=0$ while $[T,N]=\mp T\neq0$ for odd
homogeneous $T$. (Solutions of $\delta f=C_\alpha$ form an affine space of
dimension $\dim\ker\delta^1_{\rm odd}=4n$, computed in (V5); the one above is
the canonical homotopy representative.)

At the exact (not only mod-scalar) level, the strengthened certificate of §2.4
replaces $f_\alpha(F_\alpha)=\sigma N$ by $f_\alpha(F_\alpha)=a^\sigma
a^{\bar\sigma}$ plus a solvable scalar adjustment on the odd basis.

---

## 5. Computational verification (Requirements 1–3 of the issue)

All computations are performed by `scripts/verify_triviality.py`
(pure Python 3, exact rational arithmetic, no external dependencies or
network/files outside the repository). The engine normal-orders the deformed
oscillator algebra with the odd central nilpotent tag
$\widehat g_\alpha=gb_\alpha\kappa$ (sign conventions documented in the file
header), extracts structure constants, the central extension cocycle, and the
$\gamma$-components $C_\alpha$, and then performs for **$n=1,2,3$**:

| check | content | result |
|---|---|---|
| V1 | super-Jacobi identity of the undeformed structure constants (all $\dim^3$ triples: 512 / 6 859 / 39 304) | pass |
| V2 | super-Jacobi of the deformed bracket to first order in $\widehat g$ (all triples, all $\alpha$) — i.e. **each $C_\alpha$ is a genuine 2-cocycle** | pass |
| V3 | $\operatorname{ad}N$-homogeneity: every entry of $C_\alpha$ has degree $-\sigma(\alpha)$ (Lemma 1) | pass |
| V4 | **Main**: homotopy construction $f_\alpha=\tfrac1{r_\alpha}C_\alpha(N,\cdot)$ with $\delta f_\alpha = C_\alpha$ verified exactly on *every* ordered pair of basis elements; measured ratio $r_\alpha=-\sigma(\alpha)$ for all $4n$ parameters (Lemma 2) | pass |
| V5 | independent from-scratch Gaussian-elimination solve of the linear system $\delta f=C_\alpha$ over $\mathbb Q$ ($n=1,2$); solvable for every $\alpha$, solution space of dimension $4n$ | pass |
| V6 | central-extension refinement of §2.4: $\gamma=\delta f$ solvable **including** scalar parts ($n=1,2$) | pass |
| V7 | the closed-form $f$ of §4 satisfies $\delta f_\alpha=C_\alpha$ exactly and coincides with the homotopy solution | pass |

Total runtime ≈ 5 s; the script exits with
`ALL VERIFICATIONS PASSED`.

### Structured data (Requirement 2: connectivity)

For each $n\in\{1,2,3\}$ the following JSON artifacts are committed (exact
rationals as strings; basis, parities, degrees and all conventions embedded in
each file's metadata so they are independently re-usable):

* `artifacts/structure_constants_n{n}.json` — full structure constants
  $c_{ij}{}^k$ of $C(n+1)$ in the oscillator basis **and** the central
  extension cocycle $s_{ij}$ (field `central_scalar`);
* `artifacts/gamma_components_n{n}.json` — every non-zero entry of every
  $C_\alpha$ (so $\gamma_{gb}=\sum_\alpha gb_\alpha C_\alpha$ is fully
  reconstructible), with scalar parts;
* `artifacts/triviality_certificate_n{n}.json` — the theorem statement, the
  homotopy ratios $r_\alpha$, the explicit maps $f_\alpha$, and (for
  $n=1,2$) the central-extension solvability record.

A human researcher can re-derive and re-check everything with
`python3 scripts/verify_triviality.py`.

---

## 6. Scope, caveats, and honest limitations

1. **Level of the statement.** Triviality is proven for the deformation of the
   Lie superalgebra $C(n+1)$ in its adjoint (mod-center) realization — the
   setting fixed by the source documents — and even for its one-dimensional
   central extension (§2.4). It does **not** say the deformed *oscillator
   extension* $A_{\rm def}$ is isomorphic to $A$: the mixed-parity block
   $(V_{\bar0}|V_{\bar1})\ni(b_j^s|a^\sigma)=-gb_{\sigma,j,s}$ of the
   pre-oscillator form cannot be removed by any parity-preserving linear map of
   $V$ (the form decomposes into parity blocks that transform separately), and
   central shifts do nothing since $\kappa$ is central. The inhomogeneous
   structure is genuinely new at level $A$; it becomes invisible exactly when
   one passes to the quadratics in the adjoint representation. This is the
   mathematically precise content of the "up to scalar / adjoint
   representation" clause.
2. **Order of deformation.** $\kappa^2=0$ makes the deformation exactly
   first-order (no higher $gb$-order terms exist), so "first-order trivial"
   here is *bona fide* trivial: $\mathrm{id}-\kappa f_{gb}$ is an actual
   isomorphism $L_0\to L_{\gamma_{gb}}$, not merely an infinitesimal one.
3. **General $n$.** The proof in §3 (Lemmas 1–2) is uniform in $n$; the
   machine verification instantiates it exhaustively for $n=1,2,3$ as required
   by the issue. Nothing in the argument degenerates for larger $n$.
4. **Convention discrepancy found in the sources.** The "Parity Note" of
   `C_inhomogeneous_definition.md` ($p(gb)=1$) conflicts with parity
   homogeneity of its own defining relation; §2.3 records the consistent
   convention used and shows the conclusion is convention-independent. During
   verification the engine also confirmed empirically that only the
   "$\kappa$ odd-central / $gb$ even" bookkeeping satisfies the first-order
   Jacobi identity, which is an internal consistency check of this resolution.
5. **No external sources.** All computations and proofs were produced within
   this repository from the three definition documents; no external papers,
   files, or web resources were accessed.

---

## 7. Conclusion

**The triviality condition for the inhomogeneous deformation of
$C(n+1)=\mathfrak{osp}(2|2n)$ is vacuous: $\gamma_{gb}$ is a coboundary,
$\gamma_{gb}=\delta f_{gb}$, for every value of the $4n$ parameters
$gb_{\sigma,j,s}$,** with the explicit, machine-verified trivializing odd map
$$f_{gb}(N)=0,\qquad
f_{gb}(B)=-\sum_{\sigma,j,s}gb_{\sigma,j,s}\,(\partial_j^s B)\,a^{-\sigma},\qquad
f_{gb}(a^\sigma b_j^s)=\sigma\,gb_{\sigma,j,s}\,N .$$
The root cause is structural: all odd roots of $C(n+1)$ carry non-zero
$\mathfrak{so}(2)$-charge, so the inhomogeneous cocycle has no charge-zero
component and the Cartan homotopy along the grading element $N$ trivializes it
identically.
