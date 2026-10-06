# Triviality of the Inhomogeneous Deformation of $C(n+1)=\mathfrak{osp}(2|2n)$

**Sources used**: only `docs/math/Cn1_definition.md`, `docs/math/C_inhomogeneous_definition.md`, and
`docs/math/C_coboundary_definition.md`. No external literature or web access was used.
**Artifacts**: `verification/osp_deformation.py` (exact engine and checks) and `verification/artifacts/*.json`
(structured data).

---

## 0. Main result

> **Theorem.** Let $n\ge 1$ and let $\mathrm{gb}=(\mathrm{gb}_{\sigma,j,s})\in\mathbf C^{4n}$ be arbitrary.
>
> 1. **(Triviality.)** The inhomogeneous deformation $\gamma_{\mathrm{gb}}$ is a coboundary:
>    $\gamma_{\mathrm{gb}}=\delta h_{\mathrm{gb}}$, where $h_{\mathrm{gb}}$ is the explicit odd map given in §3.
>    This holds both up to scalars (adjoint module $\mathfrak g$) and exactly in
>    $\hat{\mathfrak g}=\mathfrak g\oplus\mathbf C1$.
> 2. **(Non-vanishing.)** $\gamma_{\mathrm{gb}}=0$ as a cochain iff $\mathrm{gb}=0$. The map
>    $\mathrm{gb}\mapsto\gamma_{\mathrm{gb}}$ is injective.
> 3. **(Uniqueness.)** For $n=1,2,3$ the odd maps $f$ with $\delta f=\gamma_{\mathrm{gb}}$ are exactly
>    $f=h_{\mathrm{gb}}+\operatorname{ad}Q$ with $Q\in\mathfrak g_{\bar 1}$. This was verified by computer:
>    the space of odd 1-cocycles has dimension $4n=\dim\mathfrak g_{\bar1}$ and is spanned by the odd inner maps.
>
> **The triviality condition on gb is therefore vacuous.** Every configuration, zero or non-zero, gives a
> trivial deformation. Every non-zero configuration gives a *non-zero but cohomologically trivial* 2-cocycle.
> So the answer to the issue's question "can a non-zero gb satisfy $\gamma_{\mathrm{gb}}=\delta f$?" is
> **yes, all of them do**.

The conceptual reason is that the deformation can be removed by a change of oscillator variables.
The mixed (even × odd) part of the pre-oscillator form is always absorbable, because the even (symplectic)
part of the form is non-degenerate:
$$a'^{\sigma}=a^{\sigma}+\kappa\,u^{\sigma},\qquad [b^s_j,a'^{\sigma}]=0 .$$

---

## 1. Setting and conventions

* $V_{\bar0}=\operatorname{span}\{b_k^\pm\}$ and $V_{\bar1}=\operatorname{span}\{a^\pm\}$, with $a=a_1$.
  $A=V\oplus\mathbf CK\oplus\mathbf C\kappa$, where $K$ is even central and $\kappa$ is odd central. We put $K=1$.
  The only non-zero brackets of generators are
  $$[b_k^-,b_l^+]=\delta_{kl},\quad \{a^-,a^+\}=1,\quad [b_j^s,a^\sigma]=-\mathrm{gb}_{\sigma,j,s}\,\kappa .$$
  $A$ is a Lie superalgebra for every gb, because all brackets are central and Jacobi holds trivially.
  Write $\mathcal U_{\mathrm{gb}}=\mathcal U(A_{\mathrm{gb}})/(K-1)$.
* **$\kappa^2=0$.** $\kappa$ is odd, so $\kappa^2=\tfrac12[\kappa,\kappa]=0$. Therefore every deformation
  effect is exactly first order and linear in gb.
* **PBW.** Fix the order $\kappa<a^+<a^-<b_1^+<b_1^-<\dots$. Normal-ordered words form a basis of
  $\mathcal U_{\mathrm{gb}}$ for every gb. This identifies all $\mathcal U_{\mathrm{gb}}$ with $\mathcal U_0$ as vector spaces.
* **$\mathfrak g=C(n+1)$** is the span of the normal-ordered quadratic words in $a,b$:
  * $a^+a^-$ (the $\mathfrak{so}(2)$ part);
  * the $2n^2+n$ words $b\,b$ (the $\mathfrak{sp}(2n)$ part);
  * the $4n$ odd words $a^\sigma b_k^s$ (root $\pm\varepsilon\pm\delta_k$).

  This gives superdimension $(2n^2+n+1\,|\,4n)$, matching `Cn1_definition.md`. Chevalley elements such as
  $H_{n+1}=-b_n^+b_n^--\tfrac12$ differ from these words only by scalars.
* **Definition of $\gamma$.** Following `C_inhomogeneous_definition.md`, compute the super-commutator of two
  basis words in $\mathcal U_{\mathrm{gb}}$ and normal-order it:
  $[X,Y]_{\mathrm{gb}}=[X,Y]_0+\kappa\,\gamma_{\mathrm{gb}}(X,Y)$, with $\kappa$ on the left.
  The engine verifies three facts about this decomposition:
  * the $\kappa$-free part equals the undeformed bracket;
  * $\gamma_{\mathrm{gb}}(X,Y)\in\mathcal U_{\le2}=\mathfrak g\oplus\mathbf C1$, so no degree-1 terms occur;
  * $p(\gamma(X,Y))=p(X)+p(Y)+1$, so $\gamma$ is an **odd** cochain, consistent with an odd $f$.
* **Coboundary** (`C_coboundary_definition.md`):
  $(\delta f)(X,Y)=(-1)^{p(X)}[X,fY]-(-1)^{(p(X)+1)p(Y)}[Y,fX]-f([X,Y])$.
  This sign convention is exactly the first-order term of $[X+\kappa fX,\;Y+\kappa fY]$, because
  $[X,\kappa Z]=(-1)^{p(X)}\kappa[X,Z]$ and $[\kappa Z,Y]=-(-1)^{(p(Z))p(Y)}\kappa[Y,Z]$ with $p(Z)=p(X)+1$.
  So "$\gamma=\delta f$" is literally the statement that $\Psi=\mathrm{id}+\kappa f$ intertwines the deformed
  and undeformed brackets.

### On the parity of gb

`C_inhomogeneous_definition.md` says that gb "must have parity 1". In $[b_j^s,a^\sigma]=-\mathrm{gb}\,\kappa$
the left side is odd and $\kappa$ is odd, so gb must be an **even scalar** (a complex number). If gb were
Grassmann-odd, $\mathrm{gb}\,\kappa$ would be even and the relation would be inconsistent.

I therefore read "parity 1" as "gb lives in the odd (mixed-parity) block of the pre-oscillator form and
multiplies the odd central $\kappa$". All constructions below are linear in gb. They therefore remain valid
verbatim over any supercommutative coefficient ring in which the gb are even.

---

## 2. Handling "adjoint representation / up to scalar"

Scalars enter the problem in three independent places:

1. **$\mathfrak g$ is not closed in $\mathcal U$.** The bracket satisfies $[\mathfrak g,\mathfrak g]\subset\mathfrak g\oplus\mathbf C1$.
   For example, $[b_1^+b_1^+,\,b_1^-b_1^-]=-4\,b_1^+b_1^--2$.
   The honest Lie superalgebra inside $\mathcal U$ is $\hat{\mathfrak g}=\mathfrak g\oplus\mathbf C1$, and $\mathbf C1$ is a
   central ideal. $\hat{\mathfrak g}$ acts on $\mathcal U_{\le2}=\hat{\mathfrak g}$ by the adjoint action, with $\mathbf C1$ a trivial
   submodule, and $\mathcal U_{\le2}/\mathbf C1\cong\mathfrak g$ is the **adjoint module**.
   This is the meaning of "$\gamma=\delta f$ as an adjoint representation".
2. **$\gamma$ itself has scalar components.** For $n=1$ and $\mathrm{gb}_{+,1,+}=1$ the artifact shows
   $\gamma(a^+b_1^+,\;b_1^+b_1^-)=b_1^+b_1^-+1$.
3. **Word-ordering ambiguity.** In $\mathcal U_{\mathrm{gb}}$ we have $b\,a=a\,b-\mathrm{gb}\,\kappa$. Writing an odd
   generator as $ba$ instead of $ab$ changes it by a $\kappa$-multiple of a scalar.

I treated the condition in two ways and proved the theorem in both:

* **Reading A ("up to scalar").** Values are taken in $\mathcal U_{\le2}/\mathbf C1\cong\mathfrak g$ (the adjoint module), and
  $f:\mathfrak g\to\mathfrak g$. All three scalar effects above are quotiented out. The theorem is then independent of
  word ordering and of the scalar shifts in the Chevalley basis.
* **Reading B (strict).** Work in $\hat{\mathfrak g}=\mathfrak g\oplus\mathbf C1$ with $f:\hat{\mathfrak g}\to\hat{\mathfrak g}$ odd and $f(1)=0$.
  With the normal-ordered basis words fixed, $\gamma=\delta h$ holds **exactly, scalars included**.

Reading A is the one prescribed by `C_coboundary_definition.md`. Reading B shows that the quotient is not
what makes the result true. The scalars are only needed so that the problem is well posed on $\mathfrak g$
itself.

---

## 3. Proof

**Step 1 (absorbing vector).** For $\sigma\in\{+,-\}$ set
$$u^{\sigma}=\sum_{j=1}^n\big(\mathrm{gb}_{\sigma,j,-}\,b_j^+-\mathrm{gb}_{\sigma,j,+}\,b_j^-\big)\in V_{\bar0}.$$
Then $[b_j^-,u^\sigma]=\mathrm{gb}_{\sigma,j,-}$ and $[b_j^+,u^\sigma]=\mathrm{gb}_{\sigma,j,+}$, i.e.
$[b_j^s,u^\sigma]=\mathrm{gb}_{\sigma,j,s}$. The vector $u^\sigma$ exists and is unique because the symplectic form
on $V_{\bar0}$ is non-degenerate.

**Step 2 (change of variables).** Put $a'^\sigma=a^\sigma+\kappa u^\sigma$, which is odd. In $\mathcal U_{\mathrm{gb}}$:

* $[b_j^s,a'^\sigma]=-\mathrm{gb}_{\sigma,j,s}\kappa+\kappa[b_j^s,u^\sigma]=0$.
* $\{a'^\sigma,a'^\tau\}=\{a^\sigma,a^\tau\}+\kappa\cdot(\text{multiples of }\kappa)=\{a^\sigma,a^\tau\}$, because
  $\kappa^2=0$ and $\kappa$ is central.
* $\kappa$ is still central and $[b,b]$ is unchanged.

So $(a'^\pm,b^\pm,\kappa)$ satisfy the **undeformed** relations. This gives an algebra map
$\Theta:\mathcal U_0\to\mathcal U_{\mathrm{gb}}$ with $a\mapsto a'$, $b\mapsto b$, $\kappa\mapsto\kappa$.
Since $\kappa^2=0$, it satisfies $\kappa\,\Theta(W)=\kappa W$ for every word $W$.

**Step 3 (the map $h$).** Substitute $a=a'-\kappa u$ into each basis word, using $\kappa^2=0$, $a'\kappa=-\kappa a'$,
and $[u,a']=0$:
$$
a^\sigma b=\Theta(a^\sigma b)+\kappa\,h(a^\sigma b),\qquad
a^+a^-=\Theta(a^+a^-)+\kappa\,h(a^+a^-),\qquad bb'=\Theta(bb'),
$$
where
$$
\boxed{\;h(a^\sigma b_k^s)=-u^\sigma b_k^s,\qquad h(a^+a^-)=a^+u^--a^-u^+,\qquad h(b\,b')=0,\qquad h(1)=0.\;}
$$
$h$ is odd, linear in gb, and takes values in $\hat{\mathfrak g}$. Modulo scalars it takes values in $\mathfrak g$.

**Step 4 ($\gamma=\delta h$).** Take basis words $X,Y$. Using Step 3 and $\kappa^2=0$,
$$
[X,Y]_{\mathrm{gb}}=\Theta([X,Y]_0)+\kappa\Big((-1)^{p(X)}[X,hY]_0-(-1)^{(p(X)+1)p(Y)}[Y,hX]_0\Big).
$$
Write $[X,Y]_0=\sum_Z c_Z Z+c_0$ in normal-ordered words. Then
$\Theta([X,Y]_0)=\sum c_ZZ+c_0-\kappa\,h([X,Y]_0)$, and therefore
$$
[X,Y]_{\mathrm{gb}}=[X,Y]_0+\kappa\,(\delta h)(X,Y),\qquad\text{i.e.}\qquad \gamma_{\mathrm{gb}}=\delta h_{\mathrm{gb}}
$$
exactly in $\hat{\mathfrak g}$ (Reading B), and hence also modulo $\mathbf C1$ (Reading A). $\square$ This proves part (1) for all $n$.

**Step 5 (non-vanishing; part 2).** In $[b_j^sb_j^s,\;a^\sigma b_k^t]$ the only $\kappa$-contractions are between
$b_j^s$ and $a^\sigma$. This gives
$$
\gamma_{\mathrm{gb}}(b_j^sb_j^s,\;a^\sigma b_k^t)\equiv-2\,\mathrm{gb}_{\sigma,j,s}\,b_j^s b_k^t\pmod{\mathbf C1}.
$$
For $n=1$ and $\mathrm{gb}_{+,1,+}=1$ the artifact gives $\gamma(b_1^+b_1^+,a^+b_1^+)=-2\,b_1^+b_1^+$, as predicted.
So if any $\mathrm{gb}_{\sigma,j,s}\neq0$ then $\gamma_{\mathrm{gb}}\neq0$. Equivalently, $h_{\mathrm{gb}}$ is not a cocycle.
A cocycle of the form $\operatorname{ad}Q$ that vanishes on $\mathfrak{sp}(2n)$ must have
$Q\in(\mathfrak g_{\bar1})^{\mathfrak{sp}(2n)}=(\mathbf C^2\otimes\mathbf C^{2n})^{\mathfrak{sp}(2n)}=0$.
Numerically, the rank of $\{\gamma_p\}_{p}$ is $4n$ for $n=1,2,3$. $\square$

**Step 6 (uniqueness; part 3).** $f$ is determined up to odd 1-cocycles. By construction,
$\operatorname{ad}Q$ for odd $Q$ is a cocycle: it is the first-order part of the inner automorphism
$\exp\operatorname{ad}(\kappa Q)$, and $\kappa Q$ is even. The computation shows these maps exhaust the cocycles
for $n=1,2,3$, i.e. $H^1(\mathfrak g,\mathfrak g)_{\bar1}=0$ there. So the trivialising $f$ is unique modulo odd inner
derivations.

---

## 4. Computational verification (n = 1, 2, 3)

Reproduce with `python3 verification/osp_deformation.py` (about 3 s). The script uses exact rational
arithmetic for the algebra and for the $\gamma=\delta h$ identities, and numpy ranks for dimension counts.

| | $C(2)$, n=1 | $C(3)$, n=2 | $C(4)$, n=3 |
|---|---|---|---|
| sdim $\mathfrak g$ (computed) | 4\|4 | 11\|8 | 22\|12 |
| super-Jacobi violation of computed structure constants | 0 | 0 | 0 |
| exact $\gamma_p=\delta h_p$ mod scalars, all $4n$ unit gb | ✔ | ✔ | ✔ |
| exact $\gamma_p=\delta h_p$ incl. scalars ($\hat{\mathfrak g}$), all unit gb | ✔ | ✔ | ✔ |
| unknowns of odd $f$ (Reading A) | 32 | 176 | 528 |
| rank $\delta$ on odd 1-cochains (A / B) | 28 / 36 | 168 / 184 | 516 / 540 |
| dim odd 1-cocycles = rank of $\{\operatorname{ad}Q\}_{Q\in\mathfrak g_{\bar1}}$ | 4 | 8 | 12 |
| rank $\{\gamma_p\}$ (injectivity of gb ↦ γ) | 4 | 8 | 12 |
| rank $[\delta\,|\,\gamma\text{-family}]$ = rank $\delta$ (every γ is a coboundary, solved **without** using $h$) | ✔ | ✔ | ✔ |
| least-squares residual for random gb | 1e-14 | 1e-13 | 2e-13 |
| **negative control**: random odd cochain raises the rank (test can fail) | ✔ | ✔ | ✔ |

Because $\gamma$ is linear in gb ($\kappa^2=0$), checking the $4n$ unit vectors proves the claim for every
$\mathrm{gb}\in\mathbf C^{4n}$. The random-gb solve is an extra consistency check.

### Structured data (connectivity)

`verification/artifacts/C{n+1}_n{n}.json` contains, for each $n$:

* `basis`: index, oscillator word, parity, and root vector in the basis $(\varepsilon,\delta_1,\dots,\delta_n)$;
* `structure_constants`: `"i,j" -> {k: coeff, "const": coeff}`;
* `gamma_per_unit_gb`: $\gamma_p$ for each of the $4n$ parameters, in the same sparse format.
  The general $\gamma_{\mathrm{gb}}$ is $\sum_p \mathrm{gb}_p\,\gamma_p$;
* `trivialising_map_h_per_unit_gb`: $h_p(Z_j)$;
* `exact_checks`, `numerical_checks`: the flags in the table above.

`verification/artifacts/summary.json` aggregates the checks. Coefficients are exact rationals stored as strings.

Example from `C2_n1.json` with $\mathrm{gb}_{+,1,+}=1$, so $u^+=-b_1^-$ and $u^-=0$:
$h(a^+b_1^+)=b_1^-b_1^+=b_1^+b_1^-+1$, $h(a^+b_1^-)=b_1^-b_1^-$, $h(a^+a^-)=a^-b_1^-$, and $h=0$ elsewhere.

---

## 5. Conclusion

For $C(n+1)=\mathfrak{osp}(2|2n)$ in the oscillator realisation, the inhomogeneous deformation
$\gamma_{\mathrm{gb}}$ is **trivial for every choice of the $4n$ parameters $\mathrm{gb}_{\sigma,j,s}$**. The necessary and
sufficient condition for triviality is empty.

The trivialising odd map is $h_{\mathrm{gb}}$ from §3. It is unique modulo $\operatorname{ad}(\mathfrak g_{\bar1})$, which was
verified for $n\le3$. Whenever $\mathrm{gb}\ne0$, $\gamma_{\mathrm{gb}}$ is a non-zero coboundary.

This holds both in the "adjoint representation / up to scalar" sense prescribed by the definitions and in the
strict sense on $\hat{\mathfrak g}=\mathfrak g\oplus\mathbf C1$. Structurally, the gb-deformation is the change of variables
$a\mapsto a+\kappa u$, made possible by the non-degeneracy of the bosonic symplectic form.

*Remark on the source documents.* `Cn1_definition.md` normalises $E_{\pm2\delta_n}$ as $\tfrac12(b_n^\pm)^2$ in one
table and $(b_k^\pm)^2$ in another. This is a normalisation difference only and does not affect any result,
because triviality is basis-independent.
