# JSON Schema Specification for $C(n+1) = \mathfrak{osp}(2|2n)$

This document specifies the v5.0 JSON schema extension for the Lie superalgebra family $C(n+1) = \mathfrak{osp}(2|2n)$ ($n \ge 1$), extending the base $B(0,n) = \mathfrak{osp}(1|2n)$ schema architecture while maintaining structural backward compatibility.

---

## 1. Overview & 4-Layer Architecture

The Lie superalgebra data for $C(n+1)$ is organized into 4 layers of computational depth:

| Layer | File Pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation ($\gamma$-structure / $\mathrm{gb}$ parameters) |
| Schema 3 | `C_{n}_evaluated_<gb>.json` | Numerically evaluated structure constants for specific $\mathrm{gb}$ parameter values |
| Schema 4 | `C_{n}_coboundary_<gb>.json` | Coboundary data for deformation triviality verification |

### File Naming Convention
- Files are named `C_{n}_structure.json`, where $n$ is the **bosonic rank**:
  - $n=1$: $C(2) = \mathfrak{osp}(2|2) \implies$ `C_1_structure.json`
  - $n=2$: $C(3) = \mathfrak{osp}(2|4) \implies$ `C_2_structure.json`
  - $n=3$: $C(4) = \mathfrak{osp}(2|6) \implies$ `C_3_structure.json`

---

## 2. Schema 1: Algebra Structure Specification

### 2.1 Top-Level Keys
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

### 2.2 `schema_version`
```json
"schema_version": "5.0"
```

### 2.3 `algebra`
Specifies family, ranks, Cartan classification, and dimension formulas:
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

#### Dimension Table
| $n$ | Cartan Type | Algebra | Even ($2n^2+n+1$) | Odd ($4n$) | Total ($2n^2+5n+1$) |
|---|---|---|---|---|---|
| 1 | C(2) | $\mathfrak{osp}(2\|2)$ | 4 | 4 | 8 |
| 2 | C(3) | $\mathfrak{osp}(2\|4)$ | 11 | 8 | 19 |
| 3 | C(4) | $\mathfrak{osp}(2\|6)$ | 22 | 12 | 34 |

### 2.4 `central_elements` (Top-level Key)
Explicitly records formal central elements:
```json
{
  "kappa": {
    "parity": 1,
    "description": "Formal odd central nilpotent parameter (kappa^2 = 0) parametrizing the inhomogeneous deformation"
  },
  "K": {
    "parity": 0,
    "description": "Even central element associated with canonical identity scalar in oscillator algebra"
  }
}
```

### 2.5 `oscillator_generators`
Replaces the supplementary fermion $a_0$ from $B(0,n)$ with standard CAR fermion pair:
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic oscillator pair a_1^± satisfying canonical anticommutation relations (CAR)"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n satisfying CCR"
  }
}
```
*(For general $n$, bosonic count is $2n$ with labels `b_1_p`, `b_1_m`, ..., `b_n_p`, `b_n_m`)*

### 2.6 `oscillator_relations`
Defines operator exchange relations in the enveloping algebra:
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for fermionic oscillators",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^±, a_1^±} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations (CCR) for bosonic oscillators",
    "relations": {
      "same_type": "[b_j^±, b_k^±] = 0 for all j, k",
      "conjugate_pair": "[b_j^-, b_k^+] = δ_{jk}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^±, a_1^σ] = 0 for all k and σ in {+,-}"
  }
}
```

### 2.7 `basis` & PBW Ordering
Conforms to Option A (Parity-first Graded PBW Ordering):
$$\kappa < [\text{odd roots grouped by sign of } \varepsilon] < [\text{even Cartan } H_k] < [\text{even root vectors}]$$

```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p", "E_2del1_m"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del1_pm",
    "E_eps_del1_mp", "E_eps_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd] < [even]"
}
```

#### Basis Lists for $n=1, 2, 3$
- **$n=1$ ($C(2)$)**:
  - `even`: `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
  - `odd`: `["E_eps_del1_pp", "E_eps_del1_pm", "E_eps_del1_mp", "E_eps_del1_mm"]`
- **$n=2$ ($C(3)$)**:
  - `even`: `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
  - `odd`: `["E_eps_del1_pp", "E_eps_del2_pp", "E_eps_del1_pm", "E_eps_del2_pm", "E_eps_del1_mp", "E_eps_del2_mp", "E_eps_del1_mm", "E_eps_del2_mm"]`
- **$n=3$ ($C(4)$)**:
  - `even`: 22 generators (`H_1..H_4`, positive roots `E_2del{k}_p`, `E_del{i}_del{j}_pp`, negative roots `E_2del{k}_m`, `E_del{i}_del{j}_mm`, mixed roots `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`)
  - `odd`: 12 generators (`E_eps_del{k}_pp`, `E_eps_del{k}_pm`, `E_eps_del{k}_mp`, `E_eps_del{k}_mm` for $k=1, 2, 3$)

### 2.8 `parity`
Mapping from basis label to parity ($0 = \text{even}, 1 = \text{odd}$):
```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps_del1_pp": 1, "E_eps_del1_pm": 1,
  "E_eps_del1_mp": 1, "E_eps_del1_mm": 1
}
```

### 2.9 `generator_realization`
Each generator is expressed in PBW standard form as a sum of normally ordered oscillator words with rational coefficients:
- Oscillator word PBW ordering: $a_1^+, a_1^-, b_1^+, b_1^-, \ldots, b_n^+, b_n^-$
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
    "E_eps_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    }
  }
}
```

### 2.10 `structure_constants`
List of non-vanishing graded brackets $[X, Y\}$:
```json
[
  {
    "X": "H_1",
    "Y": "E_eps_del1_pp",
    "Z": "E_eps_del1_pp",
    "coeff": "2",
    "sign_rule": "graded"
  }
]
```

### 2.11 `metadata`
Provenance metadata:
```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## 3. Backward Compatibility with $B(m,n)$ Schema

1. **Top-Level Structure**:
   - The overall layout matches $B(0,n)$ v5.0 with the addition of the top-level `central_elements` dictionary.
2. **Bracket Engine Interoperability**:
   - The structure of `structure_constants` (`X`, `Y`, `Z`, `coeff`, `sign_rule`) is 100% identical, allowing direct reuse of Jacobi identity checkers and linear algebra solvers.
3. **Monomial Representation**:
   - The `standard_form` representation format (`{"words": [...], "coeff": "..."}`) remains unchanged across both families.
