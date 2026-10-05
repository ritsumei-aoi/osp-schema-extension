# C(n+1) JSON Schema Specification v5.0

This document specifies the v5.0 JSON schema for $C(n+1) = \mathfrak{osp}(2|2n)$ structure constants, deformations, and coboundary analysis. It extends the $B(0,n)$ v5.0 schema specification (`docs/math/B0n_schema_v5.md`).

---

## 1. File Naming Conventions

File naming for $C(n+1)$ is indexed by the bosonic rank $n$ (where $C(n+1) = \mathfrak{osp}(2|2n)$):

| Rank $n$ | Algebra | Schema 1 (Structure) | Schema 2 (Deformation) | Schema 3 (Evaluated) | Schema 4 (Coboundary) |
|---|---|---|---|---|---|
| $n=1$ | $C(2) = \mathfrak{osp}(2\|2)$ | `C_1_structure.json` | `C_1_gamma.json` | `C_1_evaluated_<gb>.json` | `C_1_coboundary_<gb>.json` |
| $n=2$ | $C(3) = \mathfrak{osp}(2\|4)$ | `C_2_structure.json` | `C_2_gamma.json` | `C_2_evaluated_<gb>.json` | `C_2_coboundary_<gb>.json` |
| $n=3$ | $C(4) = \mathfrak{osp}(2\|6)$ | `C_3_structure.json` | `C_3_gamma.json` | `C_3_evaluated_<gb>.json` | `C_3_coboundary_<gb>.json` |

---

## 2. Schema 1: Algebra Structure Specification

Top-level JSON architecture:
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

### 2.1 `algebra` Key
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
*Note*: General superdimension formulas: even = $2n^2 + n + 1$, odd = $4n$, total = $2n^2 + 5n + 1$.

### 2.2 `oscillator_generators` Key
Unlike $B(0,n)$ which relies on an auxiliary fermion $a_0$, $C(n+1)$ utilizes a standard CAR fermionic pair:
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^± with CAR {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

### 2.3 `oscillator_relations` Key
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for fermionic oscillators",
    "relations": {
      "same_type": "{a_i^±, a_j^±} = 0 for all i, j",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations (CCR) for bosonic oscillators",
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

### 2.4 `central_elements` Key (Top-level)
```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotent": true,
    "description": "Odd central element parametrizing the 2-cocycle deformation (kappa^2 = 0)"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central element identified with scalar identity 1"
  }
}
```

### 2.5 `basis` Key
Order convention: Option A PBW ordering `κ < [odd basis] < [even basis]`.
```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p", "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd] < [even]"
}
```

### 2.6 `parity` Key
Mapping from generator labels to parity values ($0$ for even, $1$ for odd):
```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

### 2.7 `generator_realization` Key
```json
{
  "description": "Standard form with PBW ordering: a_1_p, a_1_m, b_1_p, b_1_m",
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
      "parity": 0
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

### 2.8 `structure_constants` Key
List of non-zero Lie superalgebra brackets $[X, Y\} = \sum Z$:
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

---

## 3. Schema Compatibility & Migration

- **Schema Version**: Retained at `"5.0"`.
- **Structural Differences from B(0,n)**:
  - `supplementary_fermion` in `oscillator_generators` replaced by `fermions` key.
  - CAR replaces $a_0^2 = 1/2$ relation in `oscillator_relations`.
  - `central_elements` added as explicit top-level key.
  - Odd basis generators replaced by $\pm\varepsilon \pm \delta_k$ family (labels `E_eps1_del{k}_{pp|pm|mp|mm}`).
