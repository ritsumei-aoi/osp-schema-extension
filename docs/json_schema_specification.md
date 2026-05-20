# C(n+1) Schema 1 JSON Specification (v5.0 Draft)

This document defines the approved Schema 1 (`*_structure.json`) specification
for the $C(n+1) = \mathfrak{osp}(2|2n)$ extension in this repository.

It is designed to remain as close as possible to the existing B-series v5.0
schema while incorporating the C-series fermionic pair, central elements, and
approved PBW ordering finalized in Issue I01.

## 1. File Naming Convention

Schema 1 files use:

`C_n_structure.json`

where `n` is the **bosonic rank**.

Examples:

- `C_1_structure.json` for `C(2) = osp(2|2)`
- `C_2_structure.json` for `C(3) = osp(2|4)`
- `C_3_structure.json` for `C(4) = osp(2|6)`

The same bosonic-rank indexing should also be used for later layers:

- `C_n_gamma.json`
- `C_n_evaluated_<gb>.json`
- `C_n_coboundary_<gb>.json`

## 2. Top-Level Structure

Schema 1 has the following top-level keys:

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "oscillator_generators": { ... },
  "oscillator_relations": { ... },
  "central_elements": { ... },
  "basis": { ... },
  "parity": { ... },
  "generator_realization": { ... },
  "structure_constants": { ... },
  "metadata": { ... }
}
```

Compared with the B-series v5.0 structure, the only new top-level key is
`central_elements`.

## 3. `schema_version`

```json
"schema_version": "5.0"
```

The C-series extension remains within the v5.0 family for compatibility with
the existing B-series layout.

## 4. `algebra`

The `algebra` object keeps the same shape as in the B-series schema.

Example for `C(3) = osp(2|4)`:

```json
{
  "family": "C",
  "m": 1,
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {
    "osp": "osp(2|4)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": 19,
    "even": 11,
    "odd": 8
  }
}
```

Conventions:

- `family` is always `"C"`
- `m` is always `1`
- `n` means the bosonic rank
- `cartan_type` is rendered as `C(n+1)`

Dimension formulas:

- even = `2n^2 + n + 1`
- odd = `4n`
- total = `2n^2 + 5n + 1`

Reference values:

| `n` | Cartan type | osp notation | even | odd | total |
|---|---|---|---|---|---|
| 1 | `C(2)` | `osp(2|2)` | 4 | 4 | 8 |
| 2 | `C(3)` | `osp(2|4)` | 11 | 8 | 19 |
| 3 | `C(4)` | `osp(2|6)` | 22 | 12 | 34 |

## 5. `oscillator_generators`

The B-series `supplementary_fermion` object is replaced by a
`standard_fermion` object.

Example for `n = 2`:

```json
{
  "standard_fermion": {
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "relation": "{a_1_m, a_1_p} = 1",
    "description": "Standard fermionic pair a_1^± with canonical anticommutation relations."
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

General rules:

- fermion labels are always `a_1_p`, `a_1_m`
- boson labels are always `b_k_p`, `b_k_m`
- `bosons.count = 2n`

## 6. `oscillator_relations`

The oscillator relations preserve the B-series key layout wherever possible,
but replace the auxiliary-fermion relation with CAR data.

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermionic pair",
    "relations": {
      "same_type": "{a_1^+, a_1^+} = 0 and {a_1^-, a_1^-} = 0",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^s, a_1^t] = 0 for all i and s,t in {+,-}"
  }
}
```

Schema 1 records only the undeformed oscillator algebra. Any deformation data
belongs in later schema layers, not here.

## 7. `central_elements`

The C-series Schema 1 records both `kappa` and `K` explicitly:

```json
{
  "kappa": {
    "parity": 0,
    "relation": "kappa^2 = 0",
    "description": "Formal central symbol for the nilpotent extension; recorded explicitly in the schema and excluded from basis lists."
  },
  "K": {
    "parity": 0,
    "relation": "K = 1",
    "description": "Central identity element; recorded for completeness and excluded from basis lists."
  }
}
```

Conventions:

- `kappa` is stored in JSON with parity `0`, matching the existing B-side
  schema note
- `K` is the central identity element
- neither `kappa` nor `K` appears in the `basis.even` or `basis.odd` arrays

## 8. `basis`

The basis uses the approved Option A PBW ordering from Issue I01:

```text
kappa < [odd generators] < [even generators]
```

with `K = 1` excluded from the basis lists.

Schema form:

```json
{
  "even": [ ... ],
  "odd": [ ... ],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded; see central_elements)"
}
```

### 8.1 Odd block

The odd basis is ordered by family, with `k = 1, ..., n` ascending inside each
family:

1. `E_eps1_del{k}_pp`
2. `E_eps1_del{k}_pm`
3. `E_eps1_del{k}_mp`
4. `E_eps1_del{k}_mm`

Equivalently:

```text
E_eps1_del1_pp, ..., E_eps1_deln_pp,
E_eps1_del1_pm, ..., E_eps1_deln_pm,
E_eps1_del1_mp, ..., E_eps1_deln_mp,
E_eps1_del1_mm, ..., E_eps1_deln_mm
```

### 8.2 Even block

The even basis is ordered as:

1. `H_1, ..., H_{n+1}`
2. `E_2del{k}_p`
3. `E_del{i}_del{j}_pp` in lexicographic `(i, j)` order
4. `E_del{i}_del{j}_pm` in lexicographic `(i, j)` order
5. `E_2del{k}_m`
6. `E_del{i}_del{j}_mm` in lexicographic `(i, j)` order
7. `E_del{i}_del{j}_mp` in lexicographic `(i, j)` order

### 8.3 Low-rank ordered basis lists

#### `C(2) = osp(2|2)`, `n = 1`

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]
}
```

#### `C(3) = osp(2|4)`, `n = 2`

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp",
    "E_del1_del2_pm",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm",
    "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ]
}
```

#### `C(4) = osp(2|6)`, `n = 3`

```json
{
  "even": [
    "H_1", "H_2", "H_3", "H_4",
    "E_2del1_p", "E_2del2_p", "E_2del3_p",
    "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp",
    "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm",
    "E_2del1_m", "E_2del2_m", "E_2del3_m",
    "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm",
    "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"
  ]
}
```

## 9. `parity`

The `parity` object maps basis generators to their $\mathbb{Z}_2$ parity:

- Cartan generators are `0`
- even root generators are `0`
- odd root generators are `1`

Example pattern:

```json
{
  "H_1": 0,
  "H_2": 0,
  "E_2del1_p": 0,
  "E_2del1_m": 0,
  "E_del1_del2_pp": 0,
  "E_del1_del2_pm": 0,
  "E_del1_del2_mm": 0,
  "E_del1_del2_mp": 0,
  "E_eps1_del1_pp": 1,
  "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1,
  "E_eps1_del1_mm": 1
}
```

The `parity` object covers basis generators only; `kappa` and `K` are tracked
under `central_elements`.

## 10. `generator_realization`

Each generator is expressed as a sum of oscillator words with rational
coefficients, using a standard oscillator-word ordering.

Recommended ordering string:

```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": { ... }
}
```

Representative entries:

```json
{
  "H_1": {
    "standard_form": [
      {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
      {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
    ],
    "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
    "parity": 0
  },
  "H_k": {
    "standard_form": [
      {"words": ["b_{k-1}_p", "b_{k-1}_m"], "coeff": "1"},
      {"words": ["b_k_p", "b_k_m"], "coeff": "-1"}
    ],
    "frappat_form": "b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-",
    "parity": 0
  },
  "H_{n+1}": {
    "standard_form": [
      {"words": ["b_n_p", "b_n_m"], "coeff": "-1"},
      {"words": [], "coeff": "-1/2"}
    ],
    "frappat_form": "-b_n^+ b_n^- - 1/2",
    "parity": 0
  },
  "E_eps1_del{k}_pp": {
    "standard_form": [
      {"words": ["a_1_p", "b_k_p"], "coeff": "1"}
    ],
    "frappat_form": "a_1^+ b_k^+",
    "parity": 1
  },
  "E_eps1_del{k}_pm": {
    "standard_form": [
      {"words": ["a_1_p", "b_k_m"], "coeff": "1"}
    ],
    "frappat_form": "a_1^+ b_k^-",
    "parity": 1
  },
  "E_eps1_del{k}_mp": {
    "standard_form": [
      {"words": ["a_1_m", "b_k_p"], "coeff": "1"}
    ],
    "frappat_form": "a_1^- b_k^+",
    "parity": 1
  },
  "E_eps1_del{k}_mm": {
    "standard_form": [
      {"words": ["a_1_m", "b_k_m"], "coeff": "1"}
    ],
    "frappat_form": "a_1^- b_k^-",
    "parity": 1
  }
}
```

Even root generators reuse the approved labels from `handover/notation.md`:

- `E_2del{k}_p`, `E_2del{k}_m`
- `E_del{i}_del{j}_pp`
- `E_del{i}_del{j}_pm`
- `E_del{i}_del{j}_mm`
- `E_del{i}_del{j}_mp`

## 11. `structure_constants`

The `structure_constants` field keeps the B-series list-based format:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "1",
    "sign_rule": "graded"
  }
]
```

Conventions:

- store only non-zero graded brackets
- use the existing `X`, `Y`, `Z`, `coeff`, `sign_rule` entry layout
- compute brackets using the C-series CAR/CCR oscillator relations

## 12. `metadata`

The `metadata` object keeps the existing schema shape:

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

If the implementation uses a different generator script name, only the
`generated_by` string should change; the metadata layout remains the same.

## 13. Compatibility Summary Relative to B(m,n) v5.0

| Area | B-series v5.0 | C-series v5.0 draft |
|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` |
| `algebra` shape | existing | unchanged shape, C-family values |
| fermion object | `supplementary_fermion` | `standard_fermion` |
| boson object | `bosons` | unchanged |
| fermion relations | auxiliary relation | CAR relation object |
| `central_elements` | implied/note-only | explicit top-level key |
| basis ordering | B-series PBW | approved C-series Option A |
| file naming | `B_n_structure.json` | `C_n_structure.json` |

This draft therefore preserves the v5.0 schema family structure while making
the minimum explicit changes required for the C(n+1) oscillator model.
