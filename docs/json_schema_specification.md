# JSON Schema v5.0 Specification for C(n+1) = osp(2|2n)

**Schema version**: 5.0  
**Algebra family**: C(n+1) = osp(2|2n)  
**Status**: Approved (I02-1)  
**Base schema**: B(0,n) v5.0 (see `math/B0n_schema_v5.md`)

---

## Overview: 4-Layer Schema Architecture

| Layer | File pattern | Contents |
|-------|-------------|---------|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_{n}_evaluated_{gb}.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_{n}_coboundary_{gb}.json` | Coboundary data for triviality verification |

`n` is the **bosonic rank**:

| Algebra | n | Schema 1 file |
|---------|---|---------------|
| C(2) = osp(2\|2) | 1 | `C_1_structure.json` |
| C(3) = osp(2\|4) | 2 | `C_2_structure.json` |
| C(4) = osp(2\|6) | 3 | `C_3_structure.json` |

---

## Schema 1: Algebra Structure

### Top-Level Key Order

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
  "structure_constants": { ... },
  "metadata": { ... }
}
```

---

### `schema_version`

```json
"schema_version": "5.0"
```

---

### `algebra`

Shown for C(3) (n=2). Substitute n and derived values for other ranks.

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
    "even_formula": "2n^2 + n + 1",
    "odd_formula": "4n"
  }
}
```

**Dimension table**:

| n | even | odd | total | cartan_type |
|---|------|-----|-------|-------------|
| 1 | 4 | 4 | 8 | C(2) |
| 2 | 11 | 8 | 19 | C(3) |
| 3 | 22 | 12 | 34 | C(4) |

---

### `central_elements`

Top-level key; identical for all n.

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotency": "kappa^2 = 0",
    "description": "Odd central element; parametrizes the inhomogeneous deformation."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "value": "K = 1 (scalar identification)",
    "description": "Even central identity; not included as an independent basis element."
  }
}
```

---

### `oscillator_generators`

Shown for n=2. General rule: `bosons.count = 2n`, labels `["b_1_p","b_1_m",...,"b_n_p","b_n_m"]`.

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± satisfying CAR {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

---

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "self_anticommutators": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

---

### `basis`

Shown for C(3) (n=2). For other n, extend odd list by 4 generators per additional bosonic mode and even list accordingly.

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
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del2_pp", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm",
    "E_eps1_del2_mp", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [ε+ odd, k ascending, δ+ before δ−] < [ε− odd, k ascending, δ+ before δ−] < [even]  (K = 1 is excluded)"
}
```

**C(2) basis** (n=1):
- even: `H_1, H_2, E_2del1_p, E_2del1_m`
- odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

**C(4) basis** (n=3):
- even (22): `H_1,...,H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del2_mp, E_del1_del3_pm, E_del1_del3_mp, E_del2_del3_pm, E_del2_del3_mp`
- odd (12): `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del3_mp, E_eps1_del3_mm`

---

### `parity`

Shown for C(3) (n=2). Even generators have parity 0; all `E_eps1_*` have parity 1.

```json
{
  "H_1": 0, "H_2": 0, "H_3": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_2del2_p": 0, "E_2del2_m": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_mm": 0,
  "E_del1_del2_pm": 0, "E_del1_del2_mp": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1,
  "E_eps1_del2_pp": 1, "E_eps1_del2_pm": 1,
  "E_eps1_del2_mp": 1, "E_eps1_del2_mm": 1
}
```

---

### `generator_realization`

Oscillator word ordering: `a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m`

```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "H_k (2 <= k <= n)": {
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
      "parity": 0,
      "note": "Terminal Cartan; constant -1/2 from the sp(2n) structure"
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
    "E_del{i}_del{j}_pp (i<j)": {
      "standard_form": [{"words": ["b_i_p", "b_j_p"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^+",
      "parity": 0
    },
    "E_del{i}_del{j}_pm (i<j)": {
      "standard_form": [{"words": ["b_i_p", "b_j_m"], "coeff": "1"}],
      "frappat_form": "b_i^+ b_j^-",
      "parity": 0
    },
    "E_del{i}_del{j}_mp (i<j)": {
      "standard_form": [{"words": ["b_i_m", "b_j_p"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^+",
      "parity": 0
    },
    "E_del{i}_del{j}_mm (i<j)": {
      "standard_form": [{"words": ["b_i_m", "b_j_m"], "coeff": "1"}],
      "frappat_form": "b_i^- b_j^-",
      "parity": 0
    }
  }
}
```

---

### `structure_constants`

Non-zero graded brackets [X, Y} stored as a list. Format identical to B(0,n); generator names updated to C(n+1) labels.

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

Structure constants are computed by the algebra's bracket using the CAR/CCR relations and oscillator realizations above.

---

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba, Dictionary on Lie Algebras and Superalgebras (2000)",
    "arXiv:hep-th/9607161"
  ]
}
```

---

## Compatibility: B(0,n) → C(n+1) Field Diff

| Field | B(0,n) | C(n+1) |
|-------|--------|--------|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `algebra.dimension.even_formula` | `2n²+n` | `2n²+n+1` |
| `algebra.dimension.odd_formula` | `2n` | `4n` |
| `oscillator_generators` fermion key | `supplementary_fermion` | `fermions` |
| `oscillator_relations` fermion key | `supplementary_fermion_relation` | `standard_fermion_anticommutators` |
| `basis.odd` count | `2n` | `4n` |
| `basis.odd` labels | `E_del{k}_p/m` | `E_eps1_del{k}_{pp/pm/mp/mm}` |
| `generator_realization.ordering` | `a_0, b_1_p, ...` | `a_1_p, a_1_m, b_1_p, ...` |

All other fields (`structure_constants`, `metadata`) use the same format with generator names updated.
