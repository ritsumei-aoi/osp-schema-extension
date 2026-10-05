# JSON Schema Specification: C(n+1) Extension (v5.0)

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n) structure constants.
It extends the B(m,n) base schema to accommodate the standard fermionic pair $a_1^\pm$ and
the associated central extension structure.

**Reference**: Frappat et al. (2000), Bakalov–Sullivan (2017).

---

## Overview: 4-Layer Schema Architecture (C(n+1))

The JSON data for C(n+1) is organized into 4 layers (same structure as B(m,n)):

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_n_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_n_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_n_evaluated_<gb>.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_n_coboundary_<gb>.json` | Coboundary data for triviality verification |

**File naming**: `C_{n}_*.json` where `n` is the bosonic rank.
- C(2) = osp(2|2): `C_1_structure.json`, `C_1_gamma.json`, etc.
- C(3) = osp(2|4): `C_2_structure.json`, `C_2_gamma.json`, etc.
- C(4) = osp(2|6): `C_3_structure.json`, `C_3_gamma.json`, etc.

---

## Schema 1: Algebra Structure

### Top-Level Keys

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

### `schema_version`

```json
"schema_version": "5.0"
```

### `algebra`

For C(n+1) = osp(2|2n):

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
  }
}
```

**Dimension formulas** (C(n+1)): even = $2n^2 + n + 1$, odd = $4n$, total = $2n^2 + 5n + 1$.

| $n$ | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

### `central_elements`

New top-level key for C(n+1). Contains the central extension structure:

```json
{
  "kappa": {
    "label": "κ",
    "parity": 1,
    "relation": "κ^2 = 0",
    "description": "Odd central element; generates the cohomology deformation"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "scalar 1 in applications",
    "description": "Even central element; identified with scalar 1"
  }
}
```

**Note on K**: In the oscillator realization, $K$ is identified with the scalar 1 and does not
appear as an independent basis element. It is recorded for schema completeness and to make the
algebraic setting explicit. The basis lists exclude $K$.

### `oscillator_generators`

No supplementary fermion for C(n+1). Instead, a standard fermionic pair:

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^± with m=1 (two operators)"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

### `oscillator_relations`

```json
{
  "fermionic_anticommutators": {
    "description": "Standard CAR for the fermionic pair",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "self_relations": "a_1^+ a_1^+ = 0, a_1^- a_1^- = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_k^±, b_l^±] = 0 for all k,l",
      "conjugate_pair": "[b_k^-, b_l^+] = δ_{kl}"
    }
  },
  "mixed_anticommutators": {
    "description": "Mixed relations between fermions and bosons",
    "relations": {
      "fermi_boson": "{a_1^±, b_k^±} = 0, {a_1^+, b_k^-} = 0, {a_1^-, b_k^+} = 0"
    }
  },
  "deformation_parameter_relations": {
    "description": "Nilpotent deformation via κ and gb-parameters",
    "relation": "κ^2 = 0"
  }
}
```

### `basis`

PBW ordering (C(n+1) convention) from Issue I01:

```
κ < [odd: E_eps_del{k}_{pp,pm,mp,mm}] < [even: H_j, E_{bosonic}]
```

For C(3) (n=2) example:

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_del1_del2_pm",
    "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del1_pm", "E_eps_del1_mp", "E_eps_del1_mm",
    "E_eps_del2_pp", "E_eps_del2_pm", "E_eps_del2_mp", "E_eps_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [odd] < [even]  (κ and K are excluded from basis; see central_elements)"
}
```

### `parity`

Assigns parity (0 for even, 1 for odd) to each basis element:

```json
{
  "H_1": 0, "H_2": 0, "H_3": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_2del2_p": 0, "E_2del2_m": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_mm": 0,
  "E_del1_del2_pm": 0, "E_del1_del2_mp": 0,
  "E_eps_del1_pp": 1, "E_eps_del1_pm": 1,
  "E_eps_del1_mp": 1, "E_eps_del1_mm": 1,
  "E_eps_del2_pp": 1, "E_eps_del2_pm": 1,
  "E_eps_del2_mp": 1, "E_eps_del2_mm": 1
}
```

### `generator_realization`

Each generator is expressed as a sum of oscillator words with rational coefficients.

```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^- - b_2^+ b_2^-",
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
      "parity": 0,
      "note": "Terminal Cartan; includes constant term"
    },
    "E_eps_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    },
    "E_eps_del1_pm": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^-",
      "parity": 1
    }
  }
}
```

### `structure_constants`

Non-zero graded brackets stored as a list. Example format:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps_del1_pp",
    "Z": "E_eps_del1_pp",
    "coeff": "1",
    "sign_rule": "graded"
  },
  {
    "X": "E_eps_del1_pp",
    "Y": "E_eps_del1_mm",
    "Z": "H_1",
    "coeff": "1/2",
    "sign_rule": "graded"
  }
]
```

The structure constants encode the graded Lie bracket $[X, Y\} = Z \cdot \text{coeff}$.

### `metadata`

```json
{
  "generated_by": "Schema 1 design (Issue I02)",
  "generation_date": "YYYY-MM-DD",
  "schema_extension": "C(n+1) from B(m,n) v5.0",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017), arXiv:1612.09400",
    "handover/notation.md: PBW ordering and generator labels"
  ]
}
```

---

## Compatibility with B(m,n) Schema

### Key Differences

| Aspect | B(m,n) | C(n+1) |
|---|---|---|
| **Fermionic part** | Supplementary $a_0$ with $a_0^2 = 1/2$ | Standard pair $a_1^\pm$ with $\{a_1^-, a_1^+\} = 1$ |
| **Central elements** | Implicit (not in top-level key) | Explicit `central_elements` key with κ, K |
| **Even algebra** | $\mathfrak{sp}(2n)$ | $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$ |
| **Odd roots** | $\pm\delta_k$ (2n total) | $\pm\varepsilon \pm \delta_k$ (4n total) |
| **Generator labels** | `E_del{k}_p`, `E_del{k}_m` | `E_eps_del{k}_{pp,pm,mp,mm}` |

### Backward Compatibility

- File naming pattern (`X_n_structure.json`) is preserved.
- Top-level key structure is maintained with additions.
- `parity` object uses the same 0/1 encoding.
- `generator_realization` format is compatible (same structure).

---

## Summary of Changes for C(n+1)

1. **New top-level key**: `central_elements` (with kappa and K).
2. **Updated `oscillator_generators`**: Replace supplementary fermion with standard pair.
3. **Updated `oscillator_relations`**: CAR anticommutator instead of $a_0^2 = 1/2$.
4. **Updated `basis.odd`**: 4n generators with pp/pm/mp/mm suffixes.
5. **Updated `parity`**: Corresponding entries for new odd generators.
6. **Updated `generator_realization`**: Oscillator words use $a_1_p, a_1_m$ instead of $a_0$.
7. **Updated `structure_constants`**: Brackets recomputed under CAR relations.
