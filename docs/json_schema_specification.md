# JSON Schema Specification for B(m,n) and C(n+1)

This document specifies Schema 1 (algebra structure) in schema version 5.0.
The B(m,n) schema remains unchanged. The C(n+1) definitions below extend the
same field structure with C-specific algebra data and a top-level
`central_elements` key.

## Schema 1: Algebra Structure

Schema 1 files contain the algebra metadata, oscillator data, basis,
generator realizations, and nonzero structure constants.

| Algebra | File name |
|---|---|
| B(0,n) | `B_n_structure.json` |
| C(n+1) = osp(2\|2n) | `C_<n>_structure.json` |

For C(n+1), `n` in the filename is the bosonic rank: C(2) uses
`C_1_structure.json`, C(3) uses `C_2_structure.json`, and C(4) uses
`C_3_structure.json`.

The schema version remains `"5.0"`.

## C(n+1) Field Definitions

### `algebra`

For C(n+1) = osp(2\|2n), `m` is fixed at 1 and `n` is the bosonic rank.
Store both the formulas and the evaluated integer dimensions for the selected
rank.

```json
{
  "family": "C",
  "m": 1,
  "n": 1,
  "cartan_type": "C(2)",
  "alternative_notation": {
    "osp": "osp(2|2)",
    "family_formula": "osp(2m|2n) with m=1"
  },
  "dimension_formula": {
    "even": "2n^2 + n + 1",
    "odd": "4n",
    "total": "2n^2 + 5n + 1"
  },
  "dimension": {
    "total": 8,
    "even": 4,
    "odd": 4
  }
}
```

For another rank, update `cartan_type`, `alternative_notation.osp`, and the
integer values in `dimension` while retaining the formulas. The dimensions
for the first three ranks are:

| `n` | Algebra | Even | Odd | Total |
|---:|---|---:|---:|---:|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

### `oscillator_generators`

C(n+1) uses a standard fermionic pair and `n` bosonic oscillator pairs. It
does not use B(m,n)'s supplementary fermion `a_0`.

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic creation and annihilation pair"
  },
  "bosons": {
    "n": 1,
    "count": 2,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

For rank `n`, the boson labels are `b_1_p`, `b_1_m`, through `b_n_p`,
`b_n_m`; the count is `2n`.

### `oscillator_relations`

The relations in Schema 1 are the undeformed oscillator relations. Later
deformation layers may specify nonzero mixed commutators.

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for a_1^±",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1^±, a_1^±} = 0"
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
    "boson_fermion": "[b_j^s, a_1^σ] = 0 in the undeformed algebra"
  }
}
```

Here `s, σ ∈ {+,−}`. The fermion anticommutator relation is
`{a_1^-,a_1^+}=1`; each fermion's anticommutator with itself is zero.

### `central_elements`

For C(n+1), `central_elements` is a **top-level** key, separate from
`oscillator_relations`. Neither element is included in the Lie-superalgebra
basis lists: `K` is the identity and `κ` belongs to the formal deformation
extension.

```json
{
  "kappa": {
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "κ^2 = 0"
  },
  "K": {
    "parity": 0,
    "central": true,
    "role": "identity",
    "realization": "1",
    "in_basis": false
  }
}
```

### `basis`

The even basis has `2n^2+n+1` generators:

- Cartan generators `H_1,...,H_{n+1}`.
- Long-root generators `E_2del{k}_p` and `E_2del{k}_m` for each `k`.
- For each `i<j`, pair-root generators
  `E_del{i}_del{j}_pp`, `_pm`, `_mp`, and `_mm`.

The odd basis has `4n` generators:
`E_eps1_del{k}_pp`, `_pm`, `_mp`, and `_mm` for each `k`.

The label suffixes encode signs as follows:

| Label suffix | Root |
|---|---|
| `E_2del{k}_p` / `E_2del{k}_m` | `+2δ_k` / `−2δ_k` |
| `E_del{i}_del{j}_pp` | `+δ_i+δ_j` |
| `E_del{i}_del{j}_pm` | `+δ_i−δ_j` |
| `E_del{i}_del{j}_mp` | `−δ_i+δ_j` |
| `E_del{i}_del{j}_mm` | `−δ_i−δ_j` |
| `E_eps1_del{k}_pp` | `+ε+δ_k` |
| `E_eps1_del{k}_pm` | `+ε−δ_k` |
| `E_eps1_del{k}_mp` | `−ε+δ_k` |
| `E_eps1_del{k}_mm` | `−ε−δ_k` |

The basis arrays contain the fully expanded generator labels for the selected
rank. `K` and `κ` are not basis entries.

Use the approved root-triangular PBW ordering: negative root vectors, Cartan
generators, then positive root vectors. The positive roots are
`2δ_k`, `δ_i+δ_j`, `δ_i−δ_j` (`i<j`), `ε+δ_k`, and `ε−δ_k`. Use ascending
indices within each group, with these group orders:

1. Negative odd roots (`mm`, `mp`), negative pair-even roots (`mm`, `mp`),
   negative long-even roots (`m`).
2. Cartan generators `H_1,...,H_{n+1}`.
3. Positive pair-even roots (`pp`, `pm`), positive long-even roots (`p`),
   positive odd roots (`pp`, `pm`).

The corresponding JSON field is:

```json
{
  "even": ["H_1", "..."],
  "odd": ["E_eps1_del1_pp", "..."],
  "ordering_convention": "PBW: negative root vectors < H_1,...,H_{n+1} < positive root vectors; see root and within-block ordering above"
}
```

### `parity`

Store a mapping for every basis generator. Cartan and all even-root
generators have parity 0; all `E_eps1_del{k}_...` generators have parity 1.
The mapping is fully expanded for the selected rank; for example:

```json
{
  "H_1": 0,
  "H_2": 0,
  "E_2del1_p": 0,
  "E_2del1_m": 0,
  "E_eps1_del1_pp": 1,
  "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1,
  "E_eps1_del1_mm": 1
}
```

### `generator_realization`

Retain the v5.0 field shape. The oscillator ordering is
`a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`. Each basis generator has a
`standard_form` (a list of oscillator words and rational coefficients), a
`frappat_form`, and its parity.

The Cartan realizations are:

```text
H_1     = a_1_p a_1_m + b_1_p b_1_m
H_k     = b_{k-1,p} b_{k-1,m} - b_{k,p} b_{k,m}    (2 <= k <= n)
H_{n+1} = -b_{n,p} b_{n,m} - 1/2
```

The root-generator labels map to oscillator words as defined above. In
particular:

```text
E_{+ε+δ_k} = a_1_p b_k_p
E_{+ε-δ_k} = a_1_p b_k_m
E_{-ε+δ_k} = a_1_m b_k_p
E_{-ε-δ_k} = a_1_m b_k_m
E_{+2δ_k}  = 1/2 (b_k_p)^2
E_{-2δ_k}  = 1/2 (b_k_m)^2
```

For `i<j`, the pair-root realizations are the corresponding products of
`b_i^± b_j^±`. The `1/2` coefficients for both long-root generators are
intentional and are used consistently for every `k`.

Example entry shape:

```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m",
  "realizations": {
    "E_eps1_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    },
    "E_2del1_p": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_p"], "coeff": "1/2"}
      ],
      "frappat_form": "1/2 (b_1^+)^2",
      "parity": 0
    }
  }
}
```

### `structure_constants`

Store the nonzero graded brackets as a list, retaining the v5.0 entry shape.
Recompute the C(n+1) constants from its CAR, CCR, and generator
realizations; do not reuse B(m,n) constants.

```json
[
  {
    "X": "H_2",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "-1",
    "sign_rule": "graded"
  }
]
```

The example illustrates the record format; each generated file contains the
complete set of nonzero brackets for its rank.

### `metadata`

Retain the v5.0 metadata shape and identify the C(n+1) generator and
references.

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

## Backward Compatibility

Existing B(m,n) files retain their existing field values, supplementary
fermion representation, basis labels, central-element handling, and
structure constants. The C(n+1) extension is selected by
`algebra.family: "C"` and uses the standard fermionic pair and the top-level
`central_elements` object specified here. Readers supporting both families
should treat that C-specific object conditionally; its addition does not
change the interpretation of existing B(m,n) files.
