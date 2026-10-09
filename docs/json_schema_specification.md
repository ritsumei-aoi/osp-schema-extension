# C(n+1) v5.0 JSON Schema Specification

This document specifies Schema 1 (algebra structure) for
$C(n+1)=\mathfrak{osp}(2|2n)$, extending the existing B(m,n) v5.0 schema.
The bosonic rank is `n`, so C(2), C(3), and C(4) correspond to `n=1`, `n=2`,
and `n=3`, respectively. Generator labels and PBW ordering follow the approved
conventions in `handover/notation.md`.

## File naming

Name each structure file `C_{n}_structure.json`, where `n` is the bosonic
rank: `C_1_structure.json` for C(2), `C_2_structure.json` for C(3), and
`C_3_structure.json` for C(4).

## Top-level structure

Each Schema 1 C(n+1) document uses schema version `"5.0"` and these keys:

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

`central_elements` is a C(n+1) top-level extension. The remaining top-level
fields retain their B(m,n) v5.0 names and general meanings.

## `algebra`

Set `family` to `"C"`, `m` to `1`, and `n` to the positive integer bosonic
rank. `cartan_type` is `"C(n+1)"`. `alternative_notation.osp` identifies the
rank-specific algebra, and `alternative_notation.dimension_formula` is
`"osp(2m|2n)"`. Store the evaluated dimensions for the file's `n` and include
the dimension formulas:

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
    "odd": 8,
    "formulas": {
      "even": "2n^2+n+1",
      "odd": "4n",
      "total": "2n^2+5n+1"
    }
  }
}
```

The total dimension is the sum of the even and odd dimensions. For ranks
`n=1,2,3`, the `(even, odd, total)` values are `(4,4,8)`, `(11,8,19)`, and
`(22,12,34)`.

## `oscillator_generators`

There is no supplementary fermion. Use exactly the `fermions` and `bosons`
groups. Fermion labels are the ordered pair `a_1_p`, `a_1_m`; boson labels
are ordered by increasing index, with `p` before `m`.

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^-."
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± for k=1,...,n."
  }
}
```

For general `n`, the boson `count` is `2n` and the labels are
`b_1_p, b_1_m, ..., b_n_p, b_n_m`.

## `oscillator_relations`

The oscillator algebra is the undeformed algebra. Fermions satisfy CAR,
bosons satisfy CCR, and fermions commute with bosons:

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermionic pair.",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators.",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i,j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0 for all i."
  }
}
```

## `central_elements`

This C(n+1)-specific top-level field records the extension symbols. These are
not basis generators and are not included in the parity map or PBW ordering.

```json
{
  "kappa": {
    "label": "κ",
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "description": "Odd central symbol for the inhomogeneous extension."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "central": true,
    "identification": "1",
    "independent_basis_element": false,
    "description": "Even central identity, identified with the scalar 1."
  }
}
```

## `basis`

The finite-dimensional Lie-superalgebra basis contains all Cartan elements
and all root generators, but excludes `K` and `κ`. For every positive integer
`n`:

- `even` begins with `H_1,...,H_{n+1}`. Append `E_2del{k}_p` for increasing
  `k`; then, for each lexicographically ordered pair `i<j`, append
  `E_del{i}_del{j}_pp` and `E_del{i}_del{j}_pm`. Next append
  `E_2del{k}_m` for increasing `k`; finally, for each pair `i<j` in
  lexicographic order, append `E_del{i}_del{j}_mp` and
  `E_del{i}_del{j}_mm`.
- `odd` is ordered by increasing `k`; for each `k`, append
  `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`, and
  `E_eps1_del{k}_mm`.

The ordering of root signs in these lists is defined in
`handover/notation.md`. The PBW order places the complete odd list before the
complete even list:

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp", "E_del1_del2_pm",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mp", "E_del1_del2_mm"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm",
    "E_eps1_del2_pp", "E_eps1_del2_pm",
    "E_eps1_del2_mp", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: [odd in listed order] < [even in listed order]; K and κ are excluded."
}
```

The example lists are for `n=2`. In general, their lengths are
`even = 2n^2+n+1` and `odd = 4n`.

## `parity`

Provide an explicit JSON object mapping every basis-generator label to its
parity: all `H_*`, `E_2del*_*`, and `E_del*_*_*` labels map to `0`; all
`E_eps1_del*_*` labels map to `1`. Include every label appearing in `basis`
exactly once. Do not include `K` or `κ`.

## `generator_realization`

Each basis generator has an entry in `realizations`. The `standard_form` is
a list of oscillator-word terms, each with an array `words` and a rational
string `coeff`. The `frappat_form` is its readable oscillator expression.
Each entry also gives the generator `parity`. The oscillator word ordering is
`a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`.

Cartan realizations are:

$$
H_1=a_1^+a_1^-+b_1^+b_1^-,
\quad
H_k=b_{k-1}^+b_{k-1}^- - b_k^+b_k^- \ (2\leq k\leq n),
\quad
H_{n+1}=-b_n^+b_n^- - \tfrac12.
$$

The root-generator realizations are:

| Label pattern | Oscillator expression |
|---|---|
| `E_2del{k}_p` | $(b_k^+)^2$ |
| `E_2del{k}_m` | $(b_k^-)^2$ |
| `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ |
| `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ |
| `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ |
| `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ |
| `E_eps1_del{k}_pp` | $a_1^+b_k^+$ |
| `E_eps1_del{k}_pm` | $a_1^+b_k^-$ |
| `E_eps1_del{k}_mp` | $a_1^-b_k^+$ |
| `E_eps1_del{k}_mm` | $a_1^-b_k^-$ |

Use coefficient `1` for both `E_2del{k}_p` and `E_2del{k}_m`, including the
terminal index `k=n`; this is the approved all-root normalization. For
example, an odd generator entry has this shape:

```json
{
  "standard_form": [
    {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
  ],
  "frappat_form": "a_1^+ b_1^+",
  "parity": 1
}
```

Represent a constant term with an empty `words` array. For instance, the
`H_{n+1}` realization contains `{"words": [], "coeff": "-1/2"}`.

The enclosing field has this shape:

```json
{
  "description": "Standard oscillator form using the documented word ordering.",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "<every basis label>": {
      "standard_form": [],
      "frappat_form": "<oscillator expression>",
      "parity": 0
    }
  }
}
```

## `structure_constants`

Store every nonzero graded bracket of basis generators as a list entry.
Compute brackets from the oscillator realizations using the stated CAR, CCR,
and mixed relations. Coefficients are strings; `sign_rule` is `"graded"`.
Keep the B(m,n) v5.0 record format:

```json
[
  {
    "X": "<basis label>",
    "Y": "<basis label>",
    "Z": "<basis label>",
    "coeff": "<rational coefficient>",
    "sign_rule": "graded"
  }
]
```

The list for a given rank must contain the complete set of nonzero brackets
for that rank, not only simple-root brackets.

## `metadata`

Retain the B(m,n) v5.0 metadata fields. Use a C-specific generator name and
the date the structure constants were generated:

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)",
    "docs/math/Cn1_definition.md"
  ]
}
```

## Compatibility with B(m,n)

Existing B(m,n) Schema 1 files remain unchanged: retain schema version
`"5.0"`, their current field names and meanings, parity encoding, generator
realization format, and structure-constant record shape. The C(n+1) extension
uses those shared conventions, adds the top-level `central_elements` field,
and defines its own `family`, fermion/boson groups, basis, and realizations.
Consumers of B(m,n) data need not change; consumers that support C(n+1) must
read the additional field and the C-specific generator groups.

## Schema 3: Evaluated deformation

Schema 3 files are named `C_{n}_evaluated.json`. They retain the complete
Schema 1 data, including its undeformed `structure_constants`, `basis`, and
`parity`, and add an `inhomogeneous_deformation` object. This separates the
ordinary bracket from its evaluated first-order correction:

```json
{
  "inhomogeneous_deformation": {
    "output_space": "Schema 1 basis plus central identity K.",
    "gb_matrix": {},
    "deformed_oscillator_relations": {},
    "evaluation_profile": {
      "name": "all_positive",
      "parameter_values": {
        "gb_a1p_b1p": 1
      }
    },
    "evaluated_gamma_coefficients": [
      {
        "X": "E_eps1_del1_pp",
        "Y": "H_1",
        "Z": "K",
        "coeff": "1",
        "sign_rule": "graded"
      }
    ]
  }
}
```

For this C(n+1) evaluated profile, set every entry of the `2 x 2n`
`gb_matrix` to the integer `1`; list every named parameter in
`evaluation_profile.parameter_values`. Substitute exactly into each Schema 2
gamma coefficient, combine records with identical `(X,Y,Z)` labels, and omit
zero results. Evaluated `coeff` values are exact rational strings, never
floating-point numbers. The `Z` label `K` remains valid for the central
identity output. The resulting deformed bracket is interpreted as
`[X,Y] = [X,Y]_0 + κ γ(X,Y)`, where `[X,Y]_0` is stored in Schema 1
`structure_constants` and `γ` is stored in
`evaluated_gamma_coefficients`.

## Schema 4: Coboundary structure

Schema 4 files are named `C_{n}_coboundary.json`. They retain the complete
Schema 1 data and add a `coboundary` object containing the most general
parity-reversing linear map on the basis, its coboundary, and the central
components of the evaluated Schema 3 target that cannot be represented by
`δf` for `f: g -> g`.

The map has one independent symbolic coefficient for every input/output
generator pair of opposite parity and zero coefficients for same-parity
pairs. Its normalization uses no separate global multiplier. Store map terms
as `{input, output, parameter}` entries, with
`parameter = "phi_<output>_from_<input>"`. For the supported ranks, the map
has 32, 176, and 528 independent coefficients for `n=1,2,3`.

Compute coefficients from the exact formula
`(δf)(X,Y) = (-1)^p(X)[X,f(Y)] - (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])`.
The `delta_f_coefficients` list uses the standard `{X,Y,Z,coeff,sign_rule}`
record shape. `coeff` is an exact symbolic linear polynomial in the `phi`
parameters, and every `Z` is a Schema 1 basis generator. The Schema 4
`comparison` object references the corresponding Schema 3 file and preserves
its `Z: "K"` gamma records in `unmatched_central_components`; these central
identity outputs are not members of the Schema 1 basis and cannot occur in
`δf` for this map.
