# JSON Schema Specification for Schema 1 (Algebra Structure)

This document specifies the fields for Schema 1, focusing on the changes and requirements for $C(n+1)$ while maintaining compatibility with the existing $B(m,n)$ schema (v5.0).

## 1. Top-Level Keys
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

## 2. Field Definitions

### `algebra`
- **Family**: `"family": "C"`
- **Rank**: `"m": 1` (fixed for $C(n+1)$) and `"n": <integer>` (bosonic rank).
- **Dimension**: `even`: $2n^2 + n + 1$, `odd`: $4n$, `total`: $2n^2 + 5n + 1$.
- **Compatibility**: The $B(m,n)$ schema uses `"family": "B"` and `"m": 0`. The structure dynamically accommodates differing dimension formulas.

### `oscillator_generators`
- **Fermions**: A new key `"fermions"` is introduced replacing `"supplementary_fermion"`. It specifies `m=1` with standard pair labels `"a_1_p", "a_1_m"`.
- **Bosons**: A key `"bosons"` identical to $B(0,n)$ with `n` count and labels `"b_1_p", "b_1_m", ...`.

### `oscillator_relations`
- Contains canonical relations for bosons and standard CAR (`{a_1^-, a_1^+} = 1`) for fermions, replacing the $a_0^2 = 1/2$ relation in $B(0,n)$.

### `central_elements`
- **Top-level key** added to accommodate central elements formally for the inhomogeneous deformation.
- Contains:
  - `kappa`: odd parity ($p=1$), the extension parameter.
  - `K`: even parity ($p=0$), standard scaling element.

## 3. File Naming Convention
Files are named based on the bosonic rank `n`:
- `C_{n}_structure.json`
- Examples: `C_1_structure.json` (for $C(2)$), `C_2_structure.json` (for $C(3)$).

## 4. Compatibility with B(m,n)
- The $B(m,n)$ schema uses `B_{n}_structure.json`. By specifying `"family"` and modularizing `"oscillator_generators"` (using `"fermions"` instead of hardcoding `supplementary_fermion`), the parser can dynamically route logic based on the algebra type without breaking the base JSON schema validation.
