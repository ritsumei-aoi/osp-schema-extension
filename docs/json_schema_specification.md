# C(n+1) v5.0 JSON Schema Specification

This document defines the complete Schema 1 structure for
$C(n+1)=\mathfrak{osp}(2|2n)$, extending the B(0,n) v5.0 schema without
changing existing B-family files. Here $n\geq1$ is the bosonic rank.

## File naming

Schema 1 files use `C_{n}_structure.json`, where `{n}` is the bosonic rank:
`C_1_structure.json` describes C(2), `C_2_structure.json` describes C(3), and
`C_3_structure.json` describes C(4). The `C_` prefix and rank distinguish these
files from B-family `B_{n}_structure.json` files.

## Schema 1 top-level fields

A Schema 1 document contains:

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

Each field is defined below. Counts, root-index ranges, and basis entries are
instantiated for the selected rank; formula strings remain symbolic.

### `schema_version`

The string `"5.0"`, matching the base schema version.

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
    "odd": 8
  },
  "dimension_formula": {
    "even": "2n^2 + n + 1",
    "odd": "4n",
    "total": "2n^2 + 5n + 1"
  }
}
```

The values shown are the `n=2` example. For arbitrary rank, set
`cartan_type` to `"C(n+1)"`, `osp` to `"osp(2|2n)"`, and numeric dimensions to
$2n^2+n+1$, $4n$, and $2n^2+5n+1$. Keep `m` explicitly equal to `1`.

### `oscillator_generators`

This object has exactly the `fermions` and `bosons` keys:

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "One standard fermionic creation/annihilation pair"
  },
  "bosons": {
    "rank": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_i^± for i=1,...,n"
  }
}
```

For rank $n$, `bosons.rank` is $n`, `bosons.count` is $2n`, and labels contain
`b_i_p`, `b_i_m` for each $i=1,\ldots,n$. There is no supplementary fermion
`a_0`.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for a_1^±",
    "relations": {
      "same_type": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for b_i^±",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i,j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
    }
  },
  "mixed_commutators": {
    "fermion_boson": "[a_1^±, b_i^±] = 0 for all i and signs"
  }
}
```

### `central_elements`

This is a top-level key, separate from `oscillator_relations`:

```json
{
  "kappa": {
    "parity": 1,
    "nilpotent": true,
    "description": "Odd formal parameter for the central extension"
  },
  "K": {
    "parity": 0,
    "value": "1",
    "description": "Even central identity; excluded from the independent basis"
  }
}
```

`kappa` and `K` are schema metadata for the extension framework, not
independent generators in the finite-dimensional C(n+1) basis. `K` is
identified with the scalar identity and is not included in PBW monomials.

### `basis`

The Cartan generators are `H_1`, ..., `H_{n+1}`, following the simple-generator
convention in `docs/math/Cn1_definition.md`. Use the
generator labels in `handover/notation.md`; include all positive and negative
root generators and the Cartan generators, but not `K` or `kappa`.

Positive even roots are $2\delta_i$ and $\delta_i\pm\delta_j$ for $i<j$.
Positive odd roots are $\varepsilon-\delta_i$ and $\varepsilon+\delta_i$.
Every root vector is labeled according to the signs of its coordinates; e.g.,
`E_eps_del1_pm` denotes the root $\varepsilon-\delta_1$.

For root-vector labels and the total PBW order (negative even, negative odd,
Cartan, positive even, positive odd), see `handover/notation.md`. The ordered
arrays in `even` and `odd` must each follow that total order restricted to the
respective parity.

```json
{
  "even": [
    "E_del1_del2_mp", "E_del1_del2_mm", "E_2del2_m", "E_2del1_m",
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_del1_del2_pm"
  ],
  "odd": [
    "E_eps_del2_mm", "E_eps_del1_mm", "E_eps_del2_mp", "E_eps_del1_mp",
    "E_eps_del1_pm", "E_eps_del2_pm", "E_eps_del1_pp", "E_eps_del2_pp"
  ],
  "ordering_convention": "PBW: negative even < negative odd < Cartan < positive even < positive odd; K and kappa excluded"
}
```

The displayed rank-2 arrays follow the selected ordering: negative roots are
listed in reverse of their corresponding positive-root family order; Cartan
generators occur between negative and positive roots.

### `parity`

An object mapping every label in `basis.even` to `0` and every label in
`basis.odd` to `1`. It contains no entries for `K` or `kappa`.

### `generator_realization`

Each basis generator maps to an object containing `standard_form` (a list of
oscillator words and rational-coefficient strings), `frappat_form`, and
`parity`. A word is an ordered list of oscillator labels. The oscillator
ordering is `a_1_p`, `a_1_m`, followed by `b_1_p`, `b_1_m`, ..., `b_n_p`,
`b_n_m`.

The realization patterns are:

| Generator | Oscillator realization |
|---|---|
| $H_1$ | $a_1^+a_1^- + b_1^+b_1^-$ |
| $H_k$, $2\leq k\leq n$ | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ |
| $H_{n+1}$ | $-b_n^+b_n^- - \tfrac12$ |
| $E_{2\delta_i}$ / $E_{-2\delta_i}$ | $(b_i^+)^2$ / $(b_i^-)^2$ |
| $E_{\delta_i+\delta_j}$ / $E_{-(\delta_i+\delta_j)}$ | $b_i^+b_j^+$ / $b_i^-b_j^-$ |
| $E_{\delta_i-\delta_j}$ / $E_{-(\delta_i-\delta_j)}$ | $b_i^+b_j^-$ / $b_i^-b_j^+$ |
| $E_{\varepsilon+\delta_i}$ / $E_{\varepsilon-\delta_i}$ | $a_1^+b_i^+$ / $a_1^+b_i^-$ |
| $E_{-\varepsilon+\delta_i}$ / $E_{-\varepsilon-\delta_i}$ | $a_1^-b_i^+$ / $a_1^-b_i^-$ |

In each realization object, include its parity (`0` for even generators and
`1` for odd generators). Constants are represented as words `[]`, using a
rational string coefficient. Use a fixed normalization consistently with
`docs/math/Cn1_definition.md`.

### `structure_constants`

An array containing each non-zero graded bracket exactly once, represented as
objects of the form:

```json
[
  {
    "X": "H_3",
    "Y": "E_2del2_p",
    "Z": "E_2del2_p",
    "coeff": "-2",
    "sign_rule": "graded"
  }
]
```

`X`, `Y`, and `Z` must be labels in the basis. `coeff` is a rational string;
`sign_rule` is `"graded"`. Compute the entries using the C(n+1) oscillator
realization and CAR/CCR relations; do not copy B(0,n) constants for brackets
involving the changed fermionic generators. Store only non-zero brackets, with
the repository's established duplicate-bracket convention applied consistently.

### `metadata`

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

Replace the date and generator name with the actual generation information
when a file is produced.

## Schema 2: Inhomogeneous deformation

Schema 2 files use `C_{n}_gamma.json` and reference the corresponding
`C_{n}_structure.json` through `source_schema`. They retain `schema_version`
and the C-family algebra identity, then record the deformation parameters and
the first-order gamma coefficients:

```json
{
  "schema_version": "5.0",
  "algebra": {
    "family": "C",
    "m": 1,
    "n": 2,
    "cartan_type": "C(3)"
  },
  "source_schema": "C_2_structure.json",
  "gb_matrix": {
    "shape": [2, 4],
    "rows": ["a_1_p", "a_1_m"],
    "columns": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "entries": [
      ["gb_a_1_p_b_1_p", "gb_a_1_p_b_1_m", "gb_a_1_p_b_2_p", "gb_a_1_p_b_2_m"],
      ["gb_a_1_m_b_1_p", "gb_a_1_m_b_1_m", "gb_a_1_m_b_2_p", "gb_a_1_m_b_2_m"]
    ],
    "parameter_parity": 1
  },
  "inhomogeneous_deformation": {
    "exchange_relations": [],
    "bracket_convention": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
    "gamma_coefficients": [
      {
        "X": "E_2del1_m",
        "Y": "E_eps_del1_mp",
        "Z": "K",
        "coeff": "-gb_a_1_m_b_1_m",
        "sign_rule": "graded"
      }
    ]
  },
  "metadata": {}
}
```

The matrix has two fermion rows and $2n$ boson columns, hence $4n$ odd
parameters. `exchange_relations` enumerates
$[b_j^s,a_1^\sigma]=-\mathrm{gb}_{a_1^\sigma,b_j^s}\kappa$ for every row and
column pair. Each `gamma_coefficients` entry contributes
`coeff * Z` to $\gamma(X,Y)$; expressions are exact rational linear
combinations of named `gb` parameters. Bracket records use the same canonical
pair order and `sign_rule` as Schema 1. A scalar contraction is represented by
`Z: "K"`: the central identity is permitted as a Schema 2 output, but remains
excluded from the independent Schema 1 basis.

The generator factors odd central $\kappa$ to the left of the gamma value using
supercentral signs. The source assigns odd parity to `gb` parameters; it also
states the mixed exchange relation in a way whose right-hand parity is
ambiguous. Schema 2 therefore follows the displayed exchange relation
literally and records this parity convention explicitly rather than inferring
another relation.

## Schema 3: Evaluated structure

Schema 3 files use `C_{n}_evaluated.json` and reference both source layers.
The initial representative profile sets every parameter to `+1`. Each
evaluated structure-constant record preserves the undeformed coefficient and
the substituted coefficient of $\kappa$ separately:

```json
{
  "schema_version": "5.0",
  "algebra": {
    "family": "C",
    "m": 1,
    "n": 1,
    "cartan_type": "C(2)"
  },
  "source_schema": "C_1_structure.json",
  "source_gamma_schema": "C_1_gamma.json",
  "gb_assignment": {
    "name": "all_plus",
    "description": "All 4 gb parameters set to +1",
    "values": {
      "gb_a_1_p_b_1_p": 1,
      "gb_a_1_p_b_1_m": 1,
      "gb_a_1_m_b_1_p": 1,
      "gb_a_1_m_b_1_m": 1
    }
  },
  "evaluated_structure": {
    "coefficient_convention": "base_coeff + kappa * kappa_coeff",
    "structure_constants": [
      {
        "X": "E_2del1_m",
        "Y": "E_eps_del1_mp",
        "Z": "K",
        "base_coeff": "0",
        "kappa_coeff": "-1",
        "sign_rule": "graded"
      }
    ]
  },
  "metadata": {}
}
```

Substitution is exact over rational coefficients. A zero component is encoded
as `"0"`; records are emitted when either component is nonzero. `K` remains a
central output available to Schema 2, not a Schema 1 basis element.

## Schema 4: Coboundary structure

Schema 4 files use `C_{n}_coboundary.json` and reference the corresponding
Schema 1 basis. They encode a generic odd linear map by one independent
coefficient for every parity-reversing source/target pair. The coefficient
parameters are even scalars; the map itself has parity 1.

```json
{
  "schema_version": "5.0",
  "algebra": {
    "family": "C",
    "m": 1,
    "n": 1,
    "cartan_type": "C(2)"
  },
  "source_schema": "C_1_structure.json",
  "odd_linear_map": {
    "parity": 1,
    "parameter_parity": 0,
    "entries": [
      {
        "source": "H_1",
        "target": "E_eps_del1_pm",
        "coefficient": "phi_E_eps_del1_pm_from_H_1"
      }
    ]
  },
  "coboundary": {
    "formula": "(delta f)(X,Y) = (-1)^p(X)[X,f(Y)] - (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])",
    "coefficients": [
      {
        "X": "E_2del1_m",
        "Y": "E_2del1_m",
        "Z": "E_eps_del1_mm",
        "coeff": "4*phi_E_eps_del1_mp_from_E_2del1_m",
        "sign_rule": "graded"
      }
    ]
  },
  "metadata": {}
}
```

For each generator $Z_j$, `odd_linear_map.entries` includes every basis
generator $Z_i$ of opposite parity with independent coefficient
`phi_{Z_i_from_Z_j}`. Each coboundary record gives the exact symbolic
coefficient of $Z$ in $(\delta f)(X,Y)$; expressions are rational linear
combinations of these map parameters. Inputs and outputs must be Schema 1
basis labels, and all brackets use the Schema 1 graded structure constants.

## Compatibility with B(m,n) v5.0

The C-family keeps the v5.0 top-level structure and field roles for `schema_version`,
`algebra`, `basis`, `parity`, `generator_realization`, `structure_constants`,
and `metadata`. It adds the required top-level `central_elements` field and
changes algebra parameters, oscillator fields, root labels, and corresponding
brackets as specified above. C-family files are separate `C_{n}_...` files;
existing B-family files and their `supplementary_fermion` representation remain
unchanged. A consumer can distinguish the families by `algebra.family` and
the filename prefix, while common fields retain their v5.0 meaning.
