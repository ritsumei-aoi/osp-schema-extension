# Triviality of the inhomogeneous deformation of C(n+1) = osp(2|2n)

## Result
**Theorem (verified exactly for n = 1, 2, 3).** The inhomogeneous deformation `gamma_gb` is trivial
(`gamma_gb = c * delta f` for some odd linear `f` and some nonzero scalar `c`) **if and only if all 4n
parameters `gb_{sigma,j,s}` vanish.** Every nonzero `gb` gives a non-trivial class.
More precisely, the map `gb -> [gamma_gb]` is injective, so the 4n parameters are 4n independent
non-trivial directions.

Scope: the proof is a complete exact-rational linear-algebra computation for n = 1, 2, 3.
For general n I have no proof; the pattern (rank G = 4n, trivial subspace 0) is consistent across the
three cases, so n >= 4 is a conjecture supported by that pattern.

## 1. Setup (from docs/math)
- `g` = quadratic elements in the oscillators `a+, a-, b_j+, b_j-` modulo constants.
  `dim g = (2n^2+n+1 | 4n)`, which is 8, 19, 34 for n = 1, 2, 3. The script asserts these dimensions.
- `gamma_gb(X,Y)` is the `kappa`-linear part of `[X,Y]` in `U(A)`, using `[b_j^s, a^sigma] = -gb_{sigma,j,s} kappa`.
  It is computed by the super-Leibniz rule. Reordering words only produces central terms, which are dropped.
  So `gamma_gb` is an odd bilinear map `g x g -> g`, and it is linear in `gb`.
- `delta f` is exactly the formula in `C_coboundary_definition.md`, for odd `f` with `f(Z_j) = sum_i phi_ij Z_i`.
  The unknowns are `phi_ij` with `p(i) != p(j)`.

## 2. Handling "adjoint representation / up to scalar"
- *Adjoint representation.* `g` has coefficients in itself, and `kappa` acts trivially on `L = g + kappa g`.
  So `gamma` is a 2-cochain of `g` with values in the adjoint module, and `delta f` is the adjoint-module
  coboundary. The script asserts, for the actual structure constants:
  - `[ , ]_0` and `gamma` are super-skew-symmetric.
  - `[ , ]_0` satisfies the super-Jacobi identity.
  I also checked by hand that `delta f` has the same super-skew-symmetry.
- *Up to scalar.* `delta` is linear in `f`, so `gamma = c * delta f` with `c != 0` is the same as
  `gamma = delta(f/c)`. The scalar changes nothing, and the question reduces to `gamma in im(delta)`.
  The case `c = 0` has to be excluded, because it would make every `gamma` "trivial".
  Because `gamma_gb` is linear in `gb`, the set `S = {gb : gamma_gb in im delta}` is a linear subspace,
  closed under scalars, so computing `S` settles the question.
- Computation: `S` is the projection onto the `gb`-coordinates of `ker [D | G]`.
  `D` is the matrix of `phi -> delta f`. `G` is the matrix of `gb -> gamma_gb`. Both are integer matrices,
  and the ranks are exact over Q (sympy).

## 3. Computational results (`artifacts/verify_triviality.py`)
| n | dim g | #gb | #phi | rank D | rank G | rank [D\|G] | dim S |
|---|---|---|---|---|---|---|---|
| 1 | 8  | 4  | 32  | 28  | 4  | 32  | 0 |
| 2 | 19 | 8  | 176 | 168 | 8  | 176 | 0 |
| 3 | 34 | 12 | 528 | 516 | 12 | 528 | 0 |

- `rank G = 4n`, so `gb -> gamma_gb` is injective, and no nonzero `gb` gives `gamma = 0`.
- `rank [D|G] = rank D + rank G`, so `im D` and `im G` intersect only at 0.
  Hence `S = {0}`: the only trivial configuration is `gb = 0`.

## 4. Artifacts
- `artifacts/verify_triviality.py` regenerates everything (`python3 artifacts/verify_triviality.py`).
- `artifacts/verification_data.json` holds, for n = 1, 2, 3:
  - basis words and parities,
  - nonzero structure constants of `[ , ]_0`,
  - nonzero `gamma` entries as linear forms in `gb`,
  - the ranks and the (empty) trivial subspace.

## 5. Caveats
- My model of the extension and of `gamma` (central `K`, `kappa`, constants dropped, `K = 1`) is my reading of
  `C_inhomogeneous_definition.md`. The sign convention for `[a,b]` versus `[b,a]` only rescales `gb`
  and does not affect which `gb` are trivial.
- I did not verify the cocycle condition for `gamma` separately. It follows from the Jacobi identity in
  `U(A)`, but I did not check it numerically.
- I used no external papers and requested no web access.
