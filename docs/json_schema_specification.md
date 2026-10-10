# JSON Schema Specification v5.0 (C(n+1) Extension)

This document specifies the schema structure for $C(n+1)$ in v5.0, focusing on the differences from the base B(0,n) schema.

## File Naming Convention
Files for C(n+1) are named using the bosonic rank `n`:
- `C_{n}_structure.json`
- `C_{n}_gamma.json`
- `C_{n}_evaluated_{gb}.json`
- `C_{n}_coboundary_{gb}.json`
For example, C(2) corresponds to `n=1` and uses `C_1_structure.json`.

## Top-Level Structure
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

## Field Definitions

### 1. `algebra`
```json
{
  "family": "C",
  "m": 1,
  "n": "<bosonic_rank>",
  "cartan_type": "C(n+1)",
  "alternative_notation": {
    "osp": "osp(2|2n)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": "<2n^2 + 5n + 1>",
    "even": "<2n^2 + n + 1>",
    "odd": "<4n>"
  }
}
```

### 2. `oscillator_generators`
Replaces the `supplementary_fermion` with a standard fermionic pair:
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Fermionic oscillators a_1^±"
  },
  "bosons": {
    "count": "<2n>",
    "n": "<n>",
    "labels": ["b_1_p", "b_1_m", "..."],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

### 3. `oscillator_relations`
Includes the canonical anticommutation relations (CAR) for fermions:
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermionic oscillators",
    "relations": {
      "same_type": "{a_i^±, a_j^±} = 0",
      "conjugate_pair": "{a_i^-, a_j^+} = δ_{ij}"
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
    "boson_fermion": "[b_i^±, a_j^±] = 0"
  }
}
```

### 4. `central_elements` (Top-level key)
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
    "description": "Even central element, identified with scalar 1"
  }
}
```

## Compatibility with B(m,n)
- The B(m,n) schema expects `supplementary_fermion` in `oscillator_generators` and `supplementary_fermion_relation` in `oscillator_relations`. C(n+1) properly replaces these with standard fermionic definitions.
- The `central_elements` top-level key is an addition to formalize `kappa` and `K`, which does not disrupt B(m,n) parsers that ignore unknown keys, and can be backported to B(m,n) in future versions.
