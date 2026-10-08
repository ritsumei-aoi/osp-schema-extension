# C(n+1) Schema 1 v5.0 Specification

This document defines the complete algebra-structure (Schema 1) record for
$C(n+1)=\mathfrak{osp}(2|2n)$, using the four-layer JSON architecture in
`docs/math/B0n_schema_v5.md`. The rank parameter `n` is the number of bosonic
oscillator pairs, so C(2), C(3), and C(4) use `C_1_structure.json`,
`C_2_structure.json`, and `C_3_structure.json`, respectively.

## Compatibility with the B(m,n) schema

The C schema retains the v5.0 top-level organization and the common meanings
of `schema_version`, `basis`, `parity`, `generator_realization`,
`structure_constants`, and `metadata`. It remains readable by consumers that
ignore unknown top-level keys and use the common field shapes. C-specific
consumers must account for the standard fermion pair, the additional
$\mathfrak{so}(2)$ Cartan generator, the four odd root generators per bosonic
index, and top-level `central_elements`; B-specific generator names and counts
are not interchangeable with C data. B files are unchanged.

## Schema 1 record

The top-level keys are:

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

Use the string `"5.0"`, as for the B(m,n) records.

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

Set `cartan_type` to `"C(n+1)"`, `osp` to `"osp(2|2n)"`, and the numeric
dimensions to $(2n^2+n+1)\mid 4n$ for the selected value of `n`.

| `n` | Algebra | Even | Odd | Total |
|---:|---|---:|---:|---:|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

### `oscillator_generators`

The C record has exactly the `fermions` and `bosons` groups; it does not have
B(0,n)'s `supplementary_fermion`.

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
    "description": "Bosonic oscillators b_i^+, b_i^- for i=1,...,n"
  }
}
```

For general rank, `bosons.count` is `2*n`; labels are ordered
`b_1_p`, `b_1_m`, ..., `b_n_p`, `b_n_m`. Fermion labels are always
`a_1_p`, `a_1_m`.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for a_1^+, a_1^-",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i_m, b_j_p] = δ_ij"
    }
  },
  "mixed_commutators": {
    "description": "Fermionic and bosonic oscillators commute",
    "relations": {
      "boson_fermion": "[b_i^±, a_1^±] = 0"
    }
  }
}
```

The mixed relation is ordinary commutation: the oscillator generators belong
to independent fermionic and bosonic sectors.

### `central_elements`

This is a C-specific top-level key. Record the deformation symbol and scalar
identity explicitly; neither is an independent generator in the Lie
superalgebra basis.

```json
{
  "kappa": {
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "kappa^2 = 0",
    "description": "Odd central symbol for the inhomogeneous extension"
  },
  "K": {
    "parity": 0,
    "central": true,
    "identity": true,
    "relation": "K = 1",
    "description": "Even central identity; identified with the scalar 1"
  }
}
```

`kappa` has parity 1, as required by the C(n+1) deformation convention, and
`K` has parity 0. Both labels are recorded for schema completeness but omitted
from `basis`, `parity`, and PBW generator ordering.

### `basis`

Use the generator names and PBW order finalized in `handover/notation.md`.
For rank `n`, `even` contains:

1. `H_1` through `H_{n+1}`;
2. `E_2del{i}_p` and `E_2del{i}_m` for every `i=1,...,n`;
3. `E_del{i}_del{j}_pp/pm/mp/mm` for every `i<j`.

`odd` contains `E_eps1_del{i}_pp/pm/mp/mm` for every `i=1,...,n`.
The `ordering_convention` string describes the selected order:

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": [
    "E_eps1_del1_pp",
    "E_eps1_del1_pm",
    "E_eps1_del1_mp",
    "E_eps1_del1_mm"
  ],
  "ordering_convention": "Cartan < positive even < positive odd < negative odd < negative even; indices and sign labels ordered as in handover/notation.md"
}
```

The shown lists are the complete basis lists for `n=1`; for other ranks,
populate them using the rules above. The even and odd list lengths must be
`2*n^2+n+1` and `4*n`. Exclude `kappa` and `K`.

### `parity`

This object has one entry for every basis generator: `0` for every `basis.even`
member and `1` for every `basis.odd` member. It has no entries for `kappa` or
`K`.

### `generator_realization`

Each basis generator maps to `standard_form`, a list of oscillator words and
rational coefficients; it also records `frappat_form` and its parity. Order
oscillator words using `a_1_p`, `a_1_m`, then `b_1_p`, `b_1_m`, ..., `b_n_p`,
`b_n_m`. Use the following realizations (the formulae specify the
normalization used in structure-constant generation):

$$
\begin{aligned}
H_1 &= a_1^+a_1^-+b_1^+b_1^-,\\
H_k &= b_{k-1}^+b_{k-1}^- - b_k^+b_k^- \quad (2\leq k\leq n),\\
H_{n+1} &= -b_n^+b_n^- - \tfrac12,\\
E_{2\delta_i} &= (b_i^+)^2,\qquad
E_{-2\delta_i}=(b_i^-)^2,\\
E_{\pm\delta_i\pm\delta_j} &= b_i^\pm b_j^\pm \quad (i<j),\\
E_{\varepsilon\pm\delta_i} &= a_1^+b_i^\pm,\qquad
E_{-\varepsilon\pm\delta_i}=a_1^-b_i^\pm.
\end{aligned}
$$

For `standard_form`, an empty `words` list denotes a scalar term. For example,
the C(2) `H_2` entry is represented by `b_1_p b_1_m` with coefficient `-1`
and the empty word with coefficient `-1/2`. The four odd labels use
`a_1_p b_i_p`, `a_1_p b_i_m`, `a_1_m b_i_p`, and `a_1_m b_i_m` respectively,
each with coefficient `"1"`.

The root-generator paragraph of `docs/math/Cn1_definition.md` fixes the
long-root normalization as $(b_i^\pm)^2$. Its simple-generator display also
shows $\tfrac12(b_n^\pm)^2$ for the terminal simple root; this schema uses the
all-root formula above uniformly and records that choice here so constants
are generated consistently.

### `structure_constants`

Store the nonzero standard (undeformed) graded brackets as objects in a JSON
array:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "2",
    "sign_rule": "graded"
  }
]
```

The example illustrates the entry shape; actual records must contain all
nonzero brackets for the selected rank, in the declared basis and realization.
Coefficients are strings of exact rational numbers. For homogeneous `X` and
`Y`, use $[X,Y\}=XY-(-1)^{p(X)p(Y)}YX$; omit zero brackets and duplicate
entries implied by graded skew-symmetry. Schema 2 deformation terms are not
stored in this field.

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "docs/math/Cn1_definition.md",
    "handover/notation.md"
  ]
}
```

Use the actual generation date and generator name when producing a data file.
The references identify the mathematical convention and local source of the
schema labels.

## File naming

Schema 1 files use `C_{n}_structure.json`, where `n` is the bosonic rank:

| Algebra | Filename |
|---|---|
| C(2) = osp(2\|2) | `C_1_structure.json` |
| C(3) = osp(2\|4) | `C_2_structure.json` |
| C(4) = osp(2\|6) | `C_3_structure.json` |

Other layers follow the same rank-based pattern, for example
`C_{n}_gamma.json`, `C_{n}_evaluated_<gb>.json`, and
`C_{n}_coboundary_<gb>.json`.

## Schema 2: Inhomogeneous deformation

Schema 2 files are named `C_{n}_gamma.json`. They preserve rank and dimension
metadata, identify the Schema 1 source file, record the central symbols, and
store the deformation in `inhomogeneous_deformation`.

### `gb_matrix`

The matrix has two fermion rows (`a_1_p`, `a_1_m`) and `2*n` boson columns
(`b_1_p`, `b_1_m`, ..., `b_n_p`, `b_n_m`). Store all `4*n` parameter records
with labels `gb_a1_{p|m}_b{i}_{p|m}`, the corresponding oscillator labels,
and the parity annotation specified in
`docs/math/C_inhomogeneous_definition.md`.

### `gamma_coefficients`

Store each nonzero ordered PBW pair/output triple once. Its `coefficients`
array lists exact rational coefficients of the formal `gb` parameters:

```json
{
  "X": "H_1",
  "Y": "E_eps1_del1_pp",
  "Z": "H_1",
  "coefficients": [
    {"parameter": "gb_a1_p_b1_p", "coeff": "1"}
  ]
}
```

`X` and `Y` use the C Schema 1 PBW order. `Z` is a Schema 1 basis label or
`K` when normal ordering produces the scalar identity; `kappa` itself is
factored outside the coefficient list. Omit zero terms. The associated
oscillator convention is the literal relation
`[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa`, expanded to first order using
`kappa^2 = 0`.

**Parity caveat in the supplied definition:** it assigns parity 1 to both
`gb` and `kappa`, while the commutator of an even boson with an odd fermion
has parity 1. Their product has parity 0, so the displayed oscillator
relation is not homogeneous under those assignments. The Schema 2 generator
retains the stated parities and records formal coefficients from the literal
relation; its closure check verifies expansion into the Schema 1 oscillator
basis (and scalar `K`), not that this parity inconsistency is resolved. A
mathematically homogeneous deformation requires reconciling the source
parity convention before interpreting the output as a Lie-superalgebra
deformation.
