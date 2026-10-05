# JSON Schema Specification for C(n+1) = osp(2|2n)

This document specifies the v5.0 JSON schema for C(n+1) algebra structure constants,
extending the B(0,n) specification to the superalgebra family C.

**Task scope**: This specification is complete for Schema 1 (algebra structure) and
serves as the reference for all subsequent schemas (Schemas 2–4).

---

## Overview: Extended 4-Layer Architecture

The schema maintains consistency with the B(0,n) pattern:

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_n_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_n_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_n_evaluated_<gb>.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_n_coboundary_<gb>.json` | Coboundary data for triviality verification |

**File naming**: `C_n_structure.json`, where `n` is the bosonic rank (so C(n+1) has rank n).

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
  "n": <n>,
  "cartan_type": "C(n+1)",
  "alternative_notation": {
    "osp": "osp(2|2n)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": <2*n^2 + 5*n + 1>,
    "even": <2*n^2 + n + 1>,
    "odd": <4*n>
  }
}
```

**Dimension Examples**:

| $n$ | C(n+1) | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) | 4 | 4 | 8 |
| 2 | C(3) | 11 | 8 | 19 |
| 3 | C(4) | 22 | 12 | 34 |

**Formulas** (C(n+1)): even = $2n^2 + n + 1$, odd = $4n$, total = $2n^2 + 5n + 1$.

### `oscillator_generators`

**Key change from B(0,n)**: Replace `supplementary_fermion` with standard `fermions` pair.

```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "relation": "{a_1^-, a_1^+} = 1",
    "description": "Standard fermionic pair under canonical anticommutation relations (CAR)"
  },
  "bosons": {
    "count": <2*n>,
    "n": <n>,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m", ..., "b_n_p", "b_n_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

**Example for C(2)** (n=1):
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "relation": "{a_1^-, a_1^+} = 1",
    "description": "Standard fermionic pair"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "One pair of bosonic oscillators"
  }
}
```

### `oscillator_relations`

**Key change from B(0,n)**: Replace `supplementary_fermion_relation` with `standard_fermion_anticommutators`.

```json
{
  "standard_fermion_anticommutators": {
    "description": "CAR for fermionic pair",
    "relations": {
      "standard_car": "{a_1^-, a_1^+} = 1",
      "self": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "CCR for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^+, b_j^+] = 0, [b_i^-, b_j^-] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

### `central_elements`

**New key for C(n+1)** (not present in B(0,n) schema):

```json
{
  "central_elements": {
    "kappa": {
      "symbol": "κ",
      "parity": 1,
      "nilpotency": "κ² = 0",
      "description": "Odd central element; appears in 2-cocycle deformation"
    },
    "K": {
      "symbol": "K",
      "parity": 0,
      "description": "Even central identity (identified with scalar 1 in realization)"
    }
  }
}
```

### `basis`

PBW ordering uses fermionic-priority convention (from Issue I01):

```
K < κ < [odd: E_eps_del{k}_{pp/pm/mp/mm}] < [even: H_i, E_2del{k}_{p/m}, E_del{i}_del{j}_{pp/mm/pm/mp}]
```

**Example for C(2)** (n=1):
```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del1_pm",
    "E_eps_del1_mp", "E_eps_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd generators] < [even generators]"
}
```

**Example for C(3)** (n=2):
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
  "ordering_convention": "PBW: κ < [odd: ε±δ_k] < [even: H, ±2δ_k, ±(δ_i±δ_j)]"
}
```

### `parity`

All generators are assigned parity 0 (even) or 1 (odd).

**Example for C(2)**:
```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps_del1_pp": 1, "E_eps_del1_pm": 1,
  "E_eps_del1_mp": 1, "E_eps_del1_mm": 1
}
```

### `generator_realization`

Each generator is realized as a sum of oscillator words with rational coefficients.

**Example for C(2)**:
```json
{
  "description": "Oscillator realization in standard PBW form",
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
      "note": "Terminal Cartan; includes constant term"
    },
    "E_2del1_p": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_p"], "coeff": "1/2"}
      ],
      "frappat_form": "(1/2)(b_1^+)^2",
      "parity": 0
    },
    "E_2del1_m": {
      "standard_form": [
        {"words": ["b_1_m", "b_1_m"], "coeff": "1/2"}
      ],
      "frappat_form": "(1/2)(b_1^-)^2",
      "parity": 0
    },
    "E_eps_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    },
    "E_eps_del1_pm": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^-",
      "parity": 1
    },
    "E_eps_del1_mp": {
      "standard_form": [
        {"words": ["a_1_m", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_1^+",
      "parity": 1
    },
    "E_eps_del1_mm": {
      "standard_form": [
        {"words": ["a_1_m", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_1^-",
      "parity": 1
    }
  }
}
```

### `structure_constants`

Non-zero graded superalgebra brackets $[X, Y\}$ (with graded sign rule) are stored as a list:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps_del1_pp",
    "Z": "E_eps_del1_pp",
    "coeff": "1",
    "sign_rule": "graded"
  },
  ...
]
```

**Computation rule**: For fermionic pair $a_1^\pm$, use:
- $\{a_1^-, a_1^+\} = 1$ (anticommutator relation)
- $[b_i^{\pm}, b_j^{\mp}] = \delta_{ij}$ (commutator relation)
- Graded bracket: $[X, Y\} = XY - (-1)^{p(X)p(Y)} YX$

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017), arXiv:1612.09400",
    "Aoi (2026), docs/math/Cn1_definition.md"
  ]
}
```

---

## Backward Compatibility: B(m,n) vs. C(n+1)

| Schema aspect | B(0,n) | C(n+1) | Compatibility |
|---|---|---|---|
| `algebra.family` | "B" | "C" | Distinct; use to branch parsing |
| `algebra.m` | 0 | 1 | Part of family definition |
| `oscillator_generators.supplementary_fermion` | Present | Removed | C uses standard pair |
| `oscillator_generators.fermions` | Absent | Present | New for C |
| `oscillator_relations` keys | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | Different relations |
| `central_elements` | Not listed | Explicit key | C includes formal extension |
| Odd generator labels | `E_del{k}_{p,m}` | `E_eps_del{k}_{pp,pm,mp,mm}` | 4× expansion of odd roots |

---

## Example: Complete C(2) Schema (Skeleton)

```json
{
  "schema_version": "5.0",
  "algebra": {
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
  },
  "oscillator_generators": {
    "fermions": {
      "count": 2,
      "m": 1,
      "labels": ["a_1_p", "a_1_m"],
      "parity": 1,
      "relation": "{a_1^-, a_1^+} = 1"
    },
    "bosons": {
      "count": 2,
      "n": 1,
      "labels": ["b_1_p", "b_1_m"]
    }
  },
  "oscillator_relations": {
    "standard_fermion_anticommutators": {
      "relations": {
        "standard_car": "{a_1^-, a_1^+} = 1",
        "self": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0"
      }
    },
    "bosonic_commutators": {
      "relations": {
        "same_type": "[b_1^+, b_1^+] = [b_1^-, b_1^-] = 0",
        "conjugate_pair": "[b_1^-, b_1^+] = 1"
      }
    },
    "mixed_commutators": {
      "boson_fermion": "[b_1^±, a_1^±] = 0"
    }
  },
  "central_elements": {
    "kappa": {
      "symbol": "κ",
      "parity": 1,
      "nilpotency": "κ² = 0"
    },
    "K": {
      "symbol": "K",
      "parity": 0
    }
  },
  "basis": {
    "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
    "odd": ["E_eps_del1_pp", "E_eps_del1_pm", "E_eps_del1_mp", "E_eps_del1_mm"],
    "ordering_convention": "PBW: κ < [odd] < [even]"
  },
  "parity": { ... },
  "generator_realization": { ... },
  "structure_constants": [ ... ],
  "metadata": { ... }
}
```

---

## Schemas 2–4 (Deformation and Triviality)

### Schema 2: `C_n_gamma.json` (Inhomogeneous Deformation)

Extends Schema 1 with a 2-cocycle $\gamma$ that modifies the bracket structure.

**Key addition**: `gamma_structure` containing deformation parameters indexed by generator pairs.

### Schema 3: `C_n_evaluated_<gb>.json` (Numerical Evaluation)

Computes structure constants for specific values of deformation parameters $\mathrm{gb}_j$.

### Schema 4: `C_n_coboundary_<gb>.json` (Triviality Verification)

Stores coboundary data and verification flags for the triviality condition.

---

## Notes for Implementers

1. **Superalgebra grading**: All computations use the graded Lie bracket $[X, Y\} = XY - (-1)^{p(X)p(Y)}YX$.
2. **Oscillator ordering**: Standard PBW ordering with fermionic-priority convention.
3. **Central extension**: The formal symbols $\kappa$ (odd) and $K$ (even) appear in Schema 1 but do not represent actual basis elements in typical applications.
4. **Structure constant generation**: Use the commutator/anticommutator relations to compute all brackets systematically.
