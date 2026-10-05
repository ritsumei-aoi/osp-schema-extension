# C(n+1) v5.0 JSON Schema Specification

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n), extending the B(0,n) schema.

---

## Overview: 4-Layer Schema Architecture

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_{n}_evaluated.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_{n}_coboundary.json` | Coboundary data for triviality verification |

Where `n` is the bosonic rank: C(2) = osp(2|2) uses n=1, C(3) = osp(2|4) uses n=2, C(4) = osp(2|6) uses n=3.

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

**Dimension table**:

| n | even | odd | total | Algebra |
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
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^- with CAR"
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
    "description": "Canonical anticommutation relations for the standard fermionic pair",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "nilpotency": "(a_1^+)^2 = 0, (a_1^-)^2 = 0"
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

**Compatibility note**: B(0,n) uses `supplementary_fermion_relation` with `a_0^2 = 1/2`; C(n+1) uses `standard_fermion_anticommutators` with the standard CAR pair.

### `central_elements`

This is a **top-level key** in C(n+1), recording the central elements of the extended algebra.

```json
{
  "kappa": {
    "parity": 1,
    "nilpotency": "kappa^2 = 0",
    "description": "Odd central element for abelian extension"
  },
  "K": {
    "parity": 0,
    "value": "1",
    "description": "Even central identity element; identified with scalar 1"
  }
}
```

### `basis`

Follows PBW ordering: κ < [odd] < [even]. K is excluded (identified with 1).

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
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
}
```

### `parity`

Maps each generator label to its parity (0 = even, 1 = odd).

### `generator_realization`

Each generator expressed as a sum of oscillator words with rational coefficients.

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
    "E_eps1_del{k}_pp": {
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

## Compatibility Summary: B(0,n) vs C(n+1)

| Key | B(0,n) | C(n+1) |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `oscillator_generators` | `supplementary_fermion` (a_0) | `fermions` (a_1_p, a_1_m) |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` |
| `central_elements` | present | present (top-level) |
| `basis.odd` | `E_del{k}_p/m` (2n) | `E_eps1_del{k}_{ss}` (4n) |
| Dimension (even) | $2n^2+n$ | $2n^2+n+1$ |
| Dimension (odd) | $2n$ | $4n$ |
| File naming | `B_{n}_*.json` | `C_{n}_*.json` |
