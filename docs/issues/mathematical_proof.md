# Triviality of the inhomogeneous $gb$-deformation of $C(n+1)=\mathfrak{osp}(2|2n)$

**Status**: resolved (definitive answer, proved for all $n\ge 1$; verified by exact computation for $n=1,2,3$)
**Sources used**: only `docs/math/Cn1_definition.md`, `docs/math/C_inhomogeneous_definition.md`,
`docs/math/C_coboundary_definition.md`. No external literature or web access was used.
**Artifacts**: `verification/cn1_deformation.py`, `verification/artifacts/cn1_n{1,2,3}.json`,
`verification/artifacts/summary.json`.

---

## 0. Answer

> **Theorem.** Let $n\ge 1$. Read the triviality condition the way the definition states it: as an identity of cochains of the
> **adjoint representation**, where the unit $K=1$ of $\mathcal U(A)$ acts by $0$ ("up to scalar").
> Then the deformation $\gamma_{gb}$ is **trivial for every** choice of the $4n$ parameters
> $gb_{\sigma,j,s}\in\mathbb C$. So the necessary and sufficient condition is **vacuous**.
> An explicit trivialising odd map is
> $$
> f_{gb} = -F_{gb},\qquad
> F_{gb}(S)=0,\quad F_{gb}(a^\sigma b)=L_\sigma\, b,\quad F_{gb}(J)=a^-L_+ - a^+L_- ,
> $$
> $$
> L_\sigma=\sum_{j=1}^n\bigl(gb_{\sigma,j,-}\,b_j^+ - gb_{\sigma,j,+}\,b_j^-\bigr)\qquad(\sigma=\pm).
> $$
> Here $S$ ranges over the $\mathfrak{sp}(2n)$ quadratics and $J$ spans $\mathfrak{so}(2)$; see §1.
> $f_{gb}$ is unique modulo $\operatorname{ad}(\mathfrak g_{\bar 1})$.
>
> Moreover $\gamma_{gb}\neq 0$ whenever $gb\neq 0$. So every **non-zero** configuration of $gb$
> gives a non-zero cochain that is nevertheless a coboundary.

> **Complement (strict reading).** Suppose instead that the $K$-component of $\gamma_{gb}$ is kept and $f$ must map
> $\mathfrak g\to\mathfrak g$. Then $\gamma_{gb}=\delta f$ holds **iff $gb=0$**.
> If $f$ may also take values in $\mathfrak g\oplus\mathbb CK$, the deformation is again trivial for every $gb$.
> In that case the trivialising map is $-F_{gb}$ *including* its scalar part.

The "adjoint representation / up to scalar" clause therefore decides the answer. §4 explains why the adjoint
reading is the one the definitions intend.

---

## 1. Set-up

**Oscillator superalgebra.** $A=V\oplus\mathbb CK\oplus\mathbb C\kappa$ with $V_{\bar0}=\langle b_j^\pm\rangle$,
$V_{\bar1}=\langle a^\pm\rangle$ (we write $a^\pm=a_1^\pm$). The non-zero brackets are
$$
[b_k^-,b_l^+]=\delta_{kl}K,\qquad \{a^-,a^+\}=K,\qquad [b_j^s,a^\sigma]=-gb_{\sigma,j,s}\,\kappa .
$$
$K$ (even) and $\kappa$ (odd) are central, and $K$ is identified with $1$ in $\mathcal U(A)$. Every bracket lands in the
centre, so $A$ is 2-step nilpotent and Jacobi holds trivially. In $\mathcal U(A)$ we have
$\kappa^2=\tfrac12[\kappa,\kappa]=0$, so everything is exactly first order in $\kappa$. For the same reason
$\gamma_{gb}$ is **linear** in $gb$.

**Basis of $\mathfrak g$** (super-symmetrised = Weyl-ordered quadratics):

| type | elements | parity | count |
|---|---|---|---|
| $\mathfrak{sp}(2n)$ | $S(x,y)=\tfrac12(xy+yx)$, $x,y\in\{b_j^\pm\}$ | 0 | $n(2n+1)$ |
| $\mathfrak{so}(2)$ | $J=\tfrac12(a^+a^--a^-a^+)$ | 0 | 1 |
| odd | $O(a^\sigma,b_j^s)=a^\sigma b_j^s$, root $\sigma\varepsilon+s\delta_j$ | 1 | $4n$ |

This reproduces $\dim\mathfrak g=(2n^2+n+1\,|\,4n)$ and the root system of `Cn1_definition.md`.
The Frappat generators are recovered exactly:
- $H_1=a^+a^-+b_1^+b_1^-=J+S(b_1^+,b_1^-)$
- $H_{n+1}=-b_n^+b_n^--\tfrac12=-S(b_n^+,b_n^-)$
- $E_{\varepsilon\pm\delta_l}=O(a^+,b_l^\pm)$, and so on.

The normalisation clash between $E_{2\delta_n}=\tfrac12(b_n^+)^2$ and $E_{2\delta_k}=(b_k^+)^2$ in that file is a rescaling of a
basis vector and plays no role here.

**Fact A (closure without constants).** With these Weyl-ordered lifts, $[X,Y]_0\in\mathfrak g$ with **no**
$K$-component for all $X,Y\in\mathfrak g$. Hence $\mathfrak g\oplus\mathbb CK=\mathfrak g\times\mathbb CK$ as Lie superalgebras.
(This is the standard property of Weyl ordering; it is also verified exactly, see `undeformed_closure_no_scalar`.)

**Deformed bracket.** For $X,Y\in\mathfrak g$, compute the supercommutator in $\mathcal U(A_{gb})$ and normal-order it.
The result has the form
$$
[X,Y]_{gb}=[X,Y]_0+\kappa\,\hat\gamma(X,Y),\qquad \hat\gamma(X,Y)\in\mathfrak g\oplus\mathbb CK .
$$
Write $\hat\gamma=\gamma+c\,K$ with $\gamma\in\mathfrak g$ and $c$ scalar. In the adjoint representation $K$ acts by $0$, so the
cochain of the deformation is $\gamma_{gb}:=\gamma$. Note that $\hat\gamma(X,Y)$ always has parity $p(X)+p(Y)+1$, so
$\gamma_{gb}$ is an **odd** 2-cochain. That is why the comparison is with $\delta f$ for an **odd** $f$.

*Parity note.* `C_inhomogeneous_definition.md` calls the $gb$ "parity-1". The bracket $[b,a]$ is odd and so is $\kappa$, so the
scalar coefficient is ordinary (even). The parity 1 belongs to the cochain $\kappa\cdot gb$, i.e. to $\gamma_{gb}$ and $f$.
Treating $gb$ as Grassmann-odd would make $[b,a]$ even, which contradicts the parity of $A$. The result does not depend on
this point because everything is linear in $gb$.

**Sample closed formulas.** Write $g_{\sigma}(x):=gb_{\sigma,j,s}$ for $x=b_j^s$ and $\omega(x,y)=[x,y]$.
These are obtained by hand and checked against the JSON:
$$
\hat\gamma\bigl(S(x,y),\,a^\sigma z\bigr)=-g_\sigma(y)\,xz-g_\sigma(x)\,yz,
$$
$$
\gamma\bigl(S(x,y),\,a^\sigma z\bigr)=-g_\sigma(y)\,S(x,z)-g_\sigma(x)\,S(y,z),\qquad
c=-\tfrac12\bigl(g_\sigma(y)\,\omega(x,z)+g_\sigma(x)\,\omega(y,z)\bigr),
$$
$$
\gamma\bigl(J,S(x,y)\bigr)=g_+(x)\,O(a^-,y)-g_-(x)\,O(a^+,y)+(x\leftrightarrow y),\qquad
\gamma(S,S')=0 .
$$
Example ($n=1$, $gb_{+,1,+}=1$): $\gamma(S(b_1^+,b_1^+),O(a^+,b_1^-))=-2S(b_1^+,b_1^-)$, with scalar part $c=+1$.
This matches `cn1_n1.json`.

---

## 2. Proof of the Theorem (all $n$)

**Lemma 1 (fermion shift).** In $\mathcal U(A_{gb})$ put $a'^\sigma:=a^\sigma+\kappa L_\sigma$. Then
$$
[b_j^s,a'^\sigma]=0,\qquad \{a'^\sigma,a'^\tau\}=\{a^\sigma,a^\tau\},\qquad [b,b']\ \text{unchanged}.
$$
*Proof.* $\kappa$ is central and $b$ is even, so $[b_j^s,\kappa L_\sigma]=\kappa[b_j^s,L_\sigma]$.
By the CCR, $[b_j^-,L_\sigma]=gb_{\sigma,j,-}$ and $[b_j^+,L_\sigma]=gb_{\sigma,j,+}$. Hence
$[b_j^s,a'^\sigma]=-gb_{\sigma,j,s}\kappa+gb_{\sigma,j,s}\kappa=0$.
Next, $\{a^\sigma,\kappa L_\tau\}=\kappa[L_\tau,a^\sigma]\in\kappa^2\mathcal U=0$, and $\{\kappa L,\kappa L'\}=0$ for the same
reason. $\square$

So $a'^\pm,b_j^\pm,\kappa$ satisfy the **undeformed** relations. By PBW the assignment
$a\mapsto a'$, $b\mapsto b$, $\kappa\mapsto\kappa$ defines an isomorphism of superalgebras
$\Theta:\mathcal U(A_0)\to\mathcal U(A_{gb})$. Its inverse is $a\mapsto a-\kappa L$.

**Lemma 2.** For $X\in\mathfrak g$, $\Theta(X)=X+\kappa F_{gb}(X)$ with $F_{gb}$ as in §0, valued in $\mathfrak g\oplus\mathbb CK$.
*Proof.* $S$ contains no $a$, so $F(S)=0$. Next, $(a^\sigma+\kappa L_\sigma)b=a^\sigma b+\kappa L_\sigma b$.
For $J$, expand $\tfrac12\bigl((a^++\kappa L_+)(a^-+\kappa L_-)-(a^-+\kappa L_-)(a^++\kappa L_+)\bigr)$ and use
$a\kappa=-\kappa a$ and $\kappa^2=0$. This gives $J+\kappa(a^-L_+-a^+L_-)$. $\square$

**Lemma 3 (sign bookkeeping).** For homogeneous $X$ and $Z$,
$[X,\kappa Z]=(-1)^{p(X)}\kappa[X,Z]$ and $[\kappa Z,Y]=\kappa[Z,Y]=-(-1)^{(p(Z))p(Y)}\kappa[Y,Z]$.
Hence, for an odd $F$ (so $p(F(X))=p(X)+1$),
$$
[X+\kappa FX,\;Y+\kappa FY]_{gb}=[X,Y]_0+\kappa\Bigl(\hat\gamma(X,Y)+(-1)^{p(X)}[X,FY]-(-1)^{(p(X)+1)p(Y)}[Y,FX]\Bigr).
$$

**Proof of the Theorem.** $\Theta$ is an algebra homomorphism, so
$[\Theta X,\Theta Y]_{gb}=\Theta([X,Y]_0)=[X,Y]_0+\kappa F([X,Y]_0)$. Comparing with Lemma 3 gives the exact identity
in $\mathfrak g\oplus\mathbb CK$:
$$
\boxed{\ \hat\gamma_{gb}=-\,\delta F_{gb}=\delta(-F_{gb})\ }
$$
Here $\delta$ is precisely the operator of `C_coboundary_definition.md`.

Now apply the projection $\pi:\mathfrak g\oplus\mathbb CK\to\mathfrak g$, which is what passing to the adjoint representation
does. By Fact A, $\pi$ is a Lie superalgebra homomorphism and $[\,\cdot\,,K]=0$. The scalar part of $F$ only enters $\delta F$
through $[X,K\cdot\lambda]=0$ and through the $K$-component of $F([X,Y])$, so
$\pi\circ\delta F=\delta(\pi\circ F)$. Therefore
$$
\gamma_{gb}=\pi\hat\gamma_{gb}=\delta f_{gb},\qquad f_{gb}=-\pi F_{gb}:\mathfrak g\to\mathfrak g\ \text{odd}.\qquad\blacksquare
$$

**Non-vanishing.** If $gb_{\sigma,j,s}\neq0$, take $x=y=b_j^s$ and $z=b_j^{-s}$ in the first sample formula. The coefficient
of $S(b_j^s,b_j^{-s})$ in $\gamma(S(x,x),a^\sigma z)$ is $-2gb_{\sigma,j,s}\neq0$. So $\gamma_{gb}\ne0$ for $gb\ne0$
(also verified: `all_params_nonzero_gamma`).

**Uniqueness.** For odd $Z$, $\delta(\operatorname{ad}Z)=0$ by the super-Jacobi identity. So $f$ is determined at least up to
$\operatorname{ad}(\mathfrak g_{\bar1})$, which has dimension $4n$ since the centre of $\mathfrak g$ is $0$. The computed nullity
of $\delta$ on odd 1-cochains is exactly $4n$ for $n=1,2,3$. Hence the odd 1-cocycles are exactly the inner ones, and
$f_{gb}$ is unique modulo $\operatorname{ad}(\mathfrak g_{\bar1})$ in those cases.

**Conceptual summary.** The $gb$-deformation is a change of variables of the oscillator algebra in disguise: the fermion is
shifted by $\kappa\times(\text{boson})$. It therefore cannot produce a non-trivial cohomology class. This is consistent with
the rigidity one expects for basic classical $\mathfrak{osp}(2|2n)$, but the proof above uses no such external result.

---

## 3. Proof of the Complement (strict reading)

Every $f:\mathfrak g\to\mathfrak g$ has $\delta f$ valued in $\mathfrak g$, by Fact A. So $\hat\gamma_{gb}=\delta f$ forces the
scalar part $c_{gb}$ to vanish. By the formula for $c$ in §1, with $x=y=b_j^s$ and $z=b_j^{-s}$:
$$
c_{gb}\bigl(S(b_j^s,b_j^s),O(a^\sigma,b_j^{-s})\bigr)=-gb_{\sigma,j,s}\,\omega(b_j^s,b_j^{-s})=\pm gb_{\sigma,j,s}.
$$
So $c_{gb}=0$ iff all $gb=0$. Conversely, if $gb=0$ then $\hat\gamma=0=\delta 0$.
(Verified: the linear map $gb\mapsto c_{gb}$ has rank $4n$ for $n=1,2,3$.)

If $f$ may take values in $\mathfrak g\oplus\mathbb CK$, the boxed identity $\hat\gamma_{gb}=\delta(-F_{gb})$ holds exactly,
including scalars. In that case the deformation is again trivial for every $gb$
(`gamma_eq_delta_f_with_scalar_valued_f(exact)` = true).

---

## 4. Handling of "as an adjoint representation / up to scalar"

The two definition files fix the reading:
1. "$C(n+1)$ is realized as a subalgebra of $\mathcal U(A)$ **by adjoint representation**".
2. The extension $L=\mathfrak g\oplus\kappa\mathfrak g$ is "an abelian extension by its **adjoint** representation".
3. "$\gamma=\delta f$ **as an adjoint representation** … **up to scalar**."

In $\mathcal U(A)$ a bracket of quadratics produces quadratics *plus multiples of $K=1$*. In the deformed bracket this
happens through the $\kappa$-contraction, e.g. $\kappa\,b_j^-b_j^+=\kappa(S(b_j^+,b_j^-)+\tfrac12)$. These multiples of $K$
are central and act by zero in the adjoint representation, so they are not part of a $\mathfrak g$-valued cochain. "Up to
scalar" is exactly the instruction to discard them, i.e. to apply $\pi$. This is also the only reading in which
$\gamma_{gb}$ is a $\mathfrak g$-valued 2-cochain (a 2-cocycle, by the Jacobi check below) of the adjoint module, so that
the question "is $\gamma=\delta f$" is a question in $H^2(\mathfrak g,\mathfrak g)$.

The other possible meaning of "up to scalar" is $\gamma=\lambda\,\delta f$ for some $\lambda\in\mathbb C^\times$. It gives the
same answer, since $\lambda\,\delta f=\delta(\lambda f)$.

Taking the strict reading (keep the $K$-part, $f$ into $\mathfrak g$) would turn a pure normal-ordering artefact into an
"obstruction". That artefact disappears as soon as $f$ is allowed its natural scalar part (§3). The strict answer "only
$gb=0$" is therefore an artefact of the realisation in $\mathcal U(A)$, not a property of the deformation of $\mathfrak g$.

---

## 5. Computational evidence ($n=1,2,3$)

Run `python3 verification/cn1_deformation.py` (Python 3, numpy and sympy; about 3 s). It regenerates all JSON files.
All oscillator arithmetic is exact (`fractions.Fraction`). Normal ordering in $\mathcal U(A_{gb})$ is implemented by
rewriting with the relations of §1. Floating point is used only for the SVD rank and least-squares cross-check.

| $n$ | $\mathfrak g$ | $\dim$ | $\delta$ on odd $f$ (rows×cols) | rank | nullity | rank of $gb\mapsto c_{gb}$ | max lstsq residual |
|---|---|---|---|---|---|---|---|
| 1 | $\mathfrak{osp}(2\|2)$ | $4\|4$ | 144×32 | 28 | 4 | 4 | 3.8e-14 |
| 2 | $\mathfrak{osp}(2\|4)$ | $11\|8$ | 1784×176 | 168 | 8 | 8 | 5.4e-14 |
| 3 | $\mathfrak{osp}(2\|6)$ | $22\|12$ | 9780×528 | 516 | 12 | 12 | 9.6e-14 |

Exact checks, all **true / 0** for every $n$ and every one of the $4n$ unit parameters $gb_{\sigma,j,s}=1$, plus one
random rational $gb$ vector per $n$ (recorded in the JSON):

| check (JSON key) | meaning | result |
|---|---|---|
| `undeformed_closure_no_scalar` | Fact A | true |
| `undeformed_jacobi_violations` | $\mathfrak g$ is a Lie superalgebra | 0 |
| `jacobi_violations_mod_scalars` | first-order Jacobi of $[\,,]_0+\kappa\gamma_{gb}$ (so $\gamma_{gb}$ is a 2-cocycle) | 0 |
| `gamma_is_zero_mod_scalars` | $\gamma_{gb}=0$? | **false** (non-trivial cochain) |
| `explicit_formula_equals_substitution` | Lemma 2 formula = direct substitution $a\to a+\kappa L$ | true |
| `gamma_eq_delta_f_mod_scalars(exact)` | **Theorem**: $\gamma_{gb}=\delta f_{gb}$ | **true** |
| `gamma_eq_delta_f_with_scalar_valued_f(exact)` | boxed identity including $K$-parts | true |
| `strict_reading_only_gb_zero` | Complement | true |

**Negative controls** (to show the checks can fail): $\delta(+F)$ and $\delta(0)$ are rejected. Perturbing one entry of
$\gamma$ produces 27, 69 and 111 Jacobi violations for $n=1,2,3$.

**Data format** (`verification/artifacts/cn1_n{n}.json`), for reuse by other researchers:
- `basis`: index, label, parity, root $(\varepsilon,\delta)$, oscillator lift as normal-ordered words.
- `structure_constants`: `[i, j, k, c]` meaning $[Z_i,Z_j]_0=\sum_k c\,Z_k$.
- `per_param[<gb name>]`, for that parameter set to 1 (everything is linear in $gb$):
  - `gamma_g_part`: `[i, j, k, coef]`
  - `gamma_scalar_part`: `[i, j, c]`
  - `explicit_f`: `[j, i, phi]` meaning $f(Z_j)=\sum_i\phi_{ij}Z_i$
  - `explicit_f_scalar_part`
  - all boolean checks
- `coboundary_rank`, `odd_1cocycle_dim(nullity)`, `strict_scalar_obstruction_rank`, `negative_controls`.

`summary.json` collects the checks without the bulky tables.

---

## 6. Conclusion

For $\mathfrak g=C(n+1)=\mathfrak{osp}(2|2n)$, the inhomogeneous deformation $\gamma_{gb}$ is a non-zero odd 2-cocycle
whenever $gb\neq0$. Read in the adjoint representation, as the definitions prescribe, it is **always a coboundary**:
$\gamma_{gb}=\delta f_{gb}$ with the explicit $f_{gb}$ of §0, for all $gb\in\mathbb C^{4n}$ and all $n\ge1$. The $f_{gb}$ is
unique modulo $\operatorname{ad}(\mathfrak g_{\bar 1})$; this is verified for $n\le3$.

The triviality condition on the $gb$ is therefore **empty**. Only the non-adjoint strict reading (keeping the central
$K$-component and forbidding scalar-valued $f$) would cut it down to $gb=0$. That reading is excluded by the
"adjoint representation / up to scalar" clause.
