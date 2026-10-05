# JSON Schema Specification v5.0 for C(n+1) = osp(2|2n)

This document specifies the v5.0 JSON schema for $C(n+1) = \mathfrak{osp}(2|2n)$ structure constants, extending the $B(0,n)$ base schema.

---

## 1. Overview and Architecture

The JSON structure follows a 4-layer architecture:
1. **Schema 1 (`C_{n}_structure.json`)**: Lie superalgebra structure (basis, parity, oscillator realization, structure constants).
2. **Schema 2 (`C_{n}_gamma.json`)**: Inhomogeneous deformation ($\gamma$-structure).
3. **Schema 3 (`C_{n}_evaluated_<gb>.json`)**: Numerically evaluated structure constants.
4. **Schema 4 (`C_{n}_coboundary_<gb>.json`)**: Coboundary matrix data for triviality verification.

Here $n$ denotes the **bosonic rank**:
- $n = 1 \implies C(2) = \mathfrak{osp}(2|2)$, file `C_1_structure.json`
- $n = 2 \implies C(3) = \mathfrak{osp}(2|4)$, file `C_2_structure.json`
- $n = 3 \implies C(4) = \mathfrak{osp}(2|6)$, file `C_3_structure.json`

---

## 2. Schema 1 Field Definitions for C(n+1)

### Top-Level Keys
- `schema_version`: `"5.0"`
- `algebra`: Algebra classification and dimension details.
- `oscillator_generators`: Generator definitions (fermions, bosons).
- `central_elements`: Central generators ($\kappa$, $K$).
- `oscillator_relations`: CAR/CCR relations.
- `basis`: Lists of even and odd basis generators.
- `parity`: Parity map for all basis generators.
- `generator_realization`: Standard oscillator word expansion and Frappat form.
- `structure_constants`: List of non-zero graded brackets $[X, Y\}$.
- `metadata`: Provenance metadata.

---

### Key Specification & Examples

#### `algebra`
```json
{
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
*Dimension Formulas*:
- `even`: $2n^2 + n + 1$
- `odd`: $4n$
- `total`: $2n^2 + 5n + 1$

#### `oscillator_generators`
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^± with CAR {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

#### `central_elements` (Top-level key)
```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotent": true,
    "description": "Odd central parameter for deformation"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central scalar multiplier (identified with 1)"
  }
}
```

#### `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermionic oscillators",
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

#### `basis`
```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p", "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd] < [even]"
}
```

---

## 3. Backward Compatibility with B(m,n) Schema

| Feature | B(0,n) Schema v5.0 | C(n+1) Schema v5.0 |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `oscillator_generators` | `supplementary_fermion` ($a_0$) & `bosons` | `fermions` ($a_1^\pm$) & `bosons` |
| `central_elements` | Embedded or top-level | Top-level key with `kappa` (1) and `K` (0) |
| `even` dimension | $2n^2 + n$ | $2n^2 + n + 1$ |
| `odd` dimension | $2n$ | $4n$ |
| File prefix | `B_{n}_...` | `C_{n}_...` |

---

## 4. File Naming Conventions

For bosonic rank $n \in \{1, 2, 3\}$:
- Schema 1: `C_{n}_structure.json`
- Schema 2: `C_{n}_gamma.json`
- Schema 3: `C_{n}_evaluated_<gb>.json`
- Schema 4: `C_{n}_coboundary_<gb>.json`
