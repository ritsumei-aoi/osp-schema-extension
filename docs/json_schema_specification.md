# C(n+1) JSON Schema Specification (v5.0)

**Version**: 5.0  
**Finalized**: 2026-10-11 (Issue I02-1)  
**Algebra**: C(n+1) = osp(2|2n)  
**Reference**: Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000); arXiv:hep-th/9607161

---

## Overview

This document specifies the Schema 1 (algebra structure) fields for C(n+1) = osp(2|2n)
in the v5.0 4-layer JSON schema architecture. It extends the B(0,n) v5.0 schema
(see `docs/math/B0n_schema_v5.md`) to the C(n+1) case.

### 4-Layer Architecture

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_{n}_evaluated_<gb>.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_{n}_coboundary_<gb>.json` | Coboundary data for triviality verification |

where `n` is the **bosonic rank**:

| JSON file | Algebra | n |
|---|---|---|
| `C_1_structure.json` | C(2) = osp(2\|2) | 1 |
| `C_2_structure.json` | C(3) = osp(2\|4) | 2 |
| `C_3_structure.json` | C(4) = osp(2\|6) | 3 |

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

---

### `schema_version`

```json
"schema_version": "5.0"
```

Unchanged from B(0,n). Maintains consistency with the 4-layer v5.0 schema architecture.

---

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
    "even_formula": "2*n^2 + n + 1",
    "odd_formula": "4*n",
    "total_formula": "2*n^2 + 5*n + 1",
    "even": 11,
    "odd": 8,
    "total": 19
  }
}
```

*(Example shown for n=2, C(3). Substitute concrete values for each instance.)*

**Dimension table**:

| n | cartan_type | even | odd | total |
|---|---|---|---|---|
| 1 | "C(2)" | 4 | 4 | 8 |
| 2 | "C(3)" | 11 | 8 | 19 |
| 3 | "C(4)" | 22 | 12 | 34 |

**Compatibility with B(0,n)**: B(0,n) uses `"family": "B"`, `"m": 0`. Downstream code should branch on `algebra.family` to select C(n+1) vs B(0,n) logic.

---

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^- satisfying CAR: {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_k^+, b_k^- for k=1,...,n with CCR: [b_k^-, b_l^+] = delta_{kl}"
  }
}
```

*(Example shown for n=2. `bosons.count = 2*n` and `labels` expand accordingly.)*

**Labels by n**:

| n | fermion labels | boson labels |
|---|---|---|
| 1 | a_1_p, a_1_m | b_1_p, b_1_m |
| 2 | a_1_p, a_1_m | b_1_p, b_1_m, b_2_p, b_2_m |
| 3 | a_1_p, a_1_m | b_1_p, b_1_m, b_2_p, b_2_m, b_3_p, b_3_m |

**Compatibility with B(0,n)**: B(0,n) uses key `supplementary_fermion` (single `a_0`). C(n+1) uses key `fermions` (pair `a_1_p`, `a_1_m`). Parsers should branch on presence of `oscillator_generators.fermions` vs `oscillator_generators.supplementary_fermion`.

---

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for the standard fermionic pair",
    "relations": {
      "self_anticommutators": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations (CCR) for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^pm, b_j^pm] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^pm, a_1^pm] = 0  (bosons and fermions commute)"
  }
}
```

**Compatibility with B(0,n)**: B(0,n) has `supplementary_fermion_relation: "a_0 * a_0 = 1/2"`. C(n+1) replaces this with `standard_fermion_anticommutators` containing `{a_1^-, a_1^+} = 1`. The structural distinction is that a₀ satisfies a non-standard idempotent-like relation while a₁± satisfy standard CAR.

---

### `central_elements`

Top-level key (absent as a top-level key in B(0,n)):

```json
{
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central identity element; identified with scalar 1 in all current applications. Excluded from PBW basis. (Bakalov-Sullivan arXiv:1612.09400)"
  },
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotency": "kappa^2 = 0",
    "pbw_position": "smallest (precedes all basis elements)",
    "description": "Odd nilpotent central extension element. Deformation: a_1^2 maps to kappa * (sum of deformation parameters gb_{a_1, b_k^pm} * b_k^pm). Prepares for Schema 2 gamma-structure."
  }
}
```

**Rationale**: κ is odd (parity 1), nilpotent (κ²=0), and is the formal symbol of the inhomogeneous extension. K is even (parity 0) and serves as a bookkeeping element for the central identity. Both elements are referenced by the γ-structure in Schema 2.

---

### `basis`

PBW ordering (C(n+1) convention, Option A approved I01-1):

```
kappa  <  [odd block]  <  [even block]
```

Odd block (Option A): grouped by ε-sign (pp→pm→mp→mm), within each group ordered by bosonic index k.  
Even block: Cartans (H_1,…,H_{n+1}), then positive-type, then negative-type, then mixed.

**C(2), n=1** (4|4):
```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW Option A: kappa < [odd: pp then pm then mp then mm by k] < [even: Cartans, pos, neg, mixed]"
}
```

**C(3), n=2** (11|8):
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
  "ordering_convention": "PBW Option A: kappa < [odd] < [even]"
}
```

**C(4), n=3** (22|12):
```json
{
  "even": [
    "H_1", "H_2", "H_3", "H_4",
    "E_2del1_p", "E_2del2_p", "E_2del3_p",
    "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp",
    "E_2del1_m", "E_2del2_m", "E_2del3_m",
    "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm",
    "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm",
    "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"
  ],
  "ordering_convention": "PBW Option A: kappa < [odd] < [even]"
}
```

---

### `parity`

All even generators have parity 0; all odd generators have parity 1.

**Pattern**:
```json
{
  "H_k":                      0,
  "E_2delk_p":                0,
  "E_2delk_m":                0,
  "E_del{i}_del{j}_pp":       0,
  "E_del{i}_del{j}_mm":       0,
  "E_del{i}_del{j}_pm":       0,
  "E_del{i}_del{j}_mp":       0,
  "E_eps1_delk_pp":           1,
  "E_eps1_delk_pm":           1,
  "E_eps1_delk_mp":           1,
  "E_eps1_delk_mm":           1
}
```

**C(3), n=2** (concrete example):
```json
{
  "H_1": 0, "H_2": 0, "H_3": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_2del2_p": 0, "E_2del2_m": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_mm": 0,
  "E_del1_del2_pm": 0, "E_del1_del2_mp": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1,
  "E_eps1_del2_pp": 1, "E_eps1_del2_pm": 1,
  "E_eps1_del2_mp": 1, "E_eps1_del2_mm": 1
}
```

---

### `generator_realization`

Each generator expressed as oscillator words with rational coefficients under PBW ordering.

**Oscillator word ordering**: `a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < …`

```json
{
  "description": "Standard oscillator-word form under PBW ordering",
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
      "parity": 0,
      "note": "Terminal Cartan; constant -1/2 arises from H_{n+1} = -b_n^+ b_n^- - 1/2 (Frappat)"
    },
    "E_eps1_delk_pp": {
      "standard_form": [{"words": ["a_1_p", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1
    },
    "E_eps1_delk_pm": {
      "standard_form": [{"words": ["a_1_p", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^-",
      "parity": 1
    },
    "E_eps1_delk_mp": {
      "standard_form": [{"words": ["a_1_m", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^+",
      "parity": 1
    },
    "E_eps1_delk_mm": {
      "standard_form": [{"words": ["a_1_m", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^-",
      "parity": 1
    },
    "E_2delk_p": {
      "standard_form": [{"words": ["b_k_p", "b_k_p"], "coeff": "1/2"}],
      "frappat_form": "(1/2)(b_k^+)^2",
      "parity": 0
    },
    "E_2delk_m": {
      "standard_form": [{"words": ["b_k_m", "b_k_m"], "coeff": "1/2"}],
      "frappat_form": "(1/2)(b_k^-)^2",
      "parity": 0
    },
    "E_del{i}_del{j}_pp (i<j)": {
      "standard_form": [{"words": ["b_i_p", "b_j_p"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^+",
      "parity": 0
    },
    "E_del{i}_del{j}_mm (i<j)": {
      "standard_form": [{"words": ["b_i_m", "b_j_m"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^-",
      "parity": 0
    },
    "E_del{i}_del{j}_pm (i<j)": {
      "standard_form": [{"words": ["b_i_p", "b_j_m"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^-",
      "parity": 0
    },
    "E_del{i}_del{j}_mp (i<j)": {
      "standard_form": [{"words": ["b_i_m", "b_j_p"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^+",
      "parity": 0
    }
  }
}
```

---

### `structure_constants`

Non-zero graded brackets `[X, Y}` stored as a list. Placeholder for Schema 1 (to be computed in subsequent issues):

```json
"structure_constants": []
```

Format when populated (same as B(0,n)):
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
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017), arXiv:1612.09400",
    "Aoi (2026), docs/drafts/aoi2026_triviality_osp1_2n.tex"
  ]
}
```

---

## Compatibility Summary: C(n+1) vs B(0,n)

| Feature | B(0,n) Schema | C(n+1) Schema | Change |
|---|---|---|---|
| `algebra.family` | `"B"` | `"C"` | Changed |
| `algebra.m` | `0` | `1` | Changed |
| Even dim formula | `2n²+n` | `2n²+n+1` | Changed (+1 for so(2)) |
| Odd dim formula | `2n` | `4n` | Changed (×2, standard pair) |
| `oscillator_generators` fermion key | `supplementary_fermion` (a_0) | `fermions` (a_1_p, a_1_m) | Key renamed + expanded |
| `oscillator_relations` fermion key | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | Key renamed |
| Fermion relation | `a_0 * a_0 = 1/2` | `{a_1^-, a_1^+} = 1` | Standard CAR |
| `central_elements` | (schema note only) | Top-level key with K and kappa | Promoted to top-level |
| `basis.odd` labels | `E_del{k}_p/m` (2n) | `E_eps1_del{k}_pp/pm/mp/mm` (4n) | Expanded |
| `parity` odd entries | 2n entries | 4n entries | Expanded |
| Oscillator word prefix (odd) | `a_0` | `a_1_p` or `a_1_m` | Changed |
| File naming prefix | `B_{n}_` | `C_{n}_` | Changed |

**Parser branch point**: check `algebra.family` (`"B"` vs `"C"`) or presence of `oscillator_generators.fermions` vs `oscillator_generators.supplementary_fermion`.
