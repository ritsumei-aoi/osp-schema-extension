# JSON Schema Specification for $C(n+1) = \mathfrak{osp}(2|2n)$

This document specifies the v5.0 JSON schema extension for $C(n+1) = \mathfrak{osp}(2|2n)$, extending the $B(0,n) = \mathfrak{osp}(1|2n)$ base schema.

---

## 1. Architecture Overview

The representation of $C(n+1)$ structure constants and deformation data is organized into four schema layers:

| Layer | File Pattern | Role / Contents |
|---|---|---|
| **Schema 1** | `C_{n}_structure.json` | Undeformed Lie superalgebra structure: basis, parity, oscillator realizations, structure constants |
| **Schema 2** | `C_{n}_gamma.json` | Symbolic inhomogeneous deformation ($\gamma$-structure, gb matrix) |
| **Schema 3** | `C_{n}_evaluated.json` | Numerically/sign-evaluated structure constants for concrete gb values |
| **Schema 4** | `C_{n}_coboundary.json` | Coboundary reference data $\delta f$ for triviality verification |

Here $n$ denotes the **bosonic rank** ($n=1, 2, 3$ corresponding to $C(2), C(3), C(4)$).

---

## 2. Schema 1: Algebra Structure Specification

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

### Detailed Field Definitions

#### 1. `schema_version`
- Type: `string`
- Value: `"5.0"`

#### 2. `algebra`
Specifies the algebra identification, ranks, and dimension formulas:
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
    "formulas": {
      "even": "2n^2 + n + 1",
      "odd": "4n",
      "total": "2n^2 + 5n + 1"
    }
  }
}
```

#### 3. `central_elements`
A mandatory top-level key defining the central extension generators:
```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotency": "kappa^2 = 0",
    "description": "Odd central element parameterizing the inhomogeneous deformation"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central element identified with scalar identity 1"
  }
}
```

#### 4. `oscillator_generators`
Specifies standard fermionic pairs and bosonic oscillators:
```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic CAR pair a_1^±"
  },
  "bosons": {
    "n": 1,
    "count": 2,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

#### 5. `oscillator_relations`
Defines the algebraic relations obeyed by the oscillators:
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for fermionic pair",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "nilpotency": "(a_1^+)^2 = (a_1^-)^2 = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations (CCR) for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed)"
  }
}
```

#### 6. `basis`
Lists the ordered even and odd basis generators:
```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p", "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp",
    "E_eps1_del1_pm",
    "E_eps1_del1_mp",
    "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]"
}
```

#### 7. `parity`
Mapping of each basis generator string to its $\mathbb{Z}_2$-grade ($0$ for even, $1$ for odd).

#### 8. `generator_realization`
Oscillator expansions in normal-ordered / PBW-ordered words:
```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ...",
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

#### 9. `structure_constants`
List of all non-zero graded Lie brackets:
$$[X, Y\} = \sum_Z c_{XY}^Z Z$$
stored in canonical order ($X \le Y$ in PBW order):
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

#### 10. `metadata`
Provenance tracking metadata:
```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "2026-10-04",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "docs/math/Cn1_definition.md"
  ]
}
```

---

## 3. Backward Compatibility with $B(m,n)$ Schema

| Field / Feature | $B(0,n)$ (Base) | $C(n+1) = \mathfrak{osp}(2|2n)$ (Extension) | Compatibility Note |
|---|---|---|---|
| `algebra.family` | `"B"` | `"C"` | Differentiates family cleanly |
| `algebra.m` | `0` | `1` | Indicates fermionic rank ($2m$ fermions) |
| Fermions | `supplementary_fermion` ($a_0$) | `fermions` ($a_1^+, a_1^-$) | Standardized key replaces single auxiliary fermion |
| Central elements | Documented inline | `central_elements` top-level key | Clean uniform access for deformation algorithms |
| Odd generator names | `E_del{k}_p`, `E_del{k}_m` | `E_eps1_del{k}_{sign_eps}{sign_del}` | Clear root-vector naming indicating both $\varepsilon$ and $\delta_k$ |
| Sign rule | `"graded"` | `"graded"` | Identical superalgebra bracket convention $[X, Y\} = -(-1)^{p(X)p(Y)}[Y, X\}$ |

---

## 4. File Naming Conventions
- Layer 1: `data/C_{n}_structure.json`
- Layer 2: `data/C_{n}_gamma.json`
- Layer 3: `data/C_{n}_evaluated.json`
- Layer 4: `data/C_{n}_coboundary.json`
Where $n \in \{1, 2, 3\}$.
