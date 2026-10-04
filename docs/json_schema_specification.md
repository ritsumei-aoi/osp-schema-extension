# C(n+1) Schema 1 Specification

This document defines the standalone Schema 1 algebra-structure format for
$C(n+1)=\mathfrak{osp}(2|2n)$, extending the existing B(m,n) v5.0
specification in `docs/math/B0n_schema_v5.md`. The parameter `n` is the
bosonic rank: C(2), C(3), and C(4) are stored as `C_1`, `C_2`, and `C_3`.

## Naming and dimensions

Use `C_{n}_structure.json`, with `n` the number of bosonic oscillator pairs.
The algebra record has `family: "C"`, `m: 1`, and `n` as that rank. Its
even, odd, and total dimensions are respectively
$2n^2+n+1$, $4n$, and $2n^2+5n+1$.

## Top-level object

Every Schema 1 file has the following keys:

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

`schema_version` remains `"5.0"` for compatibility with the B(m,n) format.
All algebra basis labels must occur exactly once in `parity` and
`generator_realization`. `structure_constants` contains the nonzero brackets
among those labels.

## Field definitions

### `algebra`

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
    "odd": 8,
    "even_formula": "2n^2 + n + 1",
    "odd_formula": "4n",
    "total_formula": "2n^2 + 5n + 1"
  }
}
```

Replace the sample `n`, cartan type, osp notation, and dimension values with
the selected rank. In particular, `C_1_structure.json` describes C(2) =
osp(2|2), not rank-one C(1).

### `oscillator_generators`

The required keys are `fermions` and `bosons`; there is no supplementary
fermion.

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "One standard fermionic creation/annihilation pair."
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic creation/annihilation pairs for i=1,...,n."
  }
}
```

`p` and `m` suffixes mean creation (`+`) and annihilation (`-`),
respectively.

### `oscillator_relations`

The standard, undeformed oscillator relations are:

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard pair.",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators.",
    "relations": {
      "same_type": "[b_i_s, b_j_t] = 0",
      "conjugate_pair": "[b_i_m, b_j_p] = δ_ij"
    }
  },
  "mixed_commutators": {
    "fermion_boson": "[a_1_s, b_i_t] = 0"
  }
}
```

Here $s,t\in\{p,m\}$. Deformed exchange relations belong in the later gamma
layer, not in these base relations.

### `central_elements`

This is a required top-level key. It records the odd formal extension symbol
and the even identity; neither is an independent member of the Lie
superalgebra basis.

```json
{
  "kappa": {
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "kappa^2 = 0"
  },
  "K": {
    "parity": 0,
    "central": true,
    "identity": true,
    "relation": "K = 1"
  }
}
```

### `basis`

`even` contains `H_1` through `H_{n+1}`, the `E_2del{i}_p/m` labels for
`i=1,...,n`, and all four `E_del{i}_del{j}_{pp,pm,mp,mm}` labels for
`1<=i<j<=n`. `odd` contains the four
`E_eps1_del{k}_{pp,pm,mp,mm}` labels for each `k=1,...,n`. The roots and
oscillator realizations of these labels are fixed in `handover/notation.md`.

Use this PBW order: `κ < [odd generators] < [even generators]`. Within the
odd block, order by increasing `k`, then `pp, pm, mp, mm`. Within the even
block, order Cartan first, positive roots second and negative roots last, as
specified in the notation document. `K=1` is recorded only in
`central_elements`, not in the basis or PBW lists.

```json
{
  "even": ["H_1", "H_2", "H_3"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm"],
  "ordering_convention": "PBW: κ < [odd] < [even]; K = 1 is excluded."
}
```

The arrays above are abbreviated shape examples, not complete bases; actual
files must enumerate every basis generator for the chosen rank.

### `parity`

Map every even and odd basis label to integer parity `0` or `1`,
respectively. The mapping is complete and contains no `kappa` or `K` entry:

```json
{
  "H_1": 0,
  "E_2del1_p": 0,
  "E_eps1_del1_pp": 1
}
```

### `generator_realization`

Store `description`, an `ordering` array of oscillator labels, and a
`realizations` object indexed by every basis generator. Each realization
contains `standard_form` (a sum of `{"words": [...], "coeff": "..."}` terms),
`frappat_form`, and `parity`. Coefficients are strings (including rational
numbers); the empty word denotes a scalar.

```json
{
  "description": "Standard form with PBW ordering.",
  "ordering": ["a_1_p", "a_1_m", "b_1_p", "b_1_m"],
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
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

The example is illustrative; actual files must provide the full basis
realizations using the formulas in `docs/math/Cn1_definition.md`.

### `structure_constants`

Represent each nonzero graded bracket by `X`, `Y`, `Z`, `coeff`, and
`sign_rule`. The entry means $[X,Y\}=coeff\,Z$. Use
`"sign_rule": "graded"` and omit zero brackets. Include a consistent
independent set of brackets; graded antisymmetry determines reversed pairs.

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

### `metadata`

Include the generator name, ISO generation date, and references. Metadata
must identify the C(n+1) generator rather than reusing a B(m,n) generator.

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "docs/math/Cn1_definition.md"
  ]
}
```

## Compatibility with B(m,n)

The outer structure remains the v5.0 JSON format: version, algebra,
oscillators, basis, parity, realizations, structure constants, and metadata
retain their roles and data shapes. C(n+1) uses `family: "C"` and `m: 1`,
adds required top-level `central_elements`, and replaces B's supplementary
fermion and odd-root labels with the standard CAR pair and the four
$\pm\varepsilon\pm\delta_k$ odd-root labels. Dimension formulas and Cartan
rank also differ. B(m,n) files remain unchanged; consumers that validate
top-level keys should accept `central_elements` for C files.

## Schema 2: Inhomogeneous deformation

Use `C_{n}_gamma.json` for rank `n`. Schema 2 references the matching
`C_{n}_structure.json` and records its deformation as follows:

```json
{
  "schema_version": "5.0",
  "algebra": {
    "family": "C",
    "m": 1,
    "n": 1,
    "cartan_type": "C(2)",
    "base_structure_file": "C_1_structure.json"
  },
  "gb_matrix": {
    "shape": [2, 2],
    "row_labels": ["a_1_p", "a_1_m"],
    "column_labels": ["b_1_p", "b_1_m"],
    "parameters": [
      ["gb_a1p_b1p", "gb_a1p_b1m"],
      ["gb_a1m_b1p", "gb_a1m_b1m"]
    ],
    "parameter_parity": 1,
    "parameter_count": 4
  },
  "inhomogeneous_deformation": {
    "bracket_formula": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
    "oscillator_exchange_relations": [],
    "gamma_coefficients": [],
    "coefficient_convention": "gamma(X,Y) is the sum of coeff * gb_parameter * Z over records."
  },
  "metadata": {}
}
```

The `gb_matrix` rows index the two fermion modes and its columns enumerate
the `2n` bosonic oscillator labels (`b_i_p`, `b_i_m`). Each exchange-relation
record specifies `X`, `Y`, the formal relation, and its parameter. Each
`gamma_coefficients` record specifies `X`, `Y`, output `Z`, `parameter`,
rational-string `coeff`, and `"sign_rule": "graded"`; the represented term in
$\gamma(X,Y)$ is `coeff * gb_parameter * Z`. `Z` may be a Schema 1 basis
generator or `K`, the central identity, when scalar oscillator terms occur.
Deformation files record assumptions and parity exceptions rather than
silently changing the base Schema 1 parity map. The parity conflict in the
source exchange relation is documented in
`docs/math/C_inhomogeneous_definition.md`.

## Schema 3: Evaluated structure

Use `C_{n}_evaluated.json` for an exact substitution into Schema 2. It
references the matching Schema 1 and Schema 2 files, records one value for
every gb parameter, and merges base and deformation terms by `(X,Y,Z)`:

```json
{
  "schema_version": "5.0",
  "layer": 3,
  "algebra": {},
  "base_structure_file": "C_1_structure.json",
  "gamma_source_file": "C_1_gamma.json",
  "parameter_assignment": {"gb_a1p_b1p": 1},
  "assignment_profile": "all_plus_one",
  "evaluated_structure_constants": [
    {
      "X": "H_1",
      "Y": "E_eps1_del1_pp",
      "Z": "E_eps1_del1_pp",
      "base_coeff": "1",
      "kappa_coeff": "2",
      "evaluated_coefficient": "1 + kappa * (2)",
      "sign_rule": "graded"
    }
  ],
  "metadata": {}
}
```

`base_coeff` and `kappa_coeff` are exact rational strings and represent the
formal first-order coefficient `base_coeff + kappa * kappa_coeff`; they are
not a numerical assignment to the nilpotent element `kappa`. The default
representative profile assigns `+1` to every gb parameter. Validation must
confirm complete assignment coverage and reproduce every merged coefficient
from the referenced Schema 1 and Schema 2 inputs.

## Schema 4: Coboundary structure

Use `C_{n}_coboundary.json` for the symbolic coboundary of a general odd map.
The `odd_linear_map.parameters` array enumerates exactly one coefficient
`phi__<target>__<source>` for every ordered basis pair of opposite parity;
`parameter_count` is twice the product of the even and odd dimensions.
`coboundary_coefficients` stores sparse coefficient expressions grouped by
`(X,Y,Z)`:

```json
{
  "schema_version": "5.0",
  "layer": 4,
  "algebra": {},
  "base_structure_file": "C_1_structure.json",
  "odd_linear_map": {
    "parity": 1,
    "rule": "f(Z_j) = sum_i phi_{i,j} Z_i with parity(Z_i) = 1 - parity(Z_j).",
    "parameter_count": 32,
    "parameters": [
      {"parameter": "phi__E_eps1_del1_pp__H_1", "target": "E_eps1_del1_pp", "source": "H_1"}
    ]
  },
  "coboundary_definition": {
    "formula": "(delta f)(X,Y) = ...",
    "sign_rule": "graded",
    "coefficient_convention": "Each term coeff * parameter contributes to the stated Z coefficient."
  },
  "coboundary_coefficients": [
    {
      "X": "H_1",
      "Y": "H_1",
      "Z": "E_eps1_del1_pp",
      "terms": [{"parameter": "phi__E_eps1_del1_pp__H_1", "coeff": "1"}]
    }
  ],
  "metadata": {}
}
```

The full coboundary formula is the one in
`docs/math/C_coboundary_definition.md`. Coefficients are exact rational
strings and are computed from the referenced Schema 1 brackets.

## References

- `handover/notation.md` — finalized C(n+1) root, label, basis, and PBW
  conventions.
- `docs/math/B0n_schema_v5.md` — base v5.0 schema design.
- `docs/math/Cn1_definition.md` — C(n+1) roots and oscillator realization.
