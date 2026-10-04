# C(n+1) Schema 1 Specification (Draft)

This document specifies the v5.0 Schema 1 algebra-structure document for
$C(n+1)=\mathfrak{osp}(2|2n)$, extending the existing B(m,n) schema without
changing its B-family files. Here $n\geq1$ is the bosonic rank and $m=1$ is
fixed. C(2), C(3), and C(4) therefore use `n=1`, `n=2`, and `n=3`.

## File naming

Name a Schema 1 file `C_{n}_structure.json`, where the subscript is the
bosonic rank: `C_1_structure.json` for C(2), `C_2_structure.json` for C(3),
and `C_3_structure.json` for C(4).

## Top-level structure

Schema 1 retains the v5.0 B(m,n) fields and adds the required top-level
`central_elements` field:

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

Each field is specified below. Lists of generators and structure constants
must be fully populated for a concrete rank; `{}` and `[]` above only show
the top-level shape.

## `algebra`

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
    "odd": 4,
    "even_formula": "2n^2 + n + 1",
    "odd_formula": "4n",
    "total_formula": "2n^2 + 5n + 1"
  }
}
```

For general rank, set `cartan_type` to `C(n+1)` and `osp` to
`osp(2|2n)`. Numeric dimensions must be evaluated at that rank:
even $=2n^2+n+1$, odd $=4n$, total $=2n^2+5n+1$. The formulas are included
alongside numeric values so the rank-dependent convention is explicit.

## `oscillator_generators`

There are exactly two generator groups: one standard fermion pair and `n`
bosonic pairs. Do not include B(m,n)'s supplementary fermion.

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^-"
  },
  "bosons": {
    "n": 1,
    "count": 2,
    "labels": ["b_1_p", "b_1_m"],
    "parity": 0,
    "description": "Bosonic oscillator pairs b_k^+, b_k^- for k=1,...,n"
  }
}
```

The bosonic `labels` array contains `b_1_p`, `b_1_m`, ..., `b_n_p`,
`b_n_m`, with `count` equal to `2n`.

## `oscillator_relations`

The undeformed oscillator algebra uses the standard CAR and CCR. Mixed
fermion-boson brackets vanish in Schema 1.

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for a_1^-, a_1^+",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
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
    "fermion_boson": "[a_1^±, b_j^±] = 0 for all j"
  }
}
```

## `central_elements`

This is a required top-level field. `$K$` is the even central identity (the
scalar 1), and `kappa` is the odd, nilpotent formal extension symbol. Neither
is an independent generator in the `basis` lists.

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relation": "kappa^2 = 0",
    "central": true,
    "description": "Odd formal symbol for the nilpotent extension"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "K = 1",
    "central": true,
    "description": "Even central identity; identified with the scalar 1"
  }
}
```

## `basis`

Use the generator labels defined in `handover/notation.md`. The even list
contains `H_1` through `H_{n+1}`, `E_2del{k}_p/m` for each `k`, and all four
`E_del{i}_del{j}_{pp,pm,mp,mm}` labels for each `i<j`. The odd list contains
all four `E_eps1_del{k}_{pp,pm,mp,mm}` labels for each `k`. The cardinalities
must be `2n^2+n+1` and `4n`.

Use the triangular PBW order: negative root generators, Cartan generators,
then positive root generators. Within each group use the ordering specified
in `handover/notation.md`. Exclude `K` and `kappa` from both basis lists.

For example, the C(2) lists are:

```json
{
  "even": ["E_2del1_m", "H_1", "H_2", "E_2del1_p"],
  "odd": [
    "E_eps1_del1_mp",
    "E_eps1_del1_mm",
    "E_eps1_del1_pm",
    "E_eps1_del1_pp"
  ],
  "ordering_convention": "PBW: negative roots < Cartan < positive roots; see handover/notation.md"
}
```

The even list is the even-parity subsequence of the full PBW order; negative
odd generators precede it and positive odd generators follow it.

## `parity`

Map every label in `basis.even` to `0` and every label in `basis.odd` to `1`.
Do not include `K` or `kappa` in this map; their parities are specified in
`central_elements`. For example, in C(2):

```json
{
  "E_2del1_m": 0,
  "H_1": 0,
  "H_2": 0,
  "E_2del1_p": 0,
  "E_eps1_del1_mp": 1,
  "E_eps1_del1_mm": 1,
  "E_eps1_del1_pm": 1,
  "E_eps1_del1_pp": 1
}
```

## `generator_realization`

Store each basis generator as a list of oscillator words with rational
coefficients, its readable oscillator expression, and its parity. Every
basis label must have exactly one realization entry. Oscillator words use
`a_1_p`, `a_1_m`, `b_k_p`, and `b_k_m`; an empty word denotes the scalar 1.
For example:

```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_1^+ b_1^- - 1/2",
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

For each rank, populate all Cartan, even-root, and odd-root realizations.
Use the C(n+1) formulas in `docs/math/Cn1_definition.md`, with a single,
consistent normalization for root generators and structure constants.
The generator in `src/C_generators.py` follows the document's all-root
normalization `E_±2δ_k=(b_k^±)^2`. The separate simple-generator display gives
half of this for the terminal simple root; when using that alternative
normalization, rescale the corresponding structure constants consistently.

Generate the rank-1, rank-2, and rank-3 documents with:

```sh
python3 src/C_generators.py
```

## `structure_constants`

Represent each nonzero undeformed graded bracket as an entry of an array:

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

For each rank, include the complete set of nonzero brackets computed from
the oscillator relations and realizations. A bracket's result is expressed
as a basis generator and rational coefficient; omit zero brackets. Encode
input pairs in full PBW order (`X` no later than `Y`), relying on graded
skew-symmetry rather than storing the reversed pair. Store one row per
nonzero output term, so a bracket that is a linear combination has multiple
rows with the same `X` and `Y` but distinct `Z` labels.

## `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "docs/math/Cn1_definition.md",
    "docs/math/B0n_schema_v5.md"
  ]
}
```

## Compatibility with B(m,n)

The C(n+1) documents retain `schema_version` 5.0 and the B-family field
names for `algebra`, `oscillator_relations`, `basis`, `parity`,
`generator_realization`, `structure_constants`, and `metadata`. C-family
documents are separate files and identify themselves with `algebra.family:
"C"` and `algebra.m: 1`; B-family values and files remain unchanged.
Consumers must branch on `algebra.family` and must accept the additional
top-level `central_elements` field. The oscillator groups, root labels,
parity map, PBW ordering, and dimension values are family-specific and must
not be assumed identical to B(m,n).
