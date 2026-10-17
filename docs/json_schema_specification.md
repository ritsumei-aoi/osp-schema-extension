# JSON Schema Specification for $C(n+1) = \mathfrak{osp}(2|2n)$ and $B(0,n) = \mathfrak{osp}(1|2n)$ (v5.0)

This document provides the complete v5.0 JSON schema specification for Lie superalgebras in the $C(n+1)$ family, with backward-compatibility notes for the base case $B(0,n)$.

---

## 1. Overview & Multi-Layer Architecture

The Lie superalgebra data is organized into a four-layer schema:

| Layer | File Pattern | Purpose |
|---|---|---|
| **Schema 1** | `C_{n}_structure.json` | Undeformed Lie superalgebra structure: basis, parity, oscillator realization, graded structure constants |
| **Schema 2** | `C_{n}_gamma.json` | Inhomogeneous deformation parameters ($\mathrm{gb}$-matrix) and deformed cocycle structure constants |
| **Schema 3** | `C_{n}_evaluated_<gb>.json` | Numerically evaluated structure constants at concrete deformation parameter values |
| **Schema 4** | `C_{n}_coboundary_<gb>.json` | Coboundary operator $\delta f$, linear map $f$, and triviality verification data |

### File Naming Convention
Files are indexed by the bosonic rank $n$ (where $C(n+1) = \mathfrak{osp}(2|2n)$):
- $n=1$: $C(2) = \mathfrak{osp}(2|2) \implies$ `C_1_structure.json`
- $n=2$: $C(3) = \mathfrak{osp}(2|4) \implies$ `C_2_structure.json`
- $n=3$: $C(4) = \mathfrak{osp}(2|6) \implies$ `C_3_structure.json`

---

## 2. Schema 1: Undeformed Algebra Structure

### 2.1 Top-Level JSON Keys

A Schema 1 document contains the following top-level keys:
- `schema_version`: String `"5.0"`.
- `algebra`: Object specifying family, ranks $m$ and $n$, Cartan type, alternative notation, and dimension formulas.
- `central_elements`: Object specifying central elements $\kappa$ and $K$.
- `oscillator_generators`: Object specifying fermionic and bosonic oscillator generators.
- `oscillator_relations`: Object specifying CAR, CCR, and undeformed commutators.
- `basis`: Object specifying even basis, odd basis, and PBW ordering convention.
- `parity`: Object mapping every generator label to its $\mathbb{Z}_2$-parity ($0$ or $1$).
- `generator_realization`: Object defining the oscillator realization of all basis generators in standard PBW form.
- `structure_constants`: Array of non-zero graded Lie brackets.
- `metadata`: Object containing generation metadata and references.

---

### 2.2 Field Definitions & Detailed Schema

#### 1. `algebra`
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

#### 2. `central_elements`
Dedicated top-level key defining the central extension parameter $\kappa$ and central scalar $K$:
```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotent": true,
    "relation": "kappa^2 = 0",
    "description": "Odd central extension parameter for inhomogeneous deformation; acts trivially on g"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "scalar_value": 1,
    "description": "Central identity element; identified with scalar 1 and excluded from PBW basis"
  }
}
```

#### 3. `oscillator_generators`
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard CAR fermionic pair a_1^± with parity 1"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic CCR oscillators b_i^± with i=1,...,n and parity 0"
  }
}
```

#### 4. `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for fermionic oscillators",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "nilpotency": "(a_1^+)^2 = 0, (a_1^-)^2 = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations (CCR) for bosonic oscillators",
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

#### 5. `basis`
PBW ordering follows **Option A (Bosonic Mode Block Ordering)**:
$$\kappa < [\text{odd basis}] < [\text{even basis}]$$
where the odd basis is grouped primarily by the bosonic oscillator index $k \in \{1, \dots, n\}$, and secondarily in `pp, pm, mp, mm` order:

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_pp", "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm",
    "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd: Mode Block (eps1_del{k}_pp/pm/mp/mm)] < [even: Cartan, Long roots, Short roots] (K = 1 is excluded)"
}
```

#### 6. `parity`
Mapping of each generator symbol to its parity ($0$ for even, $1$ for odd):
```json
{
  "H_1": 0, "H_2": 0, "H_3": 0,
  "E_2del1_p": 0, "E_2del2_p": 0,
  "E_2del1_m": 0, "E_2del2_m": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_mm": 0,
  "E_del1_del2_pm": 0, "E_del1_del2_mp": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1, "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1,
  "E_eps1_del2_pp": 1, "E_eps1_del2_pm": 1, "E_eps1_del2_mp": 1, "E_eps1_del2_mm": 1
}
```

#### 7. `generator_realization`
Internal oscillator ordering is explicitly stated in `ordering`: `a_1_p, a_1_m, b_1_p, b_1_m, ...`.
Each generator is expressed in PBW standard form as a sum of normal-ordered oscillator words with rational coefficients:
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
      "parity": 0
    },
    "E_2del1_p": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "(b_1^+)^2",
      "parity": 0
    },
    "E_del1_del2_pp": {
      "standard_form": [
        {"words": ["b_1_p", "b_2_p"], "coeff": "1"}
      ],
      "frappat_form": "b_1^+ b_2^+",
      "parity": 0
    },
    "E_eps1_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    },
    "E_eps1_del1_pm": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^-",
      "parity": 1
    },
    "E_eps1_del1_mp": {
      "standard_form": [
        {"words": ["a_1_m", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_1^+",
      "parity": 1
    },
    "E_eps1_del1_mm": {
      "standard_form": [
        {"words": ["a_1_m", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_1^-",
      "parity": 1
    }
  }
}
```

#### 8. `structure_constants`
Array of non-zero graded Lie brackets:
$$[X, Y\} = \sum_Z c_{XY}^Z Z$$
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

#### 9. `metadata`
```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "2026-10-17",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## 3. Backward Compatibility with $B(0,n) = \mathfrak{osp}(1|2n)$

| Schema Key / Concept | $B(0,n)$ (v5.0 Base) | $C(n+1)$ (Extended) | Compatibility Design |
|---|---|---|---|
| `algebra.family` | `"B"` | `"C"` | Distinguishes root system family |
| `algebra.m` | `0` | `1` | Unified parameter $m$ ($0$ for $B$, $1$ for $C$) |
| `algebra.dimension` | formulas: $2n^2+n$ even, $2n$ odd | formulas: $2n^2+n+1$ even, $4n$ odd | Explicit dimension formula subkey in both |
| `central_elements` | Implicit in notes or subkeys | Dedicated top-level key (`kappa`, `K`) | Formalized for uniform parser handling |
| `oscillator_generators` | `supplementary_fermion` (`a_0`) | `fermions` (`a_1_p`, `a_1_m`) | Differentiates CAR pair vs single auxiliary fermion |
| `oscillator_relations` | $a_0^2 = \frac{1}{2}$ | $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$ | Standard algebra-specific anticommutation |
| Odd Generators | `E_del{k}_{p/m}` | `E_eps1_del{k}_{pp/pm/mp/mm}` | Distinct naming prevents collision and reflects roots |
| PBW Ordering | $\kappa < \text{odd} < \text{even}$ | $\kappa < \text{odd} < \text{even}$ | Global macro-ordering is identical |
