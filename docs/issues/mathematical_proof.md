# Triviality of the inhomogeneous (gb) deformation of C(n+1) = osp(2|2n)

## Result

**Theorem.** For every n ≥ 1 and **every** choice of parameters `gb_{σ,j,s}` (σ,s ∈ {±}, 1 ≤ j ≤ n; 4n complex numbers), the deformation γ_gb is trivial: γ_gb = δf for an odd linear map f = f_gb that depends linearly on gb.

So the triviality condition is vacuous: the set of gb for which γ_gb = δf is all of C^{4n}. There is no non-zero gb for which γ_gb is non-trivial. The class of γ_gb in the odd part of H²(g, g) is always 0.

The proof is analytic (§2–3). I also checked it exactly for n = 1, 2, 3 (§5).

## 1. Setup and conventions

Everything is taken from `docs/math/*.md`.

* Work in U(A)/(K=1). The generators are a⁺, a⁻ (odd), b_j^± (even) and κ (odd, central). Central odd means κx = (-1)^{p(x)} xκ and κ² = ½[κ,κ] = 0.
* The relations are {a⁻,a⁺} = 1 and [b_j⁻,b_l⁺] = δ_jl. The deformation adds [b_j^s, a^σ] = -gb_{σ,j,s} κ, and by supersymmetry [a^σ, b_j^s] = +gb κ.
* **Basis of g.** Take the Weyl-symmetrised quadratics Q_{uv} = ½(uv + (-1)^{p_u p_v} vu). This gives dim g = (2n²+n+1 | 4n), matching the table in `Cn1_definition.md`.
* **Bracket.** [X,Y]_gb = [X,Y]₀ + κ·γ(X,Y), with κ on the left. This is the convention in which `(δf)` of `C_coboundary_definition.md` arises (see §3).
* **Single contraction.** For symmetrised quadratics the supercommutator is a single contraction, because the double-contraction term is a scalar that cancels in the commutator. Hence [X,Y]_gb has no scalar term and no κ·1 term. The code asserts this for every pair of basis elements. In particular γ takes values in g, not in g ⊕ Cκ.
* **Why κ² = 0 matters.** The deformed bracket is exactly affine in gb, so γ_gb = Σ gb_i γ_i with no higher-order terms. γ_gb is automatically a 2-cocycle, because the Jacobi identity holds in U(A).

## 2. Why triviality holds: a gauge transformation

Define the odd linear map β: V → V by β(b) = 0 and, for σ = ±,

  β(a^σ) = Σ_j ( -gb_{σ,j,-} b_j⁺ + gb_{σ,j,+} b_j⁻ ).

This is the unique odd map for which the redefinition **a′^σ = a^σ + κβ(a^σ), b′ = b** removes the mixed brackets.

* For b even, [b_j^s, κ y] = κ[b_j^s, y]. So [b_j^s, a′^σ] = κ( -gb_{σ,j,s} + Σ β^σ_{j′,s′} ω₀(b_j^s, b_{j′}^{s′}) ).
* The form ω₀ on the bosonic part is non-degenerate. Hence the displayed β makes the bracket vanish: [b_j^s, a′^σ] = 0.
* The remaining brackets are unchanged. [a, κβ(a′)] = ±κ[a, β(a′)] = ±κ·(gb κ) = 0 because κ² = 0.

Hence (a′, b) satisfy the **undeformed** relations. The map φ: Z ↦ Z(a′, b) is an isomorphism from the undeformed algebra onto the deformed one, to all orders in κ.

On quadratics, φ(Q_{uv}) = Q_{uv} + κ·f(Q_{uv}), where f is the derivation-type extension of β:

  f(Q_{uv}) = Q_{βu,v} + (-1)^{p_u} Q_{u,βv}.

Since β is odd, f: g → g is an odd linear map. It preserves g because the product of two linear elements is symmetrised again, and no constant term appears.

## 3. Why this gives γ = δf, including the sign

Take φ(X) = X + κf(X), as above. On L = g ⊕ κg the adjoint extension gives [X, κY] = (-1)^{p(X)}κ[X,Y] and [κY, X] = κ[Y,X]. Then

  [φX, φY] - φ([X,Y]) = κ{ (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y]) } = κ·δf(X,Y).

This is exactly the formula in `C_coboundary_definition.md`, with no extra signs.

Since φ is an isomorphism onto the deformed algebra, [φX, φY]_gb = φ([X,Y]₀) up to the order-κ bookkeeping. Comparing the κ-parts gives γ_gb = ∓δf, and the sign is fixed by convention. In the code I define f with the sign that gives **+γ**. The `explicit_f` function in `code/cn1_triviality.py` is the map above, taken with the opposite sign of β (β → -β) to obtain δf = +γ. The exact check in §5 passes with this sign.

## 4. Handling "adjoint representation / up to scalar"

* **Scalar.** The condition "γ = δf up to scalar" means γ = c·δf with c ≠ 0, or γ = 0. Coboundaries form a linear space, so c can be absorbed into f ↦ f/c. "Up to scalar" therefore changes nothing: the exact statement γ = δf and the up-to-scalar statement are equivalent.
* **Adjoint representation.** All brackets in δf are taken in the adjoint module, with κ acting trivially (L = g ⊕ κg is an abelian extension by the adjoint representation). Constants in U(A), meaning κ·1 and K-terms, are handled by the symmetrised basis, which makes them vanish identically (§1). The alternative (normal-ordered) basis differs from this one by Z ↦ Z + c(Z)κ with c: g → C, which is a change of basis by a central element and never mixes κg and g. Choosing the symmetrised basis therefore does not affect the g-valued γ.
* **Non-uniqueness of f.** f is determined only up to ker δ on odd maps. This kernel is exactly the odd derivations. Numerically its dimension is 4n, which is the dimension of ad(g_odd). So H¹_odd(g, g) = 0 and f_gb is unique modulo ad ξ, ξ ∈ g_odd.
* **Injectivity of gb ↦ γ.** Every γ_i (unit parameter) is non-zero, and the rank of [δ | γ_1…γ_4n] equals the rank of δ, so all γ_i lie in the coboundary space. I did not separately compute the rank of {γ_i} alone, so I do not claim that gb ↦ γ_gb is injective. In the argument above, γ_gb = 0 only if f_gb is a derivation, which I did not decide analytically.

## 5. Computational support

Code: `code/cn1_triviality.py`, run as `python3 code/cn1_triviality.py 1 2 3`. The super-Jacobi check is in `code/debug_jacobi.py`. Exact arithmetic is used throughout (`fractions.Fraction`), in a PBW normal-ordering engine for U(A)/(K=1).

Artifacts: `artifacts/C{n+1}_n{n}_verification.json`, for n = 1, 2, 3, and `artifacts/summary.json`. Each file contains the basis, the undeformed structure constants, γ_i for each of the 4n unit parameters, and the explicit f for each. Entries `[a,b,c,coef]` mean that the coefficient of Z_c in [Z_a, Z_b] (or in γ(Z_a,Z_b)) is `coef`.

| n | algebra | dim g (even\|odd) | #gb | odd f unknowns | rank δ on odd maps | dim ker δ (odd) | rank [δ\|γ] | trivial gb subspace | exact δf_gb = γ_gb |
|---|---|---|---|---|---|---|---|---|---|
| 1 | osp(2\|2) | 4\|4 | 4 | 32 | 28 | 4 | 28 | 4 of 4 | True |
| 2 | osp(2\|4) | 11\|8 | 8 | 176 | 168 | 8 | 168 | 8 of 8 | True |
| 3 | osp(2\|6) | 22\|12 | 12 | 528 | 516 | 12 | 516 | 12 of 12 | True |

All values are those in `artifacts/summary.json`. Every γ_i is non-zero (at least 21, 57 and 109 non-zero entries for n = 1, 2, 3).

Checks performed:
* The super-Jacobi identity for the undeformed structure constants holds for n = 1, 2, 3 with zero violations (`code/debug_jacobi.py`).
* For each of the 4n unit parameters, the explicit f satisfies δf = γ exactly (rational arithmetic) for n = 1, 2, 3.
* For a random gb, the least-squares residual of Δφ = γ_gb is about 1e-14 for each n. A float rank test is used here. The exact claim rests on the explicit f.
* Scalar residues (the constant and κ·1 terms) vanish for every pair of basis elements; the code asserts this.

A bug I found and fixed on the way: the first version lost a factor of 2 in Q_{uu} for even u because of a dictionary key collision, which broke the Jacobi identity (72 violations at n = 1). The committed code contains the fix, and all results above come from the fixed version.

## 6. Limits of this analysis

* I did not consult external references (Frappat et al.) and did not request web access.
* The result is for the parameter family exactly as defined in `C_inhomogeneous_definition.md`: only mixed bosonic/fermionic brackets, with κ nilpotent. It says nothing about other deformations of osp(2|2n).
* The ranks for n = 3 were computed in floating point (numpy `matrix_rank`). The exact statement for n = 3 is the rational check of δf = γ; the rank column is supporting evidence only.

## 7. Conclusion

γ_gb = δf_gb for all gb ∈ C^{4n}, with f_gb obtained by the gauge shift a^σ → a^σ + κβ(a^σ). The deformation is always trivial. No non-zero gb gives a non-trivial deformation.
