# JSON Schema Specification for C(n+1) Extension

This document specifies the updated schema fields for the C(n+1) = osp(2|2n) extension.
It extends the base B(0,n) v5.0 schema with specific modifications for the C(n+1) algebra.

## File Naming Conventions
As the bosonic rank is `n`, the schema files will be named according to `n`. For example:
- **C(2) (n=1):** `C_1_structure.json`
- **C(3) (n=2):** `C_2_structure.json`
- **C(4) (n=3):** `C_3_structure.json`

Other layers will follow the same pattern (e.g., `C_{n}_gamma.json`, `C_{n}_evaluated_<gb>.json`, `C_{n}_coboundary_<gb>.json`).

## 1. `algebra` field
```json
{
  "family": "C",
  "m": 1,
  "n": "{n}",
  "cartan_type": "C({n+1})",
  "alternative_notation": {
    "osp": "osp(2|{2n})",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": "{2n^2 + 5n + 1}",
    "even": "{2n^2 + n + 1}",
    "odd": "{4n}"
  }
}
```

## 2. `oscillator_generators` field
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^± satisfying CAR."
  },
  "bosons": {
    "count": "{2n}",
    "n": "{n}",
    "labels": ["b_1_p", "b_1_m", "...", "b_{n}_p", "b_{n}_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

## 3. `oscillator_relations` field
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for the standard fermionic pair.",
    "relations": {
      "same_type": "{a_1^±, a_1^±} = 0",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

## 4. `central_elements` field (Top-level key)
```json
{
  "kappa": {
    "parity": 1,
    "relation": "kappa^2 = 0",
    "description": "Formal odd central nilpotent element defining the inhomogeneous deformation."
  },
  "K": {
    "parity": 0,
    "relation": "K = 1",
    "description": "Even central element identified with the scalar identity."
  }
}
```
