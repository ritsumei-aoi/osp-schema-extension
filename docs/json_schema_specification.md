# JSON Schema Specification v5.0 (C(n+1) Extension)

This document extends the B(0,n) JSON schema specification to accommodate the $C(n+1) = \mathfrak{osp}(2|2n)$ algebra family.

## 1. Top-Level Structure

The JSON structure remains identical to B(0,n), with the addition of `central_elements` as a top-level key:

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

## 2. Algebra Field

```json
{
  "algebra": {
    "family": "C",
    "m": 1,
    "n": "<bosonic rank n>",
    "cartan_type": "C(<n+1>)",
    "alternative_notation": {
      "osp": "osp(2|2n)",
      "dimension_formula": "osp(2m|2n) with m=1"
    },
    "dimension": {
      "total": "<2*n^2 + 5*n + 1>",
      "even": "<2*n^2 + n + 1>",
      "odd": "<4*n>"
    }
  }
}
```

## 3. Oscillator Generators

We replace `supplementary_fermion` with `fermions`.

```json
{
  "oscillator_generators": {
    "fermions": {
      "m": 1,
      "labels": ["a_1_p", "a_1_m"],
      "description": "Standard fermionic pair"
    },
    "bosons": {
      "count": "<2n>",
      "n": "<n>",
      "labels": ["b_1_p", "b_1_m", "...", "b_n_p", "b_n_m"],
      "description": "Bosonic oscillators b_i^± with i=1,...,n"
    }
  }
}
```

## 4. Oscillator Relations

We replace `supplementary_fermion_relation` with `standard_fermion_anticommutators`.

```json
{
  "oscillator_relations": {
    "standard_fermion_anticommutators": {
      "description": "CAR for standard fermions",
      "relation": "{a_1^-, a_1^+} = 1"
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
}
```

## 5. Central Elements

A new top-level key for central elements.

```json
{
  "central_elements": {
    "kappa": {
      "parity": 1,
      "description": "Nilpotent odd central element"
    },
    "K": {
      "parity": 0,
      "description": "Identity central element"
    }
  }
}
```

## 6. File Naming Conventions

The file naming convention is defined based on the bosonic rank $n$ (so for C(n+1), the prefix is `C_n`):
- `C_{n}_structure.json`
- `C_{n}_gamma.json`
- `C_{n}_evaluated_<gb>.json`
- `C_{n}_coboundary_<gb>.json`

## Compatibility with B(m,n) Schema
- The top-level schema remains consistent.
- `central_elements` is explicitly hoisted to a top-level key instead of being implicitly managed.
- Instead of `supplementary_fermion`, parsers can identify the presence of `fermions` to deduce the representation.
