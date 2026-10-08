# JSON Schema Specification for C(n+1) = osp(2|2n)

This document specifies the v5.0 JSON schema extended to **C(n+1) = osp(2|2n)**, building on the base B(0,n) schema.

**Reference**: Mathematical definitions in `docs/math/Cn1_definition.md`, `C_inhomogeneous_definition.md`, `C_coboundary_definition.md`.

---

## Overview: 4-Layer Schema Architecture (C(n+1))

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_n_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_n_gamma.json` | Inhomogeneous deformation (γ-structure) with gb parameters |
| Schema 3 | `C_n_evaluated_<gb>.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_n_coboundary_<gb>.json` | Coboundary data for triviality verification |

**File Naming Convention**:
- `C_{n}_structure.json` where `n` is the **bosonic rank** (so C(2)=osp(2|2) uses `n=1`, C(3)=osp(2|4) uses `n=2`, etc.)

---

## Schema 1: Algebra Structure (C(n+1))

### Top-Level Keys

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
  "structure_constants": { ... },
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
    "odd": 4
  }
}
```

**Mandatory rules for all C(n+1)**:
- `family`: Always `"C"`
- `m`: Always `1` (one fermionic pair)
- Dimension formulas:
  - Even: $2n^2 + n + 1$
  - Odd: $4n$
  - Total: $2n^2 + 5n + 1$

**Dimension table**:

| n | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

### `oscillator_generators`

```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "car_relation": "{a_1^-, a_1^+} = 1",
    "parity": 1,
    "description": "Standard fermionic pair under canonical anticommutation relations"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

**Key changes from B(0,n)**:
- No `supplementary_fermion` key; fermionic sector uses `fermions` instead
- The standard fermionic pair satisfies CAR, not a custom relation like $a_0^2 = 1/2$

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "{a_1^-, a_1^+} = 1 (canonical anticommutation relations)",
    "relation": "{a_1_m, a_1_p} = 1"
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "fermion_boson": "[b_i^±, a_1^±] = 0"
  }
}
```

### `central_elements`

```json
{
  "description": "Central extension elements of the Lie superalgebra",
  "elements": {
    "kappa": {
      "label": "κ",
      "parity": 1,
      "property": "nilpotent: κ^2 = 0",
      "role": "Formal symbol of inhomogeneous deformation; appears in structure constants"
    },
    "K": {
      "label": "K",
      "parity": 0,
      "property": "identified with scalar 1",
      "role": "Central even element (by Bakalov–Sullivan); excluded from basis lists"
    }
  }
}
```

**Key points**:
- $\kappa$ is an **odd central element** that parametrizes the deformation
- $K$ is the **even central element**, identified with 1 in all applications
- Only $\kappa$ appears in graded brackets; $K$ is recordedfor schema completeness only

### `basis`

PBW ordering (C(n+1) convention):
```
κ < [odd: E_eps1_del{k}_{...}] < [even: H_i, E_2del{k}_{...}, E_del{i}_del{j}_{...}]
```

For C(2) (n=1):
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
  "ordering_convention": "PBW: κ < [odd: E_eps1_del{k}_{...}] < [even: H_i, E_2del{k}_p, E_del{i}_del{j}_pp/mm/pm/mp, E_2del{k}_m]"
}
```

For C(3) (n=2):
```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm",
    "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: E_eps1_del{k}_{...} for k=1,...,n] < [even generators in root order]"
}
```

### `parity`

```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_mm": 0,
  "E_del1_del2_pm": 0, "E_del1_del2_mp": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1,
  "E_eps1_del2_pp": 1, "E_eps1_del2_pm": 1,
  "E_eps1_del2_mp": 1, "E_eps1_del2_mm": 1
}
```

**Convention**: 
- Even generators (Cartan, even roots): parity 0
- Odd generators (ε roots): parity 1

### `generator_realization`

Each generator is expressed as a sum of oscillator monomials.

```json
{
  "description": "Oscillator realization for C(n+1) generators",
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
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_1^+ b_1^- - b_2^+ b_2^-",
      "parity": 0
    },
    "H_n": {
      "standard_form": [
        {"words": ["b_{n-1}_p", "b_{n-1}_m"], "coeff": "1"},
        {"words": ["b_n_p", "b_n_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_{n-1}^+ b_{n-1}^- - b_n^+ b_n^-",
      "parity": 0
    },
    "H_{n+1}": {
      "standard_form": [
        {"words": ["b_n_p", "b_n_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_n^+ b_n^- - 1/2",
      "parity": 0,
      "note": "Terminal Cartan element"
    },
    "E_eps1_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    },
    "E_eps1_del1_pm": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^-",
      "parity": 1
    }
  }
}
```

### `structure_constants`

Non-zero graded brackets $[X, Y\} = Z$ with coefficient, stored as a list:

```json
{
  "description": "Structure constants [X, Y} = coeff * Z for C(n+1)",
  "bracket_type": "graded Lie superalgebra bracket",
  "constants": [
    {
      "X": "H_1",
      "Y": "E_eps1_del1_pp",
      "Z": "E_eps1_del1_pp",
      "coeff": "1",
      "sign_rule": "graded"
    },
    {
      "X": "E_eps1_del1_pp",
      "Y": "E_eps1_del1_mm",
      "Z": "H_1",
      "coeff": "1",
      "sign_rule": "graded"
    }
  ]
}
```

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "schema_version": "5.0",
  "algebra_family": "C(n+1)",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017), arXiv:1612.09400"
  ],
  "notes": [
    "This schema extends the B(m,n) schema to the C(n+1) case",
    "Central element κ (odd) parametrizes inhomogeneous deformation",
    "K (even) is identified with scalar 1 and excluded from basis lists"
  ]
}
```

---

## Schema 2: Inhomogeneous Deformation (γ-Structure)

### File Pattern

`C_n_gamma.json`

### Top-Level Extensions

The Schema 2 extends Schema 1 with:

```json
{
  ... (all of Schema 1),
  "deformation_parameters": { ... },
  "inhomogeneous_deformation": { ... }
}
```

### `deformation_parameters`

For C(n+1), there are **4n deformation parameters** (gb matrix):

```json
{
  "description": "Inhomogeneous deformation parameters (gb) for C(n+1)",
  "parameter_set": [
    "gb_{a_1^+, b_1^+}", "gb_{a_1^+, b_1^-}",
    "gb_{a_1^-, b_1^+}", "gb_{a_1^-, b_1^-}",
    "gb_{a_1^+, b_2^+}", "gb_{a_1^+, b_2^-}",
    "gb_{a_1^-, b_2^+}", "gb_{a_1^-, b_2^-}",
    "..."
  ],
  "count": 4,
  "n": 1,
  "parity": 1,
  "role": "Coefficients in exchange relations [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ"
}
```

### `inhomogeneous_deformation`

```json
{
  "gamma_structure": [
    {
      "X": "H_1",
      "Y": "E_eps1_del1_pp",
      "gamma_expression": "symbolic formula depending on gb parameters",
      "coeff": "formula in terms of gb"
    }
  ]
}
```

---

## Schema 3: Evaluated Structure

### File Pattern

`C_n_evaluated_<gb_signature>.json`

### Numerical Substitution

Replace all `gb_i` with concrete numerical values (typically ±1) and compute all structure constant coefficients.

---

## Schema 4: Coboundary Structure

### File Pattern

`C_n_coboundary_<gb_signature>.json`

### Contents

Compute the coboundary $(\delta f)_{abc}$ where $f: \mathfrak{g} \to \mathfrak{g}$ is an odd linear map parameterized by coefficients $\phi_{ij}$.

```json
{
  ... (basis and metadata),
  "coboundary_map_f": { ... },
  "coboundary_operator": [
    {
      "X": "...",
      "Y": "...",
      "delta_f": "computed coefficients"
    }
  ]
}
```

---

## Key Differences: C(n+1) vs B(0,n)

| Feature | B(0,n) | C(n+1) |
|---|---|---|
| Fermionic sector | Supplementary $a_0$, $a_0^2 = 1/2$ | Standard pair $a_1^\pm$, CAR $\{a_1^-, a_1^+\} = 1$ |
| Oscillator generators | `supplementary_fermion` key | `fermions` key |
| Odd roots | $\pm\delta_k$ (2n total) | $\pm\varepsilon \pm \delta_k$ (4n total) |
| Even subalgebra | $\mathfrak{sp}(2n)$, dim $2n^2+n$ | $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$, dim $2n^2+n+1$ |
| Cartan elements | $H_k$ for $k=1,...,n$ | $H_k$ for $k=1,...,n+1$ |
| Deformation parameters | 2n (gb parameters) | 4n (gb parameters) |
| Central elements | Not explicitly separated | Top-level `central_elements` key |

---

## Summary

This schema specification provides a complete v5.0 JSON structure for C(n+1) = osp(2|2n) across all four layers (algebra structure, deformation, evaluation, coboundary). It maintains backward compatibility with the B(m,n) base schema while incorporating the necessary mathematical extensions for the fermionic pair and ε-roots.
