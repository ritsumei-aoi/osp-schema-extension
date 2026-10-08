# JSON Schema Specification for C(n+1) v5.0

This document specifies the v5.0 JSON schema used for C(n+1) = osp(2|2n) structure constants. It is an extension of the existing B(0,n) schema to maintain backward compatibility where possible.

## 1. File Naming Convention
The JSON files for C(n+1) must be named `C_{n}_structure.json`, where `n` is the bosonic rank.
Examples:
- C(2) = osp(2|2) -> `C_1_structure.json`
- C(3) = osp(2|4) -> `C_2_structure.json`
- C(4) = osp(2|6) -> `C_3_structure.json`

## 2. Top-Level Keys
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

## 3. Detailed Field Definitions for C(n+1)

### `algebra`
Explicitly includes `"m": 1` and `"family": "C"`.
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
*Dimension formulas*: even = `2n^2 + n + 1`, odd = `4n`, total = `2n^2 + 5n + 1`.

### `oscillator_generators`
Removes the `supplementary_fermion` key from the B(0,n) schema and replaces it with a `fermions` key.
```json
{
  "fermions": {
    "count": 2,
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
Describes the CAR for the standard fermionic pair.
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermionic oscillators",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^±, a_1^±} = 0"
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

### `central_elements`
A new top-level key explicitly capturing the deformation framework components.
```json
{
  "kappa": {
    "parity": 1,
    "relation": "kappa^2 = 0",
    "description": "Odd nilpotent central element for inhomogeneous deformation"
  },
  "K": {
    "parity": 0,
    "relation": "K = 1",
    "description": "Even central element (identity)"
  }
}
```

## 4. Compatibility with B(m,n) Schema
- The structure of basis, parity, and generator realization lists remains identical.
- Tools parsing B(m,n) expect the `supplementary_fermion` key, but tools parsing C(n+1) must read `fermions` under `oscillator_generators`.
- The PBW ordering convention remains `κ < [odd] < [even]`.
- The new `central_elements` key explicitly stores nilpotent parameter definitions to unify future extensions.
