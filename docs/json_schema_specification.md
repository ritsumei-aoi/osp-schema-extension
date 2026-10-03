# JSON Schema Specification: C(n+1) = osp(2|2n) Extension (v5.0)

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n), extending the B(0,n) base schema.

---

## File Naming Convention

| Layer | File Pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, generators, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_{n}_evaluated.json` | Numerically evaluated structure constants for specific gb values |
| Schema 4 | `C_{n}_coboundary.json` | Coboundary data for triviality verification |

**Where `n` is the bosonic rank** (number of bosonic oscillator pairs):
- C(2) = osp(2|2): `n=1` → `C_1_structure.json`
- C(3) = osp(2|4): `n=2` → `C_2_structure.json`
- C(4) = osp(2|6): `n=3` → `C_3_structure.json`

**Backward Compatibility**: B(m,n) schemas use `B_{n}_structure.json` with `family="B"`. C(n+1) uses `family="C"`. Both share the same v5.0 schema structure, differentiated by `algebra.family`.

---

## Schema 1: Algebra Structure (`C_{n}_structure.json`)

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

**Mandatory fields** (fixed for all runs):
- `"m": 1` (the m in osp(2m|2n), here m=1 for osp(2|2n))
- `"dimension_formula"` with `"even": "2*n^2 + n + 1"` and `"odd": "4*n"`

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
    "odd": 4,
    "even_formula": "2*n^2 + n + 1",
    "odd_formula": "4*n"
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

**Two mandatory keys**: `"fermions"` and `"bosons"` (replacing B(0,n)'s `"supplementary_fermion"`).

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a1p", "a1m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^- with CAR {a_1^-, a_1^+} = K"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b1p", "b1m"],
    "description": "Bosonic oscillators b_k^+/- with CCR [b_k^-, b_l^+] = delta_kl"
  }
}
```

### `oscillator_relations`

```json
{
  "fermionic_anticommutators": {
    "description": "Standard CAR for the fermionic pair",
    "relations": {
      "a1m_a1p": "{a1^-, a1^+} = K",
      "a1p_squared": "(a1^+)^2 = 0",
      "a1m_squared": "(a1^-)^2 = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations",
    "relations": {
      "same_type": "[b_i^+/-, b_j^+/-] = 0 for same sign",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_ij"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^+/-, a_1^+/-] = 0"
  }
}
```

### `central_elements`

**Top-level key** (mandatory, fixed for all runs):

```json
{
  "K": {
    "parity": 0,
    "description": "Even central identity element; K = 1 in all oscillator realizations",
    "note": "K does not appear as an independent basis element (identified with scalar 1)"
  },
  "kappa": {
    "parity": 1,
    "description": "Odd nilpotent central element; kappa^2 = 0",
    "note": "Appears as the coefficient in the inhomogeneous deformation bracket"
  }
}
```

### `basis`

PBW ordering: $\kappa < [\text{odd}] < [\text{even}]$ ($K$ excluded, see B(0,n) convention).

**Example for n=1 (C(2))**:
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
  "ordering_convention": "PBW: kappa < [odd: eps-roots] < [even: Cartan, positive, negative, mixed]"
}
```

**Example for n=2 (C(3))**:
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
  "ordering_convention": "PBW: kappa < [odd: eps-roots] < [even: Cartan, positive, negative, mixed]"
}
```

### `parity`

Each generator mapped to 0 (even) or 1 (odd).

```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

### `generator_realization`

```json
{
  "description": "Oscillator realizations in PBW order (a1p < a1m < b1p < b1m < ...)",
  "ordering": "a1p, a1m, b1p, b1m, ..., bnp, bnm",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a1p", "a1m"], "coeff": "1"},
        {"words": ["b1p", "b1m"], "coeff": "1"}
      ],
      "frappat_form": "a1^+ a1^- + b1^+ b1^-",
      "parity": 0
    },
    "H_{n+1}": {
      "standard_form": [
        {"words": ["bnp", "bnm"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_n^+ b_n^- - 1/2",
      "parity": 0
    },
    "E_eps1_del{k}_pp": {
      "standard_form": [
        {"words": ["a1p", "b{k}p"], "coeff": "1"}
      ],
      "frappat_form": "a1^+ b_k^+",
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
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "2",
    "sign_rule": "graded"
  }
]
```

**Convention**: For $p(X) = 0, p(Y) = 1$: $[X, Y\} = XY - YX$ (commutator). For $p(X) = 1, p(Y) = 1$: $[X, Y\} = XY + YX$ (anticommutator).

### `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "2026-10-04",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "docs/math/Cn1_definition.md"
  ]
}
```

---

## Schema 2: Gamma Structure (`C_{n}_gamma.json`)

Stores the inhomogeneous deformation cocycle $\gamma(X,Y)$ symbolically.

### Top-Level Keys

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "deformation_parameters": { ... },
  "gamma_structure": [ ... ],
  "metadata": { ... }
}
```

### `deformation_parameters`

```json
{
  "count": 4,
  "labels": ["gb_a1p_b1p", "gb_a1p_b1m", "gb_a1m_b1p", "gb_a1m_b1m"],
  "parity": 1,
  "defining_relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa"
}
```

### `gamma_structure`

Non-zero gamma coefficients as symbolic linear combinations of gb parameters:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps1_del1_pp",
    "Z": "H_1",
    "coeff_expr": {"gb_a1p_b1p": "2"},
    "description": "gamma(H_1, E_eps1_del1_pp) has H_1 component: 2 * gb_a1p_b1p"
  }
]
```

---

## Schema 3: Evaluated Structure (`C_{n}_evaluated.json`)

Stores numerically evaluated structure constants with specific gb values.

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "gb_assignment": {
    "gb_a1p_b1p": "1", "gb_a1p_b1m": "1",
    "gb_a1m_b1p": "1", "gb_a1m_b1m": "1"
  },
  "structure_constants": [ ... ],
  "deformed_structure_constants": [ ... ],
  "metadata": { ... }
}
```

---

## Schema 4: Coboundary Structure (`C_{n}_coboundary.json`)

Stores the coboundary operator $\delta f$ for an odd linear map $f: \mathfrak{g} \to \mathfrak{g}$.

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "f_map_parameters": {
    "description": "phi_{ij}: coefficient of Z_i in f(Z_j), where p(Z_i) != p(Z_j)",
    "labels": ["phi_H_1_E_eps1_del1_pp", ...]
  },
  "coboundary": [
    {
      "X": "H_1",
      "Y": "E_eps1_del1_pp",
      "Z": "E_eps1_del1_pp",
      "phi_coefficients": {"phi_H_1_E_eps1_del1_pp": "2"},
      "description": "(delta_f)(H_1, E_eps1_del1_pp) has E_eps1_del1_pp component: 2 * phi_H_1_E_eps1_del1_pp"
    }
  ],
  "metadata": { ... }
}
```

---

## Compatibility with B(m,n) Schema

| Field | B(0,n) | C(n+1) |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `oscillator_generators` key | `supplementary_fermion` + `bosons` | `fermions` + `bosons` |
| `oscillator_relations` key | `supplementary_fermion_relation` | `fermionic_anticommutators` |
| `central_elements` | present (K, kappa) | present (K, kappa) |
| Odd generator labels | `E_del{k}_p/m` | `E_eps1_del{k}_pp/pm/mp/mm` |
| Odd generator count | $2n$ | $4n$ |
| Even dimension | $2n^2+n$ | $2n^2+n+1$ |
