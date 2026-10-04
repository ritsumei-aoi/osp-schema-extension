# C(n+1) v5.0 JSON Schema Specification

This document defines Schema 1 (algebra structure) for
$C(n+1)=\mathfrak{osp}(2|2n)$ using schema version `5.0`. It extends the
B(m,n) Schema 1 organization without changing the meaning of its shared
fields. The C-specific fermions, odd roots, dimension, and central-element
fields are described below.

## File naming

Use the bosonic rank in filenames: `C_{n}_structure.json`,
`C_{n}_gamma.json`, `C_{n}_evaluated_<gb>.json`, and
`C_{n}_coboundary_<gb>.json`. For the representative all-plus evaluation in
this study, use the fixed filenames `C_{n}_evaluated.json`. Thus
C(2) = osp(2|2) (`n=1`) uses
`C_1_structure.json`, C(3) (`n=2`) uses `C_2_structure.json`, and C(4)
(`n=3`) uses `C_3_structure.json`.

## Schema 1 fields

Every structure file has `schema_version`, `algebra`,
`oscillator_generators`, `oscillator_relations`, `central_elements`,
`basis`, `parity`, `generator_realization`, `structure_constants`, and
`metadata`.

### `schema_version` and `algebra`

`schema_version` is the string `"5.0"`. The algebra record has family `"C"`,
`m: 1`, rank `n`, Cartan type `C(n+1)`, alternative notation, and dimensions:

```json
{
  "family": "C",
  "m": 1,
  "n": 1,
  "cartan_type": "C(2)",
  "alternative_notation": {
    "osp": "osp(2|2)",
    "dimension_formula": "osp(2m|2n)"
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

The dimension formulas apply for every `n >= 1`; the example uses `n=1`.

### `oscillator_generators`

There are exactly two generator-sector keys: a standard fermionic pair and
the rank-`n` bosons. `labels` are ordered consistently with the oscillator
ordering used in `generator_realization`.

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
    "parity": 0,
    "description": "Bosonic oscillators b_k^+, b_k^- for k=1,...,n"
  }
}
```

There is no `supplementary_fermion` field.

### `oscillator_relations` and `central_elements`

The standard fermionic pair satisfies the CAR, the bosons satisfy the CCR,
and undeformed mixed oscillator commutators vanish. During deformation, the
specified mixed relations are supplied by the Schema 2 gamma data.

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations",
    "relations": {
      "same_type": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i,j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
    }
  },
  "mixed_commutators": {
    "fermion_boson": "[a_1^σ, b_j^s] = 0 in the undeformed algebra"
  }
}
```

`central_elements` is a top-level object, not a member of
`oscillator_relations`. It records the odd nilpotent extension symbol and
the even identity symbol; neither is an independent member of the
$C(n+1)$ basis.

```json
{
  "kappa": {
    "label": "κ",
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "κ^2 = 0"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "central": true,
    "identified_with": "1",
    "independent_basis_element": false
  }
}
```

### `basis` and `parity`

The even basis contains `H_1` through `H_{n+1}`, both roots for each
$2\delta_k$, and all four roots for each pair $i<j$. It has
$2n^2+n+1$ generators. The odd basis contains all four roots
$\pm\varepsilon\pm\delta_k$ for each `k` and has `4n` generators.
Generator spelling, signs, and complete `n=1,2,3` lists are defined in
`handover/notation.md`. Arrays follow its PBW order: negative roots, Cartan,
then positive roots; within each root block, even roots precede odd roots.
The parity map assigns `0` to every even basis generator and `1` to every
odd basis generator. It does not include `κ` or `K`.

### `generator_realization`

Each realization uses `standard_form`, a list of oscillator words and
rational-string coefficients, the display expression `frappat_form`, and
generator `parity`. The oscillator ordering is
`a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`.
The realizations are determined by

```text
H_1 = a_1_p a_1_m + b_1_p b_1_m
H_k = b_(k-1)_p b_(k-1)_m - b_k_p b_k_m                  (2 <= k <= n)
H_(n+1) = -b_n_p b_n_m - 1/2
E_2del{k}_p/m = 1/2 (b_k_p/m)^2
E_del{i}_del{j}_pp/pm/mp/mm = b_i_(first sign) b_j_(second sign)
E_eps1_del{k}_pp/pm/mp/mm = a_1_(epsilon sign) b_k_(delta sign)
```

For the final line, `pp`, `pm`, `mp`, `mm` mean respectively
$\varepsilon+\delta_k$, $\varepsilon-\delta_k$,
$-\varepsilon+\delta_k$, $-\varepsilon-\delta_k$. Each expression is
stored as ordered words in the JSON `standard_form`; scalar terms use an
empty word. The terminal `1/2` in `H_(n+1)` and the `1/2` on `E_2del`
follow the explicit simple-generator normalization in
`Cn1_definition.md`.

### `structure_constants`

This is a list of non-zero graded brackets in the basis. Each entry has
`X`, `Y`, `Z`, `coeff` (a rational string), and `sign_rule: "graded"`,
representing $[X,Y\}= \mathrm{coeff}\,Z$. Store one canonical ordered pair
according to the PBW ordering, rather than duplicating its graded-skew
counterpart. Coefficients must be computed from the declared oscillator
realizations and CAR/CCR; omit zero brackets. The schema definition does not
replace or approximate the rank-specific computed list.

### `metadata`

`metadata` records the generator name, ISO generation date, and references,
following the B(m,n) Schema 1 convention. For example:

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

## Schema 3: Evaluated structure

The evaluated file records the chosen numeric gb assignment and merges
Schema 1 brackets with the first-order Schema 2 correction. Its top-level
fields are `schema_version`, `schema_layer` (integer `3`), `algebra`,
`source_files`, `gb_assignment`, `central_elements`,
`structure_constants`, and `metadata`. `gb_assignment.values` must specify
every parameter named by the source gamma file exactly once.

Each evaluated structure-constant record has canonical `X`, `Y`, and `Z`
labels, `coeff` (the Schema 1 rational coefficient), `kappa_coeff` (the
Schema 2 coefficient after numeric substitution), and `sign_rule: "graded"`.
The represented bracket is
`[X,Y] = coeff * Z + kappa_coeff * κ * Z`; omit a record only when both
coefficients are zero. `K` is permitted as `Z` for scalar identity terms.
The nilpotence relation `κ^2=0` means no higher powers are evaluated.

The issue's representative profile is `all_plus`: every gb parameter is
assigned integer `1`. This assignment is a concrete representative, not a
claim that all deformations are equivalent. A different profile must be
identified in the filename or assignment metadata.

## Compatibility with B(m,n)

The shared v5.0 envelope (`schema_version`, `algebra`, `basis`, `parity`,
`generator_realization`, `structure_constants`, and `metadata`) keeps its
existing purpose and data types. A consumer must dispatch on
`algebra.family`: C files use `m: 1`, the dimension formulas above, the
`fermions` pair instead of B's `supplementary_fermion`, CAR rather than
`a_0^2=1/2`, four odd roots per bosonic index instead of two, and the
top-level `central_elements` key. B(m,n) files and their field meanings are
not changed by this C-specific extension.
