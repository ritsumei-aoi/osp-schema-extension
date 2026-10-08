# C(n+1) v5.0 JSON Schema Specification

This document defines Schema 1 (algebra structure) for
\(C(n+1)=\mathfrak{osp}(2|2n)\), extending the B(m,n) schema conventions in
`docs/math/B0n_schema_v5.md`. All files use schema version `5.0`.

## File naming

Use the bosonic rank \(n\) in the filename: `C_{n}_structure.json`.
Therefore C(2) = osp(2|2) uses `C_1_structure.json`, C(3) uses
`C_2_structure.json`, and C(4) uses `C_3_structure.json`.

## Schema 1 top-level keys

Every structure file contains:

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

### `algebra`

For bosonic rank `n`, `m` is fixed to `1`. Dimensions are the even, odd,
and total dimensions of \(\mathfrak{osp}(2|2n)\):

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
  "dimension": {
    "total": 19,
    "even": 11,
    "odd": 8
  }
}
```

The formulas are `even = 2n^2 + n + 1`, `odd = 4n`, and
`total = 2n^2 + 5n + 1`.

### `oscillator_generators`

The fermion is a standard pair; there is no supplementary fermion.

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^-"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± for k=1,...,n"
  }
}
```

`bosons.count` is `2*n`; list labels by increasing index, plus then minus.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermion pair",
    "relations": {
      "{a_1_m, a_1_p}": "1",
      "{a_1_p, a_1_p}": "0",
      "{a_1_m, a_1_m}": "0"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0 in the undeformed oscillator algebra"
  }
}
```

In Schema 1, these are undeformed relations. Inhomogeneous exchanges belong
to the separate deformation schema.

### `central_elements`

This is a required top-level key. The formal nilpotent extension symbol
\(\kappa\) and scalar identity symbol \(K\) are recorded here, not as
independent PBW basis elements:

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "kappa^2 = 0",
    "description": "Formal odd central symbol for the inhomogeneous extension"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "central": true,
    "identified_with_scalar_identity": true,
    "relation": "K = 1",
    "description": "Even central identity; excluded as an independent basis element"
  }
}
```

### `basis`

The even basis consists of `H_1` through `H_{n+1}`, the generators for
\(\pm2\delta_k\), and the four generators for each pair
\(\delta_i,\delta_j\), \(i<j\). The odd basis consists of the four generators
for \(\pm\varepsilon\pm\delta_k\). Use the exact labels and explicit lists
for ranks 1–3 documented in `handover/notation.md`.

The canonical order is: even Cartan; positive long roots; positive pair
roots; negative long roots; negative sum roots; \(\delta_i-\delta_j\)
roots; \(-\delta_i+\delta_j\) roots. Within each root group use increasing
indices, lexicographically for pairs. Odd generators are ordered by
increasing \(k\), then `pp`, `pm`, `mp`, `mm`.

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": [
    "E_eps1_del1_pp",
    "E_eps1_del1_pm",
    "E_eps1_del1_mp",
    "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd] < [even]; K = 1 is excluded"
}
```

The shown basis is the `n=1` example; generated files must include every
basis label for their rank. Labels and sign meanings are defined in
`handover/notation.md`.

### `parity`

Provide one entry for every basis generator, with even parity `0` and odd
parity `1`. All `H_k`, `E_2del{k}_p/m`, and `E_del{i}_del{j}_xy` are even;
all `E_eps1_del{k}_xy` are odd. Central-element parities are specified
separately in `central_elements`.

### `generator_realization`

Store each basis generator as ordered oscillator words with rational-string
coefficients. The oscillator ordering is
`a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`.

```json
{
  "description": "Standard form with PBW-ordered oscillator words",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "E_eps1_del1_pm": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^-",
      "parity": 1
    }
  }
}
```

Provide a realization for every basis generator. Use the oscillator
realizations and Cartan conventions in `docs/math/Cn1_definition.md`; the
displayed records illustrate the required data shape.

### `structure_constants`

Store every nonzero undeformed graded bracket \([X,Y\}\) as an entry with
generator labels, rational-string coefficient, and graded sign convention:

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

Include all nonzero brackets for the selected rank, using the oscillator
relations and generator normalizations. Deformed \(\kappa\)-terms are stored
in the deformation schema, not here.

### `metadata`

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

## Compatibility with B(m,n)

Keep the v5.0 top-level organization, `schema_version`, basis/parity
representation, oscillator-word realization format, bracket record format,
and metadata conventions from the B(m,n) schema. C(n+1) specializes `m=1`,
uses the standard fermionic pair in place of B(0,n)'s supplementary fermion,
adds the required top-level `central_elements`, expands the odd roots to
\(4n\), and includes the additional \(\mathfrak{so}(2)\) Cartan dimension.
The B(0,n) structure files remain unchanged.
