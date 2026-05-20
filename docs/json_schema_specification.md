# C(n+1) Schema 1 v5.0 Specification

**Version**: 5.0  
**Algebra**: C(n+1) = osp(2|2n)  
**Established**: Issue I02-1 (2026-05-20)  
**References**:
- Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000); arXiv:hep-th/9607161
- Bakalov and Sullivan (2017); arXiv:1612.09400
- Aoi (2026), *On the triviality of inhomogeneous deformations of osp(1|2n)*

---

## Overview

The JSON schema for each C(n+1) algebra is organized into 4 layers:

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_{n}_evaluated_{gb}.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_{n}_coboundary_{gb}.json` | Coboundary data for triviality verification |

Here `n` is the **bosonic rank** (number of bosonic oscillator pairs).

| Algebra | n | Schema 1 file |
|---|---|---|
| C(2) = osp(2\|2) | 1 | `C_1_structure.json` |
| C(3) = osp(2\|4) | 2 | `C_2_structure.json` |
| C(4) = osp(2\|6) | 3 | `C_3_structure.json` |

---

## Top-Level Keys

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

> **Note**: `central_elements` is a new top-level key not present in the B(m,n) v5.0 schema.

---

## `schema_version`

```json
"schema_version": "5.0"
```

---

## `algebra`

Concrete example for C(2), n = 1:

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

**Dimension formulas**: even = 2n²+n+1, odd = 4n, total = 2n²+5n+1.

| n | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

---

## `oscillator_generators`

```json
{
  "standard_fermion": {
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± satisfying CAR: {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k = 1,...,n"
  }
}
```

**General pattern** (arbitrary n): `standard_fermion.count = 2`, `standard_fermion.labels = ["a_1_p", "a_1_m"]` (constant); `bosons.count = 2n`, `bosons.labels = ["b_1_p", "b_1_m", ..., "b_n_p", "b_n_m"]`.

> **Compatibility with B(m,n)**: Key renamed `supplementary_fermion` → `standard_fermion`. Content differs: B uses `a_0` with `a_0^2 = 1/2`; C uses `a_1_p`, `a_1_m` with CAR.

---

## `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermionic pair",
    "relations": {
      "cross":      "{a_1^-, a_1^+} = 1",
      "same_plus":  "{a_1^+, a_1^+} = 0",
      "same_minus": "{a_1^-, a_1^-} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type":      "[b_i^±, b_j^±] = 0  for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

> **Compatibility with B(m,n)**: Key renamed `supplementary_fermion_relation` → `standard_fermion_anticommutators`. The `bosonic_commutators` and `mixed_commutators` sub-objects are structurally identical.

---

## `central_elements`

New top-level key for C(n+1) (also applicable to B(m,n) for consistency):

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relation": "kappa^2 = 0",
    "description": "Odd central element of the Bakalov-Sullivan extension. Appears first in the PBW ordering."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "K = 1",
    "description": "Even central identity element. Identified with the scalar 1 in all current applications; excluded from PBW basis and structure constant computations."
  }
}
```

---

## `basis`

PBW ordering convention (Fermionic-first, Option A, decided in Issue I01-1):

```
κ  <  [odd generators]  <  [even generators]
```

Concrete example for C(2), n = 1:

```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p", "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: E_eps1_del{k}_{pp/pm/mp/mm} k=1..n] < [even: H_1..H_{n+1}, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]  (K=1 excluded)"
}
```

Concrete example for C(3), n = 2:

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: E_eps1_del{k}_{pp/pm/mp/mm} k=1..n] < [even: H_1..H_{n+1}, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]  (K=1 excluded)"
}
```

See `handover/notation.md` §5 for the complete PBW orderings for C(2), C(3), and C(4).

---

## `parity`

Concrete example for C(2), n = 1:

```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

General rule: all `H_k` and `E_del{...}` are parity 0; all `E_eps1_del{k}_{...}` are parity 1.

---

## `generator_realization`

Oscillator PBW ordering within realizations: `a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m`.

Concrete example for C(2), n = 1:

```json
{
  "description": "Standard form with PBW ordering of oscillators",
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
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_1^+ b_1^- - 1/2",
      "parity": 0,
      "note": "Terminal Cartan (k = n+1); constant -1/2 is intrinsic to the Frappat formula"
    },
    "E_eps1_del1_pp": {
      "standard_form": [{"words": ["a_1_p", "b_1_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    },
    "E_eps1_del1_pm": {
      "standard_form": [{"words": ["a_1_p", "b_1_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^-",
      "parity": 1
    },
    "E_eps1_del1_mp": {
      "standard_form": [{"words": ["a_1_m", "b_1_p"], "coeff": "1"}],
      "frappat_form": "a_1^- b_1^+",
      "parity": 1
    },
    "E_eps1_del1_mm": {
      "standard_form": [{"words": ["a_1_m", "b_1_m"], "coeff": "1"}],
      "frappat_form": "a_1^- b_1^-",
      "parity": 1
    },
    "E_2del1_p": {
      "standard_form": [{"words": ["b_1_p", "b_1_p"], "coeff": "1"}],
      "frappat_form": "(b_1^+)^2",
      "parity": 0,
      "note": "Convention: 1/2 factor from Frappat absorbed into normalization"
    },
    "E_2del1_m": {
      "standard_form": [{"words": ["b_1_m", "b_1_m"], "coeff": "1"}],
      "frappat_form": "(b_1^-)^2",
      "parity": 0,
      "note": "Convention: 1/2 factor from Frappat absorbed into normalization"
    }
  }
}
```

---

## `structure_constants`

Non-zero graded brackets [X, Y} stored as a list. Values are computed by `build_C_structure_constants.py`.

Format:

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

The `sign_rule: "graded"` field indicates that the graded Jacobi identity and the graded symmetry rule `[X, Y} = -(-1)^{p(X)p(Y)} [Y, X}` are used throughout.

---

## `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017), arXiv:1612.09400",
    "Aoi (2026), On the triviality of inhomogeneous deformations of osp(1|2n)"
  ]
}
```

---

## Compatibility Map: B(m,n) v5.0 → C(n+1) v5.0

| Schema 1 key | B(m,n) | C(n+1) | Change |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | None |
| `algebra.family` | `"B"` | `"C"` | Value |
| `algebra.m` | `0` | `1` | Value |
| `algebra.dimension_formula` | `osp(2m+1\|2n)` | `osp(2m\|2n)` | Value |
| `oscillator_generators` | key: `supplementary_fermion` | key: `standard_fermion` | Key rename + content |
| `oscillator_relations` | key: `supplementary_fermion_relation` | key: `standard_fermion_anticommutators` | Key rename + content |
| `central_elements` | absent | new top-level key | Addition |
| `basis.odd` count | 2n generators | 4n generators | Count + labels |
| `basis.odd` labels | `E_del{k}_p/m` | `E_eps1_del{k}_pp/pm/mp/mm` | Labels |
| `parity` odd generators | `E_del{k}_p/m` | `E_eps1_del{k}_{...}` | Labels |
| `generator_realization.ordering` | starts with `a_0` | starts with `a_1_p, a_1_m` | First entries |
| `structure_constants` | computed for B | computed for C | Values |
| `metadata.generated_by` | `build_B_structure_constants.py` | `build_C_structure_constants.py` | Value |
