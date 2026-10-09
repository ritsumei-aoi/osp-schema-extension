# C(n+1) JSON Schema Specification — v5.0

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n) structure
constants. It extends the B(0,n) v5.0 base schema (see `math/B0n_schema_v5.md`)
and must be read alongside the mathematical definitions in `math/Cn1_definition.md`,
`math/C_inhomogeneous_definition.md`, and `math/C_coboundary_definition.md`.

Notation conventions and PBW ordering are recorded in `../handover/notation.md`.

---

## File Naming Convention

| Algebra | Bosonic rank n | Schema 1 | Schema 2 | Schema 3 | Schema 4 |
|---|---|---|---|---|---|
| C(2) = osp(2\|2) | 1 | `C_1_structure.json` | `C_1_gamma.json` | `C_1_evaluated_{gb}.json` | `C_1_coboundary_{gb}.json` |
| C(3) = osp(2\|4) | 2 | `C_2_structure.json` | `C_2_gamma.json` | `C_2_evaluated_{gb}.json` | `C_2_coboundary_{gb}.json` |
| C(4) = osp(2\|6) | 3 | `C_3_structure.json` | `C_3_gamma.json` | `C_3_evaluated_{gb}.json` | `C_3_coboundary_{gb}.json` |

`n` is the bosonic rank (number of bosonic oscillator pairs b_k^±). C(n+1)
corresponds to osp(2|2n).

---

## 4-Layer Architecture

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_n_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_n_gamma.json` | Inhomogeneous deformation (γ-structure), gb parameters |
| Schema 3 | `C_n_evaluated_{gb}.json` | Numerically evaluated structure constants for specific gb values |
| Schema 4 | `C_n_coboundary_{gb}.json` | Coboundary data for triviality verification |

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

The key `central_elements` is new relative to B(0,n) v5.0 and is required for
all C(n+1) schemas.

---

### `schema_version`

```json
"schema_version": "5.0"
```

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
    "total": 19,
    "even": 11,
    "odd": 8,
    "formulas": {
      "even": "2*n^2 + n + 1",
      "odd": "4*n",
      "total": "2*n^2 + 5*n + 1"
    }
  }
}
```

`cartan_type` follows Kac notation: C(n+1) for bosonic rank n.
`m` is fixed at 1 for all C-family schemas.

**Dimension table**:

| n | Algebra | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

---

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic oscillator pair a_1^± satisfying CAR {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n satisfying CCR [b_k^-, b_l^+] = delta_{kl}"
  }
}
```

The `supplementary_fermion` key used in B(0,n) is absent. The `fermions.m`
field records the fermionic rank (= 1 for all C(n+1)).

For general n, `bosons.count` = 2n and `bosons.labels` = `["b_1_p","b_1_m",...,"b_n_p","b_n_m"]`.

---

### `oscillator_relations`

```json
{
  "fermionic_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermionic pair",
    "relations": {
      "main": "{a_1^-, a_1^+} = 1",
      "same_sign_p": "{a_1^+, a_1^+} = 0",
      "same_sign_m": "{a_1^-, a_1^-} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_k^±, b_l^±] = 0 for all k, l",
      "conjugate_pair": "[b_k^-, b_l^+] = delta_{kl}"
    }
  },
  "mixed_commutators": {
    "description": "Cross-type relations in the undeformed algebra",
    "fermion_boson": "[b_k^±, a_1^±] = 0"
  }
}
```

> **Note**: The deformed relation `[b_j^s, a_1^σ] = −gb_{σ,j,s}·κ` belongs
> to Schema 2 only. Schema 1 always records the undeformed algebra.

---

### `central_elements`

Top-level key, required for all C(n+1) schemas.

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "properties": ["kappa^2 = 0", "central in g-tilde"],
    "description": "Odd nilpotent central element of the extension; appears as coefficient in deformed brackets in Schema 2"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "properties": ["even central element", "K = 1 in all current applications"],
    "description": "Even central identity element; not a PBW basis element and excluded from basis lists"
  }
}
```

---

### `basis`

PBW ordering (approved in Issue I01-1, Option 1 — fermionic-oscillator primary):

```
κ  <  [a_1^+ block]  <  [a_1^- block]  <  [even generators]
```

Within the a_1^+ block (k = 1…n):
```
E_eps1_del1_pp, …, E_eps1_deln_pp,
E_eps1_del1_pm, …, E_eps1_deln_pm
```

Within the a_1^− block:
```
E_eps1_del1_mp, …, E_eps1_deln_mp,
E_eps1_del1_mm, …, E_eps1_deln_mm
```

Within even generators:
```
H_1, …, H_{n+1}  <  [positive roots]  <  [negative roots]  <  [mixed roots]
```

Positive roots: E_2del{k}_p (k=1..n), E_del{i}_del{j}_pp (i<j, lex order).
Negative roots: E_2del{k}_m (k=1..n), E_del{i}_del{j}_mm (i<j, lex order).
Mixed roots: E_del{i}_del{j}_pm (i<j), E_del{i}_del{j}_mp (i<j).

**n=1, C(2)**:
```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: kappa < [a_1^+ block] < [a_1^- block] < [even]  (K=1 excluded)"
}
```

**n=2, C(3)**:
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
  "ordering_convention": "PBW: kappa < [a_1^+ block] < [a_1^- block] < [even]  (K=1 excluded)"
}
```

**n=3, C(4)**:
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
  "ordering_convention": "PBW: kappa < [a_1^+ block] < [a_1^- block] < [even]  (K=1 excluded)"
}
```

---

### `parity`

All odd generators (ε-roots) carry parity 1; all even generators carry parity 0.

**n=2, C(3)** (complete):
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

Oscillator PBW ordering: `a_1_p < a_1_m < b_1_p < b_1_m < … < b_n_p < b_n_m`.

#### Cartan generators

| Generator | `standard_form` | `frappat_form` |
|---|---|---|
| `H_1` | `[a_1_p, a_1_m]` ×1, `[b_1_p, b_1_m]` ×1 | a_1^+ a_1^− + b_1^+ b_1^− |
| `H_k` (2≤k≤n) | `[b_{k-1}_p, b_{k-1}_m]` ×1, `[b_k_p, b_k_m]` ×−1 | b_{k-1}^+ b_{k-1}^− − b_k^+ b_k^− |
| `H_{n+1}` | `[b_n_p, b_n_m]` ×−1, `[]` ×−1/2 | −b_n^+ b_n^− − 1/2 |

#### Odd generators

| Generator | `standard_form` | `frappat_form` |
|---|---|---|
| `E_eps1_del{k}_pp` | `[a_1_p, b_k_p]` ×1 | a_1^+ b_k^+ |
| `E_eps1_del{k}_pm` | `[a_1_p, b_k_m]` ×1 | a_1^+ b_k^− |
| `E_eps1_del{k}_mp` | `[a_1_m, b_k_p]` ×1 | a_1^− b_k^+ |
| `E_eps1_del{k}_mm` | `[a_1_m, b_k_m]` ×1 | a_1^− b_k^− |

#### Even root generators

| Generator | `standard_form` | `frappat_form` |
|---|---|---|
| `E_2del{k}_p` | `[b_k_p, b_k_p]` ×1 | (b_k^+)^2 |
| `E_2del{k}_m` | `[b_k_m, b_k_m]` ×1 | (b_k^−)^2 |
| `E_del{i}_del{j}_pp` (i<j) | `[b_i_p, b_j_p]` ×1 | b_i^+ b_j^+ |
| `E_del{i}_del{j}_mm` (i<j) | `[b_i_m, b_j_m]` ×1 | b_i^− b_j^− |
| `E_del{i}_del{j}_pm` (i<j) | `[b_i_p, b_j_m]` ×1 | b_i^+ b_j^− |
| `E_del{i}_del{j}_mp` (i<j) | `[b_i_m, b_j_p]` ×1 | b_i^− b_j^+ |

#### Full JSON example (n=2, representative entries)

```json
{
  "description": "PBW-ordered oscillator words; ordering: a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m",
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
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_1^+ b_1^- - b_2^+ b_2^-",
      "parity": 0
    },
    "H_3": {
      "standard_form": [
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_2^+ b_2^- - 1/2",
      "parity": 0,
      "note": "Terminal Cartan; constant -1/2 from sp(2n) normalization"
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
    },
    "E_2del{k}_p": {
      "standard_form": [{"words": ["b_k_p", "b_k_p"], "coeff": "1"}],
      "frappat_form": "(b_k^+)^2",
      "parity": 0
    },
    "E_2del{k}_m": {
      "standard_form": [{"words": ["b_k_m", "b_k_m"], "coeff": "1"}],
      "frappat_form": "(b_k^-)^2",
      "parity": 0
    },
    "E_del{i}_del{j}_pp": {
      "standard_form": [{"words": ["b_i_p", "b_j_p"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^+",
      "parity": 0,
      "note": "i < j"
    },
    "E_del{i}_del{j}_mm": {
      "standard_form": [{"words": ["b_i_m", "b_j_m"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^-",
      "parity": 0,
      "note": "i < j"
    },
    "E_del{i}_del{j}_pm": {
      "standard_form": [{"words": ["b_i_p", "b_j_m"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^-",
      "parity": 0,
      "note": "i < j"
    },
    "E_del{i}_del{j}_mp": {
      "standard_form": [{"words": ["b_i_m", "b_j_p"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^+",
      "parity": 0,
      "note": "i < j"
    }
  }
}
```

---

### `structure_constants`

Format is identical to B(0,n) v5.0. Actual values are populated by
`build_C_structure_constants.py` for each n; only the format is specified here.

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

Each entry records a non-zero graded bracket [X, Y} = coeff · Z.
`sign_rule: "graded"` means the super-Jacobi identity and graded sign convention
are used throughout.

---

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "arXiv:hep-th/9607161"
  ]
}
```

---

## Compatibility with B(0,n) v5.0

| Field | B(0,n) v5.0 | C(n+1) v5.0 | Status |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | identical |
| `algebra.family` | `"B"` | `"C"` | differs by design |
| `algebra.m` | `0` | `1` | differs by design |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | key renamed |
| `oscillator_relations` | `a_0^2 = 1/2` | CAR `{a_1^-, a_1^+} = 1` | semantically replaced |
| `central_elements` | absent | top-level key (required) | new key |
| `basis` structure | `even`/`odd` lists + `ordering_convention` | same | identical |
| `parity` format | `{label: 0 or 1}` | `{label: 0 or 1}` | identical |
| `generator_realization` format | `{standard_form, frappat_form, parity}` | same | identical |
| `structure_constants` format | `[{X, Y, Z, coeff, sign_rule}]` | same | identical |
| `metadata` format | same | same | identical |

---

## Change Log

| Date | Issue | Change |
|---|---|---|
| 2026-10-09 | I01-1 | PBW ordering (Option 1, fermionic-oscillator primary) approved |
| 2026-10-09 | I02-1 | Schema 1 field definitions for C(n+1) approved; this document created |
