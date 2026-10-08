# JSON Schema Specification for C(n+1) = osp(2|2n)

This document defines the C-family Schema 1 (algebra structure) JSON format.
It extends the B(m,n) v5.0 structure described in
`docs/math/B0n_schema_v5.md`; it does not change existing B-family files.
The schema version remains `"5.0"`.

## File naming

Use `C_{n}_structure.json`, where `n` is the bosonic rank:

| Algebra | File |
|---|---|
| C(2) = osp(2\|2) | `C_1_structure.json` |
| C(3) = osp(2\|4) | `C_2_structure.json` |
| C(4) = osp(2\|6) | `C_3_structure.json` |

The corresponding later-layer names are `C_{n}_gamma.json`,
`C_{n}_evaluated.json` (the representative all-positive assignment in this
repository), and `C_{n}_coboundary.json`.

## Top-level shape

Every structure file contains the following keys:

```json
{
  "schema_version": "5.0",
  "algebra": {},
  "oscillator_generators": {},
  "oscillator_relations": {},
  "central_elements": {},
  "basis": {},
  "parity": {},
  "generator_realization": {},
  "structure_constants": [],
  "metadata": {}
}
```

`n` is a positive integer (the bosonic rank). For these algebras,
`m` is fixed to 1.

## Field definitions

### `algebra`

```json
{
  "family": "C",
  "m": 1,
  "n": 1,
  "cartan_type": "C(2)",
  "alternative_notation": {
    "osp": "osp(2|2)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": 8,
    "even": 4,
    "odd": 4,
    "even_formula": "2n^2 + n + 1",
    "odd_formula": "4n",
    "total_formula": "2n^2 + 5n + 1"
  }
}
```

Set `cartan_type` to `"C(n+1)"`, `osp` to `"osp(2|2n)"`, and calculate the
numeric dimensions from the formulas. For example, `n=2` gives `11|8` and
total 19; `n=3` gives `22|12` and total 34.

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "One standard fermionic creation/annihilation pair."
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n."
  }
}
```

Generate the two boson labels per index in `p`, `m` order. There is no
supplementary-fermion field; `a_1_p` and `a_1_m` form a standard CAR pair.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for a standard pair.",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators.",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i,j and each sign choice",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
    }
  },
  "mixed_commutators": {
    "description": "Fermions and bosons commute in the undeformed oscillator algebra.",
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

The mixed relations here are the undeformed relations. Any inhomogeneous
`gb` modification belongs to Schema 2, not Schema 1.

### `central_elements`

This is a top-level object and is mandatory for C-family files:

```json
{
  "kappa": {
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "kappa^2 = 0",
    "description": "Formal odd central symbol for the nilpotent extension."
  },
  "K": {
    "parity": 0,
    "central": true,
    "identity": true,
    "value": "1",
    "description": "Even central identity; identified with the scalar 1."
  }
}
```

These symbols are recorded for algebraic context but are not independent
elements of the C(n+1) basis or PBW generator lists.

### `basis`

For each rank, `even` lists `H_1` through `H_{n+1}`, followed by the even
root generators in the order specified by `handover/notation.md`. `odd` lists
the four `E_eps1_del{k}_{pp,pm,mp,mm}` generators per index, in increasing
`k` order. Example for `n=1`:

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: [odd generators] < [even generators]; kappa and K are excluded."
}
```

The basis has `2n^2+n+1` even elements and `4n` odd elements. The generic
even root labels and their sign meanings are defined in `handover/notation.md`.

### `parity`

This object maps every generator named in `basis` to an integer parity:
`0` for all `H_k` and even-root `E_...` generators; `1` for all
`E_eps1_del{k}_{...}` generators. The central symbols are described separately
under `central_elements` and are not basis entries.

### `generator_realization`

Use the same representation for each generator as in Schema 1 of the
B-family: `description`, `ordering`, and a `realizations` mapping. Each
realization contains `standard_form` (a list of `{ "words": [...],
"coeff": "..." }` terms), `frappat_form`, and `parity`.

The ordering is `a_1_p`, `a_1_m`, then `b_1_p`, `b_1_m`, ..., `b_n_p`,
`b_n_m`. With `$N_k=b_k^+b_k^-$`, the C(n+1) Cartan realizations are
`H_1=a_1_p a_1_m + N_1`,
`H_k=N_{k-1}-N_k` for `2<=k<=n`, and
`H_{n+1}=-N_n-1/2`. The even root generators are
`E_{2δ_k}=1/2 (b_k^+)^2`,
`E_{-2δ_k}=1/2 (b_k^-)^2`, and the four pair-root realizations are
`b_i^± b_j^±` with signs corresponding to their labels. The odd realizations
are:

| Label suffix | Root | Standard form |
|---|---|---|
| `pp` | `+ε +δ_k` | `a_1_p b_k_p` |
| `pm` | `+ε -δ_k` | `a_1_p b_k_m` |
| `mp` | `-ε +δ_k` | `a_1_m b_k_p` |
| `mm` | `-ε -δ_k` | `a_1_m b_k_m` |

Represent the constant `-1/2` as an empty `words` list with coefficient
`"-1/2"`. Record the parity on every realization. Use the half-square
normalization for `E_{±2δ_k}`, as fixed by the simple-generator formulas in
`docs/math/Cn1_definition.md`.

### `structure_constants`

Store nonzero undeformed graded brackets as a list of objects, one per
nonzero pair:

`{"X":"<generator>", "Y":"<generator>", "Z":"<generator>",
"coeff":"<rational>", "sign_rule":"graded"}`

The bracket convention is `[X,Y} = XY - (-1)^(p(X)p(Y))YX`; each record
expresses `[X,Y} = coeff * Z`. Omit zero brackets. Schema 1 constants use
the undeformed CAR, CCR, and mixed relations above; gamma-dependent terms
belong in Schema 2.

### `metadata`

Use the B-family v5.0 metadata shape: `generated_by`, ISO `generation_date`,
and `references` (a list). Cite the C(n+1) mathematical definition and the
base schema/reference sources used by the generator.

## Compatibility with B(m,n) v5.0

The shared keys retain their v5.0 meanings and structure: `schema_version`,
`algebra`, `oscillator_generators`, `oscillator_relations`, `basis`, `parity`,
`generator_realization`, `structure_constants`, and `metadata`. C-family
files use `family: "C"`, fixed `m: 1`, a standard fermion pair, the
`E_eps1_del` odd-root labels, and C-family dimensions. They add the mandatory
top-level `central_elements` object containing odd nilpotent `kappa` and even
identity `K`. B-family documents/files remain unchanged; consumers that
process both families should treat `central_elements` as an additive optional
key for B data and required key for C data.

The C(n+1) basis excludes `kappa` and `K`; in particular, the parity recorded
for `kappa` in the C schema is 1, as required by the C(n+1) deformation
definition.

## Schema 2: Inhomogeneous deformation

Schema 2 uses `C_{n}_gamma.json` and retains `"schema_version": "5.0"`.
It contains the C-family algebra identity, a `gb_matrix`, an
`inhomogeneous_deformation` object, the corresponding Schema 1 filename, and
metadata. `gb_matrix.rows` are `["a_1_p","a_1_m"]`; columns are the `2n`
bosonic labels ordered by increasing index and `p`,`m` sign. Its entries are
parameter labels and `parameter_parity` is 1, following
`docs/math/C_inhomogeneous_definition.md`.

`inhomogeneous_deformation` records the central parameter, bracket formula,
all exchange relations, parameter metadata, and `gamma_coefficients`.
Each coefficient record has `X`, `Y`, `Z`, `parameter`, rational `coeff`,
and `sign_rule`; it contributes `coeff * parameter * Z` to `gamma(X,Y)` with
`kappa` factored to the left. A `Z` of `"K"` denotes an identity contribution:
it is reported explicitly, not treated as a member of the Schema 1 basis.
The `consistency` object reports whether all outputs lie in the Schema 1
basis, lists off-basis identity terms, and reports parity consistency.

**Source-definition caveat:** the supplied exchange relation
`[b_j^s,a_1^σ] = -gb_{σ,j,s} * kappa` assigns odd parity to both `gb` and
`kappa`. Their product is even, but the bracket of an even boson and an odd
fermion must be odd. Also, the generated first-order brackets have identity
terms outside the stated Schema 1 basis. Until the deformation definition or
the C(n+1) realization is corrected, Schema 2 files are formal expansions of
the literal exchange relations and explicitly fail the grading/basis
consistency checks; they must not be interpreted as verified Lie
superalgebra deformations.

## Schema 3: Evaluated structure

The evaluated files are named `C_{n}_evaluated.json`. Each includes the
Schema 1 `base_structure_constants`, an `evaluation` object containing the
complete numeric `gb_assignment`, and `evaluated_gamma_coefficients`. Each
evaluated gamma term has `X`, `Y`, `Z`, rational `kappa_coeff`, and
`sign_rule`; equal `(X,Y,Z)` terms from different parameters are combined.
The `bracket_formula` states how the base and kappa-dependent terms combine.
`consistency` copies the Schema 2 closure, off-basis, and grading findings so
that numerical substitution cannot hide them.

The repository uses the all-positive assignment (every formal `gb` value is
`+1`) as a reproducible representative. It is a formal coefficient
substitution, not a parity-preserving specialization of odd variables; the
Schema 2 caveats continue to apply.

## Schema 4: Coboundary structure

The generic coboundary files are named `C_{n}_coboundary.json`. They record
the Schema 1 algebra identity and basis reference, `odd_linear_map`, and
`coboundary`. The odd map lists one even coefficient parameter for every
ordered input/output pair of opposite parity:

`f(X) = sum_target phi_{X,target} * target`, with
`p(target) = p(X)+1 mod 2`.

Thus there are `2 * dim_even * dim_odd` map parameters. Each nonzero
`coboundary.coefficients` record has `X`, `Y`, `Z`, `parameter`, rational
`coeff`, and `sign_rule`; it contributes `coeff * parameter * Z` to the
specified $\delta f(X,Y)$. Outputs must reference Schema 1 basis generators.
