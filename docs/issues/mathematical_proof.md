# Triviality of the Inhomogeneous (gb) Deformation of $C(n+1)=\mathfrak{osp}(2|2n)$

**Status**: resolved (theorem + exact computer verification for $n=1,2,3$)
**Author**: Claude Fable 5.1 (run `study/thm01-R-fable51-b03-C`), 2026-10-08
**Inputs used**: only `docs/math/Cn1_definition.md`, `docs/math/C_inhomogeneous_definition.md`,
`docs/math/C_coboundary_definition.md`, `docs/issues/issue_open.md`. No external sources were consulted.

---

## 0. Statement of the result

Let $\mathfrak g = C(n+1)$ be realised by quadratic oscillator expressions inside
$\mathcal U(A_{gb})$, where $A_{gb}$ is the pre-oscillator algebra with the
inhomogeneous relations $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$
($\kappa$ odd, central, hence $\kappa^2=0$; $K=1$).
Write the deformed bracket of basis elements as

$$
[X,Y]_{gb} \;=\; [X,Y]_0 \;+\; \kappa\,\gamma_{gb}(X,Y),
\qquad \gamma_{gb}(X,Y)\in \mathfrak g\oplus\mathbf C\cdot 1 .
$$

**Theorem.** For every $n\ge 1$ and *every* choice of the $4n$ complex parameters
$\mathrm{gb}_{\sigma,j,s}$ there is an explicit odd linear map
$f_{gb}:\mathfrak g\to\mathfrak g\oplus\mathbf C$ such that

$$
\gamma_{gb} \;=\; \delta f_{gb}
\qquad\text{exactly, as maps } \mathfrak g\otimes\mathfrak g\to\mathfrak g\oplus\mathbf C ,
$$

with $\delta$ the coboundary operator of `C_coboundary_definition.md`.
Writing $f_{gb}=\bar f_{gb}+f^0_{gb}$ with $\bar f_{gb}:\mathfrak g\to\mathfrak g$ (adjoint part) and
$f^0_{gb}:\mathfrak g\to\mathbf C$ (scalar part), one has

$$
\underbrace{\gamma_{gb}\bmod \mathbf C}_{\text{adjoint-valued part}} \;=\; \delta\bar f_{gb},
\qquad
\underbrace{\gamma_{gb}\big|_{\mathbf C}}_{\text{scalar part}} \;=\; -\,f^0_{gb}\circ[\,\cdot,\cdot\,]_0 .
$$

**Consequences (the triviality conditions).**

| Reading of "$\gamma_{gb}=\delta f$" | Necessary and sufficient condition on gb |
|---|---|
| (A) **Adjoint / up to scalar** (the reading prescribed by `C_coboundary_definition.md` §3): $\gamma_{gb}$ is regarded as a 2-cochain with values in the adjoint module $\mathfrak g$ (central scalars discarded), $f:\mathfrak g\to\mathfrak g$ odd. | **No condition. Every $\gamma_{gb}$ is trivial**: $[\gamma_{gb}]=0\in H^2_{\bar 1}(\mathfrak g,\mathfrak g)$, with the explicit primitive $\bar f_{gb}$ below. |
| (A') "up to scalar" read as "$\gamma_{gb}=\lambda\,\delta f$ for some $\lambda\in\mathbf C^\times$". | Same as (A) (rescale $f$). |
| (B) $f$ allowed to take values in $\mathfrak g\oplus\mathbf C$ (the natural ambient space of quadratic elements), exact equality including scalars. | **No condition.** $\gamma_{gb}=\delta f_{gb}$ exactly. |
| (C) **Strict**: $f:\mathfrak g\to\mathfrak g$ only, *and* equality of the central scalar components demanded. | $\gamma_{gb}=\delta f$ iff $\mathrm{gb}=0$ (all $4n$ parameters vanish). The obstruction is purely the scalar 2-coboundary $-f^0_{gb}\circ[\,,]_0$, which is non-zero for every $\mathrm{gb}\neq0$. |

The definitive answer to the issue, under the definitions as written
("as an adjoint representation … up to scalar"), is therefore:

> **The inhomogeneous deformation $\gamma_{gb}$ of $C(n+1)$ is trivial for all values of the
> parameters $\mathrm{gb}_{\sigma,j,s}$. There is no non-zero configuration of gb that is
> non-trivial, and conversely no configuration is excluded: the set of trivial gb is the whole
> parameter space $\mathbf C^{4n}$.** The deformation is nevertheless a *non-zero cochain*
> for every $\mathrm{gb}\ne0$ (the map $\mathrm{gb}\mapsto\gamma_{gb}$ is injective), so the
> content of the theorem is that its cohomology class vanishes.

Everything is proved uniformly in $n$ (§2) and, in addition, verified by exact computer algebra for
$n=1,2,3$ (§4) with reusable JSON artifacts (§5).

---

## 1. Conventions

* $A_{gb}=V\oplus\mathbf C K\oplus\mathbf C\kappa$, $V=\mathrm{span}\{a_1^\pm, b_j^\pm\}$,
  $p(a_1^\pm)=1$, $p(b_j^\pm)=0$, $p(\kappa)=1$. We set $K=1$. Super-commutator
  $[x,y]=xy-(-1)^{p(x)p(y)}yx$. Relations:
  $[a_1^-,a_1^+]=1$, $[b_j^-,b_k^+]=\delta_{jk}$, $[b_j^s,a_1^\sigma]=-\mathrm{gb}_{\sigma,j,s}\kappa$,
  all other generator brackets $0$. $\kappa$ central implies $[\kappa,\kappa]=2\kappa^2=0$.
* Basis $\{Z_i\}$ of $\mathfrak g$: exactly the generators of `Cn1_definition.md` §2
  ($H_1,\dots,H_{n+1}$; $E_{\delta_k-\delta_l}=b_k^+b_l^-$; $E_{\delta_k+\delta_l}=b_k^+b_l^+$,
  $E_{-\delta_k-\delta_l}=b_k^-b_l^-$ for $k<l$; $E_{\pm2\delta_k}=\tfrac12(b_k^\pm)^2$;
  $E_{\pm\varepsilon\pm\delta_l}=a_1^{\pm}b_l^{\pm}$). Dimension $2n^2+5n+1$, odd part $4n$.
* **Fact 1.1 (closure).** With this basis (note the $-\tfrac12$ in $H_{n+1}$) the undeformed
  brackets $[Z_a,Z_b]_0=\sum_c C^c_{ab}Z_c$ close inside $\mathfrak g$ with **no scalar term**,
  and the $C^c_{ab}$ satisfy the super-Jacobi identity (verified exactly, §4). Moreover the
  space $Q$ of quadratic elements of $\mathcal U(A_0)$ (including the constant $1$) satisfies
  $Q=\mathfrak g\oplus\mathbf C$ and $\mathfrak g=[Q,Q]$, so the splitting
  "adjoint part $\oplus$ scalar part" is canonical.
* The deformed bracket is written with $\kappa$ **on the left**:
  $[X,Y]_{gb}=[X,Y]_0+\kappa\,\gamma_{gb}(X,Y)$. Since $\kappa$ is odd,
  $p(\gamma_{gb}(X,Y))=p(X)+p(Y)+1$: $\gamma_{gb}$ is an **odd** 2-cochain, matching the
  requirement in `C_coboundary_definition.md` that $f$ be odd (so $\delta f$ is odd).
* Coboundary (as given): $(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y])$.
  When $f$ has a scalar component $f^0$, $[X,f^0(Y)\cdot 1]=0$, so
  $\delta(\bar f+f^0)=\delta\bar f-f^0\circ[\,,]_0$, with $\delta\bar f$ purely $\mathfrak g$-valued (Fact 1.1).

**Remark on the parity of gb.** `C_inhomogeneous_definition.md` says the gb "must have parity 1".
Since $p([b_j^s,a_1^\sigma])=1=p(\kappa)$, the *coefficients* $\mathrm{gb}_{\sigma,j,s}$ are
ordinary complex numbers; the parity-1 statement is correctly read as "the deformation cochain
$\gamma_{gb}$ (equivalently the deformation direction $\kappa$) is odd". Treating the gb as
Grassmann-odd scalars would make $\gamma_{gb}$ even and would be inconsistent with the
requirement that $f$ be odd; we therefore take $\mathrm{gb}_{\sigma,j,s}\in\mathbf C$.
(Nothing in the argument below depends on this: the proof is a formal identity in
$\mathbf Q[\mathrm{gb}]$.)

---

## 2. Proof

### Lemma 2.1 (shape of $\gamma_{gb}$)
For $X,Y\in\mathfrak g$, $[X,Y]_{gb}=[X,Y]_0+\kappa\,\gamma_{gb}(X,Y)$ with
$\gamma_{gb}(X,Y)\in\mathfrak g\oplus\mathbf C$ **linear** in gb.

*Proof.* The super-commutator of two quadratic monomials is computed by the
super-Leibniz rule; each term contains exactly one bracket of generators, which is $0$, a
scalar, or $-\mathrm{gb}\,\kappa$, times a product of the remaining two generators. Terms with
two $\kappa$'s vanish. Hence the $\kappa$-part is $\kappa$ times a quadratic (plus scalar)
element, linear in gb. $\square$

### Lemma 2.2 (the deformation is undone by a change of generators of $A_{gb}$)
Inside $\mathcal U(A_{gb})$ put
$$
C^\sigma:=\sum_{j=1}^n\Big(\mathrm{gb}_{\sigma,j,-}\,b_j^{+}-\mathrm{gb}_{\sigma,j,+}\,b_j^{-}\Big),
\qquad
\tilde a^\sigma:=a_1^\sigma+\kappa\,C^\sigma\quad(\sigma=\pm).
$$
Then $\tilde a^\pm$, $b_j^\pm$, $\kappa$ satisfy the **undeformed** relations:
$[\tilde a^-,\tilde a^+]=1$, $[\tilde a^\pm,\tilde a^\pm]=0$, $[b_j^s,\tilde a^\sigma]=0$, $[\kappa,\tilde a^\sigma]=0$.

*Proof.* $[b_j^s,\tilde a^\sigma]=-\mathrm{gb}_{\sigma,j,s}\kappa+\kappa[b_j^s,C^\sigma]$ and
$[b_j^+,C^\sigma]=-\mathrm{gb}_{\sigma,j,+}[b_j^+,b_j^-]=\mathrm{gb}_{\sigma,j,+}$,
$[b_j^-,C^\sigma]=\mathrm{gb}_{\sigma,j,-}[b_j^-,b_j^+]=\mathrm{gb}_{\sigma,j,-}$, so the bracket vanishes.
$[\tilde a^-,\tilde a^+]=[a^-,a^+]+[a^-,\kappa C^+]+[\kappa C^-,a^+]+[\kappa C^-,\kappa C^+]$;
the last term is $\propto\kappa^2=0$ and
$[a^-,\kappa C^+]=-\kappa[a^-,C^+]=-\kappa\sum(\ldots)[a^-,b]\propto\kappa^2=0$, likewise the third term.
The remaining relations are identical. $\square$

Consequently $\mathcal U(A_{gb})$ is generated by $(\tilde a,b,\kappa)$ subject to the
undeformed relations; i.e. there is an algebra isomorphism
$\Theta:\mathcal U(A_{gb})\to\mathcal U(A_0)$ with $\Theta(\tilde a^\sigma)=a^\sigma$,
$\Theta(b)=b$, $\Theta(\kappa)=\kappa$, under which the original generators go to
$\Theta(a_1^\sigma)=a^\sigma-\kappa C^\sigma$.

### Definition 2.3 (the primitive $f_{gb}$)
For $Z\in\mathfrak g$ (a quadratic polynomial $Z(a,b)$) expand
$$
\Theta(Z)=Z(a-\kappa C,\,b)=Z(a,b)+\kappa\,f_{gb}(Z),\qquad f_{gb}(Z)\in Q=\mathfrak g\oplus\mathbf C .
$$
$f_{gb}$ is linear, odd (one $a$ is replaced by a bosonic linear form), linear in gb, and explicitly:
$$
\begin{aligned}
f_{gb}(X)&=0 &&\text{for } X \text{ purely bosonic } (H_2,\dots,H_{n+1},\;E_{\pm\delta_k\pm\delta_l},\;E_{\pm2\delta_k}),\\
f_{gb}(H_1)&=a^+C^- - C^+a^-
 =\sum_j\Big(\mathrm{gb}_{-,j,-}E_{\varepsilon+\delta_j}-\mathrm{gb}_{-,j,+}E_{\varepsilon-\delta_j}
 -\mathrm{gb}_{+,j,-}E_{-\varepsilon+\delta_j}+\mathrm{gb}_{+,j,+}E_{-\varepsilon-\delta_j}\Big),\\
f_{gb}(E_{\sigma\varepsilon+s\delta_l})&=-\,C^\sigma b_l^{s}
 =\sum_j\Big(\mathrm{gb}_{\sigma,j,+}\,b_j^-b_l^{s}-\mathrm{gb}_{\sigma,j,-}\,b_j^+b_l^{s}\Big)
 \;\in\;\mathfrak{sp}(2n)\oplus\mathbf C .
\end{aligned}
$$
Re-expressed in the basis, the scalar part is
$f^0_{gb}(E_{\sigma\varepsilon+s\delta_l})=\tfrac12\mathrm{gb}_{\sigma,l,s}$ and $f^0_{gb}=0$ on
$\mathfrak g_{\bar0}$ (it arises from $b_l^-b_l^+=b_l^+b_l^-+1$ and from the $-\tfrac12$ in $H_{n+1}$).
For $n=1$:
$$
\begin{aligned}
f(H_1)&=\mathrm{gb}_{-,1,-}E_{\varepsilon+\delta}-\mathrm{gb}_{-,1,+}E_{\varepsilon-\delta}-\mathrm{gb}_{+,1,-}E_{-\varepsilon+\delta}+\mathrm{gb}_{+,1,+}E_{-\varepsilon-\delta},\\
f(E_{\varepsilon+\delta})&=-\mathrm{gb}_{+,1,+}H_2-2\,\mathrm{gb}_{+,1,-}E_{2\delta}+\tfrac12\mathrm{gb}_{+,1,+},&
f(E_{\varepsilon-\delta})&=\mathrm{gb}_{+,1,-}H_2+2\,\mathrm{gb}_{+,1,+}E_{-2\delta}+\tfrac12\mathrm{gb}_{+,1,-},\\
f(E_{-\varepsilon+\delta})&=-\mathrm{gb}_{-,1,+}H_2-2\,\mathrm{gb}_{-,1,-}E_{2\delta}+\tfrac12\mathrm{gb}_{-,1,+},&
f(E_{-\varepsilon-\delta})&=\mathrm{gb}_{-,1,-}H_2+2\,\mathrm{gb}_{-,1,+}E_{-2\delta}+\tfrac12\mathrm{gb}_{-,1,-},
\end{aligned}
$$
and $f(H_2)=f(E_{\pm2\delta})=0$.

### Theorem 2.4
$\gamma_{gb}=\delta f_{gb}$ as maps $\mathfrak g\otimes\mathfrak g\to\mathfrak g\oplus\mathbf C$.

*Proof.* Apply the isomorphism $\Theta$ to the identity $[X,Y]_{gb}=[X,Y]_0+\kappa\gamma_{gb}(X,Y)$
of $\mathcal U(A_{gb})$. On the right, $\Theta([X,Y]_0)=[X,Y]_0+\kappa f_{gb}([X,Y]_0)$
(linearity of $f_{gb}$ and Fact 1.1) and $\Theta(\kappa\gamma)=\kappa\gamma+O(\kappa^2)=\kappa\gamma$.
On the left, computing in $\mathcal U(A_0)$:
$$
[X+\kappa f(X),\,Y+\kappa f(Y)]_0=[X,Y]_0+[X,\kappa f(Y)]_0+[\kappa f(X),Y]_0 .
$$
Using $X\kappa=(-1)^{p(X)}\kappa X$ and $p(f(X))=p(X)+1$,
$$
[X,\kappa f(Y)]_0=(-1)^{p(X)}\kappa[X,f(Y)]_0,\qquad
[\kappa f(X),Y]_0=\kappa[f(X),Y]_0=-(-1)^{(p(X)+1)p(Y)}\kappa[Y,f(X)]_0 .
$$
Comparing the coefficients of $\kappa$ (legitimate because $\mathcal U(A_0)=\mathcal U(A_0')\oplus\kappa\,\mathcal U(A_0')$
by PBW, $A_0'$ the $\kappa$-free part):
$$
\gamma_{gb}(X,Y)=(-1)^{p(X)}[X,f(Y)]_0-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]_0-f([X,Y]_0)=(\delta f_{gb})(X,Y). \qquad\square
$$

Equivalently: $\Phi=\mathrm{id}+\kappa f_{gb}$ is a Lie-superalgebra isomorphism from
$(\mathfrak g,[\,,]_{gb})$ onto its image in $\mathfrak g\oplus\kappa(\mathfrak g\oplus\mathbf C)\subset\mathcal U(A_0)$,
which is the textbook meaning of a trivial first-order deformation.

### Corollary 2.5 (the three readings)
Split $f_{gb}=\bar f_{gb}+f^0_{gb}$. By the remark in §1,
$\delta f_{gb}=\delta\bar f_{gb}-f^0_{gb}\circ[\,,]_0$ with $\delta\bar f_{gb}$ purely $\mathfrak g$-valued. Hence:

* **(A) adjoint representation / up to scalar.** Projecting $\mathfrak g\oplus\mathbf C\to\mathfrak g$
  (this projection is $\mathfrak g$-equivariant since $\mathbf C$ is central), the
  $\mathfrak g$-valued cochain $\bar\gamma_{gb}$ equals $\delta\bar f_{gb}$ with
  $\bar f_{gb}:\mathfrak g\to\mathfrak g$ odd. **Trivial for all gb.**
* **(B)** $\gamma_{gb}=\delta f_{gb}$ exactly. **Trivial for all gb.**
* **(C) strict.** For $f:\mathfrak g\to\mathfrak g$ the scalar part of $\delta f$ is $0$, while the scalar
  part of $\gamma_{gb}$ equals $-f^0_{gb}\circ[\,,]_0$. Because $[\mathfrak g,\mathfrak g]_0=\mathfrak g$
  (the structure constants verify that every $E_{\sigma\varepsilon+s\delta_l}$ is a bracket, e.g.
  $[H_1,E_{\varepsilon+\delta_l}]_0=(1+\delta_{l1})E_{\varepsilon+\delta_l}$), the map
  $\mathrm{gb}\mapsto\gamma_{gb}|_{\mathbf C}$ is injective (rank $4n$, §4). So strict equality
  holds **iff gb $=0$**. The obstruction is itself a coboundary in $H^2(\mathfrak g,\mathbf C)$
  (trivial module), so it carries no deformation-theoretic content; it is precisely the
  artefact that the "up to scalar" clause in `C_coboundary_definition.md` §3 removes.

### Proposition 2.6 (uniqueness of the primitive; non-vanishing of the cochain)
For $n=1,2,3$ (exact computation, §4):
$\dim\ker\big(\delta:\mathrm{Hom}_{\bar1}(\mathfrak g,\mathfrak g)\to C^2\big)=4n=\dim\mathfrak g_{\bar1}$ and the odd
inner derivations $\mathrm{ad}(W)$, $W\in\mathfrak g_{\bar1}$, lie in this kernel; hence
$H^1_{\bar1}(\mathfrak g,\mathfrak g)=0$ and $\bar f_{gb}$ is unique up to adding $\mathrm{ad}(W)$, $W\in\mathfrak g_{\bar1}$.
The scalar part $f^0_{gb}$ is unique because $[\mathfrak g,\mathfrak g]_0=\mathfrak g$.
Finally $\mathrm{rank}(\mathrm{gb}\mapsto\bar\gamma_{gb})=4n$: $\gamma_{gb}\neq0$ as a cochain whenever $\mathrm{gb}\neq0$
(for example $\gamma_{gb}(E_{\varepsilon+\delta_k},E_{\varepsilon+\delta_l})
=\mathrm{gb}_{+,k,+}E_{\varepsilon+\delta_l}+\mathrm{gb}_{+,l,+}E_{\varepsilon+\delta_k}$).

---

## 3. Handling of the "adjoint representation / up to scalar" condition (summary)

1. `C_inhomogeneous_definition.md` places $\mathfrak g$ inside $\mathcal U(A)$ "by adjoint representation", i.e. the
   bracket is the super-commutator of $\mathcal U(A)$. The $\kappa$-part of a commutator of two quadratics is a
   quadratic **plus a central scalar** ($Q=\mathfrak g\oplus\mathbf C$, Fact 1.1). So $\gamma_{gb}$ is naturally
   $(\mathfrak g\oplus\mathbf C)$-valued, while `C_coboundary_definition.md` asks for $f:\mathfrak g\to\mathfrak g$.
2. "As an adjoint representation … up to scalar" is interpreted as: compare $\gamma_{gb}$ and $\delta f$ **as
   cochains with values in the adjoint module** $\mathfrak g=Q/\mathbf C$, i.e. discard the central scalar component.
   This is the only reading under which both sides live in the same space, and it is $\mathfrak g$-equivariant.
3. Under that reading the answer is unconditional triviality (Cor. 2.5(A)). We also computed what happens if one
   refuses to discard scalars (Cor. 2.5(C)): the only "obstruction" is a scalar-valued coboundary, non-zero iff
   $\mathrm{gb}\neq0$. Both facts are recorded in the artifacts so that a reader preferring either convention can
   check the claim they care about.
4. If "up to scalar" were instead meant as $\gamma_{gb}=\lambda\,\delta f$, the conclusion is unchanged (rescale $f$).

---

## 4. Computational verification (exact arithmetic, $n=1,2,3$)

Code: `verification/osc_algebra.py` (normal-ordered model of $\mathcal U(A_{gb})$ with coefficients in
$\mathbf Q[\mathrm{gb}]$), `verification/cn1.py` (basis, decomposition $Q=\mathfrak g\oplus\mathbf C$, $\gamma_{gb}$,
$f_{gb}$, $\delta$), `verification/run_verification.py` (driver), `verification/check_artifact.py`
(independent re-check from the JSON only). Run

```
python3 verification/run_verification.py     # ~3 s, writes artifacts/*.json
python3 verification/check_artifact.py       # re-verifies gamma = delta f from the JSON alone
```

Results (`artifacts/verification_summary.json`):

| check | $n=1$, $\mathfrak{osp}(2|2)$ | $n=2$, $\mathfrak{osp}(2|4)$ | $n=3$, $\mathfrak{osp}(2|6)$ |
|---|---|---|---|
| $\dim\mathfrak g$ (even $|$ odd) | 8 (4$|$4) | 19 (11$|$8) | 34 (22$|$12) |
| undeformed bracket closes in $\mathfrak g$ without scalars; super-Jacobi | yes; residual 0 | yes; 0 | yes; 0 |
| super-Jacobi of the deformed bracket on $L=\mathfrak g\oplus\kappa\mathfrak g$ (random gb) | 0 | 0 | 0 |
| Lemma 2.2 relations for $\tilde a$ (exact in $\mathbf Q[\mathrm{gb}]$) | all true | all true | all true |
| $\gamma_{gb}=\delta f_{gb}$, $\mathfrak g$-part **and** scalar part (exact, symbolic gb) | true / true | true / true | true / true |
| $\bar\gamma_{gb}=\delta\bar f_{gb}$ and $\delta\bar f_{gb}$ has no scalar part | true | true | true |
| odd inner derivations $\in\ker\delta$ (exact) | true | true | true |
| #odd unknowns $\phi_{ij}$; $\mathrm{rank}\,\delta$; $\dim\ker\delta$ (mod $p=2^{31}-1$) | 32; 28; 4 | 176; 168; 8 | 528; 516; 12 |
| $\Rightarrow\ \dim H^1_{\bar1}(\mathfrak g,\mathfrak g)$ | 0 | 0 | 0 |
| $\mathrm{rank}(\mathrm{gb}\mapsto\bar\gamma_{gb})$, $\mathrm{rank}(\mathrm{gb}\mapsto\gamma_{gb}|_{\mathbf C})$ | 4, 4 | 8, 8 | 12, 12 |
| $\mathrm{rank}[\delta\,|\,\bar\gamma]=\mathrm{rank}\,\delta$ (image test, independent of $f_{gb}$) | yes | yes | yes |
| dimension of trivial-gb subspace, reading (A)/(B) | 4 = all | 8 = all | 12 = all |
| dimension of trivial-gb subspace, strict reading (C) | 0 | 0 | 0 |

Logical status of each line: the symbolic identities are exact proofs for the stated $n$ (polynomial identities in
$\mathbf Q[\mathrm{gb}]$). The mod-$p$ ranks give $\mathrm{rank}_{\mathbf Q}\ge\mathrm{rank}_p$; combined with the exact
facts that $\ker\delta\supseteq\mathrm{ad}(\mathfrak g_{\bar1})$ (dimension $4n$) and that the gb-maps have at most $4n$
columns, every rank statement above is exact over $\mathbf Q$.

---

## 5. Structured artifacts (for computational reuse)

`artifacts/C{n+1}_osp2_{2n}.json`, one file per $n\in\{1,2,3\}$, with 0-based indices into `basis`:

```json
{
 "algebra": "C(2) = osp(2|2)", "n": 1, "dim": 8,
 "basis":  ["H1","H2","E[2d1]","E[-2d1]","E[e+d1]","E[e-d1]","E[-e+d1]","E[-e-d1]"],
 "parity": [0,0,0,0,1,1,1,1],
 "gb_parameters": ["gb[a+,b1+]","gb[a+,b1-]","gb[a-,b1+]","gb[a-,b1-]"],
 "conventions": { "...": "bracket, deformation, decomposition, coboundary, f, indexing" },
 "structure_constants": [[a, b, c, "C^c_ab"], ...],
 "gamma":               [[a, b, c, {"gb[..]": "coeff", ...}], ...],
 "gamma_scalar":        [[a, b,    {"gb[..]": "coeff", ...}], ...],
 "explicit_f_phi":      [[i, j,    {"gb[..]": "coeff", ...}], ...],
 "explicit_f_phi_scalar":[[j,      {"gb[..]": "coeff", ...}], ...],
 "verification": { "...": "the summary table above" }
}
```

Semantics: $[Z_a,Z_b]_{gb}=\sum_c C^c_{ab}Z_c+\kappa\big(\sum_c\gamma^c_{ab}Z_c+\gamma^0_{ab}\big)$,
$f(Z_j)=\sum_i\phi_{ij}Z_i+\phi^0_j$. All coefficients are linear forms in the gb with rational coefficients,
stored as strings of exact fractions. `check_artifact.py` consumes only these fields and re-derives
$\gamma=\delta f$ for random integer gb with exact `Fraction` arithmetic.

---

## 6. Conclusion

The two deformation structures are consistent for $n=1,2,3$ (and for all $n$ by the uniform proof): the
inhomogeneous gb-deformation of $C(n+1)$ is always the coboundary of the explicit odd map $f_{gb}$ of Definition 2.3.
The necessary and sufficient condition for triviality in the sense of `C_coboundary_definition.md` (adjoint-valued,
up to the central scalar) is **vacuous**: every $\mathrm{gb}\in\mathbf C^{4n}$ gives a trivial deformation, and no
non-zero gb yields a non-trivial class. Only if one insists on matching the central scalar component with a strictly
$\mathfrak g$-valued $f$ does one obtain the degenerate condition $\mathrm{gb}=0$, and that obstruction is a scalar
2-coboundary rather than a genuine cohomology class.
