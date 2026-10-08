# JSON Schema Specification: C(n+1) = osp(2|2n), v5.0

**Created**: 2026-10-08 (Issue I02-1)
**Model**: Claude Sonnet 4.6
**Status**: Schema 1 (algebra structure) — approved

This document specifies the v5.0 JSON schema for $C(n+1) = \mathfrak{osp}(2|2n)$,
extending the B(0,n) v5.0 base schema (`docs/math/B0n_schema_v5.md`).

**References**:
- `handover/notation.md` — finalized conventions (I01-1)
- `docs/math/B0n_schema_v5.md` — B(0,n) base schema
- `docs/math/Cn1_definition.md` — C(n+1) oscillator realization
- `docs/math/C_inhomogeneous_definition.md` — central elements κ, K

---

## File Naming Convention

| Algebra | Bosonic rank n | File |
|---|---|---|
| C(2) = osp(2\|2) | 1 | `C_1_structure.json` |
| C(3) = osp(2\|4) | 2 | `C_2_structure.json` |
| C(4) = osp(2\|6) | 3 | `C_3_structure.json` |

Pattern: `C_{n}_structure.json` where `n` is the bosonic rank (number of $b_k^\pm$ pairs),
consistent with the B(0,n) convention `B_{n}_structure.json`.

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

> **Note on ordering**: `central_elements` is placed immediately after `algebra` as a
> dedicated top-level key (new in C(n+1); only an inline note in B(0,n) v5.0).

---

### `schema_version`

```json
"schema_version": "5.0"
```

Unchanged from B(0,n) v5.0.

---

### `algebra`

```json
"algebra": {
  "family": "C",
  "m": 1,
  "n": <bosonic_rank>,
  "cartan_type": "C(n+1)",
  "alternative_notation": {
    "osp": "osp(2|2n)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": <2*n^2 + 5*n + 1>,
    "even": <2*n^2 + n + 1>,
    "odd": <4*n>
  }
}
```

**Dimension formulas**: even $= 2n^2 + n + 1$, odd $= 4n$, total $= 2n^2 + 5n + 1$.

| Case | n | even | odd | total |
|---|---|---|---|---|
| C(2) | 1 | 4 | 4 | 8 |
| C(3) | 2 | 11 | 8 | 19 |
| C(4) | 3 | 22 | 12 | 34 |

**Example (C(3), n=2)**:
```json
"algebra": {
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

---

### `central_elements`

New dedicated top-level key for C(n+1). Both elements are excluded from PBW `basis` lists.

```json
"central_elements": {
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotency": "kappa^2 = 0",
    "role": "Odd central element. Appears in the deformed bracket: [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y). Parametrizes the inhomogeneous (gb) deformation in Schema 2."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "role": "Even central element arising from the pre-oscillator form on V. Identified with scalar 1 in all current applications; not an independent basis element."
  }
}
```

---

### `oscillator_generators`

```json
"oscillator_generators": {
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± with CAR: {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": <2*n>,
    "n": <bosonic_rank>,
    "labels": ["b_1_p", "b_1_m", "...", "b_n_p", "b_n_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n; CCR: [b_k^-, b_l^+] = delta_{kl}"
  }
}
```

**Label lists by case**:

| Case | n | `fermions.labels` | `bosons.labels` |
|---|---|---|---|
| C(2) | 1 | `["a_1_p","a_1_m"]` | `["b_1_p","b_1_m"]` |
| C(3) | 2 | `["a_1_p","a_1_m"]` | `["b_1_p","b_1_m","b_2_p","b_2_m"]` |
| C(4) | 3 | `["a_1_p","a_1_m"]` | `["b_1_p","b_1_m","b_2_p","b_2_m","b_3_p","b_3_m"]` |

**Example (C(3), n=2)**:
```json
"oscillator_generators": {
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± with CAR: {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_k^± with k=1,2; CCR: [b_k^-, b_l^+] = delta_{kl}"
  }
}
```

---

### `oscillator_relations`

```json
"oscillator_relations": {
  "fermionic_anticommutators": {
    "description": "CAR for the standard fermionic pair a_1^±",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_sign": "{a_1^s, a_1^s} = 0 for s in {+,-}"
    }
  },
  "bosonic_commutators": {
    "description": "CCR for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^s, b_j^s] = 0 for all i,j,s",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"
    }
  },
  "mixed_commutators": {
    "description": "Boson-fermion mixed relations in the undeformed algebra. In Schema 2 (gamma-deformed), [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.",
    "relations": {
      "boson_fermion": "[b_k^s, a_1^sigma] = 0 for all k, s, sigma"
    }
  }
}
```

**Sign convention note**: The mixed relation is a **commutator** (not anticommutator) because
$p(a_1^\pm) = 1$ and $p(b_k^\pm) = 0$, so the graded bracket sign is $(-1)^{1 \cdot 0} = 1$.

---

### `basis`

PBW ordering follows the ε-first convention (Option A, approved I01-1).

**General template**:
```json
"basis": {
  "even": [
    "H_1", "...", "H_{n+1}",
    "E_2del1_p", "...", "E_2deln_p",
    "E_del{i}_del{j}_pp",
    "E_del{i}_del{j}_pm",
    "E_2del1_m", "...", "E_2deln_m",
    "E_del{i}_del{j}_mm",
    "E_del{i}_del{j}_mp"
  ],
  "odd": [
    "E_eps_del1_pp", "...", "E_eps_deln_pp",
    "E_eps_del1_pm", "...", "E_eps_deln_pm",
    "E_eps_del1_mp", "...", "E_eps_deln_mp",
    "E_eps_del1_mm", "...", "E_eps_deln_mm"
  ],
  "ordering_convention": "PBW: [odd, eps-first] < [even, Cartan < positive-Sp < negative-Sp < mixed-Sp]"
}
```

**C(2) (n=1)**:
```json
"basis": {
  "even": [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del1_pm",
    "E_eps_del1_mp", "E_eps_del1_mm"
  ],
  "ordering_convention": "PBW: [odd, eps-first] < [even, Cartan < positive-Sp < negative-Sp]"
}
```

**C(3) (n=2)**:
```json
"basis": {
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp",
    "E_del1_del2_pm",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm",
    "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del2_pp",
    "E_eps_del1_pm", "E_eps_del2_pm",
    "E_eps_del1_mp", "E_eps_del2_mp",
    "E_eps_del1_mm", "E_eps_del2_mm"
  ],
  "ordering_convention": "PBW: [odd, eps-first] < [even, Cartan < positive-Sp < negative-Sp < mixed-Sp]"
}
```

**C(4) (n=3)**:
```json
"basis": {
  "even": [
    "H_1", "H_2", "H_3", "H_4",
    "E_2del1_p", "E_2del2_p", "E_2del3_p",
    "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp",
    "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm",
    "E_2del1_m", "E_2del2_m", "E_2del3_m",
    "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm",
    "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del2_pp", "E_eps_del3_pp",
    "E_eps_del1_pm", "E_eps_del2_pm", "E_eps_del3_pm",
    "E_eps_del1_mp", "E_eps_del2_mp", "E_eps_del3_mp",
    "E_eps_del1_mm", "E_eps_del2_mm", "E_eps_del3_mm"
  ],
  "ordering_convention": "PBW: [odd, eps-first] < [even, Cartan < positive-Sp < negative-Sp < mixed-Sp]"
}
```

---

### `parity`

All even generators have parity 0; all odd generators have parity 1.

**C(2) (n=1)**:
```json
"parity": {
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps_del1_pp": 1, "E_eps_del1_pm": 1,
  "E_eps_del1_mp": 1, "E_eps_del1_mm": 1
}
```

**C(3) (n=2)**:
```json
"parity": {
  "H_1": 0, "H_2": 0, "H_3": 0,
  "E_2del1_p": 0, "E_2del2_p": 0,
  "E_del1_del2_pp": 0, "E_del1_del2_pm": 0,
  "E_2del1_m": 0, "E_2del2_m": 0,
  "E_del1_del2_mm": 0, "E_del1_del2_mp": 0,
  "E_eps_del1_pp": 1, "E_eps_del2_pp": 1,
  "E_eps_del1_pm": 1, "E_eps_del2_pm": 1,
  "E_eps_del1_mp": 1, "E_eps_del2_mp": 1,
  "E_eps_del1_mm": 1, "E_eps_del2_mm": 1
}
```

**C(4) (n=3)**:
```json
"parity": {
  "H_1": 0, "H_2": 0, "H_3": 0, "H_4": 0,
  "E_2del1_p": 0, "E_2del2_p": 0, "E_2del3_p": 0,
  "E_del1_del2_pp": 0, "E_del1_del3_pp": 0, "E_del2_del3_pp": 0,
  "E_del1_del2_pm": 0, "E_del1_del3_pm": 0, "E_del2_del3_pm": 0,
  "E_2del1_m": 0, "E_2del2_m": 0, "E_2del3_m": 0,
  "E_del1_del2_mm": 0, "E_del1_del3_mm": 0, "E_del2_del3_mm": 0,
  "E_del1_del2_mp": 0, "E_del1_del3_mp": 0, "E_del2_del3_mp": 0,
  "E_eps_del1_pp": 1, "E_eps_del2_pp": 1, "E_eps_del3_pp": 1,
  "E_eps_del1_pm": 1, "E_eps_del2_pm": 1, "E_eps_del3_pm": 1,
  "E_eps_del1_mp": 1, "E_eps_del2_mp": 1, "E_eps_del3_mp": 1,
  "E_eps_del1_mm": 1, "E_eps_del2_mm": 1, "E_eps_del3_mm": 1
}
```

---

### `generator_realization`

Oscillator word PBW order: `a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m`

```json
"generator_realization": {
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
      "note": "Terminal Cartan; constant -1/2 from the pre-oscillator form normalization"
    },
    "E_eps_del{k}_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1
    },
    "E_eps_del{k}_pm": {
      "standard_form": [
        {"words": ["a_1_p", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_k^-",
      "parity": 1
    },
    "E_eps_del{k}_mp": {
      "standard_form": [
        {"words": ["a_1_m", "b_k_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_k^+",
      "parity": 1
    },
    "E_eps_del{k}_mm": {
      "standard_form": [
        {"words": ["a_1_m", "b_k_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^- b_k^-",
      "parity": 1
    },
    "E_2del{k}_p": {
      "standard_form": [
        {"words": ["b_k_p", "b_k_p"], "coeff": "1/2"}
      ],
      "frappat_form": "(1/2)(b_k^+)^2",
      "parity": 0
    },
    "E_2del{k}_m": {
      "standard_form": [
        {"words": ["b_k_m", "b_k_m"], "coeff": "1/2"}
      ],
      "frappat_form": "(1/2)(b_k^-)^2",
      "parity": 0
    },
    "E_del{i}_del{j}_pp (i<j)": {
      "standard_form": [
        {"words": ["b_i_p", "b_j_p"], "coeff": "1"}
      ],
      "frappat_form": "b_i^+ b_j^+",
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
    },
    "E_del{i}_del{j}_mm (i<j)": {
      "standard_form": [
        {"words": ["b_i_m", "b_j_m"], "coeff": "1"}
      ],
      "frappat_form": "b_i^- b_j^-",
      "parity": 0
    }
  }
}
```

---

### `structure_constants`

Format is identical to B(0,n) v5.0 — a list of non-zero graded brackets $[X, Y\}$:

```json
"structure_constants": [
  {
    "X": "<label>",
    "Y": "<label>",
    "Z": "<label>",
    "coeff": "<rational>",
    "sign_rule": "graded"
  }
]
```

> **Status**: Structure constants for C(n+1) are deferred to a future issue.
> They must be recomputed from scratch using the CAR relations for $a_1^\pm$
> (replacing B(0,n)'s $a_0^2 = 1/2$ algebra).

---

### `metadata`

```json
"metadata": {
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Aoi (2026), docs/drafts/aoi2026_triviality_osp1_2n.tex"
  ]
}
```

---

## Backward Compatibility Summary

| Schema 1 key | B(0,n) v5.0 | C(n+1) v5.0 | Change |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | None |
| `algebra.family` | `"B"` | `"C"` | Changed |
| `algebra.m` | `0` | `1` | Changed |
| `algebra.dimension` | $2n^2+n \mid 2n$ | $2n^2+n+1 \mid 4n$ | Changed |
| `central_elements` | (inline note only) | **New top-level key** (κ, K) | Added |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | First key renamed |
| `oscillator_relations` | `supplementary_fermion_relation` + ... | `fermionic_anticommutators` + ... | First key renamed |
| `basis.odd` | `E_del{k}_p/m` (2n generators) | `E_eps_del{k}_pp/pm/mp/mm` (4n generators) | Changed |
| `parity` | odd = `E_del{k}_p/m` | odd = `E_eps_del{k}_{..}` | Changed |
| `generator_realization.ordering` | `a_0, b_1_p, b_1_m, ...` | `a_1_p, a_1_m, b_1_p, b_1_m, ...` | Changed |
| `structure_constants` | Computed (B(0,n)) | Deferred (future issue) | Pending |
| `metadata` | existing | same structure | None |
