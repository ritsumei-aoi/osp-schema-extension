# C(n+1) = osp(2|2n) v5.0 JSON Schema Specification

This document provides the complete v5.0 JSON schema specification for $C(n+1) = \mathfrak{osp}(2|2n)$ structure constants, basis, and deformation data. It extends the $B(0,n)$ v5.0 schema while maintaining pipeline interoperability.

---

## 1. Architecture Overview: 4-Layer Schema

The data artifacts for $C(n+1)$ are organized into 4 layers:

| Layer | File Pattern | Description |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Undeformed Lie superalgebra: basis, parity, oscillator generators, relations, central elements, realizations, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation 2-cocycle $\gamma(X,Y)$ with algebraic gb parameters |
| Schema 3 | `C_{n}_evaluated_<gb>.json` | Numerical evaluation of deformed brackets for specific gb configurations |
| Schema 4 | `C_{n}_coboundary_<gb>.json` | Triviality verification: linear map $f$ and coboundary $\delta f$ matching |

Here, $n$ designates the **bosonic rank** ($n \ge 1$):
- $n=1 \implies C(2) = \mathfrak{osp}(2|2)$ (file: `C_1_structure.json`)
- $n=2 \implies C(3) = \mathfrak{osp}(2|4)$ (file: `C_2_structure.json`)
- $n=3 \implies C(4) = \mathfrak{osp}(2|6)$ (file: `C_3_structure.json`)

---

## 2. Schema 1: Undeformed Structure (`C_{n}_structure.json`)

### 2.1 Top-Level Keys
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

### 2.2 `schema_version`
String constant: `"5.0"`.

### 2.3 `algebra` Key
Defines algebra identity, Cartan classification, and dimension metrics.
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
    "even": "2*n^2 + n + 1",
    "odd": "4*n",
    "total": "2*n^2 + 5*n + 1"
  },
  "dimension": {
    "total": 8,
    "even": 4,
    "odd": 4
  }
}
```

### 2.4 `oscillator_generators` Key
Defines standard CAR fermions and CCR bosons:
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^± satisfying CAR"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n satisfying CCR"
  }
}
```

### 2.5 `oscillator_relations` Key
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for fermionic oscillators",
    "relations": {
      "same_type": "{a_1^±, a_1^±} = 0",
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
    "boson_fermion": "[b_i^±, a_1^σ] = 0 (undeformed)"
  }
}
```

### 2.6 `central_elements` Key (Top-Level)
Central elements explicitly declared at top level:
```json
{
  "kappa": {
    "parity": 1,
    "nilpotent": true,
    "relation": "kappa^2 = 0",
    "description": "Odd nilpotent central extension parameter mediating inhomogeneous deformation"
  },
  "K": {
    "parity": 0,
    "scalar_value": 1,
    "description": "Even central element normalized to identity scalar"
  }
}
```

### 2.7 `basis` Key
Specifies the ordered basis of $\mathfrak{g} = C(n+1)$:
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
  "ordering_convention": "PBW: κ < [odd] < [even] (K = 1 is excluded from basis)"
}
```

### 2.8 `parity` Key
Maps every basis element symbol to its $\mathbb{Z}_2$-degree: `0` for even, `1` for odd.
```json
{
  "H_1": 0,
  "H_2": 0,
  "E_2del1_p": 0,
  "E_2del1_m": 0,
  "E_eps1_del1_pp": 1,
  "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1,
  "E_eps1_del1_mm": 1
}
```

### 2.9 `generator_realization` Key
Contains PBW normal-ordered oscillator words with rational coefficients:
```json
{
  "description": "Normal-ordered oscillator words with PBW ordering",
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
    "E_2del1_p": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "(b_1^+)^2",
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

### 2.10 `structure_constants` Key
List of non-zero graded brackets $[X, Y\} = \sum_Z c_{XY}^Z Z$:
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

### 2.11 `metadata` Key
```json
{
  "generated_by": "generate_c_structure.py",
  "generation_date": "2026-10-05",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## 3. Comparison and Compatibility with B(0,n) Schema v5.0

| Feature | $B(0,n)$ (v5.0 Base) | $C(n+1)$ (Extended v5.0) | Backward Compatibility / Transition |
|---|---|---|---|
| `family` | `"B"` | `"C"` | Standard family discriminator |
| `m` | `0` | `1` | Integer parameter for fermionic rank |
| Dimension | even: $2n^2+n$, odd: $2n$ | even: $2n^2+n+1$, odd: $4n$ | Parameterized dimension checks |
| Fermions | `supplementary_fermion` (`a_0`, $a_0^2=1/2$) | `fermions` (`a_1_p`, `a_1_m`, CAR) | Replaced with standard CAR pair |
| `central_elements` | Embedded or implicit | **Top-level key**: `kappa` (p=1), `K` (p=0) | Unified explicit declaration |
| Odd Generators | `E_del{k}_p`, `E_del{k}_m` | `E_eps1_del{k}_{pp,pm,mp,mm}` | Expanded from $2n$ to $4n$ root labels |
| Cartan Structure | $H_1, \dots, H_n$ | $H_1, \dots, H_{n+1}$ | Dimension grows to $n+1$ due to $\mathfrak{so}(2)$ factor |
| PBW Convention | $\kappa < [\text{odd}] < [\text{even}]$ | $\kappa < [\text{odd}] < [\text{even}]$ | Identical ordering philosophy |
