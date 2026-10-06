# Triviality of the Inhomogeneous ($gb$) Deformation of $C(n+1)=\mathfrak{osp}(2|2n)$

**Issue**: `docs/issues/issue_open.md`
**Status**: resolved — definitive conclusion reached.
**Author**: ritsumei-aoi (independent researcher) · Model: Claude Opus 4.8
**Date**: 2026-10-06

---

## 0. Executive summary — the theorem

> **Theorem.** Let $\mathfrak{g}=C(n+1)=\mathfrak{osp}(2|2n)$ with its oscillator
> realization, and let $\gamma_{gb}$ be the inhomogeneous deformation cocycle
> defined by the $4n$ parameters $\mathrm{gb}_{\sigma,j,s}$
> ($\sigma,s\in\{+,-\}$, $1\le j\le n$) of
> `docs/math/C_inhomogeneous_definition.md`. Then **for every value of the
> parameters** $\{\mathrm{gb}_{\sigma,j,s}\}$ the deformation $\gamma_{gb}$ is
> **trivial**: there exists an odd linear map $f:\mathfrak g\to\mathfrak g$ with
> $$\gamma_{gb}=\delta f$$
> as a $2$-cocycle valued in the adjoint representation (up to scalar, see §4).

Equivalently: the **necessary and sufficient condition on $gb$ for triviality is
vacuous** — *no* non-zero configuration of $gb$ yields a non-trivial
deformation. In cohomological terms the entire $4n$-dimensional space of
inhomogeneous cocycles lies inside the coboundaries:
$$
\dim\bigl(\text{inhomogeneous cocycles}\bigr)=4n,\qquad
\dim\bigl(\text{inhomogeneous cocycles}\cap\operatorname{im}\delta\bigr)=4n,\qquad
\dim\bigl(\text{non-trivial classes}\bigr)=0 .
$$

This was established by **exact (rational) symbolic computation** for $n=1,2,3$,
by two independent linear-algebra methods, and made **constructive**: an
explicit trivializing map $f$, with coefficients linear in $gb$, was produced
and symbolically verified ($\delta f=\gamma_{gb}$ with zero residual) for
$n=1,2,3$.

| $n$ | $\mathfrak g$ | $\dim\mathfrak g$ (even\|odd) | # $gb$ | trivializable dim | non-trivial classes | explicit $f$ verified |
|---|---|---|---|---|---|---|
| 1 | $\mathfrak{osp}(2\|2)$ | $8\ (4\|4)$ | 4 | **4** | **0** | ✅ ($0$ residual) |
| 2 | $\mathfrak{osp}(2\|4)$ | $19\ (11\|8)$ | 8 | **8** | **0** | ✅ ($0$ residual) |
| 3 | $\mathfrak{osp}(2\|6)$ | $34\ (22\|12)$ | 12 | **12** | **0** | ✅ ($0$ residual) |

---

## 1. Setup and conventions

### 1.1 Algebra and oscillator realization
Following `docs/math/Cn1_definition.md`, $\mathfrak g=C(n+1)=\mathfrak{osp}(2|2n)$
is realized inside $\mathcal U(A)$ by quadratic monomials in

* a **fermionic pair** $a_1^+,a_1^-$ with $\{a_1^-,a_1^+\}=1$, $(a_1^\pm)^2=0$;
* **bosonic pairs** $b_j^+,b_j^-$ ($1\le j\le n$) with $[b_j^-,b_k^+]=\delta_{jk}$;
* $a$ and $b$ super-commute in the undeformed algebra.

The basis $\{Z_i\}$ used throughout (file `code/basis.py`) is

* **even** ($\dim=2n^2+n+1$):
  $h=a_1^+a_1^-$ (the $\mathfrak{so}(2)$ generator);
  $M^{++}_{jk}=b_j^+b_k^+$, $M^{--}_{jk}=b_j^-b_k^-$ ($j\le k$) and
  $M^{+-}_{jk}=b_j^+b_k^-$ (all $j,k$), spanning $\mathfrak{sp}(2n)$;
* **odd** ($\dim=4n$):
  $F^{\sigma s}_j=a_1^\sigma b_j^s$ (the roots $\pm\varepsilon\pm\delta_j$).

### 1.2 The inhomogeneous deformation
Per `docs/math/C_inhomogeneous_definition.md`, the deformation introduces an
**odd central** element $\kappa$ ($p(\kappa)=1$, $\kappa$ central, $\kappa^2=0$)
and deforms the fermion–boson exchange relation to
$$
[\,b_j^s,\;a_1^\sigma\,] = -\,\mathrm{gb}_{\sigma,j,s}\,\kappa,
\qquad\text{i.e.}\qquad
b_j^s a_1^\sigma = a_1^\sigma b_j^s - \mathrm{gb}_{\sigma,j,s}\,\kappa .
$$
The deformed super-commutator of two quadratic generators is
$$
[X,Y]_\kappa = [X,Y]_0 + \kappa\,\gamma_{gb}(X,Y) + (\text{central scalars}),
$$
where $[X,Y]_0$ is the undeformed $\mathfrak{osp}$ bracket and
$\gamma_{gb}:\mathfrak g\otimes\mathfrak g\to\mathfrak g$ is the induced
$2$-cochain. Because $\kappa$ is odd, $\gamma_{gb}$ is a **parity-reversing**
(odd) cochain: $p\bigl(\gamma_{gb}(X,Y)\bigr)=p(X)+p(Y)+1$, i.e. it is valued in
the parity-shifted adjoint module $\Pi\mathfrak g$.

### 1.3 The coboundary / triviality criterion
Per `docs/math/C_coboundary_definition.md`, for an **odd** linear map
$f:\mathfrak g\to\mathfrak g$ (so $p(f(X))=p(X)+1$),
$$
(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y]),
$$
and $\gamma_{gb}$ is **trivial** iff $\gamma_{gb}=\delta f$ for some such $f$
(equality in the adjoint representation, up to scalar — §4).

---

## 2. The decisive technical point: $\kappa$ is **odd**

The entire result hinges on treating the central parameter $\kappa$ with its
correct parity. Since $\kappa$ is odd, moving it past oscillator content of
parity $p$ produces a sign $(-1)^p$. Concretely, two sign sources appear when
computing brackets (engine `code/osp_engine.py`):

1. **(generation)** when a $b\,a\to a\,b$ reordering *creates* $\kappa$ inside a
   monomial, carrying it to the canonical (leftmost) position past a prefix of
   fermionic parity $\pi$ contributes $(-1)^{\pi}$;
2. **(transport)** multiplying $X\cdot(\kappa\,Y')$ moves $\kappa$ left past $X$,
   contributing $(-1)^{p(X)}$.

These signs are invisible in a *single* bracket (where $\kappa$ is generated
once, at the end) but are essential in **nested** brackets. A naive
“$\kappa$-as-commuting-scalar’’ implementation passes the super-antisymmetry and
single-bracket closure tests yet **violates the graded Jacobi identity at order
$\kappa^1$**, which would spuriously make $\gamma_{gb}$ appear non-trivial. With
the correct odd-$\kappa$ bookkeeping the full associativity/Jacobi structure of
$\mathcal U(A)$ is restored:

> **Verification (engine correctness).** With odd-$\kappa$ signs, the full
> graded Jacobiator of the deformed quadratic generators vanishes **identically**
> on all monomial components (including the $\kappa$-scalar components):
> `code/test_fulljac.py` → *nonzero on $0/336$ triples* ($n=1$). Undeformed
> closure and super-antisymmetry also hold (`code/test_engine.py`).

Because the deformed $\mathcal U(A)$ super-commutator satisfies graded Jacobi
*exactly*, its restriction to $\mathfrak g$ modulo the center satisfies Jacobi;
hence $[X,Y]_0$ is the genuine $\mathfrak{osp}(2|2n)$ bracket (verified: $0$
Jacobi violations, §5) and the $\kappa^1$ adjoint part $\gamma_{gb}$ is a genuine
$2$-**cocycle**, $\delta_{\mathrm{CE}}\gamma_{gb}=0$ (it is precisely the
$\kappa^1$, degree-$2$ component of the vanishing Jacobiator; the central scalar
terms, being central, drop out of $[X,\,\cdot\,]$).

---

## 3. The deformation cocycle $\gamma_{gb}$

The engine evaluates $\gamma_{gb}(Z_a,Z_b)$ for all basis pairs; the full tables
are stored in `artifacts/struct_constants_n{1,2,3}.json`. Representative
$n=1$ values (all coefficients linear in $gb$):

* **odd $\times$ odd $\to$ odd** (graded-symmetric):
$$
\gamma(F^{++}_1,F^{+-}_1)=\mathrm{gb}_{+1+}\,F^{+-}_1+\mathrm{gb}_{+1-}\,F^{++}_1,\qquad
\gamma(F^{++}_1,F^{++}_1)=2\,\mathrm{gb}_{+1+}\,F^{++}_1 ;
$$
* **even $\times$ odd $\to$ even**:
$$
\gamma(M^{++}_{11},F^{++}_1)=-2\,\mathrm{gb}_{+1+}\,M^{++}_{11},\qquad
\gamma(M^{+-}_{11},F^{++}_1)=-\mathrm{gb}_{+1-}\,M^{++}_{11}-\mathrm{gb}_{+1+}\,M^{+-}_{11};
$$
* **even($h$) $\times$ even $\to$ odd** (non-zero only because $h$ carries the
  fermion):
$$
\gamma(h,M^{++}_{11})=2\,\mathrm{gb}_{+1+}\,F^{-+}_1-2\,\mathrm{gb}_{-1+}\,F^{++}_1,\qquad
\gamma(h,F^{++}_1)=-\mathrm{gb}_{+1+}\,h .
$$

Note $\gamma(M,M')=0$ whenever $M,M'$ are both purely bosonic (no fermion to
contract), so the deformation is supported exactly on pairs that involve the
fermionic pair $a_1^\pm$ — consistent with the exchange relation being the only
deformed relation.

---

## 4. The "adjoint representation / up to scalar" condition

The oscillator realization is a **central extension**: brackets of the quadratic
monomials close into $\mathfrak g$ only *modulo scalars*. Two kinds of central
terms appear.

* **$\kappa^0$ scalars** (the even central element $K$): standard
  normal-ordering constants (e.g. the $+\tfrac12$ in a symplectic Cartan
  generator). They are central and are quotiented out to obtain the simple
  algebra $\mathfrak{osp}(2|2n)$; they do not affect the degree-$2$ structure
  constants.
* **$\kappa^1$ scalars** ($\kappa\cdot\text{const}$): these are the
  `scalar*kappa leftovers` reported by the engine
  ($12,40,84$ terms for $n=1,2,3$). They are the component of the deformed
  bracket lying in the **odd central line** $\mathbb C\,\kappa\subset\Pi\mathbb C$,
  i.e. a cocycle valued in the *trivial* module, not the adjoint.

The deformation-theoretic object of the issue is $\gamma_{gb}$ as a cocycle
**valued in the adjoint representation** $\Pi\mathfrak g$. The clause
“$\gamma(X,Y)=(\delta f)(X,Y)$ … as an adjoint representation … up to scalar” in
`docs/math/C_coboundary_definition.md` is precisely the instruction to compare
$\gamma_{gb}$ and $\delta f$ **in $\Pi\mathfrak g$, i.e. modulo the central
scalar line**. Our treatment implements this exactly:

* we project every bracket onto its degree-$2$ ($\mathfrak g$-valued) part,
  carrying the $\kappa^1$ scalars in a separate ledger (`project_g` /
  `scalar_kappa` in `code/analyze.py`);
* the triviality equations $\delta f=\gamma_{gb}$ are imposed **only on the
  $\mathfrak g$-components**, which is the “up to scalar’’ adjoint comparison.

Thus the central $\kappa$-scalar cocycle (a possible non-trivial *central
extension* in the $\kappa$ direction) is a genuinely separate cohomology class
$H^2(\mathfrak g,\mathbb C)$ and is **outside** the scope of the adjoint
triviality question; it is exactly the "scalar" that the criterion permits us to
discard. Our theorem concerns the adjoint part, and that part is always a
coboundary.

---

## 5. Triviality computation and its validation

Let $\delta$ denote the coboundary operator on odd linear maps
$f=(\phi_{ij})$, $f(Z_j)=\sum_i\phi_{ij}Z_i$ ($\phi_{ij}=0$ unless
$p(i)\ne p(j)$). Both $\delta f$ and $\gamma_{gb}$ are linear, so
$\delta f=\gamma_{gb}$ is a linear system in the unknowns $(\phi,gb)$.

**Method A — joint nullspace** (`code/analyze.py`). Assemble all equations
$\bigl(\delta f-\gamma_{gb}\bigr)(Z_a,Z_b)[c]=0$ into a rational matrix over
columns $[\phi\,|\,gb]$; compute $\ker$; project to the $gb$-coordinates. The
image is the subspace of trivializable $gb$.

**Method B — image test** (`code/test_control.py`). Build the matrix of $\delta$
alone (columns $=\phi$, rows $=$ cochain coordinates); for each $gb$-direction
test whether the cochain $\gamma_{gb}$ lies in $\operatorname{im}\delta$ by a
rank comparison $\operatorname{rank}[\delta]\overset?=\operatorname{rank}[\delta\,|\,\gamma_{gb}]$.

**Positive control (solver validity).** A random genuine coboundary
$T=\delta f_0$ must be reported as trivial. `VALIDATION 1` → **True** (it lies in
$\operatorname{im}\delta$), confirming the solver detects coboundaries.

**Results (exact rationals).**

```
n=1:  dim im(delta)=28, dim ker(delta)=4;  Jacobi 0/56 ;  trivializable 4/4
n=2:  Jacobi 0/400 ;  trivializable 8/8
n=3:  Jacobi 0/400 ;  trivializable 12/12
```

Methods A and B agree in every case: **every** $gb$-direction is a coboundary.
(Full machine-readable summary: `artifacts/triviality_summary.json`.)

---

## 6. Constructive trivialization — an explicit $f$

Existence is made concrete. Solving $\delta f=\gamma_{gb}$ symbolically in $gb$
yields a map $f$ whose coefficients are **linear in the $gb$ parameters**, and
$\delta f=\gamma_{gb}$ is then verified on every pair with **zero residual**
(`code/explicit_f.py`; artifacts `explicit_trivializing_f_n{1,2,3}.json`). For
$n=1$ the closed form is

$$
\begin{aligned}
f(M^{++}_{11})&=-2\,\mathrm{gb}_{-1+}F^{++}_1-2\,\mathrm{gb}_{+1+}F^{-+}_1, &
f(F^{++}_1)&=\mathrm{gb}_{+1+}\,h,\\
f(M^{--}_{11})&=-2\,\mathrm{gb}_{-1-}F^{+-}_1-2\,\mathrm{gb}_{+1-}F^{--}_1, &
f(F^{+-}_1)&=\mathrm{gb}_{+1-}\,h,\\
f(M^{+-}_{11})&=-\mathrm{gb}_{-1-}F^{++}_1-\mathrm{gb}_{-1+}F^{+-}_1
              -\mathrm{gb}_{+1-}F^{-+}_1-\mathrm{gb}_{+1+}F^{--}_1, &
f(F^{-+}_1)&=-\mathrm{gb}_{-1+}\,h,\\
& & f(F^{--}_1)&=-\mathrm{gb}_{-1-}\,h,
\end{aligned}
$$
with $f(h)=0$. This is exactly the linear map induced on quadratics by the
oscillator redefinition
$$
a_1^\sigma\;\longmapsto\;a_1^\sigma+\kappa\sum_{j}\bigl(\lambda_{\sigma j}b_j^{+}+\mu_{\sigma j}b_j^{-}\bigr),
\qquad \lambda_{\sigma j}=-\mathrm{gb}_{\sigma,j,-},\;\; \mu_{\sigma j}=\mathrm{gb}_{\sigma,j,+},
$$
which reproduces the deformed exchange relation
$[b_k^t,a_1^\sigma]=-\mathrm{gb}_{\sigma,k,t}\kappa$. In other words, **the
inhomogeneous deformation is removed by a $\kappa$-linear change of the fermionic
generators** — the prototypical inner (coboundary) deformation. The structure is
transparent: $f$ sends the symplectic even generators to odd roots and the odd
roots to the $\mathfrak{so}(2)$ generator $h$, with $gb$-linear coefficients.

---

## 7. Conclusion

For $\mathfrak g=C(n+1)=\mathfrak{osp}(2|2n)$:

1. The inhomogeneous cochain $\gamma_{gb}$ is a bona-fide parity-odd
   $2$-cocycle valued in the adjoint module $\Pi\mathfrak g$ (guaranteed by the
   exact vanishing of the deformed graded Jacobiator, §2).
2. **$\gamma_{gb}$ is trivial for all $gb$.** The necessary-and-sufficient
   triviality condition is *vacuous*: there is no non-zero $gb$ giving a
   non-trivial deformation. The adjoint second-cohomology contribution of the
   $gb$-family is **zero**; verified exactly for $n=1,2,3$ by two independent
   methods and realized by an explicit, symbolically verified $f$.
3. The only genuinely non-removable datum is the **central $\kappa$-scalar**
   part (a $H^2(\mathfrak g,\mathbb C)$ phenomenon), which the "up to scalar"
   clause deliberately excludes from the adjoint triviality question.

Mathematically, the inhomogeneous $gb$-deformations of $\mathfrak{osp}(2|2n)$ are
**inner**: they amount to $\kappa$-linear redefinitions of the fermionic
oscillators and carry no adjoint deformation moduli.

---

## 8. Reproducibility — computational artifacts

All code is exact (SymPy over $\mathbb Q$); no external data or networks were
used. Run `python3 code/analyze.py 1 2 3`.

| File | Contents |
|---|---|
| `code/osp_engine.py` | Oscillator engine with correct **odd-$\kappa$** signs |
| `code/basis.py` | Basis of $\mathfrak{osp}(2\|2n)$ as quadratic monomials |
| `code/analyze.py` | Structure constants, $\gamma_{gb}$, triviality (Method A) |
| `code/test_control.py` | Independent image test (Method B) + positive control |
| `code/explicit_f.py` | Constructs & verifies explicit trivializing $f$ |
| `code/test_engine.py`, `code/test_fulljac.py` | Engine sanity + full Jacobiator $\equiv0$ |
| `artifacts/struct_constants_n{1,2,3}.json` | Full structure constants and $\gamma_{gb}$ tables |
| `artifacts/triviality_summary.json` | Dimensions, Jacobi counts, conclusions |
| `artifacts/explicit_trivializing_f_n{1,2,3}.json` | Verified trivializing maps $f$ |

Each JSON is a plain dictionary keyed by basis-generator names, directly
re-checkable by a third party: for any pair `"A|B"` and the listed $f$, one may
confirm $\delta f=\gamma_{gb}$ by substituting the (undeformed) structure
constants, independently of this engine.
