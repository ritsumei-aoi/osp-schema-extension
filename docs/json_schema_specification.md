# JSON Schema Specification for C(n+1) = osp(2|2n)

Version: 5.0 (C(n+1) extension of B(m,n) schema)

---

## Overview: 4-Layer Architecture

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_{n}_evaluated.json` | Numerically evaluated structure constants for specific gb parameters |
| Schema 4 | `C_{n}_coboundary.json` | Coboundary data for triviality verification |

File naming: `n` is the bosonic rank (e.g., C(2) = osp(2|2) uses `n=1` → `C_1_structure.json`).

---

## Schema 1: Algebra Structure (`C_{n}_structure.json`)

### Top-level keys

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
    "even": "2n^2 + n + 1",
    "odd": "4n",
    "total": "2n^2 + 5n + 1"
  }
}
```

Dimension values (C(n+1)):

| n | even | odd | total |
|---|---|---|---|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

### `central_elements` (top-level key)

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "description": "Odd nilpotent central element; kappa^2 = 0"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central element; identified with scalar 1 in all applications. Not in PBW basis."
  }
}
```

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^- with CAR"
  },
  "bosons": {
    "count": "2n",
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^+/- for k=1,...,n"
  }
}
```

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "CAR: {a_1^-, a_1^+} = 1",
    "relations": {
      "anticommutator": "{a_1_m, a_1_p} = 1",
      "self_anticommutators": "{a_1_p, a_1_p} = 0, {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "CCR: [b_i^-, b_j^+] = delta_{ij}",
    "relations": {
      "same_type": "[b_i_p, b_j_p] = 0, [b_i_m, b_j_m] = 0",
      "conjugate_pair": "[b_i_m, b_j_p] = delta_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k_p, a_1_p] = 0, [b_k_m, a_1_m] = 0, [b_k_p, a_1_m] = 0, [b_k_m, a_1_p] = 0"
  }
}
```

### `basis`

PBW ordering: `kappa < [odd] < [even]`

Example for n=1 (C(2)):
```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_{pp/pm/mp/mm}] < [even: H, E_roots]"
}
```

Example for n=2 (C(3)):
```json
{
  "even": ["H_1","H_2","H_3","E_2del1_p","E_2del2_p","E_del1_del2_pp",
           "E_2del1_m","E_2del2_m","E_del1_del2_mm","E_del1_del2_pm","E_del1_del2_mp"],
  "odd": ["E_eps1_del1_pp","E_eps1_del1_pm","E_eps1_del1_mp","E_eps1_del1_mm",
          "E_eps1_del2_pp","E_eps1_del2_pm","E_eps1_del2_mp","E_eps1_del2_mm"],
  "ordering_convention": "PBW: kappa < [odd] < [even]"
}
```

### `parity`

All even generators have parity 0; all odd generators (E_eps1_*) have parity 1.

### `generator_realization`

Each generator expressed as oscillator words with rational coefficients.

```json
{
  "description": "PBW ordering: a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
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
      "frappat_form": "b_1^+ b_1^- - b_2^+ b_2^- (for n>=2)",
      "parity": 0
    },
    "H_{n+1}": {
      "standard_form": [
        {"words": ["b_n_p", "b_n_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_n^+ b_n^- - 1/2",
      "parity": 0
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

Non-zero graded brackets stored as a list:
```json
[
  {
    "X": "H_1",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "2",
    "sign_rule": "graded"
  }
]
```

### `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "arXiv:hep-th/9607161"
  ]
}
```

---

## Compatibility with B(m,n) Schema

| Field | B(0,n) | C(n+1) |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `oscillator_generators` | `supplementary_fermion` (a_0) + `bosons` | `fermions` (a_1_p, a_1_m) + `bosons` |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` |
| `central_elements` | top-level, kappa+K | top-level, kappa+K (same structure) |
| odd basis labels | `E_del{k}_p/m` | `E_eps1_del{k}_pp/pm/mp/mm` |
| odd dimension | 2n | 4n |
| even dimension | 2n²+n | 2n²+n+1 |

---

## Schema 2: Inhomogeneous Deformation (`C_{n}_gamma.json`)

Adds `gb_matrix` and `gamma_coefficients` fields to Schema 1 data.

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "gb_matrix": {
    "description": "4n deformation parameters, parity 1",
    "size": "4n",
    "parameters": [
      "gb_a1p_b1p", "gb_a1p_b1m", "gb_a1m_b1p", "gb_a1m_b1m"
    ]
  },
  "gamma_coefficients": [
    {
      "X": "...", "Y": "...", "Z": "...",
      "coeff": "symbolic expression in gb parameters"
    }
  ]
}
```

## Schema 3: Evaluated Structure (`C_{n}_evaluated.json`)

Substitutes concrete values for gb parameters. Standard assignment: all gb = +1.

## Schema 4: Coboundary Structure (`C_{n}_coboundary.json`)

Stores coboundary coefficients $(\delta f)_{abc}$ for an odd linear map $f$.

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "linear_map_f": {
    "description": "Odd linear map f: g -> g parameterized by phi_{ij}",
    "coefficients": { ... }
  },
  "coboundary_coefficients": [
    {
      "X": "...", "Y": "...", "Z": "...",
      "coeff": "expression in phi parameters"
    }
  ]
}
```
