# C(n+1) v5.0 JSON Schema Specification

This document specifies the v5.0 JSON schema used for the structure constants of C(n+1) = osp(2|2n). It is an extension of the Schema 1 architecture originally designed for B(0,n).

## Overview: 4-Layer Schema Architecture

The JSON data is organized into 4 layers:

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_{n}_evaluated_<gb>.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_{n}_coboundary_<gb>.json` | Coboundary data for triviality verification |

**Note**: `n` refers to the bosonic rank. For example, C(2) = osp(2|2) uses `n=1` and the file `C_1_structure.json`.

---

## Schema 1: Algebra Structure

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

Explicitly defines the family, rank parameters, and standard dimensions.

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
**Dimension Formulas**:
- Even: $2n^2 + n + 1$
- Odd: $4n$
- Total: $2n^2 + 5n + 1$

### `oscillator_generators`

Replaces the single supplementary fermion of B(0,n) with a standard fermionic pair.

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

### `oscillator_relations`

Defines standard CAR for fermions and CCR for bosons.

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermions",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = 0, {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0",
      "conjugate_pair": "[b_i^m, b_j^p] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

### `central_elements`

Top-level key to formalize the presence of central extensions without forcing them into the standard PBW basis lists.

```json
{
  "kappa": {
    "parity": 1,
    "description": "Odd central extension element"
  },
  "K": {
    "parity": 0,
    "description": "Even central element (identified with scalar 1)"
  }
}
```

### `basis`, `parity`, `generator_realization`, `structure_constants`
These fields follow the analogous structure from Schema v5.0 for B(0,n), updated with the generators (`H_k`, `E_...`) and notation specific to C(n+1) decided in Issue I01.

- **`basis.even`**: Array of strings for even generators ($H_k$, $E_{2\delta_k}$, $E_{\pm \delta_i \pm \delta_j}$).
- **`basis.odd`**: Array of strings for odd generators ($E_{\pm \varepsilon \pm \delta_k}$).
- **PBW Ordering**: Standard Highest Weight ($\mathfrak{n}^- < \mathfrak{h} < \mathfrak{n}^+$).
