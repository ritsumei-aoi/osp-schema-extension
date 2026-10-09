# JSON Schema Specification for C(n+1) = osp(2|2n)

This document outlines the v5.0 JSON schema extensions designed for C(n+1) to support structure constants and inhomogeneous deformations.

## File Naming Convention
The data files use the pattern `C_{n}_<type>.json`, where `n` corresponds to the bosonic rank of the algebra.
- `C_{n}_structure.json`: Algebra structure
- `C_{n}_gamma.json`: Inhomogeneous deformation (γ-structure)
- `C_{n}_evaluated_<gb>.json`: Numerically evaluated structure constants
- `C_{n}_coboundary_<gb>.json`: Coboundary data
*(For example, C(2) = osp(2|2) uses `n=1`, hence `C_1_structure.json`.)*

## Schema 1: Algebra Structure fields

### `algebra`
```json
{
  "family": "C",
  "m": 1,
  "n": 1,
  "cartan_type": "C(2)",
  "dimension_formula": "osp(2m|2n)",
  "dimension": {
    "total": 8,
    "even": 4,
    "odd": 4
  }
}
```
*Note: For a general `n`, `even` = 2n² + n + 1, `odd` = 4n, `total` = 2n² + 5n + 1.*

### `oscillator_generators`
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^±"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

### `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermions",
    "relation": "{a_1^-, a_1^+} = 1"
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = \\delta_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^\\pm] = 0"
  }
}
```

### `central_elements`
(This is a new top-level key)
```json
{
  "kappa": {
    "parity": 1,
    "description": "Odd central element for inhomogeneous deformation, \\kappa^2 = 0"
  },
  "K": {
    "parity": 0,
    "description": "Even central identity element (K = 1)"
  }
}
```

## Compatibility with B(m,n) Schema
- The PBW ordering convention remains structured as `κ < [odd] < [even]`, compatible with B(0,n) processing logic.
- The `generator_realization`, `basis`, and `parity` keys retain the exact same hierarchical structures as B(0,n).
- The transition from `supplementary_fermion` to `fermions` in `oscillator_generators` requires generators to substitute `a_0` logic with generic CAR fermionic logic using `a_1_p` / `a_1_m`.
