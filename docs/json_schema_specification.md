# JSON Schema Specification for $C(n+1) = \mathfrak{osp}(2|2n)$ (v5.0)

This document provides the complete v5.0 JSON schema specification for the $C(n+1) = \mathfrak{osp}(2|2n)$ series, extending the $B(0,n)$ base schema while establishing uniform architectural consistency across all 4 schema layers.

---

## 1. 4-Layer Schema Architecture and File Naming

The $C(n+1)$ schema follows a 4-layer computational architecture indexed by the **bosonic rank $n$** (so $C(2) \implies n=1$, $C(3) \implies n=2$, $C(4) \implies n=3$):

| Layer | File Pattern | Description |
|---|---|---|
| **Schema 1** | `C_{n}_structure.json` | Undeformed Lie superalgebra structure: basis, parity, oscillator realization, graded structure constants |
| **Schema 2** | `C_{n}_gamma.json` | Parametric inhomogeneous deformation ($\gamma$-structure / $\mathrm{gb}$ matrix) |
| **Schema 3** | `C_{n}_evaluated_{gb}.json` | Deformed structure constants evaluated at specific parameter configurations |
| **Schema 4** | `C_{n}_coboundary_{gb}.json` | Coboundary operator $\delta f$ matrix representation and triviality linear system solver data |

---

## 2. Schema 1: Undeformed Algebra Structure (`C_{n}_structure.json`)

### 2.1 Top-Level Key Specification
A valid Schema 1 file must contain the following top-level keys:
- `schema_version`: string (always `"5.0"`)
- `algebra`: object defining algebra type and dimensions
- `central_elements`: object defining central parameters ($K, \kappa$)
- `oscillator_generators`: object defining fermionic and bosonic oscillator labels
- `oscillator_relations`: object defining CAR, CCR, and mixed relations
- `basis`: object containing `even` and `odd` generator lists and PBW ordering
- `parity`: mapping each generator name to its $\mathbb{Z}_2$-parity (`0` or `1`)
- `generator_realization`: oscillator representations in normal/standard form
- `structure_constants`: list of non-zero graded Lie brackets
- `metadata`: provenance metadata

### 2.2 Detailed Key Definitions

#### `algebra`
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
    "formula": {
      "even": "2*n^2 + n + 1",
      "odd": "4*n",
      "total": "2*n^2 + 5*n + 1"
    }
  }
}
```

#### `central_elements` (Top-Level Key)
```json
{
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central element, identified with scalar 1 in oscillator algebra"
  },
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "description": "Odd central nilpotent parameter (kappa^2 = 0) governing deformation"
  }
}
```

#### `oscillator_generators`
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic CAR pair a_1^± with parity 1"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n and parity 0"
  }
}
```

#### `oscillator_relations`
```json
{
  "fermionic_anticommutators": {
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
    "description": "Undeformed commutation relations between bosons and fermions",
    "relations": {
      "boson_fermion": "[b_i^±, a_1^±] = 0"
    }
  }
}
```

#### `basis` & `parity`
```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
}
```

#### `generator_realization`
Oscillator terms are represented in standard normal order `a_1_p, a_1_m, b_1_p, b_1_m, ...`.
```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m",
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
        {"words": ["b_1_p", "b_1_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_1^+ b_1^- - 1/2",
      "parity": 0
    },
    "E_eps1_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    }
  }
}
```

#### `structure_constants`
List of non-zero graded brackets $[X, Y\} = Z \cdot \text{coeff}$:
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

## 3. Schema 2: Inhomogeneous Deformation (`C_{n}_gamma.json`)

Deformation brackets are defined by:
$$[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma, j, s} \cdot \kappa, \quad [X, Y]_\gamma = [X, Y]_0 + \kappa \cdot \gamma(X, Y)$$

Structure:
- `schema_version`: `"5.0"`
- `algebra`: identical to Schema 1
- `deformation_parameters`: list of $4n$ parameters `["gb_a1p_b1p", "gb_a1p_b1m", "gb_a1m_b1p", "gb_a1m_b1m", ...]`
- `gamma_structure_constants`: list of deformation terms with linear combinations of `gb` parameters:
  ```json
  [
    {
      "X": "E_eps1_del1_pp",
      "Y": "E_eps1_del1_mp",
      "Z": "E_2del1_p",
      "linear_combination": [
        {"param": "gb_a1m_b1p", "coeff": "1"}
      ]
    }
  ]
  ```

---

## 4. Schema 3: Evaluated Structure Constants (`C_{n}_evaluated_{gb}.json`)

Numerical evaluation of brackets at specific parameter test points (e.g. `gb_a1p_b1p_1`, `gb_all_1`):
- `schema_version`: `"5.0"`
- `algebra`: identical to Schema 1
- `evaluated_parameters`: dictionary mapping parameter names to values (e.g. `{"gb_a1p_b1p": 1, ...}`)
- `evaluated_structure_constants`: list of non-zero structure constants with numerical coefficients.

---

## 5. Schema 4: Coboundary and Triviality Verification (`C_{n}_coboundary_{gb}.json`)

- `schema_version`: `"5.0"`
- `algebra`: identical to Schema 1
- `coboundary_formula`: definition of $\delta f$
- `map_f_parameters`: $\phi_{ij}$ for odd map $f: \mathfrak{g} \to \mathfrak{g}$
- `evaluation_case`: parameter name and values
- `linear_system`: matrix representation of $\delta f(X, Y) = \gamma(X, Y)$
- `triviality_result`: `is_trivial` (boolean), `rank`, `solution` / `residual_norm`.

---

## 6. Compatibility Comparison with $B(0,n)$

| Dimension / Property | $B(0,n) = \mathfrak{osp}(1|2n)$ | $C(n+1) = \mathfrak{osp}(2|2n)$ |
|---|---|---|
| `family` | `"B"` | `"C"` |
| Fermionic rank `m` | `0` | `1` |
| Fermionic oscillators | Supplementary fermion $a_0$ ($a_0^2 = 1/2$) | Standard CAR pair $a_1^+, a_1^-$ ($\{a_1^-, a_1^+\} = 1$) |
| Even dimension | $2n^2 + n$ | $2n^2 + n + 1$ |
| Odd dimension | $2n$ | $4n$ |
| Deformation parameters | $2n$ (`gb_a0_b{j}s`) | $4n$ (`gb_a1{sigma}_b{j}s`) |
| Central elements | `K`, `kappa` | `K`, `kappa` (top-level key) |
