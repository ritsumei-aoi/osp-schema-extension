# JSON Schema Specification v5.0

This document specifies the v5.0 JSON schema for the `osp-schema-extension` project. It covers both the $B(m,n)$ (specifically $B(0,n) = \mathfrak{osp}(1|2n)$) and $C(n+1) = \mathfrak{osp}(2|2n)$ families.

## Overview: 4-Layer Schema Architecture

The JSON data for each algebra is organized into 4 layers:

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `<Family>_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `<Family>_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `<Family>_{n}_evaluated_<gb>.json` | Numerically evaluated structure constants |
| Schema 4 | `<Family>_{n}_coboundary_<gb>.json` | Coboundary data for triviality verification |

### File Naming Conventions
- **Family B**: `B_{n}_structure.json` (where `{n}` is the rank, e.g., $B(0,2)$ is `B_2_structure.json`)
- **Family C**: `C_{n}_structure.json` (where `{n}` is the bosonic rank, e.g., $C(2)$ is `C_1_structure.json`)

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
Defines the algebraic family and dimensions.

| Field | $B(0,n)$ | $C(n+1)$ |
|---|---|---|
| `family` | `"B"` | `"C"` |
| `m` | `0` | `1` |
| `n` | rank | bosonic rank |
| `dimension_formula` | `"osp(2m+1|2n) with m=0"` | `"osp(2m|2n) with m=1"` |
| `dimension.even` | $2n^2 + n$ | $2n^2 + n + 1$ |
| `dimension.odd` | $2n$ | $4n$ |

### `oscillator_generators`
Defines the oscillators used in the realization. Consists of two primary keys:

- `fermions`: 
  - For $B(0,n)$: uses `supplementary_fermion` (label `a_0`).
  - For $C(n+1)$: uses standard CAR pair (`a_1_p`, `a_1_m`) with `m=1`.
- `bosons`: 
  - Standard bosonic oscillators (`b_i_p`, `b_i_m`) with rank `n`.

### `oscillator_relations`
Defines the commutation/anticommutation relations.

- **Family B**: `supplementary_fermion_relation` ($a_0^2 = 1/2$).
- **Family C**: `fermionic_anticommutators` ($\{a_i^-, a_j^+\} = \delta_{ij}$).
- Both: `bosonic_commutators` ($[b_i^-, b_j^+] = \delta_{ij}$) and `mixed_relations`.

### `central_elements`
**Top-level key** explicitly defining central elements for deformation.

```json
"central_elements": {
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "description": "Nilpotent central element (kappa^2 = 0)"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Central identity element (scalar 1)"
  }
}
```

### `basis`
Lists the generators in PBW order.
- **Convention**: $\kappa < [\text{odd roots}] < [\text{even Cartan}] < [\text{even roots}]$.
- $K$ is excluded from the basis lists as it is identified with identity.

### `generator_realization`
Oscillator words for each generator.
- **Family B**: `E_del{k}_p` uses `a_0 b_k^+`.
- **Family C**: `E_eps1_del{k}_pp` uses `a_1_p b_k_p`.

---

## Compatibility and Extension Note

Schema v5.0 maintains a consistent structure across families by:
1. Using a unified `schema_version`.
2. Grouping oscillators in `oscillator_generators` under `fermions` and `bosons`.
3. Providing family-specific blocks in `oscillator_relations`.
4. Standardizing the 4-layer file architecture and PBW ordering across all extensions.
