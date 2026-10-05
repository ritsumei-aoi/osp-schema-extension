# C(n+1) v5.0 JSON Schema Specification

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n), extended from the B(0,n) schema defined in `docs/math/B0n_schema_v5.md`.

---

## Overview: 4-Layer Schema Architecture

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_{n}_evaluated_{gb}.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_{n}_coboundary_{gb}.json` | Coboundary data for triviality verification |

File naming: `n` is the bosonic rank. C(2)=osp(2|2) uses `C_1_*.json`, C(3)=osp(2|4) uses `C_2_*.json`, C(4)=osp(2|6) uses `C_3_*.json`.

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

### `schema_version`

```json
"schema_version": "5.0"
```

### `algebra`

```json
{
  "family": "C",
  "m": 1,
  "n": <bosonic_rank>,
  "cartan_type": "C(<n+1>)",
  "alternative_notation": {
    "osp": "osp(2|<2n>)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": "<2n^2+5n+1>",
    "even": "<2n^2+n+1>",
    "odd": "<4n>"
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
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^± with CAR relations"
  },
  "bosons": {
    "count": "<2n>",
    "n": "<n>",
    "labels": ["b_1_p", "b_1_m", ..., "b_n_p", "b_n_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

**Compatibility note**: B(0,n) uses `supplementary_fermion` with a single `a_0`; C(n+1) replaces this with `fermions` containing the standard pair `a_1_p`, `a_1_m`.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for standard fermionic pair",
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
  "K": {
    "parity": 0,
    "description": "Central identity element (= 1 in all applications)",
    "value": 1
  },
  "kappa": {
    "parity": 1,
    "description": "Nilpotent odd central element, kappa^2 = 0",
    "nilpotent": true
  }
}
```

### `basis`

```json
{
  "even": ["H_1", ..., "H_{n+1}", "E_2del1_p", ..., "E_2deln_p",
           "E_del{i}_del{j}_pp (i<j)", ...,
           "E_2del1_m", ..., "E_2deln_m",
           "E_del{i}_del{j}_mm (i<j)", ...,
           "E_del{i}_del{j}_pm (i<j)", ...,
           "E_del{i}_del{j}_mp (i<j)", ...],
  "odd": ["E_eps_del1_pp", ..., "E_eps_deln_pp",
          "E_eps_del1_pm", ..., "E_eps_deln_pm",
          "E_eps_del1_mp", ..., "E_eps_deln_mp",
          "E_eps_del1_mm", ..., "E_eps_deln_mm"],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
}
```

### `parity`

Maps each generator label to its parity (0 for even, 1 for odd).

### `generator_realization`

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
    "E_eps_del{k}_pp": {
      "standard_form": [{"words": ["a_1_p", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1
    },
    "E_eps_del{k}_pm": {
      "standard_form": [{"words": ["a_1_p", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^-",
      "parity": 1
    },
    "E_eps_del{k}_mp": {
      "standard_form": [{"words": ["a_1_m", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^+",
      "parity": 1
    },
    "E_eps_del{k}_mm": {
      "standard_form": [{"words": ["a_1_m", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^-",
      "parity": 1
    }
  }
}
```

Even root generators follow the same pattern as B(0,n): `E_2del{k}_p/m` uses $(b_k^\pm)^2$, and `E_del{i}_del{j}_{ss}` uses $b_i^s b_j^s$.

### `structure_constants`

Non-zero graded brackets $[X, Y\}$ stored as a list:

```json
[
  {
    "X": "<generator_label>",
    "Y": "<generator_label>",
    "Z": "<generator_label>",
    "coeff": "<rational>",
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

## Compatibility with B(m,n) Schema

| Key | B(0,n) | C(n+1) | Change |
|---|---|---|---|
| `algebra.family` | `"B"` | `"C"` | Family identifier |
| `algebra.m` | `0` | `1` | Fermionic rank |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | Fermionic sector |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | CAR vs $a_0^2=1/2$ |
| `central_elements` | top-level key | top-level key | Same structure |
| `basis.odd` | $2n$ generators (`E_del{k}_p/m`) | $4n$ generators (`E_eps_del{k}_{ss}`) | Doubled odd sector |
| `basis.even` | $2n^2+n$ generators | $2n^2+n+1$ generators | Extra Cartan from $\mathfrak{so}(2)$ |
