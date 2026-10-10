# JSON Schema Specification for C(n+1) = osp(2|2n)

**Version**: 5.0  
**Finalized**: 2026-10-10 (Issue I02-1)  
**Model**: Claude Sonnet 4.6

This document specifies the Schema 1 (algebra structure) fields for
`C(n+1) = osp(2|2n)`, extending the B(0,n) v5.0 base schema.

---

## Overview: 4-Layer Schema Architecture

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_n_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_n_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_n_evaluated_<gb>.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_n_coboundary_<gb>.json` | Coboundary data for triviality verification |

File naming uses `C_n_structure.json` where `n` is the bosonic rank
(e.g., C(2) = osp(2|2) is `C_1_structure.json`).

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

---

### `schema_version`

```json
"schema_version": "5.0"
```

---

### `algebra`

Mandatory rules: `"m": 1` explicitly included; dimension formulas `even = 2n²+n+1`, `odd = 4n`.

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
  "dimension_formula": {
    "even": "2*n^2 + n + 1",
    "odd": "4*n",
    "total": "2*n^2 + 5*n + 1"
  },
  "dimension": {
    "total": 19,
    "even": 11,
    "odd": 8
  }
}
```

**Dimension table**:

| n | Algebra | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

---

### `oscillator_generators`

Mandatory rules: two keys `"fermions"` (with `m=1`, labels `a_1_p`, `a_1_m`)
and `"bosons"` (rank `n`). Replaces B(0,n)'s `supplementary_fermion`.

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "relation": "{a_1^-, a_1^+} = 1",
    "description": "Standard fermionic CAR pair; m=1 fermionic degree of freedom."
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n."
  }
}
```

---

### `oscillator_relations`

Replaces B(0,n)'s `supplementary_fermion_relation` with `standard_fermion_anticommutators`.

```json
{
  "standard_fermion_anticommutators": {
    "description": "Standard CAR for fermionic pair a_1^±",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "nilpotency": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "CCR for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

---

### `central_elements`

Top-level key (not nested). Contains `kappa` (parity 1) and `K` (parity 0).

```json
{
  "kappa": {
    "parity": 1,
    "description": "Odd central extension element; nilpotent: kappa^2 = 0.",
    "note": "Formal extension symbol; appears in deformed oscillator exchange relations."
  },
  "K": {
    "parity": 0,
    "description": "Even central element; identified with scalar 1 in all current applications.",
    "note": "Not an independent basis element; excluded from PBW ordering and basis lists. Recorded here for schema completeness only."
  }
}
```

---

### `basis`

PBW ordering (ε-grouped, approved 2026-10-10 in I01-1):
`[odd,+ε,+δ] < [odd,+ε,−δ] < [odd,−ε,+δ] < [odd,−ε,−δ] < [even]`

Example for `n=2` (C(3) = osp(2|4)):

```json
{
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ],
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "ordering_convention": "PBW (epsilon-grouped): [odd,+eps,+del] < [odd,+eps,-del] < [odd,-eps,+del] < [odd,-eps,-del] < [even]; kappa and K are excluded as independent basis elements."
}
```

---

### `parity`

All even generators have parity 0; all odd generators have parity 1.
Example for `n=2`:

```json
{
  "H_1": 0, "H_2": 0, "H_3": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_2del2_p": 0, "E_2del2_m": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_mm": 0,
  "E_del1_del2_pm": 0, "E_del1_del2_mp": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del2_pp": 1,
  "E_eps1_del1_pm": 1, "E_eps1_del2_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del2_mp": 1,
  "E_eps1_del1_mm": 1, "E_eps1_del2_mm": 1
}
```

---

### `generator_realization`

Oscillator PBW ordering: `a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m`

```json
{
  "description": "Standard form with PBW oscillator ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m, ..., b_n_p, b_n_m",
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
        {"words": ["b_{k}_p", "b_{k}_m"], "coeff": "-1"}
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
      "note": "Terminal Cartan; includes constant -1/2."
    },
    "E_eps1_del{k}_pp": {
      "standard_form": [{"words": ["a_1_p", "b_{k}_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_pm": {
      "standard_form": [{"words": ["a_1_p", "b_{k}_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^-",
      "parity": 1
    },
    "E_eps1_del{k}_mp": {
      "standard_form": [{"words": ["a_1_m", "b_{k}_p"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_mm": {
      "standard_form": [{"words": ["a_1_m", "b_{k}_m"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^-",
      "parity": 1
    },
    "E_2del{k}_p": {
      "standard_form": [{"words": ["b_{k}_p", "b_{k}_p"], "coeff": "1/2"}],
      "frappat_form": "(1/2)(b_k^+)^2",
      "parity": 0
    },
    "E_2del{k}_m": {
      "standard_form": [{"words": ["b_{k}_m", "b_{k}_m"], "coeff": "1/2"}],
      "frappat_form": "(1/2)(b_k^-)^2",
      "parity": 0
    },
    "E_del{i}_del{j}_pp (i<j)": {
      "standard_form": [{"words": ["b_{i}_p", "b_{j}_p"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^+",
      "parity": 0
    },
    "E_del{i}_del{j}_pm (i<j)": {
      "standard_form": [{"words": ["b_{i}_p", "b_{j}_m"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^-",
      "parity": 0
    },
    "E_del{i}_del{j}_mp (i<j)": {
      "standard_form": [{"words": ["b_{i}_m", "b_{j}_p"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^+",
      "parity": 0
    },
    "E_del{i}_del{j}_mm (i<j)": {
      "standard_form": [{"words": ["b_{i}_m", "b_{j}_m"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^-",
      "parity": 0
    }
  }
}
```

---

### `structure_constants`

Non-zero graded brackets `[X, Y}` stored as a list. Format identical to B(0,n).
Full population is deferred to code generation (build_C_structure_constants.py).

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

---

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## File Naming Convention

`C_{n}_structure.json` where `n` is the bosonic rank:

| n | Algebra | File |
|---|---|---|
| 1 | C(2) = osp(2\|2) | `C_1_structure.json` |
| 2 | C(3) = osp(2\|4) | `C_2_structure.json` |
| 3 | C(4) = osp(2\|6) | `C_3_structure.json` |

---

## Compatibility with B(m,n) Schema

| Key | B(0,n) | C(n+1) |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `algebra.dimension_formula.even` | `2n²+n` | `2n²+n+1` |
| `algebra.dimension_formula.odd` | `2n` | `4n` |
| `oscillator_generators` key | `supplementary_fermion` | `fermions` |
| `oscillator_relations` key | `supplementary_fermion_relation` | `standard_fermion_anticommutators` |
| `basis.odd` labels | `E_del{k}_p/m` | `E_eps1_del{k}_pp/pm/mp/mm` |
| `central_elements` | top-level key | top-level key (same structure) |
| File pattern | `B_n_structure.json` | `C_n_structure.json` |

All other keys (`schema_version`, `parity`, `generator_realization` structure,
`structure_constants` format, `metadata`) share the same schema structure.
