# C(n+1) JSON Schema Specification (v5.0 Extension)

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n),
extending the B(0,n) v5.0 base schema defined in `docs/math/B0n_schema_v5.md`.

## File Naming Convention

Files use `C_{n}_{layer}.json` where `n` is the **bosonic rank**:

| Algebra | n | Structure | Gamma | Evaluated | Coboundary |
|---|---|---|---|---|---|
| C(2) = osp(2\|2) | 1 | C_1_structure.json | C_1_gamma.json | C_1_evaluated.json | C_1_coboundary.json |
| C(3) = osp(2\|4) | 2 | C_2_structure.json | C_2_gamma.json | C_2_evaluated.json | C_2_coboundary.json |
| C(4) = osp(2\|6) | 3 | C_3_structure.json | C_3_gamma.json | C_3_evaluated.json | C_3_coboundary.json |

---

## Schema 1: Algebra Structure (`C_{n}_structure.json`)

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

**Dimension formulas for C(n+1)**:
- even = 2n^2 + n + 1
- odd = 4n
- total = 2n^2 + 5n + 1

| n | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

### `oscillator_generators`

**Key change from B(0,n)**: Replace `supplementary_fermion` with `fermions` (standard CAR pair).

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic CAR pair a_1^+, a_1^-"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

### `central_elements`

**New top-level key for C(n+1)** (not present in B(0,n)):

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
    "property": "central identity",
    "description": "Even central element, identified with scalar 1 in applications; excluded from basis"
  }
}
```

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermionic oscillators",
    "relations": {
      "cross": "{a_1^-, a_1^+} = 1",
      "square_p": "a_1^+ * a_1^+ = 0",
      "square_m": "a_1^- * a_1^- = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_sign": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "fermion_boson": "[a_1^±, b_k^±] = 0"
  }
}
```

### `basis`

PBW ordering: κ < [odd: E_eps1_del{k}_{ss}] < [even: H_k, E_2del{k}_{p/m}, E_del{i}_del{j}_{ss}]

Example for n=2 (C(3)):
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
  "ordering_convention": "PBW: κ < [odd] < [even]; K excluded (= scalar 1)"
}
```

### `parity`

All E_eps1_del{k}_{ss} generators have parity 1; all others have parity 0.

### `generator_realization`

```json
{
  "description": "Normal-ordered oscillator words, PBW order: a_1_p < a_1_m < b_1_p < b_1_m < ...",
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
    "H_k (k=2,...,n)": {
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
    }
  }
}
```

### `structure_constants`

Non-zero graded brackets [X, Y} stored as:
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
  "generation_date": "2026-10-04",
  "references": [
    "Frappat, Sciarrino, Sorba, Dictionary on Lie Algebras and Superalgebras (2000)",
    "Bakalov and Sullivan (2017)",
    "docs/math/Cn1_definition.md"
  ]
}
```

---

## Schema 2: Inhomogeneous Deformation (`C_{n}_gamma.json`)

```json
{
  "schema_version": "5.0",
  "algebra": { "...same as Schema 1..." },
  "deformation_parameters": {
    "gb_matrix": {
      "description": "4n parity-1 parameters indexed by (fermion_label, boson_label)",
      "parameters": [
        {"label": "gb_p_1_p", "fermion": "a_1_p", "boson": "b_1_p", "parity": 1},
        "..."
      ]
    }
  },
  "gamma_coefficients": [
    {
      "X": "basis_generator_label",
      "Y": "basis_generator_label",
      "Z": "basis_generator_label",
      "coeff_expr": "symbolic expression in gb parameters"
    }
  ],
  "metadata": { "..." }
}
```

---

## Schema 3: Evaluated Structure (`C_{n}_evaluated.json`)

```json
{
  "schema_version": "5.0",
  "algebra": { "..." },
  "gb_assignment": {
    "gb_p_1_p": "1", "gb_p_1_m": "1",
    "...": "..."
  },
  "evaluated_gamma": [
    {
      "X": "...", "Y": "...", "Z": "...",
      "coeff": "numerical rational value"
    }
  ],
  "metadata": { "..." }
}
```

---

## Schema 4: Coboundary Structure (`C_{n}_coboundary.json`)

```json
{
  "schema_version": "5.0",
  "algebra": { "..." },
  "f_map": {
    "description": "Odd linear map f: g -> g, parameterized by phi_{ij}",
    "phi_params": ["phi_H1_E_eps1_del1_pp", "..."],
    "f_values": [
      {"input": "H_1", "output_basis": "E_eps1_del1_pp", "coeff": "phi_H1_E_eps1_del1_pp"},
      "..."
    ]
  },
  "delta_f_coefficients": [
    {
      "X": "...", "Y": "...", "Z": "...",
      "coeff_expr": "symbolic in phi parameters"
    }
  ],
  "metadata": { "..." }
}
```

---

## Compatibility with B(m,n) Schema

| Key | B(0,n) | C(n+1) |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` |
| `central_elements` | absent | present (top-level key) |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` |
| Odd basis labels | `E_del{k}_p/m` | `E_eps1_del{k}_{ss}` |
| Odd generator count | 2n | 4n |
| Even dim | 2n^2+n | 2n^2+n+1 |
