# Triviality of the Inhomogeneous Deformation of $C(n+1)=\mathfrak{osp}(2|2n)$

**Status**: resolved. **Sources used**: only `docs/math/*.md` in this repository. No web access, no papers.
**Artifacts**: `verification/cn1_triviality.py`, `verification/artifacts/*.json`.

---

## 0. Result

> **Theorem.** Let $n\ge 1$ and $\mathrm{gb}=(\mathrm{gb}_{\sigma,j,s})\in\mathbf C^{4n}$ be arbitrary.
> Then the inhomogeneous deformation $\gamma_{\mathrm{gb}}$ of $\mathfrak g=C(n+1)$ is **trivial**: there is an
> odd linear map $f_{\mathrm{gb}}:\mathfrak g\to\mathfrak g$ with
> $$\gamma_{\mathrm{gb}}(X,Y)=(\delta f_{\mathrm{gb}})(X,Y)\qquad\text{for all }X,Y\in\mathfrak g$$
> as an identity in the adjoint representation (i.e. modulo the central scalars $\mathbf C1\oplus\mathbf C\kappa$ of $\mathcal U(A)$).
> Moreover:
> 1. The map $\mathrm{gb}\mapsto\gamma_{\mathrm{gb}}$ is injective. So every nonzero gb gives a **nonzero but trivial** deformation.
> 2. $f_{\mathrm{gb}}$ is given in closed form by (3.3) below. It depends linearly on gb.
> 3. $f_{\mathrm{gb}}$ is unique up to adding $\operatorname{ad}_Y$ for $Y\in\mathfrak g_{\bar 1}$. The solution space is an affine space of dimension $\dim\mathfrak g_{\bar1}=4n$.
>
> **The triviality condition on gb is therefore empty**: every configuration, zero or nonzero, satisfies $\gamma_{\mathrm{gb}}=\delta f$.

The proof in §3 works for every $n$. The exact computer verification (§4) covers $n=1,2,3$ in two independent basis conventions.

---

## 1. Setting and conventions

$A=V\oplus\mathbf CK\oplus\mathbf C\kappa$, with $V_{\bar0}=\operatorname{span}\{b_j^\pm\}$ and $V_{\bar1}=\operatorname{span}\{a^\pm\}$ (where $a^\pm=a_1^\pm$). We work in $\mathcal U(A)$ with $K=1$. The brackets of generators are
$$[b_j^-,b_l^+]=\delta_{jl},\quad \{a^-,a^+\}=1,\quad [b_j^s,a^\sigma]=-\mathrm{gb}_{\sigma,j,s}\,\kappa,\quad [a^\sigma,b_j^s]=+\mathrm{gb}_{\sigma,j,s}\,\kappa .$$
All other brackets vanish. The second sign comes from super-skew-symmetry $[x,y]=-(-1)^{p(x)p(y)}[y,x]$.

Three elementary facts drive everything:

* **(F1) $\kappa^2=0$.** $\kappa$ is odd and central, so $2\kappa^2=[\kappa,\kappa]=0$. Every deformation is therefore *exactly* first order: $[X,Y]_\gamma=[X,Y]_0+\kappa\,\gamma(X,Y)$, with no higher terms.
* **(F2) $\kappa$ is supercentral.** $\kappa u=(-1)^{p(u)}u\kappa$, hence $[X,\kappa W]=(-1)^{p(X)}\kappa[X,W]$ and $[\kappa W,Y]=\kappa[W,Y]$.
* **(F3) Quadratics close modulo the center.** Every bracket of generators is central. So for $x,y,z,w\in V$, $[xy,zw]$ is a sum of single contractions (a central element times a quadratic) and double contractions (central scalars). Hence
 $$[\mathfrak g,\mathfrak g]\subset \mathfrak g\;\oplus\;\kappa\,\mathfrak g\;\oplus\;(\mathbf C1\oplus\mathbf C\kappa).$$

**Parity bookkeeping.** $[b,a]$ is odd and $\kappa$ is odd, so the gb are ordinary complex numbers (even scalars). The "parity 1" in `C_inhomogeneous_definition.md` is the parity carried by the deformation term $\kappa\cdot\mathrm{gb}$. Equivalently, $\gamma$ is an **odd** 2-cochain: $p(\gamma(X,Y))=p(X)+p(Y)+1$. That is exactly the parity of $\delta f$ for odd $f$. If the gb were taken to be Grassmann-odd, then $\mathrm{gb}\,\kappa$ would be even and $[b,a]$ would break homogeneity. So "even scalars" is the only consistent reading.

---

## 2. How I handle "as an adjoint representation / up to scalar"

The definition asks for $\gamma=\delta f$ "as an adjoint representation … up to scalar". I read this as follows, and the computation is set up the same way.

1. **Quotient by the center.** By (F3), the bracket of two elements of $\mathfrak g\subset\mathcal U(A)$ is
 $$[Z_a,Z_b]=\sum_k C_{ab}^k Z_k+\kappa\sum_k\gamma_{ab}^k Z_k+\big(s_{ab}\cdot 1+t_{ab}\cdot\kappa\big).$$
 The last term lies in the center of $\mathcal U(A)$. It acts by zero in the adjoint representation, and it is not an element of $\mathfrak g$, so $\delta f$ cannot produce it. The relevant Lie superalgebra is therefore $L=\mathfrak g\oplus\kappa\mathfrak g$ (the abelian extension of the definition doc), with brackets taken modulo $\mathbf C1\oplus\mathbf C\kappa$. The identity $\gamma=\delta f$ is required in $L$, i.e. on the coefficients $\gamma_{ab}^k$.
2. **The scalar terms depend only on the basis.** I ran two bases:
 * the **super-symmetrized basis** $S(xy)=\tfrac12(xy+(-1)^{p(x)p(y)}yx)$. Here **no** scalar terms appear at all: $s_{ab}=t_{ab}=0$ for all $a,b$ and $n=1,2,3$. So in this basis $\gamma=\delta f$ holds *exactly*, with no quotient needed;
 * the **literal generators of `Cn1_definition.md`** ($E=a^+b^-$, $H_{n+1}=-b_n^+b_n^--\tfrac12$, …). Here central terms $t_{ab}\kappa$ do appear: in 20, 84 and 180 ordered pairs for $n=1,2,3$. They come from $a^\sigma b-b\,a^\sigma=\mathrm{gb}\,\kappa$, i.e. from the non-symmetrized ordering. Once they are discarded as prescribed, triviality holds in this basis too.

 Changing basis by $Z_i\mapsto Z_i+(\text{scalar})+\kappa(\text{scalar})$ moves only the central part. The conclusion is the same either way.
3. **"Up to scalar" as overall rescaling.** If someone instead reads it as $\gamma=c\,\delta f$ for some $c\in\mathbf C^\times$, nothing changes: $\delta$ is linear, so $\gamma=c\,\delta f=\delta(cf)$.

---

## 3. Proof (all $n$)

### 3.1 Untwisting the oscillators
For $\sigma\in\{+,-\}$ define
$$\lambda_\sigma=\sum_{j=1}^n\big(\mathrm{gb}_{\sigma,j,-}\,b_j^+-\mathrm{gb}_{\sigma,j,+}\,b_j^-\big),\qquad \tilde a^\sigma:=a^\sigma+\kappa\lambda_\sigma .\tag{3.1}$$
$\tilde a^\sigma$ is odd. Using (F1) and (F2):
* $[b_j^-,\tilde a^\sigma]=-\mathrm{gb}_{\sigma,j,-}\kappa+\kappa[b_j^-,\lambda_\sigma]=-\mathrm{gb}_{\sigma,j,-}\kappa+\mathrm{gb}_{\sigma,j,-}\kappa=0$. Similarly $[b_j^+,\tilde a^\sigma]=-\mathrm{gb}_{\sigma,j,+}\kappa+\mathrm{gb}_{\sigma,j,+}\kappa=0$.
* $\{\tilde a^+,\tilde a^-\}=1+\kappa\cdot(\text{multiple of }\kappa)=1$, and $(\tilde a^\pm)^2=\kappa\,[\lambda_\pm,a^\pm]\in\mathbf C\kappa^2=0$.

So $\{\tilde a^\pm,b_j^\pm\}$ satisfy the **undeformed** relations inside the deformed $\mathcal U(A)$.

### 3.2 Comparing the two copies of $\mathfrak g$
Let $Z_i=P_i(a,b)$ be the basis of $\mathfrak g$ (non-commutative quadratic polynomials) and set $\tilde Z_i:=P_i(\tilde a,b)$. By 3.1 the $\tilde Z_i$ satisfy the undeformed structure constants: $[\tilde Z_a,\tilde Z_b]=\sum_k C_{ab}^k\tilde Z_k$ modulo the center. Substituting $a=\tilde a-\kappa\lambda$ and using $\kappa^2=0$ gives
$$Z_i=\tilde Z_i+\kappa H_i,\qquad H_i=\sum_j h_{ji}Z_j\ (\text{mod center}).\tag{3.2}$$
Expand $[Z_a,Z_b]=[\tilde Z_a+\kappa H_a,\tilde Z_b+\kappa H_b]$ with (F2), and replace $\tilde Z_k=Z_k-\kappa H_k$:
$$\gamma(Z_a,Z_b)=(-1)^{p_a}[Z_a,H_b]-(-1)^{(p_a+1)p_b}[Z_b,H_a]-H([Z_a,Z_b])=(\delta h)(Z_a,Z_b).$$
This is exactly the coboundary formula of `C_coboundary_definition.md` with $f=h$. The map $h$ is odd because $p(\kappa)=1$. ∎

### 3.3 Closed form of $f$ (symmetrized basis)
From $a\,y=\tilde a\,y-\kappa\lambda y$, $y\,a=y\tilde a-\kappa y\lambda$ and the analogous expansion of $a^+a^--a^-a^+$:
$$\boxed{\;f(S(b\,b'))=0,\qquad f\big(S(a^\sigma y)\big)=-S(\lambda_\sigma\,y)\ \ (y\in\{b_j^\pm\}),\qquad f\big(S(a^+a^-)\big)=S(a^+\lambda_-)-S(a^-\lambda_+).\;}\tag{3.3}$$
For example, with $n=1$ and only $\mathrm{gb}_{+,1,+}=1$: $f(S(a^+b^+))=S(b^+b^-)$, $f(S(a^+b^-))=S(b^-b^-)$, $f(S(a^+a^-))=S(a^-b^-)$. This matches `closed_form_f.phi_per_gb` in the artifact.

### 3.4 Non-vanishing and uniqueness
* $\gamma_{\mathrm{gb}}\neq0$ for $\mathrm{gb}\ne0$. For instance (n=1, symmetrized) $\gamma(S(a^\sigma b^s),S(a^\sigma b^s))=2\,\mathrm{gb}_{\sigma,1,s}\,S(a^\sigma b^s)$, and the same pattern holds for every $j$. The computed rank of $\mathrm{gb}\mapsto\gamma$ is $4n$.
* $\ker\delta$ on odd 1-cochains contains $\operatorname{ad}_Y$ for every $Y\in\mathfrak g_{\bar1}$. By super-Jacobi, $[Y,[X,Z]]=[[Y,X],Z]+(-1)^{p_X}[X,[Y,Z]]$, and this gives $\delta(\operatorname{ad}_Y)=0$. Since $Z(\mathfrak g)=0$, this subspace has dimension $4n$. The computed kernel dimension is exactly $4n$, so $\ker\delta=\operatorname{ad}(\mathfrak g_{\bar1})$.

**Remark.** This is consistent with the general expectation that $C(n+1)$ is rigid ($H^2(\mathfrak g,\mathfrak g)=0$, and hence also for the parity-shifted module $\kappa\mathfrak g$). The proof above does not use that fact. It is constructive and self-contained.

---

## 4. Computational verification

`python3 verification/cn1_triviality.py 1 2 3` (about 16 s) does everything with exact rational arithmetic. gb are symbolic, as polynomials over $\mathbf Q$.

1. It implements PBW normal ordering in $\mathcal U(A)$ from the deformed generator brackets of §1. Nothing is assumed about $\mathfrak g$.
2. It builds both bases, computes all $[Z_a,Z_b]$, and decomposes each one as $C+\kappa\gamma+$central. It asserts closure (no other words remain), that $C$ is gb-independent and equal to the gb=0 computation, and that $\gamma$ is linear in gb.
3. It checks super-Jacobi for $C$, and the 2-cocycle condition for $\gamma$ (Jacobi on $L$ at first order in $\kappa$).
4. It sets up $\gamma=\delta f$ as a linear system in all odd unknowns $\phi_{ij}$ and solves it by exact sparse elimination, separately for each of the $4n$ elementary gb directions. By linearity this covers all gb.
5. It independently verifies the closed-form $f$ of (3.3) by substitution.
6. **Negative controls:** five random odd, super-antisymmetric elementary cochains per case are tested. A correct solver must reject them, and every one is rejected.

| case | $\dim\mathfrak g$ | odd unknowns | rank $\delta$ | $\dim\ker\delta$ | rank gb→γ | cocycle | all gb trivial | closed-form $f$ | controls rejected | pairs w/ central terms |
|---|---|---|---|---|---|---|---|---|---|---|
| n=1 sym | 4\|4 | 32 | 28 | 4 | 4 | ✓ | ✓ | ✓ | 5/5 | 0 |
| n=1 Cn1 | 4\|4 | 32 | 28 | 4 | 4 | ✓ | ✓ | ✓ | 5/5 | 20 |
| n=2 sym | 11\|8 | 176 | 168 | 8 | 8 | ✓ | ✓ | ✓ | 5/5 | 0 |
| n=2 Cn1 | 11\|8 | 176 | 168 | 8 | 8 | ✓ | ✓ | ✓ | 5/5 | 84 |
| n=3 sym | 22\|12 | 528 | 516 | 12 | 12 | ✓ | ✓ | ✓ | 5/5 | 0 |
| n=3 Cn1 | 22\|12 | 528 | 516 | 12 | 12 | ✓ | ✓ | ✓ | 5/5 | 180 |

### Artifact format (`verification/artifacts/cn1_n{n}_{sym|cn1}.json`)
* `basis`: index, name, parity.
* `gb_labels`: ordering of the $4n$ parameters `gb[σ,j,s]`.
* `structure_constants["a,b"][k]` $=C_{ab}^k$ (rational strings).
* `gamma["a,b"][k]`: $\gamma_{ab}^k$ as a linear form in gb.
* `discarded_central_scalars["a,b"]`: the central part that was removed ($1$ / $\kappa$ coefficients). It is empty in the symmetrized basis.
* `checks`, plus `coboundary_system` (rank, kernel, per-gb solvability, a particular solution $\phi$, negative controls).
* `closed_form_f.phi_per_gb[gb]["i,j"]` $=\phi_{ij}$ with $f(Z_j)=\sum_i\phi_{ij}Z_i$.
* `summary.json` collects the per-case checks.

To check a claim independently, load `structure_constants`, `gamma` and `closed_form_f`, then evaluate $(\delta f)_{ab}^k=(-1)^{p_a}\sum_i\phi_{ib}C_{ai}^k-(-1)^{(p_a+1)p_b}\sum_i\phi_{ia}C_{bi}^k-\sum_m C_{ab}^m\phi_{km}$ and compare it with $\gamma_{ab}^k$.

---

## 5. Answer to the issue

* **Consistency of the two structures.** For $n=1,2,3$ (and, by §3, all $n$) the deformed brackets close on $L=\mathfrak g\oplus\kappa\mathfrak g$ modulo the center. $\gamma_{\mathrm{gb}}$ is an odd 2-cocycle, and the coboundary operator of the definition doc has the sign convention that matches this $\kappa$-twisted extension (derived in §3.2).
* **Necessary and sufficient condition for triviality:** **none**. $\gamma_{\mathrm{gb}}$ is trivial for **every** $\mathrm{gb}\in\mathbf C^{4n}$.
* **Do nonzero gb satisfy $\gamma_{\mathrm{gb}}=\delta f$?** Yes, all of them. The deformation is nonzero as a cochain but cohomologically trivial. It is undone by the oscillator change $a^\sigma\mapsto a^\sigma+\kappa\lambda_\sigma$, with the explicit $f$ in (3.3), unique modulo $\operatorname{ad}(\mathfrak g_{\bar1})$.
