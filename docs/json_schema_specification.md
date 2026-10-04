# C(n+1) JSON Schema Specification (v5.0 Extension)

This document specifies the v5.0 JSON schema for $C(n+1) = \mathfrak{osp}(2|2n)$,
extended from the B(0,n) v5.0 schema defined in `docs/math/B0n_schema_v5.md`.

---

## File Naming Convention

| Algebra | n (bosonic rank) | Schema 1 file | Schema 2 file | Schema 3 file | Schema 4 file |
|---|---|---|---|---|---|
| C(2) = osp(2\|2) | 1 | `C_1_structure.json` | `C_1_gamma.json` | `C_1_evaluated.json` | `C_1_coboundary.json` |
| C(3) = osp(2\|4) | 2 | `C_2_structure.json` | `C_2_gamma.json` | `C_2_evaluated.json` | `C_2_coboundary.json` |
| C(4) = osp(2\|6) | 3 | `C_3_structure.json` | `C_3_gamma.json` | `C_3_evaluated.json` | `C_3_coboundary.json` |

The index `n` is the **bosonic rank** (number of bosonic oscillator pairs), not the C-series label.

---

## Schema 1: Algebra Structure

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
    "formula_even": "2n^2 + n + 1",
    "formula_odd": "4n"
  }
}
```

**Dimension formulas** (C(n+1)): even = $2n^2+n+1$, odd = $4n$, total = $2n^2+5n+1$.

| n | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

### `central_elements`

**Top-level key** (mandatory for C(n+1)):

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relation": "kappa^2 = 0",
    "description": "Odd nilpotent central element of the abelian extension."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "K = 1 (scalar identity)",
    "description": "Even central identity; identified with 1 in all realizations. Excluded from PBW basis."
  }
}
```

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^+, a_1^- with CAR {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

(Labels for n=2 would include `b_2_p, b_2_m`, etc.)

**Key difference from B(0,n)**: `supplementary_fermion` (with `a_0^2=1/2`) is replaced by `fermions` (standard CAR pair).

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "self_anticommutator_p": "{a_1^+, a_1^+} = 0",
      "self_anticommutator_m": "{a_1^-, a_1^-} = 0"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed)"
  }
}
```

### `basis`

PBW ordering: `κ < [odd: E_eps_del{k}_{pp/pm/mp/mm}] < [even: H_k, E_2del{k}_p, E_del{i}_del{j}_pp, E_2del{k}_m, E_del{i}_del{j}_mm, E_del{i}_del{j}_pm, E_del{i}_del{j}_mp]`

Example for n=1 (C(2)):
```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": [
    "E_eps_del1_pp", "E_eps_del1_pm",
    "E_eps_del1_mp", "E_eps_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: ε-roots] < [even]  (K = 1 is excluded from basis)"
}
```

Example for n=2 (C(3)):
```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del1_pm", "E_eps_del1_mp", "E_eps_del1_mm",
    "E_eps_del2_pp", "E_eps_del2_pm", "E_eps_del2_mp", "E_eps_del2_mm"
  ]
}
```

### `parity`

All even generators have parity 0; all odd generators (E_eps_del{k}_{...}) have parity 1.

```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps_del1_pp": 1, "E_eps_del1_pm": 1,
  "E_eps_del1_mp": 1, "E_eps_del1_mm": 1
}
```

### `generator_realization`

PBW oscillator ordering: `a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`

Key realizations (n=1 example):

```json
{
  "description": "Standard form with PBW oscillator ordering",
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
      "note": "Terminal Cartan H_{n+1}; constant -1/2 from definition"
    },
    "E_2del1_p": {
      "standard_form": [{"words": ["b_1_p", "b_1_p"], "coeff": "1/2"}],
      "frappat_form": "(1/2)(b_1^+)^2",
      "parity": 0
    },
    "E_2del1_m": {
      "standard_form": [{"words": ["b_1_m", "b_1_m"], "coeff": "1/2"}],
      "frappat_form": "(1/2)(b_1^-)^2",
      "parity": 0
    },
    "E_eps_del{k}_pp": {
      "standard_form": [{"words": ["a_1_p", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1
    },
    "E_eps_del{k}_pm": {
      "standard_form": [{"words": ["a_1_p", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^-",
      "parity": 1
    },
    "E_eps_del{k}_mp": {
      "standard_form": [{"words": ["a_1_m", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^+",
      "parity": 1
    },
    "E_eps_del{k}_mm": {
      "standard_form": [{"words": ["a_1_m", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^-",
      "parity": 1
    }
  }
}
```

### `structure_constants`

Non-zero graded brackets $[X, Y\}$ stored as a list of objects:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps_del1_pp",
    "Z": "E_eps_del1_pp",
    "coeff": "2",
    "sign_rule": "graded"
  }
]
```

For computation rules see `src/C_generators.py` (produced in I03).

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017), arXiv:1612.09400"
  ]
}
```

---

## Compatibility with B(m,n) Schema

| Field | B(0,n) | C(n+1) | Compatibility |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | Same |
| `algebra.family` | `"B"` | `"C"` | Family key distinguishes |
| `algebra.m` | `0` | `1` | Explicit `m` field |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | Different fermion key |
| `central_elements` | top-level (κ, K) | top-level (κ, K) | Same structure |
| `basis.odd` | `E_del{k}_p/m` | `E_eps_del{k}_{pp/pm/mp/mm}` | 4n vs 2n generators |
| `structure_constants` | list format | list format | Same format |

---

## Schema 2: Inhomogeneous Deformation (γ-structure)

Top-level keys extend Schema 1 with:

```json
{
  "inhomogeneous_deformation": {
    "gb_matrix": {
      "size": "2 x 2n",
      "description": "4n symbolic deformation parameters",
      "parameters": ["gb_a1p_b1p", "gb_a1p_b1m", "gb_a1m_b1p", "gb_a1m_b1m", ...]
    },
    "gamma_coefficients": [ ... ]
  }
}
```

## Schema 3: Evaluated Structure

Extends Schema 2 with concrete numerical values for the `gb` parameters:

```json
{
  "gb_assignment": {
    "gb_a1p_b1p": 1, "gb_a1p_b1m": 1, ...
  },
  "evaluated_structure_constants": [ ... ]
}
```

## Schema 4: Coboundary Structure

```json
{
  "f_map": {
    "description": "Odd linear map f: g -> g, parameterized by phi_{ij}",
    "phi_coefficients": { ... }
  },
  "coboundary_coefficients": [ ... ]
}
```
