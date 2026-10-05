# C(n+1) JSON Schema Specification

This document specifies the Schema 1 (algebra structure) fields for
C(n+1) = osp(2|2n). It extends the B(0,n) v5.0 schema defined in
`docs/math/B0n_schema_v5.md`.

**Approved**: 2026-10-05 (Issue I02-1)

---

## Overview: 4-Layer Schema Architecture

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_n_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_n_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_n_evaluated_<gb>.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_n_coboundary_<gb>.json` | Coboundary data for triviality verification |

File naming uses `C_n_structure.json` where `n` is the **bosonic rank**
(e.g., C(2)=osp(2|2) has n=1 → `C_1_structure.json`).

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

> **Difference from B(0,n)**: `central_elements` is a new top-level key
> (not present in B(0,n) schema).

---

### `schema_version`

```json
"schema_version": "5.0"
```

---

### `algebra`

Concrete example for n=2 (C(3)=osp(2|4)):

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
    "even": "2n^2 + n + 1",
    "odd": "4n",
    "total": "2n^2 + 5n + 1"
  },
  "dimension": {
    "total": 19,
    "even": 11,
    "odd": 8
  }
}
```

**Dimension table**:

| n | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

**Dimension formulas**: even = 2n²+n+1, odd = 4n, total = 2n²+5n+1.

---

### `oscillator_generators`

Concrete example for n=2:

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "relation": "{a_1^-, a_1^+} = 1",
    "description": "Standard fermionic CAR pair; a_1_p = a_1^+, a_1_m = a_1^-"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

> **Difference from B(0,n)**: The `supplementary_fermion` key (with `a_0`,
> satisfying `a_0^2 = 1/2`) is replaced by the `fermions` key containing
> the standard CAR pair `a_1_p`, `a_1_m`. The `m: 1` field records the
> number of fermionic pairs.

---

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "CAR for standard fermionic pair",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "same_sign_p": "{a_1^+, a_1^+} = 0",
      "same_sign_m": "{a_1^-, a_1^-} = 0"
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

> **Difference from B(0,n)**: `supplementary_fermion_relation` is replaced
> by `standard_fermion_anticommutators` with standard CAR `{a_1^-, a_1^+} = 1`.

---

### `central_elements`

```json
"central_elements": {
  "kappa": {
    "parity": 1,
    "description": "Odd nilpotent central element; kappa^2 = 0",
    "nilpotency": "kappa^2 = 0"
  },
  "K": {
    "parity": 0,
    "description": "Even central identity element; K = 1 in all current applications",
    "note": "Not an independent basis element; excluded from PBW ordering"
  }
}
```

> **New top-level key** (not present in B(0,n) schema). Both `kappa` (parity 1,
> odd nilpotent) and `K` (parity 0, even identity) are recorded here.
> `K` does not appear in the basis or PBW ordering.

---

### `basis`

PBW ordering: Option A (Parity-First). Concrete example for n=2 (C(3)):

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del2_pp", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm",
    "E_eps1_del2_mp", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW Option A: [odd] < [even]; within odd: positive ε-block (pp/pm by k) then negative ε-block (mp/mm by k); within even: Cartans H_1...H_{n+1}, then positive roots by height, then negative, then mixed"
}
```

**General odd ordering** (for arbitrary n):
```
E_eps1_del{1}_pp, E_eps1_del{1}_pm, ..., E_eps1_del{n}_pp, E_eps1_del{n}_pm,
E_eps1_del{1}_mp, E_eps1_del{1}_mm, ..., E_eps1_del{n}_mp, E_eps1_del{n}_mm
```

> **Difference from B(0,n)**: Odd basis contains 4n generators
> `E_eps1_del{k}_{ss}` instead of 2n generators `E_del{k}_p/m`.

---

### `parity`

Concrete example for n=2 (C(3)):

```json
{
  "H_1": 0, "H_2": 0, "H_3": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_2del2_p": 0, "E_2del2_m": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_mm": 0,
  "E_del1_del2_pm": 0, "E_del1_del2_mp": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del2_pp": 1, "E_eps1_del2_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1,
  "E_eps1_del2_mp": 1, "E_eps1_del2_mm": 1
}
```

All `E_eps1_del{k}_{ss}` generators have parity 1; all others have parity 0.

---

### `generator_realization`

Concrete example for n=2 (C(3)):

```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0,
      "note": "First Cartan; includes fermionic number operator a_1^+ a_1^-"
    },
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_1^+ b_1^- - b_2^+ b_2^-",
      "parity": 0
    },
    "H_{n+1}": {
      "standard_form": [
        {"words": ["b_n_p", "b_n_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_n^+ b_n^- - 1/2",
      "parity": 0,
      "note": "Terminal Cartan; constant term -1/2"
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

> **Difference from B(0,n)**: PBW ordering starts with `a_1_p, a_1_m`
> instead of `a_0`. Odd generators use `a_1_p`/`a_1_m` in place of `a_0`.

---

### `structure_constants`

Non-zero graded brackets `[X, Y}` stored as a list. Concrete values are
computed per n by `build_C_structure_constants.py`.

```json
[
  {
    "X": "H_1",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "1",
    "sign_rule": "graded"
  }
]
```

Format is identical to B(0,n). All brackets must be recomputed using CAR
for `a_1^±` instead of `a_0^2 = 1/2`.

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

`C_{n}_structure.json` where n = bosonic rank:

| Algebra | n | File name |
|---|---|---|
| C(2) = osp(2\|2) | 1 | `C_1_structure.json` |
| C(3) = osp(2\|4) | 2 | `C_2_structure.json` |
| C(4) = osp(2\|6) | 3 | `C_3_structure.json` |

---

## Backward Compatibility with B(m,n) Schema

| Key | B(0,n) | C(n+1) |
|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` (unchanged) |
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `algebra.dimension_formula.even` | `2n²+n` | `2n²+n+1` |
| `algebra.dimension_formula.odd` | `2n` | `4n` |
| `oscillator_generators` fermion key | `supplementary_fermion` (with `a_0`) | `fermions` (with `a_1_p`, `a_1_m`, `m=1`) |
| `oscillator_relations` fermion key | `supplementary_fermion_relation` | `standard_fermion_anticommutators` |
| `central_elements` | not present | top-level key; `kappa` (parity 1), `K` (parity 0) |
| `basis.odd` labels | `E_del{k}_p/m` (2n generators) | `E_eps1_del{k}_pp/pm/mp/mm` (4n generators) |
| `generator_realization.ordering` | `a_0, b_k_p/m` | `a_1_p, a_1_m, b_k_p/m` |
| File naming | `B_{n}_structure.json` | `C_{n}_structure.json` |
