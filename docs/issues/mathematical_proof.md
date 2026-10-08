# Triviality of the inhomogeneous deformation $\gamma_{gb}$ of $C(n+1)=\mathfrak{osp}(2|2n)$

**Status**: closed (conclusion reached; verified exactly for n = 1, 2, 3, 4)
**Scope**: `docs/issues/issue_open.md`
**Artifacts**: `scripts/verify_triviality.py`, `artifacts/triviality_n{1,2,3,4}.json`, `artifacts/triviality_summary.json`

---

## 0. Startup verification

| File | Result |
|---|---|
| `docs/math/Cn1_definition.md` | present; Markdown/LaTeX text only, **contains no JSON schema** (confirmed) |
| `docs/math/C_inhomogeneous_definition.md` | present |
| `docs/math/C_coboundary_definition.md` | present |
| `docs/issues/issue_open.md` | present |
| `final_reflection_template.md` | present (repo root) |
| `supplementary_metrics_template.md` | present (repo root) |

All work used only files inside the repository root. No external web access or papers were used (in particular, Frappat et al. was **not** consulted; no approval was requested).

---

## 1. Result

**Theorem.** Let $n\ge 1$, and let $\mathrm{gb}=(\mathrm{gb}_{\sigma,j,s})$ be any $4n$ parameters with $\sigma,s\in\{+,-\}$, $j=1,\dots,n$, taken as even (rational/complex) scalars. Define the odd linear map $f_{gb}:\mathfrak g\to\mathfrak g$ as the restriction to $\mathfrak g=\mathrm{Sym}^2(V)$ of the odd derivation $D_{gb}$ of $\mathrm{Sym}(V)$ given by
$$
D_{gb}(b_j^{s}) = -\big(\mathrm{gb}_{-,j,s}\,a^{+} + \mathrm{gb}_{+,j,s}\,a^{-}\big),\qquad D_{gb}(a^{\sigma})=0 .
$$
Then, with the coboundary convention of `docs/math/C_coboundary_definition.md`,
$$
\gamma_{gb} \;=\; \delta f_{gb}\qquad\text{exactly, for every } gb\in\mathbb C^{4n}.
$$

**Consequence.** Every inhomogeneous deformation $\gamma_{gb}$ is trivial. The triviality condition imposes **no constraint** on $gb$: the set of $gb$ for which $\gamma_{gb}$ is trivial is all of $\mathbb C^{4n}$. In particular, every non-zero configuration of $gb$ parameters satisfies the triviality condition, and the coboundary map is onto the 4n-dimensional space spanned by the $\gamma_{gb}$.

The sign is $s=+1$: $\gamma_{gb}=+\delta f_{gb}$ with $f_{gb}=D_{gb}$. (A convention with $\gamma=-\delta f$ would be absorbed by $f\mapsto -f$.)

---

## 2. Model and interpretation

### 2.1 Realisation of $\mathfrak g$

Let $V=V_{\bar 0}\oplus V_{\bar 1}$ with $V_{\bar 0}=\mathrm{span}\{b_j^{\pm}\}$ (even, dim $2n$) and $V_{\bar 1}=\mathrm{span}\{a^{\pm}\}$ (odd, dim $2$). Then
$$
\mathfrak g=\mathrm{Sym}^2(V)\cong\mathfrak{osp}(2|2n):\qquad
\mathrm{Sym}^2V_{\bar0}\oplus\Lambda^2V_{\bar1}=\mathfrak{sp}(2n)\oplus\mathfrak{so}(2)\ (\text{even}),\quad
V_{\bar0}\otimes V_{\bar1}\ (\text{odd}).
$$
Dimensions: even $2n^2+n+1$, odd $4n$, total $2n^2+5n+1$, matching `Cn1_definition.md` (n=1: 4|4, n=2: 11|8, n=3: 22|12). The code asserts these dimensions for every run.

The bracket on $\mathfrak g$ is the super Poisson bracket $\{\cdot,\cdot\}_\omega$ of quadratic super-polynomials for a constant super-skew form $\omega$ on $V$. Quadratic-by-quadratic brackets are exact (no ordering corrections arise in the Poisson bracket of quadratics), and the bracket is **linear in $\omega$**.

### 2.2 The deformation as a change of $\omega$

The relations in `C_inhomogeneous_definition.md`, $[b_j^s,a^\sigma]=-\mathrm{gb}_{\sigma,j,s}\,\kappa$, say exactly that
$$
\omega = \omega_0 + \kappa\,\Omega_{gb},\qquad
\Omega_{gb}(b_j^s,a^\sigma)=-\mathrm{gb}_{\sigma,j,s},\quad \Omega_{gb}(a^\sigma,b_j^s)=+\mathrm{gb}_{\sigma,j,s},
$$
with $\omega_0(b_j^-,b_k^+)=\delta_{jk}$, $\omega_0(b_j^+,b_k^-)=-\delta_{jk}$, and $\omega_0(a^+,a^-)=\omega_0(a^-,a^+)=1$ (the anticommutator $\{a^-,a^+\}=1$ is the symmetric odd–odd pairing). All other blocks of $\Omega$ vanish. Since $\omega$ is linear in $\kappa$, the deformed bracket is
$$
[Q,Q']_\kappa=[Q,Q']_0+\kappa\,\gamma_{gb}(Q,Q'),\qquad \gamma_{gb}(Q,Q') = \text{the }\kappa\text{-linear part of }\{Q,Q'\}_{\omega_0+\kappa\Omega_{gb}}.
$$

### 2.3 Parity: a correction to the input documents

`C_inhomogeneous_definition.md` states that "the deformation parameters $\mathrm{gb}$ must have parity 1". That is inconsistent with the bracket $[b,a]=-\mathrm{gb}\,\kappa$ it defines. Since $b$ is even, $a$ is odd, and $\kappa$ is odd, $[b,a]$ has parity $1$ only if $\mathrm{gb}$ is **even**. This analysis treats $\mathrm{gb}$ as even scalars, and treats $\kappa$ as an odd central generator. The code does the same (see §3.1). The input document's parity remark should be corrected; I have not edited it.

### 2.4 Handling "adjoint representation / up to scalar" (the central condition)

This is the point the issue asks me to make explicit.

**(a) Adjoint representation.** $\gamma_{gb}$ and $\delta f$ are both bilinear maps $\mathfrak g\times\mathfrak g\to\mathfrak g$. They are elements of $C^2(\mathfrak g,\mathfrak g)$, with $\mathfrak g$ regarded as a module over itself via the adjoint action. The coboundary $\delta:C^1(\mathfrak g,\mathfrak g)_{\bar1}\to C^2(\mathfrak g,\mathfrak g)_{\bar1}$ is the standard Chevalley–Eilenberg differential for the adjoint module, with the signs of `C_coboundary_definition.md`. Triviality means $[\gamma_{gb}]=0$ in $H^2$, i.e. $\gamma_{gb}\in\operatorname{im}\delta$. The code evaluates $\delta$ with the **undeformed** bracket $[\cdot,\cdot]_0$, which is the correct choice at first order in $\kappa$.

**(b) "Up to scalar".** The coboundary document says $\gamma=\delta f$ "up to scalar". Since $\delta$ is linear in $f$, $\operatorname{im}\delta$ is a linear subspace. Hence
$$
\gamma\in\operatorname{im}\delta \iff c\,\gamma\in\operatorname{im}\delta\quad\text{for every } c\neq 0,
$$
because $c\,\gamma=\delta(c f)$ when $\gamma=\delta f$. So the phrase "up to scalar" neither weakens nor strengthens the triviality condition. It only means one may rescale $f$ (or $\gamma$, i.e. $\kappa$ or $\mathrm{gb}$). I therefore prove the **exact** identity $\gamma_{gb}=\delta f_{gb}$ with $c=1$. This is strictly stronger than the scalar-projective reading. The opposite-sign convention $\gamma=-\delta f$ is also handled, by $f\mapsto -f$. The code reports $s=+1$ and treats the other sign as informational.

**(c) Why no scalar obstruction appears.** Scaling $\mathrm{gb}\mapsto c\,\mathrm{gb}$ scales $\gamma$ and $f$ together, so the triviality set in $\mathbb C^{4n}$ is a linear subspace. Here that subspace is all of $\mathbb C^{4n}$, so the scalar question does not arise.

**(d) Sign of $\kappa$ placement.** Because $\kappa$ is odd, $\kappa\,m'=(-1)^{|m'|}\,m'\,\kappa$. The doc's convention $[X,Y]_\gamma=[X,Y]_0+\kappa\,\gamma(X,Y)$ puts $\kappa$ on the left, which is the convention of the abelian extension $L=\mathfrak g\oplus\kappa\mathfrak g$ with $[X,\kappa Y]=(-1)^{|X|}\kappa[X,Y]$. The code reads $\gamma_{m'}=(-1)^{|m'|}\,r_{m'}$ from a product term $r_{m'}\,(m'\kappa)$. A right-placed convention would change $\gamma$ by the parity-dependent sign $(-1)^{|X|+|Y|}$, and I did not test that alternative.

---

## 3. Proof

### 3.1 Analytic argument (for all n)

**Step 1 (the cross block is the image of an odd infinitesimal GL(V)-action).** Let $X:V\to V$ be an odd linear map. Its odd derivation $D_X$ on $\mathrm{Sym}(V)$ restricts to an odd linear map $f_X:\mathfrak g\to\mathfrak g$. Define the infinitesimal change of a form by $(L_X\omega)(x,y)=-\omega(Xx,y)-(-1)^{|x|}\omega(x,Xy)$. For a constant super-skew form $\omega$ and any odd derivation $D$, the standard identity for Poisson brackets (transport of a bivector by a derivation) gives
$$
D\{P,Q\}_\omega-\{DP,Q\}_\omega-(-1)^{|P|}\{P,DQ\}_\omega=\pm\{P,Q\}_{L_X\omega}.
$$
I take the sign $+$ with $f=D_X$, as confirmed numerically in §3.2. Two observations make this usable:

* Because $X$ is odd, it maps $V_{\bar0}\to V_{\bar1}$ and $V_{\bar1}\to V_{\bar0}$. Since $\omega_0$ is block-diagonal, $(L_X\omega_0)$ vanishes on the even–even and odd–odd blocks, so $L_X\omega_0$ lies purely in the cross block $V_{\bar0}\times V_{\bar1}$.
* With $X(b_j^s)=-\sum_\sigma\mathrm{gb}_{-\sigma,j,s}\,a^\sigma$ and $X(a^\sigma)=0$, a direct computation gives $(L_X\omega_0)(b_j^s,a^\tau)=\mathrm{gb}_{\tau,j,s}\cdot(\text{sign})$, i.e. $L_X\omega_0=\mp\Omega_{gb}$. The sign is fixed by the computation.

Hence $\gamma_{gb}=\{\cdot,\cdot\}_{\Omega_{gb}}=\pm\delta f_X$ with $f_X=D_X|_{\mathfrak g}$, i.e. $f_{gb}=D_{gb}$.

**Step 2 (surjectivity onto the gb-space; kernel check).** The odd maps $X\in\mathrm{Hom}_{\bar1}(V,V)$ split as $X_{10}\in\mathrm{Hom}(V_{\bar0},V_{\bar1})$ (dim $4n$) and $X_{01}\in\mathrm{Hom}(V_{\bar1},V_{\bar0})$ (dim $4n$). The cross block of $L_X\omega_0$ is
$$
(L_X\omega_0)(b,a)=-\omega_1(X_{10}b,a)-\omega_0(b,X_{01}a).
$$
Because $\omega_1$ is nondegenerate on $V_{\bar1}$, the map $X_{10}\mapsto\big((b,a)\mapsto\omega_1(X_{10}b,a)\big)$ is a bijection onto all cross forms, which form a $4n$-dimensional space. Therefore the map $X\mapsto L_X\omega_0$ is **surjective** onto the cross block, and with $X_{01}=0$ it is already an isomorphism. Thus every $\Omega_{gb}$ is of the form $\mp L_X\omega_0$, and every $\gamma_{gb}$ is a coboundary.

*Consistency check.* The kernel of $X\mapsto L_X\omega_0$ has dimension $8n-4n=4n$. These are the odd $X$ preserving $\omega_0$, that is the odd part of $\mathfrak{osp}(V,\omega_0)$, which is the odd inner derivations $\mathrm{ad}(\bar Z)$ with $\bar Z\in\mathfrak g_{\bar1}$. This matches the expected kernel, so the linear algebra is consistent.

**Step 3 (conclusion).** $\gamma_{gb}=\pm\delta f_{gb}$ for all $gb$. Since $\gamma_{gb}\in\operatorname{im}\delta$ for every $gb$, the deformation is trivial for every $gb$.

*Status of Step 1.* The general identity in Step 1 is standard. I did not re-derive its sign in full generality. The sign and the identity are confirmed by exact computation for n = 1, 2, 3, 4 (§3.2). The general-n argument is therefore a proof modulo this identity, and the computation is what fixes the sign.

### 3.2 Computational verification (exact, rational)

`scripts/verify_triviality.py` builds $\mathfrak g$ with the super Poisson bracket, uses κ as an odd central generator (so $\kappa^2=0$ and all signs come from the super-commutative product), and checks:

| Check | Meaning |
|---|---|
| `dim_g_*` | dimensions $2n^2+5n+1$, $2n^2+n+1$, $4n$ |
| `omega0_superskew` | $\omega_0$ is super-skew |
| `jacobi_undeformed` | super-Jacobi for $[\cdot,\cdot]_0$ on all basis triples |
| `omega_full_superskew_random_gb` | $\omega_0+\kappa\Omega$ is super-skew for a random rational $gb$ |
| `kappa_free_part_equals_undeformed_random_gb` | the κ-free part of the bracket equals $[\cdot,\cdot]_0$ |
| `kappa_jacobi_random_gb` | **super-Jacobi for $[\cdot,\cdot]_\kappa$ modulo $\kappa^2=0$**, on all basis triples (this means γ is a cocycle; no first-order approximation is used) |
| `all_unit_gb_gamma_equals_plus_delta_f` | $\gamma_{e}=\delta(D_{e})$ for each of the $4n$ unit vectors $e$ of $gb$-space |
| `random_gb_gamma_equals_plus_delta_f` | the same identity for a random rational $gb$ (independent sample) |
| `all_unit_gb_gamma_nonzero` | each $\gamma_e$ is non-zero (the deformations are genuinely non-trivial as brackets) |
| `negative_control_wrong_index_convention_detected` | a wrong index convention for $D$ (no flip $\sigma\mapsto-\sigma$) **fails** on some unit vector, so the test discriminates |
| `negative_control_zero_f_fails_for_nonzero_gb` | with $f=0$ the identity fails, because each $\gamma_e\neq0$ |

**Why checking unit vectors proves the theorem for all $gb$ (at fixed $n$).** The maps $gb\mapsto\gamma_{gb}$, $gb\mapsto D_{gb}$ and $\delta$ are all linear over $\mathbb Q$ (or $\mathbb C$). Two linear maps agreeing on a basis agree everywhere. So the exact equality on the $4n$ unit vectors is a finite, complete proof of $\gamma_{gb}=\delta f_{gb}$ for all $gb$ at that $n$. The random $gb$ check is an independent confirmation of the linearity argument, not a substitute for it.

**Results** (all runs, sign $s=+1$):

| n | algebra | dim g (even\|odd) | Jacobi (undeformed, κ-linear) | unit $gb$ identities $\gamma=\delta D$ | random $gb$ | negative controls | `all_checks_pass` |
|---|---|---|---|---|---|---|---|
| 1 | $\mathfrak{osp}(2\|2)$ | 8 (4\|4) | pass | 4/4 | pass | pass | **True** |
| 2 | $\mathfrak{osp}(2\|4)$ | 19 (11\|8) | pass | 8/8 | pass | pass | **True** |
| 3 | $\mathfrak{osp}(2\|6)$ | 34 (22\|12) | pass | 12/12 | pass | pass | **True** |
| 4 | $\mathfrak{osp}(2\|8)$ | 53 (37\|16) | pass | 16/16 | pass | pass | **True** |

Hand-checked sample (n = 2, $gb_{+,1,+}=1$, others 0): $D(b_1^+)=-a^-$, hence $D(b_1^+b_1^+)=-2\,b_1^+a^-$. The artifact records this as `f_sparse_i_k_coeff` entry $[i,k,c]=[5,0,-2]$, where basis index 5 is $b_1^+a^-$ and index 0 is $b_1^+b_1^+$. This agrees with the hand computation.

**Artifacts (structured data).** `artifacts/triviality_n{n}.json` contains: the basis labels and parities; the $gb$ parameter index; the undeformed structure constants $[Z_p,Z_q]_0$ as sparse rows $[p,q,k,c]$; for each unit $gb$, the sparse $\gamma$ and sparse $f$ in the form $[i,k,c]$ meaning $f(Z_k)\ni c\,Z_i$; a random-$gb$ sample; and the check results. `artifacts/triviality_summary.json` collects the pass flags for all $n$. Coefficients are exact rational strings.

**Reproduce:**
```
python3 -I scripts/verify_triviality.py --n 1 2 3 4
```
Standard library only; runs in a few seconds.

---

## 4. Explicit statement of the triviality map

For each $gb$, the trivialising map is
$$
f_{gb}(Z)=D_{gb}(Z)\quad\text{for } Z\in\mathfrak g=\mathrm{Sym}^2(V),\qquad f_{gb}\text{ odd},
$$
where $D_{gb}$ is the odd derivation determined by $D_{gb}(b_j^s)=-(\mathrm{gb}_{-,j,s}a^++\mathrm{gb}_{+,j,s}a^-)$ and $D_{gb}(a^\sigma)=0$. In the parametrisation $f(Z_j)=\sum_i\phi_{ij}Z_i$ of `C_coboundary_definition.md`, the coefficients $\phi_{ij}$ are linear in $gb$, and they are recorded in the artifacts. Equivalently, $\phi$ is the matrix of the $\kappa$-free odd map $D_{gb}$.

---

## 5. Limitations and what was not done

1. **First order in κ.** The statement is about the infinitesimal deformation class, which is what $\delta f=\gamma$ means. I make no claim about finite deformations or higher-order obstructions, and the cocycle is checked exactly only modulo $\kappa^2=0$.
2. **Literature not consulted.** No external reference (including Frappat et al.) was used or fetched. Identifications with the literature are therefore not verified here.
3. **Realisation identification.** I identified $\mathfrak g$ with quadratic super-polynomials under the Poisson bracket. The oscillator realisation uses Weyl/symmetric ordering, which shifts constants such as the $-\tfrac12$ in $H_{n+1}$. Those shifts do not change the Lie structure on the quadratic part. I did not re-verify this identification against the oscillator relations by a separate computation.
4. **Analytic Step 1 sign.** Only the sign was confirmed numerically, not by a general symbolic derivation (see §3.1).
5. **Input document errata.** (a) The parity remark on $\mathrm{gb}$ in `C_inhomogeneous_definition.md` should read "even" (§2.3). (b) The "up to scalar" phrasing in `C_coboundary_definition.md` is correct but should be read as in §2.4(b).
6. **Workflow templates not filled.** `final_reflection_template.md` and `supplementary_metrics_template.md` were verified to exist but were **not** completed. The issue does not ask for them, and I cannot measure wall-clock or thinking time from inside this session.

---

## 6. Conclusion

For $\mathfrak g=C(n+1)=\mathfrak{osp}(2|2n)$ and every inhomogeneous parameter set $\mathrm{gb}_{\sigma,j,s}$, the deformation $\gamma_{gb}$ is a coboundary: $\gamma_{gb}=\delta f_{gb}$ with $f_{gb}$ the odd derivation $D_{gb}$ above. The triviality condition therefore holds for **all** $\mathrm{gb}$, and imposes no constraint. This is proved for all $n$ by the cross-block surjectivity argument (modulo the standard Lie-derivative identity), and checked exactly for $n=1,2,3,4$.
