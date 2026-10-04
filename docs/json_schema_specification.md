# C(n+1) v5.0 JSON Schema Specification

This document defines Schema 1 for $C(n+1)=\mathfrak{osp}(2|2n)$, extending
the v5.0 Schema 1 conventions documented in `docs/math/B0n_schema_v5.md`.
It specifies one concrete file per positive bosonic rank $n$; counts and
labels below are generated for that $n$.

## File names and schema compatibility

Use `C_{n}_structure.json`, where $n$ is the bosonic rank. Thus C(2) is
`C_1_structure.json`, C(3) is `C_2_structure.json`, and C(4) is
`C_3_structure.json`.

The v5.0 `schema_version`, `algebra`, `oscillator_generators`,
`oscillator_relations`, `basis`, `parity`, `generator_realization`,
`structure_constants`, and `metadata` fields retain their B(m,n) roles and
value formats. C(n+1) adds the top-level `central_elements` field. B(m,n)
files remain unchanged: the supplementary-fermion field and B(0,n) basis
must not be reused in a C(n+1) file.

## Top-level object

Every file has these top-level keys:

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

`structure_constants` is a populated array in each generated file; the empty
array above only indicates its JSON type and is not a valid completed dataset.

## `algebra`

For bosonic rank $n$, use:

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
    "odd": 8
  }
}
```

Set the example's `n`, Cartan type, osp notation, and dimensions for each
file. The dimensions are
$\dim\mathfrak g_{\bar 0}=2n^2+n+1$,
$\dim\mathfrak g_{\bar 1}=4n$, and
$\dim\mathfrak g=2n^2+5n+1$.

| $n$ | Cartan type | osp notation | even | odd | total |
|---:|---|---|---:|---:|---:|
| 1 | C(2) | osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) | osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) | osp(2\|6) | 22 | 12 | 34 |

## `oscillator_generators`

There are exactly two keys: `fermions` and `bosons`. Do not include
`supplementary_fermion`.

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
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^+, b_k^- for k=1,...,n"
  }
}
```

For general $n$, the fermion labels remain fixed and the boson labels are
`b_1_p`, `b_1_m`, ..., `b_n_p`, `b_n_m`; the boson count is $2n$.

## `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard pair",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

The mixed relation means that every bosonic oscillator commutes with each
fermionic oscillator in the undeformed oscillator algebra.

## `central_elements`

This is a required top-level key, separate from the Lie-superalgebra basis:

```json
{
  "kappa": {
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "kappa^2 = 0",
    "description": "Odd formal symbol for the inhomogeneous extension"
  },
  "K": {
    "parity": 0,
    "central": true,
    "relation": "K = 1",
    "description": "Even central identity; scalar identity, not an independent basis element"
  }
}
```

`kappa` records the odd central extension parameter and is not a member of
$C(n+1)$ itself. `K` is the even identity, identified with the scalar $1$;
neither is included in `basis`, `parity`, or the dimension counts.

## `basis`

Use the finalized labels and ordering in `handover/notation.md`. The even
list contains, in order, `H_1` through `H_{n+1}`, all `E_2del{k}_p`
generators, all `E_del{i}_del{j}_pp` and `E_del{i}_del{j}_pm` for $i<j$,
all `E_2del{k}_m`, then all `E_del{i}_del{j}_mm` and
`E_del{i}_del{j}_mp`. Pair labels are grouped lexicographically by $(i,j)$.
The odd list groups by increasing $k$, and within each $k$ uses `pp`, `pm`,
`mp`, `mm`:

```json
{
  "even": [
    "H_1", "...", "H_{n+1}",
    "E_2del1_p", "...", "E_2del{n}_p",
    "E_del{i}_del{j}_pp", "E_del{i}_del{j}_pm",
    "E_2del1_m", "...", "E_2del{n}_m",
    "E_del{i}_del{j}_mm", "E_del{i}_del{j}_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd by k, pp/pm/mp/mm] < [even: Cartan, positive roots, negative roots]; K=1 excluded"
}
```

The displayed ellipses and index patterns describe list generation and must
be expanded into concrete strings in JSON. For every $k=1,\ldots,n$, append
the four odd labels `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`,
`E_eps1_del{k}_mp`, `E_eps1_del{k}_mm`. The even and odd arrays must have
$2n^2+n+1$ and $4n$ elements, respectively.

## `parity`

Provide one integer entry for every basis label: `0` for every even
generator (`H_*`, `E_2del*_p/m`, and `E_del*_del*_*`) and `1` for every odd
generator (`E_eps1_del*_*`). Do not include `kappa` or `K`; those parities
are declared under `central_elements`.

## `generator_realization`

Use the v5.0 realization format: `realizations` is an object keyed by every
basis generator; each value has a `standard_form` array of terms with
`words` (an ordered oscillator-label array) and rational-string `coeff`,
the corresponding `frappat_form`, and integer `parity`. Constant terms use
an empty `words` array. The `ordering` field is a comma-separated string
listing the oscillator word order: `a_1_p`, `a_1_m`, `b_1_p`, `b_1_m`, ...,
`b_n_p`, `b_n_m`.

Use these realization rules, matching the root-label sign conventions in
`handover/notation.md`:

| Generators | Oscillator realization |
|---|---|
| $H_1$ | $a_1^+a_1^-+b_1^+b_1^-$ |
| $H_k$, $2\leq k\leq n$ | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ |
| $H_{n+1}$ | $-b_n^+b_n^- - \frac12$ |
| `E_2del{k}_p/m` | $(b_k^+)^2$ / $(b_k^-)^2$ |
| `E_del{i}_del{j}_pp/pm/mp/mm` | $b_i^+b_j^+$ / $b_i^+b_j^-$ / $b_i^-b_j^+$ / $b_i^-b_j^-$ |
| `E_eps1_del{k}_pp/pm/mp/mm` | $a_1^+b_k^+$ / $a_1^+b_k^-$ / $a_1^-b_k^+$ / $a_1^-b_k^-$ |

Each generator's realization parity must match the `parity` map. If a
normalization factor is needed for a chosen root-vector convention, apply it
consistently to the realization and resulting structure constants; the basis
labels and dimensions do not change.

## `structure_constants`

Store every nonzero undeformed graded bracket in the v5.0 array format:

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

The example is illustrative of the record shape. For each concrete rank,
populate the complete set of nonzero brackets calculated from the oscillator
realizations and the CAR/CCR relations. Use basis labels for `X`, `Y`, and
`Z`, rational strings for `coeff`, and `"graded"` for `sign_rule`; omit zero
brackets. Bracket data must obey
$[X,Y\}=-(-1)^{p(X)p(Y)}[Y,X\}$ and the parity map, with the sign convention
used by the repository's graded-bracket implementation. Store only the
canonical input pair with `X` no later than `Y` in the PBW order
`odd`-then-`even`; for odd-odd pairs the bracket is symmetric, as implied by
graded skew-symmetry.

## `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "docs/math/Cn1_definition.md",
    "docs/math/B0n_schema_v5.md"
  ]
}
```

Record the actual generator and ISO date used for a concrete output file.

## Schema 2: inhomogeneous gamma structure

Use `C_{n}_gamma.json`, paired with `C_{n}_structure.json`. The Schema 2
object has these top-level keys:

```json
{
  "schema_version": "5.0",
  "algebra": {},
  "source_schema1": "C_2_structure.json",
  "gb_matrix": {},
  "inhomogeneous_deformation": {},
  "metadata": {}
}
```

`algebra` must equal the corresponding Schema 1 `algebra` object, and
`source_schema1` identifies that exact basis and rank.

### `gb_matrix`

The two rows correspond, in order, to `a_1_p`, `a_1_m`; columns are bosonic
labels `b_1_p`, `b_1_m`, ..., `b_n_p`, `b_n_m`. It has shape $2\times2n$
and exactly $4n$ distinct parameters:

```json
{
  "row_labels": ["a_1_p", "a_1_m"],
  "column_labels": ["b_1_p", "b_1_m"],
  "shape": [2, 2],
  "parity": 0,
  "entries": [
    ["gb_a_1_p_b_1_p", "gb_a_1_p_b_1_m"],
    ["gb_a_1_m_b_1_p", "gb_a_1_m_b_1_m"]
  ]
}
```

Each row of `entries` aligns with a row label, each column with a column
label. The source text's parity-1 note conflicts with its relation
$[b,a]=-\mathrm{gb}\,\kappa$: since $p(b)=0$, $p(a)=1$, and $p(\kappa)=1$,
homogeneity requires $p(\mathrm{gb})=0$. The schema uses parity 0.

### `inhomogeneous_deformation`

`deformed_mixed_commutators` lists all $4n$ relations
$[b_j^s,a_1^\sigma]=-\mathrm{gb}_{a_1^\sigma,b_j^s}\kappa$, with `X` the
boson, `Y` the fermion, and `relation` the explicit string. `gamma_convention`
declares the factorization
$[X,Y]_\gamma=[X,Y]_0+\kappa\gamma(X,Y)$.

`gamma_coefficients` stores each nonzero canonical pair and output component:

```json
{
  "X": "E_eps1_del1_pp",
  "Y": "H_2",
  "Z": "E_eps1_del1_pp",
  "coefficients": [
    {"parameter": "gb_a_1_p_b_1_m", "coeff": "1"}
  ],
  "sign_rule": "graded"
}
```

`X` and `Y` are basis labels in canonical PBW pair order. `Z` is a Schema 1
basis label or `K`; `K` denotes the scalar identity when a central scalar
term occurs and is not added to the Schema 1 basis or dimension. The
`coefficients` array represents the exact rational linear combination of
named gb parameters; omit zero coefficients. With even gb parameters and odd
$\kappa$, each basis-valued output has parity
$p(Z)=p(X)+p(Y)+1\pmod2$; a `K` output is even.

The metadata records `src/C_gamma_generator.py`, the generation date, and
the inhomogeneous-deformation reference.

## Schema 3: evaluated structure

The representative evaluated profile is `all_plus`: every parameter named
in Schema 2's `gb_matrix.entries` is assigned the integer `+1`. Files are
named `C_{n}_evaluated.json`, as required for this C(n+1) dataset. An
additional `all_zero` profile is available for the zero-deformation case and
is written to `C_{n}_evaluated_zero.json`.

Each file has `schema_version`, `algebra`, `source_schema1`,
`source_schema2`, `gb_assignment`, `evaluated_structure_constants`, and
`metadata`. The two source fields identify the Schema 1 and Schema 2 inputs;
`algebra` matches both inputs. `gb_assignment` contains the profile name and
a `values` object with every gb parameter set to `1`.

Each evaluated record merges the undeformed Schema 1 coefficient and the
numerically evaluated Schema 2 coefficient for a single `(X,Y,Z)`:

```json
{
  "X": "E_eps1_del1_pp",
  "Y": "H_2",
  "Z": "E_eps1_del1_pp",
  "coeff": "1",
  "kappa_coeff": "2",
  "sign_rule": "graded"
}
```

The record means that the bracket contains `coeff * Z` plus
`kappa_coeff * kappa * Z`; either coefficient may be `"0"`, but records with
both coefficients zero are omitted. Rational values are exact strings. The
output label `K` is permitted for the central scalar component, as in Schema
2, without making it an independent Schema 1 basis element. Metadata records
`src/evaluate_C_gamma.py`, the generation date, and the evaluated-bracket
formula.

## Schema 4: coboundary structure

Use `C_{n}_coboundary.json`, paired with `C_{n}_structure.json`. The object
contains `schema_version`, `algebra`, `source_schema1`, `basis`, `parity`,
`linear_map_f`, `coboundary_convention`, `coboundary_coefficients`, and
`metadata`. The copied basis, parity, and algebra must match the source Schema
1 data.

`linear_map_f` describes a generic odd map
$f(Z_j)=\sum_{i:p(Z_i)\ne p(Z_j)}\phi_{i,j}Z_i$. Its `parameters` array has
one entry per parity-reversing input/output pair:

```json
{
  "input": "E_eps1_del1_pp",
  "output": "H_1",
  "parameter": "phi_H_1_from_E_eps1_del1_pp"
}
```

`coboundary_convention` records the formula from
`docs/math/C_coboundary_definition.md`. `coboundary_coefficients` stores each
nonzero canonical input pair and output basis label:

```json
{
  "X": "E_eps1_del1_pp",
  "Y": "E_eps1_del1_mm",
  "Z": "H_1",
  "coefficients": [
    {"parameter": "phi_H_1_from_E_eps1_del1_pp", "coeff": "2"}
  ],
  "sign_rule": "graded"
}
```

The `coefficients` array is a sparse exact rational linear combination of
the parameters in `linear_map_f`; omit zero terms. Store input pairs once in
PBW order. Since $f$ is odd, every nonzero output has parity
$p(Z)=p(X)+p(Y)+1\pmod2$. Metadata records
`src/C_coboundary_generator.py`, the generation date, and the coboundary
reference.
