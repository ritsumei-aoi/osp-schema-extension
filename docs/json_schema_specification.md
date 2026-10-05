# JSON Schema Specification for C(n+1)

This document specifies the Schema 1 (algebra structure) extensions for C(n+1) = osp(2|2n) to ensure compatibility with the existing B(0,n) schema while reflecting the different root structures.

## 1. File Naming Convention
- Files are named `C_{n}_structure.json`, where `n` is the bosonic rank.
- Examples: 
  - $C(2) = \mathfrak{osp}(2|2)$: `C_1_structure.json`
  - $C(3) = \mathfrak{osp}(2|4)$: `C_2_structure.json`
  - $C(4) = \mathfrak{osp}(2|6)$: `C_3_structure.json`

## 2. Schema 1 Definitions

### Top-Level Structure
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
    "odd": 4
  }
}
```
**Dimension formulas for C(n+1)**: `even`: $2n^2 + n + 1$, `odd`: $4n$, `total`: $2n^2 + 5n + 1$.

### `oscillator_generators`
Replaces the supplementary fermion with a standard fermionic pair.
```json
"oscillator_generators": {
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair"
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
"oscillator_relations": {
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for standard fermions",
    "relation": "{a_1^-, a_1^+} = 1"
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
Added as a top-level key.
```json
"central_elements": {
  "kappa": {
    "parity": 1,
    "relation": "kappa^2 = 0",
    "description": "Odd nilpotent central element for deformation"
  },
  "K": {
    "parity": 0,
    "relation": "K = 1",
    "description": "Even central element identified with scalar 1"
  }
}
```

### Compatibility with B(m,n) Schema
- The top-level structure remains largely unchanged except for the addition of `central_elements` as a dedicated top-level key.
- `oscillator_generators` generalizes `supplementary_fermion` to `fermions`, allowing for standard CAR relations `{a_1^-, a_1^+} = 1`.
- Basis and parity structures are identical in format (lists and dictionaries), just populated with C(n+1) specific generators.
- Downstream processing scripts must handle the "C" family by looking for the `fermions` key rather than `supplementary_fermion`.
