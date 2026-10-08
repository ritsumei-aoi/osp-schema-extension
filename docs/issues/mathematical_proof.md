# Triviality of the inhomogeneous (gb) deformation of C(n+1) = osp(2|2n)

**Scope**: the question in `docs/issues/issue_open.md`: for which parameters
`gb_{σ,j,s}` is the deformation `γ_gb` trivial, i.e. `γ_gb = δF` for some odd
linear map `F`, using only the definitions in `docs/math/`.

## 0. Startup verification

| File | Status |
|---|---|
| `docs/math/Cn1_definition.md` | present; contains no JSON schema material (checked) |
| `docs/math/C_inhomogeneous_definition.md` | present |
| `docs/math/C_coboundary_definition.md` | present |
| `docs/issues/issue_open.md` | present |
| `final_reflection_template.md` | present (repo root; not filled in, see §7) |
| `supplementary_metrics_template.md` | present (repo root; not filled in, see §7) |

No file outside the repository root was read. No web access or external papers were used
(the Frappat reference was not consulted, so no approval was needed or requested).

---

## 1. Result

**Theorem (computed for n = 1, 2, 3; analytic mechanism for all n).**
For every `n ≥ 1` and every `gb ∈ C^{4n}`, the deformation `γ_gb` is trivial:
there is an odd linear map `F_gb : g → g` (with a scalar component, if one keeps it)
such that `γ_gb = δF_gb`.

Equivalently, the set `T ⊂ C^{4n}` of trivial parameters is all of `C^{4n}`.
**There are no triviality conditions on `gb`.** The first-order inhomogeneous deformation
is trivial for every choice of parameters, and this holds in both readings of
"adjoint / up to scalar" (§3).

| n | dim g | dim T (quotient reading) | dim T (central reading) | verified how |
|---|---|---|---|---|
| 1 | 8 | 4 = 4n | 4 = 4n | exact over Q (certificates) |
| 2 | 19 | 8 = 4n | 8 = 4n | exact over Q (certificates) |
| 3 | 34 | 12 = 4n | 12 = 4n | float SVD and mod-p rank (no exact certificate) |

The conclusion is that `T` is the whole parameter space. A "triviality condition" such as
"γ_gb trivial iff gb = 0" does not hold for the definitions as written. §6 explains which
change of definition would produce that answer.

---

## 2. Setup and conventions

**Oscillators.** Fermions `a^+` (index 0), `a^-` (index 1), odd. Bosons `b_k^+` (index 2k),
`b_k^-` (index 2k+1), even, k = 1..n.
Relations: `{a^-,a^+} = 1`, `(a^±)^2 = 0`, `[b_k^-, b_l^+] = δ_kl`, other boson pairs commute,
and the deformation `[b_j^s, a^σ] = -gb_{σ,j,s} κ`.

**κ.** κ is odd and supercentral (`κ x = (-1)^{p(x)} x κ`), with `κ^2 = 0` (first order).
This convention is the consistent one. The Jacobi identity holds exactly in the computed
algebra for all tested triples (§5), which is evidence that the sign conventions are right.

**The Lie superalgebra.** Let `L = span{normal-ordered quadratic monomials} ⊕ C·1`.
Normal order puts fermions before bosons and bosons by increasing index.
Quadratic monomials are `a^+a^-`, `a^σ b_j^s` (4n of them), and `b b'` (2n²+n of them),
so `dim L = dim g + 1` with `dim g = 2n²+5n+1`. The constant `1` is central in `L`.
The scalar `1` is the only ambiguity, and §3 treats it.

**The deformation.** `γ(X,Y)` is the κ-coefficient of the deformed bracket `[X,Y]_gb` in
`L ⊗ C[κ]/κ²`. Since `[b,a]` is the only κ-source and it is linear in `gb`,
`γ_gb = Σ_m gb_m γ^{(m)}` is linear in `gb`.

**The coboundary.** For odd linear `F`,
`(δF)(X,Y) = (-1)^{p(X)}[X,F(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,F(X)] - F([X,Y])`,
with brackets from the undeformed algebra, as in `docs/math/C_coboundary_definition.md`.
For an odd `Z`, `δ(ad_Z) = 0` by the super-Jacobi identity; the computed kernel of `δ` on odd
cochains is exactly this (see the check in §5).

**Triviality as linear algebra.** The condition `γ_gb = δF` is linear in `(gb, F)`. The set of
trivial `gb` is therefore a linear subspace `T`, and
`dim T = 4n + rank(Δ) - rank([Δ | Γ])`,
where `Γ` is the matrix of `gb ↦ γ_gb` and `Δ` is the matrix of `F ↦ δF`.

---

## 3. Handling of the "adjoint representation / up to scalar" condition

`docs/math/C_coboundary_definition.md` says "γ = δf up to scalar". This is ambiguous, so
both readings were computed.

**(a) Global scalar.** If "up to scalar" means `γ = λ δf` for one scalar `λ`, it is harmless.
Since `γ_gb` and `δF` are both linear, `λδF = δ(λF)`, and the scalar is absorbed into `F`.
The set `T` is unchanged.

**(b) Quotient reading (the adjoint picture; used as the primary reading).** Work in
`g = L / C·1`, i.e. discard the scalar component of every bracket and of `γ`. `F` maps `g → g`.
This is the literal "adjoint representation" reading in the doc.

**(c) Central reading.** Work in `L`, keeping the scalar. `F: L → L` odd, so `F(1)` is an odd
element of `L`. This is the honest oscillator-level statement.

**Where the scalar comes from.** The scalar component of `γ` comes from the anticommutator
`{a^-,a^+} = 1`, which produces a `κ·1` term when a fermion is contracted inside a quadratic
product. The number of `γ`-entries with a nonzero scalar component is 12 (n=1), 40 (n=2),
84 (n=3). So the two readings really differ at the level of `γ`, but the triviality
conclusion is the same in both, as §5 shows.

---

## 4. Analytic mechanism (all n)

The computation of §5 suggests a closed-form reason. Fix `(j,s)` and write
`g_σ := gb_{σ,j,s}`, so `[b_j^s, a^σ] = -g_σ κ`. Define the shifted boson

  `b'_j^s := b_j^s + κ (g_- a^+ + g_+ a^-)`.

Using `[κu, a^τ] = κ{u, a^τ}` for odd `u` (this follows from supercentrality of κ):

- `[b', a^+] = -g_+ κ + g_+ κ{a^-,a^+} + g_- κ{a^+,a^+} = -g_+κ + g_+κ = 0`
- `[b', a^-] = -g_- κ + g_- κ{a^+,a^-} + g_+ κ{a^-,a^-} = -g_-κ + g_-κ = 0`
- `[b', b'] = [b, b] + O(κ^2) = [b,b]` and `[b'_k^-, b'_l^+] = δ_kl`.

So `(a^±, b'_j^s, κ)` satisfies the undeformed oscillator relations, and the map `ψ: b ↦ b'`
is an isomorphism from the first-order deformed oscillator algebra to the undeformed one.
Restricting to quadratic elements gives the trivialisation. Writing `F(X)` for the
κ-coefficient of `ψ^{-1}(X)` for `X ∈ g`, one gets an odd linear map with `γ_gb = δF`
(up to the sign convention of the change of variables). Since the κ-terms of `ψ^{-1}` of a
quadratic element are again quadratic in the oscillators, `F` maps `g → g`, and the
constant part of `ψ^{-1}` gives exactly the scalar component discussed in §3.

**Explicit check.** For `gb` with only `gb_{+,1,+} = 1` (direction `gb[a+,b1+]`) the shift is
`b^+ ↦ b^+ + κ a^-`, and `ψ^{-1}` gives
`F(a^+b^+) = a^+a^-`, `F((b^+)^2) = -2 a^-b^+`, `F(b^+b^-) = -a^-b^-`.
The exact certificate from §5 contains precisely these three entries, with the same coefficients
(`0,1 → 1`, `3,5 → -2`, `4,6 → -1` in the `(F(e_d) = Σ value · e_c)` notation of the JSON).
This is a non-trivial cross-check of the hand argument against the machine computation.

The hand argument is for general n and does not depend on the computation. The explicit
F for general n was not separately machine-checked beyond the n ≤ 2 certificates.

---

## 5. Computational verification

**Method** (`scripts/c_n1_triviality.py`):
1. Build the normal-ordering rewrite system for the deformed oscillator algebra, with
   κ tracked to first order (κ² = 0).
2. Compute the undeformed bracket table on the basis of `L` and the cochains `γ^{(m)}`
   (one per gb parameter, `G = e_m`).
3. Check the super-Jacobi identity for every basis triple, with both `gb = 0` and a
   random generic `gb`.
4. Build the linear system `Γ gb = Δ φ` for `F` (unknowns `φ_{c,d}`, `F(e_d) = e_c`, `p(c) ≠ p(d)`),
   in both readings.
5. Compute `dim T` by exact rank over Q (n = 1, 2), and by float SVD and mod-p rank (all n).
6. For n = 1, 2: give, for each gb direction, an explicit rational `F`, and check
   `Δφ = Γ e_m` in exact arithmetic (an `assert` in the script).

**Results.**

| n | Jacobi failures / triples | rank Δ (quotient / central) | rank [Δ\|Γ] (quotient / central) | dim T (quotient / central) |
|---|---|---|---|---|
| 1 | 0 / 1458 | 28 / 36 | 28 / 36 | 4 / 4 |
| 2 | 0 / 16000 | 168 / 184 | 168 / 184 | 8 / 8 |
| 3 | 0 / 85750 | 516 / 540 | 516 / 540 | 12 / 12 |

For every n and both readings, `rank [Δ|Γ] = rank Δ`, which means `Γ`'s columns lie in
`im Δ`. Hence `T = C^{4n}`.

**Consistency checks.**
- Kernel of `δ` on odd 1-cochains has dimension `#unknowns - rank Δ`:
  n=1: 32−28 = 4; n=2: 176−168 = 8; n=3: 528−516 = 12 (quotient). This equals `4n = dim g_1`,
  the coboundaries `δ(ad_Z) = 0` for odd `Z`, as expected from super-Jacobi.
- Jacobi holds for all tested triples, with and without deformation.
- For n = 1, 2 the exact certificates reproduce the analytic `F` of §4.

**Exactness.** The n = 1, 2 numbers come from exact rational row reduction. The n = 3 numbers
are from float SVD and mod-p rank; these agree with each other but are not an exact
certificate.

---

## 6. Caveats and sensitivity to definitions

- **Parity.** The definition used is the one in the doc: `γ` odd (gb odd), `F` odd. If one
  instead required `F` even, then `δF` would be even and `γ_gb = δF` would force `γ_gb = 0`,
  i.e. `T = {0}`. That is a parity mismatch, not a nontrivial result, and it would answer a
  different question.
- **Scalar component.** The reading affects which `F` is needed (scalar part present or
  not), not whether a solution exists.
- **Identification `g ≅ L/C·1 ≅ osp(2|2n)`.** This was taken from the doc's oscillator
  realisation. It was checked by dimension, closure, and Jacobi, not by an independent
  identification of the Killing form or a comparison with the Frappat reference (not
  accessed).
- **General n.** The analytic mechanism (§4) is a hand argument. The machine checks cover
  n = 1, 2 exactly and n = 3 numerically.

---

## 7. Templates and bookkeeping

`final_reflection_template.md` and `supplementary_metrics_template.md` were not filled in.
They are for run evaluation, which is outside this task. Session timing and token figures
are not available in this environment, so they are not reported here.

---

## 8. Artifacts

All in the repository:

- `scripts/c_n1_triviality.py`: generates every artifact below. Run with
  `python3 scripts/c_n1_triviality.py 1 2 3` (about 2 minutes; n ≤ 2 adds exact certificates).
- `docs/issues/artifacts/triviality_n1.json`, `triviality_n2.json`, `triviality_n3.json`:
  basis, parities, undeformed structure constants, `γ^{(m)}` for each gb parameter,
  Jacobi results, ranks, `dim T`, and for n ≤ 2 the exact `F` certificates.
- `docs/issues/artifacts/triviality_summary.json`: the table in §5 as structured data.
