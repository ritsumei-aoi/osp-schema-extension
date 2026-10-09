# Triviality of the Inhomogeneous Deformation of C(n+1) = osp(2|2n)

**Issue**: `docs/issues/issue_open.md`
**Author**: Claude Fable 5.1 (independent-researcher session, condition C)
**Date**: 2026-10-09
**Artifacts**: `scripts/osc_algebra.py`, `scripts/verify_triviality.py`, `scripts/recheck_artifacts.py`,
`artifacts/cn1_n{1,2,3}.json`, `artifacts/summary.json`

---

## 0. Result in one paragraph

Let $\mathfrak g = C(n+1)$ be realised by super-symmetrised quadratics in the oscillators
$a^\pm, b_j^\pm$, and let $\gamma_{gb}$ be the $\kappa$-coefficient of the bracket computed with the
deformed relations $[b_j^s, a^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$. Then for **every** $n\ge 1$ and
**every** choice of the $4n$ parameters $\mathrm{gb}_{\sigma,j,s}\in\mathbf C$,

$$
\boxed{\;\gamma_{gb}(X,Y) \;=\; (\delta f_{gb})(X,Y) \;+\; \lambda_{gb}\big([X,Y]_0\big)\cdot 1
\qquad (X,Y\in\mathfrak g)\;}
$$

with an explicit odd linear map $f_{gb}:\mathfrak g\to\mathfrak g$ (Theorem 1) and an explicit odd linear
functional $\lambda_{gb}:\mathfrak g\to\mathbf C$, $\lambda_{gb}(a^\sigma b_j^s) = -\tfrac12\mathrm{gb}_{\sigma,j,s}$,
$\lambda_{gb}|_{\mathfrak g_{\bar 0}} = 0$. Consequently:

* **In the adjoint representation / up to scalar** (the triviality condition as stated in
  `C_coboundary_definition.md`), $\gamma_{gb} = \delta f_{gb}$, so **the inhomogeneous deformation is
  trivial for all gb**. The necessary and sufficient condition on gb is vacuous.
  The cobounding map is unique up to inner odd derivations $\mathrm{ad}_Z$, $Z\in\mathfrak g_{\bar 1}$.
* The scalar residual $\lambda_{gb}\circ[\cdot,\cdot]_0$ vanishes **iff gb = 0**. Hence if the
  "up to scalar" clause were dropped while still forcing $f$ to take values in $\mathfrak g$, no non-zero
  gb would be trivial. The clause is therefore exactly what is needed, and it is the mathematically
  correct normalisation (Section 5).

The theorem is proved for general $n$ by a one-line change of oscillator variables (Section 3) and is
verified exactly (rational arithmetic) for $n=1,2,3$ (Section 7).

---

## 1. Setting and conventions

### 1.1 The deformed oscillator algebra

$V = V_{\bar 0}\oplus V_{\bar 1}$ with $V_{\bar 1} = \langle a^+, a^-\rangle$, $V_{\bar 0} = \langle b_j^\pm\rangle_{j=1..n}$,
$A_{gb} = V\oplus\mathbf C K\oplus\mathbf C\kappa$, $K$ even central, $\kappa$ odd central. We work in
$\mathcal U := \mathcal U(A_{gb})/(K-1)$. The relations are

$$
\{a^-,a^+\} = 1,\quad (a^\pm)^2 = 0,\qquad [b_j^-, b_k^+] = \delta_{jk},\qquad
[b_j^s, a^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa,\qquad \kappa^2 = 0,\ \kappa\ \text{central}.
$$

$\kappa^2 = \tfrac12[\kappa,\kappa] = 0$ because $\kappa$ is odd and central. The $\mathrm{gb}_{\sigma,j,s}$ are
complex scalars. (The "parity 1" remark in `C_inhomogeneous_definition.md` is read as the statement that
the deformation direction $\kappa\gamma$ is odd, i.e. $\gamma$ is a parity-reversing cochain; if the gb
themselves were Grassmann-odd the relation $[b,a] = -\mathrm{gb}\,\kappa$ would equate an odd element with an
even one. Everything below is linear in gb, so it holds verbatim over any commutative coefficient ring.)

### 1.2 The algebra $\mathfrak g = C(n+1)$ and $\hat{\mathfrak g}$

$\mathfrak g$ is the span of the super-symmetrised quadratics (the standard realisation of $\mathfrak{osp}(2|2n)$
inside the Weyl–Clifford algebra). The basis used in all artifacts is

| type | element | oscillator form | weight |
|---|---|---|---|
| $\mathfrak{so}(2)$ | $N$ | $a^+a^- - \tfrac12$ | $0$ |
| Cartan of $\mathfrak{sp}(2n)$ | $Hs_j$ | $b_j^+b_j^- + \tfrac12 = \tfrac12(b_j^+b_j^- + b_j^-b_j^+)$ | $0$ |
| $\mathfrak{sp}(2n)$ roots | $E_{s\delta_j + t\delta_k}$ | $b_j^s b_k^t$ (incl. $(b_j^s)^2 = E_{2s\delta_j}$) | $s\delta_j+t\delta_k$ |
| odd roots | $E_{\sigma\varepsilon + s\delta_j}$ | $a^\sigma b_j^s$ | $\sigma\varepsilon + s\delta_j$ |

($\dim = 2n^2+n+1 \,|\, 4n$; the document's Cartan elements are $H_1 = N + Hs_1$, $H_k = Hs_{k-1}-Hs_k$,
$H_{n+1} = -Hs_n$; the factor $\tfrac12$ in $E_{\pm2\delta_n}$ of the document is a harmless rescaling.)
With this (symmetrised) basis the undeformed bracket closes on $\mathfrak g$ with **no scalar terms**;
the super-Jacobi identity and the weights under $\mathrm{ad}N$, $\mathrm{ad}Hs_j$ are verified in the artifacts.

Let $\hat{\mathfrak g} := \mathfrak g\oplus\mathbf C\cdot 1\subset\mathcal U$. Since $1$ is central,
$\hat{\mathfrak g}\cong\mathfrak g\oplus\mathbf C$ as $\mathfrak g$-modules.

### 1.3 The deformation cochain $\gamma_{gb}$ and the coboundary

For $X,Y\in\mathfrak g$ the bracket in $\mathcal U$ has the form
$$[X,Y]_{gb} = [X,Y]_0 + \kappa\,\gamma_{gb}(X,Y),\qquad \gamma_{gb}(X,Y)\in\hat{\mathfrak g},$$
$\gamma_{gb}$ is linear in gb, and $p(\gamma(X,Y)) = p(X)+p(Y)+1$ (an *odd* 2-cochain).
**Important**: $\gamma_{gb}$ takes values in $\hat{\mathfrak g}$, not in $\mathfrak g$: e.g. for $n=1$
$$[\,a^+b_1^+,\,(b_1^-)^2\,]_{gb} = -2\,a^+b_1^- + 2\,\mathrm{gb}_{+,1,-}\,\kappa\,(b_1^+b_1^- + 1)
= -2E_{\varepsilon-\delta_1} + \kappa\,\mathrm{gb}_{+,1,-}\,(2\,Hs_1 + 1).$$
This is why the definition document speaks of equality "as an adjoint representation … up to scalar".

The coboundary of an odd linear map $f$ is (as in `C_coboundary_definition.md`)
$$(\delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y]).$$
Standard check (used below): the map $\Phi(X) = X + \kappa f(X)$ is a homomorphism
$(\mathfrak g\oplus\kappa\mathfrak g, [\,,]_\gamma)\to(\mathfrak g\oplus\kappa\mathfrak g,[\,,]_0)$ iff $\gamma = \delta f$,
and $\delta f = 0$ iff $f$ is an odd derivation. The deformed bracket satisfies Jacobi (it is a bracket in
an associative superalgebra), hence $\gamma_{gb}$ is a 2-cocycle; this is also verified numerically.

---

## 2. The key lemma: the oscillator deformation is a change of variables

**Lemma 1.** In $\mathcal U$ define the *shifted bosons*
$$\tilde b_j^s := b_j^s + \kappa\, c_j^s,\qquad c_j^s := \mathrm{gb}_{-,j,s}\,a^+ + \mathrm{gb}_{+,j,s}\,a^- \in V_{\bar 1}.$$
Then $\tilde b_j^s$ is even and $\{\tilde b_j^\pm\}\cup\{a^\pm\}$ satisfy the **undeformed** relations:
$$[\tilde b_j^s, a^\sigma] = 0,\qquad [\tilde b_j^-,\tilde b_k^+] = \delta_{jk},\qquad [\tilde b_j^s,\tilde b_k^s]=0 .$$

*Proof.* $[\tilde b_j^s, a^\sigma] = -\mathrm{gb}_{\sigma,j,s}\kappa + \kappa\{c_j^s, a^\sigma\}$, and
$\{c_j^s,a^+\} = \mathrm{gb}_{+,j,s}\{a^-,a^+\} = \mathrm{gb}_{+,j,s}$, $\{c_j^s,a^-\} = \mathrm{gb}_{-,j,s}$, so the
two terms cancel. $[\tilde b_j^s,\tilde b_k^t] = [b_j^s,b_k^t] + \kappa[c_j^s,b_k^t] + \kappa[b_j^s,c_k^t] + \kappa^2(\dots)$;
the middle brackets are multiples of $\kappa$ by the deformed relation, so they are killed by $\kappa^2=0$. $\square$

Hence $\iota: b_j^s\mapsto\tilde b_j^s,\ a^\sigma\mapsto a^\sigma$ extends to an algebra homomorphism
$\iota:\mathcal U(A_0)/(K-1)\to\mathcal U$ from the undeformed algebra. (This is checked symbolically in
`scripts/test_engine.py`.)

---

## 3. Derivation of $\gamma_{gb}$ as a coboundary

For $X\in\hat{\mathfrak g}$ write $\tilde X := \iota(X)$ (the same quadratic expression in $\tilde b, a$).
Expanding $\tilde b = b + \kappa c$ and using $\kappa^2=0$, $\kappa$ central and $b\,c = c\,b + O(\kappa)$:

$$\tilde X = X + \kappa\,D(X),\qquad
\begin{aligned}
D(N) &= 0,\\
D\big(\mathrm{sym}(b_j^s b_k^t)\big) &= c_k^t\, b_j^s + c_j^s\, b_k^t,\\
D(a^\sigma b_j^s) &= -\,a^\sigma c_j^s
\end{aligned}$$
(the sign in the last line comes from moving $\kappa$ past the odd $a^\sigma$). Since $\iota$ is a homomorphism,
$[\tilde X,\tilde Y]_{gb} = \widetilde{[X,Y]_0} = [X,Y]_0 + \kappa D([X,Y]_0)$. Expanding the left side,
$$[X,Y]_{gb} = [X,Y]_0 + \kappa\Big(D([X,Y]_0) - [D(X),Y]_0 - (-1)^{p(X)}[X,D(Y)]_0\Big),$$
i.e. (using $[D(X),Y] = -(-1)^{(p(X)+1)p(Y)}[Y,D(X)]$)
$$\gamma_{gb} = -\,\delta D .\tag{3.1}$$
$D$ is a well-defined odd linear map $\hat{\mathfrak g}\to\hat{\mathfrak g}$ (it is **not** a derivation of
$\hat{\mathfrak g}$, precisely because $\gamma\neq0$), and (3.1) already shows that $\gamma_{gb}$ is a
coboundary in the complex $C^\bullet(\hat{\mathfrak g},\Pi\hat{\mathfrak g})$.

Now split $D = D_{\mathfrak g} + D_c$ according to $\hat{\mathfrak g} = \mathfrak g\oplus\mathbf C1$. Using
$a^+a^- = N + \tfrac12$ and $a^-a^+ = \tfrac12 - N$:
$$D(a^+b_j^s) = -\mathrm{gb}_{+,j,s}\,(N+\tfrac12),\qquad D(a^-b_j^s) = \mathrm{gb}_{-,j,s}\,(N-\tfrac12),$$
so $D_c(a^\sigma b_j^s) = -\tfrac12\mathrm{gb}_{\sigma,j,s}$ and $D_c = 0$ on $\mathfrak g_{\bar0}$. Because $1$ is
central, $(\delta D_c)(X,Y) = -D_c([X,Y]_0)$. Substituting in (3.1):

**Theorem 1 (explicit cobounding map).** For all $n\ge1$, all gb, and all $X,Y\in\mathfrak g$,
$$\gamma_{gb}(X,Y) = (\delta f_{gb})(X,Y) + \lambda_{gb}([X,Y]_0)\cdot 1,$$
where $f_{gb} := -D_{\mathfrak g}:\mathfrak g\to\mathfrak g$ and $\lambda_{gb} := D_c:\mathfrak g\to\mathbf C$ are the odd maps
$$
\begin{aligned}
f_{gb}(N) &= 0,\\
f_{gb}\big(E_{s\delta_j+t\delta_k}\big) &= -\big(\mathrm{gb}_{-,k,t}\,E_{\varepsilon+s\delta_j} + \mathrm{gb}_{+,k,t}\,E_{-\varepsilon+s\delta_j}
 + \mathrm{gb}_{-,j,s}\,E_{\varepsilon+t\delta_k} + \mathrm{gb}_{+,j,s}\,E_{-\varepsilon+t\delta_k}\big)
 \quad(\text{incl. } Hs_j,\ (b_j^s)^2),\\
f_{gb}\big(E_{\varepsilon+s\delta_j}\big) &= +\,\mathrm{gb}_{+,j,s}\,N,\qquad
f_{gb}\big(E_{-\varepsilon+s\delta_j}\big) = -\,\mathrm{gb}_{-,j,s}\,N,\\
\lambda_{gb}\big(E_{\sigma\varepsilon+s\delta_j}\big) &= -\tfrac12\,\mathrm{gb}_{\sigma,j,s},\qquad \lambda_{gb}|_{\mathfrak g_{\bar0}} = 0 .
\end{aligned}
$$
Equivalently, $\gamma_{gb} = \delta\hat f_{gb}$ **exactly in $\mathcal U$** with $\hat f_{gb} := f_{gb} - \lambda_{gb} = -D:\mathfrak g\to\hat{\mathfrak g}$,
and $X\mapsto X + \kappa\hat f_{gb}(X) = X - \kappa D(X)$ is an explicit isomorphism from the deformed
bracket to the undeformed one. $\square$

**Worked example ($n=1$, only $g := \mathrm{gb}_{+,1,-}\neq0$).** Then $c_1^- = g\,a^-$ and
$f(Hs_1) = -g\,E_{-\varepsilon+\delta_1}$, $f(E_{-2\delta_1}) = -2g\,E_{-\varepsilon-\delta_1}$, $f(E_{\varepsilon-\delta_1}) = g\,N$, all other
basis elements $\mapsto0$. For $X = E_{\varepsilon+\delta_1} = a^+b_1^+$, $Y = E_{-2\delta_1} = (b_1^-)^2$:
$\delta f(X,Y) = -[X,f(Y)] - [Y,f(X)] - f([X,Y]_0) = 2g\{a^+b_1^+,a^-b_1^-\} + 2gN = 2g(Hs_1 - N) + 2gN = 2g\,Hs_1$,
and $\gamma(X,Y) = g(2Hs_1 + 1)$ (Section 1.3). The difference $g\cdot1 = \lambda(-2E_{\varepsilon-\delta_1})\cdot 1$. ✔

---

## 4. Uniqueness of $f$ and the cohomological picture

$\delta f = \delta f'$ iff $f - f'$ is an odd derivation of $\mathfrak g$. For every odd $Z\in\mathfrak g$,
$\delta(\mathrm{ad}_Z) = 0$ by the Jacobi identity, and $Z\mapsto\mathrm{ad}_Z$ is injective ($\mathfrak g$ is simple).
For $n = 1,2,3$ the artifacts certify (Section 7) that
$$\ker\big(\delta: C^1_{\mathrm{odd}}(\mathfrak g,\mathfrak g)\to C^2\big) = \{\mathrm{ad}_Z : Z\in\mathfrak g_{\bar1}\},\qquad \dim = 4n,$$
by combining an exact lower bound on $\mathrm{rank}\,\delta$ (computed modulo three large primes) with the
$4n$ exactly verified, linearly independent kernel elements $\mathrm{ad}_Z$. Hence **the general solution of
$\gamma_{gb}\equiv\delta f \pmod{\mathbf C1}$ is $f = f_{gb} + \mathrm{ad}_Z$, $Z\in\mathfrak g_{\bar1}$.** (For general $n$
this is the statement that all derivations of the basic classical Lie superalgebra $\mathfrak{osp}(2|2n)$ are
inner; the computation makes the session self-contained for $n\le3$ without external references.)

Cohomologically: $\hat{\mathfrak g} = \mathfrak g\oplus\mathbf C$ as $\mathfrak g$-modules, so
$C^\bullet(\mathfrak g,\Pi\hat{\mathfrak g}) = C^\bullet(\mathfrak g,\Pi\mathfrak g)\oplus C^\bullet(\mathfrak g,\Pi\mathbf C)$ and
$\gamma_{gb} = (\delta f_{gb},\ \lambda_{gb}\circ[\cdot,\cdot]_0) = (\delta f_{gb},\ -\delta_{\mathrm{triv}}\lambda_{gb})$.
Both components are coboundaries in their own complexes; $[\gamma_{gb}] = 0\in H^2(\mathfrak g,\Pi\hat{\mathfrak g})$ for all gb.

---

## 5. Theoretical handling of the "adjoint representation / up to scalar" condition

`C_inhomogeneous_definition.md` states that $C(n+1)$ is "realised as a subalgebra of $\mathcal U(A)$ by
adjoint representation", and `C_coboundary_definition.md` requires $\gamma = \delta f$ "as an adjoint
representation, i.e. … for all $X,Y$ up to scalar". I interpret and use this as follows.

1. **What the adjoint representation does to scalars.** The realisation identifies an element
   $X\in\hat{\mathfrak g}\subset\mathcal U$ with the operator $\mathrm{ad}_X$ on $\mathcal U$ (equivalently on the
   oscillators $V\oplus\mathbf CK\oplus\mathbf C\kappa$). The kernel of $\mathrm{ad}$ on $\hat{\mathfrak g}$ is exactly
   $\mathbf C\cdot1$ (an element of the Weyl–Clifford algebra commuting with all oscillators is a scalar), so
   $$\mathrm{ad}(\hat{\mathfrak g}) \cong \hat{\mathfrak g}/\mathbf C1 \cong \mathfrak g .$$
   Hence "$\gamma = \delta f$ as an adjoint representation" means $\mathrm{ad}_{\gamma(X,Y)} = \mathrm{ad}_{\delta f(X,Y)}$,
   i.e. $\gamma(X,Y) - \delta f(X,Y)\in\mathbf C1$ — this is precisely "equality up to scalar". The two phrases
   in the definition are the same condition, and it is the condition I adopt as the definition of triviality.

2. **Why the condition is needed.** $\gamma_{gb}$ genuinely takes values in $\hat{\mathfrak g}$ (Section 1.3): the
   contraction $[b,a]\propto\kappa$ inside a product of two quadratics leaves a $\kappa\cdot$(quadratic), and
   re-expressing a non-symmetrised quadratic such as $b^-b^+$ in the symmetrised basis produces $\tfrac12$.
   Without the clause the literal statement "$\gamma:\mathfrak g\otimes\mathfrak g\to\mathfrak g$" is false, and
   $\gamma=\delta f$ with $f$ valued in $\mathfrak g$ could never hold for gb $\neq0$ (item 4).

3. **Consequence (main theorem).** Under this condition Theorem 1 gives $\gamma_{gb} = \delta f_{gb}$ for all gb.
   The deformation is trivial for every gb; the trivialising map is $f_{gb}$ (unique up to $\mathrm{ad}_Z$,
   $Z$ odd). Moreover the condition is not an artefact: the scalar part is itself a coboundary in the
   trivial-coefficient complex and is absorbed exactly by letting $f$ take values in $\hat{\mathfrak g}$ ($\hat f_{gb} = f_{gb}-\lambda_{gb}$),
   i.e. the deformed Lie superalgebra is literally isomorphic to the undeformed one inside $\mathcal U$.

4. **What happens without the clause (for completeness).** If one insists on exact equality in $\mathcal U$
   while confining $f$ to $\mathfrak g$, then the scalar component of $\gamma_{gb}(X,Y)$ must vanish for all
   $X,Y$. By Theorem 1 that component is $\lambda_{gb}([X,Y]_0)$, and the witnesses
   $$\gamma_{gb}\big(a^\sigma b_j^{+},(b_j^-)^2\big)\big|_{\text{scalar}} = +\mathrm{gb}_{\sigma,j,-},\qquad
     \gamma_{gb}\big(a^\sigma b_j^{-},(b_j^+)^2\big)\big|_{\text{scalar}} = -\mathrm{gb}_{\sigma,j,+}$$
   show that all $4n$ parameters are detected (the linear map gb $\mapsto$ scalar parts has rank $4n$ in the
   artifacts). So in that asymmetric reading **no non-zero gb is trivial**. This reading compares a
   $\hat{\mathfrak g}$-valued cochain with $\mathfrak g$-valued coboundaries and is not the one the definitions
   prescribe; I record it only so that the role of the clause is unambiguous.

5. **Independence of conventions.** The odd generators may be realised as $a^\sigma b_j^s$ or $b_j^s a^\sigma$;
   the two differ by $\mathrm{gb}\,\kappa\cdot1$, which is central and nilpotent, so $\gamma_{gb}$ is unchanged.
   Rescaling basis vectors (e.g. the $\tfrac12$ in $E_{\pm2\delta_n}$) does not affect any statement.
   A projective reading "$\gamma = c\,\delta f$ for some $c\neq0$" is equivalent to the plain one since $f\mapsto f/c$.

---

## 6. Answer to the issue

> *Determine the necessary and sufficient conditions on $\mathrm{gb}_{\sigma,j,s}$ for $\gamma_{gb}$ to be trivial.*

**Under the stated triviality condition (adjoint representation / up to scalar): there is no condition —
$\gamma_{gb}$ is trivial for every $\mathrm{gb}\in\mathbf C^{4n}$ and every $n\ge1$**, with the explicit
cobounding map $f_{gb}$ of Theorem 1, unique modulo $\{\mathrm{ad}_Z: Z\in\mathfrak g_{\bar1}\}$.
In particular every non-zero configuration of gb satisfies $\gamma_{gb} = \delta f$. The *only* data that
survives is the scalar residual $\lambda_{gb}\circ[\cdot,\cdot]_0$, which is invisible to the adjoint
representation and vanishes iff gb $=0$.

The underlying reason is Lemma 1: the inhomogeneous deformation of the oscillator algebra itself is removed
by the shift $b_j^s\mapsto b_j^s+\kappa c_j^s$, so nothing non-trivial can be induced on any subalgebra of
$\mathcal U$ built from the oscillators, except for central (scalar) terms.

---

## 7. Computational verification and artifacts

### 7.1 What is computed (exact rational arithmetic, no floating point)

`scripts/osc_algebra.py` implements normal ordering in $\mathcal U$ with symbolic gb (coefficients are
polynomials in gb with `Fraction` coefficients; the assertion that only gb-degree $\le1$ occurs is checked).
`scripts/verify_triviality.py` then, for $n = 1,2,3$:

| step | check | n=1 | n=2 | n=3 |
|---|---|---|---|---|
| basis, dimension $(2n^2+n+1\,|\,4n)$ | | (4\|4) | (11\|8) | (22\|12) |
| undeformed bracket closes in $\mathfrak g$ (no scalars), super-Jacobi, $\mathrm{ad}$-weights | | ✔ | ✔ | ✔ |
| $\gamma_{gb}$ extracted for each of the $4n$ unit directions; Jacobi of the deformed bracket (cocycle identity) | | ✔ | ✔ | ✔ |
| $\gamma_{gb}|_{\mathfrak g} = \delta f_{gb}$ exactly, $f_{gb}$ from Theorem 1 | | ✔ | ✔ | ✔ |
| scalar part of $\gamma_{gb}(X,Y)$ $= \lambda_{gb}([X,Y]_0)$ exactly | | ✔ | ✔ | ✔ |
| unknowns $\phi_{ij}$ of an odd 1-cochain | | 32 | 176 | 528 |
| $\mathrm{rank}\,\delta$ mod $10^9{+}7$, $998244353$, $999999937$ | | 28 | 168 | 516 |
| $\delta(\mathrm{ad}_Z) = 0$ for odd $Z$ (exact), rank of these $= 4n$ | | 4 | 8 | 12 |
| $\Rightarrow \dim\ker\delta = 4n$ certified | | ✔ | ✔ | ✔ |
| rank of gb $\mapsto$ scalar parts of $\gamma_{gb}$ ($=4n$ ⇒ strict reading needs gb$=0$) | | 4 | 8 | 12 |

Rank certification: a rank computed modulo a prime is a lower bound for the rank over $\mathbf Q$; the $4n$
exactly verified independent kernel vectors give the matching upper bound.

`scripts/recheck_artifacts.py` re-derives every check **from the JSON files alone** (it does not import
the engine), and additionally solves $\delta\phi = \gamma_{gb}|_{\mathfrak g}$ from scratch (consistency of the
augmented system mod $p$) without using the closed form. All checks pass (`ALL RECHECKS PASS`).

### 7.2 Artifact format (`artifacts/cn1_n{n}.json`)

* `basis`: index, label, parity, weight $[\varepsilon;\delta_1,\dots,\delta_n]$, oscillator form, normal-ordered
  monomials; index $m=\dim\mathfrak g$ is the scalar $1$.
* `gb_parameters`: index $p\leftrightarrow(\sigma,j,s)$.
* `structure_constants`: `[i, j, k, value]` with $[Z_i,Z_j]_0 = \sum_k \text{value}\,Z_k$.
* `gamma`: `[p, i, j, k, value]` = coefficient of $\mathrm{gb}_p$ in $\gamma(Z_i,Z_j)$ along $Z_k$ ($k=m$: scalar).
* `f`: `[p, i, j, value]` with $f_{e_p}(Z_j) = \sum_i\text{value}\,Z_i$ (so $\phi_{ij}$ in the notation of the definition).
* `lambda_`: `[p, k, value]` with $\lambda_{e_p}(Z_k)$.
* `inner_odd_derivations`: the maps $\mathrm{ad}_Z$ spanning $\ker\delta$.
* `strict_witnesses`: the pairs $(X,Y)$ exhibiting each gb in a scalar part.
* `verification`: boolean results and ranks. All rationals are strings (`"1/2"`).
  `artifacts/summary.json` aggregates the verification dictionaries.

Reproduce with
```
python3 scripts/test_engine.py          # hand-checked relations, Lemma 1
python3 scripts/verify_triviality.py    # ~7 s, writes artifacts/
python3 scripts/recheck_artifacts.py    # ~8 s, engine-independent re-verification
```

---

## 8. Scope, assumptions, limitations

* The proof of Theorem 1 is general in $n$ and uses only the relations of $\mathcal U$; the computations are
  independent confirmations for $n=1,2,3$ as required by the issue.
* The statement "$\ker\delta$ on odd 1-cochains $=$ inner odd derivations" is certified computationally for
  $n\le3$ only; for larger $n$ it follows from the known inner-ness of derivations of $\mathfrak{osp}(2|2n)$,
  which I did not re-derive here. It affects only the uniqueness clause, not triviality.
* No external files or web resources were used; all definitions are those in `docs/math/`.
* The parameters gb are treated as complex numbers (Section 1.1).
