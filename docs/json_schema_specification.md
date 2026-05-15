# JSON Data Schema Specification — C(n+1) Extension

This document describes the JSON schema for storing algebra structure constants
for the C(n+1) = osp(2|2n) family. It extends the B(m,n) v5.0 convention from the
primary osp-triviality case study.

## Schema Version

- **Version**: 5.0 (same as B(m,n))
- **Family**: C(n+1) = osp(2|2n), n = 1, 2, 3

## Top-Level Structure

Schema 1 (algebra structure) for C(n+1) uses the following top-level keys:

| Key | Required | Description |
|-----|----------|-------------|
| `schema_version` | yes | Schema version string (e.g., "5.0") |
| `algebra` | yes | Algebra family, parameters, dimension |
| `oscillator_generators` | yes | Oscillator labels and counts |
| `oscillator_relations` | yes | CAR/CCR relations |
| `central_elements` | yes | Central elements κ and K |
| `basis` | yes | Even and odd basis lists |
| `parity` | yes | Parity (0=even, 1=odd) for each generator |
| `generator_realization` | yes | Oscillator realization of each generator |
| `structure_constants` | yes | Non-zero brackets |
| `metadata` | yes | References and generation info |

### Key Differences from B(m,n) v5.0

1. **No supplementary fermion** `a_0`. C(n+1) uses a standard fermionic pair `(a_1_p, a_1_m)`.
2. **`central_elements`** added as a top-level key (between `oscillator_relations` and `basis`).
3. **Family** is `"C"` (not `"B"`), with `m = 1` and dimension formula `osp(2m|2n)`.
4. **Odd generators** are `E_eps1_del{k}_{pp/pm/mp/mm}` (4n total), not `E_del{k}_{p/m}`.

## File Naming Convention

| n | Algebra | JSON File |
|---|---------|-----------|
| 1 | C(2) = osp(2\|2) | `data/algebra_structures/C_1_structure.json` |
| 2 | C(3) = osp(2\|4) | `data/algebra_structures/C_2_structure.json` |
| 3 | C(4) = osp(2\|6) | `data/algebra_structures/C_3_structure.json` |

## Section Specifications

### `schema_version`

```json
"schema_version": "5.0"
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
    "dimension_formula": "osp(2m|2n)"
  },
  "dimension": {
    "total": 19,
    "even": 11,
    "odd": 8
  }
}
```

#### Dimension Formulas

| n | even | odd | total | cartan_type | osp |
|---|------|-----|-------|-------------|-----|
| 1 | 4 | 4 | 8 | C(2) | osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) | osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) | osp(2\|6) |

**Formulas**: even = n(2n+1) + m(2m−1) = n(2n+1) + 1; odd = 4n; total = 2n² + 5n + 1

### `oscillator_generators`

```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic oscillators a_1^± (single pair, CAR). No supplementary fermion a_0."
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,2"
  }
}
```

**Note**: The `supplementary_fermion` field from B(m,n) is absent. For C(n+1), the fermionic content consists solely of the standard CAR pair (a_1_p, a_1_m).

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for standard fermionic pair",
    "relations": {
      "same_type": "{a_1^±, a_1^±} = 0",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
    },
    "canonical_pairs": [
      {
        "index": 1,
        "annihilation": "a_1_m",
        "creation": "a_1_p",
        "anticommutator": 1
      }
    ],
    "metric_matrix": {
      "description": "Metric g in basis [a_1_m, a_1_p] for standard fermionic pair",
      "basis_order": ["a_1_m", "a_1_p"],
      "m": 1,
      "matrix": [[0, 1], [-1, 0]]
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    },
    "canonical_pairs": [
      {"index": 1, "annihilation": "b_1_m", "creation": "b_1_p", "commutator": 1},
      {"index": 2, "annihilation": "b_2_m", "creation": "b_2_p", "commutator": 1}
    ],
    "symplectic_matrix": {
      "description": "Symplectic form J in basis [b_1_p, b_1_m, b_2_p, b_2_m]",
      "basis_order": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
      "n": 2,
      "matrix": [[0,1,0,0],[-1,0,0,0],[0,0,0,1],[0,0,-1,0]]
    }
  },
  "mixed_commutators": {
    "description": "Commutation relations between bosonic and fermionic oscillators",
    "boson_fermion": {
      "relation": "[b_i^±, a_1^±] = 0",
      "description": "Bosons commute with standard fermions (homogeneous case)"
    }
  }
}
```

**Key differences from B(m,n)**:
- `supplementary_fermion_relations` block removed
- `standard_fermion_anticommutators` now has explicit pairs (not "N/A")
- `mixed_commutators` simplified: only `boson_fermion` remains

### `central_elements`

```json
{
  "kappa": {
    "symbol": "κ",
    "description": "Nilpotent central element extending the base field, κ² = 0",
    "parity": 0
  },
  "K": {
    "symbol": "K",
    "description": "Central identity element (scalar extension)",
    "parity": 0
  }
}
```

**Note**: This is a new top-level key in Schema 1, added for C(n+1). It does not
exist in the B(m,n) v5.0 schema but is backward-compatible (optional key).

### `basis`

The basis follows the PBW ordering from Issue I01-1:

```
κ < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp] < K
```

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp] < K"
}
```

### `parity`

Each generator is assigned a parity value (0 = even/bosonic, 1 = odd/fermionic):

- Cartan generators H_1, ..., H_{n+1}: parity 0
- Even root generators E_{...}: parity 0
- Odd root generators E_eps1_del{k}_{pp/pm/mp/mm}: parity 1

### `generator_realization`

Each generator is expressed as a quadratic expression in oscillator operators,
using the `standard_form` word-list convention:

```json
{
  "description": "Standard form with PBW ordering: odd generators first, then even. No supplementary fermion.",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_k": {
      "standard_form": [
        {"words": ["b_k_p", "b_k_m"], "coeff": "1"},
        {"words": ["b_{k+1}_p", "b_{k+1}_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_k^+ b_k^- - b_{k+1}^+ b_{k+1}^-",
      "parity": 0,
      "note": "Cartan generator (diff-type, bosonic). Frappat p.220."
    },
    "H_n": {
      "standard_form": [
        {"words": ["b_n_p", "b_n_m"], "coeff": "1"},
        {"words": [], "coeff": "1/2"}
      ],
      "frappat_form": "b_n^+ b_n^- + 1/2",
      "parity": 0,
      "note": "Cartan generator (terminal, bosonic)."
    },
    "H_{n+1}": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "a_1^+ a_1^- - 1/2",
      "parity": 0,
      "note": "Cartan generator (fermionic). Frappat p.220."
    },
    "E_2del{k}_p": {
      "standard_form": [
        {"words": ["b_k_p", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "(b_k^+)^2",
      "parity": 0,
      "note": "Long even root +2δ_k."
    },
    "E_2del{k}_m": {
      "standard_form": [
        {"words": ["b_k_m", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "(b_k^-)^2",
      "parity": 0,
      "note": "Long even root -2δ_k."
    },
    "E_del{i}_del{j}_pp": {
      "standard_form": [
        {"words": ["b_i_p", "b_j_p"], "coeff": "1"}
      ],
      "frappat_form": "b_i^+ b_j^+",
      "parity": 0,
      "note": "Short even root +(δ_i+δ_j)."
    },
    "E_del{i}_del{j}_mm": {
      "standard_form": [
        {"words": ["b_i_m", "b_j_m"], "coeff": "1"}
      ],
      "frappat_form": "b_i^- b_j^-",
      "parity": 0,
      "note": "Short even root -(δ_i+δ_j)."
    },
    "E_eps1_del{k}_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1,
      "note": "Odd root +(ε₁+δ_k)."
    },
    "E_eps1_del{k}_pm": {
      "standard_form": [
        {"words": ["a_1_p", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_k^-",
      "parity": 1,
      "note": "Odd root +(ε₁-δ_k)."
    },
    "E_eps1_del{k}_mp": {
      "standard_form": [
        {"words": ["a_1_m", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_k^+",
      "parity": 1,
      "note": "Odd root -(ε₁-δ_k)."
    },
    "E_eps1_del{k}_mm": {
      "standard_form": [
        {"words": ["a_1_m", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_k^-",
      "parity": 1,
      "note": "Odd root -(ε₁+δ_k)."
    }
  }
}
```

## References

- Frappat et al., *Dictionary on Lie Algebras and Superalgebras* (2000), Chapter on C(n+1)
- Issue I01-1: C(n+1) basis and root system design (closed)
- Issue I02-1: Schema 1 v5.0 extension for C(n+1) (this issue)
- B(m,n) v5.0 schema: osp-triviality `docs/schemas.md`
