# C(n+1) JSON Schema Specification

This document specifies Schema 1 (algebra structure) for
$C(n+1)=\mathfrak{osp}(2|2n)$ using the v5.0 schema architecture. Each
instance is parameterized by the bosonic rank $n\geq1$.

## Schema 1 overview

A Schema 1 document has the following top-level keys:

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

`central_elements` is an additional top-level key for the C(n+1) extension.
The other fields retain the v5.0 shapes unless described below.

## `schema_version`

Use `"5.0"`.

## `algebra`

Set the family to C and explicitly include `m: 1`. `n` is the bosonic rank.
`cartan_type` and `alternative_notation.osp` name the concrete algebra for
that rank. The numeric dimension values are instance-specific; the formula
strings are shared by every rank.

```json
{
  "family": "C",
  "m": 1,
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {
    "osp": "osp(2|4)",
    "dimension_formula": "osp(2m|2n), with m=1"
  },
  "dimension": {
    "total": 19,
    "even": 11,
    "odd": 8,
    "formula": {
      "even": "2n^2+n+1",
      "odd": "4n",
      "total": "2n^2+5n+1"
    }
  }
}
```

The dimension values for the initial ranks are:

| Bosonic rank `n` | Algebra | Even | Odd | Total |
|---:|---|---:|---:|---:|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

## `oscillator_generators`

The standard fermionic pair replaces B(0,n)'s supplementary fermion. There
are two fermion labels and `2n` boson labels:

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "One standard fermionic pair a_1^+, a_1^-."
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± for k=1,...,n."
  }
}
```

For arbitrary `n`, enumerate boson labels as
`b_1_p`, `b_1_m`, ..., `b_n_p`, `b_n_m`; set `bosons.count` to `2n`.
Labels `_p` and `_m` denote plus and minus, respectively.

## `oscillator_relations`

Use the canonical anticommutation relations for the fermions, canonical
commutation relations for the bosons, and zero mixed commutators in the
undeformed algebra:

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for a_1^±.",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = {a_1_p, a_1_m} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for b_k^±.",
    "relations": {
      "same_type": "[b_i^+, b_j^+] = [b_i^-, b_j^-] = 0 for all i,j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_j^s, a_1^σ] = 0 for all j and s,σ in {+,-}"
  }
}
```

The inhomogeneous `gb` exchange relations are part of Schema 2 and are not
included among these undeformed Schema 1 relations.

## `central_elements`

This C(n+1)-specific top-level object records the formal central symbols.
Neither symbol is an ordinary generator in the C(n+1) basis: `K` is the
even scalar identity, while `kappa` is the odd nilpotent central symbol used
by the inhomogeneous extension.

```json
{
  "kappa": {
    "label": "κ",
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "κ^2 = 0",
    "description": "Odd central symbol used by the inhomogeneous extension."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "central": true,
    "identified_with": "1",
    "independent_basis_element": false,
    "description": "Even central identity; excluded from the basis."
  }
}
```

`kappa` is shown first in the PBW ordering for the central extension but is
not counted in the dimensions of `g`. `K=1` is excluded from the basis and
PBW ordering.

## `basis`

Use the approved C(n+1) labels and ordering from `handover/notation.md`.
For all ranks:

- `even`: `H_1` through `H_{n+1}`, followed by the even root labels in this
  order: `E_2del{k}_p` for ascending `k`; `E_del{i}_del{j}_pp` for
  lexicographic pairs `i<j`; `E_del{i}_del{j}_pm` for the same pair order;
  `E_2del{k}_m` for ascending `k`; `E_del{i}_del{j}_mm`; then
  `E_del{i}_del{j}_mp`.
- `odd`: for ascending `k`, append `E_eps1_del{k}_pp`,
  `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm`.
- `ordering_convention`: state the PBW order, including the order within
  each parity block and the exclusion of `K`.

For example, the complete C(3), `n=2` basis arrays are:

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp", "E_del1_del2_pm",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm",
    "E_eps1_del2_pp", "E_eps1_del2_pm",
    "E_eps1_del2_mp", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: k ascending, pp, pm, mp, mm] < [even: H; E_2del{k}_p; E_del{i}_del{j}_pp; E_del{i}_del{j}_pm; E_2del{k}_m; E_del{i}_del{j}_mm; E_del{i}_del{j}_mp] (K=1 is excluded)"
}
```

The arrays in every generated instance must contain all concrete generator
labels; abbreviated patterns are not literal schema entries.

## `parity`

Use a JSON object with one entry for every generator in `basis`. Assign
parity `0` to every `H_i`, `E_2del{k}_p/m`, and
`E_del{i}_del{j}_pp/pm/mp/mm`. Assign parity `1` to every
`E_eps1_del{k}_pp/pm/mp/mm`. The central elements' parities are specified
separately in `central_elements`, not in this basis map.

## `generator_realization`

Retain the v5.0 structure with `description`, `ordering`, and `realizations`.
Order the oscillators as `a_1_p`, `a_1_m`, then `b_1_p`, `b_1_m`, ...,
`b_n_p`, `b_n_m`. Every basis generator has a realization object with:

- `standard_form`: a list of oscillator words and rational coefficients,
  represented as `{ "words": [...], "coeff": "..." }`. An empty word
  represents a constant term.
- `frappat_form`: a readable mathematical expression.
- `parity`: `0` or `1`, matching `parity`.

Use these realizations:

| Generator | Standard form |
|---|---|
| `H_1` | `a_1_p a_1_m + b_1_p b_1_m` |
| `H_k`, `2 <= k <= n` | `b_{k-1}_p b_{k-1}_m - b_k_p b_k_m` |
| `H_{n+1}` | `-b_n_p b_n_m - 1/2` |
| `E_2del{k}_p` / `E_2del{k}_m` | `(b_k_p)^2` / `(b_k_m)^2` |
| `E_del{i}_del{j}_pp` | `b_i_p b_j_p` |
| `E_del{i}_del{j}_pm` | `b_i_p b_j_m` |
| `E_del{i}_del{j}_mp` | `b_i_m b_j_p` |
| `E_del{i}_del{j}_mm` | `b_i_m b_j_m` |
| `E_eps1_del{k}_pp` | `a_1_p b_k_p` |
| `E_eps1_del{k}_pm` | `a_1_p b_k_m` |
| `E_eps1_del{k}_mp` | `a_1_m b_k_p` |
| `E_eps1_del{k}_mm` | `a_1_m b_k_m` |

Each root-generator term has coefficient `"1"` under the full-root
normalization adopted in `handover/notation.md`. For example,
`H_{n+1}` is represented by terms with words
`["b_n_p", "b_n_m"]` and coefficient `"-1"`, and with `words: []` and
coefficient `"-1/2"`. Do not include central-element realizations in this
basis map.

For example, a realization object for `H_2` (when `n=1`) and one for an odd
root generator have this form:

```json
{
  "realizations": {
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_1^+ b_1^- - 1/2",
      "parity": 0
    },
    "E_eps1_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    }
  }
}
```

## `structure_constants`

Keep the v5.0 list format for nonzero undeformed graded brackets. Each entry
has the following fields:

```json
{
  "X": "H_2",
  "Y": "E_eps1_del1_pp",
  "Z": "E_eps1_del1_pp",
  "coeff": "-1",
  "sign_rule": "graded"
}
```

`X`, `Y`, and `Z` refer to basis labels; `coeff` is a rational coefficient
encoded as a string. Populate the list with all nonzero brackets computed
from the C(n+1) oscillator realizations and CAR/CCR above. Do not copy B(0,n)
coefficients. This list is for the undeformed algebra; `gb`-dependent
structure belongs to Schema 2.

## `metadata`

Retain the v5.0 metadata fields. Use a C-specific generator name and actual
generation date for generated instances:

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

## Schema 2: Inhomogeneous gamma structure

Schema 2 files are named `C_{n}_gamma.json` and reference the corresponding
Schema 1 file `C_{n}_structure.json`. They reuse its `algebra` object and
store the deformation parameters and nonzero gamma coefficients:

```json
{
  "schema_version": "5.0",
  "algebra": {},
  "gb_matrix": {
    "shape": [2, 2],
    "row_labels": ["a_1_p", "a_1_m"],
    "column_labels": ["b_1_p", "b_1_m"],
    "parameters": [
      ["gb_a1_p_b1_p", "gb_a1_p_b1_m"],
      ["gb_a1_m_b1_p", "gb_a1_m_b1_m"]
    ],
    "parity": 0
  },
  "inhomogeneous_deformation": {
    "exchange_relation": "[b_j^s, a_1^σ] = -gb_{σ,j,s} * κ",
    "sign_convention": "Literal source relation; gb is an ordinary scalar.",
    "kappa_parity": 1,
    "deformation_term_parity": 1,
    "gamma_structure": [
      {
        "X": "E_eps1_del1_pp",
        "Y": "H_1",
        "Z": "K",
        "coeff": "gb_a1_p_b1_p",
        "sign_rule": "graded"
      }
    ]
  },
  "metadata": {}
}
```

`gb_matrix.shape` is `[2, 2n]`. Its rows correspond to `a_1_p` and
`a_1_m`; its columns list each `b_k_p`, `b_k_m` in ascending `k`. Every
matrix entry is a distinct ordinary scalar parameter (`parity: 0`). The
product of a parameter with the odd central symbol `κ` has parity 1.

`gamma_structure` contains one record for every nonzero ordered pair and
output component. `coeff` is an exact linear expression in the `gb`
parameters; `X` and `Y` are Schema 1 basis labels. `Z` may be a Schema 1
basis label or `"K"`, the even central identity (`K=1`) recorded in the
Schema 1 `central_elements` object. Although `K` is excluded from the
Schema 1 basis, scalar components in gamma are intentional and must be
represented with `Z: "K"`. Coefficients use the same graded sign convention
as Schema 1. The undeformed bracket component is checked against the
corresponding Schema 1 structure constants. `metadata.schema1_file` names
the Schema 1 input used to generate the gamma data.

## Compatibility with B(m,n)

The C(n+1) schema retains `schema_version: "5.0"` and the existing v5.0
shapes for `algebra`, `basis`, `parity`, `generator_realization`,
`structure_constants`, and `metadata`. C-specific changes are:

- `algebra.family` is `"C"`, `algebra.m` is `1`, and the dimensions use the
  C(n+1) formulas above.
- `oscillator_generators.supplementary_fermion` is replaced by
  `oscillator_generators.fermions` containing the standard pair; the boson
  labels remain a rank-indexed list.
- The supplementary-fermion relation is replaced by CAR, while the
  bosonic and mixed relation fields retain their roles.
- `central_elements` is added as a top-level key for `kappa` and `K`.
- The basis, parity map, oscillator realizations, and structure-constant
  values are C(n+1)-specific.

Existing B(m,n) schema instances remain unchanged; consumers that validate
top-level keys should permit the additional C-specific `central_elements`
key when reading C(n+1) documents.

## File naming

Use `C_{n}_structure.json`, where `n` is the bosonic rank:

| Algebra | Filename |
|---|---|
| C(2) = osp(2\|2), `n=1` | `C_1_structure.json` |
| C(3) = osp(2\|4), `n=2` | `C_2_structure.json` |
| C(4) = osp(2\|6), `n=3` | `C_3_structure.json` |
