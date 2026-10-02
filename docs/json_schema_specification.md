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

## Compatibility with B(m,n) v5.0

The C-family keeps the v5.0 top-level structure and field roles for `schema_version`,
`algebra`, `basis`, `parity`, `generator_realization`, `structure_constants`,
and `metadata`. It adds the required top-level `central_elements` field and
changes algebra parameters, oscillator fields, root labels, and corresponding
brackets as specified above. C-family files are separate `C_{n}_...` files;
existing B-family files and their `supplementary_fermion` representation remain
unchanged. A consumer can distinguish the families by `algebra.family` and
the filename prefix, while common fields retain their v5.0 meaning.
