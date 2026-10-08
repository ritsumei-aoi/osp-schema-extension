# JSON Schema Specification for C(n+1) = osp(2|2n) (v5.0 extension)

This document specifies the complete 4-layer JSON schema for
$C(n+1) = \mathfrak{osp}(2|2n)$. It extends the B(0,n) v5.0 schema
(`docs/math/B0n_schema_v5.md`) and is the normative reference for the files in `data/`.

Conventions (labels, PBW order, basis lists) are defined in `handover/notation.md`.

| Layer | File | Produced by | Issue |
|---|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | `src/C_generators.py` | I03 |
| Schema 2 | `data/C_{n}_gamma.json` | `src/C_gamma.py` | I05 |
| Schema 3 | `data/C_{n}_evaluated.json` | `src/C_evaluate.py` | I06 |
| Schema 4 | `data/C_{n}_coboundary.json` | `src/C_coboundary.py` | I07 |

`n` is always the **bosonic rank** (C(2) = osp(2|2) is `n=1`, C(3) is `n=2`, C(4) is `n=3`).

---

## Schema 1: Algebra structure (`C_{n}_structure.json`)

### Top-level keys

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "oscillator_generators": { ... },
  "oscillator_relations": { ... },
  "central_elements": { ... },
  "basis": { ... },
  "parity": { ... },
  "generator_realization": { ... },
  "structure_constants": [ ... ],
  "metadata": { ... }
}
```

Compared with B(0,n) v5.0 there is exactly **one new top-level key**, `central_elements`.
All other keys keep their B(0,n) names and types, so a B(0,n) v5.0 reader can load a
C(n+1) file after ignoring the unknown key.

### `schema_version`

`"5.0"` (unchanged; the C(n+1) extension is backward compatible, see "Compatibility").

### `algebra`

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
  "dimension_formulas": {
    "even": "2n^2 + n + 1",
    "odd": "4n",
    "total": "2n^2 + 5n + 1"
  },
  "dimension": { "total": 8, "even": 4, "odd": 4 },
  "even_subalgebra": "so(2) + sp(2n)"
}
```

* `cartan_type` is `"C(n+1)"` with the value of n+1 substituted.
* `m` is always `1` (fixed rule).
* `dimension_formulas` is new (B(0,n) kept the formulas only in the spec text).

| n | even | odd | total |
|---|---|---|---|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± with CAR {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "n": 1,
    "count": 2,
    "labels": ["b_1_p", "b_1_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

The B(0,n) key `supplementary_fermion` is **removed**; it is replaced by `fermions`.
`bosons` is unchanged.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^±, a_1^±} = 0  (i.e. (a_1^±)^2 = 0)"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^±, a_1^±] = 0  (undeformed; Schema 2 deforms this to -gb·kappa)"
  },
  "normal_order": "kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m"
}
```

`supplementary_fermion_relation` is replaced by `standard_fermion_anticommutators`.

### `central_elements` (new top-level key)

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relation": "kappa^2 = 0",
    "central": "[kappa, X} = 0 for all X (anticommutes with odd oscillators as an associative element)",
    "role": "formal odd parameter of the inhomogeneous deformation (Schema 2); absent from Schema 1 brackets",
    "in_basis": false
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "K = 1 (identified with the scalar identity)",
    "role": "even central element of the oscillator extension A = V + CK + C kappa; appears as a target of gamma in Schema 2",
    "in_basis": false
  }
}
```

Neither element is in `basis.even`/`basis.odd`. `K` may appear as a value of `"Z"` in
Schema 2–4 entries (see below); `kappa` never appears as a `"Z"` because it is factored out
of $\gamma$.

### `basis`

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "cartan": ["H_1", "H_2"],
  "pbw_order": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm",
                "H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)"
}
```

`even`, `odd`, `ordering_convention` are as in B(0,n). `cartan` and `pbw_order` are new
informational keys. The list order inside `even` and `odd` is the PBW order of
`handover/notation.md` §4.

### `parity`

Map label → 0/1 for every basis element (even: 0, odd: 1).

### `generator_realization`

```json
{
  "description": "Standard form with oscillator normal ordering",
  "ordering": "kappa, a_1_p, a_1_m, b_1_p, b_1_m",
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
      "note": "Terminal Cartan; the constant is required for closure"
    },
    "E_eps1_del1_pp": {
      "standard_form": [{"words": ["a_1_p", "b_1_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    }
  }
}
```

Every basis element has an entry. `words` are in oscillator normal order; the empty word
is the scalar 1 (= K). Coefficients are rational strings.

### `structure_constants`

List of **all** non-zero graded brackets for **all ordered pairs** $(X, Y)$ of basis elements:

```json
{"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"}
```

meaning $[X, Y\} = \sum_Z \mathrm{coeff}\cdot Z$ with $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$.
Both $(X,Y)$ and $(Y,X)$ are stored, so graded antisymmetry can be verified from the file.
`Z` is always a basis label in Schema 1 (never `K`; this is asserted by the generator).

### `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "notation": "handover/notation.md",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## Compatibility with the B(m,n) / B(0,n) v5.0 schema

| Key | B(0,n) v5.0 | C(n+1) | Compatibility |
|---|---|---|---|
| `schema_version` | "5.0" | "5.0" | identical |
| `algebra.family` | "B" | "C" | readers switch on this |
| `algebra.m` | 0 | 1 | same type |
| `algebra.dimension_formulas` | absent | present | additive |
| `oscillator_generators.supplementary_fermion` | present | **absent** | readers must test for `fermions` when family == "C" |
| `oscillator_generators.fermions` | absent | present | additive |
| `oscillator_relations.supplementary_fermion_relation` | present | absent | replaced by `standard_fermion_anticommutators` |
| `central_elements` | absent (B(0,n) mentions it in prose only) | top-level | additive |
| `basis.even/odd/ordering_convention` | present | present | identical types; `cartan`, `pbw_order` additive |
| `parity`, `generator_realization`, `structure_constants`, `metadata` | present | present | identical types |

Rule: everything that exists in B(0,n) v5.0 and still makes sense for C(n+1) keeps its name and
type; family-specific keys are replaced (fermion sector) and new information is only ever added.
A generic reader can therefore handle both families by branching on `algebra.family`.

---

## Schema 2: Inhomogeneous deformation (`C_{n}_gamma.json`) — defined in I05

*(filled in by Issue I05)*

## Schema 3: Evaluated structure (`C_{n}_evaluated.json`) — defined in I06

*(filled in by Issue I06)*

## Schema 4: Coboundary structure (`C_{n}_coboundary.json`) — defined in I07

*(filled in by Issue I07)*
