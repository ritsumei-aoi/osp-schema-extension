# JSON Schema Specification for C(n+1) = osp(2|2n) (v5.0 Extension)

## Overview

This document specifies the v5.0 JSON schema extension for $C(n+1) = \mathfrak{osp}(2|2n)$, generalizing the $B(0,n) = \mathfrak{osp}(1|2n)$ base schema to standard CAR fermionic oscillator pairs.

### 4-Layer Schema Architecture

The data hierarchy consists of 4 computational layers:

| Layer | File Pattern | Role / Contents |
|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | Undeformed Lie superalgebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `data/C_{n}_gamma.json` | Inhomogeneous deformation (symbolic $\gamma$ 2-cocycle parameterized by $gb$ matrix) |
| Schema 3 | `data/C_{n}_evaluated.json` | Numerically evaluated deformed structure constants for concrete $gb$ assignments |
| Schema 4 | `data/C_{n}_coboundary.json` | Coboundary reference data $(\delta f)(X, Y)$ for odd linear maps $f: \mathfrak{g} \to \mathfrak{g}$ |

*File Naming Convention*: `C_{n}_<layer>.json`, where `n` denotes the bosonic rank $n \ge 1$. For example:
- $C(2) = \mathfrak{osp}(2|2)$ uses `n=1`: `C_1_structure.json`
- $C(3) = \mathfrak{osp}(2|4)$ uses `n=2`: `C_2_structure.json`
- $C(4) = \mathfrak{osp}(2|6)$ uses `n=3`: `C_3_structure.json`

---

## Schema 1: Base Lie Superalgebra Structure

### 1. Top-Level Keys
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

### 2. Field Specifications

#### 2.1 `schema_version`
- Type: `string`
- Value: `"5.0"`

#### 2.2 `algebra`
Specifies family, rank parameters, and dimension formulas:
```json
{
  "family": "C",
  "m": 1,
  "n": 1,
  "cartan_type": "C(2)",
  "alternative_notation": {
    "osp": "osp(2|2)",
    "dimension_formula": {
      "even": "2*n^2 + n + 1",
      "odd": "4*n",
      "total": "2*n^2 + 5*n + 1"
    }
  },
  "dimension": {
    "total": 8,
    "even": 4,
    "odd": 4
  }
}
```

#### 2.3 `central_elements` (Top-Level Key)
Specifies central elements of the extended oscillator algebra:
```json
{
  "kappa": {
    "parity": 1,
    "nilpotent_order": 2,
    "relation": "kappa^2 = 0",
    "description": "Odd central element governing inhomogeneous deformation"
  },
  "K": {
    "parity": 0,
    "relation": "K = 1",
    "description": "Even central identity element"
  }
}
```

#### 2.4 `oscillator_generators`
Divided into `"fermions"` and `"bosons"`:
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic CAR pair a_1^±"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

#### 2.5 `oscillator_relations`
Explicit CAR and CCR relations:
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
    "boson_fermion": "[b_i^±, a_1^σ] = 0 for all i, σ ∈ {+,-}"
  }
}
```

#### 2.6 `basis`
Contains ordered lists of even and odd basis generators under PBW Option A:
```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp",
    "E_eps1_del1_pm",
    "E_eps1_del1_mp",
    "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd: Polarity-First] < [even: Cartans, pos roots, neg roots, mixed roots]"
}
```

#### 2.7 `parity`
Dictionary mapping generator name to integer $p \in \{0, 1\}$.

#### 2.8 `generator_realization`
Each generator is expressed in PBW standard form as a sum of normal-ordered oscillator words with exact rational coefficients:
```json
{
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ...",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    }
  }
}
```

#### 2.9 `structure_constants`
List of non-zero graded Lie superalgebra brackets $[X, Y\} = \sum_Z c_{XY}^Z Z$:
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
where $[X, Y\} = XY - (-1)^{p(X)p(Y)} YX$.

#### 2.10 `metadata`
Provenance information: generator script path, generation date, references.

---

## Comparison and Compatibility with B(0,n)

| Field | $B(0,n)$ (v5.0) | $C(n+1)$ (v5.0 Extension) | Compatibility Notes |
|---|---|---|---|
| `algebra.family` | `"B"` | `"C"` | Discriminator for root and Cartan structure |
| `algebra.m` | `0` | `1` | Indicates 1 fermionic CAR pair |
| `algebra.cartan_type` | `"B(0,n)"` | `"C(n+1)"` | Follows Frappat notation |
| `oscillator_generators` | `supplementary_fermion` ($a_0$) + `bosons` | `fermions` ($a_1^\pm$) + `bosons` | Supplementary fermion eliminated; standard CAR pair adopted |
| `central_elements` | Embedded or implicit | Explicit top-level key | Contains odd $\kappa$ and even $K=1$ |
| `basis.odd` | `E_del{k}_p/m` ($2n$ total) | `E_eps1_del{k}_{pp,pm,mp,mm}` ($4n$ total) | Quadruplet of $\pm\varepsilon \pm \delta_k$ roots |
| `generator_realization` | Uses $a_0$ with $a_0^2 = 1/2$ | Uses $a_1^\pm$ with $\{a_1^-, a_1^+\} = 1$ | Strict PBW normal ordering |
