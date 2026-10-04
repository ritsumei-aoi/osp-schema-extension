# C(n+1) v5.0 JSON Schema Specification

This document specifies the v5.0 JSON schema used for C(n+1) = osp(2|2n)
structure constants. It extends the base B(0,n) schema to accommodate the standard fermionic pair and other changes.

---

## Overview: 4-Layer Schema Architecture

The JSON data for each algebra is organized into 4 layers of increasing
computational depth:

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_{n}_evaluated_<gb>.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_{n}_coboundary_<gb>.json` | Coboundary data for triviality verification |

**File Naming**: `C_{n}_structure.json`, where `n` is the bosonic rank (e.g., C(2) uses `n=1`).

---

## Schema 1: Algebra Structure

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
  }
}
```

**Dimension formulas** (C(n+1)): even = $2n^2+n+1$, odd = $4n$, total = $2n^2+5n+1$.

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^±"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermionic pair (CAR)",
    "relation": "{a_1^-, a_1^+} = 1, {a_1^±, a_1^±} = 0"
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators (CCR)",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

### `central_elements`

```json
{
  "kappa": {
    "parity": 1,
    "relation": "kappa^2 = 0",
    "description": "Odd nilpotent central extension element"
  },
  "K": {
    "parity": 0,
    "description": "Even central identity element (usually set to 1)"
  }
}
```

### `basis`

PBW ordering (C(n+1) convention):
`κ < [odd] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]`
where root ordering is $\varepsilon > \delta_1 > \dots > \delta_n > 0$.

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
    "E_eps_del1_pp", "E_eps_del1_pm", "E_eps_del1_mp", "E_eps_del1_mm",
    "E_eps_del2_pp", "E_eps_del2_pm", "E_eps_del2_mp", "E_eps_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
}
```

### `parity`

```json
{
  "H_1": 0, "H_2": 0, "H_3": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_2del2_p": 0, "E_2del2_m": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_mm": 0,
  "E_del1_del2_pm": 0, "E_del1_del2_mp": 0,
  "E_eps_del1_pp": 1, "E_eps_del1_pm": 1,
  "E_eps_del1_mp": 1, "E_eps_del1_mm": 1,
  "E_eps_del2_pp": 1, "E_eps_del2_pm": 1,
  "E_eps_del2_mp": 1, "E_eps_del2_mm": 1
}
```

### `generator_realization`

Each generator is expressed as a sum of oscillator words with rational coefficients.

```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "E_eps_del1_pm": {
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

Non-zero graded brackets $[X, Y\}$ stored as a list:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps_del1_pp",
    "Z": "E_eps_del1_pp",
    "coeff": "1",
    "sign_rule": "graded"
  }
]
```

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```
