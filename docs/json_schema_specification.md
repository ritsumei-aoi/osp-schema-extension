# JSON Schema Specification for C(n+1) = osp(2|2n)

**Version**: 5.0  
**Extends**: B(0,n) v5.0 schema (see `docs/math/B0n_schema_v5.md`)

---

## Overview: 4-Layer Schema Architecture

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure, gb matrix) |
| Schema 3 | `C_{n}_evaluated.json` | Numerically evaluated structure constants for specific gb values |
| Schema 4 | `C_{n}_coboundary.json` | Coboundary data for triviality verification |

File naming: `n` is the **bosonic rank** (number of bosonic oscillator pairs).
- C(2) = osp(2|2): n=1 → `C_1_structure.json`, etc.
- C(3) = osp(2|4): n=2 → `C_2_structure.json`, etc.
- C(4) = osp(2|6): n=3 → `C_3_structure.json`, etc.

---

## Schema 1: Algebra Structure (`C_{n}_structure.json`)

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
  "structure_constants": [ ... ],
  "metadata": { ... }
}
```

### `schema_version`

```json
"schema_version": "5.0"
```

### `algebra`

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
    "even": "2*n^2 + n + 1",
    "odd": "4*n",
    "total": "2*n^2 + 5*n + 1"
  }
}
```

**Dimension table**:

| n | even | odd | total |
|---|---|---|---|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

**Compatibility note**: B(0,n) uses `"family": "B"`, `"m": 0`. C(n+1) uses `"family": "C"`, `"m": 1`. The `m` field tracks the fermionic sector rank.

### `central_elements`

Top-level key (not nested under oscillator_generators). Contains both central elements:

```json
"central_elements": {
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central identity element; identified with scalar 1 in all applications. Not a basis element.",
    "nilpotent": false
  },
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "description": "Odd central nilpotent element; kappa^2 = 0. Appears in inhomogeneous deformation bracket.",
    "nilpotent": true
  }
}
```

### `oscillator_generators`

```json
"oscillator_generators": {
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic CAR pair a_1^+, a_1^-"
  },
  "bosons": {
    "count": "2*n",
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic CCR oscillators b_k^± for k=1,...,n"
  }
}
```

**Compatibility note**: B(0,n) uses `supplementary_fermion` key (single $a_0$). C(n+1) replaces this with `fermions` key containing the standard CAR pair. The `bosons` key is unchanged in structure.

### `oscillator_relations`

```json
"oscillator_relations": {
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {
      "raising_lowering": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^+, a_1^+} = 0",
      "same_type_m": "{a_1^-, a_1^-} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed)"
  }
}
```

**Note on deformation**: The mixed commutator is zero in the undeformed algebra. In the deformed algebra (Schema 2), it becomes $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s} \cdot \kappa$.

### `basis`

PBW ordering convention: κ < [odd] < [even].

```json
"basis": {
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "even": [
    "H_1", "H_2",
    "E_2del1_p", "E_2del1_m"
  ],
  "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_{pp,pm,mp,mm} for k=1..n] < [even: H_1..H_{n+1}, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]"
}
```

(Example shown for n=1. For n=2 and n=3, extend with additional generators per `handover/notation.md` §6.)

### `parity`

```json
"parity": {
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

All `E_eps1_del{k}_{...}` generators have parity 1. All `H_k` and `E_2del{k}`, `E_del{i}_del{j}_...` have parity 0.

### `generator_realization`

Each generator expressed as a sum of oscillator words with rational coefficients.

```json
"generator_realization": {
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "H_k_general": {
      "standard_form": [
        {"words": ["b_{k-1}_p", "b_{k-1}_m"], "coeff": "1"},
        {"words": ["b_{k}_p", "b_{k}_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-",
      "parity": 0,
      "note": "For 2 <= k <= n"
    },
    "H_{n+1}": {
      "standard_form": [
        {"words": ["b_n_p", "b_n_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_n^+ b_n^- - 1/2",
      "parity": 0,
      "note": "Terminal Cartan; includes constant -1/2"
    },
    "E_eps1_del{k}_pp": {
      "standard_form": [{"words": ["a_1_p", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_pm": {
      "standard_form": [{"words": ["a_1_p", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^-",
      "parity": 1
    },
    "E_eps1_del{k}_mp": {
      "standard_form": [{"words": ["a_1_m", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_mm": {
      "standard_form": [{"words": ["a_1_m", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^-",
      "parity": 1
    },
    "E_2del{k}_p": {
      "standard_form": [{"words": ["b_k_p", "b_k_p"], "coeff": "1"}],
      "frappat_form": "(b_k^+)^2",
      "parity": 0
    },
    "E_2del{k}_m": {
      "standard_form": [{"words": ["b_k_m", "b_k_m"], "coeff": "1"}],
      "frappat_form": "(b_k^-)^2",
      "parity": 0
    },
    "E_del{i}_del{j}_pp": {
      "standard_form": [{"words": ["b_i_p", "b_j_p"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^+",
      "parity": 0
    },
    "E_del{i}_del{j}_mm": {
      "standard_form": [{"words": ["b_i_m", "b_j_m"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^-",
      "parity": 0
    },
    "E_del{i}_del{j}_pm": {
      "standard_form": [{"words": ["b_i_p", "b_j_m"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^-",
      "parity": 0
    },
    "E_del{i}_del{j}_mp": {
      "standard_form": [{"words": ["b_i_m", "b_j_p"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^+",
      "parity": 0
    }
  }
}
```

### `structure_constants`

Non-zero graded brackets $[X, Y\}$ stored as a list of objects:

```json
"structure_constants": [
  {
    "X": "H_1",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "2",
    "sign_rule": "graded"
  }
]
```

The graded bracket satisfies: $[X, Y\} = -(-1)^{p(X)p(Y)} [Y, X\}$.

### `metadata`

```json
"metadata": {
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba, Dictionary on Lie Algebras and Superalgebras (2000)",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## Schema 2: Inhomogeneous Deformation (`C_{n}_gamma.json`)

### Top-Level Keys

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "gb_matrix": { ... },
  "gamma_coefficients": [ ... ],
  "metadata": { ... }
}
```

### `gb_matrix`

The gb matrix has shape 2×2n (fermionic index σ ∈ {+,-}, bosonic pair (j, s) with j=1..n, s ∈ {+,-}):

```json
"gb_matrix": {
  "shape": [2, "2*n"],
  "index_description": "gb[sigma][j][s] = gb_{a_1^sigma, b_j^s}",
  "parameters": {
    "gb_p_1_p": "gb_{a_1^+, b_1^+}",
    "gb_p_1_m": "gb_{a_1^+, b_1^-}",
    "gb_m_1_p": "gb_{a_1^-, b_1^+}",
    "gb_m_1_m": "gb_{a_1^-, b_1^-}"
  },
  "parity": 1,
  "count": "4*n"
}
```

### `gamma_coefficients`

Same list-of-objects format as structure_constants, with symbolic gb entries.

---

## Schema 3: Evaluated Structure (`C_{n}_evaluated.json`)

Extends Schema 2 with concrete gb values substituted:

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "gb_assignment": {
    "gb_p_1_p": 1, "gb_p_1_m": 1, "gb_m_1_p": 1, "gb_m_1_m": 1
  },
  "evaluated_gamma": [ ... ],
  "metadata": { ... }
}
```

---

## Schema 4: Coboundary Structure (`C_{n}_coboundary.json`)

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "phi_matrix": { ... },
  "coboundary_coefficients": [ ... ],
  "metadata": { ... }
}
```

The `phi_matrix` encodes the odd linear map $f(Z_j) = \sum_i \phi_{ij} Z_i$.

---

## Compatibility with B(m,n) Schema

| Field | B(0,n) v5.0 | C(n+1) v5.0 |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `oscillator_generators` key | `supplementary_fermion` | `fermions` |
| Odd basis generators | `E_del{k}_p/m` | `E_eps1_del{k}_pp/pm/mp/mm` |
| Odd generator count | `2n` | `4n` |
| Even dimension formula | `2n^2+n` | `2n^2+n+1` |
| `central_elements` | top-level | top-level (same) |
