# C(n+1) v5.0 JSON Schema Specification

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n),
extending the B(0,n) v5.0 schema.

---

## Schema 1: Algebra Structure

### File Naming

`C_{n}_structure.json` where `n` is the bosonic rank:
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

| $n$ | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^- with CAR: {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

**Compatibility note**: B(0,n) uses `supplementary_fermion` with label `a_0`.
C(n+1) replaces this with a `fermions` key containing a standard CAR pair.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermionic oscillators",
    "relations": {
      "canonical_pair": "{a_1^-, a_1^+} = 1",
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
    "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed)"
  }
}
```

### `central_elements`

```json
{
  "kappa": {
    "parity": 1,
    "nilpotency": "kappa^2 = 0",
    "description": "Odd central element for inhomogeneous deformation"
  },
  "K": {
    "parity": 0,
    "value": 1,
    "description": "Even central identity element (= scalar 1, excluded from basis)"
  }
}
```

### `basis`

PBW ordering: $\kappa < [\text{odd}] < [\text{even}]$, K = 1 excluded.

Example for n=2 (C(3)):
```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del2_pp",
    "E_eps_del1_pm", "E_eps_del2_pm",
    "E_eps_del1_mp", "E_eps_del2_mp",
    "E_eps_del1_mm", "E_eps_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 excluded)"
}
```

### `parity`

All even generators have parity 0, all odd generators have parity 1.

### `generator_realization`

Each generator expressed as a sum of oscillator monomials with rational coefficients.

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
    "E_eps_del{k}_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_k^+",
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
    "X": "H_1",
    "Y": "E_eps_del1_pp",
    "Z": "E_eps_del1_pp",
    "coeff": "1",
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

## Schema 2: Gamma Structure

File naming: `C_{n}_gamma.json`

Top-level keys:
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

For C(n+1), the gb matrix has size $2 \times 2n = 4n$ parameters:

```json
{
  "size": [2, 4],
  "fermion_labels": ["a_1_p", "a_1_m"],
  "boson_labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
  "parameters": {
    "gb_a1p_b1p": "gb_{a_1^+, b_1^+}",
    "gb_a1p_b1m": "gb_{a_1^+, b_1^-}",
    "gb_a1m_b1p": "gb_{a_1^-, b_1^+}",
    "gb_a1m_b1m": "gb_{a_1^-, b_1^-}",
    "gb_a1p_b2p": "gb_{a_1^+, b_2^+}",
    "gb_a1p_b2m": "gb_{a_1^+, b_2^-}",
    "gb_a1m_b2p": "gb_{a_1^-, b_2^+}",
    "gb_a1m_b2m": "gb_{a_1^-, b_2^-}"
  },
  "deformation_relation": "[b_j^s, a_1^σ] = -gb_{σ,j,s} · κ"
}
```

### `gamma_coefficients`

```json
[
  {
    "X": "E_eps_del1_pp",
    "Y": "E_eps_del1_mp",
    "gamma_Z": "H_1",
    "coeff": "symbolic expression in gb parameters"
  }
]
```

---

## Schema 3: Evaluated Structure

File naming: `C_{n}_evaluated.json`

Same structure as Schema 2 but with gb parameters substituted with concrete values.

---

## Schema 4: Coboundary Structure

File naming: `C_{n}_coboundary.json`

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "linear_map_f": { ... },
  "coboundary_coefficients": [ ... ],
  "metadata": { ... }
}
```

---

## Compatibility with B(m,n) Schema

| Field | B(0,n) | C(n+1) |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` |
| `central_elements` | top-level key | top-level key (same structure) |
| `basis.odd` | `E_del{k}_p/m` (2n) | `E_eps_del{k}_XY` (4n) |
| File naming | `B_{n}_*.json` | `C_{n}_*.json` |
