# C(n+1) = osp(2|2n) JSON Schema Specification

This document specifies Schema 1 (algebra structure) for
$C(n+1)=\mathfrak{osp}(2|2n)$, extending the v5.0 structure-data conventions
used for $B(0,n)$. The variable $n$ is the bosonic rank and is a positive
integer. Files contain one concrete rank at a time; formula fields retain the
general-rank formulas.

## Schema 1: Algebra Structure

### File name and top-level keys

Use `C_{n}_structure.json`, where `n` is the bosonic rank:

| Algebra | File |
|---|---|
| C(2) = osp(2\|2), n=1 | `C_1_structure.json` |
| C(3) = osp(2\|4), n=2 | `C_2_structure.json` |
| C(4) = osp(2\|6), n=3 | `C_3_structure.json` |

The schema version remains `"5.0"`. The required top-level keys are:

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

### `algebra`

`dimension` contains integer values evaluated for the `n` in the file.
`dimension_formula` records the general formulas as strings.

```json
{
  "family": "C",
  "m": 1,
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {
    "osp": "osp(2|4)",
    "dimension_formula": "osp(2m|2n), m=1"
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

In each file, `cartan_type` is `"C(n+1)"` with the concrete value of `n`
substituted (for example, `"C(3)"` for `n=2`), and `alternative_notation.osp`
is `"osp(2|2n)"` with the same substitution. Dimensions describe
$\mathfrak{osp}(2|2n)$ and do not include the optional formal extension
generator $\kappa$.

| n | even | odd | total |
|---:|---:|---:|---:|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

### `oscillator_generators`

This object has exactly two keys, `fermions` and `bosons`. Labels are
interleaved by bosonic rank in the boson group.

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
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± for k=1,...,n"
  }
}
```

For rank `n`, `bosons.count` is `2*n`, and its labels are
`b_1_p, b_1_m, ..., b_n_p, b_n_m`.

### `oscillator_relations`

Relation expressions are strings. The minus/plus subscripts correspond to
labels `_m` and `_p`, respectively.

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermion pair",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i,j",
      "conjugate_pair": "[b_i_m, b_j_p] = δ_ij"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

### `central_elements`

This is a top-level object. These records document the central symbols used
by the algebra/deformation data; they are not additional root generators.

```json
{
  "kappa": {
    "parity": 1,
    "central": true,
    "nilpotency": "kappa^2 = 0"
  },
  "K": {
    "parity": 0,
    "central": true,
    "value": "1"
  }
}
```

`K` is the scalar identity and is never an independent basis element.
`kappa` is the odd nilpotent central extension symbol; include it at the start
of a PBW ordering only when represented in that data. Neither symbol changes
the even/odd dimension formulas above.

### `basis`

`basis.even` contains the Cartan generators followed by the even-root
generators. `basis.odd` contains the odd-root generators. Generate labels for
each rank as follows:

- Cartan: `H_1, ..., H_{n+1}`.
- For each `1 <= k <= n`: `E_2del{k}_p`, `E_2del{k}_m`.
- For each `1 <= i < j <= n`: `E_del{i}_del{j}_pp`,
  `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`, `E_del{i}_del{j}_mm`.
- For each `1 <= k <= n`: `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`,
  `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm`.

The pair-label suffixes denote roots as follows:

| Label | Root |
|---|---|
| `E_2del{k}_p` / `E_2del{k}_m` | `±2δ_k` |
| `E_del{i}_del{j}_pp` | `δ_i + δ_j` |
| `E_del{i}_del{j}_pm` | `δ_i - δ_j` |
| `E_del{i}_del{j}_mp` | `-δ_i + δ_j` |
| `E_del{i}_del{j}_mm` | `-δ_i - δ_j` |

For odd labels the first suffix sign is the `ε` sign and the second is the
`δ_k` sign: `pp` is `ε+δ_k`, `pm` is `ε-δ_k`, `mp` is `-ε+δ_k`, and `mm` is
`-ε-δ_k`.

Use the following PBW sequence:

1. `kappa`, if represented; omit `K=1`.
2. Odd positive roots: increasing `k`, `E_eps1_del{k}_pp`, then
   `E_eps1_del{k}_pm`.
3. Odd negative roots: increasing `k`, `E_eps1_del{k}_mp`, then
   `E_eps1_del{k}_mm`.
4. `H_1, ..., H_{n+1}`.
5. Positive even roots: `E_2del{k}_p` by increasing `k`, then
   `E_del{i}_del{j}_pp` and `E_del{i}_del{j}_pm`, each by lexicographic
   `(i,j)`.
6. Negative even roots: `E_2del{k}_m` by increasing `k`, then
   `E_del{i}_del{j}_mm` and `E_del{i}_del{j}_mp`, each by lexicographic
   `(i,j)`.

Keep `basis.even` and `basis.odd` as the algebra root/Cartan lists; the
optional `kappa` ordering prefix is not included in those lists. `K` is not
listed. The basis dimensions are `2n^2+n+1` even and `4n` odd.

### `parity`

Map every label in `basis.even` to `0` and every label in `basis.odd` to `1`.
The parity field covers the algebra basis, not the optional central symbols.
The central-symbol parities are recorded in `central_elements`.

### `generator_realization`

Keep the v5.0 `description`, `ordering`, and `realizations` structure.
`ordering` is `a_1_p, a_1_m`, followed by `b_k_p, b_k_m` in increasing `k`.
Each realization has `standard_form` (a list of oscillator words and rational
coefficient strings), `frappat_form`, and `parity`.

Use these oscillator expressions:

| Generator | Oscillator expression |
|---|---|
| `H_1` | `a_1_p a_1_m + b_1_p b_1_m` |
| `H_k`, `2 <= k <= n` | `b_{k-1,p} b_{k-1,m} - b_{k,p} b_{k,m}` |
| `H_{n+1}` | `-b_{n,p} b_{n,m} - 1/2` |
| `E_2del{k}_p/m` | `(b_k_p/m)^2` |
| `E_del{i}_del{j}_XY`, `i<j` | `b_i_X b_j_Y` |
| `E_eps1_del{k}_pp` | `a_1_p b_k_p` |
| `E_eps1_del{k}_pm` | `a_1_p b_k_m` |
| `E_eps1_del{k}_mp` | `a_1_m b_k_p` |
| `E_eps1_del{k}_mm` | `a_1_m b_k_m` |

The Cartan expressions apply for all `n>=1`; the middle Cartan range is empty
for `n=1`. Use the uniform all-root expressions above. If a realization uses
a simple-generator normalization factor, record it in its coefficient; such
normalization does not alter the root-to-label mapping. For example:

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
      "parity": 0,
      "note": "Terminal Cartan generator"
    },
    "E_eps1_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    }
  }
}
```

### `structure_constants`

Store nonzero graded brackets $[X,Y\}$ as a list of records. `coeff` is a
rational coefficient encoded as a string; `sign_rule` is `"graded"`.
Recompute the C(n+1) brackets using the C(n+1) generator realizations and
the CAR/CCR above; B(0,n) constants, particularly those involving odd
generators, are not interchangeable.

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

The example illustrates the record format; each rank-specific data file
contains the complete set of nonzero brackets for that rank.

### `metadata`

Keep the v5.0 metadata fields. Identify the C(n+1) structure-constant
generator, record the generation date in `YYYY-MM-DD` format, and cite the
C(n+1) definition and applicable general references.

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "C(n+1) = osp(2|2n) mathematical definition"
  ]
}
```

## Compatibility with the B(m,n) v5.0 schema

C-family data remains version 5.0 and preserves the shared names and
representations for `algebra`, `basis`, `parity`, `generator_realization`,
`structure_constants`, and `metadata`. C-family files are separate from
B-family files, so existing B(m,n) files and their readers retain their
existing interpretation. The C-specific changes are:

- `algebra.family` is `"C"` and `algebra.m` is `1`; C dimensions include the
  additional even Cartan direction and have `4n` odd generators.
- `oscillator_generators` uses the `fermions` and `bosons` groups instead of
  B's `supplementary_fermion`.
- `oscillator_relations` defines standard CAR and CCR rather than the
  supplementary-fermion square relation.
- `central_elements` is an additional top-level key recording `kappa` and
  `K`.
- The odd-root labels, basis, parities, realizations, and structure constants
  are those of C(n+1).

Other C-family data layers, when present, use rank-based names. Schema 2 uses
`C_{n}_gamma.json`; Schema 3 uses `C_{n}_evaluated.json` for the approved
uniform-positive profile (other profiles may add a profile suffix); and Schema
4 uses `C_{n}_coboundary.json`. Schema 4 depends on the Layer 1 bracket and
general odd-map parameters, not the deformation parameter `gb`.

## Schema 3: Evaluated Structure

For the approved uniform-positive profile, use `C_{n}_evaluated.json` for
each rank. The file records the complete assignment explicitly, so the profile
remains unambiguous if additional evaluation profiles are added later.

Schema 3 has `schema_version: "5.0"`, `schema_layer: 3`, and
`schema_type: "evaluated_structure"`. It preserves `algebra`, `basis`,
`parity`, `central_elements`, and `scalar_output` from Schema 2, and adds:

```json
{
  "gb_assignment": {
    "profile": "uniform_positive",
    "description": "All scalar gb parameters are set to +1.",
    "parameters": {
      "gb_a1_p_b1_p": "1",
      "gb_a1_p_b1_m": "1",
      "gb_a1_m_b1_p": "1",
      "gb_a1_m_b1_m": "1"
    }
  },
  "evaluated_constants": [
    {
      "X": "E_eps1_del1_pp",
      "Y": "H_1",
      "Z": "H_1",
      "coeff": "1",
      "sign_rule": "graded"
    }
  ],
  "metadata": {
    "generated_by": "C_evaluate.py",
    "generation_date": "YYYY-MM-DD",
    "source_schema": "C_1_gamma.json",
    "gb_profile": "uniform_positive",
    "references": []
  }
}
```

The `parameters` object contains all `4n` Schema 2 parameter labels, each
mapped to the exact scalar string `"1"`. `evaluated_constants` contains the
exact sum of each Schema 2 `coeff` term after substitution; coefficients are
rational strings, `sign_rule` is `"graded"`, and zero terms are omitted.
The distinguished scalar output `K` is retained like any other output label.

## Schema 4: Coboundary Structure

Use `C_{n}_coboundary.json` for each bosonic rank. Schema 4 records the
symbolic coboundary of a general odd linear map and is independent of the
inhomogeneous-deformation parameters `gb`.

The map reverses parity. With even basis \(e_1,\ldots,e_E\) and odd basis
\(o_1,\ldots,o_O\), its independent coefficients are

\[
f(e_a)=\sum_{\mu=1}^{O}\phi_{\mu a}o_\mu,\qquad
f(o_\mu)=\sum_{a=1}^{E}\psi_{a\mu}e_a.
\]

The global scale is normalized to `1`; the \(\phi\) and \(\psi\) coefficients
remain independent formal parameters. There are \(2EO\) map parameters, with
\(E=2n^2+n+1\) and \(O=4n\).

Schema 4 has `schema_version: "5.0"`, `schema_layer: 4`, and
`schema_type: "coboundary_structure"`. It preserves the `algebra`, `basis`,
and `parity` context from Schema 1 and records the map and its resulting
ordered coefficients:

```json
{
  "schema_version": "5.0",
  "schema_layer": 4,
  "schema_type": "coboundary_structure",
  "algebra": {},
  "basis": {},
  "parity": {},
  "odd_linear_map": {
    "parity": 1,
    "global_scale": "1",
    "parameter_count": 32,
    "parameterization": "f(e_a) = sum_mu phi__o_mu__from__e_a * o_mu; f(o_mu) = sum_a psi__e_a__from__o_mu * e_a",
    "coefficients": [
      {
        "parameter": "phi__E_eps1_del1_pp__from__H_1",
        "source": "H_1",
        "target": "E_eps1_del1_pp"
      }
    ],
    "dimensions": {
      "even_basis_count": 4,
      "odd_basis_count": 4
    }
  },
  "coboundary_definition": "(delta f)(X,Y) = (-1)^p(X)[X,f(Y)] - (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])",
  "coboundary_constants": [
    {
      "X": "H_1",
      "Y": "E_eps1_del1_pp",
      "Z": "H_1",
      "coeff": [
        {
          "parameter": "phi__E_eps1_del1_mm__from__H_1",
          "scalar": "-1"
        }
      ],
      "sign_rule": "graded"
    }
  ],
  "metadata": {
    "generated_by": "C_coboundary.py",
    "generation_date": "YYYY-MM-DD",
    "source_schema": "C_1_structure.json",
    "references": [
      "C(n+1) = osp(2|2n) mathematical definition",
      "Coboundary operator definition (odd linear map)"
    ]
  }
}
```

The `coefficients` array enumerates every parity-reversing source/target pair
once. In each `coboundary_constants` record, `coeff` is a list of exact
parameter/scalar terms; rational scalars are strings, zero terms are omitted,
and outputs are Schema 1 basis labels. Store both ordered orientations with
coefficients satisfying graded skew-symmetry. Each output has parity
\((p(X)+p(Y)+1)\bmod 2\), and the records are computed from the Schema 1
brackets using the defining coboundary formula above.
