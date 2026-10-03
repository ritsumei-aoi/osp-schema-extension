# B(0,n) v5.0 JSON Schema Specification

This document specifies the v5.0 JSON schema used for B(0,n) = osp(1|2n)
structure constants. It serves as the **base schema** for the C(n+1) extension.

**Task for AI agents**: Read this specification to understand the schema
structure for B(0,n), then produce a **complete** equivalent schema for
C(n+1) = osp(2|2n) by applying the appropriate modifications described
in `Cn1_definition.md`. The output must be a fully populated schema —
not just a diff, but a complete, standalone specification for C(n+1).

---

## Overview: 4-Layer Schema Architecture

The JSON data for each algebra is organized into 4 layers of increasing
computational depth:

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `B_n_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `B_n_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `B_n_evaluated_<gb>.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `B_n_coboundary_<gb>.json` | Coboundary data for triviality verification |

For the C(n+1) extension, file naming uses `C_n_structure.json`, etc.
(where `n` is the bosonic rank, so C(2)=osp(2|2) is `C_1_structure.json`).

---

## Schema 1: Algebra Structure

### Top-Level Keys

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "oscillator_generators": { ... },
  "oscillator_relations": { ... },
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
  "family": "B",
  "m": 0,
  "n": 2,
  "cartan_type": "B(0,2)",
  "alternative_notation": {
    "osp": "osp(1|4)",
    "dimension_formula": "osp(2m+1|2n) with m=0"
  },
  "dimension": {
    "total": 14,
    "even": 10,
    "odd": 4
  }
}
```

**Dimension formulas** (B(0,n)): even = $2n^2+n$, odd = $2n$, total = $2n^2+3n$.

| $n$ | even | odd | total |
|---|---|---|---|
| 1 | 3 | 2 | 5 |
| 2 | 10 | 4 | 14 |
| 3 | 21 | 6 | 27 |

### `oscillator_generators`

```json
{
  "supplementary_fermion": {
    "label": "a_0",
    "parity": 1,
    "relation": "a_0^2 = 1/2",
    "description": "Auxiliary fermion; not a standard CAR pair."
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

> **For C(n+1)**: Replace `supplementary_fermion` with a standard fermionic
> pair `a_1_p`, `a_1_m` under a `standard_fermion` key with CAR relations.

### `oscillator_relations`

```json
{
  "supplementary_fermion_relation": {
    "description": "a_0^2 = 1/2 (not a standard anticommutator pair)",
    "relation": "a_0 * a_0 = 1/2"
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_0] = 0"
  }
}
```

> **For C(n+1)**: Replace `supplementary_fermion_relation` with
> `standard_fermion_anticommutators` containing `{a_1^-, a_1^+} = 1`.
> Add a new top-level key `central_elements` (see C(n+1) specification).

### `basis`

PBW ordering (B(0,n) convention):
```
κ < [odd: E_del{k}_p/m] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]
```

```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_del1_p", "E_del2_p",
    "E_del1_m", "E_del2_m"
  ],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded; see note below)"
}
```

> **Note on $K$**: The even central element $K$ (Bakalov–Sullivan, arXiv:1612.09400)
> is identified with the scalar 1 in all current applications. It does not appear
> as an independent basis element and is excluded from PBW ordering and basis lists.
> It is recorded in the `central_elements` JSON key for schema completeness only.

### `parity`

```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_2del2_p": 0, "E_2del2_m": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_mm": 0,
  "E_del1_del2_pm": 0, "E_del1_del2_mp": 0,
  "E_del1_p": 1, "E_del1_m": 1,
  "E_del2_p": 1, "E_del2_m": 1
}
```

### `generator_realization`

Each generator is expressed as a sum of oscillator words with rational coefficients.

```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_0, b_1_p, b_1_m, b_2_p, b_2_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_1^+ b_1^- - b_2^+ b_2^-",
      "parity": 0
    },
    "H_2": {
      "standard_form": [
        {"words": ["b_2_p", "b_2_m"], "coeff": "1"},
        {"words": [], "coeff": "1/2"}
      ],
      "frappat_form": "b_2^+ b_2^- + 1/2",
      "parity": 0,
      "note": "Terminal Cartan; includes constant from a_0^2 = 1/2"
    },
    "E_del{k}_p": {
      "standard_form": [
        {"words": ["a_0", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "a_0 b_k^+",
      "parity": 1
    },
    "E_del{k}_m": {
      "standard_form": [
        {"words": ["a_0", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "a_0 b_k^-",
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
    "Y": "E_del1_p",
    "Z": "E_del1_p",
    "coeff": "1",
    "sign_rule": "graded"
  }
]
```

### `metadata`

```json
{
  "generated_by": "build_B_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## Task: Producing the C(n+1) Extension

When producing the C(n+1) schema, apply the following changes to each key:

| Key | Change for C(n+1) |
|---|---|
| `algebra.family` | `"C"` |
| `algebra.m` | `1` |
| `algebra.dimension_formula` | `"osp(2m|2n)"`, even = $2n^2+n+1$, odd = $4n$ |
| `oscillator_generators` | Remove `supplementary_fermion`; add `fermions` key with `a_1_p`, `a_1_m` |
| `oscillator_relations` | Replace supplementary relation with CAR: `{a_1^-, a_1^+} = 1`; add `central_elements` key |
| `basis.odd` | Replace `E_del{k}_p/m` with `E_eps1_del{k}_pp/pm/mp/mm` (4n generators) |
| `parity` | Odd generators are `E_eps1_del{k}_{...}` |
| `generator_realization` | Replace `a_0` with `a_1_p`/`a_1_m` in oscillator words |
| `structure_constants` | Recompute all brackets under the new CAR relations |

**The output must be a complete, self-consistent schema** — not just the
changed fields, but all fields populated with correct values for C(n+1).
