# Triviality of gb-Deformations of C(n+1) = osp(2|2n)

**Status**: concluded within this session, with one stated modelling assumption (Section 2).
**Artifacts**: `scripts/verify_cn1_triviality.py` (reproduces everything) and
`artifacts/cn1_triviality.json` (structured results for n = 1, 2, 3).

---

## 0. Startup verification

| File | Result |
|---|---|
| `docs/math/Cn1_definition.md` | Present. Contains no JSON schema information (it is prose plus LaTeX and one table). |
| `docs/math/C_inhomogeneous_definition.md` | Present. |
| `docs/math/C_coboundary_definition.md` | Present. |
| `docs/issues/issue_open.md` | Present. |
| `final_reflection_template.md` | Present. |
| `supplementary_metrics_template.md` | Present. |

All reads stayed inside the repository root. No web access and no external papers were used. The Frappat reference
(*Dictionary on Lie Algebras and Superalgebras*, arXiv:hep-th/9607161) was **not** consulted. Consulting it would need your
explicit approval, so every result below is derived from the in-repo definitions.

---

## 1. Result

**Theorem.** For every parameter choice gb = (gb_{σ,k}) ∈ C^{4n} (σ ∈ {+,−}, k ∈ {1,…,2n}), the inhomogeneous deformation
γ_gb is trivial. Explicitly, the odd linear map

  f_gb : b_k ↦ Σ_σ gb_{σ,k} a_1^σ,  f_gb(a_1^σ) = 0

trivializes it, in the sense that the deformed form B + κG_gb is carried to B by the infinitesimal change of basis
1 + κ f_gb. The set of trivial gb is therefore all of C^{4n}. The triviality condition is **empty**: there are no
necessary conditions on gb beyond gb being an arbitrary parity-1 parameter collection.

Equivalently, the gb-directions contribute nothing to the deformation classes of this type. No gb configuration is
non-trivial; the zero configuration is trivially so with f = 0.

Verified by computer for n = 1, 2, 3 (Section 5).

---

## 2. Model and modelling assumption (please read)

The inputs do not fix the g-valued cochain γ_gb explicitly. `C_inhomogeneous_definition.md` says that [a,b] = (a|b)κ for
mixed parity and that γ_gb is the κ-coefficient of the deformed bracket. But the κ-term of [b,a] lies in Cκ, not in g. To
get a g-valued cochain one must choose an identification. I therefore adopted the following reading, which I believe is
the one the document intends:

- **V = C^{2n|2}**: even part spanned by the bosonic modes b_k (k = 1..2n), odd part by the fermionic modes a_1^± (σ = ±).
- **Undeformed form B**: super-skew, with block-diagonal form B = diag(Ω, I₂), where Ω is symplectic (giving sp(2n)) and I₂
  is symmetric (giving so(2)).
- **osp(B)** = {X ∈ gl(V) : X^T B + D_{p(X)} B X = 0}, with D_q = diag((−1)^{q p_i}). This has even part so(2) ⊕ sp(2n) and
  odd part of dimension 4n.
- **Deformation**: the mixed-parity part of the pre-oscillator form is deformed, B_κ = B + κG_gb. Here G_gb is the mixed
  super-skew form with G(b_k, a^σ) = gb_{σ,k} (up to an overall sign that does not affect triviality). This is exactly
  the statement [b_k, a^σ] = (mixed term) κ in the document.
- **Triviality**: the deformation is trivial iff G_gb is in the image of the infinitesimal action of odd F on B,
  i.e. G_gb = F·B := F^T B + D_1 B F for some odd F. This is the form-level version of "γ = δf".

**Caveat.** This identification is an interpretation. If the intended γ_gb is defined differently (for example through a
different projection of κ-valued terms onto g), the conclusion may change. I could not check that against a source, because
the document does not give the formula and I have not accessed Frappat. This is the main point to confirm with the human
reviewer.

---

## 3. Handling of the "up to scalar" condition

`C_coboundary_definition.md` Section 3 says γ = δf "up to scalar". Read literally this means ∃ c ∈ C with γ = c·δf, and
there are two cases:

1. **c ≠ 0**: since δ is linear, γ = c·δf = δ(c·f). So the scalar is absorbed into the trivializer f' = c·f, and nothing new is gained.
2. **c = 0**: this forces γ = 0, which is already trivial with f = 0.

So "up to scalar" does not change the notion of triviality. The set of trivial cochains is a linear subspace, and the
scalar-tolerant condition defines the same subspace. The analogous freedom in the form picture is B ↦ (1 + cκ)B, which
changes G by cB. Since B is even, cB has no odd part, so this freedom cannot alter any odd gb. This is verified in the
script (the odd part of B is zero).

---

## 4. Proof

Write F = (F_{k,i}) for odd F. Then F maps bosons to fermions and fermions to bosons. Set

  Φ_F := F·B = F^T B + D_1 B F.

**(a) Support.** Because B is block-diagonal, Φ_F(x, y) = 0 whenever x, y have the same parity. So Φ_F is purely mixed.
This is a short computation, and the script confirms it symbolically for n = 1, 2, 3.

**(b) Surjectivity onto mixed forms.** Let F be the closed-form map b_k ↦ Σ_σ gb_{σ,k} a^σ, with F(a^σ) = 0 (so the
fermion-to-boson block P is zero). Then for bosonic row k and fermionic column (2n+σ):

  Φ_F[k, 2n+σ] = Σ_m F[m, k] B[m, 2n+σ] = F[2n+σ, k] = gb_{σ,k} = G[k, 2n+σ].

Since both Φ_F and G are super-skew and purely mixed, Φ_F = G. This gives the trivialization.

**(c) Infinitesimal invariance.** Equality Φ_F = G implies that the deformed family osp(B + κG) is, to first order, the
conjugate of osp(B) by 1 + κF. Concretely, for each X ∈ osp(B) of parity q, with Z = [F, X], the identity

  Z·B − X·G = 0    (sign −1)

holds for every basis element X. The sign −1 was determined by the computation (the sign +1 version fails); see Section 5.
This is the statement that the stabilizer subalgebra of the deformed form is the conjugate of osp(B) by the trivializing
map.

**(d) No obstruction (dimension count).** The odd part of gl(V) has dimension 8n. The kernel of F ↦ F·B on odd F is the odd
part of osp(B), of dimension 4n. So the image has dimension 8n − 4n = 4n. The mixed super-skew forms also form a
4n-dimensional space, and the image lies in it by (a). Hence the map is surjective, and every mixed G is hit.
This is exactly the statement that there are no obstructions.

**(e) Kernel.** The solutions of F·B = G form an affine space over the odd part of osp(B), of dimension 4n. So the
trivializer is unique only up to the 4n free parameters of osp₁ (the automorphisms of the undeformed form), as expected.

---

## 5. Computational support

Script: `scripts/verify_cn1_triviality.py` (sympy, exact arithmetic). Run with
`python3 -I scripts/verify_cn1_triviality.py`. It writes `artifacts/cn1_triviality.json`.

| n | osp dim (computed / expected) | rank of linear system for F | free params in F | obstruction constraints on gb | all gb trivial | closed-form F verified | first-order check (sign −1) |
|---|---|---|---|---|---|---|---|
| 1 | 8 / 8 | 4 | 4 | none (rank 0) | yes | yes | all X pass |
| 2 | 19 / 19 | 8 | 8 | none (rank 0) | yes | yes | all X pass |
| 3 | 34 / 34 | 12 | 12 | none (rank 0) | yes | yes | all X pass |

Other checks, all passing for n = 1, 2, 3:

- Dimensions: even part 2n²+n+1 and odd part 4n. These match the table in `Cn1_definition.md`, which confirms the convention.
- The non-mixed part of Φ_F is identically zero as a function of F.
- The particular solution returned by exact Gauss–Jordan elimination satisfies F·B − G = 0 symbolically.
- Three random integer gb per n: F·B = G holds, and the first-order invariance holds.
- The obstruction computation uses the left kernel of the coefficient matrix A. Its image under b(gb) gives the exact
  constraints on gb. Here that list is empty.

The JSON file is the structured artifact for later work. It records the undeformed form B, the conventions, the dimension
counts, the constraint lists, the particular solutions, and the random checks.

---

## 6. Limitations

1. **Model dependence.** The result is for deformations of the form B. Other classes of H²(g,g) (for example deformations
   that move the so(2) factor or the sp(2n) factor independently) are not covered. So the claim is that the **gb family is
   trivial**. It is not a claim that osp(2|2n) is rigid.
2. **Parity of κ.** The document makes κ odd. I treated κ as a formal parameter in the linear computations, with sign
   conventions fixed by the computer checks rather than by a full Grassmann calculus. Signs of individual gb can differ by
   convention without changing the triviality statement.
3. **Cochain-level identity not computed.** I verified triviality at the level of the form and the first-order invariance
   of the subalgebra. I did not expand the deformed bracket on a basis of g to compare it with δf entry by entry. That is
   the natural next check, and the artifact is set up for it.
4. **No literature check.** Frappat and the arXiv paper were not consulted. Consistency with published results on
   osp(2|2n) deformations is unverified.

---

## 7. Answer to the issue's questions

- **Necessary and sufficient conditions on gb for triviality**: none. Every gb is trivial, with trivializer
  f_gb(b_k) = Σ_σ gb_{σ,k} a^σ (up to the 4n free parameters of osp₁).
- **Non-zero configurations trivial?** Yes, all of them.
- **Role of "up to scalar"**: harmless (Section 3).

---

## 8. Audit disclosure

- Files accessed: only inside the repository root.
- Web access or external papers: none.
- Computations: the script in `scripts/` and the artifact in `artifacts/`, both generated in this session.
- External AI assistants or agent tools: none.
