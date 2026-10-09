# C(n+1) JSON Schema Specification v5.0

This document specifies the four-layer JSON schema for $C(n+1) = \mathfrak{osp}(2|2n)$,
extending the B(0,n) v5.0 base schema.

## File Naming Convention

| Algebra | Bosonic rank n | File pattern |
|---|---|---|
| C(2) = osp(2\|2) | 1 | `C_1_structure.json`, `C_1_gamma.json`, `C_1_evaluated.json`, `C_1_coboundary.json` |
| C(3) = osp(2\|4) | 2 | `C_2_structure.json`, etc. |
| C(4) = osp(2\|6) | 3 | `C_3_structure.json`, etc. |

The index in the filename is the bosonic rank n (not the Cartan label n+1).

## Schema 1: Algebra Structure (`C_{n}_structure.json`)

### `schema_version`
```json
"schema_version": "5.0"
```

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
  "dimension": {
    "total": 8,
    "even": 4,
    "odd": 4,
    "even_formula": "2n^2 + n + 1",
    "odd_formula": "4n"
  }
}
```

### `oscillator_generators`
```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard CAR pair: {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

**Compatibility note**: B(0,n) uses a `supplementary_fermion` key with `a_0`. C(n+1) replaces this with `fermions` containing `a_1_p`, `a_1_m`. Parsers must check `algebra.family` to select the correct key.

### `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {
    "description": "CAR: {a_1^-, a_1^+} = 1",
    "relations": {
      "anticommutator": "{a_1_m, a_1_p} = 1",
      "same_sign": "{a_1_p, a_1_p} = 0",
      "same_sign_m": "{a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "CCR for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed)"
  }
}
```

### `central_elements` (top-level key)
```json
{
  "K": {
    "parity": 0,
    "description": "Even central identity element; identified with scalar 1 in all applications.",
    "note": "Not an independent basis element; listed for schema completeness."
  },
  "kappa": {
    "parity": 1,
    "description": "Odd nilpotent central element: kappa^2 = 0. Appears in the inhomogeneous deformation bracket.",
    "nilpotency": "kappa^2 = 0"
  }
}
```

### `basis`

PBW ordering: κ < [odd] < [even]

For n=1:
```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "ordering_convention": "PBW: κ < [odd: E_eps1_del{k}_{pp,pm,mp,mm} k=1..n] < [even: H_k, raising, lowering, mixed]"
}
```

For n=2:
```json
{
  "even": ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
           "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm",
          "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]
}
```

### `parity`

Even generators have parity 0; odd generators have parity 1.

```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

### `generator_realization`

```json
{
  "description": "PBW-ordered oscillator words",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "H_{n+1}": {
      "standard_form": [
        {"words": ["b_n_p", "b_n_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_n^+ b_n^- - 1/2",
      "parity": 0,
      "note": "Terminal Cartan; constant -1/2 from the C(n+1) definition"
    },
    "E_eps1_del{k}_pp": {
      "standard_form": [{"words": ["a_1_p", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_pm": {
      "standard_form": [{"words": ["a_1_p", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^-",
      "parity": 1
    },
    "E_eps1_del{k}_mp": {
      "standard_form": [{"words": ["a_1_m", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_mm": {
      "standard_form": [{"words": ["a_1_m", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^-",
      "parity": 1
    },
    "E_2del{k}_p": {
      "standard_form": [{"words": ["b_k_p", "b_k_p"], "coeff": "1/2"}],
      "frappat_form": "(1/2)(b_k^+)^2",
      "parity": 0
    },
    "E_2del{k}_m": {
      "standard_form": [{"words": ["b_k_m", "b_k_m"], "coeff": "1/2"}],
      "frappat_form": "(1/2)(b_k^-)^2",
      "parity": 0
    }
  }
}
```

### `structure_constants`

Non-zero graded brackets $[X, Y\}$ stored as a list. Format:
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

### `metadata`
```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "2026-10-09",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "arXiv:hep-th/9607161"
  ]
}
```

---

## Schema 2: Inhomogeneous Deformation (`C_{n}_gamma.json`)

Top-level keys: `schema_version`, `algebra`, `gb_matrix`, `inhomogeneous_deformation`, `metadata`.

### `gb_matrix`
```json
{
  "description": "4n deformation parameters (parity 1)",
  "count": "4n",
  "index_convention": "gb[sigma][j][s] where sigma in {p,m}, j in {1..n}, s in {p,m}",
  "labels": ["gb_p1p", "gb_p1m", "gb_m1p", "gb_m1m", ...]
}
```

### `inhomogeneous_deformation`
Contains `gamma_coefficients`: list of `{X, Y, Z, coeff_symbolic}` entries where coeff_symbolic is a polynomial in gb parameters.

---

## Schema 3: Evaluated Structure (`C_{n}_evaluated.json`)

Top-level keys: `schema_version`, `algebra`, `gb_assignment`, `evaluated_gamma`, `metadata`.

### `gb_assignment`
```json
{"gb_p1p": 1, "gb_p1m": 1, "gb_m1p": 1, "gb_m1m": 1, ...}
```

### `evaluated_gamma`
Numeric gamma coefficients after substitution.

---

## Schema 4: Coboundary Structure (`C_{n}_coboundary.json`)

Top-level keys: `schema_version`, `algebra`, `odd_map_f`, `coboundary_delta_f`, `metadata`.

### `odd_map_f`
```json
{
  "description": "Odd linear map f: g -> g, phi_{ij} coefficients",
  "phi_coefficients": {"f_H1_to_E_eps1_del1_pp": "phi_11", ...}
}
```

### `coboundary_delta_f`
List of `{X, Y, Z, coeff_symbolic}` where coeff is a linear combination of phi variables.

---

## Compatibility with B(m,n) Schema

| Field | B(0,n) | C(n+1) |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `oscillator_generators.supplementary_fermion` | present | absent |
| `oscillator_generators.fermions` | absent | present |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` |
| `central_elements` | top-level (K only or with kappa) | top-level (K and kappa) |
| odd basis | `E_del{k}_p/m` | `E_eps1_del{k}_{pp,pm,mp,mm}` |
