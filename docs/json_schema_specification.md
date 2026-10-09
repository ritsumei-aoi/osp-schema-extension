# C(n+1) JSON Schema Specification (v5.0 Extension)

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n), extending
the B(0,n) v5.0 schema defined in `docs/math/B0n_schema_v5.md`.

---

## File Naming Convention

| n | Algebra | Files |
|---|---|---|
| 1 | C(2) = osp(2\|2) | `C_1_structure.json`, `C_1_gamma.json`, `C_1_evaluated.json`, `C_1_coboundary.json` |
| 2 | C(3) = osp(2\|4) | `C_2_structure.json`, `C_2_gamma.json`, `C_2_evaluated.json`, `C_2_coboundary.json` |
| 3 | C(4) = osp(2\|6) | `C_3_structure.json`, `C_3_gamma.json`, `C_3_evaluated.json`, `C_3_coboundary.json` |

Where `n` is the bosonic rank (= number of bosonic oscillator pairs = n in osp(2|2n)).

---

## Schema 1: Algebra Structure (`C_{n}_structure.json`)

### Top-Level Keys

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "central_elements": { ... },
  "oscillator_generators": { ... },
  "oscillator_relations": { ... },
  "basis": { ... },
  "parity": { ... },
  "generator_realization": { ... },
  "structure_constants": [ ... ],
  "metadata": { ... }
}
```

Note: `central_elements` is a **top-level key** (not nested under oscillator_generators).

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
    "formula_odd": "4*n",
    "formula_total": "2*n^2 + 5*n + 1"
  }
}
```

**Dimension formulas** (C(n+1)):
| n | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

### `central_elements` (top-level key)

```json
"central_elements": {
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central identity; K=1 in all current applications, excluded from basis."
  },
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "description": "Odd nilpotent central element; kappa^2=0. Appears in deformation bracket.",
    "relation": "kappa^2 = 0"
  }
}
```

### `oscillator_generators`

```json
"oscillator_generators": {
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic CAR pair a_1^± with {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

**Difference from B(0,n)**: Replace `supplementary_fermion` (with $a_0^2 = 1/2$) by a `fermions` key containing the standard CAR pair `a_1_p`, `a_1_m`.

### `oscillator_relations`

```json
"oscillator_relations": {
  "standard_fermion_anticommutators": {
    "description": "CAR for the standard fermionic pair",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "nilpotency_p": "(a_1^+)^2 = 0",
      "nilpotency_m": "(a_1^-)^2 = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^±, a_1^±] = 0 (undeformed)"
  }
}
```

### `basis`

PBW ordering (C(n+1) convention, Option A):
`κ < [odd: E_eps1_del{k}_{pp/pm/mp/mm}] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]`

Example for n=1:
```json
"basis": {
  "even": [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m",
    "E_2del1_p", "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 excluded; kappa excluded from dim count)"
}
```

For n=1 (C(2)):
```json
"basis": {
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "ordering_convention": "PBW: κ < [odd] < [even]"
}
```

For n=2 (C(3)):
```json
"basis": {
  "even": ["H_1","H_2","H_3","E_2del1_p","E_2del2_p","E_del1_del2_pp",
           "E_2del1_m","E_2del2_m","E_del1_del2_mm","E_del1_del2_pm","E_del1_del2_mp"],
  "odd": ["E_eps1_del1_pp","E_eps1_del1_pm","E_eps1_del1_mp","E_eps1_del1_mm",
          "E_eps1_del2_pp","E_eps1_del2_pm","E_eps1_del2_mp","E_eps1_del2_mm"],
  "ordering_convention": "PBW: κ < [odd] < [even]"
}
```

### `parity`

All `E_eps1_*` generators have parity 1; all others have parity 0.

```json
"parity": {
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

### `generator_realization`

Each generator as an oscillator word sum:

```json
"generator_realization": {
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
      "note": "Terminal Cartan; constant -1/2 absorbs the K=-1/2 contribution"
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
    }
  }
}
```

### `structure_constants`

Non-zero graded brackets $[X, Y\}$ stored as a list. Each entry:

```json
{
  "X": "H_1",
  "Y": "E_eps1_del1_pp",
  "Z": "E_eps1_del1_pp",
  "coeff": "1",
  "sign_rule": "graded"
}
```

The bracket convention: $[X, Y\} = XY - (-1)^{p(X)p(Y)} YX$ (graded supercommutator).
For odd-odd pairs, this is the anticommutator.

### `metadata`

```json
"metadata": {
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)",
    "docs/math/Cn1_definition.md"
  ]
}
```

---

## Schema 2: Inhomogeneous Deformation (`C_{n}_gamma.json`)

Extends Schema 1 with the gamma-structure for the inhomogeneous deformation.

### Additional top-level key: `inhomogeneous_deformation`

```json
"inhomogeneous_deformation": {
  "gb_matrix": {
    "description": "4n deformation parameters (parity 1), indexed by fermionic and bosonic oscillator labels",
    "size": "4n",
    "parameters": [
      "gb_a1p_b1p", "gb_a1p_b1m", "gb_a1m_b1p", "gb_a1m_b1m",
      ...
    ],
    "parity": 1,
    "deformed_relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa"
  },
  "gamma_coefficients": [
    {
      "X": "...",
      "Y": "...",
      "Z": "...",
      "coeff_expr": "gb_a1p_b1p",
      "description": "gamma(X,Y) = coeff_expr * Z"
    }
  ]
}
```

---

## Schema 3: Evaluated Structure (`C_{n}_evaluated.json`)

Extends Schema 2 with numerical values for the `gb` parameters.

```json
"evaluation": {
  "gb_assignment": {
    "gb_a1p_b1p": "1",
    "gb_a1p_b1m": "1",
    "gb_a1m_b1p": "1",
    "gb_a1m_b1m": "1"
  },
  "evaluated_gamma": [
    {
      "X": "...", "Y": "...", "Z": "...", "coeff": "1"
    }
  ]
}
```

---

## Schema 4: Coboundary Structure (`C_{n}_coboundary.json`)

Records the coboundary $\delta f$ of an odd linear map $f: \mathfrak{g} \to \mathfrak{g}$.

```json
"coboundary": {
  "f_map": {
    "description": "Odd linear map f: g -> g parameterized by phi coefficients",
    "phi_parameters": {
      "phi_E_eps1_del1_pp_H_1": "1",
      ...
    }
  },
  "delta_f_coefficients": [
    {
      "X": "...", "Y": "...", "Z": "...", "coeff": "..."
    }
  ]
}
```

---

## Compatibility with B(m,n) Schema

| Key | B(0,n) v5.0 | C(n+1) v5.0 |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `algebra.dimension_formula` | even=$2n^2+n$, odd=$2n$ | even=$2n^2+n+1$, odd=$4n$ |
| `oscillator_generators` | `supplementary_fermion` (a_0) | `fermions` (a_1_p, a_1_m) |
| `oscillator_relations` | a_0^2=1/2 | {a_1^-,a_1^+}=1 |
| `central_elements` | K only | K and kappa (top-level) |
| `basis.odd` | `E_del{k}_p/m` | `E_eps1_del{k}_{pp/pm/mp/mm}` |
| `gb_matrix` size | 2n | 4n |
