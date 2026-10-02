# C(n+1) Schema 1 Specification

This document specifies the standalone Schema 1 algebra-structure data for
$C(n+1)=\mathfrak{osp}(2|2n)$. It follows the four-layer file architecture in
[`math/B0n_schema_v5.md`](math/B0n_schema_v5.md), extending its algebra
structure layer to the standard fermionic pair used by C(n+1).

## File names and supported ranks

Use `C_{n}_structure.json`, where `n` is the bosonic rank:

| Algebra | `n` | File |
|---|---:|---|
| C(2) = osp(2\|2) | 1 | `C_1_structure.json` |
| C(3) = osp(2\|4) | 2 | `C_2_structure.json` |
| C(4) = osp(2\|6) | 3 | `C_3_structure.json` |

The same field definitions apply for every positive integer `n`.

## Top-level structure

A Schema 1 file contains:

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

### `schema_version`

The schema version is the string `"5.0"`.

### `algebra`

The family is C, with `m` fixed at 1. The dimension formulas are part of the
schema contract:

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

Substitute the rank-specific cartan type and `osp(2|2n)` notation. Dimensions
for ranks 1, 2, and 3 are respectively `4|4` (total 8), `11|8` (total 19),
and `22|12` (total 34).

### `oscillator_generators`

There are exactly two oscillator families: one fermionic pair and `n`
bosonic pairs. No supplementary fermion is present.

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
    "description": "Bosonic oscillators b_i^+, b_i^- for i=1,...,n"
  }
}
```

For rank `n`, enumerate bosons in increasing index, with `p` before `m`.
The suffixes `_p` and `_m` denote plus and minus.

### `oscillator_relations`

The undeformed canonical relations are:

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relation for one standard fermion pair",
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
    "description": "Bosons commute with fermions in the undeformed oscillator algebra",
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

The deformation layer may replace the undeformed mixed relations with its
specified inhomogeneous exchange relations; it does not change this Schema 1
definition of the undeformed algebra.

### `central_elements`

This is a required top-level key. `kappa` is the odd nilpotent deformation
symbol. `K` is the even central identity, identified with scalar 1 and not an
independent basis element.

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
    "identity": true,
    "relation": "K = 1",
    "included_in_basis": false
  }
}
```

Neither central symbol is included in the finite-dimensional basis arrays for
$\mathfrak g=C(n+1)$. `κ` can be used in the extended/deformed data; `K` is
recorded for completeness only.

### `basis`

The basis separates homogeneous elements into `even` and `odd` arrays. Use the
odd-first/even-second PBW convention documented in
[`../handover/notation.md`](../handover/notation.md), with deterministic order
within each array. Cartan generators precede even root generators; doubled
roots precede paired-index roots. Root suffix order is `pp`, `pm`, `mp`, `mm`.

For `C_1_structure.json`, the complete basis is:

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": [
    "E_eps1_del1_pp",
    "E_eps1_del1_pm",
    "E_eps1_del1_mp",
    "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: [odd generators] < [even generators]; K=1 and κ are excluded from the C(n+1) basis"
}
```

For general `n`, include:

- Even: `H_1` through `H_{n+1}`; `E_2del{i}_p/m` for each `1≤i≤n`; and
  `E_del{i}_del{j}_pp/pm/mp/mm` for every `1≤i<j≤n`.
- Odd: `E_eps1_del{i}_pp/pm/mp/mm` for every `1≤i≤n`.

The counts are `n+1 + 2n^2` even and `4n` odd generators.

### `parity`

This object maps every basis label to its integer parity, with `0` even and
`1` odd. All labels in `basis.even` map to 0; all labels in `basis.odd` map
to 1. It contains no independent entries for `K` or `κ`.

### `generator_realization`

This object records a canonical oscillator ordering and one realization for
each basis generator. Each realization has `standard_form` (a list of
oscillator words with rational-string coefficients), `frappat_form`, and
`parity`. For example, the Cartan and odd-root entries are:

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
    "E_eps1_del1_pp": {
      "standard_form": [{"words": ["a_1_p", "b_1_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    }
  }
}
```

For general `n`, use the Cartan realization
$H_1=a_1^+a_1^-+b_1^+b_1^-$,
$H_k=b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ for $2≤k≤n$, and
$H_{n+1}=-b_n^+b_n^- - \tfrac12$. The even-root realizations are
$E_{\pm2\delta_i}=(b_i^\pm)^2$ and
$E_{\pm\delta_i\pm\delta_j}=b_i^\pm b_j^\pm$ (with the signs encoded by
the suffixes). The odd-root realizations are
$E_{\varepsilon\pm\delta_i}=a_1^+b_i^\pm$ and
$E_{-\varepsilon\pm\delta_i}=a_1^-b_i^\pm$.

### `structure_constants`

This array contains the nonzero undeformed graded brackets between basis
generators. Each entry has the following shape:

```json
{
  "X": "H_1",
  "Y": "E_eps1_del1_pp",
  "Z": "E_eps1_del1_pp",
  "coeff": "1",
  "sign_rule": "graded"
}
```

`X`, `Y`, and `Z` are basis labels, and `coeff` is an exact rational number
stored as a string. Store a bracket's result as a coefficient and basis label;
omit zero brackets. Store each nonzero pair once in basis order; the reversed
bracket is determined by graded antisymmetry. The brackets are computed from
the undeformed oscillator relations and the graded commutator. Deformation
cocycle terms belong to Schema 2, not this array.

### `metadata`

Metadata records provenance and generation:

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

## Compatibility with B(m,n) Schema 1

Schema 1 retains version `"5.0"` and the shared keys `algebra`,
`oscillator_generators`, `oscillator_relations`, `basis`, `parity`,
`generator_realization`, `structure_constants`, and `metadata`. Existing
B(m,n) files remain unchanged and readable under their existing
family-specific definitions.

C(n+1) specializes to `family: "C"` and `m: 1`; replaces the supplementary
fermion with the standard pair; uses the `4n` odd-root generators; and adds
the required top-level `central_elements`. Consumers must branch on
`algebra.family` and must not assume B-family odd basis or fermion fields
when reading C-family files. File names are family-specific (`B_...` versus
`C_{n}_structure.json`), so adding C files does not overwrite B(m,n) data.

## Schema 2: Inhomogeneous deformation

Schema 2 files are named `C_{n}_gamma.json` and refer to the corresponding
Schema 1 file through `source_schema`. They contain the algebra descriptor,
the `gb_matrix`, `inhomogeneous_deformation`, and metadata.

`gb_matrix` has two rows (`a_1_p`, `a_1_m`) and `2n` columns (the bosonic
oscillator labels in Schema 1 order). Each cell has one distinct parity-1
parameter; labels use `gb_a1_{p|m}_b{i}_{p|m}`, such as
`gb_a1_p_b1_m`. Its `shape` is `[2, 2n]`.

`inhomogeneous_deformation.relations` records each literal relation
`[b_i^s, a_1^σ] = -gb_a1_σ_bi_s κ`. Each nonzero entry in
`gamma_coefficients` has `X`, `Y`, `Z`, and a list of exact rational
coefficients indexed by parameter. The pair `X,Y` is stored once in basis
order. `Z` is a Schema 1 basis label, or `K` when an identity term is
required to express the oscillator result; `K` is the identity recorded in
Schema 1 `central_elements`, not a new basis generator. Reversed pairs follow
the documented graded antisymmetry rule. These fields encode formal
first-order parameter terms and omit the common factor `κ`.

**Parity caveat:** `C_inhomogeneous_definition.md` states that both `gb` and
`κ` are odd but also assigns their product to the mixed bracket
`[b_{\bar 0},a_{\bar 1}]`, which is odd. The stated parities make that product
even. The generator preserves the literal exchange-relation coefficients as
formal labels and does not infer coefficient sign changes from their parity.
This makes the generated coefficients explicit, but does not resolve the
source definition's parity inconsistency.
