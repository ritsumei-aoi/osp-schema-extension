# Schema 1 v5.0 Specification for C(n+1) = osp(2|2n)

This document specifies the v5.0 JSON Schema 1 (algebra structure) for
$C(n+1) = \mathfrak{osp}(2|2n)$, extending the B(0,n) base schema.

**Finalized**: Issue I02-1 (2026-10-06)  
**Approved by**: human researcher  
**Notation reference**: `handover/notation.md`  
**Math reference**: `docs/math/Cn1_definition.md`, `docs/math/B0n_schema_v5.md`

---

## 1. File Naming Convention

| Algebra | n (bosonic rank) | Schema 1 file |
|---|---|---|
| C(2) = osp(2\|2) | 1 | `C_1_structure.json` |
| C(3) = osp(2\|4) | 2 | `C_2_structure.json` |
| C(4) = osp(2\|6) | 3 | `C_3_structure.json` |

Convention: `C_{n}_structure.json` where `n` = number of bosonic oscillator pairs $b_k^\pm$.

---

## 2. Top-Level Schema Structure

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

`central_elements` is a **mandatory top-level key** for C(n+1), appearing after `oscillator_relations`.

---

## 3. Field Specifications

### 3.1 `schema_version`

```json
"schema_version": "5.0"
```

### 3.2 `algebra`

**Pattern** (substitute concrete values for each n):

```json
{
  "family": "C",
  "m": 1,
  "n": <n>,
  "cartan_type": "C(<n+1>)",
  "alternative_notation": {
    "osp": "osp(2|<2n>)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": <2*n^2 + 5*n + 1>,
    "even": <2*n^2 + n + 1>,
    "odd": <4*n>
  }
}
```

**Dimension table**:

| n | even ($2n^2+n+1$) | odd ($4n$) | total ($2n^2+5n+1$) |
|---|---|---|---|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

**Example** (C(3), n=2):

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

### 3.3 `oscillator_generators`

**Pattern**:

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "relation": "{a_1^-, a_1^+} = 1",
    "description": "Standard CAR fermionic pair; m=1 pair in total"
  },
  "bosons": {
    "count": <2*n>,
    "n": <n>,
    "labels": ["b_1_p", "b_1_m", ..., "b_<n>_p", "b_<n>_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

**Example** (n=2):

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "relation": "{a_1^-, a_1^+} = 1",
    "description": "Standard CAR fermionic pair; m=1 pair in total"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

### 3.4 `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermionic pair",
    "relations": {
      "nilpotency_p": "a_1_p * a_1_p = 0",
      "nilpotency_m": "a_1_m * a_1_m = 0",
      "anticommutator": "{a_1_m, a_1_p} = 1"
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
    "description": "Fermionic and bosonic oscillators commute (undeformed)",
    "relation": "[b_i^±, a_1^±] = 0"
  }
}
```

This field is identical across n=1, 2, 3 (no n-dependent content).

### 3.5 `central_elements`

This is a **mandatory top-level key** (not present in B(0,n); new for C(n+1)).

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "properties": ["nilpotent: kappa^2 = 0", "central", "parity-odd"],
    "description": "Odd nilpotent central element; appears in deformed bracket [X,Y]_γ = [X,Y]_0 + kappa·γ(X,Y)"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "properties": ["central", "even", "identified with scalar 1 in all applications"],
    "description": "Even central identity; excluded from PBW basis and basis lists"
  }
}
```

This field is identical across n=1, 2, 3.

### 3.6 `basis`

**PBW ordering** (from `handover/notation.md` §5):
```
kappa < [odd: _pp block] < [odd: _pm block] < [odd: _mp block] < [odd: _mm block]
      < [even: H's < pos-sym < neg-sym < mixed]
(K = 1 is excluded)
```

#### n=1, C(2) = osp(2|2)

```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd: _pp<_pm<_mp<_mm] < [even: H's<pos-sym<neg-sym<mixed]  (K=1 excluded)"
}
```

#### n=2, C(3) = osp(2|4)

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
  "ordering_convention": "PBW: kappa < [odd: _pp<_pm<_mp<_mm] < [even: H's<pos-sym<neg-sym<mixed]  (K=1 excluded)"
}
```

#### n=3, C(4) = osp(2|6)

```json
{
  "even": [
    "H_1", "H_2", "H_3", "H_4",
    "E_2del1_p", "E_2del2_p", "E_2del3_p",
    "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp",
    "E_2del1_m", "E_2del2_m", "E_2del3_m",
    "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm",
    "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm",
    "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd: _pp<_pm<_mp<_mm] < [even: H's<pos-sym<neg-sym<mixed]  (K=1 excluded)"
}
```

### 3.7 `parity`

Rule: `E_eps1_*` generators have parity 1; all Cartan and even root generators have parity 0.

#### n=2, C(3) (reference):

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

### 3.8 `generator_realization`

Standard form (PBW) ordering of oscillator words:
```
a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ... < b_n_p < b_n_m
```

**General pattern** (n arbitrary):

| Generator | `words` | `coeff` |
|---|---|---|
| `H_1` | `["a_1_p","a_1_m"]` + `["b_1_p","b_1_m"]` | `"1"` + `"1"` |
| `H_k` (2≤k≤n) | `["b_{k-1}_p","b_{k-1}_m"]` + `["b_k_p","b_k_m"]` | `"1"` + `"-1"` |
| `H_{n+1}` | `["b_n_p","b_n_m"]` + `[]` | `"-1"` + `"-1/2"` |
| `E_eps1_del{k}_pp` | `["a_1_p","b_k_p"]` | `"1"` |
| `E_eps1_del{k}_pm` | `["a_1_p","b_k_m"]` | `"1"` |
| `E_eps1_del{k}_mp` | `["a_1_m","b_k_p"]` | `"1"` |
| `E_eps1_del{k}_mm` | `["a_1_m","b_k_m"]` | `"1"` |
| `E_2del{k}_p` | `["b_k_p","b_k_p"]` | `"1"` |
| `E_2del{k}_m` | `["b_k_m","b_k_m"]` | `"1"` |
| `E_del{i}_del{j}_pp` (i<j) | `["b_i_p","b_j_p"]` | `"1"` |
| `E_del{i}_del{j}_mm` (i<j) | `["b_i_m","b_j_m"]` | `"1"` |
| `E_del{i}_del{j}_pm` (i<j) | `["b_i_p","b_j_m"]` | `"1"` |
| `E_del{i}_del{j}_mp` (i<j) | `["b_i_m","b_j_p"]` | `"1"` |

**Full JSON example** (n=2, C(3)):

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
      "parity": 0,
      "note": "Dual to simple root alpha_1 = epsilon - delta_1 (odd, isotropic)"
    },
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_1^+ b_1^- - b_2^+ b_2^-",
      "parity": 0,
      "note": "Dual to simple root alpha_k = delta_{k-1} - delta_k for 2<=k<=n"
    },
    "H_3": {
      "standard_form": [
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_2^+ b_2^- - 1/2",
      "parity": 0,
      "note": "Terminal Cartan H_{n+1}; dual to alpha_{n+1} = 2*delta_n; constant -1/2 from oscillator algebra"
    },
    "E_2del1_p": {
      "standard_form": [{"words": ["b_1_p", "b_1_p"], "coeff": "1"}],
      "frappat_form": "(b_1^+)^2",
      "parity": 0
    },
    "E_2del1_m": {
      "standard_form": [{"words": ["b_1_m", "b_1_m"], "coeff": "1"}],
      "frappat_form": "(b_1^-)^2",
      "parity": 0
    },
    "E_2del2_p": {
      "standard_form": [{"words": ["b_2_p", "b_2_p"], "coeff": "1"}],
      "frappat_form": "(b_2^+)^2",
      "parity": 0
    },
    "E_2del2_m": {
      "standard_form": [{"words": ["b_2_m", "b_2_m"], "coeff": "1"}],
      "frappat_form": "(b_2^-)^2",
      "parity": 0
    },
    "E_del1_del2_pp": {
      "standard_form": [{"words": ["b_1_p", "b_2_p"], "coeff": "1"}],
      "frappat_form": "b_1^+ b_2^+",
      "parity": 0
    },
    "E_del1_del2_mm": {
      "standard_form": [{"words": ["b_1_m", "b_2_m"], "coeff": "1"}],
      "frappat_form": "b_1^- b_2^-",
      "parity": 0
    },
    "E_del1_del2_pm": {
      "standard_form": [{"words": ["b_1_p", "b_2_m"], "coeff": "1"}],
      "frappat_form": "b_1^+ b_2^-",
      "parity": 0
    },
    "E_del1_del2_mp": {
      "standard_form": [{"words": ["b_1_m", "b_2_p"], "coeff": "1"}],
      "frappat_form": "b_1^- b_2^+",
      "parity": 0
    },
    "E_eps1_del1_pp": {
      "standard_form": [{"words": ["a_1_p", "b_1_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    },
    "E_eps1_del1_pm": {
      "standard_form": [{"words": ["a_1_p", "b_1_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^-",
      "parity": 1
    },
    "E_eps1_del1_mp": {
      "standard_form": [{"words": ["a_1_m", "b_1_p"], "coeff": "1"}],
      "frappat_form": "a_1^- b_1^+",
      "parity": 1
    },
    "E_eps1_del1_mm": {
      "standard_form": [{"words": ["a_1_m", "b_1_m"], "coeff": "1"}],
      "frappat_form": "a_1^- b_1^-",
      "parity": 1
    },
    "E_eps1_del2_pp": {
      "standard_form": [{"words": ["a_1_p", "b_2_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_2^+",
      "parity": 1
    },
    "E_eps1_del2_pm": {
      "standard_form": [{"words": ["a_1_p", "b_2_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_2^-",
      "parity": 1
    },
    "E_eps1_del2_mp": {
      "standard_form": [{"words": ["a_1_m", "b_2_p"], "coeff": "1"}],
      "frappat_form": "a_1^- b_2^+",
      "parity": 1
    },
    "E_eps1_del2_mm": {
      "standard_form": [{"words": ["a_1_m", "b_2_m"], "coeff": "1"}],
      "frappat_form": "a_1^- b_2^-",
      "parity": 1
    }
  }
}
```

### 3.9 `structure_constants`

Format (identical to B(0,n)):

```json
[
  {
    "X": "<generator_label>",
    "Y": "<generator_label>",
    "Z": "<generator_label>",
    "coeff": "<rational_string>",
    "sign_rule": "graded"
  }
]
```

Non-zero bracket: $[X, Y\} = \text{coeff} \cdot Z$.  
Full tables are generated by `build_C_structure_constants.py`. The key analytic results below drive code verification.

#### Cartan action eigenvalues

Let $s_\varepsilon = +1$ if a generator contains $a_1^+$, $-1$ if $a_1^-$; and $s_j = +1$ if it contains $b_j^+$, $-1$ if $b_j^-$, $0$ otherwise. Then:

| Cartan | Eigenvalue on $E$ |
|---|---|
| $H_1 = n_1 + N_1$ | $s_\varepsilon + s_1$ |
| $H_k = N_{k-1} - N_k$, $2 \leq k \leq n$ | $s_{k-1} - s_k$ |
| $H_{n+1} = -N_n - \tfrac{1}{2}$ | $-s_n$ |

Eigenvalue table for C(3), n=2:

| Generator | [H_1,·] | [H_2,·] | [H_3,·] |
|---|---|---|---|
| E_eps1_del1_pp | 2 | 1 | 0 |
| E_eps1_del1_pm | 0 | -1 | 0 |
| E_eps1_del1_mp | 0 | 1 | 0 |
| E_eps1_del1_mm | -2 | -1 | 0 |
| E_eps1_del2_pp | 1 | 0 | -1 |
| E_eps1_del2_pm | 1 | 0 | 1 |
| E_eps1_del2_mp | -1 | 0 | -1 |
| E_eps1_del2_mm | -1 | 0 | 1 |

#### Key odd–odd brackets

All computed from CAR ($\{a_1^-, a_1^+\}=1$) and CCR ($[b_j^-, b_k^+]=\delta_{jk}$):

| $X$ | $Y$ | $\{X, Y\}$ |
|---|---|---|
| $E_{\varepsilon+\delta_j}$ | $E_{-\varepsilon-\delta_j}$ | $-H_1 + \sum_{l=2}^{j} H_l + 2\sum_{l=j+1}^{n} H_l - 2H_{n+1}$ |
| $E_{\varepsilon+\delta_j}$ | $E_{-\varepsilon-\delta_k}$, $j < k$ | $E_{\delta_j - \delta_k}$ = `E_del{j}_del{k}_pm` |
| $E_{\varepsilon+\delta_j}$ | $E_{-\varepsilon-\delta_k}$, $j > k$ | $E_{\delta_j - \delta_k}$ = `E_del{k}_del{j}_mp` |
| $E_{\varepsilon-\delta_j}$ | $E_{-\varepsilon+\delta_j}$ | $+H_1 - \sum_{l=2}^{j} H_l - 2\sum_{l=j+1}^{n} H_l + 2H_{n+1}$ |

Specific examples (n=2):

```
{E_eps1_del1_pp, E_eps1_del1_mm} = -H_1 + 2*H_2 - 2*H_3
{E_eps1_del2_pp, E_eps1_del2_mm} = -H_1 + H_2 - 2*H_3
{E_eps1_del1_pp, E_eps1_del2_mm} = E_del1_del2_pm  (coeff=1)
{E_eps1_del2_pp, E_eps1_del1_mm} = E_del1_del2_mp  (coeff=1)
```

### 3.10 `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Aoi (2026), docs/math/Cn1_definition.md",
    "Issue I02-1 specification: docs/json_schema_specification.md",
    "Notation: handover/notation.md"
  ]
}
```

---

## 4. B(0,n) → C(n+1) Compatibility Summary

| Field | B(0,n) | C(n+1) | Change type |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | None |
| `algebra.family` | `"B"` | `"C"` | Value |
| `algebra.m` | `0` | `1` | Value |
| `algebra.dimension` (even/odd) | $2n^2+n$ / $2n$ | $2n^2+n+1$ / $4n$ | Value |
| `oscillator_generators` key | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | Key rename + value |
| `oscillator_relations` fermion key | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | Key rename + value |
| `central_elements` | Not present (comment only) | Mandatory top-level key | New |
| `basis.odd` count | $2n$ (`E_del{k}_p/m`) | $4n$ (`E_eps1_del{k}_{pp/pm/mp/mm}`) | Expansion |
| `basis.ordering_convention` | `κ < [odd] < [even]` | `κ < [_pp]<[_pm]<[_mp]<[_mm] < [even]` | Extended |
| `generator_realization.ordering` | `a_0, b_1_p, b_1_m, ...` | `a_1_p, a_1_m, b_1_p, b_1_m, ...` | Label + pair |
| `structure_constants` format | `{X,Y,Z,coeff,sign_rule}` list | Same | None |
| `metadata.generated_by` | `build_B_structure_constants.py` | `build_C_structure_constants.py` | Value |
