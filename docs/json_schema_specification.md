# JSON Schema Specification for C(n+1) v5.0

This document defines the schema for the C(n+1) = osp(2|2n) structure constants, extending the B(0,n) v5.0 schema.

## 1. File Naming Convention
The JSON schema files will be named `C_{n}_structure.json`, where `n` is the bosonic rank.
For example:
- C(2) (n=1): `C_1_structure.json`
- C(3) (n=2): `C_2_structure.json`
- C(4) (n=3): `C_3_structure.json`

## 2. Schema Fields

### `schema_version`
```json
"schema_version": "5.0"
```

### `algebra`
Specifies the algebra properties. For C(n+1), we use `"family": "C"` and `"m": 1`.
```json
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
    "odd": 4,
    "formulas": {
      "even": "2n^2 + n + 1",
      "odd": "4n"
    }
  }
}
```

### `oscillator_generators`
Defines the oscillators used in the realization. For C(n+1), we replace the supplementary fermion with a standard fermionic pair.
```json
"oscillator_generators": {
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^±"
  },
  "bosons": {
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

### `oscillator_relations`
Defines the CAR for fermions and CCR for bosons.
```json
"oscillator_relations": {
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations",
    "relation": "{a_1^-, a_1^+} = 1"
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

### `central_elements`
A new top-level key for C(n+1).
```json
"central_elements": {
  "kappa": {
    "parity": 1,
    "description": "Odd central element"
  },
  "K": {
    "parity": 0,
    "description": "Even central element identified with scalar 1"
  }
}
```

### `basis`, `parity`, `generator_realization`, `structure_constants`
These fields follow the definitions and naming conventions finalized in Issue I01, maintaining compatibility with the B(m,n) schema's structure format.
