# C(n+1) v5.0 JSON Schema Specification

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n),
extended from the B(0,n) v5.0 base schema.

---

## Overview: 4-Layer Schema Architecture

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_{n}_evaluated.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_{n}_coboundary.json` | Coboundary data for triviality verification |

Here `n` is the bosonic rank: C(2) = osp(2|2) → `C_1_*.json`, C(3) = osp(2|4) → `C_2_*.json`, C(4) = osp(2|6) → `C_3_*.json`.

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

### `schema_version`

```json
"schema_version": "5.0"
```

### `algebra`

```json
{
  "family": "C",
  "m": 1,
  "n": <bosonic_rank>,
  "cartan_type": "C(<n+1>)",
  "alternative_notation": {
    "osp": "osp(2|2n)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": "<2n^2 + 5n + 1>",
    "even": "<2n^2 + n + 1>",
    "odd": "<4n>"
  }
}
```

**Dimension formulas** (C(n+1)): even = $2n^2+n+1$, odd = $4n$, total = $2n^2+5n+1$.

| Algebra | n | even | odd | total |
|---|---|---|---|---|
| C(2) = osp(2\|2) | 1 | 4 | 4 | 8 |
| C(3) = osp(2\|4) | 2 | 11 | 8 | 19 |
| C(4) = osp(2\|6) | 3 | 22 | 12 | 34 |

### `oscillator_generators`

```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^± with {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": "<2n>",
    "n": "<n>",
    "labels": ["b_1_p", "b_1_m", ..., "b_n_p", "b_n_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

**Compatibility note**: B(0,n) uses `supplementary_fermion` with `a_0`; C(n+1) replaces this with `fermions` containing a standard CAR pair. The `bosons` key has the same structure in both families.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anti-commutation relations for fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "self_anticommutators": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0"
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
    "boson_fermion": "[b_k^±, a_1^±] = 0"
  }
}
```

**Compatibility note**: B(0,n) uses `supplementary_fermion_relation` with `a_0 * a_0 = 1/2`; C(n+1) replaces this with standard CAR.

### `central_elements`

```json
{
  "kappa": {
    "parity": 1,
    "property": "kappa^2 = 0",
    "description": "Odd nilpotent central element for deformation"
  },
  "K": {
    "parity": 0,
    "property": "K = 1",
    "description": "Even central identity element (Bakalov-Sullivan); identified with scalar 1"
  }
}
```

**Note**: `central_elements` is a **top-level key** in the C(n+1) schema. K does not appear in the basis lists or PBW ordering. κ appears in PBW ordering as the lowest element.

### `basis`

PBW ordering: κ < [odd generators] < [even generators]

```json
{
  "even": ["H_1", ..., "H_{n+1}", "E_2del{k}_p", ..., "E_del{i}_del{j}_pp", ...,
           "E_2del{k}_m", ..., "E_del{i}_del{j}_mm", ...,
           "E_del{i}_del{j}_pm", ..., "E_del{i}_del{j}_mp", ...],
  "odd": ["E_eps1_del{k}_pp", ..., "E_eps1_del{k}_pm", ...,
          "E_eps1_del{k}_mp", ..., "E_eps1_del{k}_mm", ...],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
}
```

Concrete examples for each rank are defined in `handover/notation.md`.

### `parity`

Maps each generator label to its parity (0 = even, 1 = odd):

```json
{
  "H_k": 0,
  "E_2del{k}_p": 0, "E_2del{k}_m": 0,
  "E_del{i}_del{j}_pp": 0, "E_del{i}_del{j}_mm": 0,
  "E_del{i}_del{j}_pm": 0, "E_del{i}_del{j}_mp": 0,
  "E_eps1_del{k}_pp": 1, "E_eps1_del{k}_pm": 1,
  "E_eps1_del{k}_mp": 1, "E_eps1_del{k}_mm": 1
}
```

### `generator_realization`

Each generator is expressed as a sum of oscillator words with rational coefficients.

```json
{
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
    "H_k (2 <= k <= n)": {
      "standard_form": [
        {"words": ["b_{k-1}_p", "b_{k-1}_m"], "coeff": "1"},
        {"words": ["b_k_p", "b_k_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-",
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
      "standard_form": [
        {"words": ["a_1_p", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_pm": {
      "standard_form": [
        {"words": ["a_1_p", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_k^-",
      "parity": 1
    },
    "E_eps1_del{k}_mp": {
      "standard_form": [
        {"words": ["a_1_m", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_mm": {
      "standard_form": [
        {"words": ["a_1_m", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_k^-",
      "parity": 1
    }
  }
}
```

### `structure_constants`

Non-zero graded brackets $[X, Y\}$ stored as a list:

```json
[
  {
    "X": "<generator_label>",
    "Y": "<generator_label>",
    "result": [
      {"Z": "<generator_label>", "coeff": "<rational>"}
    ],
    "sign_rule": "graded"
  }
]
```

**Note**: The `result` field is a list to support brackets that expand to multiple terms.

### `metadata`

```json
{
  "generated_by": "C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "schema_version": "5.0",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## Schema 2: Gamma Structure (Inhomogeneous Deformation)

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

```json
{
  "size": [2, "<2n>"],
  "parameters": [
    {"label": "gb_a1p_b{k}_p", "fermion": "a_1_p", "boson": "b_{k}_p"},
    {"label": "gb_a1p_b{k}_m", "fermion": "a_1_p", "boson": "b_{k}_m"},
    {"label": "gb_a1m_b{k}_p", "fermion": "a_1_m", "boson": "b_{k}_p"},
    {"label": "gb_a1m_b{k}_m", "fermion": "a_1_m", "boson": "b_{k}_m"}
  ],
  "parity": 1,
  "total_count": "<4n>"
}
```

### `gamma_coefficients`

```json
[
  {
    "X": "<generator>",
    "Y": "<generator>",
    "result": [
      {"Z": "<generator>", "coeff": "<expression_in_gb>"}
    ]
  }
]
```

---

## Schema 3: Evaluated Structure

### Top-Level Keys

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "gb_assignment": { ... },
  "evaluated_gamma_coefficients": [ ... ],
  "metadata": { ... }
}
```

### `gb_assignment`

```json
{
  "gb_a1p_b1_p": "+1",
  "gb_a1p_b1_m": "+1",
  ...
}
```

---

## Schema 4: Coboundary Structure

### Top-Level Keys

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "f_map": { ... },
  "coboundary_coefficients": [ ... ],
  "metadata": { ... }
}
```

### `f_map`

The odd linear map $f: \mathfrak{g} \to \mathfrak{g}$ parameterized by coefficients $\phi_{ij}$:

```json
{
  "description": "Odd linear map f: g -> g (parity-reversing)",
  "coefficients": {
    "phi_{i}_{j}": "<symbolic>"
  }
}
```

---

## Compatibility with B(m,n) Schema

| Feature | B(0,n) | C(n+1) |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| Fermion key | `supplementary_fermion` | `fermions` |
| Fermion type | `a_0`, `a_0^2=1/2` | `a_1^±`, `{a_1^-,a_1^+}=1` |
| `central_elements` | Present | Present (top-level key) |
| Odd generators | `E_del{k}_p/m` (2n) | `E_eps1_del{k}_pp/pm/mp/mm` (4n) |
| Even dimension | $2n^2+n$ | $2n^2+n+1$ |
| Cartan count | $n$ | $n+1$ |
| gb parameters | $2n$ | $4n$ |

## File Naming Convention

- Structure: `C_{n}_structure.json` (n = bosonic rank)
- Gamma: `C_{n}_gamma.json`
- Evaluated: `C_{n}_evaluated.json`
- Coboundary: `C_{n}_coboundary.json`

Examples: C(2) uses n=1 → `C_1_structure.json`, C(3) uses n=2 → `C_2_structure.json`, C(4) uses n=3 → `C_3_structure.json`.
