# Triviality of the Inhomogeneous (gb) Deformation of $C(n+1)=\mathfrak{osp}(2|2n)$

**Branch**: `study/thm01-R-opus55-b01-C` **Model**: Claude Opus 5.5 **Date**: 2026-10-06
**Sources used**: only `docs/math/Cn1_definition.md`, `docs/math/C_inhomogeneous_definition.md`,
`docs/math/C_coboundary_definition.md`, `docs/issues/issue_open.md`. I did not access any external
papers or the web, and I did not read any files outside the repository.

---

## 0. Startup verification

| File | Present | Note |
|---|---|---|
| `docs/math/Cn1_definition.md` | yes | root system, oscillator realisation, B(0,n) comparison. **No JSON schema information.** |
| `docs/math/C_inhomogeneous_definition.md` | yes | pre-oscillator form, $[b_j^s,a_1^\sigma]=-\mathrm{gb}_{\sigma,j,s}\kappa$ |
| `docs/math/C_coboundary_definition.md` | yes | $\delta f$ for odd $f$, triviality "as adjoint representation … up to scalar" |
| `docs/issues/issue_open.md` | yes | the task |
| `final_reflection_template.md` | yes | template |
| `supplementary_metrics_template.md` | yes | template |

---

## 1. Main result

> **Theorem.** Let $n\ge 1$. For **every** choice of the $4n$ parameters
> $\mathrm{gb}=(\mathrm{gb}_{\sigma,j,s})\in\mathbf C^{4n}$, the inhomogeneous deformation
> $\gamma_{\mathrm{gb}}$ of $C(n+1)=\mathfrak{osp}(2|2n)$ is **trivial**. Explicitly,
> $\gamma_{\mathrm{gb}}=\delta f_{\mathrm{gb}}$ (in the adjoint representation, i.e. up to scalars), where $f_{\mathrm{gb}}$ is the odd map given in
> closed form in §4.
>
> So the necessary and sufficient condition for triviality is **empty**: it holds
> for all $\mathrm{gb}$. Non-zero configurations are trivial too, even though
> $\gamma_{\mathrm{gb}}\neq 0$ for every $\mathrm{gb}\neq 0$ (the map $\mathrm{gb}\mapsto\gamma_{\mathrm{gb}}$ is injective).
> $f_{\mathrm{gb}}$ is unique up to adding an element of $\ker\delta$ (on odd maps),
> which has dimension $4n=\dim\mathfrak g_{\bar 1}$.

Conceptually, the gb couplings are a change of basis of the oscillators. In the deformed
algebra, the shifted bosons $b'=b+\kappa\,\ell(b)$ satisfy the *undeformed* CCR/CAR together with $a^\pm$.
Rewriting every generator of $C(n+1)$ in terms of $(a^\pm,b')$ is exactly the change of basis
$X\mapsto X+\kappa\varphi(X)$ that trivialises $\gamma_{\mathrm{gb}}$.

The proof (§3) is uniform in $n$. The exact computer verification (§5) covers $n=1,2,3$.

---

## 2. Set-up, conventions, and how the ambiguous points are handled

### 2.1 The ambient algebra
$A=V\oplus\mathbf CK\oplus\mathbf C\kappa$ with $V_{\bar0}=\mathrm{span}\{b_j^\pm\}$ and $V_{\bar1}=\mathrm{span}\{a_1^\pm\}$ (written $a^\pm$).
I set $K=1$ in $\mathcal U(A)$, consistent with the CCR/CAR of `Cn1_definition.md`. The brackets are

$$[b_k^-,b_l^+]=\delta_{kl},\quad \{a^-,a^+\}=1,\quad \{a^\pm,a^\pm\}=0,\quad
[b_j^s,a^\sigma]=-\mathrm{gb}_{\sigma,j,s}\,\kappa,\quad \kappa \text{ central}.$$

**Key fact: $\kappa^2=0$.** $\kappa$ is odd, so $\kappa^2=\tfrac12[\kappa,\kappa]=0$ because $\kappa$ is central.
Consequently every computation is exactly first order in $\kappa$, and $\gamma_{\mathrm{gb}}$ is exactly
**linear** in gb. Terms of the form $\mathrm{gb}\cdot\mathrm{gb}'$ always carry $\kappa^2=0$.

### 2.2 Parity of gb
`C_inhomogeneous_definition.md` says gb "must have parity 1". I read this as follows: the
coupling term $\mathrm{gb}\cdot\kappa$ is the parity-1 piece, since it equals $[b,a]$, which is odd.
The odd degree is carried by $\kappa$, and the coefficients $\mathrm{gb}_{\sigma,j,s}$ are treated as ordinary complex numbers.

If the gb were themselves Grassmann-odd, $\mathrm{gb}\,\kappa$ would be even and could not equal the odd element $[b,a]$.
So this is the only parity-consistent reading. Nothing in the proof uses any property of the gb values.

### 2.3 Placement of κ
I write $[X,Y]_{\mathrm{gb}}=[X,Y]_0+\kappa\,\gamma(X,Y)$ with $\kappa$ on the **left**. Since $\kappa$ is odd,
$\gamma$ is then an odd bilinear map: $p(\gamma(X,Y))=p(X)+p(Y)+1$.

This convention is the one for which the given formula
$(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y])$ is the natural
coboundary. Lemma 3 shows that the signs $(-1)^{p(X)}$ and $(-1)^{(p(X)+1)p(Y)}$ come precisely from moving $\kappa$ to the left.

### 2.4 "As an adjoint representation / up to scalar"
In the oscillator realisation, $\mathfrak g$ is spanned by quadratic elements of $\mathcal U(A)$.
Their brackets close only modulo central constants: for instance $H_{n+1}=-b_n^+b_n^--\tfrac12$, and $[X,Y]$ can produce $c\cdot1$.

With the deformation switched on, $\gamma_{\mathrm{gb}}(X,Y)$ can likewise contain a **scalar** term, i.e. $\kappa\cdot c$.
This comes from a double contraction (one $b$–$a$ contraction, which gives $\kappa$, and one $b$–$b$ contraction, which gives $1$).
For example, at $n=1$ with $\mathrm{gb}_{+,1,+}=1$:

$$[\,b_1^+b_1^-,\ a^+b_1^+\,]\ \ni\ -\kappa\cdot 1 .$$

These terms occur in $2n$ or $2n+2$ ordered pairs per unit gb, depending on the parameter (recorded in the artifacts).

I handle this as follows:

* **Official statement (the definition in `C_coboundary_definition.md`).** $\mathfrak g$ is the quadratic span modulo
  $\mathbf C\cdot 1$. This quotient is precisely what the adjoint representation detects, because $\mathrm{ad}(c\cdot 1)=0$ and $\mathfrak{osp}(2|2n)$ has trivial
  centre, so $\mathfrak g\cong\mathrm{ad}(\mathfrak g)$. Here $f:\mathfrak g\to\mathfrak g$ and the equality
  $\gamma_{\mathrm{gb}}=\delta f$ is required in $\mathfrak g$, i.e. **up to scalar**. This is the triviality notion of the Theorem.
* **Stronger statement (also proved and verified).** If one does *not* quotient by scalars and works with the central
  extension inside $\mathcal U(A)$, the identity still holds **exactly**, scalars included. One only has to allow $f$ to
  take values in $\mathfrak g\oplus\mathbf C\cdot1$ (with $f(1)=0$). The scalar part of $f$ is the scalar part of
  $-\varphi$ in Lemma 2. So "up to scalar" is a harmless normalisation, not an obstruction.

### 2.5 Basis of g
The basis used is the normal-ordered quadratic monomials, with order $a^+<a^-<b_1^+<b_1^-<\dots<b_n^-$:

* even: $a^+a^-$ (the $\mathfrak{so}(2)$ generator, up to scalar), and $b_k^sb_l^t$ for $(k,s)\le(l,t)$ ($\mathfrak{sp}(2n)$, $n(2n+1)$ elements);
* odd: $a^\sigma b_k^s$ ($4n$ elements).

The superdimension is $(2n^2+n+1\,|\,4n)$, matching `Cn1_definition.md` (verified: $4|4$, $11|8$, $22|12$). The root vectors of
`Cn1_definition.md` are, up to scalars and normalisation, elements of this basis. Since triviality is a basis-independent
statement, the choice of normalisation is irrelevant.

---

## 3. Proof

**Lemma 1 (absorbing gb into the oscillators).** In the deformed $\mathcal U(A)$, put

$$\ell(b_j^s):=\mathrm{gb}_{-,j,s}\,a^+ + \mathrm{gb}_{+,j,s}\,a^-,\qquad b_j'^{\,s}:=b_j^s+\kappa\,\ell(b_j^s),\qquad a'^{\,\sigma}:=a^\sigma.$$

Then $(a'^\pm,b'^\pm_j)$ satisfy the **undeformed** relations.

*Proof.* $\kappa a^\tau$ is even, so $[\kappa a^\tau,a^\sigma]=\kappa a^\tau a^\sigma-a^\sigma\kappa a^\tau=\kappa\{a^\tau,a^\sigma\}$. Hence

$$[b_j'^{\,s},a^+]=-\mathrm{gb}_{+,j,s}\kappa+\mathrm{gb}_{+,j,s}\kappa\{a^-,a^+\}=0,\qquad
[b_j'^{\,s},a^-]=-\mathrm{gb}_{-,j,s}\kappa+\mathrm{gb}_{-,j,s}\kappa\{a^+,a^-\}=0.$$

Also $[b_j'^{\,s},b_k'^{\,t}]=[b_j^s,b_k^t]+\kappa(\cdots)[\,\cdot\,,\,\cdot\,]$, where every correction term is proportional to $\kappa\cdot\mathrm{gb}\,\kappa=0$.
Finally, $[a',a']=[a,a]$. ∎

**Lemma 2 (the induced change of basis).** For a basis element $X=X(a,b)$, let $X':=X(a',b')$, computed in the deformed algebra. Then
$X'=X+\kappa\,\varphi(X)$. Modulo scalars, $\varphi$ is the odd map

$$\varphi(b_j^sb_k^t)=\ell(b_j^s)\,b_k^t+\ell(b_k^t)\,b_j^s,\qquad \varphi(a^\sigma b_k^t)=-a^\sigma\ell(b_k^t),\qquad \varphi(a^+a^-)=0 .$$

*Proof.* Expand the product and use $\kappa^2=0$. For $b$ even, $b\kappa=\kappa b$. For $a$ odd, $a\kappa=-\kappa a$.
Commutators between $b$ and $\ell(\cdot)$ only create further factors of $\kappa$, which vanish. ∎

Note that $\varphi$ maps into $\mathfrak g$: $a^\sigma a^+$ and $a^\sigma a^-$ are either $0$ or equal to $\pm a^+a^-$ up to scalar.

**Lemma 3 (the coboundary identity).** Write $\varphi:\mathfrak g\to\mathfrak g$ as above. Then for all $X,Y$:

$$\gamma_{\mathrm{gb}}(X,Y)=-(\delta\varphi)(X,Y).$$

*Proof.* Use $X\kappa=(-1)^{p(X)}\kappa X$ and $\kappa^2=0$ to get

$$[X',Y']_{\mathrm{gb}}=[X,Y]_{\mathrm{gb}}+\kappa\Big((-1)^{p(X)}[X,\varphi Y]_0+[\varphi X,Y]_0\Big),\qquad
[\varphi X,Y]=-(-1)^{(p(X)+1)p(Y)}[Y,\varphi X].$$

On the other hand, the primed oscillators obey the undeformed relations (Lemma 1). So the primed quadratics have the undeformed
structure constants: if $[X,Y]_0=\sum_Z c^Z_{XY}Z+c_{XY}\cdot1$, then

$$[X',Y']_{\mathrm{gb}}=\sum_Z c^Z_{XY}Z'+c_{XY}=[X,Y]_0+\kappa\,\varphi([X,Y]_0).$$

Comparing $\kappa$-parts gives
$\gamma(X,Y)=\varphi([X,Y])-(-1)^{p(X)}[X,\varphi Y]+(-1)^{(p(X)+1)p(Y)}[Y,\varphi X]=-(\delta\varphi)(X,Y)$.

The derivation never discards scalars. It therefore holds exactly in $\mathcal U(A)$ when $\varphi$ keeps its scalar part and $\varphi(1)=0$, and a fortiori it holds modulo scalars. ∎

**Proof of the Theorem.** Take $f_{\mathrm{gb}}:=-\varphi$. It is odd by construction and maps $\mathfrak g\to\mathfrak g$ (mod scalars).
Lemma 3 gives $\gamma_{\mathrm{gb}}=\delta f_{\mathrm{gb}}$. Nothing depends on the values of gb or on $n$. ∎

**Remark (non-uniqueness).** One could instead absorb gb into the fermions:
$a'^{\,\sigma}=a^\sigma+\kappa\,m(a^\sigma)$ with $m(a^\sigma)=\sum_j(\mathrm{gb}_{\sigma,j,-}b_j^+-\mathrm{gb}_{\sigma,j,+}b_j^-)$, using the
non-degeneracy of the CCR. This yields a second trivialising $f$. The two differ by an element of $\ker\delta$.

Numerically, $\dim\ker\delta|_{\text{odd maps}}=4n=\dim\mathfrak g_{\bar1}$ for $n=1,2,3$. This equals the dimension of the
"inner" solutions $X\mapsto\pm[Z,X]$, $Z\in\mathfrak g_{\bar1}$, i.e. the even derivations $\mathrm{ad}(\kappa Z)$ of $\mathfrak g\otimes\Lambda[\kappa]$.
So, for these $n$, $f_{\mathrm{gb}}$ is unique up to inner terms. I verified this dimension count for $n\le3$ only. I did not prove it for general $n$, and the Theorem does not need it.

---

## 4. Closed form of the trivialising map

With $\ell(b_j^s)=\mathrm{gb}_{-,j,s}a^+ + \mathrm{gb}_{+,j,s}a^-$, and modulo scalars:

| $X$ | $f_{\mathrm{gb}}(X)$ |
|---|---|
| $a^+a^-$ | $0$ |
| $b_j^s b_k^t$ | $-\big(\ell(b_j^s)\,b_k^t+\ell(b_k^t)\,b_j^s\big)$ |
| $a^+ b_k^t$ | $\mathrm{gb}_{+,k,t}\,a^+a^-$ |
| $a^- b_k^t$ | $\mathrm{gb}_{-,k,t}\,a^-a^+\equiv-\mathrm{gb}_{-,k,t}\,a^+a^-$ |

**Worked example** ($n=1$, $\mathrm{gb}_{+,1,+}=1$, all other gb zero, so $\ell(b_1^+)=a^-$ and $\ell(b_1^-)=0$):

* $\gamma(a^+a^-,b_1^+b_1^+)=2\,a^-b_1^+$. By hand: $[a^+a^-,b_1^+]=\kappa a^-$, so $[a^+a^-,(b_1^+)^2]=2\kappa a^-b_1^+$.
* $f(b_1^+b_1^+)=-2a^-b_1^+$, $f(b_1^+b_1^-)=-a^-b_1^-$, and $f(a^+b_1^+)=a^+a^-$. All other basis elements map to $0$.
* $\delta f=\gamma$ on all $64$ ordered pairs. $21$ of them have non-zero $\gamma$, and $2$ also carry a dropped $\kappa\cdot$scalar term.
  Full data: `verification/artifacts/cn1_n1.json` → `per_gb_parameter["gb[a1+,b1+]"]`.

---

## 5. Computational verification

**Code**: `verification/cn1_deformation.py`. It is self-contained: Python 3, `fractions`, and `numpy` (`numpy` is used for ranks only).
**Reproduce**: `python3 verification/cn1_deformation.py 1 2 3`. The full run takes about 5 seconds.

**Engine.** The script implements an exact normal-ordering algorithm for $\mathcal U(A)$ with the gb deformation:
- words are reordered with $xy=(-1)^{p(x)p(y)}yx+[x,y]$;
- odd squares are reduced with $x^2=\tfrac12[x,x]$, which gives $\kappa^2=(a^\pm)^2=0$;
- coefficients are exact rationals.

Brackets of basis quadratics are computed directly in this engine. It asserts that every result lies in $\mathfrak g\oplus\mathbf C1\oplus\kappa(\mathfrak g\oplus\mathbf C1)$.

**Checks performed for each n ∈ {1,2,3}:**
1. For each of the $4n$ unit gb vectors, the following hold exactly:
   - the primed oscillators satisfy the undeformed relations;
   - $\varphi$ computed by substitution agrees with the closed form in §4;
   - $\delta f=\gamma$ modulo scalars.
2. For a random generic gb (all $4n$ entries non-zero, rational), the following hold exactly:
   - $\delta f=\gamma$;
   - $\gamma$ is linear in gb;
   - the **exact $\mathcal U(A)$ identity including scalars** holds (§2.4, stronger form).
3. Linear algebra over all odd $f$ (all unknowns $\phi_{ij}$), with ranks computed exactly over $\mathrm{GF}(2^{31}-1)$ and cross-checked in floating point:

| n | algebra | sdim | #odd maps | rank δ | dim ker δ | rank [δ ∣ all γ_e] | rank(gb→γ) | random cochain in im δ? |
|---|---|---|---|---|---|---|---|---|
| 1 | C(2)=osp(2∣2) | 4∣4 | 32 | 28 | 4 | 28 | 4 | no (control) |
| 2 | C(3)=osp(2∣4) | 11∣8 | 176 | 168 | 8 | 168 | 8 | no (control) |
| 3 | C(4)=osp(2∣6) | 22∣12 | 528 | 516 | 12 | 516 | 12 | no (control) |

The table shows three things:
- $\mathrm{rank}[\delta\mid\gamma]=\mathrm{rank}\,\delta$, so every $\gamma_{\mathrm{gb}}$ lies in $\operatorname{im}\delta$. This is an independent confirmation, by linear algebra, of triviality for **all** gb.
- $\mathrm{rank}(\mathrm{gb}\to\gamma)=4n$, so distinct gb give distinct non-zero cochains.
- The negative control (a random odd 2-cochain on the same support) is *not* in $\operatorname{im}\delta$. So the solvability test is not vacuous.

**Structured artifacts** (`verification/artifacts/`):
- `cn1_n{1,2,3}.json` contains:
  - the basis with parities;
  - the undeformed structure constants, mod scalars, plus their scalar parts listed separately;
  - for each gb parameter: $\gamma$, the dropped $\kappa$-scalar parts, the explicit trivialising $f$, and per-parameter check flags;
  - the random-gb test and the rank data.
- `summary.json` holds all check flags and ranks for $n=1,2,3$.

All values are exact rationals, written as strings such as `"1/2"` where the value is not an integer.

---

## 6. Conclusion

There is **no** condition on gb. For every $n\ge1$ and every $\mathrm{gb}\in\mathbf C^{4n}$ (zero or non-zero), the inhomogeneous deformation
$\gamma_{\mathrm{gb}}$ of $C(n+1)=\mathfrak{osp}(2|2n)$ is a coboundary: $\gamma_{\mathrm{gb}}=\delta f_{\mathrm{gb}}$ with the explicit odd map $f_{\mathrm{gb}}$ of §4.

- **Up to scalar.** The equality holds in the adjoint representation, i.e. modulo $\mathbf C\cdot1$. It even holds exactly in $\mathcal U(A)$ once $f$ is allowed a scalar component.
- **Mechanism.** Triviality comes from the non-degeneracy of the fermionic pairing $\{a^-,a^+\}=1$. This non-degeneracy lets every mixed coupling $[b,a]\propto\kappa$ be absorbed by the shift $b\mapsto b+\kappa\ell(b)$. The bosonic pairing provides an alternative absorption.
- **Verification.** The proof is general. The exact verification covers $n=1,2,3$.
