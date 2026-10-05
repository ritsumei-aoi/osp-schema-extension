# C(n+1) v5.0 JSON Schema Specification

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n),
extending the B(0,n) v5.0 schema defined in `docs/math/B0n_schema_v5.md`.

---

## Schema 1: Algebra Structure

### File Naming Convention
- `C_{n}_structure.json` where `n` is the bosonic rank
- C(2) = osp(2|2): `C_1_structure.json`
- C(3) = osp(2|4): `C_2_structure.json`
- C(4) = osp(2|6): `C_3_structure.json`

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
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {
    "osp": "osp(2|4)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": 19,
    "even": 11,
    "odd": 8
  }
}
```

**Dimension formulas** (C(n+1)): even = $2n^2+n+1$, odd = $4n$, total = $2n^2+5n+1$.

| n | Algebra | even | odd | total |
|---|---------|------|-----|-------|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

### `oscillator_generators`
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^± with CAR"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

**Compatibility note (B vs C)**: B(0,n) uses `supplementary_fermion` with a single `a_0` satisfying $a_0^2 = 1/2$. C(n+1) replaces this with `fermions` containing a standard pair `a_1_p, a_1_m` satisfying CAR $\{a_1^-, a_1^+\} = 1$.

### `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermionic oscillators",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^±, a_1^±} = 0"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0 (homogeneous deformation)"
  }
}
```

**Compatibility note**: B(0,n) uses `supplementary_fermion_relation` with $a_0^2 = 1/2$. C(n+1) replaces this with `standard_fermion_anticommutators`.

### `central_elements`
```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotency": "kappa^2 = 0",
    "description": "Odd central element for inhomogeneous deformation"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central element, identified with scalar 1"
  }
}
```

This is a **top-level key** in C(n+1), as required. In B(0,n), the same information is present but `central_elements` may be nested differently; C(n+1) promotes it to top level.

### `basis`
```json
{
  "even": ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
           "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
           "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del2_pp", "E_eps1_del2_pm",
          "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_mp", "E_eps1_del2_mm"],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
}
```

### `parity`
All even generators have parity 0, all odd generators have parity 1. See `handover/notation.md` for the full lists.

### `generator_realization`
Each generator expressed as oscillator monomials with rational coefficients.

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
    "H_k (2<=k<=n)": {
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

Even root generators follow B(0,n) conventions (unchanged).

### `structure_constants`
Non-zero graded brackets stored as a list of objects:
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
  "generation_date": "2026-10-05",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## Schema 2: Gamma Structure

### File Naming
`C_{n}_gamma.json`

### Structure
```json
{
  "schema_version": "5.0",
  "schema_layer": 2,
  "algebra": { ... },
  "gb_matrix": { ... },
  "gamma_coefficients": [ ... ],
  "metadata": { ... }
}
```

The `gb_matrix` contains 4n deformation parameters for C(n+1):
```json
{
  "size": "2 x 2n",
  "parameters": [
    {"label": "gb_a1p_b1p", "fermionic": "a_1_p", "bosonic": "b_1_p", "parity": 1},
    {"label": "gb_a1p_b1m", "fermionic": "a_1_p", "bosonic": "b_1_m", "parity": 1},
    {"label": "gb_a1m_b1p", "fermionic": "a_1_m", "bosonic": "b_1_p", "parity": 1},
    {"label": "gb_a1m_b1m", "fermionic": "a_1_m", "bosonic": "b_1_m", "parity": 1}
  ]
}
```

---

## Schema 3: Evaluated Structure

### File Naming
`C_{n}_evaluated.json`

### Structure
Concrete numerical values after substituting specific gb parameter assignments.

---

## Schema 4: Coboundary Structure

### File Naming
`C_{n}_coboundary.json`

### Structure
Coboundary coefficients $(\delta f)_{abc}$ for the odd linear map $f$.
