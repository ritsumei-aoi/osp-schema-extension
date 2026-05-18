# JSON Schema Specification for osp(m|2n)

This document specifies the v5.0 JSON schema for algebra structure constants.

## C(n+1) = osp(2|2n) Extension (Revised)

### 1. Algebra Structure (Schema 1)
- **Family**: C
- **m**: 1
- **Dimensions**:
    - **even**: `2n^2 + n + 1`
    - **odd**: `4n`

### 2. Oscillator Generators
- **fermions**: `labels`: ["a_1_p", "a_1_m"], `rank`: 1, `relation`: `{a_1_-, a_1_+} = 1`
- **bosons**: `rank`: n, `labels`: ["b_1_p", "b_1_m", ..., "b_n_p", "b_n_m"]

### 3. Central Elements (Top-Level)
- **kappa**: 1 (parity: 1)
- **K**: 1 (parity: 0)

### 4. File Naming Convention
- `C_{n}_structure.json` (where n is the bosonic rank, e.g., C(2) uses n=1).
