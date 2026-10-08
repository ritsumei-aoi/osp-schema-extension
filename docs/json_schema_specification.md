# JSON Schema Specification for C(n+1)

This document outlines the v5.0 Schema 1 extension for $C(n+1) = \mathfrak{osp}(2|2n)$.

## 1. Algebra Field
```json
"algebra": {
  "family": "C",
  "m": 1,
  "n": <n>,
  "cartan_type": "C(<n>+1)",
  "alternative_notation": {
    "osp": "osp(2|2n)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": <2n^2 + 5n + 1>,
    "even": <2n^2 + n + 1>,
    "odd": <4n>
  }
}
```

## 2. Oscillator Generators
```json
"oscillator_generators": {
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic CAR pair a_1^±"
  },
  "bosons": {
    "count": <2n>,
    "n": <n>,
    "labels": ["b_1_p", "b_1_m", ...],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

## 3. Oscillator Relations
```json
"oscillator_relations": {
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermionic oscillators",
    "relations": {
      "same_type": "{a_1^±, a_1^±} = 0",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
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

## 4. Central Elements
Top-level key to store the central elements required by the algebra.
```json
"central_elements": {
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "description": "Odd central element"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central element (typically identified with scalar 1)"
  }
}
```

## 5. File Naming Convention
Files for Schema 1 (algebra structure) are named according to the bosonic rank $n$:
- `C_1_structure.json` for C(2) = osp(2|2)
- `C_2_structure.json` for C(3) = osp(2|4)
- `C_3_structure.json` for C(4) = osp(2|6)
- and so on.

## Compatibility with B(m,n) Schema
- The structure retains the basic architecture of the B(0,n) schema.
- The `supplementary_fermion` block is completely replaced by `fermions` and standard CAR.
- The `central_elements` is explicitly added as a top-level key rather than just implicitly present.
