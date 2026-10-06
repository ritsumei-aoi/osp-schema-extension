# Triviality of the inhomogeneous (gb) deformation of C(n+1) = osp(2|2n)

**Status: resolved.** Verified for n = 1, 2, 3 by exact computation; general-n proof below.

## Theorem

Let g = C(n+1) = osp(2|2n) and let γ_gb be the inhomogeneous deformation defined by
`[b_j^s, a_1^σ] = -gb_{σ,j,s} κ` (4n parameters). Then:

1. **Every** choice of gb gives a trivial deformation: there is an odd linear map f with γ_gb = δf.
   There is no non-trivial condition on gb; the set of trivial parameters is the whole space C^{4n}.
   In particular the answer to "does a non-zero gb satisfy γ_gb = δf?" is **yes, all of them do**.
2. An explicit solution is
   `f = D|_g`, where D is the odd derivation of S(V) with
   `D(a^σ) = Σ_{j,t} t · gb_{σ,j,t} · b_j^{-t}`  (t = ±1), `D(b_j^s) = 0`.
3. f is unique modulo ker δ, which (computed for n=1,2,3) has dimension dim g_odd = 4n, i.e. it consists
   exactly of the inner maps ad(Θ), Θ ∈ g_odd. So f is determined up to inner odd maps.
4. The map gb ↦ γ_gb is injective (rank 4n), so the deformation is non-zero as a cochain, yet always exact.

## Setup and conventions (what was actually computed)

* V = span{a^±, b_j^±}; A = V ⊕ CK ⊕ Cκ; K = 1, κ odd central, κ² = 0.
  Brackets: `{a^-,a^+} = 1`, `[b_k^-,b_l^+] = δ_kl`, `[b_j^s,a^σ] = -gb_{σ,j,s}κ`, `[a^σ,b_j^s] = +gb κ`
  (super-skew-symmetry), all other brackets zero.
* g is realised inside U(A) as the span of super-Weyl-symmetrised quadratics `sym(xy)`, x,y ∈ V
  (the (a^+)², (a^-)² vanish). This matches the generators in `Cn1_definition.md`
  (H_{n+1} = -b_n^+b_n^- - 1/2, H_1 = a^+a^- + b_1^+b_1^- are exactly Weyl-ordered).
  Dimension: (2n²+n+1 | 4n), i.e. 8, 19, 34 for n = 1, 2, 3.
* Because κ and K are central and the form is the only source of contractions, the bracket of two
  symmetrised quadratics is again a symmetrised quadratic (double contractions cancel; this was
  checked by code: no constants or non-quadratic terms ever appear). Hence
  `[X,Y]_gb = [X,Y]_0 + κ γ_gb(X,Y)` with γ_gb(X,Y) ∈ g, κ written on the left.
  γ_gb is the same bracket formula using only the κ-valued part of the form (the gb pairing a ↔ b).
* Coboundary: `(δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])`, f odd,
  exactly as in `C_coboundary_definition.md`.

## Proof (all n)

Let ℓ^σ ∈ V_0 = span{b_j^±} and put φ(x) = x for x = b, φ(a^σ) = a^σ + κℓ^σ.
Then in the undeformed U(A) (κ central, so [κℓ, b] = κ[ℓ,b])
`[φ(a^σ), b_j^s] = κ [ℓ^σ, b_j^s]`, and all other brackets between the φ(x) are unchanged
(κ² = 0, [ℓ,a] = 0). So the elements φ(x) satisfy the *deformed* relations with
`gb_{σ,j,s} = [ℓ^σ, b_j^s]` (coefficient). Writing ℓ^σ = Σ λ_{σ,j,t} b_j^{-t} gives `gb_{σ,j,t} = t λ_{σ,j,t}`
since `[b^-,b^+] = 1, [b^+,b^-] = -1`. This is a bijection between ℓ and gb (4n ↔ 4n), so every gb arises.

Symmetrised quadratics transform by `sym(x'y') = X + κ D(X)`, with D the odd derivation extending
ℓ (this is linear in κ because κ² = 0), and D maps S²V → S²V, so f := D|_g is an odd map g → g.
Computing the undeformed bracket of `X' = X + κ f(X)`, `Y' = Y + κ f(Y)`:
`[X',Y'] = [X,Y]_0 + κ{(-1)^{p(X)}[X,f(Y)] + [f(X),Y]}`, and `[f(X),Y] = -(-1)^{(p(X)+1)p(Y)}[Y,f(X)]`.
Since X'_k = X_k + κ f(X_k), `[X',Y'] = Σ c^k X'_k + κ γ_gb(X,Y)` gives
`γ_gb(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y]) = (δf)(X,Y)`. ∎

Conceptually: the gb-deformation is a change of the odd oscillators a^σ ↦ a^σ + κ ℓ^σ, i.e. the
"gauge" freedom κ·(V_0) of the odd generators; the b-b form is non-degenerate, so every gb is pure gauge.

## Handling of "adjoint representation / up to scalar"

* *Adjoint representation.* The bracket extends to L = g ⊕ κg with κ acting trivially and κg ≅ g as
  g-module (adjoint). Thus γ: g⊗g → g is a 2-cochain with adjoint coefficients and δ above is the
  Chevalley–Eilenberg differential for odd 1-cochains f ∈ Hom(g,g)_odd. The identification
  κ·g ≅ g is made by writing κ on the left; the sign in δ (the (-1)^{p(X)} in the first term) is
  exactly the sign produced by moving the odd κ past X, as in the proof above. So "γ = δf as an adjoint
  representation" means equality of g-valued cochains after stripping the κ.
* *Up to scalar.* We interpret "γ = δf up to scalar" as γ = c·δf with a single c ≠ 0. Then f' = f/c
  gives γ = δf', so a scalar neither creates nor destroys triviality (c = 0 would only allow γ = 0,
  which would make the condition vacuous). Since the exact condition (c = 1) already holds for all
  gb, the scalar freedom is not needed. The computations test exact equality, no scalar is fitted.
  (If the scalar were allowed to vary per component of gb, nothing changes: the trivial set is already everything.)

## Computational artifacts

`verification/cn1_triviality.py` (engine) and `verification/run_verification.py` (driver; run
`python3 run_verification.py 1 2 3` inside `verification/`). The engine implements U(A) by a generic
normal-ordering rewriting system with signs (no ansatz), builds structure constants c_ij^k and γ_ij^k
for each unit gb parameter, assembles δ as a sparse matrix for all odd f (n=3: 528 unknowns), and decides
the triviality using ranks over F_p (p = 2³¹-1; entries are dyadic rationals, so rank over F_p
equals the rank over Q unless p divides a minor, extremely unlikely; the explicit witness below is an exact check anyway).

| n | dim g (even\|odd) | #gb | rank γ | rank δ | dim(im δ ∩ im γ) | all gb trivial | dim ker δ_odd | explicit f_λ: δf = γ (random integer gb, exact) |
|---|---|---|---|---|---|---|---|---|
| 1 | 4\|4 | 4 | 4 | 28 | 4 | yes | 4 | True |
| 2 | 11\|8 | 8 | 8 | 168 | 8 | yes | 8 | True |
| 3 | 22\|12 | 12 | 12 | 516 | 12 | yes | 12 | True |

Files: `verification/summary.json`, `verification/artifacts_n{1,2,3}.json` (basis labels, parities,
undeformed structure constants `structure_constants_c0` keyed "i,j" → {k: coeff}, γ for each unit gb
`gamma_unit` keyed "σ,j,s" → {"i,j,k": coeff}, the witness f as {"k,m": coeff} meaning f(Z_m) ∋ coeff·Z_k, and the generic gb used).

## Caveats / honesty notes

* A first version of the code had a bug (`sym(x,x)` lost a factor 2 through a dict key collision); it
  wrongly reported "no gb is trivial" for n=1. It was found by testing the hand-derived witness f against
  γ, fixed, and all reported numbers are from the fixed code.
* The general-n statement rests on the proof above; the computer check covers n=1,2,3 only.
* The model of g (Weyl-symmetrised quadratics in U(A)) is my reading of the supplied definitions;
  no external references (Frappat et al.) were consulted, and no files outside the repository were accessed.
* Not examined: the higher-order (non-linear in κ) obstruction question is vacuous here since κ² = 0.
