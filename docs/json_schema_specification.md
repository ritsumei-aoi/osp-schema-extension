# C(n+1) v5.0 JSON Schema Specification

This document defines Schema 1 (algebra structure) for
\(C(n+1)=\mathfrak{osp}(2|2n)\), where \(n\) is the bosonic rank. It preserves
the v5.0 field conventions used by the B(m,n) schema while specifying the
C(n+1) oscillator pair, basis, and central elements.

## Scope and compatibility

Schema 1 contains the undeformed algebra structure, oscillator realization,
and nonzero graded structure constants. Deformation parameters and cocycle
data belong to Schema 2 and are not included in the Schema 1 relations or
structure constants.

The following v5.0 conventions are retained: `schema_version`, concrete
rank-specific dimension values, the `basis` and `parity` maps, the
`generator_realization` representation, the `structure_constants` array, and
the `metadata` fields. C(n+1) intentionally replaces the B(m,n)
`supplementary_fermion` with `fermions` and adds the required top-level
`central_elements` object. Existing B(m,n) documents and schemas are not
modified.

## File naming

Use `C_{n}_structure.json`, with \(n\) equal to the bosonic rank:

| Algebra | Bosonic rank | Schema 1 file |
|---|---:|---|
| C(2) = osp(2\|2) | 1 | `C_1_structure.json` |
| C(3) = osp(2\|4) | 2 | `C_2_structure.json` |
| C(4) = osp(2\|6) | 3 | `C_3_structure.json` |

## Top-level structure

Every C(n+1) Schema 1 document has these top-level keys:

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

## `schema_version`

Use the string value `"5.0"`.

## `algebra`

Set the family and superalgebra parameter to `"C"` and `m: 1`. Store
rank-specific integer dimensions in `dimension`, and store the general
dimension formulas in `dimension_formula`.

For C(3), where \(n=2\), the field is:

```json
{
  "family": "C",
  "m": 1,
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {
    "osp": "osp(2|4)",
    "dimension_formula": "osp(2m|2n)"
  },
  "dimension_formula": {
    "even": "2n^2 + n + 1",
    "odd": "4n",
    "total": "2n^2 + 5n + 1"
  },
  "dimension": {
    "total": 19,
    "even": 11,
    "odd": 8
  }
}
```

Use the same shape for all ranks, changing `n`, `cartan_type`, the `osp`
notation, and concrete dimensions as appropriate:

| \(n\) | `cartan_type` | `osp` | even | odd | total |
|---:|---|---|---:|---:|---:|
| 1 | `C(2)` | `osp(2|2)` | 4 | 4 | 8 |
| 2 | `C(3)` | `osp(2|4)` | 11 | 8 | 19 |
| 3 | `C(4)` | `osp(2|6)` | 22 | 12 | 34 |

## `oscillator_generators`

Do not include the B(m,n) `supplementary_fermion`. Define exactly two
oscillator groups, `fermions` and `bosons`. The fermion group records the
required `m: 1`; its two labels are the standard CAR pair. The boson group
records the bosonic rank and both oscillator labels for each index.

For \(n=2\):

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "One standard fermionic CAR pair a_1^+, a_1^-."
  },
  "bosons": {
    "rank": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillator pairs b_i^+, b_i^- for i=1,...,n."
  }
}
```

For general \(n\), use `rank: n`, `count: 2n`, and list `b_i_p`,
`b_i_m` in increasing index order. Here `m` is the superalgebra parameter,
while `count` is the number of individual oscillator labels.

## `oscillator_relations`

Schema 1 records the undeformed oscillator relations. The C(n+1) standard
fermionic pair satisfies the canonical anticommutation relations (CAR);
bosons satisfy the canonical commutation relations (CCR); bosons commute
with fermions. Inhomogeneous `gb` terms are defined in Schema 2.

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for a_1^+, a_1^-.",
    "relations": {
      "same_type": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for b_i^+, b_i^-.",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

The conjugate-pair CCR applies to every \(i,j\); the reverse commutator
follows by antisymmetry.

## `central_elements`

This is a required top-level key. Record both central symbols for schema
completeness, but do not include either symbol in the Lie superalgebra basis.
The odd deformation element \(\kappa\) has parity 1 and is nilpotent. \(K\)
has parity 0 and represents the scalar identity.

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
    "relation": "K = 1",
    "in_basis": false
  }
}
```

The `kappa` parity here follows the C(n+1) convention and the mandatory
unified rule; do not copy a conflicting parity value from a B(0,n) example.

## `basis`

The `even` and `odd` arrays contain only the C(n+1) Lie superalgebra
generators. The central symbols \(\kappa\) and \(K\) are not array entries.
Use the approved Issue I01-1 basis and PBW convention:

```text
κ < [odd generators] < [even generators]
```

`K` is the scalar identity and is excluded. When a schema view includes the
extended basis, \(\kappa\) is ordered before the algebra generators.

Use these array orders:

1. Even: `H_1` through `H_{n+1}`; positive long roots
   `E_2del{i}_p` in increasing \(i\); positive sum roots
   `E_del{i}_del{j}_pp` in lexicographic \((i,j)\) order; negative long roots
   `E_2del{i}_m`; negative sum roots `E_del{i}_del{j}_mm`; then, for each
   pair in lexicographic order, `E_del{i}_del{j}_pm` followed by
   `E_del{i}_del{j}_mp`.
2. Odd: for each \(i\) in increasing order, append
   `E_eps1_del{i}_pp`, `E_eps1_del{i}_pm`; then, for each \(i\) in
   increasing order, append `E_eps1_del{i}_mp`, `E_eps1_del{i}_mm`.

For C(3), \(n=2\), the arrays are:

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del2_pp", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm",
    "E_eps1_del2_mp", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [odd] < [even]; K = 1 is excluded."
}
```

For any rank, the arrays must contain \(2n^2+n+1\) even and \(4n\) odd
generators.

## `parity`

Use an object mapping every label in `basis.even` to integer `0` and every
label in `basis.odd` to integer `1`. The map must have one entry for each
basis label and no extra entries. Neither \(\kappa\) nor \(K\) is included in
this map.

## `generator_realization`

Retain the v5.0 object shape: a `description`, an `ordering` string, and a
`realizations` object. Each realization contains `standard_form` (a list of
oscillator `words` and rational-string `coeff` values), `frappat_form`, and
`parity`.

Use oscillator order `a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`.
The Cartan generators are:

\[
\begin{aligned}
H_1 &= a_1^+a_1^- + b_1^+b_1^-,\\
H_k &= b_{k-1}^+b_{k-1}^- - b_k^+b_k^- \quad (2\leq k\leq n),\\
H_{n+1} &= -b_n^+b_n^- - \tfrac12.
\end{aligned}
\]

Use the root labels defined in `handover/notation.md`. Realize root
generators as follows:

| Generator | Oscillator realization | Parity |
|---|---|---:|
| `E_2del{i}_p` | \(\tfrac12(b_i^+)^2\) | 0 |
| `E_2del{i}_m` | \(\tfrac12(b_i^-)^2\) | 0 |
| `E_del{i}_del{j}_pp` | \(b_i^+b_j^+\) | 0 |
| `E_del{i}_del{j}_pm` | \(b_i^+b_j^-\) | 0 |
| `E_del{i}_del{j}_mp` | \(b_i^-b_j^+\) | 0 |
| `E_del{i}_del{j}_mm` | \(b_i^-b_j^-\) | 0 |
| `E_eps1_del{i}_pp` | \(a_1^+b_i^+\) | 1 |
| `E_eps1_del{i}_pm` | \(a_1^+b_i^-\) | 1 |
| `E_eps1_del{i}_mp` | \(a_1^-b_i^+\) | 1 |
| `E_eps1_del{i}_mm` | \(a_1^-b_i^-\) | 1 |

**Long-root normalization:** use Choice B, uniformly multiplying every
long-root square by \(\tfrac12\), as approved for Issue I02-1. Thus the
simple-root expression and the all-root expression use the same normalization
for every \(i\).

## `structure_constants`

Use the v5.0 array of nonzero graded brackets. Each entry has the fields
`X`, `Y`, `Z`, `coeff`, and `sign_rule`; `coeff` is a rational string and
`sign_rule` is `"graded"`. Recompute the undeformed structure constants
using the CAR, CCR, mixed commutators, and approved uniform long-root
normalization. Do not include Schema 2 cocycle or `gb` deformation terms.
Keep the bracket list deterministic in the basis ordering.

```json
[
  {
    "X": "basis generator",
    "Y": "basis generator",
    "Z": "basis generator",
    "coeff": "rational number",
    "sign_rule": "graded"
  }
]
```

## `metadata`

Preserve the v5.0 metadata fields:

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "C(n+1) oscillator realization, docs/math/Cn1_definition.md"
  ]
}
```

Use the actual generation date and generator name in each produced data file.

## Schema 3: Evaluated structure

Schema 3 records one concrete assignment of the Schema 2 deformation
parameters. Use `C_{n}_evaluated.json` for bosonic rank \(n\). Preserve the
Schema 2 `schema_version`, `algebra`, and `inhomogeneous_deformation` metadata,
and include the corresponding Schema 1 `structure_constants` unchanged.

Within `inhomogeneous_deformation`, retain `gb_matrix`, `deformed_relations`,
and any scalar-projection metadata. Add `parameter_assignment`, an object
mapping every `gb_matrix` parameter name to its assigned integer value, and
replace the symbolic `gamma_structure` array with
`evaluated_gamma_structure`. The latter uses the same `X`, `Y`, `Z`, `coeff`,
and `sign_rule` fields; `coeff` is a canonical exact rational string after
substitution. Omit entries whose evaluated coefficient is zero. As in Schema
2, \(\kappa\) is implicit in each gamma record, and `Z` remains a Schema 1
basis label.

For the representative rank-two profile used by Issue I06-1, repeat the
following assignment for each bosonic index \(i\):

| Parameter row | `b_i_p` | `b_i_m` |
|---|---:|---:|
| `a_1_p` | `1` | `1` |
| `a_1_m` | `-1` | `1` |

The `metadata` object identifies `C_evaluated_generator.py` as the generator,
records the generation date, and retains the relevant references.
