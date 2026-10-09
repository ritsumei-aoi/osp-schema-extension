# C(n+1) JSON Schema Specification (v5.0 Extension)

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n) structure constants,
extending the B(0,n) v5.0 schema defined in `docs/math/B0n_schema_v5.md`.

---

## File Naming Convention

| n | Algebra | Schema 1 | Schema 2 | Schema 3 | Schema 4 |
|---|---|---|---|---|---|
| 1 | C(2) = osp(2\|2) | `C_1_structure.json` | `C_1_gamma.json` | `C_1_evaluated.json` | `C_1_coboundary.json` |
| 2 | C(3) = osp(2\|4) | `C_2_structure.json` | `C_2_gamma.json` | `C_2_evaluated.json` | `C_2_coboundary.json` |
| 3 | C(4) = osp(2\|6) | `C_3_structure.json` | `C_3_gamma.json` | `C_3_evaluated.json` | `C_3_coboundary.json` |

The index `n` is the **bosonic rank** (number of bosonic oscillator pairs), matching B(0,n) convention.

---

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
    "formula_even": "2*n^2 + n + 1",
    "formula_odd": "4*n"
  }
}
```

Dimension formulas (C(n+1)):
- even = 2n² + n + 1
- odd = 4n
- total = 2n² + 5n + 1

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
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± with CAR: {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n; CCR: [b_k^-, b_l^+] = delta_kl"
  }
}
```

**Key difference from B(0,n)**: The `supplementary_fermion` key is replaced by `fermions`
containing a standard CAR pair. The `bosons` key structure is identical.

### `central_elements` (top-level key)

```json
{
  "K": {
    "parity": 0,
    "description": "Even central element; identified with scalar 1 in all current applications.",
    "nilpotent": false
  },
  "kappa": {
    "parity": 1,
    "description": "Odd central element; formal symbol of nilpotent extension. kappa^2 = 0.",
    "nilpotent": true
  }
}
```

`central_elements` is a **top-level key** in the JSON document (not nested under `oscillator_generators`).

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {
      "creation_annihilation": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^+, a_1^+} = 0",
      "same_type_m": "{a_1^-, a_1^-} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_ij"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^±, a_1^±] = 0 (undeformed)"
  }
}
```

### `basis`

PBW ordering: `κ < [odd] < [even]`

```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]"
}
```

(The above example is for n=1. For n=2 and n=3 the lists are longer, per `handover/notation.md`.)

### `parity`

```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

All even generators have parity 0; all `E_eps1_del{k}_{...}` generators have parity 1.

### `generator_realization`

```json
{
  "description": "Oscillator words with PBW ordering",
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
      "note": "Terminal Cartan; negative sign distinguishes from B(0,n)"
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
      "standard_form": [{"words": ["b_k_p", "b_k_p"], "coeff": "1"}],
      "frappat_form": "(b_k^+)^2",
      "parity": 0
    },
    "E_2del{k}_m": {
      "standard_form": [{"words": ["b_k_m", "b_k_m"], "coeff": "1"}],
      "frappat_form": "(b_k^-)^2",
      "parity": 0
    },
    "E_del{i}_del{j}_pp": {
      "standard_form": [{"words": ["b_i_p", "b_j_p"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^+",
      "parity": 0
    }
  }
}
```

### `structure_constants`

Format identical to B(0,n) schema: list of non-zero graded brackets.

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
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "arXiv:hep-th/9607161"
  ]
}
```

---

## Compatibility with B(m,n) Schema

| Field | B(0,n) | C(n+1) | Notes |
|---|---|---|---|
| `algebra.family` | `"B"` | `"C"` | |
| `algebra.m` | `0` | `1` | |
| `oscillator_generators` key | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | |
| Fermionic relation | `a_0^2 = 1/2` | `{a_1^-, a_1^+} = 1` | CAR vs. non-standard |
| Odd basis labels | `E_del{k}_p/m` | `E_eps1_del{k}_pp/pm/mp/mm` | 2n vs. 4n generators |
| `central_elements` | present (top-level) | present (top-level) | Same structure |
| `schema_version` | `"5.0"` | `"5.0"` | Unchanged |
| Dimension formulas | even=2n²+n, odd=2n | even=2n²+n+1, odd=4n | Extra so(2) factor |

---

## Schema 2: Gamma Structure (`C_{n}_gamma.json`)

Top-level keys:
- `schema_version`: `"5.0"`
- `algebra`: same as Schema 1
- `gb_matrix`: 4n deformation parameters (parity 1)
- `inhomogeneous_deformation`: gamma coefficients γ_abc as symbolic expressions in gb

### `gb_matrix`

```json
{
  "size": "2 x 2n",
  "description": "4n deformation parameters of parity 1",
  "parameters": {
    "gb_a1p_b1p": {"parity": 1, "index": ["+", 1, "+"]},
    "gb_a1p_b1m": {"parity": 1, "index": ["+", 1, "-"]},
    "gb_a1m_b1p": {"parity": 1, "index": ["-", 1, "+"]},
    "gb_a1m_b1m": {"parity": 1, "index": ["-", 1, "-"]}
  }
}
```

---

## Schema 3: Evaluated Structure (`C_{n}_evaluated.json`)

Same as Schema 2 but with concrete numeric values substituted for all gb parameters.
Includes an `evaluation` key recording the substitution used.

---

## Schema 4: Coboundary Structure (`C_{n}_coboundary.json`)

Records the coboundary δf for an odd linear map f: g → g.
Top-level keys:
- `schema_version`: `"5.0"`
- `algebra`: same as Schema 1
- `linear_map_f`: coefficients φ_ij of the odd map f
- `coboundary`: (δf)_abc coefficients

The coboundary formula: (δf)(X,Y) = (-1)^p(X) [X, f(Y)] - (-1)^((p(X)+1)p(Y)) [Y, f(X)] - f([X,Y])
