# JSON Schema Specification for C(n+1) = osp(2|2n)

**Version**: 5.0  
**Date**: 2026-10-05  
**Scope**: Extension of B(m,n) v5.0 schema to C(n+1) family

---

## Overview

This document specifies the complete JSON schema for C(n+1) = osp(2|2n), extending the B(0,n) v5.0 schema. The C(n+1) family features:
- Standard fermionic CAR pair (a₁⁺, a₁⁻) instead of supplementary fermion a₀
- Odd root structure: ±ε ± δₖ (4n generators)
- Dimension formula: even = 2n² + n + 1, odd = 4n, total = 2n² + 5n + 1

---

## File Naming Convention

```
C_{n}_structure.json       → Schema 1 (algebra structure)
C_{n}_gamma.json           → Schema 2 (gamma deformation structure)
C_{n}_evaluated.json       → Schema 3 (evaluated deformation)
C_{n}_coboundary.json      → Schema 4 (coboundary reference)
```

Where **n is the bosonic rank**:
- C(2) = osp(2|2): n=1 → `C_1_structure.json`
- C(3) = osp(2|4): n=2 → `C_2_structure.json`
- C(4) = osp(2|6): n=3 → `C_3_structure.json`

---

## Schema 1: Algebra Structure

### Top-Level Keys

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "central_elements": { ... },
  "oscillator_generators": { ... },
  "oscillator_relations": { ... },
  "basis": { ... },
  "parity": { ... },
  "generator_realization": { ... },
  "structure_constants": { ... },
  "metadata": { ... }
}
```

---

### 1. `algebra` Field

```json
{
  "family": "C",
  "m": 1,
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {
    "osp": "osp(2|4)",
    "dimension_formula": "osp(2m|2n) with m=1, n=2"
  },
  "dimension": {
    "total": 19,
    "even": 11,
    "odd": 8
  }
}
```

**Mandatory rules**:
- `family`: Always `"C"` for this extension
- `m`: Always `1` for C(n+1) = osp(2|2n)
- `n`: Bosonic rank (1, 2, 3, ...)
- **Dimension formulas**:
  - Even: 2n² + n + 1
  - Odd: 4n
  - Total: 2n² + 5n + 1

**Dimension table** (for reference):

| n | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) |
| 2 | 11 | 8 | 19 | C(3) |
| 3 | 22 | 12 | 34 | C(4) |

---

### 2. `central_elements` Field (New for C(n+1))

```json
{
  "central_elements": [
    {
      "label": "kappa",
      "parity": 1,
      "property": "nilpotent",
      "relation": "kappa^2 = 0",
      "description": "Central odd element for deformation cocycle"
    },
    {
      "label": "K",
      "parity": 0,
      "property": "identity",
      "relation": "K = 1",
      "description": "Central even identity (excluded from PBW basis)"
    }
  ]
}
```

**Key points**:
- **κ (kappa)**: Parity 1 (odd), nilpotent (κ² = 0), used in coboundary calculations
- **K**: Parity 0 (even), identified with scalar 1, excluded from basis lists
- Both appear in schema for completeness; only κ appears in PBW ordering

---

### 3. `oscillator_generators` Field

```json
{
  "fermions": {
    "label": "standard pair",
    "m": 1,
    "parity": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic CAR pair a₁⁺, a₁⁻"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_j^± with j=1,...,n"
  }
}
```

**Differences from B(0,n)**:
- **Removed**: `supplementary_fermion` key (no a₀)
- **Added**: `fermions` key with standard pair
- **Unchanged**: `bosons` structure and labeling

---

### 4. `oscillator_relations` Field

```json
{
  "fermion_relations": {
    "description": "Standard CAR for fermionic pair",
    "relations": {
      "anticommutation": "{a_1^-, a_1^+} = 1",
      "self_annihilation": "a_1^- a_1^- = 0",
      "self_creation": "a_1^+ a_1^+ = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_j^±, b_k^±] = 0 for all j, k",
      "conjugate_pair": "[b_j^-, b_k^+] = δ_{jk}"
    }
  },
  "mixed_commutators": {
    "fermion_boson": "[b_j^±, a_1^±] = 0 (undeformed)"
  }
}
```

**Deformation** (in Schema 2):
$$[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma, j, s} \cdot \kappa$$

---

### 5. `basis` Field

#### 5a. Full basis lists

**For C(2) (n=1)**:

```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del1_pm",
    "E_eps_del1_mp", "E_eps_del1_mm"
  ],
  "central": ["kappa"],
  "ordering_convention": "PBW: kappa < [odd] < [even]"
}
```

**For C(3) (n=2)**:

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_del1_del2_pp",
    "E_del1_del2_pm", "E_del1_del2_mp",
    "E_2del1_p", "E_2del2_p",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del2_pp",
    "E_eps_del1_pm", "E_eps_del2_pm",
    "E_eps_del1_mp", "E_eps_del2_mp",
    "E_eps_del1_mm", "E_eps_del2_mm"
  ],
  "central": ["kappa"],
  "ordering_convention": "PBW: kappa < [odd: ε-roots] < [even: Cartan, pairs, doubles]"
}
```

---

### 6. `parity` Field

```json
{
  "H_1": 0, "H_2": 0, "H_3": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_pm": 0, "E_del1_del2_mp": 0,
  "E_del1_del2_mm": 0,
  "E_2del1_p": 0, "E_2del1_m": 0, "E_2del2_p": 0, "E_2del2_m": 0,
  "E_eps_del1_pp": 1, "E_eps_del1_pm": 1, "E_eps_del1_mp": 1, "E_eps_del1_mm": 1,
  "E_eps_del2_pp": 1, "E_eps_del2_pm": 1, "E_eps_del2_mp": 1, "E_eps_del2_mm": 1,
  "kappa": 1,
  "K": 0
}
```

**Convention**:
- Even generators: parity 0
- Odd generators: parity 1
- κ: parity 1
- K: parity 0

---

### 7. `generator_realization` Field

Each generator is expressed as a sum of oscillator words with rational coefficients.

```json
{
  "description": "Oscillator realization in standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_1^+ b_1^- - b_2^+ b_2^-",
      "parity": 0
    },
    "E_eps_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    },
    "E_eps_del1_pm": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^-",
      "parity": 1
    }
  }
}
```

---

### 8. `structure_constants` Field

Non-zero graded brackets stored as a list:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps_del1_pp",
    "Z": "E_eps_del1_pp",
    "coeff": "1",
    "sign_rule": "graded"
  },
  {
    "X": "E_eps_del1_pp",
    "Y": "E_eps_del1_mm",
    "Z": "H_1",
    "coeff": "1/2",
    "sign_rule": "graded"
  }
]
```

**Notes**:
- Computed from oscillator commutation/anticommutation relations
- Sign rule: `(-1)^{p(X)p(Y)}` for graded bracket
- All triples must satisfy Super Jacobi identity

---

### 9. `metadata` Field

```json
{
  "generated_by": "C_generators.py",
  "generation_date": "2026-10-05",
  "schema_version": "5.0",
  "algebra_family": "C",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017), arXiv:1612.09400",
    "Issue I01 notation document"
  ],
  "notes": "C(n+1) = osp(2|2n) with fermionic CAR pair and 4n odd roots"
}
```

---

## Schema 2: Gamma (Deformation) Structure

**File**: `C_n_gamma.json`

Extends Schema 1 with:

```json
{
  ...schema_1_fields...,
  "deformation_parameters": {
    "gb_matrix": {
      "description": "Inhomogeneous deformation parameters",
      "size": [2, 2, "n"],
      "total_count": 4,
      "parity": 1,
      "parameters": [
        {
          "label": "gb_{a_1_p, b_1_p}",
          "fermion": "a_1_p",
          "boson": "b_1_p",
          "parity": 1
        },
        ...
      ]
    }
  },
  "gamma_coefficients": {
    "description": "2-cocycle coefficients γ(X,Y)",
    "data": [
      {
        "X": "H_1",
        "Y": "E_eps_del1_pp",
        "gamma_XY": "2 * gb_{a_1_p, b_1_p}",
        "coeff_symbolic": true
      },
      ...
    ]
  }
}
```

---

## Schema 3: Evaluated Structure

**File**: `C_n_evaluated.json`

Extends Schema 2 with numerical substitution of gb parameters:

```json
{
  ...schema_2_fields...,
  "gb_assignment": {
    "profile": "all_positive",
    "values": {
      "gb_{a_1_p, b_1_p}": 1,
      "gb_{a_1_p, b_1_m}": 1,
      "gb_{a_1_m, b_1_p}": 1,
      "gb_{a_1_m, b_1_m}": 1,
      ...
    }
  },
  "gamma_coefficients_evaluated": [
    {
      "X": "H_1",
      "Y": "E_eps_del1_pp",
      "Z": "E_eps_del1_pp",
      "gamma_XY_evaluated": 2,
      "coeff": "1"
    }
  ]
}
```

---

## Schema 4: Coboundary Structure

**File**: `C_n_coboundary.json`

Reference structure for triviality verification:

```json
{
  ...schema_1_fields...,
  "coboundary_map": {
    "description": "Odd linear map f: g → g",
    "parameters": [
      {
        "source_basis_element": "H_1",
        "target_expansion": "f(H_1) = Σ φ_ij * Z_j",
        "coefficients": { ... }
      }
    ]
  },
  "coboundary_coefficients": [
    {
      "X": "H_1",
      "Y": "E_eps_del1_pp",
      "delta_f_XY": "(...coboundary formula...)",
      "result": "Z",
      "coeff": "value"
    }
  ]
}
```

---

## Backward Compatibility with B(m,n)

| Feature | B(m,n) schema | C(n+1) schema | Notes |
|---|---|---|---|
| `family` | B | C | Fixed in algebra field |
| `m` | variable | 1 | Dimension parameter |
| `oscillator_generators` | `supplementary_fermion` | `fermions` (CAR) | Structural change |
| `oscillator_relations` | `a_0^2 = 1/2` | `{a_1^-, a_1^+} = 1` | Different algebra |
| `central_elements` | Not present | Present (κ, K) | New key for C family |
| `basis.odd` | `E_δₖ` (2m roots) | `E_ε±δₖ` (4n roots) | Different root structure |
| PBW ordering | Same convention | Same convention | Extended to ε-roots |

---

## Implementation Notes

1. **Generator realization**: All realizations must use PBW ordering of oscillator words
2. **Structure constants**: Compute via oscillator commutation relations; sign rule depends on parity
3. **Verification**: All structures must satisfy:
   - Anti-symmetry: [X,Y} = -(-1)^{p(X)p(Y)}[Y,X}
   - Super Jacobi: [[X,Y},Z} + ... = 0 (super-graded)

4. **File organization**:
   - Schema 1,2,3,4 are generated sequentially
   - Each higher layer depends on the previous layer
   - All files include complete metadata and references

---

## Version History

- **v5.0**: C(n+1) extension with standard fermionic CAR pair and deformation parameters
  - Extends B(m,n) v5.0 schema
  - Adds `central_elements` key
  - Modifies `oscillator_generators` and `oscillator_relations`
  - Changes odd basis structure
