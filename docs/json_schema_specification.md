# C(n+1) JSON Schema Specification v5.0

This document specifies the 4-layer JSON schema for C(n+1) = osp(2|2n),
extending the B(0,n) v5.0 schema (see `docs/math/B0n_schema_v5.md`).

---

## File Naming Convention

| Layer | File pattern |
|-------|-------------|
| Schema 1 (structure) | `C_{n}_structure.json` |
| Schema 2 (gamma) | `C_{n}_gamma.json` |
| Schema 3 (evaluated) | `C_{n}_evaluated.json` |
| Schema 4 (coboundary) | `C_{n}_coboundary.json` |

where `n` is the bosonic rank: C(2)=osp(2|2) → n=1, C(3)=osp(2|4) → n=2, C(4)=osp(2|6) → n=3.

---

## Schema 1: Algebra Structure

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
    "total": 8,
    "even": 4,
    "odd": 4
  }
}
```

**Dimension formulas** (C(n+1)): even = $2n^2+n+1$, odd = $4n$, total = $2n^2+5n+1$.

| n | even | odd | total | Algebra |
|---|------|-----|-------|---------|
| 1 | 4    | 4   | 8     | C(2)=osp(2\|2) |
| 2 | 11   | 8   | 19    | C(3)=osp(2\|4) |
| 3 | 22   | 12  | 34    | C(4)=osp(2\|6) |

### `central_elements` (top-level key)
```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "property": "kappa^2 = 0",
    "description": "Odd nilpotent central element for inhomogeneous deformation"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "property": "identified with scalar 1 in all current applications",
    "description": "Even central identity element; excluded from PBW basis"
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
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

### `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermionic pair",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "self_anticommutator": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed)"
  }
}
```

### `basis`

PBW ordering: `κ < [odd: E_eps1_del{k}_{...}] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_{...}]`

```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
}
```

### `parity`
```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

### `generator_realization`

Each generator expressed as oscillator words with rational coefficients.

```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "H_{n+1}": {
      "standard_form": [
        {"words": ["b_n_p", "b_n_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_n^+ b_n^- - 1/2",
      "parity": 0,
      "note": "Terminal Cartan"
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
    },
    "E_2del{k}_p": {
      "standard_form": [
        {"words": ["b_k_p", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "(b_k^+)^2",
      "parity": 0
    },
    "E_2del{k}_m": {
      "standard_form": [
        {"words": ["b_k_m", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "(b_k^-)^2",
      "parity": 0
    }
  }
}
```

### `structure_constants`

Non-zero graded brackets $[X, Y\}$ stored as a list:

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
  "generated_by": "C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## Schema 2: Gamma Structure (inhomogeneous deformation)

```json
{
  "schema_version": "5.0",
  "algebra": { "...": "same as Schema 1" },
  "inhomogeneous_deformation": {
    "description": "Gamma coefficients for C(n+1) deformation",
    "gb_matrix": {
      "size": "2 x 2n",
      "parameters": [
        "gb_a1p_b1p", "gb_a1p_b1m",
        "gb_a1m_b1p", "gb_a1m_b1m"
      ],
      "parity": 1
    },
    "gamma_coefficients": [
      {
        "X": "generator_label",
        "Y": "generator_label",
        "Z": "generator_label",
        "coeff_expr": "symbolic expression in gb parameters"
      }
    ]
  },
  "metadata": { "...": "..." }
}
```

---

## Schema 3: Evaluated Structure

```json
{
  "schema_version": "5.0",
  "algebra": { "...": "same as Schema 1" },
  "gb_assignment": {
    "gb_a1p_b1p": "1", "gb_a1p_b1m": "1",
    "gb_a1m_b1p": "1", "gb_a1m_b1m": "1"
  },
  "evaluated_gamma": [
    {
      "X": "generator_label",
      "Y": "generator_label",
      "Z": "generator_label",
      "coeff": "numerical value"
    }
  ],
  "metadata": { "...": "..." }
}
```

---

## Schema 4: Coboundary Structure

```json
{
  "schema_version": "5.0",
  "algebra": { "...": "same as Schema 1" },
  "odd_map_f": {
    "description": "Odd linear map f: g -> g",
    "coefficients": { "phi_{ij}": "value" }
  },
  "coboundary_delta_f": [
    {
      "X": "generator_label",
      "Y": "generator_label",
      "Z": "generator_label",
      "coeff": "value"
    }
  ],
  "metadata": { "...": "..." }
}
```

---

## Compatibility with B(m,n) Schema

| Field | B(0,n) | C(n+1) |
|-------|--------|--------|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `oscillator_generators` key | `supplementary_fermion` + `bosons` | `fermions` + `bosons` |
| Odd generators | `E_del{k}_p/m` (2n) | `E_eps1_del{k}_{pp,pm,mp,mm}` (4n) |
| `central_elements` | present (kappa parity 1) | present (kappa parity 1) |
| Dimension odd | `2n` | `4n` |
| Dimension even | `2n^2+n` | `2n^2+n+1` |
