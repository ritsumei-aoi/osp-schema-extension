# JSON Schema Specification v5.0 for C(n+1) = osp(2|2n)

This document specifies the v5.0 JSON schema used for $C(n+1) = \mathfrak{osp}(2|2n)$ structure constants, deformation parameters, evaluated matrices, and coboundaries across Layers 1 through 4.

---

## 1. Overview of the 4-Layer Architecture

| Layer | File Naming Pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Core algebra structure: basis, parity, oscillator realizations, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation ($\gamma$-structure, $4n$ symbolic `gb` parameters) |
| Schema 3 | `C_{n}_evaluated.json` | Structure constants evaluated under concrete sign assignments for `gb` |
| Schema 4 | `C_{n}_coboundary.json` | Coboundary matrix $(\delta f)_{abc}$ for odd linear maps $f$ |

*Note*: $n$ denotes the bosonic rank ($n=1$ for $C(2)$, $n=2$ for $C(3)$, $n=3$ for $C(4)$).

---

## 2. Schema 1: Algebra Structure Specification

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
  "structure_constants": [ ... ],
  "metadata": { ... }
}
```

### Key Field Definitions

#### `algebra`
- `family`: `"C"`
- `m`: `1`
- `n`: Bosonic rank (1, 2, or 3)
- `cartan_type`: `"C(2)"`, `"C(3)"`, or `"C(4)"`
- `alternative_notation`: `{"osp": "osp(2|2n)", "dimension_formula": "osp(2m|2n) with m=1"}`
- `dimension`: `{"total": 2*n^2 + 5*n + 1, "even": 2*n^2 + n + 1, "odd": 4*n}`

#### `oscillator_generators`
- `fermions`: `{"m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1, "description": "Standard CAR fermionic pair a_1^\pm"}`
- `bosons`: `{"count": 2n, "n": n, "labels": ["b_1_p", "b_1_m", ...], "description": "Bosonic CCR oscillators b_i^\pm"}`

#### `oscillator_relations`
- `standard_fermion_anticommutators`: `{a_1^-, a_1^+} = 1`
- `bosonic_commutators`: `[b_i^-, b_j^+] = \delta_{ij}`
- `mixed_commutators`: `[b_i^\pm, a_1^\pm] = 0`

#### `central_elements` (Top-Level Key)
- `kappa`: `{"parity": 1, "nilpotent": true, "relation": "kappa^2 = 0", "description": "Odd central element"}`
- `K`: `{"parity": 0, "relation": "K = 1", "description": "Even central element (identity scalar)"}`

#### `basis`
- `even`: Array of even generator names (length $2n^2 + n + 1$).
- `odd`: Array of odd generator names (length $4n$).
- `ordering_convention`: `"PBW: κ < [odd] < [even]"`

#### `parity`
Map from generator label string to integer parity (`0` or `1`).

#### `generator_realization`
Map from generator label string to realization object containing:
- `standard_form`: Array of `{"words": [...], "coeff": "..."}`
- `frappat_form`: LaTeX / string representation
- `parity`: `0` or `1`

#### `structure_constants`
Array of graded commutator non-zero results:
```json
[
  {
    "X": "H_0",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "1",
    "sign_rule": "graded"
  }
]
```

---

## 3. Layer 2, Layer 3, and Layer 4 Specifications

### Schema 2 (`C_{n}_gamma.json`)
Contains the `gb_matrix` of size $2 \times 2n$ with $4n$ parameters:
$$\{ \mathrm{gb}_{a_1^+, b_k^+}, \mathrm{gb}_{a_1^+, b_k^-}, \mathrm{gb}_{a_1^-, b_k^+}, \mathrm{gb}_{a_1^-, b_k^-} \mid k=1, \ldots, n \}$$
And top-level field `inhomogeneous_deformation` storing symbolic $\gamma_{abc}$ coefficients where $[X_a, Y_b]_\gamma = [X_a, Y_b]_0 + \kappa \cdot \sum_c \gamma_{abc} Z_c$.

### Schema 3 (`C_{n}_evaluated.json`)
Stores structure constants with concrete sign assignments (e.g. $+1$ or $-1$) substituted into all $4n$ `gb` parameters.

### Schema 4 (`C_{n}_coboundary.json`)
Stores the coboundary tensor $(\delta f)(X_a, Y_b)$ for an odd linear map $f: \mathfrak{g} \to \mathfrak{g}$, specified by transformation matrix $\phi_{ij}$ where $f(Z_j) = \sum_i \phi_{ij} Z_i$.

---

## 4. Compatibility with B(m,n) Schemas

- **Unified Versioning**: Both B(0,n) and C(n+1) use Schema Version `5.0`.
- **Top-Level Parity Block Ordering**: Both enforce `κ < [odd] < [even]` in `basis.ordering_convention`.
- **Standardized Central Elements**: `central_elements` is maintained as a top-level key containing `kappa` and `K`.
- **Differentiator**: `algebra.family` differentiates `"B"` ($a_0$ supplementary fermion) from `"C"` ($a_1^\pm$ CAR pair).
