# Verification artifacts: triviality of the gb-deformation of C(n+1) = osp(2|2n)

Companion code and data for `docs/issues/mathematical_proof.md`.

## Files

| file | content |
|---|---|
| `osp_deform.py` | exact model of the deformed oscillator algebra U(A') over Q[gb] (normal ordering, super-commutators), the quadratic basis of osp(2\|2n) from `docs/math/Cn1_definition.md`, decomposition into ĝ = g ⊕ C·1, the coboundary δf of `docs/math/C_coboundary_definition.md`, the explicit splitting map Φ / f_gb, cocycle (super-Jacobi) check, exact modular rank, odd H² |
| `run_verification.py` | driver; `python3 run_verification.py [n ...]` (default `1 2 3`) writes `artifacts/osp2_2n_n{n}.json` and `artifacts/summary.json` |
| `artifacts/osp2_2n_n{1,2,3}.json` | structure constants, γ_gb (linear forms in gb), explicit f_gb, rank data for readings R1/R2/R3, scalar-part conditions, all checks, odd H² (n ≤ 2) |
| `artifacts/summary.json` | the check/rank summary for all n |

Requirements: Python ≥ 3.10, numpy (only for the independent modular/float rank cross-checks).
Runtime: ≈0.2 s (n=1), ≈7 s (n=2), ≈85 s (n=3).

## Conventions encoded

* K = 1; κ odd central with κ² = 0; gb parameters are even scalars; γ is the (odd) coefficient of κ.
* Deformed relation `[b_j^s, a^sigma] = - gb[sigma][j][s] * kappa`.
* Coboundary `(df)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])`.
* Readings of "γ = δf": **R1** modulo scalars (adjoint representation, as in the docs) with f: g → g;
  **R2** exact in ĝ with f: g → ĝ; **R3** exact in ĝ with f: g → g.

## JSON schema (per n)

```
basis[i]                      = {index, name, parity, root, oscillator_expression}
structure_constants.entries   = [[a, b, k, value], ...]          [Z_a, Z_b]_0 = Σ_k value Z_k
gamma.entries_in_g            = [[a, b, k, gb_name, value], ...] γ(Z_a,Z_b) = Σ value·gb·Z_k   (k in g)
gamma.entries_scalar          = [[a, b, "1", gb_name, value], ...]                            (scalar part)
explicit_f.entries            = [[j, i, gb_name, value], ...]    f(Z_j) = Σ value·gb·Z_i  ("1" = scalar)
explicit_f.scalar_part_f_C    = {Z_j: {gb_name: value}}
linear_system.{R1,R2,R3}      = {num_unknowns_phi, num_equations, ranks{mod_p, float}, codim_of_admissible_gb,
                                 dim_admissible_gb_subspace, dim Z^1_odd, all_gb_trivial}
R3_scalar_part_conditions     = {forms: {γ_C(Z_a,Z_b): {gb_name: value}}, rank_of_conditions}
odd_cohomology_H2(g,Pi g)     = {dim_C2_odd, dim_Z2_odd, dim_B2_odd, dim_H2_odd, dim_Z1_odd}   (n ≤ 2)
checks                        = {closure, gb-linearity, oddness, skewness, cocycle, Phi relations,
                                 gamma == delta f (exact / mod scalars), f odd}
```
All values are exact rationals stored as strings. Basis names: `H1..H{n+1}`, `E[d1+d2]`, `E[-2d1]`,
`E[e-d1]` (ε−δ₁), etc. Parameter names: `gb[sigma][j][s]` = gb_{σ,j,s} = gb_{a_1^σ, b_j^s}.
