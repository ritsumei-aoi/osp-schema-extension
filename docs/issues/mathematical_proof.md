# Triviality of the inhomogeneous (gb) deformation of C(n+1) = osp(2|2n)

## Conclusion (Theorem)

For every n ≥ 1 and **every** choice of the 4n parameters gb_{σ,j,s}, the deformation γ_gb is trivial: γ_gb = δf for an explicit odd linear map f: g → g that is linear in gb.
There is no condition on gb. The map gb ↦ γ_gb is injective, so γ_gb = 0 only for gb = 0. Hence "nontrivial gb" does not exist, and no non-zero gb is "obstructed".

Supported by exact/numerical computation for n = 1, 2, 3 (`artifacts/cn1_triviality.py`, data in `artifacts/results.json`) and by the proof below for all n.

## 1. Setup and conventions

- Generators of A: b_j^± (even), a^± (odd), K = 1, κ (odd, central, κ² = 0). Undeformed relations: [b_k^-, b_l^+] = δ_kl, {a^-, a^+} = 1.
- Deformed relations: [b_j^s, a^σ] = −gb_{σ,j,s} κ. Skew-supersymmetry gives [a^σ, b_j^s] = +gb_{σ,j,s} κ.
- g = C(n+1) is spanned by **Weyl-symmetrized** quadratics: b_i b_j, a^+a^-, a b. This gives dim (2n²+n+1 | 4n) = 8, 19, 34 for n = 1, 2, 3 (checked by the code). For quadratic elements the commutator equals the first-order super Poisson bracket exactly, so there are no ordering constants. The bracket is a graded derivation in each argument, with every contraction coming from the form.
- Write [X,Y]_γ = [X,Y]_0 + κ γ(X,Y). γ(X,Y) is the sum of the single contractions between an a and a b (the κ-valued ones). The code asserts that the κ-free part is unchanged by gb, and that γ(X,Y) always lies in g (no term escapes g).
- The parity of γ is odd (p(γ(X,Y)) = p(X)+p(Y)+1), as is f. The coboundary uses the formula of `C_coboundary_definition.md` verbatim. [·,·] there is the undeformed bracket.

## 2. Proof of triviality (all n)

Realize the deformed oscillators inside the undeformed algebra by an odd shift. Let b0, a satisfy the undeformed relations and put

  b_j^s = b0_j^s + κ Σ_σ c^σ_{j,s} a^σ,  with c^{−σ'}_{j,s} = −gb_{σ',j,s}.

Since κ is central and κ² = 0:
- [b_j^s, a^{σ'}] = κ c^{−σ'}_{j,s} {a^{−σ'}, a^{σ'}} = −gb_{σ',j,s} κ. This is the required relation.
- [b, b'] is unchanged, because every κ-term pairs κ·a with a b0 (bracket 0) or with another κ-term (κ² = 0).
- So the deformed algebra A_gb is the image of A under an automorphism-like shift.

For a quadratic X in (a, b), X(b0 + κ c a, a) = X(b0, a) + κ f(X), where f(X) is the derivative of X in the direction b ↦ c a. Concretely f(b_i b_j) = c(b_i)·b_j + b_i·c(b_j) is odd in g, and f(b a) = c(b) a ∈ span(a^+a^-) ⊂ g, since (a^±)² = 0. Thus f maps g into g and is odd. Because [Φ(X), Φ(Y)] with Φ = id + κf is the bracket of undeformed elements, the κ-coefficient of the deformed bracket is exactly δf (this is the coboundary identity of the odd, κ-graded cochain), i.e.

  γ_gb = δf_gb,  f_gb linear in gb.

The code computes f_gb by this substitution for random integer gb and checks γ = +δf exactly (the sign matches +1 in n = 1, 2, 3, entry by entry over all N³ components).

## 3. Independent linear-algebra check

Unknowns: φ_ij (odd, i.e. parity(Z_i) ≠ parity(Z_j)). The matrix D of δ acts on φ. G is the matrix of gb ↦ γ.

| n | dim g | #gb | rank G | rank D | rank [D\|G] | all gb trivial | explicit f ↔ δf |
|---|---|---|---|---|---|---|---|
| 1 | 4\|4 | 4 | 4 | 28 | 28 | yes | sign +1 |
| 2 | 11\|8 | 8 | 8 | 168 | 168 | yes | sign +1 |
| 3 | 22\|12 | 12 | 12 | 516 | 516 | yes | sign +1 |

rank [D|G] = rank D means im G ⊂ im D: every gb direction is a coboundary, so no gb-condition arises. rank G = #gb means gb ↦ γ is injective: γ_gb = 0 iff gb = 0. Ranks are numpy floating-point ranks (`matrix_rank`), but the decisive identity γ = δf_explicit is an exact comparison on integer data (`np.allclose` on integer-valued arrays).

## 4. Handling of "adjoint representation / up to scalar"

1. **Adjoint representation.** The bracket is extended to L = g ⊕ κg, with κ acting trivially and κg ≅ g as the adjoint module. Hence γ takes values in g (≅ κg), and f is taken as an odd map g → g. This is what the code does: every κ-term is decomposed in the basis of g (an assertion fails if it left g).
2. **"Up to scalar."** I read this as a single **global** scalar: γ = c·δf with one c ≠ 0 (the same c for all X, Y). c can be absorbed into f (f ↦ f/c) and corresponds to rescaling κ, so it does not change the set of trivial deformations. If c = 0 were allowed, it would force γ = 0, i.e. gb = 0 by injectivity.
   A *pointwise* scalar (a different c for each pair (X, Y)) would make the condition vacuous, because the scalars could scale any nonzero value, so I do not use it. In any case, for gb ≠ 0 the exact scalar is c = 1, as the check above shows.
3. The scalar freedom therefore only reflects normalization (κ ↦ λκ sends gb ↦ λ gb, f ↦ λ f). The triviality locus is the whole parameter space C^{4n}.

## 5. Artifacts

- `artifacts/cn1_triviality.py`: reproduces everything (runs in about 1 s). Run `python3 artifacts/cn1_triviality.py`.
- `artifacts/results.json`: for n = 1, 2, 3: ranks, flags, nonzero-γ counts. For n = 1 also the basis, the structure constants, the full γ structure for each unit gb_{σ,j,s}, and the explicit φ for a random gb.

## 6. Caveats

- Only n = 1, 2, 3 are computed. The all-n statement rests on the shift argument in §2 (an exact algebraic argument), which the computation confirms for n ≤ 3.
- I assumed K = 1, the Weyl-symmetrized basis, and the sign conventions stated in §1. A different sign convention in the coboundary formula could change the sign between γ and δf (a global scalar −1, which is absorbed in f). The sign found is +1 with the formula as given.
- No external sources (Frappat etc.) were accessed, and no files outside the repository were read.
