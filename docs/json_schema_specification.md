# C(n+1) Schema 1 Specification

This document defines the v5.0 Schema 1 algebra-structure document for
\(C(n+1)=\mathfrak{osp}(2|2n)\). It extends the common four-layer structure
described in [the B(0,n) v5.0 specification](math/B0n_schema_v5.md) while
preserving its field names and structure wherever possible.

## File names and supported ranks

Use `C_{n}_structure.json`, where `n` is the bosonic rank and not the
integer in \(C(n+1)\): `C_1_structure.json` describes C(2),
`C_2_structure.json` describes C(3), and `C_3_structure.json` describes
C(4). The file contains one rank-specific, fully populated JSON object.

## Top-level fields

Every file contains the following keys:

| Key | Type | Meaning |
|---|---|---|
| `schema_version` | string | Schema revision; `"5.0"`. |
| `algebra` | object | Algebra family, rank, notation, and dimensions. |
| `oscillator_generators` | object | Standard fermionic pair and bosonic oscillators. |
| `oscillator_relations` | object | Undeformed CAR, CCR, and mixed relations. |
| `central_elements` | object | Formal extension symbol `kappa` and identity `K`. |
| `basis` | object | Ordered even and odd basis labels. |
| `parity` | object | Map from every basis label to parity 0 or 1. |
| `generator_realization` | object | Oscillator word realizations of basis generators. |
| `structure_constants` | array | Non-zero undeformed graded brackets. |
| `metadata` | object | Generator, date, and references. |

### `algebra`

Required fields:

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
    "formula": {
      "even": "2n^2 + n + 1",
      "odd": "4n",
      "total": "2n^2 + 5n + 1"
    }
  }
}
```

The rank-specific dimensions are `(even, odd, total) = (4,4,8)` for `n=1`,
`(11,8,19)` for `n=2`, and `(22,12,34)` for `n=3`. `m` is always 1.

### `oscillator_generators`

There are exactly two generator groups. The fermion object has `m: 1`,
labels `["a_1_p", "a_1_m"]`, parity 1, and a description identifying the
standard pair \(a_1^\pm\). The boson object has `n` equal to the algebra's
rank, `count: 2*n`, labels in `b_1_p, b_1_m, ..., b_n_p, b_n_m` order,
and a description identifying \(b_j^\pm\).

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
    "description": "Bosonic oscillators b_j^± with j=1,...,n"
  }
}
```

### `oscillator_relations`

The standard pair satisfies the CAR
\(\{a_1^-,a_1^+\}=1\), with both same-sign anticommutators zero. Bosons
satisfy \([b_i^-,b_j^+]=\delta_{ij}\) and same-type commutators zero.
Fermions commute with bosons in the undeformed oscillator algebra. The
inhomogeneous \(\kappa\)-terms are specified by Schema 2, not included in
these undeformed relations.

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for a_1^±",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for b_i^±",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^σ] = 0 for σ in {+, -}"
  }
}
```

### `central_elements`

This is a required top-level key. `kappa` is the formal odd central
extension symbol, with parity 1 and nilpotency `kappa^2 = 0`. `K` is the
even central identity, parity 0, identified with scalar 1. Neither is an
independent basis generator: exclude both from `basis` and `parity`.
`kappa` is recorded here to identify the extension used by deformation
data; the undeformed \(C(n+1)\) structure constants do not contain it.

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

### `basis` and `parity`

`basis.even` and `basis.odd` are ordered arrays of unique generator labels.
Their required labels and order are defined in
[`handover/notation.md`](../handover/notation.md): the even Cartan and
\(\mathfrak{sp}(2n)\) root vectors, and four odd root vectors
`E_eps1_del{k}_{pp,pm,mp,mm}` per `k`. `basis.ordering_convention` records
`κ < [odd] < [even]`; within each parity block use the order documented
there. The `parity` object maps every and only basis generator to `0`
(even) or `1` (odd).

The basis sizes are `2n^2+n+1` even and `4n` odd. `K` and `kappa` are not
included. The scalar identity is not part of the Lie-superalgebra basis.

### `generator_realization`

This object has a descriptive `description`, an `ordering` array listing
the oscillator labels in the convention used for canonical forms, and a
`realizations` object with exactly one entry per basis generator. Every
entry contains:

- `standard_form`: an array of terms, each with `words` (ordered oscillator
  labels; an empty array denotes the scalar term) and `coeff` (a rational
  coefficient encoded as a string);
- `frappat_form`: readable mathematical notation for the same expression;
- `parity`: 0 or 1, matching the top-level `parity` map.

Include a `note` only when needed to explain a convention or normalization.
Generator realizations must use `a_1_p`/`a_1_m` and the boson labels above;
there is no supplementary fermion. For example, a term in the
`E_eps1_del1_pp` realization has words `["a_1_p", "b_1_p"]`, coefficient
`"1"`.

### `structure_constants`

This is an array containing each non-zero undeformed graded bracket once.
Each record has string fields `X`, `Y`, and `Z` and a rational-string
`coeff`, representing \([X,Y\}= \text{coeff}\,Z\), plus
`"sign_rule": "graded"`. Use the superbracket; zero brackets are omitted.
The data must be consistent with the CAR/CCR, basis, parity, and generator
realizations. Deformation terms belong to Schema 2.

### `metadata`

Include `generated_by` (string), `generation_date` (`YYYY-MM-DD` string),
and `references` (array of citation strings). Cite the mathematical
definitions used to produce the constants.

## Compatibility with B(m,n) v5.0

The shared fields and their basic roles (`schema_version`, `algebra`,
`oscillator_generators`, `oscillator_relations`, `basis`, `parity`,
`generator_realization`, `structure_constants`, and `metadata`) retain
their names and general data shapes. A B(m,n) reader can therefore reuse
the common parsing logic, but must branch on `algebra.family` and cannot
assume B-specific labels or generator content.

C(n+1) intentionally changes B-specific values and adds required
structure: `family` is `"C"`, `m` is 1, the dimensions use the C formulas,
`supplementary_fermion` is replaced by the `fermions` pair, the
supplementary relation is replaced by CAR, the basis/parity and
realizations use the C root labels, and the top-level `central_elements`
key is added. In particular, consumers must not infer that the
supplementary B(0,n) oscillator `a_0` or B odd roots `E_del{k}_p/m` exist
in a C document.

## Schema 2: Inhomogeneous deformation

Schema 2 files are named `C_{n}_gamma.json` and use the same `schema_version`
and rank-identifying `algebra` fields as Schema 1. The top-level
`gb_matrix` and `inhomogeneous_deformation` fields describe the formal
deformation; `metadata` identifies the generator and references.

`gb_matrix` contains a `[2, 2*n]` shape, row labels `["a_1_p", "a_1_m"]`,
the ordered bosonic column labels, a matching 2-by-2n `entries` matrix,
and parameter records with `name`, `fermion`, `boson`, and `parity`.
Parameter names are `gb_{fermion-label}_{boson-label}`; all 4n parameters
are marked parity 0.

`inhomogeneous_deformation` contains the exchange-relation string, the
central nilpotent `kappa` description, `gamma_coefficients`, and a
`consistency` report. Each gamma record has `X`, `Y`, `Z`, `gb_parameter`,
a rational-string `coeff`, and `"sign_rule": "graded"`, representing the
term \(\kappa\,\mathrm{gb}_{parameter}\,\mathrm{coeff}\,Z\). `X` and `Y`
are canonical Schema 1 basis labels. `Z` is a Schema 1 basis label, or
`K` when the oscillator calculation produces the scalar identity. Such a
`K` term is explicitly a central contribution and is not an addition to the
Schema 1 basis. The `consistency` object reports closure both in the
Schema 1 generators alone and with the declared central identity, whether
all outputs are representable in that extended set, whether the stated
oscillator relations are associative, and any oscillator terms that fail
to decompose.

**Parity decision:** the earlier source note assigned parity 1 to `gb`,
but the exchange relation \([b,a]=-gb\,\kappa\) requires parity 0 for `gb`
because \(b\) is even, \(a\) and \(\kappa\) are odd. With this choice the
relation is homogeneous and preserves the CAR for independent parameters.
`C_inhomogeneous_definition.md` and the generated Schema 2 files use this
corrected parity. Gamma outputs close in the Schema 1 generator labels plus
the declared central identity `K`; terms with `K` are reported explicitly
because `K` is excluded from the basis arrays.

## Schema 3: Evaluated structure

Evaluated files are named `C_{n}_evaluated.json`. The generator uses one
representative profile, `all_positive`, assigning every parameter in the
Schema 2 gb matrix the integer value `+1`. The top-level object contains
`schema_version`, the Schema 1 `algebra`, `basis`, and `parity`, an
`evaluation` object with the profile and complete `gb_assignment`, an
array of evaluated `structure_constants`, the evaluated
`inhomogeneous_deformation`, and `metadata`.

Each evaluated structure-constant record identifies `X`, `Y`, and `Z`,
and supplies exact rational strings `undeformed_coeff` and `kappa_coeff`
for the corresponding parts of
\([X,Y]_0+\kappa[X,Y]_{\gamma,\mathrm{evaluated}}\), along with
`"sign_rule": "graded"`. The inhomogeneous object contains the `kappa`
description, the non-zero evaluated gamma coefficients, symbolic and
evaluated term counts, and the inherited consistency report. The
evaluation is reproducible from the matching Schema 1 and Schema 2 files.
