# Triviality of the Inhomogeneous Deformation of $C(n+1)=\mathfrak{osp}(2|2n)$

**Status**: resolved. **Conclusion**: *every* configuration of the $4n$ parameters
$\mathrm{gb}_{\sigma,j,s}$ gives a trivial deformation. There is no condition on
$\mathrm{gb}$. For each $\mathrm{gb}$ there is an explicit odd map $f_{\mathrm{gb}}$
with $\gamma_{\mathrm{gb}}=\delta f_{\mathrm{gb}}$. This holds modulo scalars, as the
adjoint-representation clause requires. The statement is proved for all $n\ge 1$ and
checked with exact arithmetic for $n=1,2,3$.

Sources used: only `docs/math/Cn1_definition.md`, `docs/math/C_inhomogeneous_definition.md`,
and `docs/math/C_coboundary_definition.md`. No external literature or web access was used.

---

## 0. Conventions and interpretation

### 0.1 The algebra $U(A)$
$V$ has basis $a_1^\pm$ (odd) and $b_k^\pm$ (even), $k=1,\dots,n$. We write $a^\pm:=a_1^\pm$.
$A=V\oplus\mathbf C K\oplus\mathbf C\kappa$ with $K$ even central, $\kappa$ odd central, and we set $K=1$.
The brackets in $A$ (all central) are:

$$
[b_k^-,b_l^+]=\delta_{kl},\qquad \{a^-,a^+\}=1,\qquad [a^\pm,a^\pm]=0,\qquad
[b_j^s,a^\sigma]=-\mathrm{gb}_{\sigma,j,s}\,\kappa .
$$

Since every bracket in $A$ lies in the centre, the super-Jacobi identity holds trivially for **every**
$\mathrm{gb}\in\mathbf C^{4n}$. So the deformed $A$ is always a Lie superalgebra, and $U(A)$ has a PBW basis.
In $U(A)$, $\kappa^2=\tfrac12[\kappa,\kappa]=0$. Also, $\kappa$ commutes with even elements and
anticommutes with odd ones. Because $\kappa^2=0$, the deformation is exactly first order: there are no
$\mathrm{gb}^2$ terms.

### 0.2 Parity of $\mathrm{gb}$
`C_inhomogeneous_definition.md` says that the parameters "must have parity 1". Read literally (as
Grassmann-odd numbers), this cannot hold. The left side $[b_j^s,a^\sigma]$ has parity $0+1=1$ and
$\kappa$ has parity 1, so $\mathrm{gb}$ must have parity 0.

We therefore take $\mathrm{gb}_{\sigma,j,s}\in\mathbf C$ and read "parity 1" as a statement about the
**deformation**: $(X,Y)\mapsto\gamma(X,Y)$ is an *odd* map. That is,
$p(\gamma(X,Y))=p(X)+p(Y)+1$, which is what the odd coboundary $\delta f$ also satisfies.

### 0.3 The algebra $\mathfrak g$
$\mathfrak g=C(n+1)$ is the span in $U(A)$ of the quadratic oscillator monomials. We use the
normal-ordered basis below (order: $\kappa<a^+<a^-<b^+_1<\dots<b^+_n<b^-_1<\dots<b^-_n$):

| part | basis | count |
|---|---|---|
| $\mathfrak{so}(2)$ | $a^+a^-$ | 1 |
| $\mathfrak{sp}(2n)$ | $b_k^+b_l^+\ (k\le l)$, $b_k^+b_l^-$, $b_k^-b_l^-\ (k\le l)$ | $2n^2+n$ |
| odd | $a^\sigma b_l^s$ | $4n$ |

This gives superdimension $(2n^2+n+1\,|\,4n)$, which matches `Cn1_definition.md`. Two quirks of that
file do not affect anything here:
- The simple generators carry factors $\tfrac12$ and $-\tfrac12$ that the root-vector list omits.
- $H_{n+1}$ includes the constant $-\tfrac12$.

Both differ from our basis only by rescaling or by scalars, and they span the same space modulo scalars.

### 0.4 Treatment of "adjoint representation / up to scalar"
This is the key interpretive point. The definition is
$[X,Y]_\gamma=[X,Y]_0+\kappa\,\gamma(X,Y)$, viewed as an abelian extension
$L=\mathfrak g\oplus\kappa\mathfrak g$ with $\kappa\mathfrak g$ the adjoint module.

When $[X,Y]$ is computed in $U(A)$, it can also contain **central** terms $c_0\cdot 1+c_1\cdot\kappa$.
Normal-ordering $b^-_kb^+_k=b^+_kb^-_k+1$ or $a^-a^+=1-a^+a^-$ produces constants. Such central elements
- act by zero in the adjoint representation ($\operatorname{ad}1=\operatorname{ad}\kappa=0$), and
- are not elements of $\mathfrak g$, since $\mathfrak g$ is simple and $\mathfrak g\cap\mathbf C1=0$.

So the statement "$\gamma=\delta f$ as an adjoint representation, up to scalar" means:

> $\gamma$ and $\delta f$ are compared as maps $\mathfrak g\otimes\mathfrak g\to\mathfrak g$, i.e. in
> $U(A)/(\mathbf C1\oplus\mathbf C\kappa)$. Equivalently, the $\kappa$-coefficient of the bracket is
> projected onto $\mathfrak g$ along the centre.

We also checked the two other readings:
* **"$\gamma=\lambda\,\delta f$ for some scalar $\lambda\neq0$."** This is equivalent, because $\delta$ is
  linear and we can replace $f$ by $\lambda f$. It changes nothing.
* **Exact equality in $U(A)$, central parts included.** The leftover central part $\kappa\cdot c(X,Y)$ of
  $\gamma$ is *itself* given by the same coboundary formula. It is evaluated with the scalar parts of
  $f$ and of the $U(A)$-brackets (Sec. 3, Remark). So it is a coboundary with trivial coefficients, and
  the deformation is trivial in this stronger sense as well. The computational artifacts verify this
  exactly (`central_part_equals_minus_s_of_bracket`).

---

## 1. Untwisting lemma

**Lemma 1.** For $\sigma\in\{+,-\}$ put
$$
\ell_\sigma:=\sum_{j=1}^n\bigl(\mathrm{gb}_{\sigma,j,-}\,b_j^+-\mathrm{gb}_{\sigma,j,+}\,b_j^-\bigr),
\qquad a'^\sigma:=a^\sigma+\kappa\,\ell_\sigma .
$$
Then $a'^\pm,b^\pm_k$ satisfy the **undeformed** relations:
$[b_j^s,a'^\sigma]=0$, $\{a'^-,a'^+\}=1$, $(a'^\pm)^2=0$.

*Proof.*
1. $[b_j^-,\ell_\sigma]=\mathrm{gb}_{\sigma,j,-}$ and $[b_j^+,\ell_\sigma]=-\mathrm{gb}_{\sigma,j,+}[b_j^+,b_j^-]=\mathrm{gb}_{\sigma,j,+}$.
   So $[b_j^s,\ell_\sigma]=\mathrm{gb}_{\sigma,j,s}$.
2. Since $b$ is even and commutes with $\kappa$,
   $[b_j^s,a'^\sigma]=-\mathrm{gb}_{\sigma,j,s}\kappa+\kappa\,\mathrm{gb}_{\sigma,j,s}=0$.
3. Next,
   $\{a^\sigma,\kappa\ell_\tau\}=-\kappa a^\sigma\ell_\tau+\kappa\ell_\tau a^\sigma=\kappa[\ell_\tau,a^\sigma]\in\kappa\cdot\mathbf C\kappa=0$.
   Also $\{\kappa\ell_\sigma,\kappa\ell_\tau\}\in\kappa^2U=0$.
4. Hence $\{a'^\sigma,a'^\tau\}=\{a^\sigma,a^\tau\}$. $\square$

So the assignment $a\mapsto a'$, $b\mapsto b$, $\kappa\mapsto\kappa$ defines an isomorphism
$\psi:U(A)_{\mathrm{gb}=0}\to U(A)_{\mathrm{gb}}$. The deformation of the oscillator algebra is
**removable by a change of generators**. Note that $\kappa a'^\sigma=\kappa a^\sigma$.

## 2. Generators in the untwisted variables

For a polynomial $X(a,b)$, write $X':=\psi(X)=X(a',b)$. Substituting $a^\sigma=a'^\sigma-\kappa\ell_\sigma$
and using $\kappa^2=0$ gives:

| $X$ | $X$ in terms of $X'$ |
|---|---|
| $b\,b$ | $X=X'$ |
| $a^\sigma b_l^s$ | $X=X'-\kappa\,\ell_\sigma b_l^s$ |
| $a^+a^-$ | $X=X'+\kappa\bigl(a^+\ell_--a^-\ell_+\bigr)$ |

Define the **odd** linear map $f_{\mathrm{gb}}:\mathfrak g\to\mathfrak g$ by

$$
\boxed{\;f(b\,b)=0,\qquad f(a^\sigma b_l^s)=-\ell_\sigma b_l^s,\qquad
f(a^+a^-)=a^+\ell_--a^-\ell_+\;}
$$

Here $\ell_\sigma b_l^s$ is quadratic in the bosons, so it lies in $\mathfrak{sp}(2n)$ modulo a scalar.
$a^\pm\ell_\mp$ is a combination of odd generators. So $f$ reverses parity, as
`C_coboundary_definition.md` §1 requires.

Writing $f^U(X)$ for the exact $U(A)$-element in the box and $s(X)\in\mathbf C$ for its scalar part, we
have $f^U(X)=f(X)+s(X)\cdot1$ and $X=\psi\bigl(X+\kappa f^U(X)\bigr)$ for all $X\in\mathfrak g$.

## 3. Main theorem

**Theorem.** For every $n\ge1$ and every $\mathrm{gb}\in\mathbf C^{4n}$, the inhomogeneous deformation is
trivial:
$$
\gamma_{\mathrm{gb}}(X,Y)=(\delta f_{\mathrm{gb}})(X,Y)\quad\text{for all }X,Y\in\mathfrak g,\ \text{modulo scalars}.
$$
So the necessary and sufficient condition for triviality is **empty**: every $\mathrm{gb}$, zero or not,
is trivial.

*Proof.* Since $\psi$ is an algebra isomorphism, we can compute brackets in the $\mathrm{gb}=0$ algebra.
Bracket $X+\kappa f^UX$ with $Y+\kappa f^UY$ and drop $\kappa^2$:

$$
[X+\kappa f^UX,\;Y+\kappa f^UY]=[X,Y]+[X,\kappa f^UY]+[\kappa f^UX,Y].
$$

The middle and last terms simplify as follows:
* $[X,\kappa Z]=(-1)^{p(X)}\kappa[X,Z]$, because $\kappa$ is odd and supercentral.
* $[\kappa Z,Y]=-(-1)^{(p(X)+1)p(Y)}\kappa[Y,Z]$ for $Z=f^UX$, whose parity is $p(X)+1$.

The undeformed bracket is $[X,Y]_0=\sum_k c_kZ_k+c_0$. Applying $\psi$ gives
$\sum_kc_kZ_k-\kappa\sum_kc_kf^U(Z_k)+c_0$. Since $\psi$ maps $[X,Y]_0$ in the undeformed algebra to the
bracket of the images, we get, in $U(A)_{\mathrm{gb}}$:

$$
[X,Y]_{\mathrm{gb}}=[X,Y]_0+\kappa\Bigl((-1)^{p(X)}[X,f^UY]-(-1)^{(p(X)+1)p(Y)}[Y,f^UX]-f^U([X,Y]_0)\Bigr).
$$

Modulo scalars, the scalar parts of $f^U$ drop out of the two brackets (central elements bracket to zero)
and $f^U\equiv f$. This is exactly
$\gamma_{\mathrm{gb}}=\delta f_{\mathrm{gb}}$ with the formula in `C_coboundary_definition.md` §2. $\square$

**Remark (consistency of the coboundary formula).** For an odd $f$, the given $\delta f$ is the
Chevalley–Eilenberg differential of the even cochain $X\mapsto\kappa f(X)$ with values in the
$\mathfrak g$-module $\kappa\mathfrak g$, where $X\cdot\kappa Z=(-1)^{p(X)}\kappa[X,Z]$. This explains
the signs $(-1)^{p(X)}$ and $(-1)^{(p(X)+1)p(Y)}$. One also checks from super-Jacobi that
$\delta(\operatorname{ad}_Z)=0$ for odd $Z$.

**Remark (central part).** The proof also identifies the $\kappa\cdot1$ part of $\gamma$: it equals the
scalar part of
$(-1)^{p(X)}[X,f^UY]-(-1)^{(p(X)+1)p(Y)}[Y,f^UX]-s([X,Y]_0)$.
This is the coboundary of $(X\mapsto f^U(X))$ read off in the scalar component. So even without passing
to the adjoint quotient, the scalar part is accounted for by the same $f$.

**Uniqueness.** The odd map $f$ is unique up to $\ker\delta|_{\text{odd}}$, which is the space of odd
derivations. It contains the odd inner derivations $\operatorname{ad}(\mathfrak g_{\bar1})$, which have
dimension $4n$. The computed kernel dimension is exactly $4n$ (table below). So for $n=1,2,3$ every odd
derivation is inner, and $f_{\mathrm{gb}}$ is unique modulo $\operatorname{ad}(\mathfrak g_{\bar 1})$.

**Non-vanishing.** $\gamma_{\mathrm{gb}}\neq0$ whenever $\mathrm{gb}\neq0$: the linear map
$\mathrm{gb}\mapsto\gamma_{\mathrm{gb}}$ has full rank $4n$. So the result is not vacuous. Every one of
the $4n$ independent nonzero deformations is a genuine nonzero cocycle that is nonetheless a coboundary.
This answers the issue's question "can any non-zero configuration satisfy $\gamma_{\mathrm{gb}}=\delta f$?":
**yes, all of them.**

**Example ($n=1$, $\mathrm{gb}_{+,1,+}=1$, others $0$).**
- $\ell_+=-b_1^-$ and $\ell_-=0$.
- So $f(a^+b_1^+)=b_1^-b_1^+=b_1^+b_1^-+1$ (scalar part $1$, dropped modulo scalars),
  $f(a^+b_1^-)=b_1^-b_1^-$, $f(a^+a^-)=a^-b_1^-$, and $f=0$ on the rest.
- One nonzero component is $\gamma(a^+a^-,\,b_1^+b_1^+)=2\,a^-b_1^+$, which equals $\delta f$ there.
- The full table is in `verification/artifacts/cn1_n1.json` under `configs["unit_gb[+,1,+]"]`.

---

## 4. Computational verification ($n=1,2,3$)

Script: `verification/cn1_triviality.py` (pure Python with `fractions.Fraction`; NumPy is used only for
ranks). Run it with `python3 verification/cn1_triviality.py`; it takes about 10 s.

What the script does:
1. **Model.** It implements $U(A)$ symbolically, with normal ordering by the super-commutation rules of
   §0.1 and $\kappa^2=0$, for an arbitrary rational $\mathrm{gb}$.
2. **Structure of $\mathfrak g$.** It computes the structure constants of $\mathfrak g$ modulo scalars,
   checks closure, and checks super-Jacobi on all triples.
3. **$\gamma$ from the definition.** For each test configuration it computes $\gamma_{\mathrm{gb}}(Z_i,Z_j)$
   for all basis pairs directly from the deformed oscillator relations. It does not use Lemma 1. It also
   asserts that the $\kappa$-free part equals the undeformed bracket.
4. **Exact test.** It checks $\gamma_{\mathrm{gb}}=\delta f_{\mathrm{gb}}$ exactly, using the closed-form
   $f_{\mathrm{gb}}$ from §2 and the abstract structure constants. It checks the central part exactly
   too.
5. **Independent test.** It builds the full linear map $\phi\mapsto\delta f$ on all odd maps and checks by
   least squares that $\gamma_{\mathrm{gb}}\in\operatorname{im}\delta$. This does not rely on the
   closed-form $f$.

Test configurations: all $4n$ unit vectors, which suffice by linearity, plus one random rational vector.

| $n$ | algebra | dims | Jacobi | #odd $\phi$ | rank $\delta$ | $\ker\delta$ | #gb | rank(gb→γ) | $\gamma=\delta f$ (exact) | central part | max lstsq residual |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | osp(2\|2) | 4\|4 | ✓ | 32 | 28 | 4 | 4 | 4 | ✓ all | ✓ | 6.7e-14 |
| 2 | osp(2\|4) | 11\|8 | ✓ | 176 | 168 | 8 | 8 | 8 | ✓ all | ✓ | 1.8e-13 |
| 3 | osp(2\|6) | 22\|12 | ✓ | 528 | 516 | 12 | 12 | 12 | ✓ all | ✓ | 4.3e-13 |

### Structured artifacts (for future verification)
`verification/artifacts/cn1_n{1,2,3}.json` contains:
- `basis`: index, monomial, parity.
- `structure_constants`: `"i,j" -> {k: c}`, so that $[Z_i,Z_j]=\sum c\,Z_k$ modulo scalars.
- `delta_on_odd_maps`: rank and kernel data.
- `rank_of_gb_to_gamma_map`.
- `configs[<name>]`, with:
  - `gb`: the parameters.
  - `gamma`: `"i,j" -> {k: c}`.
  - `gamma_central_kappa_part`.
  - `explicit_f`: `"j" -> {i: c}`, so that $f(Z_j)=\sum_i\phi_{ij}Z_i$.
  - `explicit_f_scalar_parts`.
  - Booleans for the exact checks and the least-squares residual.

`verification/artifacts/summary.json` aggregates the table above. All rational numbers are stored as
exact strings.

---

## 5. Conclusion

For $C(n+1)=\mathfrak{osp}(2|2n)$ realized by oscillators in $U(A)$, the inhomogeneous deformation
$[b_j^s,a_1^\sigma]=-\mathrm{gb}_{\sigma,j,s}\kappa$ is **trivial for every choice of the $4n$ parameters**.
The trivializing odd map is
$$
f_{\mathrm{gb}}(a^\sigma b_l^s)=-\ell_\sigma b_l^s,\quad f_{\mathrm{gb}}(a^+a^-)=a^+\ell_--a^-\ell_+,\quad
f_{\mathrm{gb}}|_{\mathfrak{sp}(2n)}=0,\qquad
\ell_\sigma=\sum_j(\mathrm{gb}_{\sigma,j,-}b_j^+-\mathrm{gb}_{\sigma,j,+}b_j^-).
$$
It is unique modulo odd inner derivations. Conceptually, the whole deformation is the change of odd
generators $a^\sigma\mapsto a^\sigma+\kappa\ell_\sigma$, so its class in $H^2(\mathfrak g;\kappa\mathfrak g)$
vanishes. The "up to scalar" clause is needed only because $U(A)$-brackets carry central constants, which
the adjoint representation does not see. Even those constants are accounted for by the same $f$.
The proof holds for all $n$. For $n=1,2,3$ it was also checked with exact arithmetic, independently of
the proof.
