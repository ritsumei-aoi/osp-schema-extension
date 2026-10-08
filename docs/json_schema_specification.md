# JSON Schema Specification for C(n+1) (Schema 1 v5.0 Extension)

This document specifies the fields required for the C(n+1) = osp(2|2n) JSON structure schema, extending the B(0,n) v5.0 schema.

## 1. File Naming Convention
The JSON schema files will be named `C_{n}_structure.json`, where `n` is the bosonic rank.
- C(2) (n=1) -> `C_1_structure.json`
- C(3) (n=2) -> `C_2_structure.json`
- C(4) (n=3) -> `C_3_structure.json`

## 2. Top-Level Field Updates

### `algebra`
Specifies the algebra family and properties.
```json
{
  "family": "C",
  "m": 1,
  "n": <n>,
  "cartan_type": "C(<n>+1)",
  "alternative_notation": {
    "osp": "osp(2|<2n>)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": <2*n^2 + 5*n + 1>,
    "even": <2*n^2 + n + 1>,
    "odd": <4*n>
  }
}
```

### `oscillator_generators`
Defines the fermionic and bosonic oscillators, removing the supplementary fermion.
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic oscillators a_i^± with i=1,...,m"
  },
  "bosons": {
    "count": <2*n>,
    "n": <n>,
    "labels": ["b_1_p", "b_1_m", ...],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

### `oscillator_relations`
Updates to canonical anticommutation relations (CAR).
```json
{
  "fermionic_anticommutators": {
    "description": "Canonical anticommutation relations for fermionic oscillators",
    "relations": {
      "same_type": "{a_i^±, a_j^±} = 0 for all i, j",
      "conjugate_pair": "{a_i^-, a_j^+} = δ_{ij}"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_k^±, b_l^±] = 0 for all k, l",
      "conjugate_pair": "[b_k^-, b_l^+] = δ_{kl}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^±, a_i^±] = 0"
  }
}
```

### `central_elements`
Added as a **top-level key** for the central extensions.
```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "description": "Odd central element"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central element (identified with scalar 1)"
  }
}
```

## 3. Compatibility with B(m,n) Schema
- The introduction of `fermions` replacing `supplementary_fermion` is a structural change. Parsers need to check the `algebra.family` field (C vs B) and handle the `fermions` list accordingly.
- The `central_elements` as a top-level key should be safely ignored by older B(0,n) parsers if not strictly validated, or the older schema parser should be updated to tolerate it.
- PBW ordering structure (`basis.even`, `basis.odd`, `basis.ordering_convention`) remains exactly the same (`[odd] < [even]`), ensuring structure constant loaders require zero changes.
