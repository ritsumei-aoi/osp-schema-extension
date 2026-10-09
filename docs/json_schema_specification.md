# C(n+1) = osp(2|2n) JSON Schema Specification (v5.0)

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n), extending
the B(0,n) v5.0 schema. All four layers are defined below.

## File Naming Convention

| Layer | File pattern | Example (n=1) |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | `C_1_structure.json` |
| Schema 2 | `C_{n}_gamma.json` | `C_1_gamma.json` |
| Schema 3 | `C_{n}_evaluated.json` | `C_1_evaluated.json` |
| Schema 4 | `C_{n}_coboundary.json` | `C_1_coboundary.json` |

Here `n` is the bosonic rank, so C(2) = osp(2|2) uses n=1.

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

**Dimension formulas** (C(n+1)): even = $2n^2 + n + 1$, odd = $4n$, total = $2n^2 + 5n + 1$.

| $n$ | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

### `oscillator_generators`

```json
{
  "fermions": {
    "type": "standard_pair",
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± with CAR: {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

> **Compatibility note**: B(0,n) uses `supplementary_fermion` with label `a_0` and
> relation $a_0^2 = 1/2$. C(n+1) replaces this with `fermions` key containing
> a standard pair `a_1_p`, `a_1_m` under CAR.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermionic pair",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
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
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

### `central_elements`

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotency": "kappa^2 = 0",
    "description": "Odd central element for the nilpotent extension"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "value": 1,
    "description": "Even central identity element (= scalar 1)"
  }
}
```

### `basis`

```json
{
  "even": ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
           "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
           "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del2_pp",
          "E_eps1_del1_pm", "E_eps1_del2_pm",
          "E_eps1_del1_mp", "E_eps1_del2_mp",
          "E_eps1_del1_mm", "E_eps1_del2_mm"],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
}
```

### `parity`

All H_k and E_{even root} generators have parity 0.
All E_eps1_{...} generators have parity 1.

### `generator_realization`

Each generator expressed as sum of oscillator words with rational coefficients.
Ordering: `a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`.

Example realizations:
```json
{
  "H_1": {
    "standard_form": [
      {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
      {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
    ],
    "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
    "parity": 0
  },
  "E_eps1_del1_pp": {
    "standard_form": [
      {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
    ],
    "frappat_form": "a_1^+ b_1^+",
    "parity": 1
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
    "result": [{"Z": "E_eps1_del1_pp", "coeff": "2"}],
    "sign_rule": "graded"
  }
]
```

> **Note**: The `result` field is an array of `{"Z": ..., "coeff": ...}` entries,
> allowing multi-term bracket results. This extends the B(0,n) format which used
> a single `Z`/`coeff` pair.

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

For C(n+1), the gb matrix has shape 2 × 2n (fermionic labels × bosonic labels):

```json
{
  "description": "Deformation parameters for C(n+1) inhomogeneous deformation",
  "size": "2 x 2n",
  "parameters": [
    {"label": "gb_a1p_b1p", "fermion": "a_1_p", "boson": "b_1_p"},
    {"label": "gb_a1p_b1m", "fermion": "a_1_p", "boson": "b_1_m"},
    {"label": "gb_a1m_b1p", "fermion": "a_1_m", "boson": "b_1_p"},
    {"label": "gb_a1m_b1m", "fermion": "a_1_m", "boson": "b_1_m"}
  ],
  "parity": 1
}
```

### `gamma_coefficients`

```json
[
  {
    "X": "E_eps1_del1_pp",
    "Y": "E_eps1_del1_mp",
    "result": [{"Z": "H_1", "coeff": "gb_a1m_b1p"}],
    "type": "deformation"
  }
]
```

---

## Schema 3: Evaluated Structure

Same format as Schema 2 `gamma_coefficients`, but with all `gb_*` parameters
substituted with concrete numerical values (e.g., ±1).

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "gb_assignment": { "gb_a1p_b1p": 1, "gb_a1p_b1m": 1, ... },
  "evaluated_gamma": [ ... ],
  "metadata": { ... }
}
```

---

## Schema 4: Coboundary Structure

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

| Field | B(0,n) | C(n+1) | Change |
|---|---|---|---|
| `algebra.family` | `"B"` | `"C"` | Value change |
| `algebra.m` | `0` | `1` | Value change |
| `oscillator_generators` | `supplementary_fermion` key | `fermions` key | Key replacement |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | Key replacement |
| `central_elements` | (present) | (present, top-level) | Same structure |
| `basis.odd` | `E_del{k}_p/m` (2n) | `E_eps1_del{k}_pp/pm/mp/mm` (4n) | Label change, count doubled |
| `generator_realization` | Uses `a_0` | Uses `a_1_p`, `a_1_m` | Oscillator change |
| `structure_constants.result` | Single `Z`/`coeff` | Array of `{"Z", "coeff"}` | Format extension |
