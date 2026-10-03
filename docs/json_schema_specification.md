# JSON Schema Specification for C(n+1) = osp(2|2n)

**Version**: 5.0 (C-extension)
**Based on**: B(0,n) v5.0 schema (`docs/math/B0n_schema_v5.md`)
**Reference**: `docs/math/Cn1_definition.md`, `handover/notation.md`

---

## Overview: 4-Layer Schema Architecture

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure, gb parameters) |
| Schema 3 | `C_{n}_evaluated.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_{n}_coboundary.json` | Coboundary data for triviality verification |

File naming uses bosonic rank `n`: C(2) = osp(2|2) → `C_1_structure.json`.

---

## Schema 1: Algebra Structure

### `schema_version`

```json
"schema_version": "5.0"
```

### `algebra`

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

**Dimension formulas** (C(n+1)):
- even = 2n²+n+1
- odd = 4n
- total = 2n²+5n+1

| n | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

### `oscillator_generators`

Replaces `supplementary_fermion` (B(0,n)) with a standard fermionic **pair**:

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^- with CAR"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

> **Compatibility note**: B(0,n) uses key `supplementary_fermion`; C(n+1) uses `fermions`. The bosonic sector structure is identical.

### `oscillator_relations`

Replaces supplementary fermion relation with standard CAR:

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for fermionic pair",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "self_anticommutator": "{a_1^+, a_1^+} = 0",
      "self_anticommutator_m": "{a_1^-, a_1^-} = 0"
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
    "fermion_boson": "[b_k^s, a_1^σ] = 0  (undeformed)"
  }
}
```

> **Note**: The mixed commutator `[b_k^s, a_1^σ] = 0` holds in the undeformed algebra. In the inhomogeneous deformation (Schema 2), this is replaced by `[b_j^s, a_1^σ] = -gb_{σ,j,s} · κ`.

### `central_elements` (top-level key)

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotency": "kappa^2 = 0",
    "description": "Odd nilpotent central element; formal symbol of the extension"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central identity; identified with scalar 1 in all applications. Not an independent basis element."
  }
}
```

> This is a **top-level key** at the same level as `algebra`, `basis`, etc.
> `K` is recorded for schema completeness but excluded from PBW ordering and basis lists.

### `basis`

PBW ordering for C(n+1): `κ < [odd] < [even]`

**C(2) (n=1) example**:

```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m",
    "E_del_none_pp",
    "E_del_none_mm",
    "E_del_none_pm",
    "E_del_none_mp"
  ],
  "odd": [
    "E_eps1_del1_pp",
    "E_eps1_del1_pm",
    "E_eps1_del1_mp",
    "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: pp<pm<mp<mm, k asc] < [even: Cartan, +even, -even, mixed]"
}
```

> Note: For n=1, there are no cross-pair even roots (E_del{i}_del{j}_* requires i<j≤n, needing n≥2). The n=1 even basis has only H_1, H_2, E_2del1_p, E_2del1_m (4 generators).

**C(3) (n=2) example**:

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: pp<pm<mp<mm, k asc] < [even: Cartan, +even, -even, mixed]"
}
```

### `parity`

```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

All `H_*` and `E_*del*` (even roots) have parity 0.
All `E_eps1_del*` (ε-roots) have parity 1.

### `generator_realization`

```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, [b_2_p, b_2_m, ...]",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0,
      "note": "First simple root generator for C(n+1)"
    },
    "H_{k} (k=2,...,n)": {
      "standard_form": [
        {"words": ["b_{k-1}_p", "b_{k-1}_m"], "coeff": "1"},
        {"words": ["b_{k}_p", "b_{k}_m"], "coeff": "-1"}
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
      "note": "Terminal Cartan; includes -1/2 constant"
    },
    "E_eps1_del{k}_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_pm": {
      "standard_form": [
        {"words": ["a_1_p", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_k^-",
      "parity": 1
    },
    "E_eps1_del{k}_mp": {
      "standard_form": [
        {"words": ["a_1_m", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_k^+",
      "parity": 1
    },
    "E_eps1_del{k}_mm": {
      "standard_form": [
        {"words": ["a_1_m", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_k^-",
      "parity": 1
    },
    "E_2del{k}_p": {
      "standard_form": [
        {"words": ["b_k_p", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "(b_k^+)^2",
      "parity": 0
    },
    "E_2del{k}_m": {
      "standard_form": [
        {"words": ["b_k_m", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "(b_k^-)^2",
      "parity": 0
    },
    "E_del{i}_del{j}_pp (i<j)": {
      "standard_form": [
        {"words": ["b_i_p", "b_j_p"], "coeff": "1"}
      ],
      "frappat_form": "b_i^+ b_j^+",
      "parity": 0
    },
    "E_del{i}_del{j}_mm (i<j)": {
      "standard_form": [
        {"words": ["b_i_m", "b_j_m"], "coeff": "1"}
      ],
      "frappat_form": "b_i^- b_j^-",
      "parity": 0
    },
    "E_del{i}_del{j}_pm (i<j)": {
      "standard_form": [
        {"words": ["b_i_p", "b_j_m"], "coeff": "1"}
      ],
      "frappat_form": "b_i^+ b_j^-",
      "parity": 0
    },
    "E_del{i}_del{j}_mp (i<j)": {
      "standard_form": [
        {"words": ["b_i_m", "b_j_p"], "coeff": "1"}
      ],
      "frappat_form": "b_i^- b_j^+",
      "parity": 0
    }
  }
}
```

### `structure_constants`

Non-zero graded brackets `[X, Y}` stored as a list:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "1",
    "sign_rule": "graded"
  }
]
```

The graded bracket satisfies:
- `[X, Y} = -(-1)^{p(X)p(Y)} [Y, X}`
- Super Jacobi identity holds.

### `metadata`

```json
{
  "generated_by": "C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Frappat et al., arXiv:hep-th/9607161",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## Compatibility with B(m,n) Schema

| Field | B(0,n) v5.0 | C(n+1) v5.0 |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `algebra.dimension.even_formula` | `2*n^2 + n` | `2*n^2 + n + 1` |
| `algebra.dimension.odd_formula` | `2*n` | `4*n` |
| `oscillator_generators` key | `supplementary_fermion` + `bosons` | `fermions` + `bosons` |
| Fermionic oscillators | `a_0` (single, $a_0^2=1/2$) | `a_1_p`, `a_1_m` (CAR pair) |
| `oscillator_relations` | supplementary + bosonic + mixed | CAR + bosonic + mixed |
| `central_elements` | top-level (kappa odd, K even) | top-level (same structure) |
| Odd generator labels | `E_del{k}_p/m` | `E_eps1_del{k}_pp/pm/mp/mm` |
| Odd generator count | `2n` | `4n` |
| PBW ordering | `κ < [odd] < [even]` | `κ < [odd] < [even]` (same) |

---

## File Naming Convention

| Algebra | n (bosonic) | Schema 1 | Schema 2 | Schema 3 | Schema 4 |
|---|---|---|---|---|---|
| C(2) = osp(2\|2) | 1 | `C_1_structure.json` | `C_1_gamma.json` | `C_1_evaluated.json` | `C_1_coboundary.json` |
| C(3) = osp(2\|4) | 2 | `C_2_structure.json` | `C_2_gamma.json` | `C_2_evaluated.json` | `C_2_coboundary.json` |
| C(4) = osp(2\|6) | 3 | `C_3_structure.json` | `C_3_gamma.json` | `C_3_evaluated.json` | `C_3_coboundary.json` |

All files are located in `data/`.
