# C(n+1) = osp(2|2n) JSON Schema Specification (v5.0)

This document specifies the v5.0 JSON schema for the $C(n+1) = \mathfrak{osp}(2|2n)$ superalgebra family, extending the $B(0,n) = \mathfrak{osp}(1|2n)$ schema architecture while maintaining structural compatibility.

---

## 1. 4-Layer Schema Architecture

The data for each algebra is organized into four computational layers:

| Layer | File Pattern | Purpose |
|---|---|---|
| **Layer 1: Structure** | `data/C_{n}_structure.json` | Basis, parity, oscillator realization, and unperturbed Lie superalgebra structure constants. |
| **Layer 2: Gamma** | `data/C_{n}_gamma.json` | Symbolic inhomogeneous deformation ($\gamma$-structure) and $gb$ parameter matrix ($2 \times 2n$). |
| **Layer 3: Evaluated** | `data/C_{n}_evaluated.json` | Numerical evaluation of deformed brackets under concrete $gb$ parameter assignments. |
| **Layer 4: Coboundary** | `data/C_{n}_coboundary.json` | Coboundary operator $\delta f$ for odd linear maps $f: \mathfrak{g} \to \mathfrak{g}$ for triviality verification. |

Here, $n$ is the **bosonic rank** ($n=1$ for $C(2)$, $n=2$ for $C(3)$, $n=3$ for $C(4)$).

---

## 2. Schema 1: Algebra Structure Specification

### 2.1 Top-Level Key Layout

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "central_elements": { ... },
  "oscillator_generators": { ... },
  "oscillator_relations": { ... },
  "basis": { ... },
  "parity": { ... },
  "generator_realization": { ... },
  "structure_constants": [ ... ],
  "metadata": { ... }
}
```

### 2.2 Detailed Key Definitions

#### `schema_version`
Must be `"5.0"`.

#### `algebra`
Specifies algebraic classification and dimensions:
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
    "odd": 4
  }
}
```
*Dimension formulas*:
- Even: $2n^2 + n + 1$
- Odd: $4n$
- Total: $2n^2 + 5n + 1$

#### `central_elements` (Top-level Key)
Explicitly records the central elements:
```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relation": "kappa^2 = 0",
    "description": "Odd nilpotent central element parametrizing deformations."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "K = 1",
    "description": "Even central identity element."
  }
}
```

#### `oscillator_generators`
Replaces the supplementary fermion $a_0$ with standard fermionic oscillator pair(s):
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic oscillator pair satisfying CAR."
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators satisfying CCR."
  }
}
```

#### `oscillator_relations`
Defines canonical (anti)commutation relations:
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations (CAR)",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "nilpotency": "(a_1_p)^2 = 0, (a_1_m)^2 = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations (CCR)",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0 (unperturbed)"
  }
}
```

#### `basis`
Ordered lists of even and odd basis generators conforming to PBW ordering:
```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p", "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd] < [even]"
}
```

#### `parity`
Mapping of each generator label to its $\mathbb{Z}_2$-parity (0 for even, 1 for odd):
```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

#### `generator_realization`
Oscillator monomial expressions for each generator:
```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ...",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
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
List of non-zero Lie superalgebra brackets $[X, Y\} = \sum_Z c_{XY}^Z Z$:
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

#### `metadata`
Provenance and generation information:
```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "2026-10-04",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## 3. Schema 2: Inhomogeneous Deformation ($\gamma$-Structure)

`data/C_{n}_gamma.json` contains:
- `schema_version`: `"5.0"`
- `algebra`: identical to Schema 1
- `gb_matrix`:
  - `parameters`: $4n$ parameters `["gb_a1p_b1p", "gb_a1p_b1m", "gb_a1m_b1p", "gb_a1m_b1m", ...]`
  - `shape`: `[2, 2*n]` (2 fermion modes $\times$ $2n$ boson modes)
- `gamma_structure`: list of non-zero deformed bracket terms:
  ```json
  [
    {
      "X": "...",
      "Y": "...",
      "Z": "...",
      "gb_param": "gb_a1p_b1p",
      "coeff": "1"
    }
  ]
  ```

---

## 4. Schema 3: Evaluated Structure

`data/C_{n}_evaluated.json` contains the numerical evaluation under specific $gb$ assignments (e.g., $gb = +1$ for all parameters):
- `schema_version`: `"5.0"`
- `algebra`: identical to Schema 1
- `gb_assignment`: `{ "gb_a1p_b1p": 1, ... }`
- `evaluated_brackets`: non-zero deformed brackets with numerical coefficients $[X, Y]_\gamma = [X, Y]_0 + \kappa \cdot \gamma(X, Y)$.

---

## 5. Schema 4: Coboundary Structure

`data/C_{n}_coboundary.json` contains:
- `schema_version`: `"5.0"`
- `algebra`: identical to Schema 1
- `map_f`: specification of odd linear map $f: \mathfrak{g} \to \mathfrak{g}$ with parameter matrix $\phi_{ij}$
- `coboundary_brackets`: evaluated coboundary values $(\delta f)(X, Y)$ for basis pairs $(X, Y)$.

---

## 6. Compatibility with B(m,n) Schema v5.0

1. **Shared 4-Layer Hierarchy**: Both $B(0,n)$ and $C(n+1)$ share identical top-level keys (`schema_version`, `algebra`, `basis`, `parity`, `structure_constants`, `metadata`).
2. **Modular Oscillator Specification**: In $B(0,n)$, `supplementary_fermion` is used; in $C(n+1)$, `fermions` is used.
3. **Explicit `central_elements`**: Promoted to a first-class top-level key for uniform parsing.
4. **PBW Ordering**: The standard `kappa < [odd] < [even]` convention is maintained across all families.
