# JSON Schema Specification v5.0: B(m,n) and C(n+1)

This document defines the algebra-structure layer (Schema 1) for the
B(m,n) and C(n+1) oscillator Lie superalgebra data. Existing B(m,n) files
retain their current structure. C(n+1) uses the same Schema 1 architecture,
with the family-specific fields and conventions defined below.

## File Naming

For C(n+1), `n` is the bosonic rank:

| Algebra | File |
|---|---|
| C(2) = osp(2\|2) | `C_1_structure.json` |
| C(3) = osp(2\|4) | `C_2_structure.json` |
| C(4) = osp(2\|6) | `C_3_structure.json` |

The corresponding patterns for other layers are `C_{n}_gamma.json`,
`C_{n}_evaluated_<gb>.json`, and `C_{n}_coboundary_<gb>.json`.

## Schema 3: Evaluated Structure

Schema 3 records an explicit numeric assignment to the `gb_matrix` from
Schema 2 and the resulting bracket coefficients. The selected profile is
part of the filename; for example, the all-plus profile uses
`C_1_evaluated_all_plus.json`.

### Top-Level Keys

```json
{
  "schema_version": "5.0",
  "algebra": {},
  "source_schemas": {},
  "gb_assignment": {},
  "evaluation": {},
  "structure_constants": [],
  "metadata": {}
}
```

`source_schemas` identifies the Schema 1 and Schema 2 inputs. `gb_assignment`
contains the profile, matrix shape, row and column labels, and numeric entries.
`evaluation` documents the substitution and the convention for retaining
`κ`. `structure_constants` contains every nonzero ordered bracket from the
undeformed or evaluated structure.

Each evaluated bracket record has `X`, `Y`, `Z`, `base_coeff`,
`kappa_coeff`, and `sign_rule`. Its value is interpreted as
`base_coeff + κ * kappa_coeff`, with `κ` factored to the left. `K` may appear
as `Z` for a central identity contribution to the deformation; it is not an
independent basis generator.

Example for the all-plus evaluation of C(2):

```json
{
  "schema_version": "5.0",
  "algebra": {
    "family": "C",
    "m": 1,
    "n": 1,
    "cartan_type": "C(2)",
    "osp": "osp(2|2)"
  },
  "source_schemas": {
    "schema_1": "C_1_structure.json",
    "schema_2": "C_1_gamma.json"
  },
  "gb_assignment": {
    "profile": "all_plus",
    "shape": [2, 2],
    "row_labels": ["a_1_p", "a_1_m"],
    "column_labels": ["b_1_p", "b_1_m"],
    "entries": [[1, 1], [1, 1]]
  },
  "evaluation": {
    "substitution": "All gb parameters are set to +1.",
    "kappa": "Formal odd central element with kappa^2 = 0.",
    "expression": "base_coeff + kappa * kappa_coeff",
    "coefficient_order": "kappa is factored to the left."
  },
  "structure_constants": [
    {
      "X": "E_eps1_del1_pp",
      "Y": "E_eps1_del1_pp",
      "Z": "E_eps1_del1_pp",
      "base_coeff": "0",
      "kappa_coeff": "2",
      "sign_rule": "graded"
    }
  ],
  "metadata": {
    "generated_by": "src/evaluate_C_structure.py",
    "generation_date": "YYYY-MM-DD",
    "profile": "all_plus"
  }
}
```

## Schema 1: Algebra Structure

### Top-Level Keys

Schema 1 retains the v5.0 fields and adds `central_elements` as a top-level
key:

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

### `schema_version`

The schema version remains `"5.0"`.

### `algebra`

For each file, `n` is the positive integer bosonic rank. The dimensions in
`dimension` are numeric values calculated at that rank. `dimension_formula`
records the general formulas.

Example for C(2), where `n = 1`:

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
    "odd": 4
  },
  "dimension_formula": {
    "total": "2n^2+5n+1",
    "even": "2n^2+n+1",
    "odd": "4n"
  }
}
```

| `n` | Even | Odd | Total | Algebra |
|---:|---:|---:|---:|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

### `oscillator_generators`

C(n+1) has one standard fermionic pair and `n` bosonic oscillator pairs.
There is no supplementary fermion.

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^-"
  },
  "bosons": {
    "n": 1,
    "count": 2,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^+, b_k^- for k=1,...,n"
  }
}
```

For general rank, expand the boson labels as
`["b_1_p", "b_1_m", ..., "b_n_p", "b_n_m"]`; `count` is `2n`.

### `oscillator_relations`

These are the undeformed relations used to construct Schema 1. Deformed
fermion-boson exchange relations belong to Schema 2.

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermion pair",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

### `central_elements`

Both central symbols are declared at the top level. Neither is an independent
generator in the C(n+1) basis: `K` is the scalar identity, while `κ` is the
formal odd central symbol used for the nilpotent extension and deformation.

```json
{
  "kappa": {
    "label": "κ",
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "κ^2 = 0",
    "in_basis": false
  },
  "K": {
    "label": "K",
    "parity": 0,
    "central": true,
    "identified_with": "1",
    "in_basis": false,
    "description": "Even central identity element"
  }
}
```

### `basis`

The even basis consists of the `n+1` Cartan generators, the `2n` roots
`±2δ_k`, and the four roots `±δ_i±δ_j` for each `i<j`. The odd basis
contains the four roots `±ε±δ_k` for each `k`.

For C(2):

```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p", "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd generators, k ascending and suffix pp, pm, mp, mm] < [even: Cartan, positive roots, negative roots]; K = 1 is excluded"
}
```

For general `n`, expand these lists as follows:

- Even: `H_1, ..., H_{n+1}`; `E_2del{k}_p` for `k=1,...,n`; then
  `E_del{i}_del{j}_pp` and `E_del{i}_del{j}_pm` for `i<j`; then
  `E_2del{k}_m` for `k=1,...,n`; then
  `E_del{i}_del{j}_mm` and `E_del{i}_del{j}_mp` for `i<j`.
- Odd: for each `k=1,...,n`, in order, include
  `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`,
  `E_eps1_del{k}_mp`, and `E_eps1_del{k}_mm`.

The suffixes `pp`, `pm`, `mp`, and `mm` indicate the signs of the two
coordinates, in order. For odd roots they denote `+ε+δ_k`, `+ε−δ_k`,
`−ε+δ_k`, and `−ε−δ_k`; for even pair roots they denote
`+δ_i+δ_j`, `+δ_i−δ_j`, `−δ_i+δ_j`, and `−δ_i−δ_j`.
The formal `κ` precedes the algebra basis in the PBW convention when the
extension is included; it is listed separately from the basis. `K=1` is
excluded from the basis and PBW ordering.

### `parity`

The parity map has one entry for each basis generator: `0` for every `H_i`,
`E_2del{k}_p/m`, and `E_del{i}_del{j}_{pp,pm,mp,mm}`; `1` for every
`E_eps1_del{k}_{pp,pm,mp,mm}`. The central symbols have the parities declared
in `central_elements`.

### `generator_realization`

Use the v5.0 structure: `description`, `ordering`, and `realizations`.
The oscillator ordering is `a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`.
Each realization stores PBW-ordered oscillator words with rational
coefficients, a readable `frappat_form`, and the generator parity.

The realization rules are:

```text
H_1       = a_1^+ a_1^- + b_1^+ b_1^-
H_k       = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-       (2 <= k <= n)
H_{n+1}   = -b_n^+ b_n^- - 1/2
E_2del{k}_p/m = (b_k^±)^2                         (coefficient 1 for every k)
E_del{i}_del{j}_pp = b_i^+ b_j^+
E_del{i}_del{j}_pm = b_i^+ b_j^-
E_del{i}_del{j}_mp = b_i^- b_j^+
E_del{i}_del{j}_mm = b_i^- b_j^-
E_eps1_del{k}_pp = a_1^+ b_k^+
E_eps1_del{k}_pm = a_1^+ b_k^-
E_eps1_del{k}_mp = a_1^- b_k^+
E_eps1_del{k}_mm = a_1^- b_k^-
```

The coefficient-one convention for all `E_2del{k}_p/m` follows the
all-roots realization and is used consistently for every `k`, including
`k=n`.

### `structure_constants`

Store all nonzero undeformed graded brackets `[X,Y}` as a list. Each entry
uses the v5.0 shape:

```json
{
  "X": "H_1",
  "Y": "E_eps1_del1_pp",
  "Z": "E_eps1_del1_pp",
  "coeff": "2",
  "sign_rule": "graded"
}
```

Coefficients are strings so rational values can be represented exactly.
The bracket values are calculated from the generator realizations and the
undeformed oscillator relations above.

### `metadata`

Retain the v5.0 metadata fields:

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Frappat et al., arXiv:hep-th/9607161"
  ]
}
```

## Compatibility with B(m,n)

The C(n+1) extension keeps the v5.0 field names and structure for
`schema_version`, `basis`, `parity`, `generator_realization`,
`structure_constants`, and `metadata`. C-specific algebra dimensions,
oscillator fields, and root generators are populated according to this
document. Existing B(m,n) files are not changed; `central_elements` is
required for C files and optional for existing B files. Validators that
reject unknown top-level keys must allow this optional key to read both
families.

The C-specific oscillator keys are `fermions` and `bosons`; the B-specific
`supplementary_fermion` is not used. The C odd roots are the `4n` generators
`E_eps1_del{k}_{pp,pm,mp,mm}` rather than the B(0,n) generators
`E_del{k}_p/m`.

## References

- Frappat, Sciarrino, and Sorba, *Dictionary on Lie Algebras and
  Superalgebras*, Academic Press (2000); arXiv:hep-th/9607161.
- B(0,n) v5.0 base-schema conventions, as summarized in
  `docs/math/B0n_schema_v5.md`.
