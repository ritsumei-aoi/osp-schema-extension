# JSON Schema Specification for C(n+1) = osp(2|2n) (v5.0)

This document specifies the v5.0 JSON schema for $C(n+1) = \mathfrak{osp}(2|2n)$ structure constants, deformation parameters, and coboundary data. It extends the base schema originally developed for $B(0,n) = \mathfrak{osp}(1|2n)$ while accommodating the standard CAR fermionic pair, the resulting root system structure, and the inhomogeneous deformation framework.

---

## 1. Overview: 4-Layer Schema Architecture

The data for each algebra is organized into four standardized layers of increasing computational depth:

| Layer | File Pattern | Description |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation ($\gamma$-structure and $gb$ parameter dependencies) |
| Schema 3 | `C_{n}_evaluated_<gb>.json` | Numerically / symbolically evaluated structure constants for specific $gb$ parameters |
| Schema 4 | `C_{n}_coboundary_<gb>.json` | Coboundary operator data for triviality verification |

### File Naming Convention
- Files are indexed by the **bosonic rank $n$** (rank of $\mathfrak{sp}(2n)$):
  - $n = 1$: $C(2) = \mathfrak{osp}(2|2) \implies$ `C_1_structure.json`, `C_1_gamma.json`, etc.
  - $n = 2$: $C(3) = \mathfrak{osp}(2|4) \implies$ `C_2_structure.json`, `C_2_gamma.json`, etc.
  - $n = 3$: $C(4) = \mathfrak{osp}(2|6) \implies$ `C_3_structure.json`, `C_3_gamma.json`, etc.

---

## 2. Schema 1: Algebra Structure Specification

Schema 1 files define the underlying Lie superalgebra $\mathfrak{g} = C(n+1)$ in an oscillator realization, its canonical basis, parity assignments, and undeformed structure constants.

### 2.1 Top-Level Keys

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

---

### 2.2 `schema_version`

```json
"schema_version": "5.0"
```

---

### 2.3 `algebra`

Specifies the Cartan family, fermionic and bosonic ranks, naming, and superdimension formulas.

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
    "odd": 8
  },
  "dimension_formulas": {
    "even": "2n^2 + n + 1",
    "odd": "4n",
    "total": "2n^2 + 5n + 1"
  }
}
```

#### Dimension Table
| $n$ | Cartan Type | OSP Notation | Even ($\dim \mathfrak{g}_{\bar{0}}$) | Odd ($\dim \mathfrak{g}_{\bar{1}}$) | Total Dimension |
|---|---|---|---|---|---|
| 1 | C(2) | $\mathfrak{osp}(2\|2)$ | 4 | 4 | 8 |
| 2 | C(3) | $\mathfrak{osp}(2\|4)$ | 11 | 8 | 19 |
| 3 | C(4) | $\mathfrak{osp}(2\|6)$ | 22 | 12 | 34 |

---

### 2.4 `oscillator_generators`

Specifies the fundamental creation and annihilation operators generating the algebra. In $C(n+1)$, this contains two keys: `"fermions"` ($m=1$) and `"bosons"` ($n$ modes).

```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^± with m=1 (CAR)"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n (CCR)"
  }
}
```

---

### 2.5 `oscillator_relations`

Defines the canonical algebraic relations among oscillator generators:

```json
{
  "fermionic_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for standard fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "nilpotency": "(a_1^±)^2 = 0"
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
    "boson_fermion": "[b_k^±, a_1^±] = 0 (undeformed)"
  }
}
```

---

### 2.6 `central_elements` (Dedicated Top-Level Key)

Defines central extensions of the algebra used in deformation theory ($\tilde{\mathfrak{g}} = \mathfrak{g} \oplus \mathbb{R}\kappa \oplus \mathbb{R}K$):

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotency": "kappa^2 = 0",
    "description": "Odd central element parametrizing inhomogeneous deformation"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "value": 1,
    "description": "Even central element (identity scalar unit K = 1)"
  }
}
```

---

### 2.7 `basis`

Specifies the ordered basis elements following the approved **Option 1 (Polarity-Ordered)** PBW convention:
$$\kappa < [\text{Odd } \Delta_{\bar{1}}^+] < [\text{Odd } \Delta_{\bar{1}}^-] < [\text{Even Cartan}] < [\text{Even } \Delta_{\bar{0}}^+] < [\text{Even } \Delta_{\bar{0}}^-] < [\text{Even } \Delta_{\bar{0}}^0]$$

#### Example: $n = 2$ ($C(3)$)
```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm",
    "E_del1_del2_pm",
    "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd: Delta_{1}^+ (pp, pm) < Delta_{1}^- (mp, mm)] < [even: Cartan < Long(+) < Short(++) < Long(-) < Short(--) < Short(+-) < Short(-+)]"
}
```

---

### 2.8 `parity`

Provides the explicit $\mathbb{Z}_2$-grading map ($0 = \text{even}, 1 = \text{odd}$) for all basis elements:

```json
{
  "H_1": 0, "H_2": 0, "H_3": 0,
  "E_2del1_p": 0, "E_2del2_p": 0,
  "E_del1_del2_pp": 0,
  "E_2del1_m": 0, "E_2del2_m": 0,
  "E_del1_del2_mm": 0,
  "E_del1_del2_pm": 0, "E_del1_del2_mp": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del2_pp": 1,
  "E_eps1_del1_pm": 1, "E_eps1_del2_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del2_mp": 1,
  "E_eps1_del1_mm": 1, "E_eps1_del2_mm": 1
}
```

---

### 2.9 `generator_realization`

Expresses each generator as an element of the oscillator algebra written as a sum of normal-ordered words with rational coefficients:

```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m, ...",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "H_k": {
      "standard_form": [
        {"words": ["b_{k-1}_p", "b_{k-1}_m"], "coeff": "1"},
        {"words": ["b_k_p", "b_k_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-",
      "parity": 0
    },
    "H_{n+1}": {
      "standard_form": [
        {"words": ["b_n_p", "b_n_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_n^+ b_n^- - 1/2",
      "parity": 0
    },
    "E_2del{k}_p": {
      "standard_form": [{"words": ["b_k_p", "b_k_p"], "coeff": "1"}],
      "frappat_form": "(b_k^+)^2",
      "parity": 0
    },
    "E_2del{k}_m": {
      "standard_form": [{"words": ["b_k_m", "b_k_m"], "coeff": "1"}],
      "frappat_form": "(b_k^-)^2",
      "parity": 0
    },
    "E_del{i}_del{j}_pp": {
      "standard_form": [{"words": ["b_i_p", "b_j_p"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^+",
      "parity": 0
    },
    "E_del{i}_del{j}_mm": {
      "standard_form": [{"words": ["b_i_m", "b_j_m"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^-",
      "parity": 0
    },
    "E_del{i}_del{j}_pm": {
      "standard_form": [{"words": ["b_i_p", "b_j_m"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^-",
      "parity": 0
    },
    "E_del{i}_del{j}_mp": {
      "standard_form": [{"words": ["b_i_m", "b_j_p"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^+",
      "parity": 0
    },
    "E_eps1_del{k}_pp": {
      "standard_form": [{"words": ["a_1_p", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_pm": {
      "standard_form": [{"words": ["a_1_p", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^-",
      "parity": 1
    },
    "E_eps1_del{k}_mp": {
      "standard_form": [{"words": ["a_1_m", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_mm": {
      "standard_form": [{"words": ["a_1_m", "b_k_m"], "coeff": "1"}],
      "frappat_form": "a_1^- b_k^-",
      "parity": 1
    }
  }
}
```

---

### 2.10 `structure_constants`

List of non-zero graded Lie superalgebra brackets $[X, Y\} = \sum_Z c_{XY}^Z Z$:

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

### 2.11 `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161"
  ]
}
```

---

## 3. Comparison and Migration Guide: $B(0,n)$ vs $C(n+1)$

| Key | $B(0,n)$ (osp(1\|2n)) | $C(n+1)$ (osp(2\|2n)) | Rationale |
|---|---|---|---|
| `algebra.family` | `"B"` | `"C"` | Lie superalgebra Cartan series |
| `algebra.m` | `0` | `1` | Fermionic oscillator rank ($2m$ operators) |
| `algebra.dimension` | $(2n^2+n) \mid 2n$ | $(2n^2+n+1) \mid 4n$ | Even includes $H_1$ ($\mathfrak{so}(2)$); odd has $\pm\varepsilon\pm\delta_k$ |
| `oscillator_generators` | `supplementary_fermion` (`a_0`, $a_0^2=1/2$) | `fermions` (`m=1`, `a_1_p`, `a_1_m`, CAR) | True CAR fermion pair replaces auxiliary fermion |
| `oscillator_relations` | $a_0^2 = 1/2$ | $\{a_1^-, a_1^+\} = 1$ | Canonical anticommutation relation |
| `central_elements` | Implicit / optional in v5.0 | Top-level key (`kappa`, `K`) | Formalizes inhomogeneous deformation framework |
| `basis.odd` | `E_del{k}_p`, `E_del{k}_m` ($2n$) | `E_eps1_del{k}_pp/pm/mp/mm` ($4n$) | Explicit $\varepsilon_1$-tagged labels |
| `basis.ordering_convention` | $\kappa < \text{Odd}(p < m) < \text{Even}$ | $\kappa < \text{Odd}(pp < pm < mp < mm) < \text{Even}$ | Polarity ordering preserved |
| `file_naming` | `B_{n}_structure.json` | `C_{n}_structure.json` | Ranked by bosonic degree $n$ |
