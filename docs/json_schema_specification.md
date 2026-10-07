# C(n+1) v5.0 JSON Schema Specification

This document specifies Schema 1 (algebra structure) for
$C(n+1)=\mathfrak{osp}(2|2n)$. It extends the v5.0 schema conventions used
for $B(0,n)$ while defining the C-specific algebra, oscillators, basis,
realizations, and central elements. Here $n\geq1$ is the bosonic rank.

## Schema 1: Algebra Structure

### Top-level keys

Every structure file has the following keys:

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

`central_elements` is a top-level key. The other fields retain the v5.0
structure and meanings described below.

### `schema_version`

```json
{"schema_version": "5.0"}
```

### `algebra`

The value of `n` is the positive integer rank for the particular structure
file. Dimension formulas are recorded as strings and instantiated dimensions
as integers:

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
    "total": "2n^2 + 5n + 1",
    "even": "2n^2 + n + 1",
    "odd": "4n"
  }
}
```

In general, `cartan_type` is `C(n+1)` and `alternative_notation.osp` is
`osp(2|2n)`. The dimensions are
\[
\dim \mathfrak g_{\bar 0}=2n^2+n+1,\qquad
\dim \mathfrak g_{\bar 1}=4n,\qquad
\dim\mathfrak g=2n^2+5n+1.
\]

| $n$ | Algebra | Even | Odd | Total |
|---:|---|---:|---:|---:|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

### `oscillator_generators`

There is one standard fermionic pair and `n` bosonic pairs. The `fermions`
and `bosons` keys replace B(0,n)'s supplementary-fermion key:

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
    "description": "Bosonic oscillators b_i^± for i=1,...,n"
  }
}
```

The boson count is `2n`; labels are emitted in increasing index order, with
`p` then `m` for each index. Suffixes `p` and `m` denote `+` and `-`,
respectively.

### `oscillator_relations`

Use canonical anticommutation relations (CAR) for the fermions, canonical
commutation relations (CCR) for the bosons, and ordinary commutation between
fermions and bosons:

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0 for all i and fermion signs"
  }
}
```

No supplementary fermion or supplementary-fermion relation is present.

### `central_elements`

The extension symbol and scalar identity are described separately from the
Lie-superalgebra basis:

```json
{
  "kappa": {
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "description": "Odd central symbol for the inhomogeneous extension"
  },
  "K": {
    "parity": 0,
    "central": true,
    "identity": true,
    "description": "Even scalar identity, K=1"
  }
}
```

The parity of `kappa` is 1 and the parity of `K` is 0. `kappa` records the
odd central symbol used by the inhomogeneous extension; it is not one of the
generators in the C(n+1) Lie-superalgebra basis. `K` is the scalar identity,
not an independent generator, and is excluded from the basis and PBW
ordering.

### `basis`

The basis consists of all Cartan and root generators, excluding `kappa` and
the identity `K`. Use the finalized parity-block ordering from
`handover/notation.md`:

1. **Odd block:** for `i=1,...,n`, list `E_eps1_del{i}_pp`,
   `E_eps1_del{i}_pm`; then for `i=1,...,n`, list
   `E_eps1_del{i}_mp`, `E_eps1_del{i}_mm`.
2. **Even block:** list `H_1,...,H_{n+1}`; positive even roots
   `E_2del{i}_p`, `E_del{i}_del{j}_pp`, `E_del{i}_del{j}_pm`; then negative
   even roots `E_2del{i}_m`, `E_del{i}_del{j}_mm`,
   `E_del{i}_del{j}_mp`.

Within each family indices increase; pair-root indices are lexicographic
with `1 <= i < j <= n`. The complete basis field has `even` and `odd` arrays,
plus an `ordering_convention` string. For example, for n=2:

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp", "E_del1_del2_pm",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del2_pp", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm",
    "E_eps1_del2_mp", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: [odd: epsilon-positive, epsilon-negative] < [even: Cartan, positive roots, negative roots]; K=1 is excluded"
}
```

The basis cardinalities are `2n^2+n+1` even generators and `4n` odd
generators.

### `parity`

`parity` is an object mapping every label in `basis.even` to `0` and every
label in `basis.odd` to `1`. It contains no entry for `kappa` or `K`.

For example, for n=2:

```json
{
  "H_1": 0, "H_2": 0, "H_3": 0,
  "E_2del1_p": 0, "E_2del2_p": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_pm": 0,
  "E_2del1_m": 0, "E_2del2_m": 0,
  "E_del1_del2_mm": 0, "E_del1_del2_mp": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del2_pp": 1, "E_eps1_del2_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1,
  "E_eps1_del2_mp": 1, "E_eps1_del2_mm": 1
}
```

### `generator_realization`

Each basis generator has a realization as a sum of oscillator words with
rational-string coefficients. Retain the v5.0 `standard_form`, `frappat_form`,
and `parity` entry structure. The oscillator ordering is
`a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`.

The Cartan realizations are
\[
\begin{aligned}
H_1 &= a_1^+a_1^-+b_1^+b_1^-,\\
H_k &= b_{k-1}^+b_{k-1}^- - b_k^+b_k^- &&(2\leq k\leq n),\\
H_{n+1} &= -b_n^+b_n^- - \tfrac12.
\end{aligned}
\]

Root realizations follow the labels and sign convention in
`handover/notation.md`, with the following required terminal-root
normalization:

| Root | Label | Oscillator realization |
|---|---|---|
| $2\delta_i$, $i<n$ | `E_2del{i}_p` | $(b_i^+)^2$ |
| $-2\delta_i$, $i<n$ | `E_2del{i}_m` | $(b_i^-)^2$ |
| $2\delta_n$ | `E_2del{n}_p` | $\tfrac12(b_n^+)^2$ |
| $-2\delta_n$ | `E_2del{n}_m` | $\tfrac12(b_n^-)^2$ |
| $\delta_i+\delta_j$ | `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ |
| $-(\delta_i+\delta_j)$ | `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ |
| $\delta_i-\delta_j$ | `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ |
| $-(\delta_i-\delta_j)$ | `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ |
| $\varepsilon+\delta_i$ | `E_eps1_del{i}_pp` | $a_1^+b_i^+$ |
| $\varepsilon-\delta_i$ | `E_eps1_del{i}_pm` | $a_1^+b_i^-$ |
| $-\varepsilon+\delta_i$ | `E_eps1_del{i}_mp` | $a_1^-b_i^+$ |
| $-\varepsilon-\delta_i$ | `E_eps1_del{i}_mm` | $a_1^-b_i^-$ |

For the terminal simple even root, the factor `1/2` is used for both root
vectors. With the stated CCR and Cartan realization it gives
\[
[E_{-2\delta_n},E_{2\delta_n}]
= \left[\tfrac12(b_n^-)^2,\tfrac12(b_n^+)^2\right]
= b_n^+b_n^-+\tfrac12
= -H_{n+1}.
\]
This terminal-root normalization takes precedence over the unscaled
all-root shorthand in the C(n+1) reference.

An individual realization entry has the v5.0 form, for example:

```json
{
  "standard_form": [
    {"words": ["a_1_p", "b_1_m"], "coeff": "1"}
  ],
  "frappat_form": "a_1^+ b_1^-",
  "parity": 1
}
```

The `realizations` object contains exactly one entry for each label in the
even and odd basis arrays.

### `structure_constants`

Store all non-zero graded brackets of basis generators for the selected rank
as a list. Retain the v5.0 entry shape:

```json
[
  {
    "X": "E_2del2_m",
    "Y": "E_2del2_p",
    "Z": "H_3",
    "coeff": "-1",
    "sign_rule": "graded"
  }
]
```

Each entry encodes $[X,Y\}= \mathrm{coeff}\,Z$. Coefficients are strings;
`sign_rule` is `graded`. Constants must be computed for the C(n+1)
realizations using the fermionic CAR and bosonic CCR above, including the
approved terminal-root normalization. Do not copy B(0,n) structure
constants without recomputing them for C(n+1).

### `metadata`

Retain the v5.0 metadata shape, using a C-specific generator identifier:

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "C(n+1) mathematical definition and oscillator realization"
  ]
}
```

## Compatibility with B(m,n) v5.0

The C(n+1) structure files retain the v5.0 top-level organization,
`schema_version`, basis/parity representation, generator-realization entry
shape, structure-constant entry shape, and metadata shape. The C-specific
changes are:

| Field | B(0,n) convention | C(n+1) convention |
|---|---|---|
| `algebra.family`, `algebra.m` | `"B"`, `0` | `"C"`, `1` |
| Dimensions | even $2n^2+n$, odd $2n$ | even $2n^2+n+1$, odd $4n$ |
| Fermions | Supplementary `a_0` | `fermions` pair `a_1_p`, `a_1_m` |
| Fermion relation | $a_0^2=\tfrac12$ | $\{a_1^-,a_1^+\}=1$ |
| `central_elements` | Not a top-level C field | Top-level object with `kappa`, `K` |
| Odd basis | `E_del{i}_p/m` | Four `E_eps1_del{i}_...` labels per i |
| Terminal even root | B-specific normalization | `E_±2del{n}` use coefficient `1/2` |

These changes do not alter the interpretation of existing B files.

## File naming

Use `C_{n}_structure.json`, where `n` is the bosonic rank:

| Algebra | File |
|---|---|
| C(2) = osp(2\|2), n=1 | `C_1_structure.json` |
| C(3) = osp(2\|4), n=2 | `C_2_structure.json` |
| C(4) = osp(2\|6), n=3 | `C_3_structure.json` |

## Schema 2: Inhomogeneous Deformation

Schema 2 files are named `C_{n}_gamma.json`. They use the Schema 1 algebra
identity and identify the source structure file:

```json
{
  "schema_version": "5.0",
  "algebra": {},
  "source_schema": "C_1_structure.json",
  "gb_matrix": {
    "rows": ["a_1_p", "a_1_m"],
    "columns": ["b_1_p", "b_1_m"],
    "entries": [
      [
        {"parameter": "gb_a1_p_b1_p", "parity": 0},
        {"parameter": "gb_a1_p_b1_m", "parity": 0}
      ],
      [
        {"parameter": "gb_a1_m_b1_p", "parity": 0},
        {"parameter": "gb_a1_m_b1_m", "parity": 0}
      ]
    ],
    "parameter_order": [
      "gb_a1_p_b1_p", "gb_a1_p_b1_m",
      "gb_a1_m_b1_p", "gb_a1_m_b1_m"
    ]
  },
  "inhomogeneous_deformation": {
    "central_symbol": "kappa",
    "central_parity": 1,
    "parameter_parity": 0,
    "sign_convention": "gram_entry",
    "exchange_relations": [],
    "coefficient_format": "Exact rational linear combinations of the even gb parameters",
    "gamma_structure": []
  },
  "metadata": {}
}
```

The `gb_matrix` has two rows in fermion order `a_1_p`, `a_1_m`; its columns
are ordered `b_1_p`, `b_1_m`, ..., `b_n_p`, `b_n_m`. `entries` is a 2-by-2n
array aligned with those labels. The parameters are even scalars; their
products with the odd central symbol `kappa` are odd. Each mixed relation is
stored in the approved Gram-entry convention
`[b_j^s, a_1^σ] = -gb_{a_1^σ,b_j^s} * kappa`.

Each nonzero `gamma_structure` record uses the Schema 1 bracket fields
`X`, `Y`, `Z`, `coeff`, and `sign_rule`. `coeff` is an exact symbolic linear
combination of `gb` parameters, with rational coefficients formatted as
`1/2*gb_name` and terms joined by ` + ` or ` - `. The deformation calculation
retains scalar identity components as `Z: "K"` even though `K` is excluded
from the Schema 1 Lie-superalgebra basis. These scalar terms are intentional;
triviality comparisons use the up-to-scalar convention in
`C_coboundary_definition.md`.

Files are `data/C_1_gamma.json`, `data/C_2_gamma.json`, and
`data/C_3_gamma.json` for bosonic ranks 1, 2, and 3.
