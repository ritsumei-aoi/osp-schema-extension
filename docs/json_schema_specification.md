# JSON Schema Specification for C(n+1)

This document specifies the schema fields used to define $C(n+1) = \mathfrak{osp}(2|2n)$ structure data, extending the baseline $B(0,n)$ schema (v5.0) for the $C$ family.

## 1. File Naming Conventions
Files for $C(n+1)$ are named according to the bosonic rank $n$:
- **Schema 1 (Structure)**: `C_{n}_structure.json` (e.g., C(2) uses `n=1` -> `C_1_structure.json`)
- **Schema 2 (Gamma)**: `C_{n}_gamma.json`
- **Schema 3 (Evaluated)**: `C_{n}_evaluated_<gb>.json`
- **Schema 4 (Coboundary)**: `C_{n}_coboundary_<gb>.json`

## 2. Top-Level Keys for C(n+1)
The schema structurally mirrors $B(0,n)$ with key differences in the field values for `algebra`, `oscillator_generators`, `oscillator_relations`, and the introduction of a new `central_elements` key.

### 2.1 `algebra`
```json
{
  "family": "C",
  "m": 1,
  "n": 1,  // The bosonic rank, example for C(2)
  "cartan_type": "C(n+1)",
  "alternative_notation": {
    "osp": "osp(2m|2n)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "even": "2n^2 + n + 1",
    "odd": "4n"
  }
}
```

### 2.2 `oscillator_generators`
Replaces `supplementary_fermion` with a standard fermionic pair:
```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair satisfying CAR"
  },
  "bosons": {
    "n": 1, // dynamically set to rank n
    "count": 2, // 2n
    "labels": ["b_1_p", "b_1_m"],
    "description": "Standard bosonic pairs satisfying CCR"
  }
}
```

### 2.3 `oscillator_relations`
Describes the CAR, CCR, and mixed commutators:
```json
{
  "fermionic_anticommutators": {
    "description": "Standard Canonical Anticommutation Relations (CAR) for fermions",
    "relations": {
      "same_type": "{a_i^±, a_i^±} = 0",
      "conjugate_pair": "{a_i^-, a_i^+} = 1"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical Commutation Relations (CCR) for bosons",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0",
      "conjugate_pair": "[b_i^-, b_j^+] = \delta_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_j^±] = 0"
  }
}
```

### 2.4 `central_elements`
Added as a new top-level key explicitly denoting the even and odd central elements.
```json
{
  "kappa": {
    "parity": 1,
    "description": "Odd central extension element (\kappa)"
  },
  "K": {
    "parity": 0,
    "description": "Even central extension element (K), typically identified with the scalar 1 in representations"
  }
}
```

## Backward Compatibility with B(m,n) Schema
The addition of `central_elements` as a top-level key avoids breaking existing parsing loops that scan `basis` and `oscillator_generators`. Programs reading $B(0,n)$ schemas can read the $C(n+1)$ schema and simply ignore `central_elements` if not supported, or can be trivially updated to handle the `fermions` vs `supplementary_fermion` distinction in `oscillator_generators` based on the `algebra.family` key.
