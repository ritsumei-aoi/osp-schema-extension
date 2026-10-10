# C(n+1) JSON Schema Specification (Schema 1)

This document specifies the Schema 1 (algebra structure) for the $C(n+1) = \mathfrak{osp}(2|2n)$ extension, based on the $B(0,n)$ v5.0 schema.

## File Naming Convention
- Files are named `C_{n}_structure.json`, where `n` is the bosonic rank.
- Examples: C(2) is `C_1_structure.json`, C(3) is `C_2_structure.json`.

## Schema 1 Structure

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

### `algebra`
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
*Formulas: even = $2n^2 + n + 1$, odd = $4n$.*

### `oscillator_generators`
```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Fermionic oscillators a_i^± with i=1,...,m"
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_j^± with j=1,...,n"
  }
}
```

### `oscillator_relations`
```json
{
  "fermionic_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for fermionic oscillators",
    "relations": {
      "same_type": "{a_i^±, a_j^±} = 0 for all i, j",
      "conjugate_pair": "{a_i^-, a_j^+} = \\delta_{ij}"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations (CCR) for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = \\delta_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_j^±] = 0"
  }
}
```

### `central_elements`
```json
{
  "kappa": {
    "parity": 1,
    "description": "Odd central element (nilpotent: kappa^2 = 0) used for the inhomogeneous deformation."
  },
  "K": {
    "parity": 0,
    "description": "Even central element, identified with scalar 1 in applications."
  }
}
```

## Compatibility Notes
- Replaces `supplementary_fermion` with standard `fermions` (CAR).
- Shifts `central_elements` out of basis notes to a dedicated top-level key.
- File naming aligns with `B_{n}_structure.json`, replacing B with C.
